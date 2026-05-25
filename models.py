from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    nombre = Column(String(100), index=True)
    apellido_paterno = Column(String(100))
    apellido_materno = Column(String(100))
    fecha_nacimiento = Column(Date)
    rol = Column(String(50), nullable=False)

    # RELACIONES
    cursos_dictados = relationship("Curso", back_populates="profesor", cascade="all, delete-orphan")
    inscripciones_alumno = relationship("Inscripcion", back_populates="alumno", cascade="all, delete-orphan")
    entregas_realizadas = relationship("EntregaActividad", back_populates="alumno", cascade="all, delete-orphan")


class Curso(Base):
    __tablename__ = "cursos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_del_curso = Column(String(255), index=True, nullable=False)
    id_del_profesor = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    descripcion = Column(String(500)) 
    fecha_de_inicio = Column(Date)
    fecha_de_fin = Column(Date)
    color_banner = Column(String(50), default="#3F51B5")

    # RELACIONES
    profesor = relationship("Usuario", back_populates="cursos_dictados")
    inscripciones = relationship("Inscripcion", back_populates="curso", cascade="all, delete-orphan")
    actividades = relationship("Actividad", back_populates="curso", cascade="all, delete-orphan")


class Inscripcion(Base):
    __tablename__ = "inscripciones"
    
    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    curso_id = Column(Integer, ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False)
    calificacion = Column(Integer, nullable=True)

    # RELACIONES
    alumno = relationship("Usuario", back_populates="inscripciones_alumno")
    curso = relationship("Curso", back_populates="inscripciones")


class Actividad(Base):
    __tablename__ = "actividades"

    id = Column(Integer, primary_key=True, index=True)
    curso_id = Column(Integer, ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(String(1000), nullable=True)
    puntos_maximos = Column(Float, default=100.0)
    
    # ACTUALIZACIÓN: Incluimos fecha_inicio y cambiamos fecha_limite a Date para coincidir con el App
    fecha_inicio = Column(Date, nullable=True) 
    fecha_limite = Column(Date, nullable=True) 

    # RELACIONES
    curso = relationship("Curso", back_populates="actividades")
    entregas = relationship("EntregaActividad", back_populates="actividad", cascade="all, delete-orphan")
    
class EntregaActividad(Base):
    __tablename__ = "entregas_actividades"

    id = Column(Integer, primary_key=True, index=True)
    actividad_id = Column(Integer, ForeignKey("actividades.id", ondelete="CASCADE"), nullable=False)
    alumno_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    contenido_entrega = Column(String(2000), nullable=False)
    fecha_entrega = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Feedback
    nota_obtenida = Column(Float, nullable=True)
    comentario_profesor = Column(String(1000), nullable=True)

    # RELACIONES
    actividad = relationship("Actividad", back_populates="entregas")
    alumno = relationship("Usuario", back_populates="entregas_realizadas")