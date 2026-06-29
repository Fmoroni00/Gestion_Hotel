import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
import app.models as models

# 1. Importamos los enrutadores
from app.routers import autenticacion, habitaciones, huespedes, administracion
from app.routers import reservas, servicios, facturacion, parking, notas_servicio, historial, codigos_acceso

# 2. Inicializamos las tablas en la base de datos (si alguna falta, SQLAlchemy la crea)
Base.metadata.create_all(bind=engine)

# 3. Configuramos la instancia principal de FastAPI (ESTA ES LA VARIABLE 'app' QUE BUSCA UVICORN)
app = FastAPI(
    title="Sistema de Gestión Hotelera (PMS)",
    description="API para el control de usuarios, habitaciones, reservas y facturación.",
    version="1.0.0"
)

# 4. Configuramos CORS para que tu frontend (Vue) pueda conectarse sin problemas
allowed_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "https://gestion-hotel-168m.onrender.com,http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 5. Registramos las rutas
app.include_router(autenticacion.router, prefix="/api/v1")
app.include_router(habitaciones.router, prefix="/api/v1")
app.include_router(huespedes.router, prefix="/api/v1")
app.include_router(reservas.router, prefix="/api/v1")
app.include_router(servicios.router, prefix="/api/v1")
app.include_router(facturacion.router, prefix="/api/v1")
app.include_router(administracion.router, prefix="/api/v1")
app.include_router(parking.router, prefix="/api/v1")
app.include_router(notas_servicio.router, prefix="/api/v1")
app.include_router(historial.router, prefix="/api/v1")
app.include_router(codigos_acceso.router, prefix="/api/v1")

# 6. Ruta base para comprobar que el servidor está vivo
@app.get("/", tags=["General"])
def read_root():
    return {"mensaje": "API del Sistema Hotelero en línea y conectada a MySQL"}