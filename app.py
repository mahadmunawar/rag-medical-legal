from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware # Add this

from embeddings import get_embedding
from qdrant_db import search_qdrant

app = FastAPI()

# Add this block to fix the "Failed to fetch" error
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str

@app.post("/rag")
def rag(request: Query):
    try:
        vector = get_embedding(request.query)
        results = search_qdrant(vector)

        return {
            "query": request.query,
            "result": results
        }
    except Exception as e:
        return {"error": str(e)}