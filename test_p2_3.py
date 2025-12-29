#!/usr/bin/env python3
"""
P2.3 Automated Test - Intent Routing Verification
Tests that correct inputs route to CHAT vs TASK
"""

import sys
sys.path.insert(0, 'c:\\Users\\Virendra\\ai-os')
sys.path.insert(0, 'c:\\Users\\Virendra\\ai-os\\brain')

from brain.core.intent_router import get_intent

# Test cases from P2.3 matrix
test_cases = [
    # (input, expected_intent, expected_dialog)
    ("hello", "CHAT", False),
    ("status", "CHAT", False),
    ("scroll down", "TASK", True),
    ("cancel", "CHAT", False),
    # Abort is tested manually in UI
]

print("=" * 60)
print("P2.3: Action Confirmation Reliability - Intent Tests")
print("=" * 60)

passed = 0
failed = 0

for query, expected_intent, should_show_dialog in test_cases:
    result = get_intent(query)
    dialog_text = "DIALOG" if should_show_dialog else "NO DIALOG"
    status = "✓ PASS" if result == expected_intent else "✗ FAIL"
    
    if result == expected_intent:
        passed += 1
    else:
        failed += 1
    
    print(f"{status}: '{query}' → {result} ({dialog_text})")

print("=" * 60)
print(f"Results: {passed} passed, {failed} failed")
print("=" * 60)

if failed > 0:
    print("❌ VERIFICATION FAILED")
    sys.exit(1)
else:
    print("✅ INTENT ROUTING CORRECT")
    print("\n⚠️  Manual UI test still required for:")
    print("   - Dialog appearance")
    print("   - Cancel/Abort button states")
    sys.exit(0)
