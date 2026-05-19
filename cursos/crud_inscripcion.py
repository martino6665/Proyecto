from sqlalchemy.orm import Session
import models
import dtos

# --- OPERACIONES BÁSICAS ---

def inscribir_alumno(db: Session, inscripcion: dtos.InscripcionCreate):
    """
    Crea el vínculo (inscripción) entre un alumno y un curso en la tabla intermedia.
    """
    db_inscripcion = models.Inscripcion(
        alumno_id=inscripcion.alumno_id,
        curso_id=inscripcion.curso_id,
        calificacion=None  # Toda inscripción arranca sin calificación asignada
    )
    db.add(db_inscripcion)
    db.commit()
    db.refresh(db_inscripcion)
    return db_inscripcion


def obtener_inscripcion(db: Session, alumno_id: int, curso_id: int):
    """
    Busca una inscripción específica por los IDs de alumno y curso.
    """
    return db.query(models.Inscripcion).filter(
        models.Inscripcion.alumno_id == alumno_id,
        models.Inscripcion.curso_id == curso_id
    ).first()


# --- GESTIÓN DE CALIFICACIONES ---

def calificar_alumno_curso(db: Session, alumno_id: int, curso_id: int, nota: int):
    """
    Permite al profesor asignar o modificar la nota de un alumno en un curso específico.
    Retorna un diccionario mapeado con la estructura estricta de dtos.SimpleResponse.
    """
    db_inscripcion = obtener_inscripcion(db, alumno_id, curso_id)
    
    if not db_inscripcion:
        return {
            "estado": "Error",
            "mensaje": f"No se encontró ninguna inscripción para el alumno {alumno_id} en el curso {curso_id}."
        }
        
    db_inscripcion.calificacion = nota
    db.commit()
    db.refresh(db_inscripcion)
    
    return {
        "estado": "Exitoso",
        "mensaje": f"Calificación de {nota} asignada correctamente al alumno."
    }


# --- ELIMINACIÓN / BAJAS ---

def dar_de_baja_curso(db: Session, alumno_id: int, curso_id: int):
    """
    Elimina permanentemente la relación de la tabla intermedia (Darse de baja).
    Retorna un diccionario mapeado con la estructura estricta de dtos.SimpleResponse.
    """
    db_inscripcion = obtener_inscripcion(db, alumno_id, curso_id)
    
    if db_inscripcion:
        db.delete(db_inscripcion)
        db.commit()
        return {
            "estado": "Exitoso",
            "mensaje": "Baja del curso procesada correctamente."
        }
        
    return {
        "estado": "Error",
        "mensaje": "No se pudo procesar la baja porque el alumno no está inscrito en este curso."
    }