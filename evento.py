from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Lista que almacena todos los eventos
listaeventos = []

# Clase para manejar los datos de un evento
class Evento(BaseModel):
    id: int
    titulo: str
    descripcion: str
    fecha: datetime
    notas: Optional[str] = None  # Notas opcionales como un campo de cadena
    fue_realizado: bool = False

# Ruta para obtener todos los eventos
@app.get("/eventos", response_model=List[Evento])
def get_eventos() -> List[Evento]:
    return listaeventos

# Ruta para obtener todos los eventos que ya se realizaron
@app.get("/eventos/realizados", response_model=List[Evento])
def get_eventos_realizados() -> List[Evento]:
    eventos_realizados = [evento for evento in listaeventos if evento.fue_realizado]
    return eventos_realizados

# Ruta para obtener todos los eventos que no se realizaron
@app.get("/eventos/no-realizados", response_model=List[Evento])
def get_eventos_no_realizados() -> List[Evento]:
    eventos_no_realizados = [evento for evento in listaeventos if not evento.fue_realizado]
    return eventos_no_realizados

# Ruta para crear un nuevo evento
@app.post("/eventos/", response_model=Evento)
def crear_evento(evento: Evento):
    if any(e.id == evento.id for e in listaeventos):
        raise HTTPException(status_code=400, detail="Evento con este ID ya existe")
    listaeventos.append(evento)
    return evento

# Ruta para obtener un evento por su ID
@app.get("/eventos/{id}", response_model=Evento)
def get_evento(id: int):
    evento = next((e for e in listaeventos if e.id == id), None)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return evento

# Ruta para actualizar un evento existente
@app.put("/eventos/{id}", response_model=Evento)
def update_evento(id: int, evento: Evento):
    index = next((i for i, e in enumerate(listaeventos) if e.id == id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    listaeventos[index] = evento
    return evento

# Ruta para agregar notas a un evento existente
@app.post("/eventos/{id}/notas", response_model=Evento)
def agregar_notas(id: int, notas: str):
    index = next((i for i, e in enumerate(listaeventos) if e.id == id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    listaeventos[index].notas = notas
    return listaeventos[index]

# Ruta para eliminar un evento por su ID
@app.delete("/eventos/{id}")
def delete_evento(id: int):
    index = next((i for i, e in enumerate(listaeventos) if e.id == id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    del listaeventos[index]
    return {"mensaje": "Evento eliminado exitosamente."}

# Ruta para eliminar un evento si NO se ha realizado
@app.delete("/eventos/no-realizado/{id}")
def delete_evento_no_realizado(id: int):
    index = next((i for i, e in enumerate(listaeventos) if e.id == id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    evento = listaeventos[index]
    if evento.fue_realizado:
        raise HTTPException(status_code=400, detail="No se puede eliminar un evento que ya se ha realizado")
    del listaeventos[index]
    return {"mensaje": "Evento eliminado exitosamente."}
