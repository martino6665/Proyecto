import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, dtos
import cursos.crud as crud
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Gestión de Cursos - Octavo Semestre")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Bienvenido a la API de Cursos",
        "docs": "/docs"
    }

# --- RUTAS DE CURSOS ---

@app.get("/cursos/{curso_id}", response_model=dtos.CursoResponse)
def get_curso(curso_id: int, db: Session = Depends(get_db)):
    db_curso = crud.find_curso(db=db, curso_id=curso_id)
    if db_curso is None:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return db_curso

@app.get("/cursos", response_model=list[dtos.CursoResponse])
def get_cursos(db: Session = Depends(get_db)):
    return crud.get_cursos(db)

@app.post("/cursos", response_model=dtos.CursoResponse, status_code=201)
def crear_curso(curso: dtos.CursoCreate, db: Session = Depends(get_db)):
    return crud.crear_curso(db=db, curso=curso)

@app.put("/cursos/{curso_id}", response_model=dtos.CursoResponse)
def actualizar_curso(curso_id: int, curso: dtos.CursoCreate, db: Session = Depends(get_db)):
    db_curso = crud.actualizar_curso(db=db, curso_id=curso_id, curso_update=curso)
    if db_curso is None:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return db_curso

@app.delete("/cursos/{curso_id}", response_model=dtos.CursoResponse)
def eliminar_curso(curso_id: int, db: Session = Depends(get_db)):
    db_curso = crud.eliminar_curso(db=db, curso_id=curso_id)
    if db_curso is None:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return db_curso