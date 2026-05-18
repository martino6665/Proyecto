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

# Inicialización de la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VisionEducation",
    description="Sistema de gestión de cursos Universitarios - CUValles",
    version="1.3.0"
)

# --- CONFIGURACIÓN DE CORS ---
# Permite que la App de Android se conecte desde cualquier red
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
    return {"estado": "En línea", "mensaje": "API VisionEducation v1.3 - CUValles"}

# --- REGISTRO Y ACCESO ---

@app.post("/registro/alumno", response_model=dtos.AlumnoResponse, tags=["Registro"])
def registrar_alumno(alumno: dtos.AlumnoCreate, db: Session = Depends(get_db)):
    # El CRUD debe asignar rol="alumno" internamente
    return crud_alumnos.crear_alumno(db=db, usuario=alumno)

@app.post("/registro/profesor", response_model=dtos.ProfesorResponse, tags=["Registro"])
def registrar_profesor(profesor: dtos.ProfesorCreate, db: Session = Depends(get_db)):
    # El CRUD debe asignar rol="profesor" internamente
    return crud_profesores.crear_profesor(db=db, usuario=profesor)

# --- LOGIN PROFESIONAL (Sincronizado con Android) ---
@app.post("/login", response_model=dtos.LoginResponse, tags=["Acceso"])
def login(login_data: dtos.LoginRequest, db: Session = Depends(get_db)):
    # 1. Bloqueo de datos vacíos (Quita espacios extras con .strip())
    usuario_ingresado = login_data.usuario.strip()
    pass_ingresada = login_data.password.strip()

    if not usuario_ingresado or not pass_ingresada:
        return {"estado": "Error", "mensaje": "Por favor, llena todos los campos", "rol": None}

    # 2. Búsqueda por 'nombre_usuario' (el apodo ej. Martin11)
    user = db.query(models.Usuario).filter(models.Usuario.nombre_usuario == usuario_ingresado).first()
    
    if not user:
        return {"estado": "Error", "mensaje": "El usuario no existe", "rol": None}
    
    # 3. Validación de contraseña
    if user.password != pass_ingresada:
        return {"estado": "Error", "mensaje": "La contraseña es incorrecta", "rol": None}
    
    # 4. Respuesta exitosa
    # Mandamos el rol para que Android sepa si mandarlo al Dashboard de Alumno o Profe
    return {
        "estado": "Exitoso",
        "mensaje": f"¡Bienvenido de nuevo, {user.nombre}!",
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

@app.delete("/alumnos/desinscribir/{alumno_id}/{curso_id}", tags=["Alumnos"])
def dar_de_baja_materia(alumno_id: int, curso_id: int, db: Session = Depends(get_db)):
    exito = crud_inscripcion.dar_de_baja(db, alumno_id, curso_id)
    if not exito:
        raise HTTPException(status_code=404, detail="No se encontró la inscripción")
    return {"mensaje": "Materia dada de baja correctamente"}

# --- MÓDULO PROFESORES ---

@app.post("/profesores/cursos/crear", response_model=dtos.CursoResponse, tags=["Profesores"])
def crear_materia(curso: dtos.CursoCreate, db: Session = Depends(get_db)):
    return crud_cursos.crear_curso(db=db, curso=curso)

@app.get("/profesores/{maestro_id}/mis-cursos", response_model=List[dtos.CursoResponse], tags=["Profesores"])
def ver_materias_asignadas(maestro_id: int, db: Session = Depends(get_db)):
    return crud_profesores.listar_mis_cursos_profesor(db, maestro_id)

@app.put("/profesores/cursos/editar/{curso_id}/{maestro_id}", response_model=dtos.CursoResponse, tags=["Profesores"])
def editar_materia(curso_id: int, maestro_id: int, curso: dtos.CursoCreate, db: Session = Depends(get_db)):
    db_curso = crud_profesores.actualizar_curso_maestro(db, curso_id, maestro_id, curso)
    if not db_curso:
        raise HTTPException(status_code=403, detail="Sin permiso o curso inexistente")
    return db_curso

@app.put("/profesores/calificar/{alumno_id}/{curso_id}", response_model=dtos.InscripcionResponse, tags=["Profesores"])
def asignar_nota(alumno_id: int, curso_id: int, nota_data: dtos.CalificacionUpdate, db: Session = Depends(get_db)):
    resultado = crud_inscripcion.assign_calificacion(db, alumno_id, curso_id, nota_data.nota)
    if not resultado:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    return resultado