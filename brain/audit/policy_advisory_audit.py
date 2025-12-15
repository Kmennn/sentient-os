
import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

class AdvisoryAudit:
    """
    Logs all advisory actions for accountability.
    """
    def __init__(self):
        self.logs: List[Dict] = []
        
    def log_event(self, action: str, advisory_id: str, details: Dict):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action, # SUBMIT, APPROVE, REJECT, APPLY
            "advisory_id": advisory_id,
            "details": details
        }
        self.logs.append(entry)
        logger.info(f"AUDIT [{action}]: {advisory_id} - {details}")

advisory_audit = AdvisoryAudit()
