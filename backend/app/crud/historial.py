from sqlalchemy.orm import Session

from app.models import Historial
from app.schemas.historial import HistorialCreate


def registrar_historial(db: Session, historial: HistorialCreate) -> Historial:
    nuevo_historial = Historial(
        accion=historial.accion,
        ID_Usuario=historial.ID_Usuario,
        ID_Habitacion=historial.ID_Habitacion
    )
    db.add(nuevo_historial)
    db.commit()
    db.refresh(nuevo_historial)
    return nuevo_historial


def obtener_historial(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Historial).order_by(Historial.fecha_hora.desc()).offset(skip).limit(limit).all()
