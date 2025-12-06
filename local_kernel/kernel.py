from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import platform
import psutil
import time

app = FastAPI(title="Sentient Local Kernel", version="0.1.0")

# Allow Flutter frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/status")
def system_status():
    """Simulates reading local hardware stats (RTOS duties)"""
    return {
        "system": platform.system(),
        "os_type": psutil.os.name,
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "kernel_mode": "Active (Simulated)",
        "process_count": len(psutil.pids())
    }

@app.get("/stream")
def stream_telemetry():
    """Lightweight telemetry endpoint for high-frequency polling"""
    return {
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "ts": time.time()
    }

@app.post("/simulate/wake")
def simulate_wake_word():
    """Endpoint to trigger a 'wake word' event manually for testing"""
    return {"event": "wake_word_detected", "confidence": 0.99}

if __name__ == "__main__":
    # Running on port 8001 to distinguish from Brain (8000)
    uvicorn.run(app, host="0.0.0.0", port=8001)
