# Sentient Console v1 (H1)

## 1. Overview

The **Sentient Console** is a developer-centric, text-based interface for interacting with the Mission Scheduler and Autonomy features. It prioritizes density, speed, and logs over aesthetics.

## 2. Layout

```
+---------------------------------------------------------------+
|  STATUS: ONLINE   |   TICK: 145ms (SLOW)  |   HEALTH: OK      |
+---------------------------------------------------------------+
|  ACTIVE MISSION: Research "Quantum Computing"                 |
|  [EXEC] Searching Arxiv...                                    |
+---------------------------------------------------------------+
|  SUGGESTIONS [2]                                              |
|  [1] Optimize Database (High Util)                            |
|  [2] Enable Focus Mode (Context)                              |
+---------------------------------------------------------------+
|  LOGS (Tail -f)                                               |
|  [12:00:01] [INFO] Tick started                               |
|  [12:00:01] [WARN] Tick duration > 100ms                      |
|  [12:00:02] [INFO] Decision: CONTINUE                         |
+---------------------------------------------------------------+
|  > _ (Command Input)                                          |
+---------------------------------------------------------------+
```

## 3. Command Reference

| Command                   | Action                            |
| :------------------------ | :-------------------------------- |
| `/status`                 | Show full system state (JSON).    |
| `/mission start [desc]`   | Queue a new mission.              |
| `/mission stop`           | Abort current mission.            |
| `/suggestion accept [id]` | Accept proactive suggestion.      |
| `/runtime panic`          | Simulate a crash (Test Recovery). |
| `/runtime override`       | Request manual override token.    |

## 4. Event Flows

### A. Crash & Recovery

1. User enters `/runtime panic`.
2. System Logs: `[CRITICAL] Runtime Exception detected.`
3. Console Status: `HEALTH: RECOVERY (SOFT)`
4. Action: Mission Paused.
5. User enters `/mission resume`.
6. System Logs: `[BLOCK] Cannot resume in Recovery Mode.`

### B. Proactive Suggestion

1. Backend detects high resource usage.
2. Console Suggestions: `[NEW] [3] Kill Chrome (Memory Leak)`
3. User enters `/suggestion accept 3`.
4. System Logs: `[ACTION] Killing Chrome process...`
