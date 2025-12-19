# Real World Capabilities (H1)

## 1. Context Awareness

| Backend Feature        | User Capability                             | Limitation                              |
| :--------------------- | :------------------------------------------ | :-------------------------------------- |
| `AmbientObserver`      | "I know if you are busy or free."           | Sensor data only (camera/mic presence). |
| `FocusPatternDetector` | "I can detect when you are in 'Deep Work'." | Needs 15m of history to trigger.        |
| `ContextualMemory`     | "I remember what you were doing yesterday." | Text/Code context only.                 |

## 2. Autonomy & Action

| Backend Feature    | User Capability                      | Limitation                                            |
| :----------------- | :----------------------------------- | :---------------------------------------------------- |
| `MissionScheduler` | "I can run tasks in the background." | Limited to 100ms ticks (no heavy compute).            |
| `ProactiveEngine`  | "I can suggest help before you ask." | Suggestions are passive (Toast/Log) unless Emergency. |
| `RecoveryManager`  | "I fix my own crashes."              | HARD recovery requires manual override.               |

## 3. Safety & Trust

| Backend Feature     | User Capability                                  | Limitation                      |
| :------------------ | :----------------------------------------------- | :------------------------------ |
| `AutonomyLedger`    | "I keep a permanent record of every decision."   | Read-only. Cannot be edited.    |
| `SystemStatusPanel` | "You can see my brain's health instantly."       | Read-only transparency.         |
| `OverrideManager`   | "You can force me to obey, even if it's unsafe." | Lowers trust score immediately. |

## 4. Integration

| Backend Feature            | User Capability                                     | Limitation                       |
| :------------------------- | :-------------------------------------------------- | :------------------------------- |
| `ExternalSuggestionBridge` | "I can react to external events (email, calendar)." | Passive bridge; polling based.   |
| `DeviceRegistry`           | "I know which device you are using."                | Desktop/Mobile distinction only. |
