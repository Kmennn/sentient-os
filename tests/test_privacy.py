
import pytest
import uuid
from core.policy.action_policy import action_policy
from core.db import init_db

def test_privacy_policy():
    init_db()
    user = f"adv_user_{uuid.uuid4()}"
    
    # 1. Default -> Blocked if REAL_ACTION?
    # Actually logic said "REAL_ACTION" explicitly checks consent["actions"] which defaults to 0.
    assert action_policy.check_action(user, "REAL_ACTION", {}) == False
    
    # 2. Update Consent
    action_policy.update_consent(user, {"actions": True})
    
    # 3. Check again
    assert action_policy.check_action(user, "REAL_ACTION", {}) == True
    
    # 4. Memory
    assert action_policy.check_action(user, "MEMORY_STORE", {}) == False # Default
    action_policy.update_consent(user, {"memory": True})
    assert action_policy.check_action(user, "MEMORY_STORE", {}) == True
