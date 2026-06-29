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


def index_exists(cursor, table, index_name):
    cursor.execute("SELECT COUNT(*) FROM information_schema.STATISTICS WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND INDEX_NAME=%s", (DB_CONFIG['database'], table, index_name))
    return cursor.fetchone()[0] > 0


def main():
    print('migracion_05_indices: Iniciando')
    conn = get_conn()
    cursor = conn.cursor()
    try:
        indices = [
            ('reserva', 'idx_reserva_dni', 'DNI'),
            ('reserva', 'idx_reserva_habitacion', 'ID_Habitacion'),
            ('consumo', 'idx_consumo_reserva', 'ID_Reserva'),
            ('consumo', 'idx_consumo_servicio', 'ID_Servicio'),
            ('historial', 'idx_historial_usuario', 'ID_Usuario'),
            ('asignacion_parking', 'idx_asignacion_reserva', 'ID_Reserva'),
            ('asignacion_parking', 'idx_asignacion_parking', 'ID_Parking'),
            ('boleta', 'idx_boleta_asignacion', 'ID_Asignacion'),
        ]

        for table, idx_name, col in indices:
            if not index_exists(cursor, table, idx_name):
                try:
                    print(f'Creando indice {idx_name} en {table}({col})...')
                    cursor.execute(f'CREATE INDEX {idx_name} ON {table}({col})')
                except Exception as e:
                    print('No se pudo crear indice', idx_name, e)
            else:
                print(f'Indice {idx_name} ya existe en {table}')

        conn.commit()
        print('migracion_05_indices: Completada')
    except Exception as e:
        conn.rollback()
        print('migracion_05_indices: ERROR:', e)
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()
"""
Script de migración: Agregar índices para optimizar consultas
- Agrega índices en tablas principales para mejorar el rendimiento
- Verifica si cada índice ya existe antes de crearlo
"""

import mysql.connector
from mysql.connector import Error
import sys


class MigracionIndices:
    """Maneja la creación de índices en la base de datos."""
    
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
    
    def tabla_existe(self, nombre_tabla):
        """Verifica si una tabla existe en la base de datos."""
        try:
            sql = f"SHOW TABLES LIKE '{nombre_tabla}'"
            self.cursor.execute(sql)
            resultado = self.cursor.fetchone()
            return resultado is not None
        except Error as e:
            print(f"✗ Error al verificar tabla {nombre_tabla}: {e}")
            return False
    
    def indice_existe(self, tabla, nombre_indice):
        """Verifica si un índice ya existe en una tabla."""
        try:
            sql = f"SHOW INDEX FROM {tabla} WHERE Key_name = %s"
            self.cursor.execute(sql, (nombre_indice,))
            resultado = self.cursor.fetchone()
            return resultado is not None
        except Error as e:
            print(f"✗ Error al verificar índice {nombre_indice} en {tabla}: {e}")
            return False
    
    def crear_indice(self, tabla, nombre_indice, columnas):
        """Crea un índice en la tabla especificada."""
        try:
            # Verificar si la tabla existe
            if not self.tabla_existe(tabla):
                print(f"✗ La tabla '{tabla}' no existe")
                return False
            
            # Verificar si el índice ya existe
            if self.indice_existe(tabla, nombre_indice):
                print(f"⚠ El índice '{nombre_indice}' ya existe en '{tabla}'")
                return True
            
            # Crear el índice
            sql = f"CREATE INDEX {nombre_indice} ON {tabla}({columnas})"
            self.cursor.execute(sql)
            self.conexion.commit()
            print(f"✓ Índice '{nombre_indice}' creado en '{tabla}'")
            return True
        
        except Error as e:
            print(f"✗ Error al crear índice {nombre_indice} en {tabla}: {e}")
            self.conexion.rollback()
            return False
    
    def verificar_indices(self):
        """Verifica la información de los índices creados."""
        try:
            print("\n" + "="*60)
            print("INFORMACIÓN DE ÍNDICES CREADOS")
            print("="*60)
            
            indices_info = [
                ('reserva', 'idx_reserva_dni'),
                ('reserva', 'idx_reserva_habitacion'),
                ('consumo', 'idx_consumo_reserva'),
                ('consumo', 'idx_consumo_servicio'),
                ('historial', 'idx_historial_usuario'),
                ('asignacion_parking', 'idx_asignacion_reserva'),
                ('asignacion_parking', 'idx_asignacion_parking'),
            ]
            
            total_indices = 0
            indices_existentes = 0
            
            for tabla, indice in indices_info:
                if self.indice_existe(tabla, indice):
                    print(f"✓ {indice} en {tabla}")
                    indices_existentes += 1
                else:
                    print(f"✗ {indice} en {tabla} NO EXISTE")
                total_indices += 1
            
            print(f"\nTotal: {indices_existentes}/{total_indices} índices presentes")
            
            return indices_existentes == total_indices
        
        except Error as e:
            print(f"✗ Error al verificar índices: {e}")
            return False
    
    def obtener_estadisticas_indices(self):
        """Obtiene estadísticas sobre los índices."""
        try:
            print("\n" + "="*60)
            print("ESTADÍSTICAS DE ÍNDICES")
            print("="*60)
            
            tablas = ['reserva', 'consumo', 'historial', 'asignacion_parking']
            
            for tabla in tablas:
                if not self.tabla_existe(tabla):
                    print(f"\n⚠ Tabla '{tabla}' no existe")
                    continue
                
                print(f"\nTabla: {tabla}")
                sql = f"SHOW INDEX FROM {tabla}"
                self.cursor.execute(sql)
                indices = self.cursor.fetchall()
                
                if not indices:
                    print("  Sin índices")
                    continue
                
                for idx in indices:
                    print(f"  - {idx['Key_name']}: {idx['Column_name']} (Seq: {idx['Seq_in_index']})")
            
            return True
        
        except Error as e:
            print(f"✗ Error al obtener estadísticas: {e}")
            return False
    
    def ejecutar_migracion(self):
        """Ejecuta el proceso completo de creación de índices."""
        print("="*60)
        print("INICIANDO CREACIÓN DE ÍNDICES")
        print("="*60 + "\n")
        
        # Paso 1: Conectar
        if not self.conectar():
            return False
        
        try:
            # Paso 2: Crear índices en reserva
            print("[1/7] Creando índices en reserva...")
            if not self.crear_indice('reserva', 'idx_reserva_dni', 'DNI'):
                print("✗ Error al crear índice en reserva (DNI)")
                return False
            
            if not self.crear_indice('reserva', 'idx_reserva_habitacion', 'ID_Habitacion'):
                print("✗ Error al crear índice en reserva (ID_Habitacion)")
                return False
            
            # Paso 3: Crear índices en consumo
            print("\n[2/7] Creando índices en consumo...")
            if not self.crear_indice('consumo', 'idx_consumo_reserva', 'ID_Reserva'):
                print("✗ Error al crear índice en consumo (ID_Reserva)")
                return False
            
            if not self.crear_indice('consumo', 'idx_consumo_servicio', 'ID_Servicio'):
                print("✗ Error al crear índice en consumo (ID_Servicio)")
                return False
            
            # Paso 4: Crear índice en historial
            print("\n[3/7] Creando índice en historial...")
            if not self.crear_indice('historial', 'idx_historial_usuario', 'ID_Usuario'):
                print("✗ Error al crear índice en historial")
                return False
            
            # Paso 5: Crear índices en asignacion_parking
            print("\n[4/7] Creando índices en asignacion_parking...")
            if not self.crear_indice('asignacion_parking', 'idx_asignacion_reserva', 'ID_Reserva'):
                print("✗ Error al crear índice en asignacion_parking (ID_Reserva)")
                return False
            
            if not self.crear_indice('asignacion_parking', 'idx_asignacion_parking', 'ID_Parking'):
                print("✗ Error al crear índice en asignacion_parking (ID_Parking)")
                return False
            
            # Paso 6: Verificar índices
            print("\n[5/7] Verificando índices...")
            self.verificar_indices()
            
            # Paso 7: Obtener estadísticas
            print("\n[6/7] Obteniendo estadísticas...")
            self.obtener_estadisticas_indices()
            
            print("\n" + "="*60)
            print("✓ CREACIÓN DE ÍNDICES COMPLETADA")
            print("="*60)
            
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
    migracion = MigracionIndices(
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
