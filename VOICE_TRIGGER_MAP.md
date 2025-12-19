# Voice Trigger Map (H4)

## 1. Emergency Escalation

| Event                 | Criteria                             | Phrase                                      |
| :-------------------- | :----------------------------------- | :------------------------------------------ |
| `RECOVERY_HARD_ENTER` | `RecoveryManager` enters HARD level. | "Attention. System entering Hard Recovery." |
| `RECOVERY_HARD_EXIT`  | `RecoveryManager` clears triggers.   | "System Stable. Recovery complete."         |

## 2. Safety & Override

| Event              | Criteria                                | Phrase                                      |
| :----------------- | :-------------------------------------- | :------------------------------------------ |
| `ACTION_BLOCKED`   | High-risk cmd blocked (e.g., `rm -rf`). | "Action Blocked. Safety protocols engaged." |
| `OVERRIDE_GRANTED` | User forces execution.                  | "Override active. Trust penalty applied."   |
| `OVERRIDE_EXPIRED` | 10m token expires.                      | "Override expired. Safety restored."        |

## 3. Runtime Critical

| Event                   | Criteria                       | Phrase                                               |
| :---------------------- | :----------------------------- | :--------------------------------------------------- |
| `STARTUP_BLOCKED`       | Crash loop detected on boot.   | "Startup Interrupted. Manual intervention required." |
| `BACKPRESSURE_CRITICAL` | Tick duration > 500ms for 10s. | "High Load. Throttling background processes."        |

## 4. Test/Verification

| Event       | Criteria               | Phrase                   |
| :---------- | :--------------------- | :----------------------- |
| `SELF_TEST` | Explicit user request. | "Voice Systems Nominal." |
