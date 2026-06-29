from datetime import date, datetime
from decimal import Decimal
from typing import Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Reserva, Boleta
from app.crud.servicio import obtener_consumos_por_reserva


def _calcular_monto_servicios(consumos) -> Decimal:
    total = Decimal(0)
    for consumo in consumos:
        total += Decimal(consumo.precio_unitario) * consumo.cantidad
    return total


def _generar_numero_boleta(db: Session) -> Tuple[str, int, str]:
    serie = "B001"
    ultimo_correlativo = db.query(func.max(Boleta.correlativo)).filter(Boleta.serie == serie).scalar()
    siguiente = (ultimo_correlativo or 0) + 1
    numero_boleta = f"{serie}-{siguiente:06d}"
    return serie, siguiente, numero_boleta


def obtener_estado_cuenta_reserva(db: Session, id_reserva: int):
    reserva = db.query(Reserva).filter(Reserva.ID_Reserva == id_reserva).first()
    if not reserva:
        raise ValueError(f"Reserva con ID {id_reserva} no encontrada")

    consumos = obtener_consumos_por_reserva(db, id_reserva)
    
    # Cálculo dinámico de días
    dias = (datetime.now() - reserva.fecha_entrada).days
    if dias <= 0:
        dias = 1

    precio_noche = reserva.habitacion.precio_noche
    monto_hospedaje = Decimal(dias) * Decimal(precio_noche)
    monto_servicios = _calcular_monto_servicios(consumos)
    monto_total = monto_hospedaje + monto_servicios

    # Obtener estado de boleta si existe
    boleta = db.query(Boleta).filter(Boleta.ID_Reserva == id_reserva).first()
    estado_boleta = boleta.estado if boleta else "generada"

    return {
        "ID_Reserva": id_reserva,
        "monto_hospedaje": float(monto_hospedaje),
        "monto_servicios": float(monto_servicios),
        "monto_total": float(monto_total),
        "consumos": consumos,
        "estado_reserva": reserva.estado,
        "estado_boleta": estado_boleta
    }


def generar_boleta_final(db: Session, id_reserva: int) -> Boleta:
    reserva = db.query(Reserva).filter(Reserva.ID_Reserva == id_reserva).first()
    if not reserva:
        raise ValueError(f"Reserva con ID {id_reserva} no encontrada")

    consumos = obtener_consumos_por_reserva(db, id_reserva)
    
    # Cálculo dinámico de días
    dias = (datetime.now() - reserva.fecha_entrada).days
    if dias <= 0:
        dias = 1

    precio_noche = reserva.habitacion.precio_noche
    monto_hospedaje = Decimal(dias) * Decimal(precio_noche)
    monto_servicios = _calcular_monto_servicios(consumos)
    monto_total = monto_hospedaje + monto_servicios

    boleta_existente = db.query(Boleta).filter(Boleta.ID_Reserva == id_reserva).first()
    if boleta_existente:
        return boleta_existente

    serie, correlativo, numero_boleta = _generar_numero_boleta(db)
    boleta = Boleta(
        serie=serie,
        correlativo=correlativo,
        fecha=date.today(),
        total=monto_total,
        ID_Reserva=id_reserva
    )
    db.add(boleta)
    db.commit()
    db.refresh(boleta)
    return boleta
