import pandas as pd
from typing import Annotated, List
from fastapi import FastAPI, Depends, Query
from sqlmodel import Field, Session, create_engine, select, SQLModel
from fastapi.middleware.cors import CORSMiddleware
from sklearn.metrics.pairwise import cosine_similarity

from model import generar_embeddings, entrenar_modelo

# Conexión con MySQL
url_connection = 'mysql+pymysql://root:mipassword@localhost:3306/universidad'
engine = create_engine(url_connection)


# Modelos
class asignatura(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    codigo: int
    carrera: str
    area: str
    nivel: str
    tipo: str
    electiva: bool
    modalidad: str
    es_compartida: bool
    departamento: str


class conexiones(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_origen: int = Field(foreign_key="asignatura.id")
    id_destino: int = Field(foreign_key="asignatura.id")
    Relacion: str


# Crear base y tablas
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Dependencia de sesión
def get_session():
    with Session(engine) as session:
        yield session

session_dep = Annotated[Session, Depends(get_session)]

# FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Obtener datos en DataFrames
def obtener_datos():
    asignaturas = pd.read_sql("SELECT * FROM asignatura", con=engine)
    conexiones_df = pd.read_sql("SELECT id_origen, id_destino FROM conexiones", con=engine)
    return asignaturas, conexiones_df


@app.get("/")
def root():
    return {"Hello": "World"}



@app.get("/similares")
def calcular_similitud(nombre: str = Query(...)):
    asignaturas, conexiones_df = obtener_datos()
    data, nombres, carreras, areas = generar_embeddings(asignaturas, conexiones_df)
    modelo = entrenar_modelo(data)
    out = modelo(data).detach().numpy()
    sim_matrix = cosine_similarity(out)

    try:
        index_nombre = nombres.index(nombre.strip().upper())
    except ValueError:
        return {"nodes": [], "links": []}

    nodes = set()
    links = []

    for j in range(len(out)):
        if j == index_nombre:
            continue

        # ✅ ÚNICA condición: similitud alta
        if sim_matrix[index_nombre][j] > 0.98:  # puedes ajustar este valor
            source = nombres[index_nombre]
            target = nombres[j]

            # Agregar nodos sin forzar por área ni carrera
            nodes.add((source, carreras[index_nombre], areas[index_nombre]))
            nodes.add((target, carreras[j], areas[j]))

            links.append({
                "source": source,
                "target": target,
                "similitud": round(float(sim_matrix[index_nombre][j]), 2)
            })

    nodes_dict = [{"id": n[0], "carrera": n[1], "area": n[2]} for n in nodes]

    return {"nodes": nodes_dict, "links": links}





@app.get("/asignaturas/", response_model=list[asignatura])
def read_asignaturas(session: session_dep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    return session.exec(select(asignatura).offset(offset).limit(limit)).all()


@app.post("/asignaturas/", response_model=asignatura)
def create_asignatura(asignatura: asignatura, session: session_dep):
    session.add(asignatura)
    session.commit()
    session.refresh(asignatura)
    return asignatura


@app.get("/carreras/", response_model=List[str])
def list_carreras(session: Session = Depends(get_session)):
    stmt = select(asignatura.carrera).distinct().order_by(asignatura.carrera)
    return session.exec(stmt).all()


@app.get("/areas/", response_model=List[str])
def list_areas(session: Session = Depends(get_session)):
    stmt = select(asignatura.area).distinct().order_by(asignatura.area)
    return session.exec(stmt).all()


@app.get("/conexiones/", response_model=List[conexiones])
def get_conexiones(session: Session = Depends(get_session)):
    return session.exec(select(conexiones)).all()


#desde aca volverr 
