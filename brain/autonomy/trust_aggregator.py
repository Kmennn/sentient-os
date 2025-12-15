
import logging
from typing import Dict
from brain.autonomy.trust_model import TrustModel, TrustTier

logger = logging.getLogger(__name__)

class TrustAggregator:
    """
    Aggregates trust across multiple missions to compute a Global System Trust.
    Ensures that a single bad actor (mission) degrades global trust.
    """
    def __init__(self):
        self._mission_trust: Dict[str, TrustModel] = {}
        
    def register_mission(self, mission_id: str):
        if mission_id not in self._mission_trust:
            self._mission_trust[mission_id] = TrustModel() # Start fresh/neutral
            
    def get_mission_trust(self, mission_id: str) -> TrustModel:
        if mission_id not in self._mission_trust:
            self.register_mission(mission_id)
        return self._mission_trust[mission_id]
        
    def get_global_trust_score(self) -> float:
        """
        Conservative aggregation: 
        Global Trust = Average of all missions, weighted towards the lowest?
        Or simply: MIN(all active missions) to be safest.
        Policy: We take the Minimum score of any active mission to represent 'System Health'.
        """
        if not self._mission_trust:
            return 1.0 # Default High
            
        scores = [tm.score for tm in self._mission_trust.values()]
        return min(scores)
        
    def get_global_tier(self) -> TrustTier:
        min_score = self.get_global_trust_score()
        # Re-use TrustModel logic to map score -> tier
        # We can just instantiate a tmp model or static method, or just logic here.
        # Logic: >0.8 High, >0.5 Medium, else Low.
        if min_score >= 0.8:
            return TrustTier.HIGH
        elif min_score >= 0.5:
            return TrustTier.MEDIUM
        return TrustTier.LOW

trust_aggregator = TrustAggregator()
