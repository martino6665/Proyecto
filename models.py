from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    password = Column(String(255), nullable=False)
    nombre = Column(String(100), index=True)
    apellido_paterno = Column(String(100))
    apellido_materno = Column(String(100))
    fecha_nacimiento = Column(Date)
    rol = Column(String(50), nullable=False)

class Curso(Base):
    __tablename__ = "cursos"
    id = Column(Integer, primary_key=True, index=True)
    nombre_del_curso = Column(String(255), index=True)
    id_del_profesor = Column(Integer, ForeignKey("usuarios.id"), index=True)
    descripcion = Column(String(500)) 
    fecha_de_inicio = Column(Date)
    fecha_de_fin = Column(Date)
    
    # Esta línea limpia las inscripciones cuando el curso se borra
    inscripciones = relationship("Inscripcion", cascade="all, delete-orphan", backref="curso")

class Inscripcion(Base):
    __tablename__ = "inscripciones"
    id = Column(Integer, primary_key=True, index=True)
    
    # Llaves foráneas con borrado en cascada a nivel DB
    alumno_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"))
    curso_id = Column(Integer, ForeignKey("cursos.id", ondelete="CASCADE"))

    # --- CAMPOS ADICIONALES ACTUALIZADOS ---
    calificacion = Column(Integer, nullable=True) # Permite que la nota sea nula al inicio
    fecha_registro = Column(DateTime, default=func.now()) # Se genera automáticamente al inscribirse