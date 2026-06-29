from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ParkingCreate(BaseModel):
    numero: int = Field(..., description="Número único de estacionamiento")
    estado: Optional[str] = Field(None, description="Estado inicial del parking")


class ParkingResponse(BaseModel):
    ID_Parking: int
    numero: int
    estado: str

    model_config = ConfigDict(from_attributes=True)


class AsignacionParkingCreate(BaseModel):
    ID_Reserva: int = Field(..., description="ID de la reserva asociada")
    ID_Parking: int = Field(..., description="ID del parking a asignar")
    fecha_inicio: datetime = Field(..., description="Fecha y hora de inicio de la asignación")
    fecha_fin: datetime = Field(..., description="Fecha y hora de fin de la asignación")


class AsignacionParkingResponse(AsignacionParkingCreate):
    ID_Asignacion: int

    model_config = ConfigDict(from_attributes=True)
