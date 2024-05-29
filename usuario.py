from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Lista que almacena todas las usuarios
listausuarios = []

# Clase para manejar los datos de un profesor
class Usuario(BaseModel):
    id: int
    nombre_usuario: str
    cooreo_electronico: str
    nombre: str
    apellido: str
  

# Ruta para obtener todas las usuarios
@app.get("/usuarios", response_model=List[Usuario])
def get_usuarios() -> List[Usuario]:
    return listausuarios

# Ruta para crear una nueva usuarios
@app.post("/usuarios/", response_model=Usuario)
def crear_usuarios(usuario: Usuario):
    if any(m.id == usuario.id for m in listausuarios):
        raise HTTPException(status_code=400, detail="Usuario con este ID ya existe")
    listausuarios.append(usuario)
    return usuario

# Ruta para obtener una usuario por su ID
@app.get("/usuarios/{id}", response_model=Usuario)
def get_usuario(id: int):
    usuario = next((m for m in listausuarios if m.id == id), None)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

# Ruta para actualizar una usuario existente
@app.put("/usuarios/{id}", response_model=Usuario)
def update_usuario(id: int, usuario: Usuario):
    index = next((i for i, m in enumerate(listausuarios) if m.id == id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrada")
    listausuarios[index] = usuario
    return usuario

# Ruta para eliminar una usuario por su ID
@app.delete("/usuarios/{id}")
def delete_usuario(id: int):
    index = next((i for i, m in enumerate(listausuarios) if m.id == id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrada")
    del listausuarios[index]
    return {"mensaje": "Usuario eliminado exitosamente."}

