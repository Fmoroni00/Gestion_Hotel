from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CodigoAccesoCreate(BaseModel):
    DNI: str
    valor: str
    activo: Optional[bool] = True


class CodigoAccesoResponse(BaseModel):
    ID_Codigo: int
    valor: str
    estado: str
    DNI: str
