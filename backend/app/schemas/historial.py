from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class HistorialBase(BaseModel):
    accion: str = Field(..., max_length=255, description="Acción realizada en el sistema")
    ID_Usuario: Optional[int] = Field(None, description="ID del usuario asociado (administrador, recepcionista o personal)")
    ID_Habitacion: Optional[int] = Field(None, description="ID de la habitación asociada")


class HistorialCreate(HistorialBase):
    pass


class HistorialResponse(HistorialBase):
    ID_Historial: int
    fecha_hora: datetime

    model_config = ConfigDict(from_attributes=True)
