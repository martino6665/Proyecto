from datetime import datetime
from sqlalchemy.orm import Session
import models
import dtos

# ==============================================================================
# --- 👤 GESTIÓN DE IDENTIDAD ---
# ==============================================================================

def crear_alumno(db: Session, usuario: dtos.AlumnoCreate):
    """
    Registra un nuevo alumno en la tabla única de usuarios.
    Convierte de forma segura la cadena String de la fecha a un objeto Date de Python.
    """
    # Parseo seguro de string "YYYY-MM-DD" a objeto datetime.date de SQLAlchemy
    fecha_nacimiento_date = datetime.strptime(usuario.fecha_nacimiento.strip(), "%Y-%m-%d").date()

    db_usuario = models.Usuario(
        nombre_usuario=usuario.nombre_usuario.strip(),
        password=usuario.password.strip(),
        nombre=usuario.nombre.strip(),
        apellido_paterno=usuario.apellido_paterno.strip(),
        apellido_materno=usuario.apellido_materno.strip(),
        fecha_nacimiento=fecha_nacimiento_date,
        rol="alumno"  # Asignación automática y segura
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def find_usuario_por_id(db: Session, usuario_id: int):
    """
    Busca un usuario específico por su ID único en la base de datos.
    """
    return db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()


def buscar_usuarios_global(db: Session, query: str = ""):
    """
    Busca usuarios (alumnos o profesores) cuyo nombre_usuario, nombre o apellido
    coincidan con la palabra clave. Si no hay query, regresa todos de forma estándar.
    """
    if not query.strip():
        return db.query(models.Usuario).all()
        
    return db.query(models.Usuario).filter(
        (models.Usuario.nombre_usuario.ilike(f"%{query}%")) |
        (models.Usuario.nombre.ilike(f"%{query}%")) |
        (models.Usuario.apellido_paterno.ilike(f"%{query}%"))
    ).all()


# ==============================================================================
# --- 📚 CONSULTAS Y ENTREGAS DEL ALUMNO ---
# ==============================================================================

def listar_mis_cursos_alumno(db: Session, alumno_id: int):
    """
    Realiza un JOIN preciso para mostrar las materias donde el alumno está inscrito actualmente.
    """
    return db.query(models.Curso).join(
        models.Inscripcion, models.Curso.id == models.Inscripcion.curso_id
    ).filter(
        models.Inscripcion.alumno_id == alumno_id
    ).all()


def listar_todos_los_alumnos(db: Session):
    """
    Trae estrictamente a los usuarios cuyo rol sea 'alumno'.
    """
    return db.query(models.Usuario).filter(models.Usuario.rol == "alumno").all()


# NUEVA MEJORA EN LÍNEA RECTA: El alumno sube o actualiza su tarea
def registrar_entrega_alumno(db: Session, actividad_id: int, alumno_id: int, entrega: dtos.EntregaCreate):
    """
    Permite al alumno registrar el contenido de su tarea para una actividad específica.
    Si ya existía un envío, sobreescribe el texto y actualiza la estampa de tiempo.
    """
    entrega_previa = db.query(models.EntregaActividad).filter(
        models.EntregaActividad.actividad_id == actividad_id,
        models.EntregaActividad.alumno_id == alumno_id
    ).first()

    if entrega_previa:
        entrega_previa.contenido_entrega = entrega.contenido_entrega.strip()
        entrega_previa.fecha_entrega = datetime.utcnow()  # Actualiza la fecha de modificación
        db.commit()
        db.refresh(entrega_previa)
        return entrega_previa

    # Si es su primer intento de entrega, inserta el nuevo registro relacional
    db_entrega = models.EntregaActividad(
        actividad_id=actividad_id,
        alumno_id=alumno_id,
        contenido_entrega=entrega.contenido_entrega.strip()
    )
    db.add(db_entrega)
    db.commit()
    db.refresh(db_entrega)
    return db_entrega