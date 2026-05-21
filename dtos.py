from pydantic import BaseModel
import datetime
from typing import Optional

# ==========================================
# --- ESQUEMAS DE ACCESO Y RESPUESTAS SIMPLES ---
# ==========================================

class LoginRequest(BaseModel):
    nombre_usuario: str  
    password: str

class LoginResponse(BaseModel):
    estado: str   
    mensaje: str
    rol: Optional[str] = None
    usuario_id: Optional[int] = None  # <--- AÑADE ESTA LÍNEA


# NUEVA: Para respuestas estándar de éxito/error (Bajas, Eliminaciones, Notas)
class SimpleResponse(BaseModel):
    estado: str
    mensaje: str


# ==========================================
# --- MÓDULO USUARIOS (ALUMNOS Y PROFESORES) ---
# ==========================================

# Base con tipos de datos de lectura estándar
class PersonaBase(BaseModel):
    nombre_usuario: str 
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    fecha_nacimiento: datetime.date

# MEJORA: Recibe la fecha como String para que FastAPI no truene si Postman o Android mandan formatos con variaciones
class AlumnoCreate(BaseModel):
    nombre_usuario: str
    password: str
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    fecha_nacimiento: str  # Espera un String. Se parsea en el CRUD.

class AlumnoResponse(PersonaBase):
    id: int  
    rol: str
    class Config:
        from_attributes = True

# MEJORA: Igual que en alumnos, la entrada de fechas se flexibiliza a String para el transporte seguro
class ProfesorCreate(BaseModel):
    nombre_usuario: str
    password: str
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    fecha_nacimiento: str  # Espera un String. Se parsea en el CRUD.

class ProfesorResponse(PersonaBase):
    id: int  
    rol: str
    class Config:
        from_attributes = True

# NUEVA: Molde requerido para el nuevo endpoint global de búsqueda de usuarios
class UsuarioResponse(PersonaBase):
    id: int
    rol: str
    class Config:
        from_attributes = True


# ==========================================
# --- MÓDULO CURSOS E INSCRIPCIONES ---
# ==========================================

class CursoBase(BaseModel):
    nombre_del_curso: str
    id_del_profesor: int
    descripcion: str
    fecha_de_inicio: datetime.date 
    fecha_de_fin: datetime.date

# MEJORA: Permite que el profesor envíe las fechas del nuevo curso como String para su procesamiento
class CursoCreate(BaseModel):
    nombre_del_curso: str
    id_del_profesor: int
    descripcion: str
    fecha_de_inicio: str  # "YYYY-MM-DD"
    fecha_de_fin: str     # "YYYY-MM-DD"

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