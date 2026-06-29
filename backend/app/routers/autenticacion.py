from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core import security
import app.models as models
from app.schemas.autenticacion import StaffLogin, HuespedLogin, TokenResponse

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login-staff", response_model=TokenResponse)
def login_staff(payload: StaffLogin, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == payload.correo).first()

    if not usuario or usuario.activo == "inactivo":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas o usuario inactivo"
        )

    if not usuario.password_hash or not security.verificar_password(payload.contrasena, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    token_data = {
        "sub": usuario.correo,
        "id": usuario.ID_Usuario,
        "rol": usuario.rol,
        "user_type": "staff"
    }
    token = security.crear_token_acceso(data=token_data)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_type="staff",
        rol=usuario.rol
    )


@router.post("/login-huesped", response_model=TokenResponse)
def login_huesped(payload: HuespedLogin, db: Session = Depends(get_db)):
    codigo = db.query(models.Codigo_Acceso).filter(models.Codigo_Acceso.valor == payload.valor).first()

    # Permitir código expirado para que el huésped pueda ver su boleta después del checkout
    if not codigo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código de acceso inválido"
        )

    huesped = codigo.huesped
    if not huesped or huesped.estado == "inactivo":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Huésped inactivo o no encontrado"
        )

    # Buscar reserva: primero activa, luego finalizada (para permitir ver boleta después del checkout)
    reserva_asociada = db.query(models.Reserva).filter(
        models.Reserva.DNI == huesped.DNI,
        models.Reserva.estado.in_(["pendiente", "confirmada", "activa", "finalizada"])
    ).order_by(models.Reserva.fecha_entrada.desc()).first()

    token_data = {
        "sub": huesped.DNI,
        "rol": "huesped",
        "user_type": "huesped",
    }
    if reserva_asociada:
        token_data["ID_Reserva"] = reserva_asociada.ID_Reserva

    token = security.crear_token_acceso(data=token_data)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_type="huesped",
        ID_Reserva=(reserva_asociada.ID_Reserva if reserva_asociada else None)
    )
