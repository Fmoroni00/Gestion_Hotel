from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime
from typing import Optional


class EstadoNotaServicio(str, Enum):
    pendiente = "pendiente"
    entregado = "entregado"
    completado = "completado"
    cancelado = "cancelado"


class NotaServicioBase(BaseModel):
    estado: EstadoNotaServicio = EstadoNotaServicio.pendiente
    ID_Reserva: int = Field(..., description="ID de la reserva asociada")
    ID_Servicio: Optional[int] = Field(None, description="ID del servicio pedido")
    concepto: Optional[str] = Field(None, description="Concepto de la nota de servicio")
    descripcion: Optional[str] = Field(None, description="Descripción de la nota de servicio")
    motivo_cancelacion: Optional[str] = Field(None, description="Motivo de cancelación si aplica")


class NotaServicioCreate(NotaServicioBase):
    pass


class NotaServicioUpdate(BaseModel):
    estado: EstadoNotaServicio = Field(..., description="Nuevo estado de la nota de servicio")
    motivo_cancelacion: Optional[str] = Field(None, description="Motivo de la cancelación")
    cochera_asignada: Optional[str] = Field(None, description="Número de cochera asignada si aplica")
    costo_parking: Optional[float] = Field(None, description="Costo de estacionamiento asignado si aplica")


class NotaServicioResponse(NotaServicioBase):
    ID_Nota: int
    fecha_hora: datetime
    # Detalles del servicio para mejor presentación
    nombre_servicio: Optional[str] = None
    descripcion_servicio: Optional[str] = None
    tipo_servicio: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
