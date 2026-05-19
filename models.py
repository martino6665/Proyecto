from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    nombre = Column(String(100), index=True)
    apellido_paterno = Column(String(100))
    apellido_materno = Column(String(100))
    fecha_nacimiento = Column(Date)  # Almacena fechas reales. Requiere parseo en el CRUD.
    rol = Column(String(50), nullable=False)  # "alumno" o "profesor"

    # --- RELACIONES ---
    # Si el usuario es profesor, mapea los cursos que imparte
    cursos_dictados = relationship("Curso", back_populates="profesor", cascade="all, delete-orphan")
    
    # Si el usuario es alumno, mapea las inscripciones que posee
    inscripciones_alumno = relationship("Inscripcion", back_populates="alumno", cascade="all, delete-orphan")


class Curso(Base):
    __tablename__ = "cursos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_del_curso = Column(String(255), index=True, nullable=False)
    id_del_profesor = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    descripcion = Column(String(500)) 
    fecha_de_inicio = Column(Date)
    fecha_de_fin = Column(Date)
    
    # --- RELACIONES ---
    # Enlace directo al profesor que imparte la materia
    profesor = relationship("Usuario", back_populates="cursos_dictados")
    
    # Enlace a la tabla intermedia de inscripciones para auditar alumnos y notas
    inscripciones = relationship("Inscripcion", back_populates="curso", cascade="all, delete-orphan")


class Inscripcion(Base):
    __tablename__ = "inscripciones"
    
    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    curso_id = Column(Integer, ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False)
    calificacion = Column(Integer, nullable=True)  # Puede ser nulo hasta que el profesor califique

    # --- RELACIONES RELATIVAS ---
    # Permite acceder directo a los datos del alumno inscrito desde la inscripción
    alumno = relationship("Usuario", back_populates="inscripciones_alumno")
    
    # Permite acceder directo a los detalles del curso desde la inscripción
    curso = relationship("Curso", back_populates="inscripciones")