from datetime import datetime, time
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import Habitacion, Huesped, Recepcionista, Reserva, Codigo_Acceso
from app.schemas.reserva import ReservaCreate, ReservaUpdate, EstadoReserva

# Nuevo: importar facturación e historial para emitir boleta al terminar la reserva
from app.crud.facturacion import generar_boleta_final
from app.crud.historial import registrar_historial
from app.schemas.historial import HistorialCreate


def _map_estado_api_to_db(estado: EstadoReserva) -> str:
    if estado == EstadoReserva.terminada:
        return "finalizada"
    return estado.value


def _map_estado_db_to_api(estado: str) -> str:
    if estado == "finalizada":
        return "terminada"
    return estado


def _fecha_datetime(fecha):
    if isinstance(fecha, datetime):
        return fecha
    return datetime.combine(fecha, time.min)


def obtener_reservas(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    estado: Optional[EstadoReserva] = None
) -> List[Reserva]:
    query = db.query(Reserva)

    if estado:
        estado_db = _map_estado_api_to_db(estado)
        query = query.filter(Reserva.estado == estado_db)

    return query.offset(skip).limit(limit).all()


def obtener_reserva_por_id(db: Session, id_reserva: int) -> Optional[Reserva]:
    return db.query(Reserva).filter(Reserva.ID_Reserva == id_reserva).first()


def crear_nueva_reserva(db: Session, reserva: ReservaCreate) -> Reserva:
    huesped = db.query(Huesped).filter(Huesped.DNI == reserva.Huesped_DNI).first()
    if not huesped:
        raise ValueError(f"Huésped con DNI {reserva.Huesped_DNI} no encontrado")

    habitacion = db.query(Habitacion).filter(Habitacion.ID_Habitacion == reserva.ID_Habitacion).first()
    if not habitacion:
        raise ValueError(f"Habitación con ID {reserva.ID_Habitacion} no encontrada")

    if habitacion.estado != "disponible":
        raise ValueError(
            f"La habitación {reserva.ID_Habitacion} no está disponible: estado actual {habitacion.estado}"
        )

    if reserva.fecha_salida <= reserva.fecha_entrada:
        raise ValueError("La fecha de salida debe ser posterior a la fecha de entrada")

    recepcionista = db.query(Recepcionista).first()
    if not recepcionista:
        raise ValueError("No hay recepcionista registrado para asignar la reserva")

    db_reserva = Reserva(
        fecha_entrada=_fecha_datetime(reserva.fecha_entrada),
        fecha_salida=_fecha_datetime(reserva.fecha_salida),
        estado=_map_estado_api_to_db(reserva.estado),
        DNI=reserva.Huesped_DNI,
        ID_Habitacion=reserva.ID_Habitacion,
        ID_Recepcionista=recepcionista.ID_Usuario
    )

    habitacion.estado = "ocupada"
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva


def cambiar_estado_reserva(
    db: Session,
    id_reserva: int,
    nuevo_estado: EstadoReserva
) -> Optional[Reserva]:
    reserva = db.query(Reserva).filter(Reserva.ID_Reserva == id_reserva).first()
    if not reserva:
        return None

    reserva.estado = _map_estado_api_to_db(nuevo_estado)

    if nuevo_estado in (EstadoReserva.cancelada, EstadoReserva.terminada):
        if reserva.habitacion:
            reserva.habitacion.estado = "disponible"

    # Generar boleta automáticamente si la reserva se marca como terminada (check-out)
    try:
        if nuevo_estado == EstadoReserva.terminada:
            # generar_boleta_final es idempotente: si ya existe devuelve la existente
            boleta = generar_boleta_final(db, id_reserva)
            # Registrar en historial de auditoría
            try:
                registrar_historial(
                    db,
                    HistorialCreate(
                        accion=f"Check-out realizado. Boleta generada: {boleta.serie}-{boleta.correlativo:06d} para Reserva ID {id_reserva}"
                    )
                )
            except Exception:
                # No queremos que falle la transacción principal si el historial falla
                pass
    except Exception:
        # No debe romper la transición de estado si la emisión falla; fallar silenciosamente y seguir
        pass

    db.commit()
    db.refresh(reserva)
    return reserva
