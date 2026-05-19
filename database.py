import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Ruta absoluta blindada para Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'sql_app.db')}"

# 2. Motor de base de datos
engine = create_engine(
    SQL_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# CORRECCIÓN AQUÍ: Removemos el autoflush=False que está rompiendo el flujo relacional
SessionLocal = sessionmaker(autocommit=False, bind=engine)

Base = declarative_base()