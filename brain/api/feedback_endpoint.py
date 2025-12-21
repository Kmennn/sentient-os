from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from brain.feedback.feedback_model import FeedbackType
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType
import logging

router = APIRouter()
logger = logging.getLogger("Feedback")

class FeedbackRequest(BaseModel):
    type: str # positive, negative, neutral
    target_id: str
    comment: Optional[str] = None

@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    try:
        fb_type = FeedbackType(req.type)
        
        # Log to Ledger
        mission_scheduler._log_autonomy_decision(
            DecisionType.FEEDBACK_RECEIVED,
            reason=f"{req.type.upper()} on {req.target_id}",
            was_auto=False
        )
        
        logger.info(f"[FEEDBACK] Received {req.type} for {req.target_id}")
        
        return {"status": "OK", "message": "Feedback recorded."}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid feedback type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
