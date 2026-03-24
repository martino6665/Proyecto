from pydantic import BaseModel
import datetime
from typing import Optional

# --- ESQUEMAS PARA CURSOS ---
class CursoBase(BaseModel):
    nombre_del_curso: str
    id_del_profesor: int
    descripcion: str
    fecha_de_inicio: datetime.date 
    fecha_de_fin: datetime.date

class CursoCreate(CursoBase):
    pass

class CursoResponse(CursoBase):
    id: int 
    class Config:
        from_attributes = True

# --- BASE PARA USUARIOS ---
class PersonaBase(BaseModel):
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    fecha_nacimiento: datetime.date

# --- Lógica para Alumnos ---
class AlumnoCreate(PersonaBase):
    password: str

class AlumnoResponse(PersonaBase):
    id: int  
    rol: str
    class Config:
        from_attributes = True

# --- Lógica para Profesores ---
class ProfesorCreate(PersonaBase):
    password: str

class ProfesorResponse(PersonaBase):
    id: int  
    rol: str
    class Config:
        from_attributes = True

# --- ESQUEMA PARA INSCRIPCIONES ---
class InscripcionCreate(BaseModel):
    alumno_id: int
    curso_id: int

class InscripcionResponse(InscripcionCreate):
    id: int
    # --- COMPLEMENTOS AÑADIDOS ---
    calificacion: Optional[int] = None  # Permite que la nota sea nula al inicio
    # fecha_registro: Optional[datetime.datetime] = None # Descomenta si añadiste la fecha en models
    
    class Config:
        from_attributes = True

# --- ESQUEMA PARA ACTUALIZAR CALIFICACIÓN ---
class CalificacionUpdate(BaseModel):
    """DTO específico para que el profesor envíe solo la nota."""
    nota: int