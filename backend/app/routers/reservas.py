from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from datetime import datetime

from app.core.database import get_db
from app.core.security import extraer_datos_token
from app.crud.reserva import (
    obtener_reservas,
    obtener_reserva_por_id,
    crear_nueva_reserva,
    cambiar_estado_reserva,
)
from app.crud.historial import registrar_historial
from app.schemas.reserva import ReservaCreate, ReservaResponse, EstadoReserva
from app.schemas.historial import HistorialCreate
from app.models import Reserva, Usuario


router = APIRouter(prefix="/reservas", tags=["Reservas"])


def _map_db_estado_a_api(estado: str) -> str:
    if estado == "finalizada":
        return "terminada"
    return estado


def _calcular_precio_total(reserva: Reserva) -> Decimal:
    if reserva.habitacion and reserva.habitacion.precio_noche is not None:
        noches = (reserva.fecha_salida.date() - reserva.fecha_entrada.date()).days
        return reserva.habitacion.precio_noche * Decimal(noches)
    return Decimal(0)


def _construir_respuesta_reserva(reserva: Reserva) -> ReservaResponse:
    numero_cochera = None
    if reserva.asignacion_parking and reserva.asignacion_parking.parking:
        numero_cochera = reserva.asignacion_parking.parking.numero

    payload = {
        "ID_Reserva": reserva.ID_Reserva,
        "DNI": reserva.DNI,
        "ID_Habitacion": reserva.ID_Habitacion,
        "numero_habitacion": reserva.habitacion.numero if reserva.habitacion else None,
        "huesped_nombre": f"{reserva.huesped.nombre} {reserva.huesped.apellido}" if reserva.huesped else None,
        "fecha_entrada": reserva.fecha_entrada.date() if isinstance(reserva.fecha_entrada, datetime) else reserva.fecha_entrada,
        "fecha_salida": reserva.fecha_salida.date() if isinstance(reserva.fecha_salida, datetime) else reserva.fecha_salida,
        "precio_total": float(_calcular_precio_total(reserva)),
        "estado": _map_db_estado_a_api(reserva.estado),
        "numero_cochera": numero_cochera,
    }
    return ReservaResponse.model_validate(payload)


@router.get("/", response_model=List[ReservaResponse])
def listar_reservas(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    estado: EstadoReserva = Query(None),
    db: Session = Depends(get_db)
):
    reservas = obtener_reservas(
        db,
        skip=skip,
        limit=limit,
        estado=estado
    )
    return [_construir_respuesta_reserva(reserva) for reserva in reservas]


@router.get("/{id_reserva}", response_model=ReservaResponse)
def obtener_reserva(id_reserva: int, db: Session = Depends(get_db)):
    reserva = obtener_reserva_por_id(db, id_reserva)
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva con ID {id_reserva} no encontrada"
        )
    return _construir_respuesta_reserva(reserva)


@router.post("/", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED)
def crear_reserva(
    reserva: ReservaCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    usuario_actual = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        payload = extraer_datos_token(token)
        if payload.get("user_type") == "staff" and payload.get("id") is not None:
            usuario_actual = db.query(Usuario).filter(Usuario.ID_Usuario == payload.get("id")).first()

    try:
        nueva_reserva = crear_nueva_reserva(db, reserva, usuario_actual=usuario_actual)
        registrar_historial(
            db,
            HistorialCreate(
                accion=f"Se creó una nueva reserva con ID {nueva_reserva.ID_Reserva}"
            )
        )
        return _construir_respuesta_reserva(nueva_reserva)
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear la reserva"
        )


@router.put("/{id_reserva}/estado", response_model=ReservaResponse)
def actualizar_estado_reserva(
    id_reserva: int,
    estado: EstadoReserva = Query(None),
    db: Session = Depends(get_db)
):
    if estado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estado no proporcionado")
    reserva_actualizada = cambiar_estado_reserva(db, id_reserva, estado)
    if not reserva_actualizada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva con ID {id_reserva} no encontrada"
        )

    registrar_historial(
        db,
        HistorialCreate(
            accion=f"Reserva ID {id_reserva} actualizada a estado {estado.value}"
        )
    )

    return _construir_respuesta_reserva(reserva_actualizada)
