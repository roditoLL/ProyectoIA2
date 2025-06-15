import pandas as pd
from typing import  Annotated
from fastapi import FastAPI,Depends,Query
from sqlmodel import Field,Session,create_engine,select,SQLModel
from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from fastapi.middleware.cors import CORSMiddleware
from sklearn.metrics.pairwise import cosine_similarity
import numpy
from model import  generar_embeddings, entrenar_modelo


#Definimos el sqlmodel y la conexion con mysql
url_connection = 'mysql+pymysql://root:{usar_su_constrasena}@localhost:{usar_su_puerto_de_mysql}/universidad'
engine = create_engine(url_connection)

#funcion para crear las tablas y la base de datos si no exisitiera 
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

#funcion que solo nos permite tener una sesion activa,cada vez que cambie algo en la base de datos
def get_session():
    with Session(engine) as session:
        yield session

session_dep = Annotated[Session,Depends(get_session)]


#definimos los modelos
class Asignatura(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    area:str
    semestre:int
    carrera:str

class Relaciones(SQLModel, table=True):
    origen_id: int = Field(
        sa_column=Column(Integer, ForeignKey("asignatura.id", name="fk_relaciones_origen"))
    )
    destino_id: int = Field(
        sa_column=Column(Integer, ForeignKey("asignatura.id", name="fk_relaciones_destino"))
    )

    __table_args__ = (
        PrimaryKeyConstraint("origen_id", "destino_id", name="pk_relaciones"),
    )

#iniciamos el backend en este punto
app = FastAPI()
# se deben configurar los CORS para poder compartir informacion del backend hacia el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Aquí va tu frontend (React)
    allow_credentials=True,
    allow_methods=["*"],  # Puedes restringir si lo deseas: ["GET", "POST"]
    allow_headers=["*"],
)

#funcion que realizara directamente consultas a la base de datos y las guardara en dataframes
def obtener_datos():
    asignaturas = pd.read_sql("SELECT * FROM asignatura", con=engine)
    relaciones = pd.read_sql("SELECT origen_id, destino_id FROM relaciones", con=engine)
    return asignaturas, relaciones

#endpoint que nos devolvera la similitud de las asignaturas segun el area
@app.get("/similares")
def calcular_similitud():
    asignaturas, relaciones = obtener_datos()
    #converitmos los datos a grafo
    '''
    data: objeto Data de PyTorch Geometric con nodos y aristas.
    nombres, carreras, areas: listas paralelas para cada nodo (por índice).
    '''
    data, nombres, carreras,areas = generar_embeddings(asignaturas, relaciones)
    modelo = entrenar_modelo(data)  # Aquí entrenamos el modelo
    out = modelo(data).detach().numpy()
    #Calcular similitud,Esto genera una matriz de similitud coseno entre los embeddings, donde sim_matrix[i][j] indica cuán parecidos son los nodos i y j.
    sim_matrix = cosine_similarity(out)

    nodes = []
    links = []
    added_nodes = set()
    pares_ya_agregados = set()
    #para cada nodo , si no fue agregado lo anadimos con su id,carrera,area
    for i in range(len(out)):
        nombre_i = nombres[i]
        if nombre_i not in added_nodes:
            nodes.append({
                "id": nombre_i,
                "carrera": carreras[i],
                "area": areas[i]  # incluir área
            })
            added_nodes.add(nombre_i)
        
        #Solo enlazamos pares de materias si:Son de carreras diferentes,son del mismo área temática,tienen alta similitud (> 0.7).
        for j in range(i + 1, len(out)):
            if (
                carreras[i] != carreras[j]
                and areas[i] == areas[j]  # misma área
                and sim_matrix[i][j] > 0.7
            ):
                nombre_j = nombres[j]
                if nombre_j not in added_nodes:
                    nodes.append({
                        "id": nombre_j,
                        "carrera": carreras[j],
                        "area": areas[j]
                    })
                    added_nodes.add(nombre_j)

                par = tuple(sorted([nombre_i, nombre_j]))
                if par not in pares_ya_agregados:
                    #Se crea un link entre las dos materias con el área y la similitud.
                    links.append({
                        "source": nombre_i,
                        "target": nombre_j,
                        "similitud": round(float(sim_matrix[i][j]), 2),
                        "area": areas[i]  # también puedes incluir el área en el enlace
                    })
                    pares_ya_agregados.add(par)

    return {"nodes": nodes, "links": links}


@app.get("/")
def root():
    return {"Hello": "World"}

@app.on_event('startup')
def on_startup():
    create_db_and_tables()

@app.get("/asignaturas/",response_model=list[Asignatura])
def read_asignaturas(
    session:session_dep,
    offset:int = 0,
    limit:Annotated[int,Query(le=100)]=100,
):
    asignaturas = session.exec(select(Asignatura).offset(offset).limit(limit)).all()
    return asignaturas

@app.post("/asignaturas/", response_model=Asignatura)
def create_asignatura(asignatura: Asignatura, session: session_dep):
    db_asignatura = Asignatura.model_validate(asignatura)
    session.add(db_asignatura)
    session.commit()
    session.refresh(db_asignatura)
    return db_asignatura


