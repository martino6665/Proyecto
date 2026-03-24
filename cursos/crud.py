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


# --- ACCIONES GLOBALES ---

def crear_curso(db: Session, curso: dtos.CursoCreate):
    """
    Crea un nuevo curso vinculándolo al ID del profesor.
    """
    db_curso = models.Curso(
        nombre_del_curso=curso.nombre_del_curso,
        id_del_profesor=curso.id_del_profesor, 
        descripcion=curso.descripcion,
        fecha_de_inicio=curso.fecha_de_inicio,
        fecha_de_fin=curso.fecha_de_fin
    )
    db.add(db_curso)
    db.commit()
    db.refresh(db_curso)
    return db_curso

def eliminar_curso_global(db: Session, curso_id: int):
    """
    Elimina un curso sin validar quién lo hace (Uso administrativo).
    Gracias al CASCADE en models.py, limpia las inscripciones automáticamente.
    """
    db_curso = find_curso(db, curso_id)
    if db_curso:
        db.delete(db_curso)
        db.commit()
        return True
    return False