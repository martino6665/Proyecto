from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException  # Verificado: Importación explícita para evitar errores de contexto
import models
import dtos

# ==============================================================================
# --- 👤 GESTIÓN DE IDENTIDAD ---
# ==============================================================================

def crear_profesor(db: Session, profesor: dtos.ProfesorCreate):
    """
    Registra un nuevo profesor en la tabla única de usuarios.
    Convierte de forma segura la cadena String de la fecha a un objeto Date de Python.
    """
    # Parseo seguro de string "YYYY-MM-DD" a objeto datetime.date de SQLAlchemy
    fecha_nacimiento_date = datetime.strptime(profesor.fecha_nacimiento.strip(), "%Y-%m-%d").date()

    db_usuario = models.Usuario(
        nombre_usuario=profesor.nombre_usuario.strip(),
        password=profesor.password.strip(),
        nombre=profesor.nombre.strip(),
        apellido_paterno=profesor.apellido_paterno.strip(),
        apellido_materno=profesor.apellido_materno.strip(),
        fecha_nacimiento=fecha_nacimiento_date,
        rol="profesor"  # Asignación automatizada elimina fallas de rol en el cliente
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


# ==============================================================================
# --- 📚 CONSULTAS Y ACCIONES DEL PROFESOR ---
# ==============================================================================

def listar_mis_cursos_profesor(db: Session, maestro_id: int):
    """
    Trae todos los cursos que un profesor específico imparte (es dueño).
    Aprovecha la relación relacional 'cursos_dictados' añadida en models.py.
    """
    return db.query(models.Curso).filter(models.Curso.id_del_profesor == maestro_id).all()


def crear_actividad_para_curso(db: Session, curso_id: int, actividad: dtos.ActividadCreate):
    """
    El profesor inserta una nueva actividad/tarea vinculada a uno de sus cursos activos.
    """
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


def obtener_alumnos_inscritos_en_materia(db: Session, curso_id: int):
    """
    El profesor consulta la lista de alumnos registrados oficialmente en su curso.
    Inspecciona la tabla 'inscripciones' y extrae los perfiles mediante la relación relacional.
    """
    inscripciones = db.query(models.Inscripcion).filter(models.Inscripcion.curso_id == curso_id).all()
    
    # Mapeo directo y seguro de los objetos Usuario enlazados en cada inscripción
    lista_alumnos = [ins.alumno for ins in inscripciones if ins.alumno is not None]
    return lista_alumnos


def calificar_entrega_de_alumno(db: Session, entrega_id: int, evaluacion: dtos.CalificarEntregaRequest):
    """
    El profesor evalúa y asigna una calificación junto con retroalimentación 
    a una entrega específica enviada previamente por un alumno.
    """
    db_entrega = db.query(models.EntregaActividad).filter(models.EntregaActividad.id == entrega_id).first()
    
    if not db_entrega:
        raise HTTPException(
            status_code=404, 
            detail="No se encontró la entrega especificada para calificar en el servidor de Render."
        )
        
    db_entrega.nota_obtenida = evaluacion.nota_obtenida
    db_entrega.comentario_profesor = evaluacion.comentario_profesor.strip() if evaluacion.comentario_profesor else None
    
    db.commit()
    db.refresh(db_entrega)
    return db_entrega