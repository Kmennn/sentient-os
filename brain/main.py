from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from api.ws_handlers import router as ws_router
from core.config import config

app = FastAPI(title="Sentient OS Brain", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "ok"}

# Allow frontend to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/v1")
app.include_router(ws_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=True)
