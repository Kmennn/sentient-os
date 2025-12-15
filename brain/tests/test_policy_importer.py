
import pytest
from brain.learning.policy_importer import PolicyImporter

def test_import_success():
    importer = PolicyImporter()
    data = {
        "sim_version": "3.1",
        "safety_envelope_hash": "abc1234",
        "distilled_rules": {"height": 0.2}
    }
    result = importer.import_policy(data)
    assert result is not None

def test_import_fail_missing_meta():
    importer = PolicyImporter()
    data = {"weights": []}
    result = importer.import_policy(data)
    assert result is None
