import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Carga automáticamente las variables del archivo .env
load_dotenv()

# Lee la URL de la base de datos desde el entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Si por alguna razón no lee el .env, usa esta ruta por defecto con tu usuario y clave
if not DATABASE_URL:
    DATABASE_URL = "mysql+pymysql://root:123@localhost:3306/hotel_db"


def build_engine(database_url: str | None = None):
    """Crea un motor SQLAlchemy con un pool pequeño para entornos con pocos slots de BD."""
    pool_size = int(os.getenv("DB_POOL_SIZE", "1"))
    max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "0"))
    pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "1800"))

    return create_engine(
        database_url or DATABASE_URL,
        pool_pre_ping=True,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_recycle=pool_recycle,
        pool_timeout=30,
    )


# Configuración del motor de SQLAlchemy
engine = build_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependencia para los Routers/EndPoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()