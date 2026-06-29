from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.orm import Session, joinedload
from typing import List
from logging import getLogger

from app.core.database import get_db
from app.core.security import extraer_datos_token
import app.models as models
from app.crud.huesped import (
    obtener_huespedes,
    obtener_huesped_por_dni,
    obtener_huesped_por_correo,
    crear_nuevo_huesped,
    actualizar_huesped,
    eliminar_huesped,
    contar_huespedes
)
from app.schemas.huesped import (
    HuespedCreate,
    HuespedResponse,
    HuespedUpdate,
    EstadoHuesped,
    EstadiaHuespedResponse
)

logger = getLogger(__name__)
router = APIRouter(prefix="/huespedes", tags=["Huéspedes"]) # <-- Corregido el tag para que se vea elegante en Swagger


@router.get("/estadia", response_model=EstadiaHuespedResponse)
def obtener_estadia_huesped(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Obtiene la información de estadía actual del huésped autenticado.
    Retorna: número de habitación, tipo, fecha de entrada, monto total y estado de la boleta.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato inválido"
        )
    
    token = authorization.split(" ")[1]
    payload = extraer_datos_token(token)
    user_type = payload.get('user_type')

    # Extraer el DNI del huésped del token si corresponde
    dni_huesped = None
    if user_type == 'huesped':
        dni_huesped = payload.get('sub')
        if not dni_huesped:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: no contiene información del huésped"
            )
    
    try:
        # Buscar la reserva activa/ocupada del huésped
        reserva = db.query(models.Reserva).options(
            joinedload(models.Reserva.habitacion),
            joinedload(models.Reserva.boletas)
        ).filter(
            models.Reserva.DNI == dni_huesped,
            models.Reserva.estado.in_(["activa", "ocupada", "confirmada"])
        ).order_by(models.Reserva.fecha_entrada.desc()).first()
        
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay reserva activa para este huésped"
            )
        
        # Obtener la boleta más reciente
        boleta = None
        monto_total = 0
        estado_boleta = "Sin facturar"
        
        if reserva.boletas:
            boleta = reserva.boletas[0]  # Asumimos que hay una boleta por reserva
            monto_total = float(boleta.total) if boleta.total else 0
            estado_boleta = boleta.estado if boleta.estado else "Sin facturar"
        
        return {
            "ID_Reserva": reserva.ID_Reserva,
            "numero_habitacion": reserva.habitacion.numero if reserva.habitacion else "N/A",
            "tipo_habitacion": reserva.habitacion.tipo if reserva.habitacion else "N/A",
            "fecha_entrada": reserva.fecha_entrada,
            "fecha_salida": reserva.fecha_salida,
            "monto_total": monto_total,
            "estado_boleta": estado_boleta
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en obtener_estadia_huesped: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar información de estadía"
        )


@router.get("/", response_model=List[HuespedResponse])
def listar_huespedes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    estado: EstadoHuesped = Query(None),
    db: Session = Depends(get_db)
):
    """
    Lista todos los huéspedes con paginación opcional y filtrado por estado.
    """
    huespedes = obtener_huespedes(
        db,
        skip=skip,
        limit=limit,
        estado=estado.value if estado else None
    )
    return huespedes


@router.get("/estadisticas/total")
def obtener_estadisticas(db: Session = Depends(get_db)):
    """Obtiene estadísticas generales de huéspedes."""
    total = contar_huespedes(db)
    activos = contar_huespedes(db, estado="activo")
    inactivos = contar_huespedes(db, estado="inactivo")
    
    return {
        "total": total,
        "activos": activos,
        "inactivos": inactivos
    }


@router.get("/buscar/dni")
def buscar_huesped_por_dni(dni: str = Query(None, description="DNI del huésped a buscar"), db: Session = Depends(get_db)):
    """
    Busca un huésped específico por su DNI.
    """
    if not dni:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El parámetro 'dni' es requerido")
    huesped = obtener_huesped_por_dni(db, dni)
    if not huesped:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Huésped con DNI {dni} no encontrado"
        )
    return huesped


@router.get("/buscar/correo")
def buscar_huesped_por_correo(correo: str = Query(None, description="Correo del huésped a buscar"), db: Session = Depends(get_db)):
    """
    Busca un huésped específico por su correo electrónico.
    """
    if not correo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El parámetro 'correo' es requerido")
    huesped = obtener_huesped_por_correo(db, correo)
    if not huesped:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Huésped con correo {correo} no encontrado"
        )
    return huesped


@router.get("/{dni}", response_model=HuespedResponse)
def obtener_huesped(dni: str, db: Session = Depends(get_db)):
    """
    Obtiene los detalles de un huésped específico por su DNI.
    """
    huesped = obtener_huesped_por_dni(db, dni)
    if not huesped:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Huésped con DNI {dni} no encontrado"
        )
    return huesped


@router.post("/", response_model=HuespedResponse, status_code=status.HTTP_201_CREATED)
def registrar_huesped(
    huesped: HuespedCreate,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo huésped en el sistema.
    """
    # CORREGIDO: Cambiado 'huesped.dni' a 'huesped.DNI'
    huesped_existente = obtener_huesped_por_dni(db, huesped.DNI)
    if huesped_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El DNI {huesped.DNI} ya está registrado"
        )
    
    # Validar que el correo no esté registrado (si se proporciona)
    if huesped.correo:
        huesped_por_correo = obtener_huesped_por_correo(db, huesped.correo)
        if huesped_por_correo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El correo {huesped.correo} ya está registrado"
            )
    
    try:
        nuevo_huesped = crear_nuevo_huesped(db, huesped)
        return nuevo_huesped
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al registrar el huésped"
        )


@router.put("/{dni}", response_model=HuespedResponse)
def actualizar_huesped_endpoint(
    dni: str,
    huesped_actualizado: HuespedUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de un huésped existente.
    """
    # Validar que el huésped existe
    huesped_existente = obtener_huesped_por_dni(db, dni)
    if not huesped_existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Huésped con DNI {dni} no encontrado"
        )
    
    # Si se proporciona un nuevo correo, validar que no esté en uso
    if huesped_actualizado.correo and huesped_actualizado.correo != huesped_existente.correo:
        otro_huesped = obtener_huesped_por_correo(db, huesped_actualizado.correo)
        if otro_huesped:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El correo {huesped_actualizado.correo} ya está en uso"
            )
    
    try:
        huesped = actualizar_huesped(db, dni, huesped_actualizado)
        return huesped
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar el huésped"
        )


@router.delete("/{dni}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_huesped_endpoint(
    dni: str,
    db: Session = Depends(get_db)
):
    """
    Elimina un huésped del sistema.
    """
    eliminado = eliminar_huesped(db, dni)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Huésped con DNI {dni} no encontrado"
        )
    return None