from sqlalchemy.orm import Session
import models, dtos

# --- REGISTRO DE PROFESOR ---

def crear_profesor(db: Session, usuario: dtos.ProfesorCreate):
    """
    Registra un nuevo profesor en la tabla unificada de usuarios.
    """
    db_usuario = models.Usuario(
        password=usuario.password,
        nombre=usuario.nombre,
        apellido_paterno=usuario.apellido_paterno,
        apellido_materno=usuario.apellido_materno,
        fecha_nacimiento=usuario.fecha_nacimiento,
        rol="profesor"
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

# --- GESTIÓN DE CURSOS PROPIOS ---

def listar_mis_cursos_profesor(db: Session, maestro_id: int):
    """
    Lista solo los cursos donde este profesor es el titular asignado.
    """
    return db.query(models.Curso).filter(models.Curso.id_del_profesor == maestro_id).all()

def actualizar_curso_maestro(db: Session, curso_id: int, maestro_id: int, curso_update: dtos.CursoCreate):
    """
    Edita un curso solo si el maestro_id coincide con el creador (Seguridad).
    """
    db_curso = db.query(models.Curso).filter(
        models.Curso.id == curso_id, 
        models.Curso.id_del_profesor == maestro_id
    ).first()
    
    if db_curso:
        db_curso.nombre_del_curso = curso_update.nombre_del_curso
        db_curso.descripcion = curso_update.descripcion
        db_curso.fecha_de_inicio = curso_update.fecha_de_inicio
        db_curso.fecha_de_fin = curso_update.fecha_de_fin
        db.commit()
        db.refresh(db_curso)
    return db_curso

def eliminar_curso_maestro(db: Session, curso_id: int, maestro_id: int):
    """
    Elimina el curso completo y dispara automáticamente el borrado 
    en cascada de las inscripciones vinculadas.
    """
    db_curso = db.query(models.Curso).filter(
        models.Curso.id == curso_id, 
        models.Curso.id_del_profesor == maestro_id
    ).first()
    
    if db_curso:
        db.delete(db_curso)
        db.commit()
        return True
    return False

# --- FUNCIÓN DE APOYO PARA LOGIN ---

def find_usuario(db: Session, login_data: str):
    """
    Permite buscar al profesor por su ID o Nombre para el acceso al sistema.
    """
    if login_data.isdigit():
        return db.query(models.Usuario).filter(models.Usuario.id == int(login_data)).first()
    return db.query(models.Usuario).filter(models.Usuario.nombre == login_data).first()