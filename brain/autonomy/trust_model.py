
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
        self.user_scores: dict[str, float] = {} # user_id -> trust_multiplier (0.0 to 1.0)
        
    @property
    def score(self) -> float:
        return self._score
        
    def get_effective_score(self, user_id: str = None) -> float:
        """
        Calculate trust score weighted by user reputation.
        User multiplier defaults to 1.0 (neutral/trusted).
        Bad actors get clamped down.
        """
        base = self._score
        if user_id:
            multiplier = self.user_scores.get(user_id, 1.0)
            return base * multiplier
        return base

    def get_tier(self, user_id: str = None) -> TrustTier:
        eff_score = self.get_effective_score(user_id)
        return self._get_tier_for_score(eff_score)
            
    def update(self, outcome: str, user_id: str = None):
        """
        Outcome: 'SUCCESS', 'FAILURE', 'CRITICAL_FAILURE', 'INTERVENTION'
        """
        old_score = self._score
        
        # 1. Update Global System Trust
        if outcome == 'SUCCESS':
            self._score += 0.05
        elif outcome == 'FAILURE':
            self._score -= 0.1
        elif outcome == 'CRITICAL_FAILURE':
            self._score -= 0.3
        elif outcome == 'INTERVENTION':
            # Human had to take over
            self._score -= 0.05
            
        # Clamp Global
        self._score = max(0.0, min(1.0, self._score))
        
        # 2. Update User Reputation if applicable
        if user_id:
            current_user_score = self.user_scores.get(user_id, 1.0)
            if outcome == 'CRITICAL_FAILURE':
                # Penalize user heavily
                self.user_scores[user_id] = max(0.1, current_user_score - 0.2)
            elif outcome == 'SUCCESS':
                 # Slowly rebuild user trust
                 self.user_scores[user_id] = min(1.0, current_user_score + 0.01)
        
        if self.get_tier(user_id) != self._get_tier_for_score(old_score): # Compare roughly against old global
            # This log is a bit messy with mixed contexts, but sufficient.
            pass
            
    def _get_tier_for_score(self, score: float) -> TrustTier:
        if score < 0.5: return TrustTier.LOW
        elif score < 0.8: return TrustTier.MEDIUM
        return TrustTier.HIGH

trust_model = TrustModel()
