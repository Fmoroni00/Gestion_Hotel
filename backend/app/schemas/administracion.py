from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioResponse(BaseModel):
    ID_Usuario: int
    nombre: str
    correo: EmailStr
    rol: str
    activo: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class BoletaResumenResponse(BaseModel):
    ID_Boleta: int
    numero_habitacion: Optional[int]
    monto: Decimal
    fecha: date
    estado: str


class ConfiguracionBase(BaseModel):
    nombre_hotel: str = Field(..., max_length=100)
    hora_checkin: str = Field(..., max_length=5)
    hora_checkout: str = Field(..., max_length=5)


class ConfiguracionResponse(ConfiguracionBase):
    ID_Configuracion: int
    model_config = ConfigDict(from_attributes=True)
