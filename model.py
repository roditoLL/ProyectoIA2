import torch
from torch import nn
from torch_geometric.nn import TransformerConv
from torch_geometric.data import Data
import torch.nn.functional as F
import torch.optim as optim
import pandas as pd
import numpy as np

#definimos una red neuronal basada en grafos.
#utilizamos Pytorch Geometric, una librería diseñada para trabajar con datos estructurados como grafos.
class GraphTransformerModel(torch.nn.Module):
    def __init__(self, in_channels, out_channels):
        '''
        in_channels: Número de características de entrada por nodo (por ejemplo, semestre, área, carrera codificados).
        out_channels: Número de características de salida que queremos producir (tamaño del embedding).
        super().__init__() llama al constructor de la clase base (nn.Module), necesario para que PyTorch maneje bien los parámetros del modelo.
        '''
        super().__init__()
        '''
        Primera capa de atención sobre grafos.
        TransformerConv aplica una atención parecida a la de Transformers tradicionales, pero adaptada a grafos.
        heads=2: Usa 2 "cabezas de atención" que aprenden diferentes patrones de conectividad.'''
        self.conv1 = TransformerConv(in_channels, out_channels, heads=2)
        #segunda capa de atencion
        self.conv2 = TransformerConv(out_channels * 2, out_channels)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        '''
        Aplica la primera capa de atención y luego ReLU (función de activación no lineal).
        la salida son  vectores de tamaño out_channels * heads para cada nodo.
        '''
        x = self.conv1(x, edge_index).relu()
        # a qui se aplica la segunda capa de atencion
        x = self.conv2(x, edge_index)
        #devolvemos el embeding de cada nodo
        return x

def entrenar_modelo(data, epochs=100, lr=0.01):
    modelo = GraphTransformerModel(data.num_node_features, 16)
    optimizer = optim.Adam(modelo.parameters(), lr=lr)

    modelo.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        out = modelo(data)
        # Entrenamiento sin etiquetas, solo para dispersar embeddings
        loss = F.mse_loss(out, out.detach())
        loss.backward()
        optimizer.step()

    modelo.eval()
    return modelo

'''
 asignaturas DataFrame con info de las materias (nombre, semestre, área, carrera, etc).
 relaciones:DataFrame con pares de IDs que indican qué asignaturas están relacionadas (aristas del grafo).
'''
def generar_embeddings(asignaturas, conexiones):
    # Convertir columnas categóricas a variables dummy
    area_dummies = pd.get_dummies(asignaturas['area'])
    carrera_dummies = pd.get_dummies(asignaturas['carrera'])

    # Asegurarse de que el nivel sea numérico o codificarlo
    try:
        nivel = asignaturas['nivel'].astype(float)
    except:
        # si contiene letras, las codificamos
        nivel_map = {val: idx for idx, val in enumerate(sorted(asignaturas['nivel'].unique()))}
        nivel = asignaturas['nivel'].map(nivel_map)

    # Concatenamos todos los features
    features = pd.concat([
        nivel.rename("nivel"),
        area_dummies,
        carrera_dummies
    ], axis=1)

    # Depuración: verificar que todo sea numérico
    print(features.dtypes)

    # Convertir a tensor
    x = torch.tensor(features.values.astype(np.float32), dtype=torch.float)

    # Crear aristas (edge_index)
    edge_index = torch.tensor(conexiones.values.T - 1, dtype=torch.long)

    # Devolver grafo PyG
    data = Data(x=x, edge_index=edge_index)
    return data, list(asignaturas['nombre']), list(asignaturas['carrera']), list(asignaturas['area'])
