from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional


class ServicioBase(BaseModel):
    nombre: str = Field(..., max_length=120, description="Nombre del servicio o extra")
    tipo: str = Field(..., max_length=50, description="Tipo de servicio")
    precio_unitario: float = Field(..., gt=0, description="Precio unitario del servicio")
    descripcion: Optional[str] = Field(None, max_length=255, description="Descripción del servicio")


class ServicioCreate(ServicioBase):
    """Esquema para crear un servicio en el catálogo."""
    pass


class ServicioResponse(ServicioBase):
    ID_Servicio: int
    estado: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ConsumoBase(BaseModel):
    ID_Reserva: int = Field(..., description="ID de la reserva asociada")
    ID_Servicio: int = Field(..., description="ID del servicio consumido")
    cantidad: int = Field(..., gt=0, description="Cantidad de unidades o días de servicio")
    fecha: Optional[datetime] = Field(None, description="Fecha del consumo")
    precio_unitario: Optional[float | Decimal] = Field(None, description="Precio unitario aplicado")


class ConsumoCreate(BaseModel):
    ID_Reserva: int = Field(..., description="ID de la reserva asociada")
    ID_Servicio: int = Field(..., description="ID del servicio consumido")
    cantidad: int = Field(..., gt=0, description="Cantidad de unidades o días de servicio")


class ConsumoResponse(ConsumoBase):
    ID_Consumo: int
    fecha: datetime
    subtotal: float | Decimal

    model_config = ConfigDict(from_attributes=True)
