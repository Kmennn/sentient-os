# Voice Output Policy (H4)

## 1. Zero-Voice Default

By default, the system is **silent**. Voice output is an exception, not a feature.
It is treated as a "High-Priority Safety Alerter", not a conversational interface.

## 2. Allowed Triggers (The "Red" List)

Voice output is PERMITTED ONLY for:

1.  **Emergency Escalation**: When the system detects critical instability (`RecoveryLevel.HARD`).
2.  **Safety Intercept**: When a high-risk user action is actively blocked (`Override Required`).
3.  **Manual Override**: When the user explicitly activates "Force Mode" (`Trust Penalty`).
4.  **Recovery Status**: Brief confirmation when entering/exiting recovery modes.

## 3. Strict Suppression (The "Black" List)

Voice output is BLOCKED if:

1.  **Focus Active**: `FocusState` is `DEEP_WORK` or `FLOW`. (Exception: `CRITICAL` resource failure).
2.  **Public Presence**: `PresenceState` is `WITH_OTHERS` or `MEETING`.
3.  **Low Confidence**: Any alert with `< 99%` system confidence.

## 4. Tone & Style

- **Robotic/Neutral**: Do not simulate human emotion.
- **Concise**: Max 10 words.
- **Action-First**: "System Stabilizing" instead of "I am trying to fix the system."
- **No "I"**: Refer to "System", "Process", or "Result".

## 5. Technical Constraints

- **One-Way**: No microphone listening.
- **Local Only**: No cloud TTS APIs (Privacy).
- **Low Latency**: Must speak within 200ms of trigger.
