from typing import Literal, Optional
from pydantic import BaseModel, EmailStr


class StaffLogin(BaseModel):
    correo: EmailStr
    contrasena: str


class HuespedLogin(BaseModel):
    valor: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user_type: Literal["staff", "huesped"]
    rol: Optional[str] = None
    ID_Reserva: Optional[int] = None
