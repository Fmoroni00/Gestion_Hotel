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
    print('migracion_04_historial: Iniciando')
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cols = ['ID_Administrador', 'ID_Recepcionista', 'ID_PL']
        found = [c for c in cols if column_exists(cursor, 'historial', c)]
        if found:
            print('Columnas antiguas encontradas en historial:', found)
            if not column_exists(cursor, 'historial', 'ID_Usuario'):
                print('Agregando columna historial.ID_Usuario...')
                cursor.execute('ALTER TABLE historial ADD COLUMN ID_Usuario INT NULL')
            else:
                print('Columna historial.ID_Usuario ya existe')

            # Migrar datos
            print('Migrando datos a ID_Usuario...')
            cursor.execute(
                "UPDATE historial SET ID_Usuario = COALESCE(ID_Administrador, ID_Recepcionista, ID_PL) WHERE ID_Usuario IS NULL"
            )

            # Agregar FK si no existe
            if not fk_exists(cursor, 'historial', 'ID_Usuario', 'usuario', 'ID_Usuario'):
                try:
                    cursor.execute('ALTER TABLE historial ADD CONSTRAINT fk_historial_usuario FOREIGN KEY (ID_Usuario) REFERENCES usuario(ID_Usuario)')
                    print('FK historial.ID_Usuario -> usuario.ID_Usuario creada')
                except Exception as e:
                    print('No se pudo crear FK historial.ID_Usuario:', e)
            else:
                print('FK historial.ID_Usuario ya existe')

            # Eliminar columnas antiguas
            for c in found:
                try:
                    print(f'Eliminando columna historial.{c}...')
                    cursor.execute(f'ALTER TABLE historial DROP COLUMN {c}')
                except Exception as e:
                    print('No se pudo eliminar columna', c, e)
        else:
            print('No se encontraron columnas antiguas en historial')
            # Verificar ID_Usuario y su FK
            if column_exists(cursor, 'historial', 'ID_Usuario'):
                if not fk_exists(cursor, 'historial', 'ID_Usuario', 'usuario', 'ID_Usuario'):
                    try:
                        cursor.execute('ALTER TABLE historial ADD CONSTRAINT fk_historial_usuario FOREIGN KEY (ID_Usuario) REFERENCES usuario(ID_Usuario)')
                        print('FK historial.ID_Usuario -> usuario.ID_Usuario creada')
                    except Exception as e:
                        print('No se pudo crear FK historial.ID_Usuario:', e)
                else:
                    print('ID_Usuario y su FK ya están correctos')
            else:
                print('ID_Usuario no existe en historial; nada que verificar')

        conn.commit()
        print('migracion_04_historial: Completada')
    except Exception as e:
        conn.rollback()
        print('migracion_04_historial: ERROR:', e)
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()
"""
Script de migración: Consolidar IDs de usuarios en historial
- Agrega columna ID_Usuario a historial
- Migra datos de ID_Administrador, ID_Recepcionista, ID_PL hacia ID_Usuario
- Crea FK hacia tabla usuario
- Elimina columnas antiguas de usuario
"""

import mysql.connector
from mysql.connector import Error
import sys


class MigracionHistorial:
    """Maneja la migración de datos de historial."""
    
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
    
    def verificar_datos_historial(self):
        """Verifica que la tabla historial existe y obtiene información sobre los datos."""
        try:
            # Verificar que la tabla existe
            if not self.tabla_existe('historial'):
                print("✗ La tabla 'historial' no existe")
                return False
            
            print("✓ Tabla 'historial' encontrada")
            
            # Contar registros
            sql_count = "SELECT COUNT(*) as total FROM historial"
            self.cursor.execute(sql_count)
            total_registros = self.cursor.fetchone()['total']
            print(f"✓ Total de registros en historial: {total_registros}")
            
            # Verificar estructura de la tabla
            sql_estructura = "DESCRIBE historial"
            self.cursor.execute(sql_estructura)
            columnas = self.cursor.fetchall()
            print("✓ Estructura actual de historial:")
            for col in columnas:
                print(f"  - {col['Field']} ({col['Type']})")
            
            # Verificar que las columnas a migrar existen
            columnas_necesarias = ['ID_Administrador', 'ID_Recepcionista', 'ID_PL']
            columnas_encontradas = [col['Field'] for col in columnas]
            
            print("\n[Verificando columnas a migrar]")
            for col_necesaria in columnas_necesarias:
                if col_necesaria not in columnas_encontradas:
                    print(f"⚠ La columna '{col_necesaria}' no existe en historial")
                else:
                    print(f"✓ Columna '{col_necesaria}' encontrada")
            
            # Contar registros con datos en cada columna
            print("\n[Información de datos a migrar]")
            for columna in columnas_necesarias:
                sql_count_col = f"SELECT COUNT(*) as con_valor FROM historial WHERE {columna} IS NOT NULL"
                self.cursor.execute(sql_count_col)
                con_valor = self.cursor.fetchone()['con_valor']
                print(f"  Registros con {columna}: {con_valor}")
            
            return True
        
        except Error as e:
            print(f"✗ Error al verificar datos de historial: {e}")
            return False
    
    def agregar_columna_id_usuario(self):
        """Agrega la columna ID_Usuario a la tabla historial."""
        try:
            # Verificar si ya existe
            if self.columna_existe('historial', 'ID_Usuario'):
                print("⚠ La columna 'ID_Usuario' ya existe en historial")
                return True
            
            print("\n[Agregando columna ID_Usuario...]")
            sql = "ALTER TABLE historial ADD COLUMN ID_Usuario INT NULL"
            self.cursor.execute(sql)
            self.conexion.commit()
            print("✓ Columna 'ID_Usuario' agregada a historial")
            return True
        
        except Error as e:
            print(f"✗ Error al agregar columna ID_Usuario: {e}")
            self.conexion.rollback()
            return False
    
    def actualizar_desde_administrador(self):
        """Actualiza ID_Usuario desde ID_Administrador."""
        try:
            print("\n[Actualizando ID_Usuario desde ID_Administrador...]")
            
            # Contar registros que se actualizarán
            sql_count = "SELECT COUNT(*) as cantidad FROM historial WHERE ID_Administrador IS NOT NULL AND ID_Usuario IS NULL"
            self.cursor.execute(sql_count)
            cantidad = self.cursor.fetchone()['cantidad']
            
            if cantidad == 0:
                print("  No hay registros a actualizar desde ID_Administrador")
                return True
            
            print(f"  Se actualizarán {cantidad} registros")
            
            sql_update = "UPDATE historial SET ID_Usuario = ID_Administrador WHERE ID_Administrador IS NOT NULL AND ID_Usuario IS NULL"
            self.cursor.execute(sql_update)
            self.conexion.commit()
            print(f"✓ {self.cursor.rowcount} registros actualizados desde ID_Administrador")
            return True
        
        except Error as e:
            print(f"✗ Error al actualizar desde ID_Administrador: {e}")
            self.conexion.rollback()
            return False
    
    def actualizar_desde_recepcionista(self):
        """Actualiza ID_Usuario desde ID_Recepcionista."""
        try:
            print("\n[Actualizando ID_Usuario desde ID_Recepcionista...]")
            
            # Contar registros que se actualizarán
            sql_count = "SELECT COUNT(*) as cantidad FROM historial WHERE ID_Recepcionista IS NOT NULL AND ID_Usuario IS NULL"
            self.cursor.execute(sql_count)
            cantidad = self.cursor.fetchone()['cantidad']
            
            if cantidad == 0:
                print("  No hay registros a actualizar desde ID_Recepcionista")
                return True
            
            print(f"  Se actualizarán {cantidad} registros")
            
            sql_update = "UPDATE historial SET ID_Usuario = ID_Recepcionista WHERE ID_Recepcionista IS NOT NULL AND ID_Usuario IS NULL"
            self.cursor.execute(sql_update)
            self.conexion.commit()
            print(f"✓ {self.cursor.rowcount} registros actualizados desde ID_Recepcionista")
            return True
        
        except Error as e:
            print(f"✗ Error al actualizar desde ID_Recepcionista: {e}")
            self.conexion.rollback()
            return False
    
    def actualizar_desde_pl(self):
        """Actualiza ID_Usuario desde ID_PL."""
        try:
            print("\n[Actualizando ID_Usuario desde ID_PL...]")
            
            # Contar registros que se actualizarán
            sql_count = "SELECT COUNT(*) as cantidad FROM historial WHERE ID_PL IS NOT NULL AND ID_Usuario IS NULL"
            self.cursor.execute(sql_count)
            cantidad = self.cursor.fetchone()['cantidad']
            
            if cantidad == 0:
                print("  No hay registros a actualizar desde ID_PL")
                return True
            
            print(f"  Se actualizarán {cantidad} registros")
            
            sql_update = "UPDATE historial SET ID_Usuario = ID_PL WHERE ID_PL IS NOT NULL AND ID_Usuario IS NULL"
            self.cursor.execute(sql_update)
            self.conexion.commit()
            print(f"✓ {self.cursor.rowcount} registros actualizados desde ID_PL")
            return True
        
        except Error as e:
            print(f"✗ Error al actualizar desde ID_PL: {e}")
            self.conexion.rollback()
            return False
    
    def eliminar_foreign_keys_antiguas(self):
        """Elimina las Foreign Keys antiguas de las columnas a eliminar."""
        try:
            print("\n[Eliminando Foreign Keys antiguas...]")
            
            # Obtener todas las FKs de la tabla historial
            sql_fks = """
            SELECT CONSTRAINT_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
            WHERE TABLE_NAME='historial' 
            AND REFERENCED_TABLE_NAME IS NOT NULL
            """
            self.cursor.execute(sql_fks)
            fks = self.cursor.fetchall()
            
            columnas_a_eliminar = ['ID_Administrador', 'ID_Recepcionista', 'ID_PL']
            eliminadas = 0
            
            for fk in fks:
                if fk['COLUMN_NAME'] in columnas_a_eliminar:
                    constraint_name = fk['CONSTRAINT_NAME']
                    column_name = fk['COLUMN_NAME']
                    
                    print(f"  Eliminando FK: {constraint_name} ({column_name})")
                    sql_drop_fk = f"ALTER TABLE historial DROP FOREIGN KEY {constraint_name}"
                    self.cursor.execute(sql_drop_fk)
                    eliminadas += 1
            
            self.conexion.commit()
            
            if eliminadas > 0:
                print(f"✓ {eliminadas} Foreign Keys eliminadas")
            else:
                print("  No hay Foreign Keys antiguas para eliminar")
            
            return True
        
        except Error as e:
            print(f"✗ Error al eliminar Foreign Keys antiguas: {e}")
            self.conexion.rollback()
            return False
    
    def agregar_foreign_key(self):
        """Agrega la Foreign Key ID_Usuario → usuario(ID_Usuario)."""
        try:
            print("\n[Agregando Foreign Key...]")
            
            # Verificar si la FK ya existe
            sql_check_fk = """
            SELECT CONSTRAINT_NAME 
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
            WHERE TABLE_NAME='historial' 
            AND COLUMN_NAME='ID_Usuario' 
            AND REFERENCED_TABLE_NAME='usuario'
            """
            self.cursor.execute(sql_check_fk)
            resultado = self.cursor.fetchone()
            
            if resultado:
                print("⚠ La Foreign Key ya existe")
                return True
            
            # Crear la FK
            sql_fk = """
            ALTER TABLE historial
            ADD CONSTRAINT fk_historial_usuario
            FOREIGN KEY (ID_Usuario) REFERENCES usuario(ID_Usuario) ON DELETE SET NULL
            """
            self.cursor.execute(sql_fk)
            self.conexion.commit()
            print("✓ Foreign Key agregada correctamente")
            return True
        
        except Error as e:
            print(f"✗ Error al agregar Foreign Key: {e}")
            self.conexion.rollback()
            return False
    
    def eliminar_columna_administrador(self):
        """Elimina la columna ID_Administrador."""
        try:
            if not self.columna_existe('historial', 'ID_Administrador'):
                print("⚠ La columna 'ID_Administrador' no existe")
                return True
            
            print("\n[Eliminando columna ID_Administrador...]")
            sql = "ALTER TABLE historial DROP COLUMN ID_Administrador"
            self.cursor.execute(sql)
            self.conexion.commit()
            print("✓ Columna 'ID_Administrador' eliminada")
            return True
        
        except Error as e:
            print(f"✗ Error al eliminar ID_Administrador: {e}")
            self.conexion.rollback()
            return False
    
    def eliminar_columna_recepcionista(self):
        """Elimina la columna ID_Recepcionista."""
        try:
            if not self.columna_existe('historial', 'ID_Recepcionista'):
                print("⚠ La columna 'ID_Recepcionista' no existe")
                return True
            
            print("\n[Eliminando columna ID_Recepcionista...]")
            sql = "ALTER TABLE historial DROP COLUMN ID_Recepcionista"
            self.cursor.execute(sql)
            self.conexion.commit()
            print("✓ Columna 'ID_Recepcionista' eliminada")
            return True
        
        except Error as e:
            print(f"✗ Error al eliminar ID_Recepcionista: {e}")
            self.conexion.rollback()
            return False
    
    def eliminar_columna_pl(self):
        """Elimina la columna ID_PL."""
        try:
            if not self.columna_existe('historial', 'ID_PL'):
                print("⚠ La columna 'ID_PL' no existe")
                return True
            
            print("\n[Eliminando columna ID_PL...]")
            sql = "ALTER TABLE historial DROP COLUMN ID_PL"
            self.cursor.execute(sql)
            self.conexion.commit()
            print("✓ Columna 'ID_PL' eliminada")
            return True
        
        except Error as e:
            print(f"✗ Error al eliminar ID_PL: {e}")
            self.conexion.rollback()
            return False
    
    def verificar_migracion(self):
        """Verifica que la migración se completó correctamente."""
        try:
            print("\n" + "="*60)
            print("RESULTADO DE LA MIGRACIÓN")
            print("="*60)
            
            # Verificar estructura de historial
            sql = "DESCRIBE historial"
            self.cursor.execute(sql)
            columnas = self.cursor.fetchall()
            nombres_columnas = [col['Field'] for col in columnas]
            
            print("\nEstructura final de historial:")
            for col in columnas:
                print(f"  - {col['Field']} ({col['Type']})")
            
            # Confirmaciones de eliminación
            eliminadas_correctamente = True
            
            print("\n[Verificación de columnas eliminadas]")
            columnas_eliminadas = ['ID_Administrador', 'ID_Recepcionista', 'ID_PL']
            for col in columnas_eliminadas:
                if col in nombres_columnas:
                    print(f"✗ Error: '{col}' aún existe")
                    eliminadas_correctamente = False
                else:
                    print(f"✓ Confirmado: '{col}' ha sido eliminada")
            
            # Verificar ID_Usuario
            if 'ID_Usuario' in nombres_columnas:
                print(f"\n✓ Confirmado: 'ID_Usuario' agregada")
                
                # Contar registros con ID_Usuario
                sql_count = "SELECT COUNT(*) as total FROM historial WHERE ID_Usuario IS NOT NULL"
                self.cursor.execute(sql_count)
                total_usuarios = self.cursor.fetchone()['total']
                
                sql_count_todos = "SELECT COUNT(*) as total FROM historial"
                self.cursor.execute(sql_count_todos)
                total_registros = self.cursor.fetchone()['total']
                
                print(f"  Registros con ID_Usuario: {total_usuarios}/{total_registros}")
            else:
                print(f"\n✗ Error: 'ID_Usuario' no existe")
                eliminadas_correctamente = False
            
            # Verificar Foreign Key
            sql_check_fk = """
            SELECT CONSTRAINT_NAME 
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
            WHERE TABLE_NAME='historial' 
            AND COLUMN_NAME='ID_Usuario' 
            AND REFERENCED_TABLE_NAME='usuario'
            """
            self.cursor.execute(sql_check_fk)
            resultado = self.cursor.fetchone()
            
            if resultado:
                print(f"\n✓ Foreign Key verificada: {resultado['CONSTRAINT_NAME']}")
            else:
                print("\n⚠ Foreign Key no encontrada")
            
            return eliminadas_correctamente
        
        except Error as e:
            print(f"✗ Error al verificar migración: {e}")
            return False
    
    def ejecutar_migracion(self):
        """Ejecuta el proceso completo de migración."""
        print("="*60)
        print("INICIANDO MIGRACIÓN DE HISTORIAL")
        print("="*60 + "\n")
        
        # Paso 1: Conectar
        if not self.conectar():
            return False
        
        try:
            # Paso 2: Verificar datos
            print("[1/8] Verificando datos de historial...")
            if not self.verificar_datos_historial():
                print("✗ Verificación fallida")
                return False
            
            # Paso 3: Agregar columna
            print("\n[2/8] Agregando columna ID_Usuario...")
            if not self.agregar_columna_id_usuario():
                print("✗ Error al agregar columna")
                return False
            
            # Paso 4-6: Actualizar datos
            print("\n[3/8] Migrando datos desde ID_Administrador...")
            if not self.actualizar_desde_administrador():
                print("✗ Error al actualizar desde ID_Administrador")
                return False
            
            print("\n[4/8] Migrando datos desde ID_Recepcionista...")
            if not self.actualizar_desde_recepcionista():
                print("✗ Error al actualizar desde ID_Recepcionista")
                return False
            
            print("\n[5/8] Migrando datos desde ID_PL...")
            if not self.actualizar_desde_pl():
                print("✗ Error al actualizar desde ID_PL")
                return False
            
            # Paso 7: Agregar FK
            print("\n[6/8] Agregando Foreign Key...")
            if not self.agregar_foreign_key():
                print("✗ Error al agregar Foreign Key")
                return False
            
            # Paso 8: Eliminar FKs antiguas
            print("\n[7/9] Eliminando Foreign Keys antiguas...")
            if not self.eliminar_foreign_keys_antiguas():
                print("✗ Error al eliminar Foreign Keys antiguas")
                return False
            
            # Paso 9-11: Eliminar columnas antiguas
            print("\n[8/9] Eliminando columnas antiguas...")
            if not self.eliminar_columna_administrador():
                print("✗ Error al eliminar ID_Administrador")
                return False
            
            if not self.eliminar_columna_recepcionista():
                print("✗ Error al eliminar ID_Recepcionista")
                return False
            
            if not self.eliminar_columna_pl():
                print("✗ Error al eliminar ID_PL")
                return False
            
            # Paso 12: Verificar
            print("\n[9/9] Verificando resultado...")
            if not self.verificar_migracion():
                return False
            
            print("\n" + "="*60)
            print("✓ MIGRACIÓN COMPLETADA EXITOSAMENTE")
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
    migracion = MigracionHistorial(
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
