from sqlalchemy.orm import Session
from app.models import Habitacion
from app.schemas.habitacion import HabitacionCreate, HabitacionUpdate
from typing import List, Optional


def obtener_habitaciones(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None
) -> List[Habitacion]:
    """
    Obtiene una lista de habitaciones con paginación y filtrado opcional por estado.
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a saltar (para paginación)
        limit: Número máximo de registros a retornar
        estado: Filtro opcional por estado (disponible, ocupada, mantenimiento)
    
    Returns:
        Lista de objetos Habitacion
    """
    query = db.query(Habitacion)
    
    if estado:
        query = query.filter(Habitacion.estado == estado)
    
    return query.offset(skip).limit(limit).all()


def obtener_habitacion_por_id(db: Session, id_habitacion: int) -> Optional[Habitacion]:
    """
    Obtiene una habitación específica por su ID.
    
    Args:
        db: Sesión de base de datos
        id_habitacion: ID de la habitación a buscar
    
    Returns:
        Objeto Habitacion si existe, None si no
    """
    return db.query(Habitacion).filter(Habitacion.ID_Habitacion == id_habitacion).first()


def obtener_habitacion_por_numero(db: Session, numero: int) -> Optional[Habitacion]:
    """
    Obtiene una habitación por su número.
    
    Args:
        db: Sesión de base de datos
        numero: Número de la habitación
    
    Returns:
        Objeto Habitacion si existe, None si no
    """
    return db.query(Habitacion).filter(Habitacion.numero == numero).first()


def crear_nueva_habitacion(db: Session, habitacion: HabitacionCreate) -> Habitacion:
    """
    Crea una nueva habitación en la base de datos.
    
    Args:
        db: Sesión de base de datos
        habitacion: Esquema HabitacionCreate con datos de la nueva habitación
    
    Returns:
        Objeto Habitacion creado
    
    Raises:
        SQLAlchemy IntegrityError si el número ya existe
    """
    db_habitacion = Habitacion(
        numero=habitacion.numero,
        tipo=habitacion.tipo,
        precio_noche=habitacion.precio_noche,
        estado=habitacion.estado.value
    )
    db.add(db_habitacion)
    db.commit()
    db.refresh(db_habitacion)
    return db_habitacion


def actualizar_habitacion(
    db: Session,
    id_habitacion: int,
    habitacion_actualizada: HabitacionUpdate
) -> Optional[Habitacion]:
    """
    Actualiza una habitación existente.
    
    Args:
        db: Sesión de base de datos
        id_habitacion: ID de la habitación a actualizar
        habitacion_actualizada: Esquema HabitacionUpdate con los nuevos datos
    
    Returns:
        Objeto Habitacion actualizado si existe, None si no
    """
    db_habitacion = db.query(Habitacion).filter(Habitacion.ID_Habitacion == id_habitacion).first()
    
    if not db_habitacion:
        return None
    
    # Actualizar solo los campos que no son None
    datos_actualizacion = habitacion_actualizada.model_dump(exclude_unset=True)
    
    for campo, valor in datos_actualizacion.items():
        if valor is not None:
            if campo == "estado" and hasattr(valor, "value"):
                setattr(db_habitacion, campo, valor.value)
            else:
                setattr(db_habitacion, campo, valor)
    
    db.commit()
    db.refresh(db_habitacion)
    return db_habitacion


def eliminar_habitacion(db: Session, id_habitacion: int) -> bool:
    """
    Elimina una habitación de la base de datos.
    
    Args:
        db: Sesión de base de datos
        id_habitacion: ID de la habitación a eliminar
    
    Returns:
        True si se eliminó correctamente, False si no existe
    """
    db_habitacion = db.query(Habitacion).filter(Habitacion.ID_Habitacion == id_habitacion).first()
    
    if not db_habitacion:
        return False
    
    try:
        # Eliminar relaciones con amenidades primero para evitar FK constraints
        from app.models import Habitacion_Amenidad
        db.query(Habitacion_Amenidad).filter(Habitacion_Amenidad.ID_Habitacion == id_habitacion).delete()
        db.delete(db_habitacion)
        db.commit()
        return True
    except Exception:
        # Evitar que errores de integridad (FK) propaguen 500s.
        db.rollback()
        return False


def contar_habitaciones(db: Session, estado: Optional[str] = None) -> int:
    """
    Cuenta el número total de habitaciones, opcionalmente filtradas por estado.
    
    Args:
        db: Sesión de base de datos
        estado: Filtro opcional por estado
    
    Returns:
        Número total de habitaciones
    """
    query = db.query(Habitacion)
    
    if estado:
        query = query.filter(Habitacion.estado == estado)
    
    return query.count()
