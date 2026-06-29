from sqlalchemy.orm import Session
from app.models import Huesped
from app.schemas.huesped import HuespedCreate, HuespedUpdate
from typing import List, Optional


def obtener_huespedes(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    estado: Optional[str] = None
) -> List[Huesped]:
    """
    Obtiene una lista de huéspedes con paginación y filtrado opcional por estado.
    """
    query = db.query(Huesped)
    
    if estado:
        query = query.filter(Huesped.estado == estado)
    
    return query.offset(skip).limit(limit).all()


def obtener_huesped_por_dni(db: Session, dni: str) -> Optional[Huesped]:
    """
    Obtiene un huésped específico por su DNI.
    """
    return db.query(Huesped).filter(Huesped.DNI == dni).first()


def obtener_huesped_por_correo(db: Session, correo: str) -> Optional[Huesped]:
    """
    Obtiene un huésped por su correo electrónico.
    """
    return db.query(Huesped).filter(Huesped.correo == correo).first()


def crear_nuevo_huesped(db: Session, huesped: HuespedCreate) -> Huesped:
    """
    Crea un nuevo huésped en la base de datos vinculando el DNI correctamente.
    """
    # CORREGIDO: Cambiado 'huesped.dni' a 'huesped.DNI' para alinearse al esquema Pydantic
    db_huesped = Huesped(
        DNI=huesped.DNI,  
        nombre=huesped.nombre,
        apellido=huesped.apellido,
        correo=huesped.correo,
        telefono=huesped.telefono,
        estado=huesped.estado.value
    )
    db.add(db_huesped)
    db.commit()
    db.refresh(db_huesped)
    return db_huesped


def actualizar_huesped(
    db: Session,
    dni: str,
    huesped_actualizado: HuespedUpdate
) -> Optional[Huesped]:
    """
    Actualiza un huésped existente de forma parcial.
    """
    db_huesped = db.query(Huesped).filter(Huesped.DNI == dni).first()
    
    if not db_huesped:
        return None
    
    # Actualizar solo los campos que no son None
    datos_actualizacion = huesped_actualizado.model_dump(exclude_unset=True)
    
    for campo, valor in datos_actualizacion.items():
        if valor is not None:
            if campo == "estado" and hasattr(valor, "value"):
                setattr(db_huesped, campo, valor.value)
            else:
                setattr(db_huesped, campo, valor)
    
    db.commit()
    db.refresh(db_huesped)
    return db_huesped


def eliminar_huesped(db: Session, dni: str) -> bool:
    """
    Elimina un huésped de la base de datos por su DNI.
    """
    db_huesped = db.query(Huesped).filter(Huesped.DNI == dni).first()
    
    if not db_huesped:
        return False
    
    db.delete(db_huesped)
    db.commit()
    return True


def contar_huespedes(db: Session, estado: Optional[str] = None) -> int:
    """
    Cuenta el número total de huéspedes, opcionalmente filtrados por estado.
    """
    query = db.query(Huesped)
    
    if estado:
        query = query.filter(Huesped.estado == estado)
    
    return query.count()