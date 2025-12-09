
from fastapi import APIRouter
from core.config import config

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/version")
async def get_version():
    return {
        "version": getattr(config, "VERSION", "1.0.0"),
        "api": "v1.10",
        "status": "online"
    }

@router.get("/health")
async def health_check():
    return {"status": "ok", "version": getattr(config, "VERSION", "1.0.0")}

@router.get("/metrics")
async def get_metrics():
    from core.agents.supervisor import supervisor
    # Expose Prometheus format
    return supervisor.get_metrics()
