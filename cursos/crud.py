from datetime import datetime
from sqlalchemy.orm import Session
import models
import dtos

# --- CONSULTAS GENERALES ---

def get_cursos(db: Session):
    """Trae todos los cursos existentes. Útil para la lista general en Android."""
    return db.query(models.Curso).all()


def find_curso(db: Session, curso_id: int):
    """Busca un curso específico por su ID único."""
    return db.query(models.Curso).filter(models.Curso.id == curso_id).first()


# NUEVA: Requerida por el endpoint de búsqueda con filtros del alumno
def buscar_todos_los_cursos(db: Session, query: str = ""):
    """
    Busca cursos cuyo nombre o descripción coincidan con la palabra clave.
    Si no hay query, regresa todos los cursos de forma estándar.
    """
    if not query.strip():
        return get_cursos(db)
    
    return db.query(models.Curso).filter(
        (models.Curso.nombre_del_curso.ilike(f"%{query}%")) |
        (models.Curso.descripcion.ilike(f"%{query}%"))
    ).all()


# --- ACCIONES DEL PROFESOR (CON VALIDACIÓN DE PERMISOS) ---

def crear_curso(db: Session, curso: dtos.CursoCreate):
    """
    Crea un nuevo curso vinculándolo al ID del profesor.
    Convierte de forma segura las cadenas String de fechas a objetos Date de Python.
    """
    # Parseo preventivo de strings "YYYY-MM-DD" a objetos datetime.date de SQLAlchemy
    fecha_inicio_date = datetime.strptime(curso.fecha_de_inicio.strip(), "%Y-%m-%d").date()
    fecha_fin_date = datetime.strptime(curso.fecha_de_fin.strip(), "%Y-%m-%d").date()

    db_curso = models.Curso(
        nombre_del_curso=curso.nombre_del_curso.strip(),
        id_del_profesor=curso.id_del_profesor, 
        descripcion=curso.descripcion.strip(),
        fecha_de_inicio=fecha_inicio_date,
        fecha_de_fin=fecha_fin_date
    )
    db.add(db_curso)
    db.commit()
    db.refresh(db_curso)
    return db_curso


# NUEVA: Requerida por el endpoint de actualización del profesor
def actualizar_curso_existente(db: Session, curso_id: int, maestro_id: int, curso_data: dtos.CursoCreate):
    """
    Busca un curso y lo actualiza, validando estrictamente que pertenezca al maestro que lo solicita.
    """
    db_curso = db.query(models.Curso).filter(
        models.Curso.id == curso_id,
        models.Curso.id_del_profesor == maestro_id
    ).first()

    if not db_curso:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404, 
            detail="Curso no encontrado o no tienes permisos para modificarlo."
        )

    # Convertimos los nuevos strings de fechas recibidos
    db_curso.nombre_del_curso = curso_data.nombre_del_curso.strip()
    db_curso.descripcion = curso_data.descripcion.strip()
    db_curso.fecha_de_inicio = datetime.strptime(curso_data.fecha_de_inicio.strip(), "%Y-%m-%d").date()
    db_curso.fecha_de_fin = datetime.strptime(curso_data.fecha_de_fin.strip(), "%Y-%m-%d").date()

    db.commit()
    db.refresh(db_curso)
    return db_curso


# CORREGIDA: Sincronizada con el main y protegida por ID de profesor
def eliminar_curso_existente(db: Session, curso_id: int, maestro_id: int):
    """
    Elimina un curso validando que el maestro que lo solicita sea el dueño.
    Retorna la estructura estricta de dtos.SimpleResponse.
    """
    db_curso = db.query(models.Curso).filter(
        models.Curso.id == curso_id,
        models.Curso.id_del_profesor == maestro_id
    ).first()
    
    if db_curso:
        db.delete(db_curso)
        db.commit()
        return dtos.SimpleResponse(
            estado="Exitoso",
            mensaje="El curso y sus inscripciones asociadas fueron eliminados correctamente."
        )
        
    return {
        "estado": "Error",
        "mensaje": "No se pudo eliminar el curso. Verifica tus permisos o la existencia del ID."
    }