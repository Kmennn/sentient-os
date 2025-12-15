
import logging
from enum import Enum, auto

logger = logging.getLogger(__name__)

class TrustTier(Enum):
    LOW = auto()    # < 0.5: Frequent pauses
    MEDIUM = auto() # 0.5 - 0.8: Bounded execution
    HIGH = auto()   # > 0.8: Full autonomy

class TrustModel:
    """
    Tracks the system's runtime reliability (Trust Score).
    Adjusts based on mission outcomes and interventions.
    """
    def __init__(self, initial_score: float = 0.5):
        self._score = initial_score
        
    @property
    def score(self) -> float:
        return self._score
        
    def get_tier(self) -> TrustTier:
        if self._score < 0.5:
            return TrustTier.LOW
        elif self._score < 0.8:
            return TrustTier.MEDIUM
        else:
            return TrustTier.HIGH
            
    def update(self, outcome: str):
        """
        Outcome: 'SUCCESS', 'FAILURE', 'CRITICAL_FAILURE', 'INTERVENTION'
        """
        old_score = self._score
        
        if outcome == 'SUCCESS':
            self._score += 0.05
        elif outcome == 'FAILURE':
            self._score -= 0.1
        elif outcome == 'CRITICAL_FAILURE':
            self._score -= 0.3
        elif outcome == 'INTERVENTION':
            # Human had to take over
            self._score -= 0.05
            
        # Clamp
        self._score = max(0.0, min(1.0, self._score))
        
        if self.get_tier() != self._get_tier_for_score(old_score):
            logger.info(f"Trust Tier Changed: {self._get_tier_for_score(old_score).name} -> {self.get_tier().name} (Score: {self._score:.2f})")
            
    def _get_tier_for_score(self, score: float) -> TrustTier:
        if score < 0.5: return TrustTier.LOW
        elif score < 0.8: return TrustTier.MEDIUM
        return TrustTier.HIGH

trust_model = TrustModel()
