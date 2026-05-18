import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware # IMPORTANTE: Para que el cel conecte
from sqlalchemy.orm import Session
from typing import List

import models, dtos
import cursos.crud as crud_cursos 
import cursos.crud_inscripcion as crud_inscripcion 
import usuarios.crud_alumnos as crud_alumnos 
import usuarios.crud_profesores as crud_profesores
from database import SessionLocal, engine

# Inicialización de la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VisionEducation",
    description="Sistema de gestión de cursos Universitarios - CUValles",
    version="1.2.0"
)

# --- CONFIGURACIÓN MÁGICA DE CORS ---
# Esto permite que tu teléfono (que es un dispositivo externo) se conecte a Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencia de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", tags=["General"])
def read_root():
    # Sincronizado con lo que Android espera leer
    return {"estado": "En línea", "mensaje": "API VisionEducation v1.2"}

# --- REGISTRO Y ACCESO ---

@app.post("/registro/alumno", response_model=dtos.AlumnoResponse, tags=["Registro"])
def registrar_alumno(alumno: dtos.AlumnoCreate, db: Session = Depends(get_db)):
    return crud_alumnos.crear_alumno(db=db, usuario=alumno)

@app.post("/registro/profesor", response_model=dtos.ProfesorResponse, tags=["Registro"])
def registrar_profesor(profesor: dtos.ProfesorCreate, db: Session = Depends(get_db)):
    return crud_profesores.crear_profesor(db=db, usuario=profesor)

# --- LOGIN CORREGIDO (POST + DTO + SEGURIDAD) ---
@app.post("/login", response_model=dtos.LoginResponse, tags=["Acceso"])
def login(login_data: dtos.LoginRequest, db: Session = Depends(get_db)):
    """
    Busca al usuario por nombre y valida la contraseña.
    Coincide con lo que Android envía (usuario y password).
    """
    # 1. Buscamos en la tabla de Usuarios (que incluye alumnos y profesores)
    # Buscamos en la columna 'nombre' usando el 'usuario' que viene de Android
    user = db.query(models.Usuario).filter(models.Usuario.nombre == login_data.usuario).first()
    
    if not user:
        return {"estado": "Error", "mensaje": "Usuario no encontrado", "rol": None}
    
    # 2. Validamos contraseña (Asegúrate que en tu DB la columna sea 'password')
    if user.password != login_data.password:
        return {"estado": "Error", "mensaje": "Contraseña incorrecta", "rol": None}
    
    # 3. Respuesta exitosa que Android ya sabe leer
    return {
        "estado": "Exitoso",
        "mensaje": f"Bienvenido {user.nombre}",
        "rol": user.rol
    }

# --- MÓDULO ALUMNOS ---

@app.get("/alumnos/cursos/buscar/{curso_id}", response_model=dtos.CursoResponse, tags=["Alumnos"])
def buscar_curso_alumno(curso_id: int, db: Session = Depends(get_db)):
    db_curso = crud_cursos.find_curso(db, curso_id)
    if not db_curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return db_curso

@app.post("/alumnos/inscribir", response_model=dtos.InscripcionResponse, tags=["Alumnos"])
def inscribirse(inscripcion: dtos.InscripcionCreate, db: Session = Depends(get_db)):
    return crud_inscripcion.inscribir_alumno(db, inscripcion)

@app.get("/alumnos/{alumno_id}/mis-cursos", response_model=List[dtos.CursoResponse], tags=["Alumnos"])
def ver_cursos_inscritos(alumno_id: int, db: Session = Depends(get_db)):
    return crud_alumnos.listar_mis_cursos_alumno(db, alumno_id)

# ... El resto de tus rutas (delete, put, etc) se mantienen igual abajo ...