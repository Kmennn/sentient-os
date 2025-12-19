# Sentient Console V2 Flow (H2)

## 1. Concept

V2 extends the text-based console with "Interactive Modes" that allow for richer, multi-step workflows without leaving the keyboard.

## 2. New Command Modes

### A. Focus Mode (`/focus`)

```
> /focus
[SYSTEM] Entering Focus Config...
[1] Deep Work (Block All, 50m)
[2] Lite (Allow Calls, 25m)
[3] Custom
> 1
[SYSTEM] Focus: DEEP WORK started. Ends at 14:50.
[SYSTEM] Notifications: BLOCKED.
```

### B. Recovery Diagnostics (`/diagnose`)

```
> /diagnose
[SYSTEM] Running Self-Check...
[FAIL] Tick Duration: 120ms (Target: <100ms)
[WARN] Memory Pressure: 85%
[OK]   Invariants
[OK]   Persistence

[RECOMMENDATION]
1. Purge Cache (Est. -200MB)
2. Restart Scheduler (Soft)
> 1
[ACTION] Purging Cache... Done.
[STATUS] Memory Pressure: 65% (OK)
```

### C. History Narrative (`/rewind`)

```
> /rewind 1h
[SYSTEM] Generating Narrative for last hour...
- 10:00: Started 'Code Review' (VS Code).
- 10:15: Interrupted by 'Slack' (Blocked).
- 10:45: Context switched to 'Browser' (Research).
- 10:55: Returned to 'VS Code'.
[SUMMARY] High Fragmentation (3 switches). Efficiency: 65%.
```

## 3. Real-Time Stream (TUI)

The console now supports a split-screen view:

- **Top:** Active Status / Ticker
- **Bottom:** Input / Log Scrolling
  _(Note: Requires TUI library like `textual` or `curses` in future impl)_

## 4. Keybinding Shortcuts

- `Ctrl+C`: Abort Current Action (Safety).
- `Ctrl+D`: Detach Console (Background Mode).
- `Ctrl+R`: Force Reload Config.
