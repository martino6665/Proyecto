import datetime
from fastapi import FastAPI, Depends, HTTPException, status
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

# Dependencia de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", tags=["General"])
def read_root():
    return {"status": "Online", "msg": "API VisionEducation v1.2"}

# --- REGISTRO Y ACCESO ---

@app.post("/registro/alumno", response_model=dtos.AlumnoResponse, tags=["Registro"])
def registrar_alumno(alumno: dtos.AlumnoCreate, db: Session = Depends(get_db)):
    return crud_alumnos.crear_alumno(db=db, usuario=alumno)

@app.post("/registro/profesor", response_model=dtos.ProfesorResponse, tags=["Registro"])
def registrar_profesor(profesor: dtos.ProfesorCreate, db: Session = Depends(get_db)):
    return crud_profesores.crear_profesor(db=db, usuario=profesor)

@app.get("/login/{login_data}", response_model=dtos.AlumnoResponse, tags=["Acceso"])
def login(login_data: str, db: Session = Depends(get_db)):
    user = crud_alumnos.find_usuario(db, login_data) 
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

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

# --- FUNCIÓN AGREGADA/CORREGIDA: EDITAR MATERIA ---
@app.put("/profesores/cursos/editar/{curso_id}/{maestro_id}", response_model=dtos.CursoResponse, tags=["Profesores"])
def editar_materia(curso_id: int, maestro_id: int, curso: dtos.CursoCreate, db: Session = Depends(get_db)):
    """Permite al profesor editar los detalles de su curso."""
    db_curso = crud_profesores.actualizar_curso_maestro(db, curso_id, maestro_id, curso)
    if not db_curso:
        raise HTTPException(status_code=403, detail="No tienes permiso sobre este curso o el curso no existe")
    return db_curso

@app.put("/profesores/calificar/{alumno_id}/{curso_id}", response_model=dtos.InscripcionResponse, tags=["Profesores"])
def asignar_nota(alumno_id: int, curso_id: int, nota_data: dtos.CalificacionUpdate, db: Session = Depends(get_db)):
    resultado = crud_inscripcion.assign_calificacion(db, alumno_id, curso_id, nota_data.nota)
    if not resultado:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    return resultado

# --- CONSULTAS DE TABLAS (PARA POSTMAN) ---

@app.get("/tablas/alumnos", response_model=List[dtos.AlumnoResponse], tags=["Tablas"])
def get_all_alumnos(db: Session = Depends(get_db)):
    return db.query(models.Usuario).filter(models.Usuario.rol == "alumno").all()

@app.get("/tablas/profesores", response_model=List[dtos.ProfesorResponse], tags=["Tablas"])
def get_all_profesores(db: Session = Depends(get_db)):
    return db.query(models.Usuario).filter(models.Usuario.rol == "profesor").all()

@app.get("/tablas/cursos", response_model=List[dtos.CursoResponse], tags=["Tablas"])
def get_all_cursos(db: Session = Depends(get_db)):
    return db.query(models.Curso).all()

# --- RUTAS DE ELIMINACIÓN ADMIN ---

@app.delete("/admin/alumnos/{alumno_id}", tags=["Admin"])
def eliminar_alumno_total(alumno_id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == alumno_id, models.Usuario.rol == "alumno").first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    db.delete(db_usuario)
    db.commit()
    return {"mensaje": f"Alumno con ID {alumno_id} eliminado exitosamente"}

@app.delete("/admin/profesores/{profesor_id}", tags=["Admin"])
def eliminar_profesor_total(profesor_id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == profesor_id, models.Usuario.rol == "profesor").first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")

    cantidad_cursos = db.query(models.Curso).filter(models.Curso.id_del_profesor == profesor_id).count()
    if cantidad_cursos > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede borrar: El profesor tiene {cantidad_cursos} curso(s) asignado(s). Elimina primero los cursos."
        )

    db.delete(db_usuario)
    db.commit()
    return {"mensaje": f"Profesor {db_usuario.nombre} eliminado exitosamente"}

@app.delete("/admin/cursos/{curso_id}", tags=["Admin"])
def eliminar_curso_admin(curso_id: int, db: Session = Depends(get_db)):
    exito = crud_cursos.eliminar_curso_global(db, curso_id)
    if not exito:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return {"mensaje": f"Curso con ID {curso_id} eliminado exitosamente"}