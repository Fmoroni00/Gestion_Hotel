from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from decimal import Decimal
from datetime import date

from app.schemas.servicio import ConsumoResponse


class BoletaResponse(BaseModel):
    ID_Boleta: int
    ID_Reserva: int
    numero_boleta: str
    fecha_emision: date
    monto_hospedaje: float | Decimal
    monto_servicios: float | Decimal
    subtotal: float | Decimal
    igv: float | Decimal
    monto_total: float | Decimal

    model_config = ConfigDict(from_attributes=True)


class EstadoCuentaResponse(BaseModel):
    ID_Reserva: int
    monto_hospedaje: float | Decimal
    monto_servicios: float | Decimal
    monto_total: float | Decimal
    consumos: List[ConsumoResponse]
    estado_reserva: str
    estado_boleta: str
    numero_cochera: int | None = None

    model_config = ConfigDict(from_attributes=True)
