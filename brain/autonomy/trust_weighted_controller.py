
import logging
from brain.autonomy.trust_model import TrustModel, TrustTier, trust_model
from brain.missions.mission_contract import AutonomyLevel

logger = logging.getLogger(__name__)

class TrustWeightedController:
    """
    Decides the Effective Autonomy Level based on the Contract and current Trust.
    Safety Principle: We can act with LESS autonomy than contracted (more safety), but never MORE.
    """
    def __init__(self, model: TrustModel = trust_model):
        self.model = model
        
    def get_effective_level(self, contracted_level: AutonomyLevel) -> AutonomyLevel:
        tier = self.model.get_tier()
        
        # Rule: If Low Trust, downgrade EXECUTE to ASSIST
        if tier == TrustTier.LOW and contracted_level == AutonomyLevel.EXECUTE:
            logger.warning("Trust Weighted Controller: Downgrading EXECUTE -> ASSIST (Low Trust)")
            return AutonomyLevel.ASSIST
            
        # Medium/High Trust: Respect Contract
        return contracted_level
        
    def should_pause_for_confirmation(self, contracted_level: AutonomyLevel) -> bool:
        effective = self.get_effective_level(contracted_level)
        return effective == AutonomyLevel.ASSIST

trust_weighted_controller = TrustWeightedController()
