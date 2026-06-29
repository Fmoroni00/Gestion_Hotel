# Scripts de Migración - Hotel Proyecto

Este directorio contiene 5 scripts de migración para reestructurar y optimizar la base de datos del proyecto Hotel.

## Requisitos

- Python 3.6+
- mysql-connector-python
- Base de datos MySQL local en 127.0.0.1:3306

## Instalación de Dependencias

```bash
pip install mysql-connector-python
```

## Credenciales de Conexión

Todos los scripts usan las siguientes credenciales (del archivo .env):
- **Host**: localhost (127.0.0.1)
- **User**: root
- **Password**: 1234
- **Database**: hotel_db

## Scripts de Migración

### 1. migracion_01_amenidades.py
**Propósito**: Crear tablas de amenidades y migrar de modelo plano a relacional

**Acciones**:
- Crea tabla `amenidad` (almacena amenidades únicas)
- Crea tabla `habitacion_amenidad` (relación M:N)
- Migra datos de `habitacion.amenidades` (TEXT) a las nuevas tablas
- Elimina columna `amenidades` de habitacion

**Ejecución**:
```bash
python migracion_01_amenidades.py
```

---

### 2. migracion_02_parking.py
**Propósito**: Verificar integridad y limpiar tabla parking

**Acciones**:
- Verifica integridad referencial de `asignacion_parking`
- Detecta asignaciones duplicadas
- Elimina columna `reserva_id` de parking

**Ejecución**:
```bash
python migracion_02_parking.py
```

---

### 3. migracion_03_boleta.py
**Propósito**: Crear respaldo de datos y limpiar tabla boleta

**Acciones**:
- Crea tabla `boleta_backup` (respaldo histórico)
- Guarda datos de `cochera_asignada` y `costo_parking`
- Elimina columnas `cochera_asignada` y `costo_parking` de boleta
- Incluye timestamp de respaldo para auditoría

**Ejecución**:
```bash
python migracion_03_boleta.py
```

---

### 4. migracion_04_historial.py
**Propósito**: Consolidar referencias de usuarios en historial

**Acciones**:
- Agrega columna `ID_Usuario` a historial
- Migra datos de `ID_Administrador`, `ID_Recepcionista`, `ID_PL` a `ID_Usuario`
- Elimina Foreign Keys antiguas
- Agrega nueva FK: ID_Usuario → usuario(ID_Usuario)
- Elimina columnas antiguas

**Ejecución**:
```bash
python migracion_04_historial.py
```

---

### 5. migracion_05_indices.py
**Propósito**: Crear índices para optimizar consultas

**Índices Creados**:
- `idx_reserva_dni` en reserva(DNI)
- `idx_reserva_habitacion` en reserva(ID_Habitacion)
- `idx_consumo_reserva` en consumo(ID_Reserva)
- `idx_consumo_servicio` en consumo(ID_Servicio)
- `idx_historial_usuario` en historial(ID_Usuario)
- `idx_asignacion_reserva` en asignacion_parking(ID_Reserva)
- `idx_asignacion_parking` en asignacion_parking(ID_Parking)

**Ejecución**:
```bash
python migracion_05_indices.py
```

---

## Orden de Ejecución Recomendado

```bash
# 1. Migrations de estructura
python migracion_01_amenidades.py
python migracion_02_parking.py
python migracion_03_boleta.py
python migracion_04_historial.py

# 2. Optimización
python migracion_05_indices.py
```

## Características Comunes

Todos los scripts incluyen:
- ✓ Manejo de errores con try/except
- ✓ Rollback automático en caso de fallo
- ✓ Verificación de existencia de tablas/columnas
- ✓ Verificación de Foreign Keys y índices antes de crear
- ✓ Mensajes descriptivos del progreso (✓/✗)
- ✓ Desconexión automática de la base de datos

## Monitoreo y Verificación

Cada script proporciona:
- Conteo de registros procesados
- Información de integridad referencial
- Verificación de cambios aplicados
- Estadísticas de la operación

## Recuperación en Caso de Error

Si un script falla:
1. Se hace rollback automático de la transacción
2. Los datos no se modifican
3. Revisa el mensaje de error para diagnosticar el problema
4. Puedes ejecutar el script nuevamente después de corregir

## Respaldos

La migración `migracion_03_boleta.py` crea automáticamente:
- Tabla `boleta_backup` con todos los datos históricos
- Útil para auditoría y consultas retrospectivas

## Soporte

Para problemas:
1. Verifica que MySQL esté en ejecución
2. Valida credenciales en .env
3. Asegúrate que la base de datos `hotel_db` exista
4. Ejecuta los scripts en el orden recomendado
