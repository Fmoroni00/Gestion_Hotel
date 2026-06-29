from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.crud.servicio import crear_servicio, registrar_consumo_reserva
from app.crud.facturacion import obtener_estado_cuenta_reserva, generar_boleta_final
from app.crud.historial import registrar_historial
from app.schemas.servicio import ServicioCreate, ServicioResponse, ConsumoCreate, ConsumoResponse
from app.schemas.facturacion import BoletaResponse, EstadoCuentaResponse
from app.schemas.historial import HistorialCreate

router = APIRouter(prefix="/facturacion", tags=["Facturación y Servicios"])


def _servicio_response(servicio):
    return {
        "ID_Servicio": servicio.ID_Servicio,
        "nombre": servicio.nombre,
        "descripcion": servicio.descripcion,
        "precio": float(servicio.precio_unitario)
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


@router.post("/servicios", response_model=ServicioResponse, status_code=status.HTTP_201_CREATED)
def crear_servicio_facturacion(
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
def cargar_consumo_reserva(
    id_reserva: int,
    consumo: ConsumoCreate,
    db: Session = Depends(get_db)
):
    if consumo.ID_Reserva != id_reserva:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID de reserva en la ruta y el cuerpo deben coincidir"
        )
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


@router.get("/reservas/{id_reserva}/estado-cuenta", response_model=EstadoCuentaResponse)
def ver_estado_cuenta_reserva(
    id_reserva: int,
    db: Session = Depends(get_db)
):
    try:
        estado = obtener_estado_cuenta_reserva(db, id_reserva)
        estado["consumos"] = [_consumo_response(consumo) for consumo in estado["consumos"]]
        return estado
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.post("/reservas/{id_reserva}/emitir-boleta", response_model=BoletaResponse, status_code=status.HTTP_201_CREATED)
def emitir_boleta_reserva(
    id_reserva: int,
    db: Session = Depends(get_db)
):
    try:
        boleta = generar_boleta_final(db, id_reserva)
        estado = obtener_estado_cuenta_reserva(db, id_reserva)
        numero_boleta = f"{boleta.serie}-{boleta.correlativo:06d}"
        total = estado["monto_total"]
        registrar_historial(
            db,
            HistorialCreate(
                accion=f"Se generó la boleta final {boleta.serie}-{boleta.correlativo:06d} para la Reserva ID {id_reserva}"
            )
        )
        return {
            "ID_Boleta": boleta.ID_Boleta,
            "ID_Reserva": boleta.ID_Reserva,
            "numero_boleta": numero_boleta,
            "fecha_emision": boleta.fecha,
            "monto_hospedaje": estado["monto_hospedaje"],
            "monto_servicios": estado["monto_servicios"],
            "monto_total": estado["monto_total"],
        }
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
