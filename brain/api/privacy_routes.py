
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict
from core.policy.action_policy import action_policy
from core.db import get_connection
import logging

router = APIRouter(prefix="/privacy", tags=["privacy"])
logger = logging.getLogger("privacy_api")

class ConsentUpdate(BaseModel):
    actions: Optional[bool] = None
    memory: Optional[bool] = None
    vision: Optional[bool] = None

@router.post("/user/{user_id}/consent")
async def update_consent(user_id: str, consent: ConsentUpdate):
    try:
        # Pydantic model dump excluding None
        updates = {k: v for k, v in consent.dict().items() if v is not None}
        action_policy.update_consent(user_id, updates)
        return {"status": "success", "consent": action_policy._get_consent(user_id)}
    except Exception as e:
        logger.error(f"Failed consent update: {e}")
        raise HTTPException(status_code=500, detail="Database Error")

@router.get("/user/{user_id}/consent")
async def get_consent(user_id: str):
    return action_policy._get_consent(user_id)

@router.get("/admin/export")
async def export_data(user_id: str = Query(...)):
    """
    Export all data for user.
    """
    try:
        data = {}
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. Conversations
        cursor.execute("SELECT * FROM conversations WHERE user_id = ?", (user_id,))
        data['conversations'] = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]
        
        # 2. Vision Events
        if "vision_events" in _get_tables(cursor):
             cursor.execute("SELECT * FROM vision_events WHERE user_id = ?", (user_id,))
             data['vision'] = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]
             
        # Audit Logs
        cursor.execute("SELECT * FROM audit_logs WHERE user_id = ?", (user_id,))
        data['audit_logs'] = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]
        
        conn.close()
        return data
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/purge")
async def purge_data(user_id: str = Query(...), confirm: bool = Query(False)):
    if not confirm:
        raise HTTPException(status_code=400, detail="Must set confirm=True")
        
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Delete PII
        cursor.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM vision_events WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM action_records WHERE user_id = ?", (user_id,))
        
        # Nullify user in audit logs (keep record but anon)
        cursor.execute("UPDATE audit_logs SET user_id = 'ANON' WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        return {"status": "purged", "user_id": user_id}
    except Exception as e:
        logger.error(f"Purge failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _get_tables(cursor) -> list:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return [r[0] for r in cursor.fetchall()]
