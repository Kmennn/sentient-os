from fastapi import APIRouter
from fastapi.responses import JSONResponse
import psutil
import platform
import base64
import io
import logging

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    from PIL import Image
except ImportError:
    Image = None

router = APIRouter()
logger = logging.getLogger("BodyEndpoint")

@router.get("/stream")
async def get_telemetry():
    """Real-time body telemetry (CPU/RAM)."""
    return {
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent
    }

@router.get("/status")
async def get_status():
    """Static body metadata."""
    return {
        "os_type": platform.system(),
        "process_count": len(psutil.pids()),
        "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else 100
    }

@router.get("/screenshot")
async def get_screenshot():
    """Capture screen content."""
    if not pyautogui:
        return JSONResponse(status_code=500, content={"error": "pyautogui not installed"})
    
    try:
        # Capture raw
        screenshot = pyautogui.screenshot()
        
        # Convert to Base64
        buffered = io.BytesIO()
        screenshot.save(buffered, format="JPEG", quality=50)
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        return {"image": img_str}
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/vision/screenshot")
async def get_vision_screenshot_alias():
    """Alias for vision engine compatibility"""
    return await get_screenshot()
