
import pytest
from brain.missions.mission_contract import MissionContract
from brain.safety.mission_enforcer import MissionEnforcer, MissionViolationError

def test_scope_validation():
    contract = MissionContract(
        allowed_actions=["pick"],
        allowed_objects=["cup"]
    )
    enforcer = MissionEnforcer(contract)
    
    # Valid
    enforcer.validate_action("pick", "cup")
    
    # Invalid Action
    with pytest.raises(MissionViolationError) as e:
        enforcer.validate_action("throw", "cup")
    assert "Action 'throw' not allowed" in str(e.value)
    
    # Invalid Object
    with pytest.raises(MissionViolationError) as e:
        enforcer.validate_action("pick", "ball")
    assert "Object 'ball' not allowed" in str(e.value)

def test_time_violation():
    contract = MissionContract(max_duration=0.0)
    enforcer = MissionEnforcer(contract)
    
    import time
    time.sleep(0.01)
    
    with pytest.raises(MissionViolationError) as e:
        enforcer.validate_action("pick", "cup")
    assert "Time Expired" in str(e.value)
