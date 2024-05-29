from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

app = FastAPI()

# Lista que almacena todas las eventos
listaeventos = []

# Clase para manejar los datos de un profesor
class Evento(BaseModel):
    id: int
    titulo: str
    descripcion: str
    fecha: datetime
    notas: str
    nivel: str
    fue_realizado: Optional [bool] = None


# Ruta para obtener todas las eventos
@app.get("/eventos", response_model=List[Evento])
def get_eventos() -> List[Evento]:
    return listaeventos

# Ruta para obtener todas las eventos que ya se realizaron
@app.get("/eventos", response_model=List[Evento])
def get_eventos_realizados() -> List[Evento]:
    if Evento.fue_realizado:
        return listaeventos, f" Aquí los que se realizaron :) "
    

# Ruta para obtener todas las eventos que no se realizaron
@app.get("/eventos", response_model=List[Evento])
def get_eventos_realizados() -> List[Evento]:
    if Evento != Evento.fue_realizado:
        return listaeventos, f" Aquí los que no realizaron :) "
    

# Ruta para crear una nueva evento
@app.post("/eventos/", response_model=Evento)
def crear_evento(evento: Evento):
    if any(m.id == evento.id for m in listaeventos):
        raise HTTPException(status_code=400, detail="Evento con este ID ya existe")
    listaeventos.append(evento)
    return evento

# Ruta para obtener una evento por su ID
@app.get("/eventos/{id}", response_model=Evento)
def get_evento(id: int):
    evento = next((m for m in listaeventos if m.id == id), None)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return evento


# Ruta para crear una nota en el evento
@app.post("/eventos/", response_model=Evento)
def crear_evento(evento: Evento):
    if any(m.id == evento.id for m in listaeventos):
        raise HTTPException(status_code=400, detail="Evento con este ID ya existe")
    listaeventos.append(evento)
    return evento

# Ruta para actualizar una evento existente
@app.put("/eventos/{id}", response_model=Evento)
def update_eventos(id: int, evento: Evento):
    index = next((i for i, m in enumerate(listaeventos) if m.id == id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    listaeventos[index] = evento
    return evento

# Ruta para eliminar una evento por su ID
@app.delete("/eventos/{id}")
def delete_evento(id: int):
    index = next((i for i, m in enumerate(listaeventos) if m.id == id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Evento no encontrada")
    del listaeventos[index]
    return {"mensaje": "Evento eliminado exitosamente."}

# Ruta para eliminar una evento si NO se ha realizado
@app.delete("/eventos/{id}")
def delete_evento_no_realizado(id: int):
    index = next((i for i, m in enumerate(listaeventos) if m.id == id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Evento no encontrada")
    if Evento != Evento.fue_realizado: 
        del listaeventos[index]
        return {"mensaje": "Evento eliminadao exitosamente."}
