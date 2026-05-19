import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models, dtos
import cursos.crud as crud_cursos 
import cursos.crud_inscripcion as crud_inscripcion 
import usuarios.crud_alumnos as crud_alumnos 
import usuarios.crud_profesores as crud_profesores
from database import SessionLocal, engine

# --- INICIALIZACIÓN ---
# Solo creamos las tablas si no existen.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VisionEducation",
    description="Sistema de gestión de cursos Universitarios",
    version="1.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", tags=["General"])
def read_root():
    return {"estado": "En línea", "mensaje": "VisionEducation API - Estable"}

# --- REGISTRO ---
@app.post("/registro/alumno", response_model=dtos.AlumnoResponse, tags=["Registro"])
def registrar_alumno(alumno: dtos.AlumnoCreate, db: Session = Depends(get_db)):
    return crud_alumnos.crear_alumno(db=db, usuario=alumno)

@app.post("/registro/profesor", response_model=dtos.ProfesorResponse, tags=["Registro"])
def registrar_profesor(profesor: dtos.ProfesorCreate, db: Session = Depends(get_db)):
    return crud_profesores.crear_profesor(db=db, usuario=profesor)

# --- LOGIN CORREGIDO (Sin código repetido) ---
@app.post("/login", response_model=dtos.LoginResponse, tags=["Acceso"])
def login(login_data: dtos.LoginRequest, db: Session = Depends(get_db)):
    # 1. Limpiamos los datos de entrada para evitar espacios accidentales
    u_ingresado = login_data.nombre_usuario.strip()
    p_ingresada = login_data.password.strip()

    # 2. Buscamos en la base de datos por el campo unificado
    user = db.query(models.Usuario).filter(models.Usuario.nombre_usuario == u_ingresado).first()
    
    # 3. Validaciones de existencia y contraseña
    if not user:
        return {"estado": "Error", "mensaje": f"No existe el usuario: {u_ingresado}", "rol": None}
    
    if user.password != p_ingresada:
        return {"estado": "Error", "mensaje": "Contraseña incorrecta", "rol": None}
    
    # 4. Respuesta exitosa
    return {
        "estado": "Exitoso", 
        "mensaje": f"¡Bienvenido de nuevo, {user.nombre}!", 
        "rol": user.rol
    }

# --- ALUMNOS ---
@app.get("/alumnos/{alumno_id}/mis-cursos", response_model=List[dtos.CursoResponse], tags=["Alumnos"])
def ver_cursos_inscritos(alumno_id: int, db: Session = Depends(get_db)):
    return crud_alumnos.listar_mis_cursos_alumno(db, alumno_id)

@app.post("/alumnos/inscribir", response_model=dtos.InscripcionResponse, tags=["Alumnos"])
def inscribirse(inscripcion: dtos.InscripcionCreate, db: Session = Depends(get_db)):
    return crud_inscripcion.inscribir_alumno(db, inscribir)

# --- PROFESORES ---
@app.post("/profesores/cursos/crear", response_model=dtos.CursoResponse, tags=["Profesores"])
def crear_materia(curso: dtos.CursoCreate, db: Session = Depends(get_db)):
    return crud_cursos.crear_curso(db=db, curso=curso)

@app.get("/profesores/{maestro_id}/mis-cursos", response_model=List[dtos.CursoResponse], tags=["Profesores"])
def ver_materias_asignadas(maestro_id: int, db: Session = Depends(get_db)):
    return crud_profesores.listar_mis_cursos_profesor(db, maestro_id)