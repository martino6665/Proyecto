import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Calculamos la ruta absoluta real de la carpeta donde vive este archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Forzamos a que la base de datos se cree de forma segura dentro de tu proyecto
SQL_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'sql_app.db')}"

# 3. Creamos el motor de la base de datos con los argumentos correctos
engine = create_engine(
    SQL_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()