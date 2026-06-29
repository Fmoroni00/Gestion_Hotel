import os
import mysql.connector

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '1234'),
    'database': os.getenv('DB_NAME', 'hotel_db'),
}


def get_conn():
    return mysql.connector.connect(**DB_CONFIG)


def table_exists(cursor, table_name):
    cursor.execute("SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s", (DB_CONFIG['database'], table_name))
    return cursor.fetchone()[0] > 0


def column_exists(cursor, table_name, column_name):
    cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s", (DB_CONFIG['database'], table_name, column_name))
    return cursor.fetchone()[0] > 0


def fk_exists(cursor, table_name, column_name, ref_table, ref_column):
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s AND REFERENCED_TABLE_NAME=%s AND REFERENCED_COLUMN_NAME=%s",
        (DB_CONFIG['database'], table_name, column_name, ref_table, ref_column),
    )
    return cursor.fetchone()[0] > 0


def main():
    print('migracion_01_amenidades: Iniciando')
    conn = get_conn()
    cursor = conn.cursor()
    try:
        # Crear amenidad
        print('Verificando tabla amenidad...')
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS amenidad (ID_Amenidad INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(100) NOT NULL UNIQUE) ENGINE=InnoDB"
        )

        # Crear habitacion_amenidad
        print('Verificando tabla habitacion_amenidad...')
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS habitacion_amenidad (ID_Habitacion INT NOT NULL, ID_Amenidad INT NOT NULL, PRIMARY KEY (ID_Habitacion, ID_Amenidad)) ENGINE=InnoDB"
        )

        # Agregar FKs si es posible y no existen
        if table_exists(cursor, 'habitacion') and table_exists(cursor, 'amenidad'):
            if not fk_exists(cursor, 'habitacion_amenidad', 'ID_Amenidad', 'amenidad', 'ID_Amenidad'):
                try:
                    cursor.execute(
                        'ALTER TABLE habitacion_amenidad ADD CONSTRAINT fk_ha_amenidad FOREIGN KEY (ID_Amenidad) REFERENCES amenidad(ID_Amenidad)'
                    )
                    print('FK habitacion_amenidad.ID_Amenidad -> amenidad.ID_Amenidad creada')
                except Exception:
                    print('No se pudo crear FK habitacion_amenidad.ID_Amenidad (posiblemente ya existe)')
            if not fk_exists(cursor, 'habitacion_amenidad', 'ID_Habitacion', 'habitacion', 'ID_Habitacion'):
                try:
                    cursor.execute(
                        'ALTER TABLE habitacion_amenidad ADD CONSTRAINT fk_ha_habitacion FOREIGN KEY (ID_Habitacion) REFERENCES habitacion(ID_Habitacion)'
                    )
                    print('FK habitacion_amenidad.ID_Habitacion -> habitacion.ID_Habitacion creada')
                except Exception:
                    print('No se pudo crear FK habitacion_amenidad.ID_Habitacion (posiblemente ya existe)')

        # Migrar datos desde habitacion.amenidades si existe
        if column_exists(cursor, 'habitacion', 'amenidades'):
            print('Columna habitacion.amenidades encontrada: migrando datos...')
            cursor.execute("SELECT ID_Habitacion, amenidades FROM habitacion WHERE amenidades IS NOT NULL AND amenidades <> ''")
            rows = cursor.fetchall()
            for id_hab, amenidades in rows:
                vals = [a.strip() for a in amenidades.split(',') if a.strip()]
                for nombre in vals:
                    # Insertar amenidad si no existe
                    cursor.execute("INSERT INTO amenidad (nombre) VALUES (%s) ON DUPLICATE KEY UPDATE nombre=nombre", (nombre,))
                    # Obtener id
                    cursor.execute("SELECT ID_Amenidad FROM amenidad WHERE nombre=%s", (nombre,))
                    id_amen = cursor.fetchone()[0]
                    # Insertar relación (ignorar duplicados)
                    try:
                        cursor.execute(
                            "INSERT INTO habitacion_amenidad (ID_Habitacion, ID_Amenidad) VALUES (%s, %s)", (id_hab, id_amen)
                        )
                    except Exception:
                        pass

            # Después de migrar, eliminar columna
            print('Eliminando columna habitacion.amenidades...')
            cursor.execute('ALTER TABLE habitacion DROP COLUMN amenidades')
        else:
            print('Columna habitacion.amenidades no existe; no hay datos que migrar.')

        conn.commit()
        print('migracion_01_amenidades: Completada')
    except Exception as e:
        conn.rollback()
        print('migracion_01_amenidades: ERROR:', e)
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()
"""
Script de migración: Crear tablas de amenidades y migrar datos existentes
Migra de habitacion.amenidades (TEXT con valores separados por coma) a:
- tabla amenidad (almacena amenidades únicas)
- tabla habitacion_amenidad (relación M:N entre habitaciones y amenidades)
"""

import mysql.connector
from mysql.connector import Error
import sys


class MigracionAmenidades:
    """Maneja la migración de amenidades de habitaciones."""
    
    def __init__(self, host='localhost', user='root', password='1234', database='hotel_db'):
        """Inicializa la conexión a la base de datos."""
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conexion = None
        self.cursor = None
    
    def conectar(self):
        """Establece conexión con la base de datos."""
        try:
            self.conexion = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conexion.cursor(dictionary=True)
            print("✓ Conexión a la base de datos exitosa")
            return True
        except Error as e:
            print(f"✗ Error al conectar a la base de datos: {e}")
            return False
    
    def desconectar(self):
        """Cierra la conexión con la base de datos."""
        if self.cursor:
            self.cursor.close()
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
            print("✓ Conexión cerrada")
    
    def crear_tabla_amenidad(self):
        """Crea la tabla amenidad."""
        try:
            sql = """
            CREATE TABLE IF NOT EXISTS amenidad (
                ID_Amenidad INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL UNIQUE
            )
            """
            self.cursor.execute(sql)
            self.conexion.commit()
            print("✓ Tabla 'amenidad' creada exitosamente")
            return True
        except Error as e:
            print(f"✗ Error al crear tabla amenidad: {e}")
            self.conexion.rollback()
            return False
    
    def crear_tabla_habitacion_amenidad(self):
        """Crea la tabla habitacion_amenidad (tabla de unión)."""
        try:
            sql = """
            CREATE TABLE IF NOT EXISTS habitacion_amenidad (
                ID_Habitacion INT NOT NULL,
                ID_Amenidad INT NOT NULL,
                PRIMARY KEY (ID_Habitacion, ID_Amenidad),
                FOREIGN KEY (ID_Habitacion) REFERENCES habitacion(ID_Habitacion) ON DELETE CASCADE,
                FOREIGN KEY (ID_Amenidad) REFERENCES amenidad(ID_Amenidad) ON DELETE CASCADE
            )
            """
            self.cursor.execute(sql)
            self.conexion.commit()
            print("✓ Tabla 'habitacion_amenidad' creada exitosamente")
            return True
        except Error as e:
            print(f"✗ Error al crear tabla habitacion_amenidad: {e}")
            self.conexion.rollback()
            return False
    
    def obtener_habitaciones_con_amenidades(self):
        """Obtiene todas las habitaciones que tienen amenidades."""
        try:
            sql = "SELECT ID_Habitacion, amenidades FROM habitacion WHERE amenidades IS NOT NULL AND amenidades != ''"
            self.cursor.execute(sql)
            habitaciones = self.cursor.fetchall()
            print(f"✓ Se encontraron {len(habitaciones)} habitaciones con amenidades")
            return habitaciones
        except Error as e:
            print(f"✗ Error al obtener habitaciones: {e}")
            return []
    
    def obtener_o_crear_amenidad(self, nombre_amenidad):
        """Obtiene el ID de una amenidad o la crea si no existe."""
        nombre_amenidad = nombre_amenidad.strip()
        
        try:
            # Buscar si ya existe
            sql_select = "SELECT ID_Amenidad FROM amenidad WHERE nombre = %s"
            self.cursor.execute(sql_select, (nombre_amenidad,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return resultado['ID_Amenidad']
            
            # Si no existe, crearla
            sql_insert = "INSERT INTO amenidad (nombre) VALUES (%s)"
            self.cursor.execute(sql_insert, (nombre_amenidad,))
            # No hacer commit aquí, se hace al final del lote
            
            return self.cursor.lastrowid
        except Error as e:
            print(f"✗ Error al obtener/crear amenidad '{nombre_amenidad}': {e}")
            raise
    
    def migrar_amenidades(self):
        """Migra las amenidades de la columna texto a las nuevas tablas."""
        try:
            habitaciones = self.obtener_habitaciones_con_amenidades()
            
            if not habitaciones:
                print("✓ No hay amenidades para migrar")
                return True
            
            amenidades_procesadas = 0
            relaciones_creadas = 0
            
            for habitacion in habitaciones:
                id_habitacion = habitacion['ID_Habitacion']
                amenidades_texto = habitacion['amenidades']
                
                # Parsear las amenidades (separadas por coma)
                amenidades_lista = [a.strip() for a in amenidades_texto.split(',')]
                
                for amenidad_nombre in amenidades_lista:
                    if not amenidad_nombre:  # Ignorar vacías
                        continue
                    
                    try:
                        # Obtener o crear la amenidad
                        id_amenidad = self.obtener_o_crear_amenidad(amenidad_nombre)
                        
                        # Insertar la relación en habitacion_amenidad
                        sql_relacion = """
                        INSERT IGNORE INTO habitacion_amenidad (ID_Habitacion, ID_Amenidad)
                        VALUES (%s, %s)
                        """
                        self.cursor.execute(sql_relacion, (id_habitacion, id_amenidad))
                        relaciones_creadas += 1
                        amenidades_procesadas += 1
                    
                    except Error as e:
                        print(f"✗ Error procesando amenidad '{amenidad_nombre}' en habitación {id_habitacion}: {e}")
                        raise
            
            self.conexion.commit()
            print(f"✓ {amenidades_procesadas} amenidades procesadas")
            print(f"✓ {relaciones_creadas} relaciones creadas en habitacion_amenidad")
            return True
        
        except Error as e:
            print(f"✗ Error durante la migración de amenidades: {e}")
            self.conexion.rollback()
            return False
    
    def eliminar_columna_amenidades(self):
        """Elimina la columna amenidades de la tabla habitacion."""
        try:
            sql = "ALTER TABLE habitacion DROP COLUMN amenidades"
            self.cursor.execute(sql)
            self.conexion.commit()
            print("✓ Columna 'amenidades' eliminada de la tabla 'habitacion'")
            return True
        except Error as e:
            print(f"✗ Error al eliminar columna amenidades: {e}")
            self.conexion.rollback()
            return False
    
    def verificar_migracion(self):
        """Verifica que la migración se completó correctamente."""
        try:
            # Contar amenidades
            self.cursor.execute("SELECT COUNT(*) as total FROM amenidad")
            total_amenidades = self.cursor.fetchone()['total']
            
            # Contar relaciones
            self.cursor.execute("SELECT COUNT(*) as total FROM habitacion_amenidad")
            total_relaciones = self.cursor.fetchone()['total']
            
            print("\n" + "="*50)
            print("RESULTADO DE LA MIGRACIÓN")
            print("="*50)
            print(f"Total de amenidades únicas: {total_amenidades}")
            print(f"Total de relaciones habitación-amenidad: {total_relaciones}")
            
            # Mostrar algunas amenidades como ejemplo
            self.cursor.execute("SELECT * FROM amenidad LIMIT 5")
            amenidades = self.cursor.fetchall()
            if amenidades:
                print("\nPrimeras amenidades creadas:")
                for amenidad in amenidades:
                    print(f"  - {amenidad['nombre']}")
            
            return True
        except Error as e:
            print(f"✗ Error al verificar migración: {e}")
            return False
    
    def ejecutar_migracion(self):
        """Ejecuta el proceso completo de migración."""
        print("="*50)
        print("INICIANDO MIGRACIÓN DE AMENIDADES")
        print("="*50 + "\n")
        
        # Paso 1: Conectar
        if not self.conectar():
            return False
        
        try:
            # Paso 2: Crear tablas
            print("\n[1/5] Creando tabla amenidad...")
            if not self.crear_tabla_amenidad():
                return False
            
            print("\n[2/5] Creando tabla habitacion_amenidad...")
            if not self.crear_tabla_habitacion_amenidad():
                return False
            
            # Paso 3: Migrar datos
            print("\n[3/5] Migrando datos...")
            if not self.migrar_amenidades():
                return False
            
            # Paso 4: Eliminar columna antigua
            print("\n[4/5] Eliminando columna antigua...")
            if not self.eliminar_columna_amenidades():
                return False
            
            # Paso 5: Verificar
            print("\n[5/5] Verificando migración...")
            self.verificar_migracion()
            
            print("\n" + "="*50)
            print("✓ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("="*50)
            
            return True
        
        except Exception as e:
            print(f"\n✗ Error inesperado durante la migración: {e}")
            if self.conexion:
                self.conexion.rollback()
            return False
        
        finally:
            self.desconectar()


def main():
    """Función principal."""
    migracion = MigracionAmenidades(
        host='localhost',
        user='root',
        password='1234',
        database='hotel_db'
    )
    
    exito = migracion.ejecutar_migracion()
    
    # Retornar código de salida
    sys.exit(0 if exito else 1)


if __name__ == "__main__":
    main()
