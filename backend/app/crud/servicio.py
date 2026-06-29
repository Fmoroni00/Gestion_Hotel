from datetime import datetime
from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session

from app.models import Servicio, Reserva, Consumo
from app.schemas.servicio import ServicioCreate, ConsumoCreate


def obtener_servicios(db: Session) -> List[Servicio]:
    return db.query(Servicio).order_by(Servicio.nombre).all()


def obtener_servicio_por_id(db: Session, id_servicio: int) -> Servicio:
    return db.query(Servicio).filter(Servicio.ID_Servicio == id_servicio).first()


def crear_servicio(db: Session, servicio: ServicioCreate) -> Servicio:
    db_servicio = Servicio(
        nombre=servicio.nombre,
        tipo=servicio.tipo,
        descripcion=servicio.descripcion,
        precio_unitario=servicio.precio_unitario
    )
    db.add(db_servicio)
    db.commit()
    db.refresh(db_servicio)
    return db_servicio


def registrar_consumo_reserva(db: Session, consumo: ConsumoCreate) -> Consumo:
    reserva = db.query(Reserva).filter(Reserva.ID_Reserva == consumo.ID_Reserva).first()
    if not reserva:
        raise ValueError(f"Reserva con ID {consumo.ID_Reserva} no encontrada")

    servicio = db.query(Servicio).filter(Servicio.ID_Servicio == consumo.ID_Servicio).first()
    if not servicio:
        raise ValueError("Servicio no encontrado")

    precio_unitario = servicio.precio_unitario
    if precio_unitario is None:
        raise ValueError("El servicio no tiene precio unitario configurado")

    db_consumo = Consumo(
        ID_Reserva=consumo.ID_Reserva,
        ID_Servicio=consumo.ID_Servicio,
        cantidad=consumo.cantidad,
        fecha=datetime.utcnow(),
        precio_unitario=precio_unitario
    )
    db.add(db_consumo)
    db.commit()
    db.refresh(db_consumo)
    return db_consumo


def obtener_consumos_por_reserva(db: Session, id_reserva: int) -> List[Consumo]:
    return db.query(Consumo).filter(Consumo.ID_Reserva == id_reserva).order_by(Consumo.fecha).all()
