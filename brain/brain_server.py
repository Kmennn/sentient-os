from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import psutil
from pydantic import BaseModel
import logging

from core.config import config
from core.llm_service import llm_service
from core.local_model_engine import local_engine

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("brain_server")

app = FastAPI(title="Sentient OS - Brain (Offline Mode)")

# Allow frontend (Flutter app) to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.routes import router as api_router
app.include_router(api_router)

class ChatMessage(BaseModel):
    message: str

@app.on_event("startup")
async def startup_event():
    logger.info("AI engine: LOCAL MODE ACTIVE")
    logger.info(f"LLM: Ollama ({config.LOCAL_LLM_MODEL}) at {config.OLLAMA_URL}")
    logger.info("Embeddings: sentence-transformers (local)")

@app.get("/ping")
async def ping():
    return {"ok": True, "msg": "Brain (Offline) here ✅"}

@app.get("/reply")
async def reply(text: str = Query(..., description="user text")):
    text = text.strip()
    if not text:
        return {"reply": "(empty)"}

    try:
        response = await llm_service.generate_response(text)
        return {"reply": response}
    except Exception as e:
        return {"reply": f"(error using local model) {e}"}

@app.post("/chat")
async def chat(msg: ChatMessage):
    return await reply(text=msg.message)

@app.get("/v1/memory/search")
async def memory_search(q: str = Query(..., min_length=1), k: int = 5):
    """
    Semantic search over long-term memory (vector store).
    """
    from core.vector_store import vector_store
    results = vector_store.search(q, k)
    return {"results": results}

@app.get("/local-intelligence")
async def local_intelligence():
    """
    Report available model sizes and memory usage.
    """
    mem = psutil.virtual_memory()
    return {
        "status": "active",
        "mode": "local",
        "llm_model": config.LOCAL_LLM_MODEL,
        "ollama_url": config.OLLAMA_URL,
        "embedding_model": "all-MiniLM-L6-v2",
        "memory_usage": {
            "total": mem.total,
            "available": mem.available,
            "percent": mem.percent
        }
    }

@app.get("/v1/models")
async def list_models():
    """
    List downloaded Ollama models.
    """
    import subprocess
    import shutil
    
    ollama_path = shutil.which("ollama")
    if not ollama_path:
        return {"error": "Ollama CLI not found in PATH."}

    try:
        # Run 'ollama list'
        result = subprocess.run([ollama_path, "list"], capture_output=True, text=True)
        if result.returncode != 0:
            return {"error": f"Ollama error: {result.stderr}"}
            
        # Parse output (simple)
        # HEADER: NAME ID SIZE MODIFIED
        lines = result.stdout.strip().split('\n')
        models = []
        if len(lines) > 1:
            for line in lines[1:]: # Skip header
                parts = line.split()
                if len(parts) >= 1:
                    models.append({
                        "name": parts[0],
                        "id": parts[1] if len(parts)>1 else "",
                        "size": parts[2] if len(parts)>2 else "",
                        "modified": " ".join(parts[3:]) if len(parts)>3 else ""
                    })
        return {"models": models}
    except Exception as e:
        return {"error": str(e)}

class ModelRequest(BaseModel):
    model: str

@app.post("/v1/models/pull")
async def pull_model(req: ModelRequest):
    """
    Trigger a model pull.
    """
    import subprocess
    import shutil
    
    ollama_path = shutil.which("ollama")
    if not ollama_path:
        return {"error": "Ollama not found"}

    # We won't await this, just fire and forget (logging to console)
    subprocess.Popen([ollama_path, "pull", req.model])
    
    return {"status": "pulling", "msg": f"Started pulling {req.model}. Check brain console logs."}

@app.post("/v1/models/unload")
async def unload_model(req: ModelRequest):
    """
    Unload a model from memory via keep_alive=0.
    """
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            # Send a request to unload (keep_alive 0)
            await client.post(
                f"{config.OLLAMA_URL}/api/generate",
                json={"model": req.model, "prompt": "", "keep_alive": 0}
            )
        return {"status": "unloaded", "msg": f"Requested unload for {req.model}"}
    except Exception as e:
        return {"error": str(e)}
