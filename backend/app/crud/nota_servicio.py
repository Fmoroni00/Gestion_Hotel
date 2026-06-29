from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List

from app.models import Nota_Servicio, Servicio
from app.schemas.nota_servicio import NotaServicioCreate, NotaServicioUpdate


def crear_nota_servicio(db: Session, nota: NotaServicioCreate) -> Nota_Servicio:
    nueva_nota = Nota_Servicio(
        estado=nota.estado.value if hasattr(nota.estado, 'value') else nota.estado,
        ID_Reserva=nota.ID_Reserva,
        ID_Servicio=nota.ID_Servicio,
        concepto=nota.concepto,
        descripcion=nota.descripcion,
        motivo_cancelacion=nota.motivo_cancelacion
    )
    db.add(nueva_nota)
    db.commit()
    db.refresh(nueva_nota)
    return nueva_nota


def cambiar_estado_nota_servicio(db: Session, id_nota: int, nota_actualizada: NotaServicioUpdate) -> Nota_Servicio:
    nota = db.query(Nota_Servicio).filter(Nota_Servicio.ID_Nota == id_nota).first()
    if not nota:
        return None

    # Actualizar estado
    nota.estado = nota_actualizada.estado.value if hasattr(nota_actualizada.estado, 'value') else nota_actualizada.estado
    
    # Si viene motivo de cancelación, registrarlo
    if nota_actualizada.motivo_cancelacion:
        nota.motivo_cancelacion = nota_actualizada.motivo_cancelacion

    # Si se marca como completado/entregado y es una solicitud de cochera
    es_cochera = (nota.concepto == "Solicitud de Cochera" or 
                  (nota.servicio and "cochera" in nota.servicio.nombre.lower()))
                  
    if nota.estado in ['completado', 'entregado']:
        from app.models import Consumo, Boleta, Reserva
        if es_cochera:
            cochera_num = nota_actualizada.cochera_asignada or "Ninguna"
            costo_park = Decimal(str(nota_actualizada.costo_parking or 20.00))
            
            from app.models import Parking, Asignacion_Parking
            reserva = db.query(Reserva).filter(Reserva.ID_Reserva == nota.ID_Reserva).first()
            if reserva:
                # 1. Crear asignación de Parking en base de datos
                try:
                    # Extraer número entero de la cochera ingresada por el recepcionista
                    cleaned_num = "".join(filter(str.isdigit, cochera_num))
                    num_int = int(cleaned_num) if cleaned_num else 1
                    
                    # Buscar o crear el Parking
                    parking = db.query(Parking).filter(Parking.numero == num_int).first()
                    if not parking:
                        parking = Parking(numero=num_int, estado="ocupado")
                        db.add(parking)
                        db.flush()
                    else:
                        parking.estado = "ocupado"
                    
                    # Buscar o crear la asignación
                    asignacion = db.query(Asignacion_Parking).filter(Asignacion_Parking.ID_Reserva == reserva.ID_Reserva).first()
                    if not asignacion:
                        asignacion = Asignacion_Parking(
                            ID_Reserva=reserva.ID_Reserva,
                            ID_Parking=parking.ID_Parking,
                            fecha_inicio=reserva.fecha_entrada,
                            fecha_fin=reserva.fecha_salida
                        )
                        db.add(asignacion)
                        db.flush()
                    else:
                        asignacion.ID_Parking = parking.ID_Parking
                except Exception as e:
                    print("Error registrando parking:", e)
                    asignacion = None
                    
                # 2. Actualizar Boleta con la cochera y costo asignado
                boleta = db.query(Boleta).filter(Boleta.ID_Reserva == reserva.ID_Reserva).first()
                if boleta:
                    # Vincular la boleta con la asignación de parking y sumar el costo
                    if asignacion:
                        boleta.ID_Asignacion = asignacion.ID_Asignacion
                    boleta.total = Decimal(str(boleta.total)) + costo_park
                else:
                    # Si no hay boleta, la creamos preliminarmente para que el huésped vea su costo
                    from app.crud.facturacion import generar_boleta_final
                    try:
                        boleta = generar_boleta_final(db, reserva.ID_Reserva)
                        if asignacion:
                            boleta.ID_Asignacion = asignacion.ID_Asignacion
                        # Aquí sumar el costo extra de la cochera a la boleta recién creada si generar_boleta_final no la incluyó
                        # (generar_boleta_final no incluye cochera automáticamente en su lógica base)
                        boleta.total = Decimal(str(boleta.total)) + costo_park
                    except Exception as e:
                        print("Error generando boleta final:", e)
        else:
            # Otros servicios
            if nota.ID_Servicio:
                nuevo_consumo = Consumo(
                    ID_Reserva=nota.ID_Reserva,
                    ID_Servicio=nota.ID_Servicio,
                    cantidad=1,
                    precio_unitario=nota.servicio.precio_unitario if nota.servicio else Decimal(0)
                )
                db.add(nuevo_consumo)
                db.flush()

                reserva = db.query(Reserva).filter(Reserva.ID_Reserva == nota.ID_Reserva).first()
                if reserva:
                    boleta = db.query(Boleta).filter(Boleta.ID_Reserva == reserva.ID_Reserva).first()
                    if boleta:
                        boleta.total = Decimal(str(boleta.total)) + nuevo_consumo.precio_unitario
                    else:
                        from app.crud.facturacion import generar_boleta_final
                        try:
                            # Al generar la boleta, ya sumará los consumos incluyendo el recién insertado.
                            boleta = generar_boleta_final(db, reserva.ID_Reserva)
                        except Exception as e:
                            print("Error generando boleta final:", e)

    db.commit()
    db.refresh(nota)
    return nota


def obtener_notas_servicio_por_reserva(db: Session, id_reserva: int):
    """Retorna notas de servicio con detalles del servicio para mejor presentación."""
    notas = db.query(Nota_Servicio).filter(Nota_Servicio.ID_Reserva == id_reserva).order_by(Nota_Servicio.fecha_hora.desc()).all()
    return notas
