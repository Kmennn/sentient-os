#!/usr/bin/env python3
"""
Test script for P2.1 Intent Router verification.

Required test cases:
- hello        → CHAT
- hi           → CHAT  
- status       → CHAT
- scroll       → CHAT (missing object)
- scroll down  → TASK
- open chrome  → TASK
- can you scroll down → TASK
"""

import sys
sys.path.insert(0, 'c:\\Users\\Virendra\\ai-os')
sys.path.insert(0, 'c:\\Users\\Virendra\\ai-os\\brain')

from brain.core.intent_router import get_intent

# Test cases from specification
test_cases = [
    ("hello", "CHAT"),
    ("hi", "CHAT"),
    ("status", "CHAT"),
    ("scroll", "CHAT"),  # missing object
    ("scroll down", "TASK"),
    ("open chrome", "TASK"),
    ("can you scroll down", "TASK"),
]

print("=" * 60)
print("P2.1 Intent Router Verification")
print("=" * 60)

passed = 0
failed = 0

for query, expected in test_cases:
    result = get_intent(query)
    status = "✓ PASS" if result == expected else "✗ FAIL"
    
    if result == expected:
        passed += 1
    else:
        failed += 1
    
    print(f"{status}: '{query}' → {result} (expected: {expected})")

print("=" * 60)
print(f"Results: {passed} passed, {failed} failed")
print("=" * 60)

if failed > 0:
    print("❌ VERIFICATION FAILED")
    sys.exit(1)
else:
    print("✅ ALL TESTS PASSED")
    sys.exit(0)
