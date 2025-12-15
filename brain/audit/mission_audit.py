
import json
import logging
from dataclasses import asdict
from typing import Dict, List, Any
from brain.missions.mission_contract import MissionContract

logger = logging.getLogger(__name__)

class MissionAudit:
    """
    Records the entire lifecycle of a mission for replay and accountability.
    """
    def __init__(self):
        self.traces: Dict[str, Dict[str, Any]] = {}

    def start_mission_log(self, contract: MissionContract):
        s_dict = asdict(contract)
        # Handle enum serialization manually if needed
        s_dict['autonomy_level'] = contract.autonomy_level.name 
        
        self.traces[contract.mission_id] = {
            "contract": s_dict,
            "events": []
        }
        
    def log_trust_change(self, mission_id: str, old_tier: str, new_tier: str, score: float):
        self.log_event(mission_id, "TRUST_CHANGE", {
            "old_tier": old_tier,
            "new_tier": new_tier,
            "score": score
        })
        
    def log_recovery(self, mission_id: str, step_index: int):
        self.log_event(mission_id, "RECOVERY", {
            "restored_at_step": step_index,
            "msg": "System restarted and mission resumed."
        })
        
    def log_event(self, mission_id: str, event_type: str, details: Any):
        if mission_id not in self.traces:
            return
            
        entry = {
            "type": event_type,
            "details": details
        }
        self.traces[mission_id]["events"].append(entry)
        
    def export_json(self, mission_id: str) -> str:
        if mission_id not in self.traces:
            return "{}"
        return json.dumps(self.traces[mission_id], indent=2)

mission_audit = MissionAudit()
