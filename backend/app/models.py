# Modelo de dominio para el PMS hotelero
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Enum, 
    Numeric, 
    DateTime, 
    Date, 
    ForeignKey, 
    UniqueConstraint, 
    CheckConstraint, 
    text,
    func
)
from sqlalchemy.orm import relationship
from app.core.database import Base

class Usuario(Base):
    __tablename__ = "Usuario"

    ID_Usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(150), unique=True, nullable=False)
    rol = Column(Enum('personal_limpieza', 'administrador', 'recepcionista'), nullable=False)
    activo = Column(Enum('activo', 'inactivo'), default='activo')
    
    # ============================================================
    # MODIFICACIÓN CRUCIAL: Añadir esta columna tal cual tu MySQL
    # ============================================================
    password_hash = Column(String(255), nullable=True) 
    # Es nullable=True porque los Huéspedes no usan esta tabla ni contraseña
    
    # Columnas de auditoría temporal (opcionales si ya las tienes)
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ============================================================
# 2. SUBTIPOS DE USUARIO (Herencia por tabla por subtipo)
# ============================================================
class Personal_Limpieza(Usuario):
    __tablename__ = 'Personal_Limpieza'
    
    ID_Usuario = Column(
        Integer, 
        ForeignKey('Usuario.ID_Usuario', ondelete='CASCADE', onupdate='CASCADE'), 
        primary_key=True
    )

    __mapper_args__ = {
        'polymorphic_identity': 'personal_limpieza'
    }


class Administrador(Usuario):
    __tablename__ = 'Administrador'
    
    ID_Usuario = Column(
        Integer, 
        ForeignKey('Usuario.ID_Usuario', ondelete='CASCADE', onupdate='CASCADE'), 
        primary_key=True
    )

    __mapper_args__ = {
        'polymorphic_identity': 'administrador'
    }


class Recepcionista(Usuario):
    __tablename__ = 'Recepcionista'
    
    ID_Usuario = Column(
        Integer, 
        ForeignKey('Usuario.ID_Usuario', ondelete='CASCADE', onupdate='CASCADE'), 
        primary_key=True
    )

    __mapper_args__ = {
        'polymorphic_identity': 'recepcionista'
    }


# ============================================================
# 3. HABITACIÓN
# ============================================================
class Habitacion(Base):
    __tablename__ = 'Habitacion'
    
    ID_Habitacion = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(Integer, nullable=False, unique=True)
    tipo = Column(String(50), nullable=False)  # simple, doble, suite, etc.
    estado = Column(Enum('disponible', 'ocupada', 'mantenimiento'), nullable=False, server_default=text("'disponible'"))
    precio_noche = Column(Numeric(10, 2), nullable=False)

    # Relaciones virtuales
    reservas = relationship("Reserva", back_populates="habitacion")
    historiales = relationship("Historial", back_populates="habitacion")


# ============================================================
# 4. HISTORIAL
# ============================================================
class Historial(Base):
    __tablename__ = 'Historial'
    
    ID_Historial = Column(Integer, primary_key=True, autoincrement=True)
    fecha_hora = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    accion = Column(String(255), nullable=False)
    
    # Consolidated user reference after migration
    ID_Usuario = Column(
        Integer,
        ForeignKey('Usuario.ID_Usuario', ondelete='SET NULL', onupdate='CASCADE'),
        nullable=True
    )
    ID_Habitacion = Column(
        Integer, 
        ForeignKey('Habitacion.ID_Habitacion', ondelete='SET NULL', onupdate='CASCADE'), 
        nullable=True
    )

    # Relaciones virtuales para auditorías rápidas en Python
    usuario = relationship("Usuario")
    habitacion = relationship("Habitacion", back_populates="historiales")


# ============================================================
# 5. HUÉSPED
# ============================================================
class Huesped(Base):
    __tablename__ = 'Huesped'
    
    DNI = Column(String(20), primary_key=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo = Column(String(150), unique=True, nullable=True)
    telefono = Column(String(20), nullable=True)
    estado = Column(Enum('activo', 'inactivo'), nullable=False, server_default=text("'activo'"))

    # Relaciones virtuales
    codigos_acceso = relationship("Codigo_Acceso", back_populates="huesped", cascade="all, delete-orphan")
    reservas = relationship("Reserva", back_populates="huesped")


# ============================================================
# 6. CÓDIGO DE ACCESO
# ============================================================
class Codigo_Acceso(Base):
    __tablename__ = 'Codigo_Acceso'
    
    ID_Codigo = Column(Integer, primary_key=True, autoincrement=True)
    valor = Column(String(100), nullable=False, unique=True)
    estado = Column(Enum('activo', 'inactivo', 'expirado'), nullable=False, server_default=text("'activo'"))
    DNI = Column(
        String(20), 
        ForeignKey('Huesped.DNI', ondelete='CASCADE', onupdate='CASCADE'), 
        nullable=False
    )

    # Relación hacia Huésped
    huesped = relationship("Huesped", back_populates="codigos_acceso")


# ============================================================
# 7. RESERVA
# ============================================================
class Reserva(Base):
    __tablename__ = 'Reserva'
    
    ID_Reserva = Column(Integer, primary_key=True, autoincrement=True)
    fecha_entrada = Column(DateTime, nullable=False)
    fecha_salida = Column(DateTime, nullable=False)
    estado = Column(
        Enum('pendiente', 'confirmada', 'activa', 'finalizada', 'cancelada'), 
        nullable=False, 
        server_default=text("'pendiente'")
    )
    DNI = Column(String(20), ForeignKey('Huesped.DNI', onupdate='CASCADE'), nullable=False)
    ID_Habitacion = Column(Integer, ForeignKey('Habitacion.ID_Habitacion', onupdate='CASCADE'), nullable=False)
    ID_Recepcionista = Column(Integer, ForeignKey('Recepcionista.ID_Usuario', onupdate='CASCADE'), nullable=False)

    # Restricciones de la tabla (CHECK constraint)
    __table_args__ = (
        CheckConstraint('fecha_salida > fecha_entrada', name='chk_fechas'),
    )

    # Relaciones bidireccionales de core operativo
    huesped = relationship("Huesped", back_populates="reservas")
    habitacion = relationship("Habitacion", back_populates="reservas")
    recepcionista = relationship("Recepcionista")
    
    # Relaciones 0..1 o 0..N hacia otros módulos transaccionales
    asignacion_parking = relationship("Asignacion_Parking", back_populates="reserva", uselist=False, cascade="all, delete-orphan")
    notas_servicio = relationship("Nota_Servicio", back_populates="reserva", cascade="all, delete-orphan")
    boletas = relationship("Boleta", back_populates="reserva")


# ============================================================
# 8. PARKING
# ============================================================
class Parking(Base):
    __tablename__ = 'Parking'
    
    ID_Parking = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(Integer, nullable=False, unique=True)
    estado = Column(Enum('disponible', 'ocupado', 'mantenimiento'), nullable=False, server_default=text("'disponible'"))

    asignaciones = relationship("Asignacion_Parking", back_populates="parking")


# ============================================================
# 9. ASIGNACIÓN PARKING (Relación 0..1 estructurada por el UNIQUE)
# ============================================================
class Asignacion_Parking(Base):
    __tablename__ = 'Asignacion_Parking'
    
    ID_Asignacion = Column(Integer, primary_key=True, autoincrement=True)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    
    # ID_Reserva es UNIQUE para forzar la relación estricta de 0 o 1 espacio por reserva
    ID_Reserva = Column(
        Integer, 
        ForeignKey('Reserva.ID_Reserva', ondelete='CASCADE', onupdate='CASCADE'), 
        nullable=False, 
        unique=True  
    )
    ID_Parking = Column(Integer, ForeignKey('Parking.ID_Parking', onupdate='CASCADE'), nullable=False)

    __table_args__ = (
        CheckConstraint('fecha_fin > fecha_inicio', name='chk_parking_fechas'),
    )

    reserva = relationship("Reserva", back_populates="asignacion_parking")
    parking = relationship("Parking", back_populates="asignaciones")


# ============================================================
# AMENIDADES
# ============================================================
class Amenidad(Base):
    __tablename__ = 'Amenidad'

    ID_Amenidad = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)


class Habitacion_Amenidad(Base):
    __tablename__ = 'Habitacion_Amenidad'

    ID_Habitacion = Column(Integer, ForeignKey('Habitacion.ID_Habitacion', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    ID_Amenidad = Column(Integer, ForeignKey('Amenidad.ID_Amenidad', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)

    # Opcional: relaciones
    amenidad = relationship('Amenidad')
    habitacion_rel = relationship('Habitacion')


# ============================================================
# 10. SERVICIO
# ============================================================
class Servicio(Base):
    __tablename__ = 'Servicio'
    
    ID_Servicio = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    estado = Column(Enum('activo', 'inactivo'), server_default=text("'activo'"))
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    descripcion = Column(String(255), nullable=True)
    fecha_creacion = Column(DateTime, server_default=func.now())

    notas_servicio = relationship("Nota_Servicio", back_populates="servicio")


# ============================================================
# 11. NOTA DE SERVICIO
# ============================================================
class Nota_Servicio(Base):
    __tablename__ = 'Nota_Servicio'
    
    ID_Nota = Column(Integer, primary_key=True, autoincrement=True)
    estado = Column(Enum('pendiente', 'entregado', 'completado', 'cancelado'), nullable=False, server_default=text("'pendiente'"))
    fecha_hora = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    concepto = Column(String(255), nullable=True)
    descripcion = Column(String(255), nullable=True)
    motivo_cancelacion = Column(String(255), nullable=True)
    
    ID_Reserva = Column(
        Integer, 
        ForeignKey('Reserva.ID_Reserva', ondelete='CASCADE', onupdate='CASCADE'), 
        nullable=False
    )
    ID_Servicio = Column(Integer, ForeignKey('Servicio.ID_Servicio', onupdate='CASCADE'), nullable=True)

    reserva = relationship("Reserva", back_populates="notas_servicio")
    servicio = relationship("Servicio", back_populates="notas_servicio")


# ============================================================
# 12. CONSUMO DE SERVICIO / EXTRAS
# ============================================================
class Consumo(Base):
    __tablename__ = 'Consumo'

    ID_Consumo = Column(Integer, primary_key=True, autoincrement=True)
    ID_Reserva = Column(
        Integer,
        ForeignKey('Reserva.ID_Reserva', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )
    ID_Servicio = Column(
        Integer,
        ForeignKey('Servicio.ID_Servicio', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )
    cantidad = Column(Integer, nullable=False, server_default=text('1'))
    fecha = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    precio_unitario = Column(Numeric(10, 2), nullable=False)

    reserva = relationship("Reserva")
    servicio = relationship("Servicio")


# ============================================================
# 13. BOLETA
# ============================================================
class Boleta(Base):
    __tablename__ = 'Boleta'
    
    ID_Boleta = Column(Integer, primary_key=True, autoincrement=True)
    serie = Column(String(10), nullable=False)
    correlativo = Column(Integer, nullable=False)
    fecha = Column(Date, nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    estado = Column(Enum('generada', 'pagada', 'cancelada'), nullable=False, server_default=text("'generada'"))
    # Parking info migrated to asignacion_parking. Keep reference by FK.
    ID_Asignacion = Column(Integer, ForeignKey('Asignacion_Parking.ID_Asignacion', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    
    # ON DELETE RESTRICT impide borrar reservas facturadas por motivos financieros y auditorías
    ID_Reserva = Column(
        Integer, 
        ForeignKey('Reserva.ID_Reserva', ondelete='RESTRICT', onupdate='CASCADE'), 
        nullable=False
    )

    # Restricción UNIQUE compuesta (serie, correlativo)
    __table_args__ = (
        UniqueConstraint('serie', 'correlativo', name='uq_boleta'),
    )

    reserva = relationship("Reserva", back_populates="boletas")
    asignacion = relationship('Asignacion_Parking')


class Configuracion(Base):
    __tablename__ = 'Configuracion'

    ID_Configuracion = Column(Integer, primary_key=True, autoincrement=True)
    nombre_hotel = Column(String(100), nullable=False, server_default=text("'Hotel PMS'"))
    hora_checkin = Column(String(5), nullable=False, server_default=text("'15:00'"))
    hora_checkout = Column(String(5), nullable=False, server_default=text("'12:00'"))
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())
