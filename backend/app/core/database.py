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

# Configuración del motor de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True  # Evita desconexiones silenciosas con MySQL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependencia para los Routers/EndPoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()