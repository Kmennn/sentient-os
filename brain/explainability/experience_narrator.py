from typing import List, Optional
from brain.memory.mission_memory import MissionMemory
from brain.optimization.mission_optimizer import MissionOptimizer
from brain.missions.mission_outcome import MissionStatus

class ExperienceNarrator:
    """
    Generates human-readable insights from mission history and optimization hints.
    """
    def __init__(self, memory: MissionMemory, optimizer: MissionOptimizer):
        self.memory = memory
        self.optimizer = optimizer

    def narrate_insights(self, mission_type: str) -> str:
        stats = self.memory.get_stats(mission_type)
        if stats["sample_size"] == 0:
            return f"No prior experience for '{mission_type}'."

        outcomes = self.memory.get_outcomes(mission_type, limit=5)
        recent_status = [o.status for o in outcomes]
        
        narrative = []
        
        # 1. Historical Context
        success_rate_pct = int(stats["success_rate"] * 100)
        narrative.append(f"Success rate: {success_rate_pct}% ({stats['sample_size']} missions).")
        
        # 2. Recent Trend
        failures = recent_status.count(MissionStatus.FAILURE) + recent_status.count(MissionStatus.ABORTED)
        if failures > 0:
            narrative.append(f"Last {len(recent_status)} runs had {failures} issues.")
            
            # Find common failure reason
            reasons = {}
            for o in outcomes:
                if o.status in (MissionStatus.FAILURE, MissionStatus.ABORTED) and o.failure_reason:
                    reasons[o.failure_reason] = reasons.get(o.failure_reason, 0) + 1
            
            if reasons:
                top_reason = max(reasons, key=reasons.get)
                narrative.append(f"Most common error: {top_reason}.")

        # 3. Optimization Advice
        hints = self.optimizer.analyze_history(mission_type)
        if hints:
            narrative.append("Suggestions:")
            for h in hints:
                narrative.append(f"- {h.action.name.replace('_', ' ').title()}: {h.reason}")
        
        return " ".join(narrative)

experience_narrator = None # Will be initialized
