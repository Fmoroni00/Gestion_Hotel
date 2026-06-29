from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.crud.parking import listar_parkings, asignar_parking_a_reserva
from app.crud.historial import registrar_historial
from app.schemas.parking import ParkingResponse, AsignacionParkingCreate, AsignacionParkingResponse
from app.schemas.historial import HistorialCreate

router = APIRouter(prefix="/parking", tags=["Parking"])


@router.get("/", response_model=List[ParkingResponse])
def obtener_mapa_parkings(db: Session = Depends(get_db)):
    return listar_parkings(db)


@router.post("/", response_model=AsignacionParkingResponse, status_code=status.HTTP_201_CREATED)
def asignar_parking(
    asignacion: AsignacionParkingCreate,
    db: Session = Depends(get_db)
):
    try:
        nueva_asignacion = asignar_parking_a_reserva(db, asignacion)
        registrar_historial(
            db,
            HistorialCreate(
                accion=f"Se asignó el Parking ID {nueva_asignacion.ID_Parking} a la Reserva ID {nueva_asignacion.ID_Reserva}"
            )
        )
        return nueva_asignacion
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
