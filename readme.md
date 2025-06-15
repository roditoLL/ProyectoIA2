# Instalacion del entorno
Primero deben crearse un entorno para hacer correr en pyton, la version es 3.10
```bash
python -m venv entorno-virtual-del-proyecto
source entorno-virtual-del-proyecto/Scripts/activate     # Linux/macOS

entorno-virtual-del-proyecto\Scripts\activate        # Windows

```
esto ejecutenlo desde una terminal de gitbash en su windows, si estan con linux no pasa nada.El arqchivo requeriments.txt tuvo muchos errores asi que mejor haganlo con estos pasos.
Luego deben instalarse estas dependecias con el entorno activado
```bash
pip install torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cpu
pip install torch-scatter torch-sparse torch-cluster torch-spline-conv torch-geometric -f https://data.pyg.org/whl/torch-2.2.0+cpu.html
pip install "fastapi[standard]"
pip install sqlmodel sqlalchemy
pip install scikit-learn
pip install pandas 
## si ya instalaron numpy en la version 2.0 o mayor por fa desistalenlo con este comando
pip pip uninstall numpy
## usar este otro comando
pip install "numpy<2"
pip install pymysql
```
Esto haganlo en una terminal linux como el de git bash ubicados en el proyecto.
Para desactivar el entorno solo usar el comando:
```bash
deactivate
```

# Para el frontend
Para el frontend solamente ejecuten este comando
```bash
 npm run install
```
el frontend deben abrirlo en otra pestana de su terminal

# Para la base de datos
Se instalan docker de su pagina ofical, pero antes se deben instalar WSL2 para que corra bien docker,despues deben
instalar una imagen y apartir de esa imagen crear un contenedor de mysql [video de docker mysql](https://www.youtube.com/watch?v=gRylJCfjkrQ&t=461s), [instalacion docker en windows](https://www.youtube.com/watch?v=ZO4KWQfUBBc), despues pueden utilizar el cliente de su preferencia para crear las tablas y insertar las columnas.
