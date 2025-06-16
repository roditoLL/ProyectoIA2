from main import asignatura, conexiones, engine  # ✅ acceso directo ahora
from model import entrenar_modelo  # solo si decides moverlo allí


import torch
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import TransformerConv
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from sqlmodel import Session, select

# Función para convertir textos categóricos a vectores numéricos
def encode_column(values):
    unique = list(set(values))
    mapping = {val: idx for idx, val in enumerate(unique)}
    return [mapping[val] for val in values], mapping

# Cargar asignaturas desde la base de datos
def cargar_datos():
    with Session(engine) as session:
        asignaturas = session.exec(select(asignatura)).all()
        df = pd.DataFrame([a.dict() for a in asignaturas])
    return df

# Construcción del grafo a partir de los datos codificados
def construir_grafo(df):
    carrera, _ = encode_column(df['carrera'])
    area, _ = encode_column(df['area'])
    modalidad, _ = encode_column(df['modalidad'])
    tipo, _ = encode_column(df['tipo'])
    departamento, _ = encode_column(df['departamento'])

    try:
        nivel = df['nivel'].astype(int)
    except:
        nivel, _ = encode_column(df['nivel'])

    electiva = df['electiva'].astype(int)
    compartida = df['es_compartida'].astype(int)

    atributos = np.stack([
        carrera,
        area,
        modalidad,
        tipo,
        departamento,
        nivel,
        electiva,
        compartida
    ], axis=1)

    x = torch.tensor(atributos, dtype=torch.float)
    edge_index = torch.empty((2, 0), dtype=torch.long)

    return Data(x=x, edge_index=edge_index), df

# Modelo Transformer basado en TransformerConv
class TransformerGNN(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels, heads=4):
        super().__init__()
        self.conv1 = TransformerConv(in_channels, hidden_channels, heads=heads)
        self.conv2 = TransformerConv(hidden_channels * heads, out_channels, heads=1)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = torch.relu(x)
        x = self.conv2(x, edge_index)
        return x

# Entrenamiento del modelo
def entrenar_modelo(data, epochs=200):
    model = TransformerGNN(
        in_channels=data.num_node_features,
        hidden_channels=64,
        out_channels=32,
        heads=4
    )

    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    model.train()

    for epoch in range(epochs):
        optimizer.zero_grad()
        out = model(data.x, data.edge_index)
        loss = F.mse_loss(out, out)
        loss.backward()
        optimizer.step()

    model.eval()
    return model(data.x, data.edge_index).detach().numpy()

# Calcular similitud coseno y guardar en la base
def guardar_similitudes(df, embeddings, umbral=0.99):
    
    sim_matrix = cosine_similarity(embeddings)
    relaciones = []

    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            sim = sim_matrix[i, j]
            if sim >= umbral:
                relaciones.append({
                    "id_origen": int(df.iloc[i]["id"]),
                    "id_destino": int(df.iloc[j]["id"]),
                    "Relacion": "similar"
                })

    print(f"Total de relaciones encontradas: {len(relaciones)}")

    with Session(engine) as session:
        for r in relaciones:
            nueva = conexiones(**r)
            session.add(nueva)
        session.commit()

# Ejecutar todo el pipeline
def main():
    df = cargar_datos()
    print(f"Asignaturas cargadas: {len(df)}")
    data, df = construir_grafo(df)
    embeddings = entrenar_modelo(data)
    guardar_similitudes(df, embeddings)

if __name__ == "__main__":
    main()
