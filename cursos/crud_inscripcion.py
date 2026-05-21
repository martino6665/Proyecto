from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models
import dtos

# --- OPERACIONES BÁSICAS ---

def inscribir_alumno(db: Session, inscripcion: dtos.InscripcionCreate):
    """
    Crea el vínculo (inscripción) entre un alumno y un curso en la tabla intermedia.
    Valida la existencia de las llaves foráneas para evitar colapsos por IDs inexistentes.
    """
    # 1. VALIDACIÓN DEL ALUMNO: Verifica si el ID enviado desde Kotlin existe en Render
    alumno_existe = db.query(models.Alumno).filter(models.Alumno.id == inscripcion.alumno_id).first()
    if not alumno_existe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error: El alumno con ID {inscripcion.alumno_id} no existe en el sistema. Vuelve a iniciar sesión."
        )

    # 2. VALIDACIÓN DEL CURSO: Verifica si el curso seleccionado sigue activo
    curso_existe = db.query(models.Curso).filter(models.Curso.id == inscripcion.curso_id).first()
    if not curso_existe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error: El curso con ID {inscripcion.curso_id} no existe o fue eliminado por el profesor."
        )

    # 3. EVITAR DUPLICADOS: Si ya está inscrito, no creamos otra fila idéntica
    inscripcion_duplicada = obtener_inscripcion(db, inscripcion.alumno_id, inscripcion.curso_id)
    if inscripcion_duplicada is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya te encuentras registrado voluntariamente en esta materia."
        )

    # Si pasa todas las aduanas, se guarda de forma segura
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
        # CORREGIDO: Retorno unificado en una sola línea y llaves cerradas correctamente
        return {
            "estado": "Exitoso",
            "mensaje": "Baja del curso procesada correctamente."
        }
        
    return {
        "estado": "Error",
        "mensaje": "No se pudo procesar la baja porque el alumno no está inscrito en este curso."
    }