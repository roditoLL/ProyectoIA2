# Instalacion del entorno
Primero deben crearse un entorno para hacer correr en pyton 
```bash
python -m venv entorno-virtual-del-proyecto
source entorno-virtual-del-proyecto/bin/activate     # Linux/macOS
entorno-virtual-del-proyecto\Scripts\activate        # Windows

pip install -r requirements.txt
```
esto ejecutenlo desde una terminal de gitbash en su windows, si estan con linux no pasa nada

# Para el frontend
Para el frontend solamente ejecuten este comando
```bash
 npm run install
```
el frontend deben abrirlo en otra pestana de su terminal

# Para la base de datos
Se instalan docker de su pagina ofical, pero antes se deben instalar WSL2 para que corra bien docker,despues deben
instalar una imagen y apartir de esa imagen crear un contenedor de mysql [video de docker mysql](https://www.youtube.com/watch?v=gRylJCfjkrQ&t=461s), [instalacion docker en windows](https://www.youtube.com/watch?v=ZO4KWQfUBBc), despues pueden utilizar el cliente de su preferencia para crear las tablas y insertar las columnas.
