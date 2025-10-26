from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import requests
import os
from web_app.wrapper import QdrantClientWrapper

app = FastAPI()

REDIS_HOST = "redis-master"
REDIS_PORT = 6379
QDRANT_HOST = "qdrant"
QDRANT_PORT = 6333

try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
except Exception as e:
    redis_client = None
    print(f"Redis init error: {e}")

try:
    qdrant = QdrantClientWrapper(host=QDRANT_HOST, port=QDRANT_PORT)
except Exception as e:
    qdrant = None
    print(f"Qdrant init error: {e}")


class Item(BaseModel):
    id: str
    text: str
    vector: list[float]

@app.get("/health")
def health():
    #проверка Redis
    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        redis_client.ping()
        redis_ok = True
    except Exception:
        redis_ok = False

    #проверка Qdrant
    try:
        qdrant = QdrantClientWrapper(host=QDRANT_HOST, port=QDRANT_PORT)
        qdrant.get_collections()
        qdrant_ok = True
    except Exception:
        qdrant_ok = False

    status = {"redis": redis_ok, "qdrant": qdrant_ok}

    if all(status.values()):
        return {"status": "ok", **status}
    raise HTTPException(status_code=500, detail=status)

@app.post("/items")
def create_item(item: Item):
    redis_client.set(item.id, item.text)
    qdrant.upsert_point(item.id, item.vector, payload={"text": item.text})
    return {"id": item.id}

@app.get("/search")
def search(q: str):
    return qdrant.search_by_vector([0.1, 0.2])