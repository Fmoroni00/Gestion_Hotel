from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.crud.servicio import (
    crear_servicio,
    obtener_servicios,
    registrar_consumo_reserva,
    obtener_consumos_por_reserva,
)
from app.schemas.servicio import (
    ServicioCreate,
    ServicioResponse,
    ConsumoCreate,
    ConsumoResponse,
)

router = APIRouter(prefix="", tags=["Servicios"])


def _servicio_response(servicio):
    return {
        "ID_Servicio": servicio.ID_Servicio,
        "nombre": servicio.nombre,
        "tipo": servicio.tipo,
        "descripcion": servicio.descripcion,
        "precio_unitario": float(servicio.precio_unitario),
        "estado": servicio.estado,
    }


def _consumo_response(consumo):
    subtotal = float(consumo.precio_unitario * consumo.cantidad)
    return {
        "ID_Consumo": consumo.ID_Consumo,
        "ID_Reserva": consumo.ID_Reserva,
        "ID_Servicio": consumo.ID_Servicio,
        "cantidad": consumo.cantidad,
        "fecha": consumo.fecha,
        "subtotal": subtotal
    }


@router.get("/servicios", response_model=List[ServicioResponse])
def listar_servicios(db: Session = Depends(get_db)):
    servicios = obtener_servicios(db)
    return [_servicio_response(servicio) for servicio in servicios]


@router.get("/servicios-disponibles", response_model=List[ServicioResponse])
def listar_servicios_disponibles(db: Session = Depends(get_db)):
    """
    Endpoint que trae todos los servicios activos disponibles para que los huéspedes soliciten.
    Filtra por estado='activo'.
    """
    import app.models as models
    servicios = db.query(models.Servicio).filter(
        models.Servicio.estado == 'activo'
    ).all()
    return [_servicio_response(servicio) for servicio in servicios]


@router.post("/servicios", response_model=ServicioResponse, status_code=status.HTTP_201_CREATED)
def crear_servicio_endpoint(
    servicio: ServicioCreate,
    db: Session = Depends(get_db)
):
    try:
        nuevo_servicio = crear_servicio(db, servicio)
        return _servicio_response(nuevo_servicio)
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.post("/reservas/{id_reserva}/consumos", response_model=ConsumoResponse, status_code=status.HTTP_201_CREATED)
def agregar_consumo_reserva(
    id_reserva: int,
    consumo: ConsumoCreate,
    db: Session = Depends(get_db)
):
    # CORRECCIÓN Y OPTIMIZACIÓN AQUÍ: 
    # Forzamos que el ID de la reserva en el payload sea exactamente el de la URL.
    # Así el Frontend no tiene que enviarlo dos veces ni salta el error 400.
    consumo.ID_Reserva = id_reserva

    try:
        nuevo_consumo = registrar_consumo_reserva(db, consumo)
        return _consumo_response(nuevo_consumo)
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.get("/reservas/{id_reserva}/consumos", response_model=List[ConsumoResponse])
def listar_consumos_reserva(id_reserva: int, db: Session = Depends(get_db)):
    consumos = obtener_consumos_por_reserva(db, id_reserva)
    return [_consumo_response(consumo) for consumo in consumos]