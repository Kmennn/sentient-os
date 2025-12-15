from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from api.ws_handlers import router as ws_router
from core.config import config
import asyncio
import threading
import time
import logging

logger = logging.getLogger("BrainStartup")

# Import v2.4 Subsystems
try:
    from brain.robotics.ros_bridge import ros_bridge
    from brain.autonomy.spatial_autonomy_engine import spatial_autonomy
    SUBSYSTEMS_AVAILABLE = True
except ImportError:
    SUBSYSTEMS_AVAILABLE = False
    logger.warning("v2.4 Subsystems not found (ImportError).")

def autonomy_loop():
    while True:
        try:
            if SUBSYSTEMS_AVAILABLE and spatial_autonomy.active:
                spatial_autonomy.tik_tok()
        except Exception as e:
            logger.error(f"Autonomy Loop Error: {e}")
        time.sleep(1.0)

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

@app.on_event("startup")
async def startup_event():
    logger.info("Brain Starting Up...")
    if SUBSYSTEMS_AVAILABLE:
        # Start ROS (Initialized on import, but good to log)
        logger.info(f"ROS Bridge Mock Mode: {ros_bridge.is_mock}")
        
        # Start Autonomy Loop
        spatial_autonomy.start_loop()
        t = threading.Thread(target=autonomy_loop, daemon=True)
        t.start()
        logger.info("Spatial Autonomy Loop Started (Background Thread)")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=True)
