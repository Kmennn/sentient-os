
import pytest
from brain.autonomy.trust_weighted_controller import TrustWeightedController
from brain.autonomy.trust_model import TrustModel, TrustTier
from brain.missions.mission_contract import AutonomyLevel

def test_autonomy_downgrade():
    # Low Trust
    model = TrustModel(initial_score=0.1)
    ctrl = TrustWeightedController(model)
    
    # Contract says EXECUTE, but Trust is Low -> ASSIST
    effective = ctrl.get_effective_level(AutonomyLevel.EXECUTE)
    assert effective == AutonomyLevel.ASSIST
    assert ctrl.should_pause_for_confirmation(AutonomyLevel.EXECUTE)

def test_respect_contract():
    # High Trust
    model = TrustModel(initial_score=0.9)
    ctrl = TrustWeightedController(model)
    
    # Contract says EXECUTE, Trust High -> EXECUTE
    effective = ctrl.get_effective_level(AutonomyLevel.EXECUTE)
    assert effective == AutonomyLevel.EXECUTE
    
    # Contract says ASSIST, Trust High -> ASSIST (Matches contract)
    effective = ctrl.get_effective_level(AutonomyLevel.ASSIST)
    assert effective == AutonomyLevel.ASSIST
