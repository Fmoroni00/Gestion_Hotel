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
    print('migracion_02_parking: Iniciando')
    conn = get_conn()
    cursor = conn.cursor()
    try:
        # Verificar y eliminar parking.reserva_id si existe
        if column_exists(cursor, 'parking', 'reserva_id'):
            print('Columna parking.reserva_id encontrada: eliminando...')
            cursor.execute('ALTER TABLE parking DROP COLUMN reserva_id')
        else:
            print('Columna parking.reserva_id no existe')

        # Verificar FKs en asignacion_parking
        print('Verificando FKs en asignacion_parking...')
        # FK ID_Reserva -> reserva(ID_Reserva)
        if not fk_exists(cursor, 'asignacion_parking', 'ID_Reserva', 'reserva', 'ID_Reserva'):
            try:
                cursor.execute('ALTER TABLE asignacion_parking ADD CONSTRAINT fk_ap_reserva FOREIGN KEY (ID_Reserva) REFERENCES reserva(ID_Reserva)')
                print('FK asignacion_parking.ID_Reserva -> reserva.ID_Reserva creada')
            except Exception as e:
                print('No se pudo crear FK asignacion_parking.ID_Reserva:', e)
        else:
            print('FK asignacion_parking.ID_Reserva ya existe')

        # FK ID_Parking -> parking(ID_Parking)
        if not fk_exists(cursor, 'asignacion_parking', 'ID_Parking', 'parking', 'ID_Parking'):
            try:
                cursor.execute('ALTER TABLE asignacion_parking ADD CONSTRAINT fk_ap_parking FOREIGN KEY (ID_Parking) REFERENCES parking(ID_Parking)')
                print('FK asignacion_parking.ID_Parking -> parking.ID_Parking creada')
            except Exception as e:
                print('No se pudo crear FK asignacion_parking.ID_Parking:', e)
        else:
            print('FK asignacion_parking.ID_Parking ya existe')

        conn.commit()
        print('migracion_02_parking: Completada')
    except Exception as e:
        conn.rollback()
        print('migracion_02_parking: ERROR:', e)
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()
"""
Script de migración: Verificar tabla asignacion_parking y limpiar parking
- Verifica integridad de datos en asignacion_parking
- Elimina la columna reserva_id de la tabla parking
"""

import mysql.connector
from mysql.connector import Error
import sys


class MigracionParking:
    """Maneja la migración de datos de parking."""
    
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
    
    def verificar_asignacion_parking(self):
        """Verifica que la tabla asignacion_parking existe y tiene datos consistentes."""
        try:
            # Verificar que la tabla existe
            if not self.tabla_existe('asignacion_parking'):
                print("✗ La tabla 'asignacion_parking' no existe")
                return False
            
            print("✓ Tabla 'asignacion_parking' encontrada")
            
            # Contar registros
            sql_count = "SELECT COUNT(*) as total FROM asignacion_parking"
            self.cursor.execute(sql_count)
            total_registros = self.cursor.fetchone()['total']
            print(f"✓ Total de registros en asignacion_parking: {total_registros}")
            
            # Verificar estructura de la tabla
            sql_estructura = f"DESCRIBE asignacion_parking"
            self.cursor.execute(sql_estructura)
            columnas = self.cursor.fetchall()
            print("✓ Columnas en asignacion_parking:")
            for col in columnas:
                print(f"  - {col['Field']} ({col['Type']})")
            
            # Verificar integridad referencial
            print("\n[Verificando integridad referencial...]")
            
            # Verificar que todos los ID_Reserva existen en reserva
            sql_integrity_res = """
            SELECT COUNT(*) as invalidos 
            FROM asignacion_parking ap 
            WHERE NOT EXISTS (
                SELECT 1 FROM reserva r 
                WHERE r.ID_Reserva = ap.ID_Reserva
            )
            """
            self.cursor.execute(sql_integrity_res)
            invalidos_res = self.cursor.fetchone()['invalidos']
            
            if invalidos_res > 0:
                print(f"⚠ Advertencia: {invalidos_res} registros con ID_Reserva inválido")
            else:
                print("✓ Todos los ID_Reserva son válidos")
            
            # Verificar que todos los ID_Parking existen en parking
            sql_integrity_park = """
            SELECT COUNT(*) as invalidos 
            FROM asignacion_parking ap 
            WHERE NOT EXISTS (
                SELECT 1 FROM parking p 
                WHERE p.ID_Parking = ap.ID_Parking
            )
            """
            self.cursor.execute(sql_integrity_park)
            invalidos_park = self.cursor.fetchone()['invalidos']
            
            if invalidos_park > 0:
                print(f"⚠ Advertencia: {invalidos_park} registros con ID_Parking inválido")
            else:
                print("✓ Todos los ID_Parking son válidos")
            
            # Verificar datos duplicados
            sql_duplicados = """
            SELECT ID_Reserva, ID_Parking, COUNT(*) as cantidad
            FROM asignacion_parking
            GROUP BY ID_Reserva, ID_Parking
            HAVING COUNT(*) > 1
            """
            self.cursor.execute(sql_duplicados)
            duplicados = self.cursor.fetchall()
            
            if duplicados:
                print(f"⚠ Advertencia: {len(duplicados)} asignaciones duplicadas encontradas")
                for dup in duplicados:
                    print(f"  - Reserva {dup['ID_Reserva']} - Parking {dup['ID_Parking']}: {dup['cantidad']} veces")
            else:
                print("✓ No hay asignaciones duplicadas")
            
            # Si hay problemas, reportarlos pero continuar
            if invalidos_res > 0 or invalidos_park > 0:
                print("\n⚠ La integridad referencial tiene problemas, pero continuaremos con la migración")
                return True
            
            print("\n✓ Verificación de asignacion_parking completada exitosamente")
            return True
        
        except Error as e:
            print(f"✗ Error al verificar asignacion_parking: {e}")
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
    
    def eliminar_columna_reserva_id(self):
        """Elimina la columna reserva_id de la tabla parking."""
        try:
            # Verificar que la tabla existe
            if not self.tabla_existe('parking'):
                print("✗ La tabla 'parking' no existe")
                return False
            
            print("✓ Tabla 'parking' encontrada")
            
            # Verificar que la columna existe antes de intentar eliminarla
            if not self.columna_existe('parking', 'reserva_id'):
                print("⚠ La columna 'reserva_id' no existe en la tabla 'parking'")
                print("  (Puede haber sido eliminada anteriormente)")
                return True
            
            print("✓ Columna 'reserva_id' encontrada en 'parking'")
            
            # Obtener información sobre la columna
            sql_info = "DESCRIBE parking"
            self.cursor.execute(sql_info)
            columnas = self.cursor.fetchall()
            for col in columnas:
                if col['Field'] == 'reserva_id':
                    print(f"  Tipo: {col['Type']}")
                    print(f"  Nullable: {col['Null']}")
                    print(f"  Key: {col['Key']}")
            
            # Contar registros con valores en reserva_id
            sql_count_values = "SELECT COUNT(*) as con_valor FROM parking WHERE reserva_id IS NOT NULL"
            self.cursor.execute(sql_count_values)
            con_valor = self.cursor.fetchone()['con_valor']
            print(f"  Registros con valor en reserva_id: {con_valor}")
            
            # Advertencia si hay datos que se perderán
            if con_valor > 0:
                print(f"\n⚠ ADVERTENCIA: Se perderán {con_valor} valores de reserva_id")
                print("  Asegúrate de que estos datos hayan sido migrados a asignacion_parking")
            
            # Eliminar la columna
            print("\n[Eliminando columna reserva_id...]")
            sql = "ALTER TABLE parking DROP COLUMN reserva_id"
            self.cursor.execute(sql)
            self.conexion.commit()
            print("✓ Columna 'reserva_id' eliminada exitosamente de 'parking'")
            return True
        
        except Error as e:
            print(f"✗ Error al eliminar columna reserva_id: {e}")
            self.conexion.rollback()
            return False
    
    def verificar_migracion(self):
        """Verifica que la migración se completó correctamente."""
        try:
            # Verificar estructura de parking
            sql = "DESCRIBE parking"
            self.cursor.execute(sql)
            columnas = self.cursor.fetchall()
            nombres_columnas = [col['Field'] for col in columnas]
            
            print("\n" + "="*50)
            print("RESULTADO DE LA MIGRACIÓN")
            print("="*50)
            print(f"Columnas en tabla 'parking': {len(columnas)}")
            print("Lista de columnas:")
            for col in columnas:
                print(f"  - {col['Field']} ({col['Type']})")
            
            # Confirmar que reserva_id fue eliminada
            if 'reserva_id' not in nombres_columnas:
                print("\n✓ Confirmado: 'reserva_id' ha sido eliminada")
            else:
                print("\n✗ Error: 'reserva_id' aún existe en la tabla")
                return False
            
            return True
        except Error as e:
            print(f"✗ Error al verificar migración: {e}")
            return False
    
    def ejecutar_migracion(self):
        """Ejecuta el proceso completo de migración."""
        print("="*50)
        print("INICIANDO MIGRACIÓN DE PARKING")
        print("="*50 + "\n")
        
        # Paso 1: Conectar
        if not self.conectar():
            return False
        
        try:
            # Paso 2: Verificar asignacion_parking
            print("[1/3] Verificando tabla asignacion_parking...")
            if not self.verificar_asignacion_parking():
                print("✗ Verificación fallida, abortando migración")
                return False
            
            # Paso 3: Eliminar columna
            print("\n[2/3] Eliminando columna reserva_id...")
            if not self.eliminar_columna_reserva_id():
                print("✗ Error al eliminar columna, abortando migración")
                return False
            
            # Paso 4: Verificar
            print("\n[3/3] Verificando resultado...")
            if not self.verificar_migracion():
                return False
            
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
    migracion = MigracionParking(
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
