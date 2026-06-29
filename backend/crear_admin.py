import bcrypt
from app.core.database import SessionLocal
import app.models as models
from app.crud.facturacion import generar_boleta_final

db = SessionLocal()

try:
    print("====== INICIANDO ACTUALIZACIÓN DE CONTRASEÑAS ======")
    
    # 1. Generamos el hash nuevo oficial para la contraseña "123"
    password_plana = "123"
    hash_bytes = bcrypt.hashpw(password_plana.encode('utf-8'), bcrypt.gensalt())
    nuevo_hash = hash_bytes.decode('utf-8')
    
    # 2. Traemos a TODOS los usuarios que existen en la base de datos
    usuarios = db.query(models.Usuario).all()
    print(f"Se encontraron {len(usuarios)} usuarios en la base de datos.")
    
    # 3. Recorremos uno por uno y actualizamos su password_hash y estado
    for usuario in usuarios:
        usuario.password_hash = nuevo_hash
        usuario.activo = "activo"  # Nos aseguramos de que todos estén aptos para loguearse
        print(f" -> Chancando contraseña para: {usuario.nombre} ({usuario.correo})")
    
    # 4. Guardamos los cambios en MySQL
    db.commit()

    # 5. Creamos boletas de prueba para algunas reservas activas/confirmadas/finalizadas
    reservas = db.query(models.Reserva).filter(models.Reserva.estado.in_(["activa", "confirmada", "finalizada"])).limit(3).all()
    if reservas:
        boletas_generadas = 0
        for reserva in reservas:
            existente = db.query(models.Boleta).filter(models.Boleta.ID_Reserva == reserva.ID_Reserva).first()
            if existente:
                continue
            boleta = generar_boleta_final(db, reserva.ID_Reserva)
            boletas_generadas += 1
            print(f" -> Boleta creada: ID {boleta.ID_Boleta}, Reserva {reserva.ID_Reserva}, Habitación {reserva.ID_Habitacion}, Total {float(boleta.total)}")

        if boletas_generadas == 0:
            print("No se generaron boletas nuevas porque ya existían boletas para las reservas seleccionadas.")
    else:
        print("No se encontraron reservas activas/confirmadas/finalizadas para crear boletas de prueba.")

    configuracion = db.query(models.Configuracion).order_by(models.Configuracion.ID_Configuracion).first()
    if not configuracion:
        configuracion = models.Configuracion(
            nombre_hotel="Hotel PMS",
            hora_checkin="15:00",
            hora_checkout="12:00"
        )
        db.add(configuracion)
        db.commit()
        print("✔ Configuración base creada en la base de datos.")

    print("====================================================")
    print("¡ÉXITO! Todos los usuarios existentes han sido actualizados.")
    print("Ahora todos pueden iniciar sesión usando la contraseña: 123")
    print("====================================================")

except Exception as e:
    db.rollback()
    print(f"❌ Hubo un error al chancar los usuarios: {e}")
finally:
    db.close()