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
        # Maneja tanto dict como objetos SQLAlchemy
        precio = consumo.get('precio_unitario') if isinstance(consumo, dict) else consumo.precio_unitario
        cantidad = consumo.get('cantidad') if isinstance(consumo, dict) else consumo.cantidad
        if precio and cantidad:
            total += Decimal(str(precio)) * Decimal(str(cantidad))
    return total


def _generar_numero_boleta(db: Session) -> Tuple[str, int, str]:
    serie = "B001"
    ultimo_correlativo = db.query(func.max(Boleta.correlativo)).filter(Boleta.serie == serie).scalar()
    siguiente = (ultimo_correlativo or 0) + 1
    numero_boleta = f"{serie}-{siguiente:06d}"
    return serie, siguiente, numero_boleta


def _asegurar_boleta_completa(db: Session, boleta: Boleta, subtotal: Decimal, igv: Decimal, monto_total: Decimal) -> None:
    updated = False
    if not boleta:
        return

    if not boleta.serie or boleta.correlativo is None:
        boleta.serie, boleta.correlativo, _ = _generar_numero_boleta(db)
        updated = True

    if not boleta.fecha:
        boleta.fecha = date.today()
        updated = True

    if boleta.subtotal is None or boleta.subtotal == 0:
        boleta.subtotal = subtotal
        updated = True

    if boleta.igv is None or boleta.igv == 0:
        boleta.igv = igv
        updated = True

    if boleta.total is None or boleta.total == 0:
        boleta.total = monto_total
        updated = True

    if not boleta.estado:
        boleta.estado = 'generada'
        updated = True

    if updated:
        db.commit()
        db.refresh(boleta)


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
    subtotal = monto_hospedaje + monto_servicios
    igv = (subtotal * Decimal('0.18')).quantize(Decimal('0.01'))
    monto_total = subtotal + igv

    # Obtener estado de boleta si existe
    boleta = db.query(Boleta).filter(Boleta.ID_Reserva == id_reserva).first()
    if boleta:
        _asegurar_boleta_completa(db, boleta, subtotal, igv, monto_total)
    estado_boleta = boleta.estado if boleta else "generada"

    numero_cochera = None
    if reserva.asignacion_parking and reserva.asignacion_parking.parking:
        numero_cochera = reserva.asignacion_parking.parking.numero

    return {
        "ID_Reserva": id_reserva,
        "monto_hospedaje": float(monto_hospedaje),
        "monto_servicios": float(monto_servicios),
        "subtotal": float(subtotal),
        "igv": float(igv),
        "monto_total": float(monto_total),
        "consumos": consumos,
        "estado_reserva": reserva.estado,
        "estado_boleta": estado_boleta,
        "numero_cochera": numero_cochera
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
    subtotal = monto_hospedaje + monto_servicios
    igv = (subtotal * Decimal('0.18')).quantize(Decimal('0.01'))
    monto_total = subtotal + igv

    boleta_existente = db.query(Boleta).filter(Boleta.ID_Reserva == id_reserva).first()
    if boleta_existente:
        # Asegurar que la boleta existente tenga todos los campos válidos.
        if not boleta_existente.serie:
            boleta_existente.serie, boleta_existente.correlativo, _ = _generar_numero_boleta(db)
        if not boleta_existente.fecha:
            boleta_existente.fecha = date.today()
        if boleta_existente.subtotal is None or boleta_existente.subtotal == 0:
            boleta_existente.subtotal = subtotal
        if boleta_existente.igv is None or boleta_existente.igv == 0:
            boleta_existente.igv = igv
        if boleta_existente.total is None or boleta_existente.total == 0:
            boleta_existente.total = monto_total
        db.commit()
        db.refresh(boleta_existente)
        return boleta_existente

    serie, correlativo, numero_boleta = _generar_numero_boleta(db)
    boleta = Boleta(
        serie=serie,
        correlativo=correlativo,
        fecha=date.today(),
        subtotal=subtotal,
        igv=igv,
        total=monto_total,
        ID_Reserva=id_reserva
    )
    db.add(boleta)
    db.commit()
    db.refresh(boleta)
    return boleta
