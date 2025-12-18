
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

    def log_hints(self, mission_id: str, hints: List[Any]):
        """
        Log optimization hints used for scheduling/execution.
        """
        hint_data = []
        for h in hints:
            # Check if h is OptimizationHint or dict
            if hasattr(h, 'action'):
                hint_data.append({
                    "action": h.action.name,
                    "reason": h.reason,
                    "parameter": h.parameter
                })
            else:
                hint_data.append(str(h))
                
        self.log_event(mission_id, "OPTIMIZATION_HINTS", hint_data)

    def log_trust_init(self, mission_id: str, base_trust: float, adjustment: float, final_score: float):
        """
        Log how trust was initialized (including memory-based adjustments).
        """
        self.log_event(mission_id, "TRUST_INIT", {
            "base_trust": base_trust,
            "adjustment": adjustment,
            "final_score": final_score
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
        
    def log_approval(self, mission_id: str, approver_id: str, approver_role: str, approved: bool, reason: str = None):
        """
        Log an approval or denial decision by a user.
        """
        self.log_event(mission_id, "APPROVAL_DECISION", {
            "approver_id": approver_id,
            "approver_role": approver_role,
            "approved": approved,
            "reason": reason
        })

    def log_conflict(self, mission_id: str, conflict_info: dict):
        """
        Log details about a detected conflict.
        conflict_info should be a dict describing the conflict (or serialized ConflictReport).
        """
        self.log_event(mission_id, "CONFLICT_DETECTED", conflict_info)

    def log_deferral(self, mission_id: str, new_start_time: float, reason: str):
        self.log_event(mission_id, "MISSION_DEFERRED", {
            "new_start_time": new_start_time,
            "reason": reason
        })

    def log_preference(self, mission_id: str, pref_key: str, pref_value: str):
        self.log_event(mission_id, "PREFERENCE_USED", {
            "key": pref_key,
            "value": pref_value
        })

    def log_routine(self, mission_id: str, routine_name: str, action: str):
        self.log_event(mission_id, "ROUTINE_EVENT", {
            "routine_name": routine_name,
            "action": action # DETECTED, PROTECTED, CONFLICTED
        })

    def log_proactive_suggestion(self, routine_name: str, action: str):
        # Proactive events might not have a mission_id yet if just a suggestion
        # Use "system" or specific ID?
        # For now, trace under "proactive_log"
        if "proactive_log" not in self.traces:
            self.traces["proactive_log"] = {
                "contract": {"mission_id": "proactive_log", "type": "SYSTEM"},
                "events": []
            }
            
        self.log_event("proactive_log", "PROACTIVE_SUGGESTION", {
            "routine_name": routine_name,
            "action": action # SHOWN, ACCEPTED, DISMISSED
        })

    def log_day_plan_usage(self, action: str):
        """
        Log when Day Plan is generated or viewed.
        """
        if "day_plan_log" not in self.traces:
             self.traces["day_plan_log"] = {
                "contract": {"mission_id": "day_plan_log", "type": "SYSTEM"},
                "events": []
             }
             
        self.log_event("day_plan_log", "DAY_PLAN_USAGE", {
            "action": action # GENERATED, VIEWED
        })

    def log_week_insights(self, action: str, insight_count: int = 0):
        """
        Log when Week Insights are generated or viewed.
        """
        if "week_insights_log" not in self.traces:
             self.traces["week_insights_log"] = {
                "contract": {"mission_id": "week_insights_log", "type": "SYSTEM"},
                "events": []
             }
             
        self.log_event("week_insights_log", "WEEK_INSIGHTS_USAGE", {
            "action": action, # GENERATED, VIEWED
            "insight_count": insight_count
        })

    def log_load_insights(self, action: str):
        """
        Log when Load Insights are generated or viewed.
        """
        if "load_insights_log" not in self.traces:
             self.traces["load_insights_log"] = {
                "contract": {"mission_id": "load_insights_log", "type": "SYSTEM"},
                "events": []
             }
             
        self.log_event("load_insights_log", "LOAD_INSIGHT_USAGE", {
            "action": action # GENERATED, VIEWED
        })

    def log_reflection(self, action: str, prompt_id: str):
        """
        Log Reflection events.
        """
        if "reflection_log" not in self.traces:
             self.traces["reflection_log"] = {
                "contract": {"mission_id": "reflection_log", "type": "SYSTEM"},
                "events": []
             }
             
        self.log_event("reflection_log", "REFLECTION_USAGE", {
            "action": action, # SHOWN, DISMISSED, REFLECTED
            "prompt_id": prompt_id
        })

    def log_simulation(self, action: str, scenario_id: str):
        """
        Log What-If Simulation events.
        """
        if "simulation_log" not in self.traces:
             self.traces["simulation_log"] = {
                "contract": {"mission_id": "simulation_log", "type": "SYSTEM"},
                "events": []
             }
             
        self.log_event("simulation_log", "WHAT_IF_USAGE", {
            "action": action, # VIEWED, RUN
            "scenario_id": scenario_id
        })

    def log_coplan(self, action: str, proposal_id: str):
        """
        Log Co-Planning events.
        """
        if "coplan_log" not in self.traces:
             self.traces["coplan_log"] = {
                "contract": {"mission_id": "coplan_log", "type": "SYSTEM"},
                "events": []
             }
             
        self.log_event("coplan_log", "COPLAN_ACTION", {
            "action": action, # CREATED, APPLIED, REVERTED
            "proposal_id": proposal_id
        })

    def log_shared_vote(self, proposal_id: str, user_id: str, vote: bool):
        """
        Log voting events.
        """
        if "coplan_log" not in self.traces:
             self.traces["coplan_log"] = {
                "contract": {"mission_id": "coplan_log", "type": "SYSTEM"},
                "events": []
             }
             
    def log_delegation_used(self, proposal_id: str, delegate_id: str, on_behalf_of: str):
        """
        Log delegation usage.
        """
        if "coplan_log" not in self.traces:
             self.traces["coplan_log"] = {
                "contract": {"mission_id": "coplan_log", "type": "SYSTEM"},
                "events": []
             }
             
        self.log_event("coplan_log", "DELEGATION_USED", {
            "proposal_id": proposal_id,
            "delegate_id": delegate_id,
            "on_behalf_of": on_behalf_of
        })

    def log_delegation_blocked(self, proposal_id: str, delegate_id: str, reason: str):
        """
        Log blocked delegation usage.
        """
        self.log_event("coplan_log", "DELEGATION_BLOCKED", {
            "proposal_id": proposal_id,
            "delegate_id": delegate_id,
            "reason": reason
        })

mission_audit = MissionAudit()
