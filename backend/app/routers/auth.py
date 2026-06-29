from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
import app.models as models
import app.core.security as security
from app.crud.historial import registrar_historial  # Para registrar la auditoría
from app.schemas.historial import HistorialCreate

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Esquema para Staff (Correo + Contraseña)
class LoginStaffRequest(BaseModel):
    correo: str
    contrasena: str

# Esquema para Huésped (¡ÚNICAMENTE EL CÓDIGO/VALOR!)
class LoginHuespedRequest(BaseModel):
    valor: str

# ============================================================
# 1. LOGIN PARA PERSONAL (Admin, Recepcionista, Limpieza)
# ============================================================
@router.post("/login-staff")
def login_staff(payload: LoginStaffRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == payload.correo).first()
    
    if not usuario or usuario.activo == "inactivo":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas o usuario inactivo"
        )
    
    if not security.verificar_contrasena(payload.contrasena, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
        
    token_data = {"sub": usuario.correo, "id": usuario.ID_Usuario, "rol": usuario.rol, "user_type": "staff"}
    token = security.crear_token_acceso(data=token_data)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_type": "staff",
        "usuario": {
            "id": usuario.ID_Usuario,
            "nombre": usuario.nombre,
            "rol": usuario.rol
        }
    }

# ============================================================
# 2. LOGIN PARA EL HUÉSPED (Estilo Google Classroom - Solo Código)
# ============================================================
@router.post("/login-huesped")
def login_huesped(payload: LoginHuespedRequest, db: Session = Depends(get_db)):
    # 1. Buscar el código directamente en la base de datos física usando la columna 'valor'
    codigo_db = db.query(models.Codigo_Acceso).filter(models.Codigo_Acceso.valor == payload.valor).first()
    
    if not codigo_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código de acceso no válido"
        )
        
    # 2. Validar que el código esté en estado 'activo'
    if codigo_db.estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"El código de acceso no está disponible. Estado: {codigo_db.estado}"
        )
        
    # 3. Obtener los datos del huésped cruzando el DNI que tiene el código asignado
    huesped = db.query(models.Huesped).filter(models.Huesped.DNI == codigo_db.DNI).first()
    if not huesped:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Huésped asociado a este código no encontrado"
        )
    
    # 3.5. Buscar la reserva más reciente del huésped (priorizar activas, luego finalizadas)
    reserva = db.query(models.Reserva).filter(
        models.Reserva.DNI == huesped.DNI,
        models.Reserva.estado.in_(["pendiente", "confirmada", "activa", "ocupada"])
    ).order_by(models.Reserva.fecha_entrada.desc()).first()
    
    # Si no hay reserva activa, buscar la más reciente finalizada (para mostrar boleta)
    if not reserva:
        reserva = db.query(models.Reserva).filter(
            models.Reserva.DNI == huesped.DNI
        ).order_by(models.Reserva.fecha_entrada.desc()).first()
    
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ninguna reserva asociada a este huésped."
        )
    
    # 4. Generar el Token de acceso amarrado al Huésped
    token_data = {"sub": huesped.correo, "dni": huesped.DNI, "rol": "huesped", "user_type": "huesped"}
    token = security.crear_token_acceso(data=token_data)
    
    # EXTRA: Guardar de forma automática en el Historial de auditoría
    try:
        historial_data = HistorialCreate(
            accion=f"Huésped {huesped.nombre} {huesped.apellido} inició sesión con código {payload.valor}"
        )
        registrar_historial(db, historial_data)
    except Exception:
        pass # Que no rompa el login si el historial falla
    
    # 5. Retornar el token con ID_Reserva y estado de la reserva
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_type": "huesped",
        "ID_Reserva": reserva.ID_Reserva,
        "estado_reserva": reserva.estado,
        "huesped": {
            "dni": huesped.DNI,
            "nombre": f"{huesped.nombre} {huesped.apellido}",
            "rol": "huesped"
        }
    }