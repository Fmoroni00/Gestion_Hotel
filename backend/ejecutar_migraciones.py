"""
Script Maestro: Ejecutar todas las migraciones en secuencia
Permite ejecutar todas las migraciones de una sola vez con confirmación
"""

import subprocess
import sys
import os


class EjecutorMigraciones:
    """Ejecuta todas las migraciones en orden."""
    
    def __init__(self):
        """Inicializa el ejecutor."""
        self.migraciones = [
            ('migracion_01_amenidades.py', 'Crear tablas de amenidades (M:N)'),
            ('migracion_02_parking.py', 'Verificar integridad y limpiar parking'),
            ('migracion_03_boleta.py', 'Crear respaldo y limpiar boleta'),
            ('migracion_04_historial.py', 'Consolidar usuarios en historial'),
            ('migracion_05_indices.py', 'Crear índices de optimización'),
        ]
        self.resultados = []
    
    def mostrar_menu(self):
        """Muestra el menú de opciones."""
        print("="*70)
        print("EJECUTOR DE MIGRACIONES - HOTEL PROYECTO")
        print("="*70)
        print()
        print("Migraciones disponibles:")
        print()
        
        for i, (script, descripcion) in enumerate(self.migraciones, 1):
            print(f"  {i}. {script}")
            print(f"     {descripcion}")
            print()
        
        print("Opciones:")
        print("  1-5  : Ejecutar migración específica")
        print("  a    : Ejecutar TODAS las migraciones")
        print("  v    : Verificar credenciales")
        print("  s    : Salir")
        print()
    
    def ejecutar_migracion(self, indice):
        """Ejecuta una migración específica."""
        if indice < 0 or indice >= len(self.migraciones):
            print("✗ Índice inválido")
            return False
        
        script, descripcion = self.migraciones[indice]
        
        print()
        print("="*70)
        print(f"Ejecutando: {script}")
        print(f"Descripción: {descripcion}")
        print("="*70)
        print()
        
        try:
            resultado = subprocess.run(
                [sys.executable, script],
                cwd=os.path.dirname(__file__),
                capture_output=False
            )
            
            exito = resultado.returncode == 0
            self.resultados.append((script, exito))
            
            if exito:
                print()
                print(f"✓ {script} completado exitosamente")
            else:
                print()
                print(f"✗ {script} terminó con errores (código: {resultado.returncode})")
            
            return exito
        
        except Exception as e:
            print(f"✗ Error al ejecutar {script}: {e}")
            self.resultados.append((script, False))
            return False
    
    def ejecutar_todas(self, confirmacion=True):
        """Ejecuta todas las migraciones en orden."""
        if confirmacion:
            print()
            print("⚠ Advertencia: Ejecutarás TODAS las migraciones")
            print("Orden de ejecución:")
            for i, (script, _) in enumerate(self.migraciones, 1):
                print(f"  {i}. {script}")
            
            respuesta = input("\n¿Estás seguro de que deseas continuar? (s/n): ").strip().lower()
            if respuesta != 's':
                print("Operación cancelada")
                return False
        
        print()
        for i in range(len(self.migraciones)):
            if not self.ejecutar_migracion(i):
                respuesta = input(f"\nLa migración {i+1} falló. ¿Continuar? (s/n): ").strip().lower()
                if respuesta != 's':
                    print("Ejecución cancelada")
                    return False
        
        return True
    
    def mostrar_resultados(self):
        """Muestra un resumen de los resultados."""
        if not self.resultados:
            return
        
        print()
        print("="*70)
        print("RESUMEN DE EJECUCIÓN")
        print("="*70)
        print()
        
        exitosas = sum(1 for _, exito in self.resultados if exito)
        fallidas = len(self.resultados) - exitosas
        
        for script, exito in self.resultados:
            estado = "✓ EXITOSA" if exito else "✗ FALLIDA"
            print(f"  {script}: {estado}")
        
        print()
        print(f"Exitosas: {exitosas}/{len(self.resultados)}")
        print(f"Fallidas: {fallidas}/{len(self.resultados)}")
        print("="*70)
    
    def verificar_credenciales(self):
        """Ejecuta el script de verificación."""
        print()
        print("Ejecutando verificación de credenciales...")
        print()
        
        try:
            subprocess.run(
                [sys.executable, 'verificar_migraciones.py'],
                cwd=os.path.dirname(__file__)
            )
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def ejecutar(self):
        """Bucle principal interactivo."""
        while True:
            self.mostrar_menu()
            
            opcion = input("Selecciona una opción: ").strip().lower()
            
            if opcion == 's':
                self.mostrar_resultados()
                print("\nGracias por usar el ejecutor de migraciones")
                break
            
            elif opcion == 'v':
                self.verificar_credenciales()
                input("\nPresiona Enter para continuar...")
            
            elif opcion == 'a':
                if self.ejecutar_todas(confirmacion=True):
                    self.mostrar_resultados()
                input("\nPresiona Enter para continuar...")
            
            elif opcion.isdigit():
                indice = int(opcion) - 1
                if 0 <= indice < len(self.migraciones):
                    self.ejecutar_migracion(indice)
                    input("\nPresiona Enter para continuar...")
                else:
                    print("✗ Opción inválida")
                    input("\nPresiona Enter para continuar...")
            
            else:
                print("✗ Opción no reconocida")
                input("\nPresiona Enter para continuar...")
            
            # Limpiar pantalla
            os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Función principal."""
    ejecutor = EjecutorMigraciones()
    
    # Si se pasa argumento 'auto', ejecuta todas automáticamente sin confirmación
    if len(sys.argv) > 1 and sys.argv[1] == 'auto':
        if ejecutor.ejecutar_todas(confirmacion=False):
            print("\n✓ Todas las migraciones completadas")
            sys.exit(0)
        else:
            print("\n✗ Algunas migraciones fallaron")
            sys.exit(1)
    
    # Si se pasa un número, ejecuta esa migración específica
    elif len(sys.argv) > 1 and sys.argv[1].isdigit():
        indice = int(sys.argv[1]) - 1
        if ejecutor.ejecutar_migracion(indice):
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Modo interactivo
    else:
        ejecutor.ejecutar()


if __name__ == "__main__":
    main()
