from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from enum import Enum
from typing import Optional


class EstadoHabitacion(str, Enum):
    """Estados posibles de una habitación."""
    disponible = "disponible"
    ocupada = "ocupada"
    mantenimiento = "mantenimiento"


class HabitacionBase(BaseModel):
    """Esquema base con campos comunes para Habitación."""
    numero: int = Field(..., description="Número único de la habitación")
    tipo: str = Field(..., max_length=50, description="Tipo de habitación (simple, doble, suite, etc.)")
    precio_noche: Decimal = Field(..., max_digits=10, decimal_places=2, description="Precio por noche en formato decimal")
    estado: EstadoHabitacion = Field(default=EstadoHabitacion.disponible, description="Estado actual de la habitación")


class HabitacionCreate(HabitacionBase):
    """Esquema para crear una nueva Habitación."""
    pass


class HabitacionUpdate(BaseModel):
    """Esquema para actualizar una Habitación (todos los campos opcionales)."""
    numero: Optional[int] = Field(None, description="Número único de la habitación")
    tipo: Optional[str] = Field(None, max_length=50, description="Tipo de habitación")
    precio_noche: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2, description="Precio por noche")
    estado: Optional[EstadoHabitacion] = Field(None, description="Estado de la habitación")


class HabitacionResponse(HabitacionBase):
    """Esquema de respuesta con ID de la Habitación."""
    ID_Habitacion: int
    amenidades: list[str] = Field(default_factory=list, description="Nombres de las amenidades asociadas")

    model_config = ConfigDict(from_attributes=True)
