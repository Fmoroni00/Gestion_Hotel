from pydantic import BaseModel, Field, EmailStr, ConfigDict
from enum import Enum
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class EstadoHuesped(str, Enum):
    """Estados posibles de un huésped."""
    activo = "activo"
    inactivo = "inactivo"


class HuespedBase(BaseModel):
    """Esquema base con campos comunes para Huésped."""
    DNI: str = Field(..., max_length=20, description="Documento de identidad del huésped") # <-- Corregido a DNI
    nombre: str = Field(..., max_length=100, description="Nombre del huésped")
    apellido: str = Field(..., max_length=100, description="Apellido del huésped")
    correo: Optional[EmailStr] = Field(None, max_length=150, description="Correo electrónico del huésped")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto del huésped")
    estado: EstadoHuesped = Field(default=EstadoHuesped.activo, description="Estado del huésped")


class HuespedCreate(HuespedBase):
    """Esquema para registrar un nuevo Huésped."""
    pass


class HuespedUpdate(BaseModel):
    """Esquema para actualizar un Huésped (todos los campos opcionales)."""
    nombre: Optional[str] = Field(None, max_length=100, description="Nombre del huésped")
    apellido: Optional[str] = Field(None, max_length=100, description="Apellido del huésped")
    correo: Optional[EmailStr] = Field(None, max_length=150, description="Correo electrónico del huésped")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto del huésped")
    estado: Optional[EstadoHuesped] = Field(None, description="Estado del huésped")


class HuespedResponse(HuespedBase):
    """Esquema de respuesta con información completa del Huésped."""
    DNI: str # <-- Corregido a DNI

    model_config = ConfigDict(from_attributes=True)


class EstadiaHuespedResponse(BaseModel):
    """Respuesta con la información de estadía actual del huésped."""
    ID_Reserva: Optional[int] = None
    numero_habitacion: int
    tipo_habitacion: str
    fecha_entrada: datetime
    fecha_salida: Optional[datetime]
    monto_total: Decimal
    estado_boleta: str
    cochera_asignada: str = "Ninguna"
    costo_parking: Decimal = Decimal("0.0")
    
    model_config = ConfigDict(from_attributes=True)