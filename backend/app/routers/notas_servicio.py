from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.crud.nota_servicio import crear_nota_servicio, cambiar_estado_nota_servicio, obtener_notas_servicio_por_reserva
from app.crud.historial import registrar_historial
from app.schemas.nota_servicio import NotaServicioCreate, NotaServicioResponse, NotaServicioUpdate
from app.schemas.historial import HistorialCreate
from app.models import Nota_Servicio

router = APIRouter(prefix="/notas-servicio", tags=["Notas de Servicio"])


@router.get("/", response_model=List[NotaServicioResponse])
def listar_notas_servicio_endpoint(db: Session = Depends(get_db)):
    return db.query(Nota_Servicio).order_by(Nota_Servicio.fecha_hora.desc()).all()


@router.post("/", response_model=NotaServicioResponse, status_code=status.HTTP_201_CREATED)
def crear_nota_servicio_endpoint(
    nota: NotaServicioCreate,
    db: Session = Depends(get_db)
):
    from app.models import Reserva
    reserva = db.query(Reserva).filter(Reserva.ID_Reserva == nota.ID_Reserva).first()
    if not reserva:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reserva no encontrada")
    if reserva.estado in ["finalizada", "cancelada"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pueden solicitar servicios para una estadía finalizada"
        )

    try:
        nueva_nota = crear_nota_servicio(db, nota)
        return nueva_nota
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.patch("/{id_nota}", response_model=NotaServicioResponse)
def actualizar_estado_nota_servicio(
    id_nota: int,
    nota_actualizada: NotaServicioUpdate,
    db: Session = Depends(get_db)
):
    nota = cambiar_estado_nota_servicio(db, id_nota, nota_actualizada)
    if not nota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nota de servicio con ID {id_nota} no encontrada"
        )

    motivo_str = f" con motivo: {nota_actualizada.motivo_cancelacion}" if nota_actualizada.motivo_cancelacion else ""
    registrar_historial(
        db,
        HistorialCreate(
            accion=f"Nota de servicio ID {id_nota} marcada como {nota_actualizada.estado.value}{motivo_str}"
        )
    )
    return nota


@router.get("/reserva/{id_reserva}", response_model=List[dict])
def obtener_notas_servicio_por_reserva_endpoint(
    id_reserva: int,
    db: Session = Depends(get_db)
):
    """Obtiene todas las notas de servicio de una reserva con detalles de servicios."""
    return obtener_notas_servicio_por_reserva(db, id_reserva)
