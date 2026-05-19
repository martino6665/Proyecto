from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    password = Column(String(255), nullable=False)
    nombre_usuario = Column(String(50), unique=True, index=True, nullable=False)
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
    
    inscripciones = relationship("Inscripcion", cascade="all, delete-orphan", backref="curso")

class Inscripcion(Base):
    __tablename__ = "inscripciones"
    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"))
    curso_id = Column(Integer, ForeignKey("cursos.id", ondelete="CASCADE"))
    calificacion = Column(Integer, nullable=True)