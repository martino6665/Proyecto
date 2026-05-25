from pydantic import BaseModel
import datetime
from typing import Optional, List

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
    usuario_id: Optional[int] = None


# Para respuestas estándar de éxito/error (Bajas, Eliminaciones, Notas)
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

# Recibe la fecha como String para que FastAPI no truene si Postman o Android mandan formatos con variaciones
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

# La entrada de fechas se flexibiliza a String para el transporte seguro
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

# Molde requerido para el nuevo endpoint global de búsqueda de usuarios
class UsuarioResponse(PersonaBase):
    id: int
    rol: str
    class Config:
        from_attributes = True


# ==========================================
# --- MÓDULO CURSES E INSCRIPCIONES ---
# ==========================================

class CursoBase(BaseModel):
    nombre_del_curso: str
    id_del_profesor: int
    descripcion: str
    fecha_de_inicio: datetime.date 
    fecha_de_fin: datetime.date
    color_banner: Optional[str] = "#3F51B5" # SINCRONIZADO: Soporte nativo para la UI

# Permite que el profesor envíe las fechas del nuevo curso como String para su procesamiento
class CursoCreate(BaseModel):
    nombre_del_curso: str
    id_del_profesor: int
    descripcion: str
    fecha_de_inicio: str  # "YYYY-MM-DD"
    fecha_de_fin: str     # "YYYY-MM-DD"
    color_banner: Optional[str] = "#3F51B5" # SINCRONIZADO: Recibe el hex desde Android

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


# ==========================================
# --- NUEVO MÓDULO: ACTIVIDADES (PROFESOR) ---
# ==========================================

class ActividadCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    puntos_maximos: float = 100.0
    # Aseguramos que los campos sean opcionales y de tipo String para recibir "YYYY-MM-DD"
    fecha_inicio: Optional[str] = None 
    fecha_limite: Optional[str] = None

class ActividadResponse(BaseModel):
    id: int
    curso_id: int
    titulo: str
    descripcion: Optional[str]
    puntos_maximos: float
    # Cambiamos a Optional[datetime.date] para que Pydantic maneje la serialización
    fecha_inicio: Optional[datetime.date] = None
    fecha_limite: Optional[datetime.date] = None

    class Config:
        from_attributes = True

# ==========================================
# --- NUEVO MÓDULO: ENTREGAS (ALUMNO) ---
# ==========================================

class EntregaCreate(BaseModel):
    contenido_entrega: str  # Texto de la respuesta o URL que manda el alumno

class EntregaResponse(BaseModel):
    id: int
    actividad_id: int
    alumno_id: int
    contenido_entrega: str
    fecha_entrega: datetime.datetime
    nota_obtenida: Optional[float] = None       # Nulo hasta que el profesor califique
    comentario_profesor: Optional[str] = None   # Nulo hasta que el profesor califique

    class Config:
        from_attributes = True


# ==========================================
# --- NUEVO MÓDULO: CALIFICAR (PROFESOR) ---
# ==========================================

class CalificarEntregaRequest(BaseModel):
    nota_obtenida: float
    comentario_profesor: Optional[str] = None