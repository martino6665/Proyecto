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

# --- INICIALIZACIÓN DE BASE DE DATOS ---
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


# ==============================================================================
# --- 🔍 GENERAL / BÚSQUEDAS ---
# ==============================================================================

@app.get("/usuarios/buscar", response_model=List[dtos.UsuarioResponse], tags=["General"])
def buscar_usuarios(query: str = "", db: Session = Depends(get_db)):
    return crud_alumnos.buscar_usuarios_global(db, query)


# ==============================================================================
# --- 🔑 REGISTRO Y ACCESO ---
# ==============================================================================

@app.post("/registro/alumno", response_model=dtos.AlumnoResponse, tags=["Registro"])
def registrar_alumno(alumno: dtos.AlumnoCreate, db: Session = Depends(get_db)):
    return crud_alumnos.crear_alumno(db, alumno)

@app.post("/registro/profesor", response_model=dtos.ProfesorResponse, tags=["Registro"])
def registrar_profesor(profesor: dtos.ProfesorCreate, db: Session = Depends(get_db)):
    return crud_profesores.crear_profesor(db, profesor)


@app.post("/login", response_model=dtos.LoginResponse, tags=["Acceso"])
def login(login_data: dtos.LoginRequest, db: Session = Depends(get_db)):
    u_ingresado = login_data.nombre_usuario.strip()
    p_ingresada = login_data.password.strip()

    user = db.query(models.Usuario).filter(models.Usuario.nombre_usuario == u_ingresado).first()
    
    if not user:
        return {"estado": "Error", "mensaje": f"No existe el usuario: {u_ingresado}", "rol": None, "usuario_id": None}
    
    if user.password != p_ingresada:
        return {"estado": "Error", "mensaje": "Contraseña incorrecta", "rol": None, "usuario_id": None}
    
    return {
        "estado": "Exitoso", 
        "mensaje": f"¡Bienvenido de nuevo, {user.nombre}!", 
        "rol": user.rol,
        "usuario_id": user.id
    }


# ==============================================================================
# --- 🎓 MÓDULO ALUMNOS ---
# ==============================================================================

@app.get("/alumnos/cursos/buscar", response_model=List[dtos.CursoResponse], tags=["Alumnos"])
def buscar_cursos(query: str = "", db: Session = Depends(get_db)):
    return crud_cursos.buscar_todos_los_cursos(db, query)

@app.get("/alumnos/{alumno_id}/mis-cursos", response_model=List[dtos.CursoResponse], tags=["Alumnos"])
def ver_cursos_inscritos(alumno_id: int, db: Session = Depends(get_db)):
    return crud_alumnos.listar_mis_cursos_alumno(db, alumno_id)

@app.post("/alumnos/inscribir", response_model=dtos.InscripcionResponse, tags=["Alumnos"])
def inscribirse(inscripcion: dtos.InscripcionCreate, db: Session = Depends(get_db)):
    return crud_inscripcion.inscribir_alumno(db, inscripcion)

@app.delete("/alumnos/desinscribir/{alumno_id}/{curso_id}", response_model=dtos.SimpleResponse, tags=["Alumnos"])
def salir_de_curso(alumno_id: int, curso_id: int, db: Session = Depends(get_db)):
    return crud_inscripcion.dar_de_baja_curso(db, alumno_id, curso_id)

@app.post("/alumnos/actividades/{actividad_id}/entregar/{alumno_id}", response_model=dtos.EntregaResponse, tags=["Alumnos - Actividades"])
def entregar_actividad(actividad_id: int, alumno_id: int, entrega: dtos.EntregaCreate, db: Session = Depends(get_db)):
    actividad = db.query(models.Actividad).filter(models.Actividad.id == actividad_id).first()
    if not actividad:
        raise HTTPException(status_code=404, detail="La actividad no existe.")
    return crud_alumnos.registrar_entrega_alumno(db, actividad_id, alumno_id, entrega)

# (NUEVA) Agenda Real del Alumno
@app.get("/alumnos/{alumno_id}/agenda", response_model=List[dtos.EntregaResponse], tags=["Alumnos - Actividades"])
def ver_agenda_escolar_alumno(alumno_id: int, db: Session = Depends(get_db)):
    return db.query(models.EntregaActividad).filter(models.EntregaActividad.alumno_id == alumno_id).all()


# ==============================================================================
# --- 👨‍🏫 MÓDULO PROFESORES ---
# ==============================================================================

@app.get("/profesores/alumnos", response_model=List[dtos.AlumnoResponse], tags=["Profesores"])
def obtener_lista_de_alumnos(db: Session = Depends(get_db)):
    return crud_alumnos.listar_todos_los_alumnos(db)

@app.post("/profesores/cursos/crear", response_model=dtos.CursoResponse, tags=["Profesores"])
def crear_materia(curso: dtos.CursoCreate, db: Session = Depends(get_db)):
    return crud_cursos.crear_curso(db=db, curso=curso)

@app.get("/profesores/{maestro_id}/mis-cursos", response_model=List[dtos.CursoResponse], tags=["Profesores"])
def ver_materias_asignadas(maestro_id: int, db: Session = Depends(get_db)):
    return crud_profesores.listar_mis_cursos_profesor(db, maestro_id)

@app.put("/profesores/cursos/actualizar/{curso_id}/{maestro_id}", response_model=dtos.CursoResponse, tags=["Profesores"])
def actualizar_materia(curso_id: int, maestro_id: int, curso_data: dtos.CursoCreate, db: Session = Depends(get_db)):
    return crud_cursos.actualizar_curso_existente(db, curso_id, maestro_id, curso_data)

# MODIFICACIÓN: Borrado seguro e integral
@app.delete("/profesores/cursos/eliminar/{curso_id}/{maestro_id}", response_model=dtos.SimpleResponse, tags=["Profesores"])
def eliminar_materia(curso_id: int, maestro_id: int, db: Session = Depends(get_db)):
    curso = db.query(models.Curso).filter(models.Curso.id == curso_id, models.Curso.id_del_profesor == maestro_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="El curso no existe o no te pertenece.")
    db.delete(curso)
    db.commit()
    return {"estado": "Exitoso", "mensaje": "Curso y su estructura escolar eliminados correctamente."}

@app.put("/profesores/calificar/{alumno_id}/{curso_id}", response_model=dtos.SimpleResponse, tags=["Profesores"])
def asignar_calificacion(alumno_id: int, curso_id: int, calificacion: dtos.CalificacionUpdate, db: Session = Depends(get_db)):
    return crud_inscripcion.calificar_alumno_curso(db, alumno_id, curso_id, calificacion.nota)

# (NUEVA) Pendientes del Maestro
@app.get("/profesores/{maestro_id}/pendientes", response_model=List[dtos.EntregaResponse], tags=["Profesores - Actividades"])
def ver_pendientes_calificar_maestro(maestro_id: int, db: Session = Depends(get_db)):
    return db.query(models.EntregaActividad).join(models.Actividad).join(models.Curso).filter(
        models.Curso.id_del_profesor == maestro_id,
        models.EntregaActividad.nota_obtenida == None
    ).all()


# --- RUTAS DE ACTIVIDADES ---

@app.post("/profesores/cursos/{curso_id}/actividades", response_model=dtos.ActividadResponse, tags=["Profesores - Actividades"])
def asignar_actividad_a_materia(curso_id: int, actividad: dtos.ActividadCreate, db: Session = Depends(get_db)):
    try:
        # Validación básica de existencia del curso
        curso = db.query(models.Curso).filter(models.Curso.id == curso_id).first()
        if not curso:
            raise HTTPException(status_code=404, detail="El curso no existe.")
        
        # Llamada al CRUD
        return crud_profesores.crear_actividad_para_curso(db, curso_id, actividad)
        
    except Exception as e:
        # Esto te permitirá ver el error real en la terminal de VS Code
        print(f"Error en endpoint asignar_actividad: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# ¡ESTA ES LA RUTA QUE TE FALTABA PARA VERLAS EN LA APP!
@app.get("/profesores/cursos/{curso_id}/actividades", response_model=List[dtos.ActividadResponse], tags=["Profesores - Actividades"])
def obtener_actividades_por_curso(curso_id: int, db: Session = Depends(get_db)):
    return db.query(models.Actividad).filter(models.Actividad.curso_id == curso_id).all()

@app.get("/profesores/cursos/{curso_id}/alumnos-inscritos", response_model=List[dtos.UsuarioResponse], tags=["Profesores - Actividades"])
def ver_alumnos_activos_en_curso(curso_id: int, db: Session = Depends(get_db)):
    return crud_profesores.obtener_alumnos_inscritos_en_materia(db, curso_id)

@app.put("/profesores/entregas/{entrega_id}/calificar", response_model=dtos.EntregaResponse, tags=["Profesores - Actividades"])
def evaluar_entrega_alumno(entrega_id: int, evaluacion: dtos.CalificarEntregaRequest, db: Session = Depends(get_db)):
    return crud_profesores.calificar_entrega_de_alumno(db, entrega_id, evaluacion)