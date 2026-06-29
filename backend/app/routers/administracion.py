from datetime import date
from typing import List
from logging import getLogger

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app import models
from app.schemas.administracion import UsuarioResponse, BoletaResumenResponse, ConfiguracionResponse, ConfiguracionBase
from app.crud.facturacion import generar_boleta_final

logger = getLogger(__name__)

router = APIRouter(prefix="", tags=["Administración"])


@router.get("/usuarios", response_model=List[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()
    return usuarios


@router.get("/boletas", response_model=List[BoletaResumenResponse])
def listar_boletas(db: Session = Depends(get_db)):
    try:
        # Usar joinedload para cargar relaciones de manera eficiente (evita N+1 queries)
        boletas = db.query(models.Boleta).options(
            joinedload(models.Boleta.reserva).joinedload(models.Reserva.habitacion)
        ).all()
        resultado = []

        for boleta in boletas:
            numero_habitacion = "N/A"
            
            # Validar que la boleta tiene reserva
            if boleta.reserva:
                try:
                    # Intentar obtener el número de habitación desde la relación cargada
                    if boleta.reserva.habitacion:
                        numero_habitacion = boleta.reserva.habitacion.numero
                    elif boleta.reserva.ID_Habitacion:
                        numero_habitacion = boleta.reserva.ID_Habitacion
                except Exception as e:
                    logger.warning(f"Error accediendo a habitación de boleta {boleta.ID_Boleta}: {str(e)}")
                    numero_habitacion = "N/A"

            resultado.append({
                "ID_Boleta": boleta.ID_Boleta,
                "numero_habitacion": numero_habitacion,
                "monto": float(boleta.total),
                "fecha": boleta.fecha,
                "estado": boleta.estado
            })

        return resultado
    
    except Exception as e:
        logger.error(f"Error en listar_boletas: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar boletas de la base de datos"
        )


@router.get("/configuracion", response_model=ConfiguracionResponse)
def obtener_configuracion(db: Session = Depends(get_db)):
    configuracion = db.query(models.Configuracion).order_by(models.Configuracion.ID_Configuracion).first()
    if not configuracion:
        configuracion = models.Configuracion(
            nombre_hotel="Hotel PMS",
            hora_checkin="15:00",
            hora_checkout="12:00"
        )
        db.add(configuracion)
        db.commit()
        db.refresh(configuracion)
    return configuracion


@router.put("/configuracion", response_model=ConfiguracionResponse)
def actualizar_configuracion(
    payload: ConfiguracionBase,
    db: Session = Depends(get_db)
):
    configuracion = db.query(models.Configuracion).order_by(models.Configuracion.ID_Configuracion).first()

    if not configuracion:
        configuracion = models.Configuracion(
            nombre_hotel=payload.nombre_hotel,
            hora_checkin=payload.hora_checkin,
            hora_checkout=payload.hora_checkout,
        )
        db.add(configuracion)
    else:
        configuracion.nombre_hotel = payload.nombre_hotel
        configuracion.hora_checkin = payload.hora_checkin
        configuracion.hora_checkout = payload.hora_checkout

    db.commit()
    db.refresh(configuracion)
    return configuracion
