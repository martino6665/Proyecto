from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models
import dtos

# ==============================================================================
# --- 📝 OPERACIONES BÁSICAS DE INSCRIPCIÓN ---
# ==============================================================================

def inscribir_alumno(db: Session, inscripcion: dtos.InscripcionCreate):
    """
    Crea el vínculo (inscripción) entre un alumno y un curso en la tabla intermedia.
    Valida la existencia de las llaves foráneas y evita duplicaciones en la base de datos.
    """
    # 1. VALIDACIÓN DEL ALUMNO: Interroga a la tabla 'Usuario' verificando que el rol sea correcto
    alumno_existe = db.query(models.Usuario).filter(
        models.Usuario.id == inscripcion.alumno_id,
        models.Usuario.rol == "alumno"
    ).first()
    
    if not alumno_existe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error: El alumno con ID {inscripcion.alumno_id} no existe en el sistema. Vuelve a iniciar sesión."
        )

    # 2. VALIDACIÓN DEL CURSO: Verifica si el curso seleccionado sigue activo en Render
    curso_existe = db.query(models.Curso).filter(models.Curso.id == inscripcion.curso_id).first()
    if not curso_existe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error: El curso con ID {inscripcion.curso_id} no existe o fue eliminado por el profesor."
        )

    # 3. EVITAR DUPLICADOS (VERIFICADO): Si el alumno ya está en el curso, lanzamos un estado 409 Conflict
    inscripcion_duplicada = obtener_inscripcion(db, inscripcion.alumno_id, inscripcion.curso_id)
    if inscripcion_duplicada is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,  # Verificado: Código HTTP exacto para registros duplicados
            detail="Ya te encuentras registrado oficialmente en esta materia."
        )

    # Si pasa todas las aduanas de control, se guarda de forma segura en la tabla intermedia
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


# ==============================================================================
# --- 📊 GESTIÓN DE CALIFICACIONES GLOBALES ---
# ==============================================================================

def calificar_alumno_curso(db: Session, alumno_id: int, curso_id: int, nota: int):
    # VALIDACIÓN EXTRA: Rango de calificación
    if nota < 0 or nota > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La calificación debe estar entre 0 y 100."
        )

    db_inscripcion = obtener_inscripcion(db, alumno_id, curso_id)
    
    if not db_inscripcion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ninguna inscripción para el alumno {alumno_id} en el curso {curso_id}."
        )
        
    db_inscripcion.calificacion = nota
    db.commit()
    db.refresh(db_inscripcion)
    
    return dtos.SimpleResponse(
        estado="Exitoso",
        mensaje=f"Calificación de {nota} asignada correctamente al alumno."
    )


# ==============================================================================
# --- ❌ ELIMINACIÓN / BAJAS ---
# ==============================================================================

def dar_de_baja_curso(db: Session, alumno_id: int, curso_id: int):
    """
    Elimina permanentemente la relación de la tabla intermedia (Darse de baja).
    Retorna la estructura estricta tipada de dtos.SimpleResponse para Retrofit.
    """
    db_inscripcion = obtener_inscripcion(db, alumno_id, curso_id)
    
    if db_inscripcion:
        db.delete(db_inscripcion)
        db.commit()
        return dtos.SimpleResponse(
            estado="Exitoso",
            mensaje="Baja del curso procesada correctamente."
        )
        
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No se pudo procesar la baja porque el alumno no está inscrito en este curso."
    )