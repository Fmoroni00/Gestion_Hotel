import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi import HTTPException, status

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta_super_segura")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña en texto plano contra un hash bcrypt.
    Intenta con passlib/ CryptContext y si falla hace fallback a bcrypt.checkpw
    para compatibilidad con hashes generados con la librería `bcrypt` directamente.
    """
    try:
        # Intentamos la verificación estándar con passlib
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback a bcrypt puro si passlib no funciona por compatibilidad
        try:
            import bcrypt as _bcrypt
            return _bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

def obtener_password_hash(contrasena: str) -> str:
    """Genera un hash bcrypt para una contraseña en texto plano."""
    return pwd_context.hash(contrasena)

def crear_token_acceso(data: dict) -> str:
    """Genera un token JWT firmado para el usuario"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def extraer_datos_token(token: str) -> dict:
    """Extrae y valida los datos del token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

# backward compatibility
verificar_contrasena = verificar_password