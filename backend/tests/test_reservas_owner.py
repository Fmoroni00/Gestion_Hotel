from datetime import date

from app.crud.reserva import crear_nueva_reserva, cambiar_estado_reserva
from app.models import Usuario, Recepcionista, Huesped, Habitacion, Reserva
from app.schemas.reserva import ReservaCreate, EstadoReserva


def test_estado_reserva_acepta_finalizada_y_activa():
    assert EstadoReserva("finalizada") == EstadoReserva.finalizada
    assert EstadoReserva("activa") == EstadoReserva.activa


def test_crear_nueva_reserva_asigna_recepcionista_autenticado(monkeypatch):
    class DummyDB:
        def __init__(self):
            self.committed = False
            self.added = []
            self.refreshed = []

        def query(self, model):
            if model is Huesped:
                return DummyQuery([Huesped(DNI='12345678', nombre='Ana', apellido='Torres', correo='ana@test.com')])
            if model is Habitacion:
                return DummyQuery([Habitacion(ID_Habitacion=1, numero=101, tipo='simple', estado='disponible', precio_noche=100)])
            if model is Recepcionista:
                return DummyQuery([Recepcionista(ID_Usuario=42, nombre='Ana Torres', correo='ana@test.com', rol='recepcionista', activo='activo')])
            raise AssertionError(f'Unexpected model: {model}')

        def commit(self):
            self.committed = True

        def refresh(self, obj):
            self.refreshed.append(obj)

        def add(self, obj):
            self.added.append(obj)

    class DummyQuery:
        def __init__(self, rows):
            self.rows = rows

        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return self.rows[0] if self.rows else None

    db = DummyDB()
    reserva_payload = ReservaCreate(
        DNI='12345678',
        ID_Habitacion=1,
        fecha_entrada=date(2026, 6, 1),
        fecha_salida=date(2026, 6, 3),
        precio_total=200,
        estado='pendiente',
        Huesped_DNI='12345678',
    )

    reserva = crear_nueva_reserva(db, reserva_payload, usuario_actual=Usuario(ID_Usuario=42, nombre='Ana Torres', correo='ana@test.com', rol='recepcionista', activo='activo'))

    assert reserva.ID_Recepcionista == 42
    assert db.committed is True
