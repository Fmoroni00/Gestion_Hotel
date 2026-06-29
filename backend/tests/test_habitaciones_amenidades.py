from app.models import Habitacion, Amenidad
from app.schemas.habitacion import HabitacionResponse


def test_habitacion_response_incluye_amenidades():
    habitacion = Habitacion(
        ID_Habitacion=1,
        numero=101,
        tipo='simple',
        estado='disponible',
        precio_noche=120,
    )
    habitacion.amenidades_rel = [Amenidad(ID_Amenidad=1, nombre='Wi-Fi')]

    response = HabitacionResponse.model_validate(habitacion)

    assert response.amenidades == ['Wi-Fi']
