import logging
from brain.memory.mission_memory import MissionMemory
from brain.missions.mission_outcome import MissionOutcome, MissionStatus

logger = logging.getLogger(__name__)

class TrustFeedback:
    """
    Adjusts trust initialization based on historical mission outcomes.
    Enforces strict bounds to prevent runaway feedback loops.
    """
    MAX_DELTA = 0.1
    
    def __init__(self, memory: MissionMemory):
        self.memory = memory
        
    def adjust_initial_trust(self, mission_type: str, base_trust: float) -> float:
        """
        Calculates a new initial trust score based on history.
        """
        stats = self.memory.get_stats(mission_type)
        
        if stats["sample_size"] < 3:
            # Not enough data, stick to base trust
            return base_trust
            
        success_rate = stats["success_rate"]
        
        # Simple heuristic:
        # > 80% success -> +delta
        # < 50% success -> -delta
        
        delta = 0.0
        if success_rate >= 0.8:
            delta = 0.05
        elif success_rate < 0.5:
            delta = -0.05
            
        # Clamp delta just in case logic changes
        delta = max(-self.MAX_DELTA, min(self.MAX_DELTA, delta))
        
        adjusted = base_trust + delta
        # Ensure result is within [0.0, 1.0] valid trust range
        adjusted = max(0.0, min(1.0, adjusted))
        
        if delta != 0:
            logger.info(f"Trust adjustment for {mission_type}: {base_trust} -> {adjusted} (Delta: {delta})")
            
        return adjusted

trust_feedback = None # Will be initialized with global memory
