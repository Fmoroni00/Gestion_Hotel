from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import date
from decimal import Decimal
from typing import Optional


class EstadoReserva(str, Enum):
    """Estados posibles de una reserva."""
    pendiente = "pendiente"
    confirmada = "confirmada"
    activa = "activa"
    cancelada = "cancelada"
    terminada = "terminada"
    finalizada = "finalizada"


class ReservaBase(BaseModel):
    """Esquema base con los campos de una reserva."""
    DNI: str = Field(..., max_length=20, description="DNI del huésped")
    ID_Habitacion: int = Field(..., description="ID de la habitación reservada")
    fecha_entrada: date = Field(..., description="Fecha de entrada")
    fecha_salida: date = Field(..., description="Fecha de salida")
    precio_total: float | Decimal = Field(..., gt=0, description="Precio total de la reserva")
    estado: EstadoReserva = Field(
        default=EstadoReserva.pendiente,
        description="Estado de la reserva"
    )


class ReservaCreate(ReservaBase):
    """Esquema para crear una nueva reserva."""
    Huesped_DNI: str = Field(..., max_length=20, description="DNI del huésped")
    DNI: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class ReservaUpdate(BaseModel):
    """Esquema para actualizar una reserva."""
    fecha_salida: Optional[date] = Field(None, description="Nueva fecha de salida")
    precio_total: Optional[float | Decimal] = Field(None, gt=0, description="Nuevo precio total")
    estado: Optional[EstadoReserva] = Field(None, description="Nuevo estado de la reserva")


class ReservaResponse(BaseModel):
    """Esquema de respuesta con los campos exactos del modelo Reserva."""
    ID_Reserva: int
    DNI: str
    ID_Habitacion: int
    numero_habitacion: int | None = None
    huesped_nombre: str | None = None
    fecha_entrada: date
    fecha_salida: date
    precio_total: float | Decimal
    estado: EstadoReserva
    numero_cochera: int | None = None

    model_config = ConfigDict(from_attributes=True)
