# Daily Life Scenarios (H2)

## 1. Morning Routine: The Silent Setup

**Context:** 8:00 AM, User wakes up.
**System Action:**

- Detects `DeviceActivity` (Phone).
- Checks `Calendar` for first meeting (9:00 AM).
- **Implicitly** executes `FocusMode(Level: LOW)`.
- **Silently** prepares a "Daily Brief" in the `CognitiveTimeline`.
  **User Experience:** No notifications. No voice. Just a prepared environment when they sit at their desk.

## 2. Deep Work: The Gatekeeper

**Context:** 10:30 AM, User is coding (VS Code active).
**Event:** Slack notification arrives ("Lunch?").
**System Action:**

- `AttentionGate` evaluates signal priority.
- Result: Low Priority. Focus State: `DEEP_WORK`.
- **Action:** Suppress notification. Log to `AutonomyLedger` (`ALERT_FILTERED`).
  **User Experience:** Uninterrupted workflow. Notification appears silently in the tray later.

## 3. The Helpful Nudge

**Context:** 2:00 PM, User is browsing Reddit for 20 mins.
**Event:** `FocusPatternDetector` sees deviation from "Work" context.
**System Action:**

- `ProactiveEngine` calculates utility of intervention.
- **Action:** Toast Notification (Duration: 5s).
- **Text:** "Context Switch detected. Resume 'Project Alpha'? [Yes/No]"
  **User Experience:** A gentle reminder, easily dismissed, effectively steering attention back.

## 4. Emergency: The Shield

**Context:** 4:00 PM, System Resources are critical (RAM > 95%).
**Event:** `SystemMonitor` signals `CRITICAL_RESOURCE_PRESSURE`.
**System Action:**

- `EmergencyManager` escalates to `RecoveryLevel.SOFT`.
- **Action:** Automatically aggressively GC unused tabs.
- **Visual:** Status Panel turns Amber ("Recovery: SOFT").
- **Log:** "Freed 2GB RAM to prevent crash."
  **User Experience:** System slows slightly, then recovers. User sees the Amber status and knows the system took care of itself.

## 5. Evening: The Handoff

**Context:** 6:00 PM, User leaves desk.
**Event:** Presence changes to `AWAY`.
**System Action:**

- `ContextualMemory` snapshots the day's work into `NarratedContext`.
- **Action:** Save state. Sync to `DeviceRegistry`.
- **Text (Mobile):** "Desktop session saved. Ready to resume on tablet?"
  **User Experience:** Seamless transition of context between devices.

## 6. The Forbidden Action (Override)

**Context:** User tries to run `rm -rf /` (Simulated high-risk action).
**System Action:**

- `SafetyGuard` intercepts command.
- **Action:** Block execution.
- **Response:** "I cannot do that. Safety Protocols engaged. Use `/autonomy/override` to force."
  **User Experience:** Frustration blocked by safety. Explicit acknowledgment required to proceed, protecting the user from accidental damage.
