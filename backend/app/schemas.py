from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from enum import Enum

# ============================================================
# ENUMS PARA VALIDACIÓN EXACTA
# ============================================================
class RolUsuario(str, Enum):
    personal_limpieza = 'personal_limpieza'
    administrador = 'administrador'
    recepcionista = 'recepcionista'

class EstadoActivoInactivo(str, Enum):
    activo = 'activo'
    inactivo = 'inactivo'

class EstadoHabitacion(str, Enum):
    disponible = 'disponible'
    ocupada = 'ocupada'
    mantenimiento = 'mantenimiento'

class EstadoReserva(str, Enum):
    pendiente = 'pendiente'
    confirmada = 'confirmada'
    activa = 'activa'
    finalizada = 'finalizada'
    cancelada = 'cancelada'

class EstadoParking(str, Enum):
    disponible = 'disponible'
    ocupado = 'ocupado'
    mantenimiento = 'mantenimiento'

class EstadoNotaServicio(str, Enum):
    pendiente = 'pendiente'
    entregado = 'entregado'
    cancelado = 'cancelado'

class EstadoCodigoAcceso(str, Enum):
    activo = 'activo'
    inactivo = 'inactivo'
    expirado = 'expirado'


# ============================================================
# 1. ESQUEMAS DE USUARIO Y SUBTIPOS
# ============================================================
class UsuarioBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    correo: EmailStr = Field(..., max_length=150)
    rol: RolUsuario
    estado: EstadoActivoInactivo = EstadoActivoInactivo.activo

class UsuarioCreate(UsuarioBase):
    contrasena: str = Field(..., min_length=3, description="Contraseña en texto plano que será encriptada por el backend")

class UsuarioResponse(UsuarioBase):
    ID_Usuario: int
    
    # Configuración para permitir leer modelos de SQLAlchemy directamente
    model_config = ConfigDict(from_attributes=True)

# Esquemas específicos para los subtipos si requirieran lógica extra en el futuro
class PersonalLimpiezaResponse(UsuarioResponse):
    pass

class AdministradorResponse(UsuarioResponse):
    pass

class RecepcionistaResponse(UsuarioResponse):
    pass


# ============================================================
# 2. ESQUEMAS DE HABITACIÓN
# ============================================================
class HabitacionBase(BaseModel):
    numero: int
    tipo: str = Field(..., max_length=50)
    estado: EstadoHabitacion = EstadoHabitacion.disponible
    precio_noche: Decimal = Field(..., max_digits=10, decimal_places=2)

class HabitacionCreate(HabitacionBase):
    pass

class HabitacionResponse(HabitacionBase):
    ID_Habitacion: int
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 3. ESQUEMAS DE HUÉSPED
# ============================================================
class HuespedBase(BaseModel):
    DNI: str = Field(..., max_length=20)
    nombre: str = Field(..., max_length=100)
    apellido: str = Field(..., max_length=100)
    correo: Optional[EmailStr] = Field(None, max_length=150)
    telefono: Optional[str] = Field(None, max_length=20)
    estado: EstadoActivoInactivo = EstadoActivoInactivo.activo

class HuespedCreate(HuespedBase):
    pass

class HuespedResponse(HuespedBase):
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 4. ESQUEMAS DE CÓDIGO DE ACCESO
# ============================================================
class CodigoAccesoBase(BaseModel):
    valor: str = Field(..., max_length=100)
    estado: EstadoCodigoAcceso = EstadoCodigoAcceso.activo
    DNI: str = Field(..., max_length=20)

class CodigoAccesoCreate(CodigoAccesoBase):
    pass

class CodigoAccesoResponse(CodigoAccesoBase):
    ID_Codigo: int
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 5. ESQUEMAS DE PARKING
# ============================================================
class ParkingBase(BaseModel):
    numero: int
    estado: EstadoParking = EstadoParking.disponible

class ParkingCreate(ParkingBase):
    pass

class ParkingResponse(ParkingBase):
    ID_Parking: int
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 6. ESQUEMAS DE RESERVA
# ============================================================
class ReservaBase(BaseModel):
    fecha_entrada: datetime
    fecha_salida: datetime
    estado: EstadoReserva = EstadoReserva.pendiente
    DNI: str = Field(..., max_length=20)
    ID_Habitacion: int
    ID_Recepcionista: int

class ReservaCreate(ReservaBase):
    pass

class ReservaResponse(ReservaBase):
    ID_Reserva: int
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 7. ESQUEMAS DE ASIGNACIÓN PARKING
# ============================================================
class AsignacionParkingBase(BaseModel):
    fecha_inicio: datetime
    fecha_fin: datetime
    ID_Reserva: int
    ID_Parking: int

class AsignacionParkingCreate(AsignacionParkingBase):
    pass

class AsignacionParkingResponse(AsignacionParkingBase):
    ID_Asignacion: int
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 8. ESQUEMAS DE SERVICIO
# ============================================================
class ServicioBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    tipo: str = Field(..., max_length=50)
    estado: EstadoActivoInactivo = EstadoActivoInactivo.activo
    precio_unitario: Decimal = Field(..., max_digits=10, decimal_places=2)

class ServicioCreate(ServicioBase):
    pass

class ServicioResponse(ServicioBase):
    ID_Servicio: int
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 9. ESQUEMAS DE NOTA DE SERVICIO
# ============================================================
class NotaServicioBase(BaseModel):
    estado: EstadoNotaServicio = EstadoNotaServicio.pendiente
    ID_Reserva: int
    ID_Servicio: int

class NotaServicioCreate(NotaServicioBase):
    pass

class NotaServicioResponse(NotaServicioBase):
    ID_Nota: int
    fecha_hora: datetime
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 10. ESQUEMAS DE BOLETA
# ============================================================
class BoletaBase(BaseModel):
    serie: str = Field(..., max_length=10)
    correlativo: int
    fecha: date
    fecha_emision: Optional[datetime] = None
    subtotal: Optional[Decimal] = None
    igv: Optional[Decimal] = None
    total: Decimal = Field(..., max_digits=10, decimal_places=2)
    ID_Reserva: int
    ID_Asignacion: Optional[int] = None

class BoletaCreate(BoletaBase):
    pass

class BoletaResponse(BoletaBase):
    ID_Boleta: int
    model_config = ConfigDict(from_attributes=True)


class BoletaResumenResponse(BaseModel):
    ID_Boleta: int
    numero_habitacion: int
    monto: Decimal
    fecha: date
    estado_pago: str


class ConfiguracionBase(BaseModel):
    nombre_hotel: str = Field(..., max_length=100)
    hora_checkin: str = Field(..., max_length=5)
    hora_checkout: str = Field(..., max_length=5)


class ConfiguracionResponse(ConfiguracionBase):
    ID_Configuracion: int
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 11. ESQUEMAS DE HISTORIAL (AUDITORÍA)
# ============================================================
class HistorialBase(BaseModel):
    accion: str = Field(..., max_length=255)
    ID_Usuario: Optional[int] = None
    ID_Habitacion: Optional[int] = None

class HistorialCreate(HistorialBase):
    pass

class HistorialResponse(HistorialBase):
    ID_Historial: int
    fecha_hora: datetime
    model_config = ConfigDict(from_attributes=True)