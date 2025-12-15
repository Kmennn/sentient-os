
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
    def __init__(self, log_path: str = None):
        self.traces: Dict[str, Dict[str, Any]] = {}
        self.log_path = log_path
        # Ensure dir exists
        if self.log_path:
            import os
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

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

    def log_scheduling(self, mission_id: str, action: str, details: Dict = None):
        """
        Log Scheduler decisions: QUEUE, START, PREEMPT.
        """
        data = details or {}
        data['action'] = action
        self.log_event(mission_id, "SCHEDULING", data)
        
    def log_resource_event(self, mission_id: str, resource_id: str, event_type: str):
        """
        Log Resource locks: ACQUIRE, RELEASE, DENIED.
        """
        self.log_event(mission_id, "RESOURCE_LOCK", {
            "resource": resource_id,
            "event": event_type
        })

        
    def log_event(self, mission_id: str, event_type: str, details: Any):
        if mission_id not in self.traces:
            return
            
        entry = {
            "type": event_type,
            "details": details
        }
        self.traces[mission_id]["events"].append(entry)
        
        if self.log_path:
            # Flatten for linear log: timestamp, mission_id, type, details
            import time
            flat_entry = {
                "timestamp": time.time(),
                "mission_id": mission_id,
                "event_type": event_type,
                "details": details
            }
            with open(self.log_path, 'a') as f:
                json.dump(flat_entry, f)
                f.write('\n')
        
    def export_json(self, mission_id: str) -> str:
        if mission_id not in self.traces:
            return "{}"
        return json.dumps(self.traces[mission_id], indent=2)

mission_audit = MissionAudit()
