from datetime import datetime
from typing import List
from sqlalchemy.orm import Session

from app.models import Parking, Asignacion_Parking, Reserva
from app.schemas.parking import AsignacionParkingCreate


def listar_parkings(db: Session) -> List[Parking]:
    return db.query(Parking).order_by(Parking.numero).all()


def obtener_parking_por_id(db: Session, id_parking: int) -> Parking:
    return db.query(Parking).filter(Parking.ID_Parking == id_parking).first()


def asignar_parking_a_reserva(db: Session, asignacion: AsignacionParkingCreate) -> Asignacion_Parking:
    reserva = db.query(Reserva).filter(Reserva.ID_Reserva == asignacion.ID_Reserva).first()
    if not reserva:
        raise ValueError("Reserva no encontrada")

    parking = db.query(Parking).filter(Parking.ID_Parking == asignacion.ID_Parking).first()
    if not parking:
        raise ValueError("Parking no encontrado")

    if asignacion.fecha_fin <= asignacion.fecha_inicio:
        raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")

    conflicto = db.query(Asignacion_Parking).filter(
        Asignacion_Parking.ID_Parking == asignacion.ID_Parking,
        Asignacion_Parking.fecha_inicio <= asignacion.fecha_fin,
        Asignacion_Parking.fecha_fin >= asignacion.fecha_inicio
    ).first()
    if conflicto:
        raise ValueError("El parking ya está asignado en ese rango de fechas")

    db_asignacion = Asignacion_Parking(
        ID_Reserva=asignacion.ID_Reserva,
        ID_Parking=asignacion.ID_Parking,
        fecha_inicio=asignacion.fecha_inicio,
        fecha_fin=asignacion.fecha_fin
    )
    parking.estado = "ocupado"
    db.add(db_asignacion)
    db.commit()
    db.refresh(db_asignacion)
    return db_asignacion


def liberar_parking(db: Session, id_parking: int) -> Parking:
    parking = db.query(Parking).filter(Parking.ID_Parking == id_parking).first()
    if not parking:
        return None

    parking.estado = "disponible"
    asignaciones = db.query(Asignacion_Parking).filter(Asignacion_Parking.ID_Parking == id_parking).all()
    for asignacion in asignaciones:
        db.delete(asignacion)

    db.commit()
    return parking
