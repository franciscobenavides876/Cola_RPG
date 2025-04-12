from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError

# Configuración de la base de datos con SQLAlchemy
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos de base de datos
class Personaje(Base):
    __tablename__ = "personajes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    nivel = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    genero = Column(String)
    color_piel = Column(String)

class Mision(Base):
    __tablename__ = "misiones"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    descripcion = Column(String)
    completada = Column(Boolean, default=False)

# Crear la base de datos si no existe
Base.metadata.create_all(bind=engine)

# Aplicación FastAPI
app = FastAPI()

# Pydantic Models
class PersonajeCreate(BaseModel):
    nombre: str
    nivel: int = 1
    xp: int = 0
    genero: str
    color_piel: str

class PersonajeOut(BaseModel):
    nombre: str
    nivel: int
    xp: int
    genero: str
    color_piel: str

    class Config:
        orm_mode = True

class MisionCreate(BaseModel):
    nombre: str
    descripcion: str
    completada: bool = False

class MisionOut(BaseModel):
    nombre: str
    descripcion: str
    completada: bool

    class Config:
        orm_mode = True

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Insertar misiones por defecto
def insertar_misiones_default(db: Session):
    misiones_default = [
        ("Recoger hierbas", "Ve a la zona norte y recoge hierbas medicinales."),
        ("Cazar monstruos", "Caza 5 monstruos en la zona sur."),
        ("Explorar el castillo", "Explora el castillo abandonado y regresa con un informe."),
        ("Entrenar con el maestro", "Entrena con el maestro en el dojo."),
        ("Reparar el puente", "Recolecta madera y piedra para reparar el puente."),
        ("Buscar tesoros", "Encuentra el cofre oculto en las ruinas del bosque."),
        ("Vencer al dragón", "Derrota al dragón que vive en la montaña."),
        ("Ayudar al aldeano", "Ayuda al aldeano a recuperar su ganado."),
        ("Recolectar agua", "Ve al río y trae agua para el pueblo."),
        ("Salvar a la princesa", "Rescata a la princesa secuestrada por bandidos."),
        ("Rastrear a los bandidos", "Rastrear y capturar a los bandidos que atacaron el pueblo."),
        ("Destruir el altar oscuro", "Destruye el altar que invoca a los demonios."),
        ("Encuentros con el mercader", "Habla con el mercader y compra pociones."),
        ("Despertar el poder ancestral", "Encuentra el templo perdido y despierta el poder ancestral."),
        ("Destruir la horda de orcos", "Elimina a la horda de orcos que amenaza el bosque."),
        ("Reparar la granja", "Ayuda a reparar la granja dañada por el viento."),
        ("Luchar en el torneo", "Participa en el torneo de luchadores del reino."),
        ("Defender la aldea", "Defiende la aldea de los ataques de las bestias nocturnas."),
        ("Recuperar el libro perdido", "Recupera el libro perdido en la biblioteca del reino."),
        ("Construir una casa", "Ayuda a los aldeanos a construir una nueva casa para ellos."),
    ]

    for nombre, descripcion in misiones_default:
        mision = Mision(nombre=nombre, descripcion=descripcion)
        try:
            db.add(mision)
            db.commit()
        except IntegrityError:
            db.rollback()

# Ejecutar al iniciar FastAPI
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    insertar_misiones_default(db)
    db.close()

# Rutas de la API

@app.post("/personajes", response_model=PersonajeOut)
async def crear_personaje(personaje: PersonajeCreate, db: Session = Depends(get_db)):
    db_personaje = Personaje(**personaje.dict())
    db.add(db_personaje)
    db.commit()
    db.refresh(db_personaje)
    return db_personaje

@app.get("/personajes", response_model=List[PersonajeOut])
async def obtener_personajes(db: Session = Depends(get_db)):
    return db.query(Personaje).all()

@app.get("/personajes/{nombre}", response_model=PersonajeOut)
async def obtener_personaje(nombre: str, db: Session = Depends(get_db)):
    personaje = db.query(Personaje).filter(Personaje.nombre == nombre).first()
    if personaje is None:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return personaje

@app.post("/personajes/{nombre}/completar_mision")
async def completar_mision(nombre: str, db: Session = Depends(get_db)):
    db_personaje = db.query(Personaje).filter(Personaje.nombre == nombre).first()
    if db_personaje:
        db_personaje.xp += 10
        db_personaje.nivel = (db_personaje.xp // 100) + 1
        db.commit()
        db.refresh(db_personaje)
        return db_personaje
    raise HTTPException(status_code=404, detail="Personaje no encontrado")

@app.post("/misiones", response_model=MisionOut)
async def crear_mision(mision: MisionCreate, db: Session = Depends(get_db)):
    db_mision = Mision(**mision.dict())
    db.add(db_mision)
    db.commit()
    db.refresh(db_mision)
    return db_mision

@app.get("/misiones", response_model=List[MisionOut])
async def obtener_misiones(db: Session = Depends(get_db)):
    return db.query(Mision).all()

@app.post("/misiones/{mision_id}/completar")
async def completar_mision_por_id(mision_id: int, db: Session = Depends(get_db)):
    db_mision = db.query(Mision).filter(Mision.id == mision_id).first()
    if db_mision:
        db_mision.completada = True
        db.commit()
        db.refresh(db_mision)
        return db_mision
    raise HTTPException(status_code=404, detail="Misión no encontrada")
