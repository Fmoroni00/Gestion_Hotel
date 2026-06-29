from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
import app.models as models
from app.schemas.codigo_acceso import CodigoAccesoCreate, CodigoAccesoResponse

router = APIRouter(prefix="/codigos-acceso", tags=["Codigos de Acceso"])


@router.post("/", response_model=CodigoAccesoResponse, status_code=status.HTTP_201_CREATED)
def crear_codigo_acceso(payload: CodigoAccesoCreate, db: Session = Depends(get_db)):
    # Verificar que el huésped exista
    huesped = db.query(models.Huesped).filter(models.Huesped.DNI == payload.DNI).first()
    if not huesped:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Huésped no encontrado")

    # Verificar que el código no exista
    existente = db.query(models.Codigo_Acceso).filter(models.Codigo_Acceso.valor == payload.valor).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El código ya existe")

    estado = 'activo' if payload.activo else 'inactivo'

    nuevo = models.Codigo_Acceso(
        valor=payload.valor,
        estado=estado,
        DNI=huesped.DNI
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return CodigoAccesoResponse(
        ID_Codigo=nuevo.ID_Codigo,
        valor=nuevo.valor,
        estado=nuevo.estado,
        DNI=nuevo.DNI
    )


@router.get("/reserva/{id_reserva}", response_model=List[CodigoAccesoResponse])
def obtener_codigos_por_reserva(id_reserva: int, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.ID_Reserva == id_reserva).first()
    if not reserva:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")

    # Buscar códigos asociados al huésped de la reserva
    codigos = db.query(models.Codigo_Acceso).filter(models.Codigo_Acceso.DNI == reserva.DNI).all()

    return [CodigoAccesoResponse(
        ID_Codigo=item.ID_Codigo,
        valor=item.valor,
        estado=item.estado,
        DNI=item.DNI
    ) for item in codigos]
