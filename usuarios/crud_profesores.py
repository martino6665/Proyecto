from datetime import datetime
from sqlalchemy.orm import Session
import models
import dtos

# --- GESTIÓN DE IDENTIDAD ---

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
        rol="profesor"  # ASIGNACIÓN AUTOMÁTICA Y SEGURA ELIMINA ERRORES
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


# --- CONSULTAS DEL PROFESOR ---

def listar_mis_cursos_profesor(db: Session, maestro_id: int):
    """
    Trae todos los cursos que un profesor específico imparte (es dueño).
    Aprovecha la relación relacional 'cursos_dictados' añadida en models.py.
    """
    return db.query(models.Curso).filter(models.Curso.id_del_profesor == maestro_id).all()