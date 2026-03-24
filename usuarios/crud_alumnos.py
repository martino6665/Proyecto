from sqlalchemy.orm import Session
import models, dtos

# --- GESTIÓN DE IDENTIDAD ---

def crear_alumno(db: Session, usuario: dtos.AlumnoCreate):
    """
    Registra un nuevo estudiante en la tabla unificada de usuarios.
    """
    db_usuario = models.Usuario(
        password=usuario.password,
        nombre=usuario.nombre,
        apellido_paterno=usuario.apellido_paterno,
        apellido_materno=usuario.apellido_materno,
        fecha_nacimiento=usuario.fecha_nacimiento,
        rol="alumno" 
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def find_usuario(db: Session, login_data: str):
    """
    Busca al alumno para el proceso de Login (por ID numérico o Nombre).
    """
    if login_data.isdigit():
        return db.query(models.Usuario).filter(models.Usuario.id == int(login_data)).first()
    return db.query(models.Usuario).filter(models.Usuario.nombre == login_data).first()

# --- CONSULTAS DEL ALUMNO ---

def listar_mis_cursos_alumno(db: Session, alumno_id: int):
    """
    Realiza un JOIN para mostrar las materias donde el alumno está inscrito.
    """
    return db.query(models.Curso).join(models.Inscripcion).filter(
        models.Inscripcion.alumno_id == alumno_id
    ).all()