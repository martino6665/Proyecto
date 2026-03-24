from sqlalchemy.orm import Session
import models, dtos

# --- OPERACIONES BÁSICAS ---

def inscribir_alumno(db: Session, inscripcion: dtos.InscripcionCreate):
    """
    Crea el vínculo entre un alumno y un curso.
    """
    db_inscripcion = models.Inscripcion(
        alumno_id=inscripcion.alumno_id,
        curso_id=inscripcion.curso_id
    )
    db.add(db_inscripcion)
    db.commit()
    db.refresh(db_inscripcion)
    return db_inscripcion

def obtener_inscripcion(db: Session, alumno_id: int, curso_id: int):
    """
    Busca una inscripción específica. Útil para validar antes de calificar.
    """
    return db.query(models.Inscripcion).filter(
        models.Inscripcion.alumno_id == alumno_id,
        models.Inscripcion.curso_id == curso_id
    ).first()

# --- GESTIÓN DE CALIFICACIONES (El extra) ---

def asignar_calificacion(db: Session, alumno_id: int, curso_id: int, nota: int):
    """
    Permite al profesor subir o modificar la nota de un alumno.
    """
    db_inscripcion = obtener_inscripcion(db, alumno_id, curso_id)
    
    if db_inscripcion:
        db_inscripcion.calificacion = nota
        db.commit()
        db.refresh(db_inscripcion)
        return db_inscripcion
    return None

# --- ELIMINACIÓN ---

def dar_de_baja(db: Session, alumno_id: int, curso_id: int):
    """
    Elimina la relación de la tabla intermedia.
    """
    db_inscripcion = obtener_inscripcion(db, alumno_id, curso_id)
    
    if db_inscripcion:
        db.delete(db_inscripcion)
        db.commit()
        return True
    return False