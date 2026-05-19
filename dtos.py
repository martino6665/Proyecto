from pydantic import BaseModel
import datetime
from typing import Optional

# --- ESQUEMA PARA LOGIN ---
class LoginRequest(BaseModel):
    nombre_usuario: str  # CAMBIO: Antes decía 'usuario'. Ahora coincide con PersonaBase.
    password: str

# --- RESPUESTA DE LOGIN ---
class LoginResponse(BaseModel):
    estado: str   
    mensaje: str
    rol: Optional[str] = None

# --- BASE PARA USUARIOS ---
class PersonaBase(BaseModel):
    nombre_usuario: str 
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    fecha_nacimiento: datetime.date

class AlumnoCreate(PersonaBase):
    password: str

class AlumnoResponse(PersonaBase):
    id: int  
    rol: str
    class Config:
        from_attributes = True

class ProfesorCreate(PersonaBase):
    password: str

class ProfesorResponse(PersonaBase):
    id: int  
    rol: str
    class Config:
        from_attributes = True

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

class InscripcionCreate(BaseModel):
    alumno_id: int
    curso_id: int

class InscripcionResponse(InscripcionCreate):
    id: int
    calificacion: Optional[int] = None  
    class Config:
        from_attributes = True

class CalificacionUpdate(BaseModel):
    nota: int