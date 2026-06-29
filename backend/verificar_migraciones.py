"""
Script de verificación: Validar credenciales en todos los scripts de migración
Asegura que todos los scripts usen las credenciales correctas del .env
"""

import os
import re
import sys


def verificar_credenciales():
    """Verifica que todos los scripts tengan las credenciales correctas."""
    
    # Credenciales esperadas
    credenciales_esperadas = {
        'host': 'localhost',
        'user': 'root',
        'password': '1234',
        'database': 'hotel_db'
    }
    
    # Scripts a verificar
    scripts = [
        'migracion_01_amenidades.py',
        'migracion_02_parking.py',
        'migracion_03_boleta.py',
        'migracion_04_historial.py',
        'migracion_05_indices.py'
    ]
    
    print("="*70)
    print("VERIFICACIÓN DE CREDENCIALES EN SCRIPTS DE MIGRACIÓN")
    print("="*70)
    print()
    
    todos_correctos = True
    
    for script in scripts:
        ruta = os.path.join(os.path.dirname(__file__), script)
        
        if not os.path.exists(ruta):
            print(f"✗ {script}: ARCHIVO NO ENCONTRADO")
            todos_correctos = False
            continue
        
        print(f"📄 {script}")
        
        with open(ruta, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Buscar las credenciales en el __init__
        patron = r"def __init__\(.*?host='([^']+)'.*?user='([^']+)'.*?password='([^']*)'.*?database='([^']+)'"
        match = re.search(patron, contenido, re.DOTALL)
        
        if match:
            host, user, password, database = match.groups()
            
            credenciales_encontradas = {
                'host': host,
                'user': user,
                'password': password,
                'database': database
            }
            
            # Verificar cada credencial
            print(f"  host: {host} {'✓' if host == credenciales_esperadas['host'] else '✗'}")
            print(f"  user: {user} {'✓' if user == credenciales_esperadas['user'] else '✗'}")
            print(f"  password: {'*' * len(password)} {'✓' if password == credenciales_esperadas['password'] else '✗'}")
            print(f"  database: {database} {'✓' if database == credenciales_esperadas['database'] else '✗'}")
            
            # Verificar también en la función main()
            patron_main = r"def main\(\):.*?MigracionAmenidades\(.*?\)|MigracionParking\(.*?\)|MigracionBoleta\(.*?\)|MigracionHistorial\(.*?\)|MigracionIndices\(.*?\)"
            match_main = re.search(patron_main, contenido, re.DOTALL)
            
            if credenciales_encontradas != credenciales_esperadas:
                print(f"  ⚠ Advertencia: Credenciales inconsistentes")
                todos_correctos = False
            else:
                print(f"  ✓ Credenciales CORRECTAS")
        else:
            print(f"  ✗ No se encontraron credenciales")
            todos_correctos = False
        
        print()
    
    # Resumen
    print("="*70)
    if todos_correctos:
        print("✓ TODAS LAS CREDENCIALES SON CORRECTAS")
    else:
        print("✗ ALGUNAS CREDENCIALES NECESITAN CORRECCIÓN")
    print("="*70)
    
    return todos_correctos


def resumen_migraciones():
    """Proporciona un resumen de las migraciones disponibles."""
    
    print("\n" + "="*70)
    print("RESUMEN DE MIGRACIONES DISPONIBLES")
    print("="*70 + "\n")
    
    migraciones = [
        {
            'nombre': 'migracion_01_amenidades.py',
            'descripcion': 'Crear tablas de amenidades (M:N)',
            'impacto': 'ALTO'
        },
        {
            'nombre': 'migracion_02_parking.py',
            'descripcion': 'Verificar integridad y limpiar parking',
            'impacto': 'MEDIO'
        },
        {
            'nombre': 'migracion_03_boleta.py',
            'descripcion': 'Crear respaldo y limpiar boleta',
            'impacto': 'ALTO'
        },
        {
            'nombre': 'migracion_04_historial.py',
            'descripcion': 'Consolidar usuarios en historial',
            'impacto': 'ALTO'
        },
        {
            'nombre': 'migracion_05_indices.py',
            'descripcion': 'Crear índices de optimización',
            'impacto': 'BAJO'
        }
    ]
    
    for i, migracion in enumerate(migraciones, 1):
        print(f"{i}. {migracion['nombre']}")
        print(f"   Descripción: {migracion['descripcion']}")
        print(f"   Impacto: {migracion['impacto']}")
        print()
    
    print("="*70)
    print("Orden recomendado de ejecución:")
    print("  1. migracion_01_amenidades.py")
    print("  2. migracion_02_parking.py")
    print("  3. migracion_03_boleta.py")
    print("  4. migracion_04_historial.py")
    print("  5. migracion_05_indices.py")
    print("="*70 + "\n")


def main():
    """Función principal."""
    verificar_credenciales()
    resumen_migraciones()


if __name__ == "__main__":
    main()
