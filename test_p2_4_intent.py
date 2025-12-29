#!/usr/bin/env python3
"""
P2.4 Intent Router Test - All required test cases
"""

import sys
sys.path.insert(0, 'c:\\Users\\Virendra\\ai-os')
sys.path.insert(0, 'c:\\Users\\Virendra\\ai-os\\brain')

from brain.core.intent_router import classify_intent

# Required test cases from P2.4 spec
test_cases = [
    ("hello", "CHAT"),
    ("hi", "CHAT"),
    ("status", "CHAT"),
    ("scroll", "CHAT"),
    ("scroll down", "TASK"),
    ("open chrome", "TASK"),
    ("can you open chrome", "CHAT"),
    ("please scroll down", "CHAT"),
    ("scroll down now", "TASK"),
]

print("=" * 70)
print("P2.4: Intent Boundary Lock - Test Results")
print("=" * 70)

passed = 0
failed = 0
results = []

for query, expected in test_cases:
    decision = classify_intent(query)
    status = "✓ PASS" if decision.intent == expected else "✗ FAIL"
    
    if decision.intent == expected:
        passed += 1
    else:
        failed += 1
    
    result_line = f"{status}: '{query}' → {decision.intent} (reason: {decision.reason})"
    print(result_line)
    results.append((query, expected, decision.intent, decision.reason, decision.intent == expected))

print("=" * 70)
print(f"Results: {passed} passed, {failed} failed")
print("=" * 70)

if failed > 0:
    print("❌ VERIFICATION FAILED")
    sys.exit(1)
else:
    print("✅ ALL TESTS PASSED - Intent boundary locked!")
    sys.exit(0)
