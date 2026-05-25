from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
import models
import dtos

# ==========================================
# --- MÓDULO: CONSULTAS GENERALES Y BÚSQUEDAS ---
# ==========================================

def get_cursos(db: Session):
    """Trae todos los cursos existentes. Útil para la lista general en Android."""
    return db.query(models.Curso).all()


def find_curso(db: Session, curso_id: int):
    """Busca un curso específico por su ID único."""
    return db.query(models.Curso).filter(models.Curso.id == curso_id).first()


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


# ==========================================
# --- MÓDULO PROFESORES: GESTIÓN DE MATERIAS ---
# ==========================================

def crear_curso(db: Session, curso: dtos.CursoCreate):
    """
    Crea un nuevo curso vinculándolo al ID del profesor.
    Convierte de forma segura las cadenas String de fechas a objetos Date de Python.
    """
    fecha_inicio_date = datetime.strptime(curso.fecha_de_inicio.strip(), "%Y-%m-%d").date()
    fecha_fin_date = datetime.strptime(curso.fecha_de_fin.strip(), "%Y-%m-%d").date()

    db_curso = models.Curso(
        nombre_del_curso=curso.nombre_del_curso.strip(),
        id_del_profesor=curso.id_del_profesor, 
        descripcion=curso.descripcion.strip(),
        fecha_de_inicio=fecha_inicio_date,
        fecha_de_fin=fecha_fin_date,
        color_banner=curso.color_banner # SINCRONIZADO: Guarda el color elegido en la paleta
    )
    db.add(db_curso)
    db.commit()
    db.refresh(db_curso)
    return db_curso


def actualizar_curso_existente(db: Session, curso_id: int, maestro_id: int, curso_data: dtos.CursoCreate):
    """
    Busca un curso y lo actualiza, validando estrictamente que pertenezca al maestro que lo solicita.
    """
    db_curso = db.query(models.Curso).filter(
        models.Curso.id == curso_id,
        models.Curso.id_del_profesor == maestro_id
    ).first()

    if not db_curso:
        raise HTTPException(
            status_code=404, 
            detail="Curso no encontrado o no tienes permisos para modificarlo."
        )

    db_curso.nombre_del_curso = curso_data.nombre_del_curso.strip()
    db_curso.descripcion = curso_data.descripcion.strip()
    db_curso.fecha_de_inicio = datetime.strptime(curso_data.fecha_de_inicio.strip(), "%Y-%m-%d").date()
    db_curso.fecha_de_fin = datetime.strptime(curso_data.fecha_de_fin.strip(), "%Y-%m-%d").date()
    db_curso.color_banner = curso_data.color_banner # SINCRONIZADO: Permite cambiar de color en la edición

    db.commit()
    db.refresh(db_curso)
    return db_curso


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
            mensaje="El curso, actividades e inscripciones asociadas fueron eliminados correctamente."
        )
        
    raise HTTPException(
        status_code=404,
        detail="No se pudo eliminar el curso. Verifica tus permisos o la existencia del ID."
    )


# ==========================================
# --- NUEVA LÓGICA: ACTIVIDADES ESCUELA ---
# ==========================================

def crear_actividad_para_curso(db: Session, curso_id: int, actividad: dtos.ActividadCreate):
    """Inserta una nueva tarea/actividad asignada por el profesor dentro de un curso."""
    db_actividad = models.Actividad(
        curso_id=curso_id,
        titulo=actividad.titulo.strip(),
        descripcion=actividad.descripcion.strip() if actividad.descripcion else None,
        puntos_maximos=actividad.puntos_maximos
    )
    db.add(db_actividad)
    db.commit()
    db.refresh(db_actividad)
    return db_actividad


def registrar_entrega_alumno(db: Session, actividad_id: int, alumno_id: int, entrega: dtos.EntregaCreate):
    """Inserta la respuesta o entrega de la tarea por parte de un estudiante."""
    # Validación preventiva: Verificar si el alumno ya realizó una entrega para esta actividad
    entrega_previa = db.query(models.EntregaActividad).filter(
        models.EntregaActividad.actividad_id == actividad_id,
        models.EntregaActividad.alumno_id == alumno_id
    ).first()

    if entrega_previa:
        # Si ya existía, actualizamos el contenido con la nueva entrega de forma segura
        entrega_previa.contenido_entrega = entrega.contenido_entrega.strip()
        entrega_previa.fecha_entrega = datetime.utcnow()
        db.commit()
        db.refresh(entrega_previa)
        return entrega_previa

    db_entrega = models.EntregaActividad(
        actividad_id=actividad_id,
        alumno_id=alumno_id,
        contenido_entrega=entrega.contenido_entrega.strip()
    )
    db.add(db_entrega)
    db.commit()
    db.refresh(db_entrega)
    return db_entrega


def calificar_entrega_existente(db: Session, entrega_id: int, evaluacion: dtos.CalificarEntregaRequest):
    """Permite al profesor calificar y dejar comentarios sobre la entrega de un alumno."""
    db_entrega = db.query(models.EntregaActividad).filter(models.EntregaActividad.id == entrega_id).first()
    
    if not db_entrega:
        raise HTTPException(status_code=404, detail="La entrega del alumno no existe.")
        
    db_entrega.nota_obtenida = evaluacion.nota_obtenida
    db_entrega.comentario_profesor = evaluacion.comentario_profesor.strip() if evaluacion.comentario_profesor else None
    
    db.commit()
    db.refresh(db_entrega)
    return db_entrega


def obtener_alumnos_inscritos_en_materia(db: Session, curso_id: int):
    """Filtra y devuelve todos los usuarios con rol de alumno registrados de forma oficial en el curso."""
    # Buscamos a través de tu entidad intermedia Inscripcion
    inscripciones = db.query(models.Inscripcion).filter(models.Inscripcion.curso_id == curso_id).all()
    
    # Extraemos la lista limpia de usuarios/alumnos mapeados en las relaciones relativas
    lista_alumnos = [ins.alumno for ins in inscripciones if ins.alumno is not None]
    return lista_alumnos