from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.crud.habitacion import (
    obtener_habitaciones,
    obtener_habitacion_por_id,
    crear_nueva_habitacion,
    actualizar_habitacion,
    eliminar_habitacion,
    contar_habitaciones
)
from app.crud.historial import registrar_historial
from app.schemas.habitacion import (
    HabitacionCreate,
    HabitacionResponse,
    HabitacionUpdate,
    EstadoHabitacion
)
from app.schemas.historial import HistorialCreate

router = APIRouter(prefix="/habitaciones", tags=["habitaciones"])


@router.get("/", response_model=List[HabitacionResponse])
def listar_habitaciones(
    skip: int = 0,
    limit: int = Query(100, ge=1, le=500),
    estado: EstadoHabitacion = None,
    db: Session = Depends(get_db)
):
    """
    Lista todas las habitaciones con paginación opcional y filtrado por estado.
    
    Query Parameters:
    - skip: Número de registros a saltar (default: 0)
    - limit: Número máximo de registros a retornar (default: 10)
    - estado: Filtrar por estado (disponible, ocupada, mantenimiento)
    """
    habitaciones = obtener_habitaciones(
        db,
        skip=skip,
        limit=limit,
        estado=estado.value if estado else None
    )
    return habitaciones


@router.get("/estadisticas/total")
def obtener_estadisticas(db: Session = Depends(get_db)):
    """Obtiene estadísticas generales de habitaciones."""
    total = contar_habitaciones(db)
    disponibles = contar_habitaciones(db, estado="disponible")
    ocupadas = contar_habitaciones(db, estado="ocupada")
    mantenimiento = contar_habitaciones(db, estado="mantenimiento")
    
    return {
        "total": total,
        "disponibles": disponibles,
        "ocupadas": ocupadas,
        "mantenimiento": mantenimiento
    }


@router.get("/{id_habitacion}", response_model=HabitacionResponse)
def obtener_habitacion(id_habitacion: int, db: Session = Depends(get_db)):
    """
    Obtiene una habitación específica por su ID.
    
    Path Parameters:
    - id_habitacion: ID de la habitación a buscar
    """
    habitacion = obtener_habitacion_por_id(db, id_habitacion)
    if not habitacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habitación con ID {id_habitacion} no encontrada"
        )
    return habitacion


@router.post("/", response_model=HabitacionResponse, status_code=status.HTTP_201_CREATED)
def crear_habitacion(
    habitacion: HabitacionCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva habitación.
    
    Body:
    - numero: Número único de la habitación (requerido)
    - tipo: Tipo de habitación (simple, doble, suite, etc.) (requerido)
    - precio_noche: Precio por noche (requerido)
    - estado: Estado inicial (disponible por defecto)
    """
    try:
        nueva_habitacion = crear_nueva_habitacion(db, habitacion)
        return nueva_habitacion
    except Exception as e:
        db.rollback()
        if "Duplicate entry" in str(e) or "UNIQUE constraint failed" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El número de habitación {habitacion.numero} ya existe"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear la habitación"
        )


@router.put("/{id_habitacion}", response_model=HabitacionResponse)
def actualizar_habitacion_endpoint(
    id_habitacion: int,
    habitacion_actualizada: HabitacionUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza una habitación existente.
    
    Path Parameters:
    - id_habitacion: ID de la habitación a actualizar
    
    Body:
    - Todos los campos son opcionales (solo se actualizan los que se proporcionen)
    """
    try:
        habitacion = actualizar_habitacion(db, id_habitacion, habitacion_actualizada)
        if not habitacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Habitación con ID {id_habitacion} no encontrada"
            )

        if habitacion_actualizada.estado is not None:
            registrar_historial(
                db,
                HistorialCreate(
                    accion=f"Habitación {habitacion.numero} cambiada a estado {habitacion.estado}",
                    ID_Habitacion=id_habitacion
                )
            )

        return habitacion
    except Exception as e:
        db.rollback()
        if "Duplicate entry" in str(e) or "UNIQUE constraint failed" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El número de habitación ya existe"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar la habitación"
        )


@router.delete("/{id_habitacion}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_habitacion_endpoint(
    id_habitacion: int,
    db: Session = Depends(get_db)
):
    """
    Elimina una habitación de la base de datos.
    
    Path Parameters:
    - id_habitacion: ID de la habitación a eliminar
    """
    eliminada = eliminar_habitacion(db, id_habitacion)
    if not eliminada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habitación con ID {id_habitacion} no encontrada"
        )
    return None
