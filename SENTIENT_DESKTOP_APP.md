# Sentient Desktop App (H3)

## 1. Concept

A lightweight, "always-available" companion that lives in the system tray (Windows) or Menu Bar (macOS). It is the primary "Face" of the OS.

## 2. Design Philosophy

- **Unobtrusive**: No dock icon, no taskbar entry.
- **Transient**: Click to open, lose focus to close.
- **Visual**: Dark glass, high contrast, minimal text.

## 3. Core Features

### A. The Shield (Flagship)

A prominent toggle switch representing the `AttentionGate`.

- **State: SHIELD DOWN (Green)**: Interruptions allowed.
- **State: SHIELD UP (Purple)**: Deep Work (Focus Mode).
- **Sub-feature**: "Let Through" list (Spouse, Boss, Critical Alerts).

### B. The Pulse (Health)

A single "Heartbeat" icon.

- **Green**: Healthy.
- **Amber**: Backpressure (System is thinking/cleaning).
- **Red**: Blocked/Recovery (Requires attention).

### C. The Timeline (Memory)

A vertical stream of the last 5 significant events.

- "Saved context from Meeting."
- "Blocked 3 notifications."
- "Optimized RAM."

### D. Suggestions (Feed)

A clean list of proactive insights.

- "Pattern: You usually take a break now."
- "Suggestion: Archive old downloads?"

## 4. Interaction Constraints

- **No Chat**: This is not a conversation window.
- **No Configuration**: Settings are handled via config files or deep links.
- **Voice**: Outputs audio alerts ONLY for critical/emergency events.

## 5. Technology

- **Framework**: Flutter (Desktop Embedder).
- **State**: Polls `Brain` API (`127.0.0.1:8000`).
- **Windowing**: `bitsdojo_window` or system native calls for frameless window.
