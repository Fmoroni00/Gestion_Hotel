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


def column_exists(cursor, table, column):
    cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s", (DB_CONFIG['database'], table, column))
    return cursor.fetchone()[0] > 0


def fk_exists(cursor, table, column, ref_table, ref_column):
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s AND REFERENCED_TABLE_NAME=%s AND REFERENCED_COLUMN_NAME=%s",
        (DB_CONFIG['database'], table, column, ref_table, ref_column),
    )
    return cursor.fetchone()[0] > 0


def main():
    print('migracion_03_boleta: Iniciando')
    conn = get_conn()
    cursor = conn.cursor()
    try:
        # Eliminar columnas antiguas si existen
        for col in ('cochera_asignada', 'costo_parking'):
            if column_exists(cursor, 'boleta', col):
                print(f'Columna boleta.{col} encontrada: eliminando...')
                cursor.execute(f'ALTER TABLE boleta DROP COLUMN {col}')
            else:
                print(f'Columna boleta.{col} no existe')

        # Eliminar tabla boleta_backup si existe
        print('Eliminando tabla boleta_backup si existe...')
        cursor.execute('DROP TABLE IF EXISTS boleta_backup')

        # Agregar columna ID_Asignacion si no existe
        if not column_exists(cursor, 'boleta', 'ID_Asignacion'):
            print('Agregando columna boleta.ID_Asignacion...')
            cursor.execute('ALTER TABLE boleta ADD COLUMN ID_Asignacion INT NULL')
        else:
            print('Columna boleta.ID_Asignacion ya existe')

        # Agregar FK
        if not fk_exists(cursor, 'boleta', 'ID_Asignacion', 'asignacion_parking', 'ID_Asignacion'):
            try:
                cursor.execute('ALTER TABLE boleta ADD CONSTRAINT fk_boleta_asignacion FOREIGN KEY (ID_Asignacion) REFERENCES asignacion_parking(ID_Asignacion)')
                print('FK boleta.ID_Asignacion -> asignacion_parking.ID_Asignacion creada')
            except Exception as e:
                print('No se pudo crear FK boleta.ID_Asignacion:', e)
        else:
            print('FK boleta.ID_Asignacion ya existe')

        conn.commit()
        print('migracion_03_boleta: Completada')
    except Exception as e:
        conn.rollback()
        print('migracion_03_boleta: ERROR:', e)
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()
"""
Script de migración: Guardar respaldo de datos de boleta antes de eliminar columnas
- Crea tabla boleta_backup para almacenar datos históricos
- Guarda cochera_asignada y costo_parking en el respaldo
- Elimina columnas de la tabla original
"""

import mysql.connector
from mysql.connector import Error
import sys
from datetime import datetime


class MigracionBoleta:
    """Maneja la migración de datos de boleta."""
    
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
    
    def columna_existe(self, tabla, columna):
        """Verifica si una columna existe en una tabla."""
        try:
            sql = f"DESCRIBE {tabla}"
            self.cursor.execute(sql)
            columnas = self.cursor.fetchall()
            nombres_columnas = [col['Field'] for col in columnas]
            return columna in nombres_columnas
        except Error as e:
            print(f"✗ Error al verificar columna {columna} en {tabla}: {e}")
            return False
    
    def crear_tabla_respaldo(self):
        """Crea la tabla boleta_backup para almacenar el respaldo."""
        try:
            # Verificar si ya existe
            if self.tabla_existe('boleta_backup'):
                print("⚠ Tabla 'boleta_backup' ya existe")
                # Preguntar si continuar o no
                print("  Se añadirán nuevos registros a la tabla existente")
            else:
                sql = """
                CREATE TABLE IF NOT EXISTS boleta_backup (
                    ID_Backup INT AUTO_INCREMENT PRIMARY KEY,
                    ID_Boleta INT NOT NULL UNIQUE,
                    cochera_asignada VARCHAR(50),
                    costo_parking DECIMAL(10, 2),
                    fecha_backup TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_id_boleta (ID_Boleta)
                )
                """
                self.cursor.execute(sql)
                self.conexion.commit()
                print("✓ Tabla 'boleta_backup' creada exitosamente")
            
            return True
        except Error as e:
            print(f"✗ Error al crear tabla boleta_backup: {e}")
            self.conexion.rollback()
            return False
    
    def verificar_datos_boleta(self):
        """Verifica que la tabla boleta existe y obtiene información sobre los datos."""
        try:
            # Verificar que la tabla existe
            if not self.tabla_existe('boleta'):
                print("✗ La tabla 'boleta' no existe")
                return False
            
            print("✓ Tabla 'boleta' encontrada")
            
            # Contar registros
            sql_count = "SELECT COUNT(*) as total FROM boleta"
            self.cursor.execute(sql_count)
            total_registros = self.cursor.fetchone()['total']
            print(f"✓ Total de registros en boleta: {total_registros}")
            
            # Verificar estructura de la tabla
            sql_estructura = "DESCRIBE boleta"
            self.cursor.execute(sql_estructura)
            columnas = self.cursor.fetchall()
            print("✓ Estructura de boleta:")
            for col in columnas:
                print(f"  - {col['Field']} ({col['Type']})")
            
            # Verificar que las columnas a respaldar existen
            columnas_necesarias = ['cochera_asignada', 'costo_parking']
            columnas_encontradas = [col['Field'] for col in columnas]
            
            for col_necesaria in columnas_necesarias:
                if col_necesaria not in columnas_encontradas:
                    print(f"✗ La columna '{col_necesaria}' no existe en boleta")
                    return False
            
            print("✓ Columnas a respaldar encontradas")
            
            # Contar registros con datos en las columnas
            sql_cochera = "SELECT COUNT(*) as con_valor FROM boleta WHERE cochera_asignada IS NOT NULL"
            self.cursor.execute(sql_cochera)
            con_cochera = self.cursor.fetchone()['con_valor']
            
            sql_costo = "SELECT COUNT(*) as con_valor FROM boleta WHERE costo_parking IS NOT NULL"
            self.cursor.execute(sql_costo)
            con_costo = self.cursor.fetchone()['con_valor']
            
            print(f"\n[Información de datos]")
            print(f"  Registros con cochera_asignada: {con_cochera}")
            print(f"  Registros con costo_parking: {con_costo}")
            
            return True
        
        except Error as e:
            print(f"✗ Error al verificar datos de boleta: {e}")
            return False
    
    def guardar_respaldo_datos(self):
        """Guarda los datos de cochera_asignada y costo_parking en boleta_backup."""
        try:
            print("\n[Guardando respaldo de datos...]")
            
            # Obtener todos los registros de boleta
            sql_select = "SELECT ID_Boleta, cochera_asignada, costo_parking FROM boleta"
            self.cursor.execute(sql_select)
            registros = self.cursor.fetchall()
            
            if not registros:
                print("⚠ No hay registros para respaldar")
                return True
            
            print(f"✓ Se respaldarán {len(registros)} registros")
            
            # Insertar en boleta_backup
            sql_insert = """
            INSERT INTO boleta_backup (ID_Boleta, cochera_asignada, costo_parking)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                cochera_asignada = VALUES(cochera_asignada),
                costo_parking = VALUES(costo_parking),
                fecha_backup = CURRENT_TIMESTAMP
            """
            
            for registro in registros:
                try:
                    self.cursor.execute(sql_insert, (
                        registro['ID_Boleta'],
                        registro['cochera_asignada'],
                        registro['costo_parking']
                    ))
                except Error as e:
                    print(f"✗ Error al insertar registro {registro['ID_Boleta']}: {e}")
                    raise
            
            self.conexion.commit()
            print(f"✓ {len(registros)} registros guardados en boleta_backup")
            
            # Verificar que se guardaron correctamente
            sql_verify = "SELECT COUNT(*) as total FROM boleta_backup"
            self.cursor.execute(sql_verify)
            total_backup = self.cursor.fetchone()['total']
            print(f"✓ Verificación: {total_backup} registros en respaldo")
            
            return True
        
        except Error as e:
            print(f"✗ Error al guardar respaldo: {e}")
            self.conexion.rollback()
            return False
    
    def eliminar_columna_cochera_asignada(self):
        """Elimina la columna cochera_asignada de la tabla boleta."""
        try:
            if not self.columna_existe('boleta', 'cochera_asignada'):
                print("⚠ La columna 'cochera_asignada' no existe")
                return True
            
            print("\n[Eliminando columna cochera_asignada...]")
            sql = "ALTER TABLE boleta DROP COLUMN cochera_asignada"
            self.cursor.execute(sql)
            self.conexion.commit()
            print("✓ Columna 'cochera_asignada' eliminada")
            return True
        
        except Error as e:
            print(f"✗ Error al eliminar cochera_asignada: {e}")
            self.conexion.rollback()
            return False
    
    def eliminar_columna_costo_parking(self):
        """Elimina la columna costo_parking de la tabla boleta."""
        try:
            if not self.columna_existe('boleta', 'costo_parking'):
                print("⚠ La columna 'costo_parking' no existe")
                return True
            
            print("\n[Eliminando columna costo_parking...]")
            sql = "ALTER TABLE boleta DROP COLUMN costo_parking"
            self.cursor.execute(sql)
            self.conexion.commit()
            print("✓ Columna 'costo_parking' eliminada")
            return True
        
        except Error as e:
            print(f"✗ Error al eliminar costo_parking: {e}")
            self.conexion.rollback()
            return False
    
    def verificar_migracion(self):
        """Verifica que la migración se completó correctamente."""
        try:
            print("\n" + "="*60)
            print("RESULTADO DE LA MIGRACIÓN")
            print("="*60)
            
            # Verificar estructura de boleta
            sql = "DESCRIBE boleta"
            self.cursor.execute(sql)
            columnas = self.cursor.fetchall()
            nombres_columnas = [col['Field'] for col in columnas]
            
            print("\nColumnas en tabla 'boleta':")
            for col in columnas:
                print(f"  - {col['Field']} ({col['Type']})")
            
            # Confirmar que las columnas fueron eliminadas
            eliminadas_correctamente = True
            
            if 'cochera_asignada' in nombres_columnas:
                print("\n✗ Error: 'cochera_asignada' aún existe en boleta")
                eliminadas_correctamente = False
            else:
                print("\n✓ Confirmado: 'cochera_asignada' ha sido eliminada")
            
            if 'costo_parking' in nombres_columnas:
                print("✗ Error: 'costo_parking' aún existe en boleta")
                eliminadas_correctamente = False
            else:
                print("✓ Confirmado: 'costo_parking' ha sido eliminada")
            
            # Verificar respaldo
            sql_backup = "SELECT COUNT(*) as total FROM boleta_backup"
            self.cursor.execute(sql_backup)
            total_backup = self.cursor.fetchone()['total']
            print(f"\n✓ Total de registros en boleta_backup: {total_backup}")
            
            # Mostrar algunas filas del respaldo como ejemplo
            sql_sample = "SELECT * FROM boleta_backup LIMIT 3"
            self.cursor.execute(sql_sample)
            samples = self.cursor.fetchall()
            
            if samples:
                print("\nMuestra del respaldo (primeros 3 registros):")
                for sample in samples:
                    print(f"  ID_Boleta: {sample['ID_Boleta']}")
                    print(f"    - Cochera: {sample['cochera_asignada']}")
                    print(f"    - Costo: {sample['costo_parking']}")
                    print(f"    - Fecha backup: {sample['fecha_backup']}")
            
            return eliminadas_correctamente
        
        except Error as e:
            print(f"✗ Error al verificar migración: {e}")
            return False
    
    def ejecutar_migracion(self):
        """Ejecuta el proceso completo de migración."""
        print("="*60)
        print("INICIANDO MIGRACIÓN DE BOLETA")
        print("="*60 + "\n")
        
        # Paso 1: Conectar
        if not self.conectar():
            return False
        
        try:
            # Paso 2: Verificar datos
            print("[1/5] Verificando datos de boleta...")
            if not self.verificar_datos_boleta():
                print("✗ Verificación fallida")
                return False
            
            # Paso 3: Crear tabla de respaldo
            print("\n[2/5] Creando tabla de respaldo...")
            if not self.crear_tabla_respaldo():
                print("✗ Error al crear respaldo")
                return False
            
            # Paso 4: Guardar respaldo
            print("\n[3/5] Guardando datos en respaldo...")
            if not self.guardar_respaldo_datos():
                print("✗ Error al guardar respaldo")
                return False
            
            # Paso 5: Eliminar columnas
            print("\n[4/5] Eliminando columnas...")
            if not self.eliminar_columna_cochera_asignada():
                print("✗ Error al eliminar cochera_asignada")
                return False
            
            if not self.eliminar_columna_costo_parking():
                print("✗ Error al eliminar costo_parking")
                return False
            
            # Paso 6: Verificar
            print("\n[5/5] Verificando resultado...")
            if not self.verificar_migracion():
                return False
            
            print("\n" + "="*60)
            print("✓ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("="*60)
            print("\nNota: Los datos se encuentran guardados en boleta_backup")
            print("      para consultas históricas o auditoría.")
            
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
    migracion = MigracionBoleta(
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
