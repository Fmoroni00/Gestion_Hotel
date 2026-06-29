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


def table_exists(cursor, table):
    cursor.execute("SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s", (DB_CONFIG['database'], table))
    return cursor.fetchone()[0] > 0


def fk_defined(cursor, table, column, ref_table, ref_column):
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s AND REFERENCED_TABLE_NAME=%s AND REFERENCED_COLUMN_NAME=%s",
        (DB_CONFIG['database'], table, column, ref_table, ref_column),
    )
    return cursor.fetchone()[0] > 0


def main():
    print('migracion_06_verificacion: Iniciando verificación de esquema')
    conn = get_conn()
    cursor = conn.cursor()
    try:
        tables = [
            'usuario', 'administrador', 'recepcionista', 'personal_limpieza', 'huesped', 'codigo_acceso',
            'habitacion', 'amenidad', 'habitacion_amenidad', 'servicio', 'reserva', 'boleta', 'consumo',
            'nota_servicio', 'parking', 'asignacion_parking', 'historial', 'configuracion'
        ]

        print('\nVerificación de tablas:')
        for t in tables:
            ok = table_exists(cursor, t)
            print(f'{t}:', 'OK' if ok else 'ERROR (no existe)')

        # Lista de FKs esperadas (tabla, columna, ref_table, ref_col)
        expected_fks = [
            ('administrador', 'ID_Usuario', 'usuario', 'ID_Usuario'),
            ('recepcionista', 'ID_Usuario', 'usuario', 'ID_Usuario'),
            ('personal_limpieza', 'ID_Usuario', 'usuario', 'ID_Usuario'),
            ('codigo_acceso', 'DNI', 'huesped', 'DNI'),
            ('habitacion_amenidad', 'ID_Habitacion', 'habitacion', 'ID_Habitacion'),
            ('habitacion_amenidad', 'ID_Amenidad', 'amenidad', 'ID_Amenidad'),
            ('reserva', 'DNI', 'huesped', 'DNI'),
            ('reserva', 'ID_Habitacion', 'habitacion', 'ID_Habitacion'),
            ('reserva', 'ID_Recepcionista', 'recepcionista', 'ID_Usuario'),
            ('boleta', 'ID_Reserva', 'reserva', 'ID_Reserva'),
            ('boleta', 'ID_Asignacion', 'asignacion_parking', 'ID_Asignacion'),
            ('consumo', 'ID_Reserva', 'reserva', 'ID_Reserva'),
            ('consumo', 'ID_Servicio', 'servicio', 'ID_Servicio'),
            ('nota_servicio', 'ID_Reserva', 'reserva', 'ID_Reserva'),
            ('nota_servicio', 'ID_Servicio', 'servicio', 'ID_Servicio'),
            ('asignacion_parking', 'ID_Reserva', 'reserva', 'ID_Reserva'),
            ('asignacion_parking', 'ID_Parking', 'parking', 'ID_Parking'),
            ('historial', 'ID_Habitacion', 'habitacion', 'ID_Habitacion'),
            ('historial', 'ID_Usuario', 'usuario', 'ID_Usuario'),
        ]

        print('\nVerificación de FKs:')
        for table, col, ref_table, ref_col in expected_fks:
            ok = fk_defined(cursor, table, col, ref_table, ref_col)
            print(f'{table}.{col} -> {ref_table}.{ref_col}:', 'OK' if ok else 'ERROR (FK faltante)')

        print('\nmigracion_06_verificacion: Verificación completada')
    except Exception as e:
        print('migracion_06_verificacion: ERROR durante verificación:', e)
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()
