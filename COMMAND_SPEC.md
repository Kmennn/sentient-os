# Command Specification (H5)

## 1. Principles

- **Whitelist Only**: Unknown commands are rejected.
- **Parametric**: Commands accept arguments (time, id).
- **Safe**: No direct shell access. Only Brain API mappings.

## 2. Command Vocabulary

### A. Focus & State

| Command       | Arguments       | Behavior                              |
| :------------ | :-------------- | :------------------------------------ |
| `/focus`      | `[duration=25]` | Start Deep Work focus session.        |
| `/focus stop` | None            | Cancel active focus session.          |
| `/status`     | None            | Return current system health & state. |

### B. Missions & actions

| Command    | Arguments       | Behavior                              |
| :--------- | :-------------- | :------------------------------------ |
| `/mission` | `[description]` | Queue a new queued mission (Planner). |
| `/stop`    | None            | Preempt valid active mission.         |
| `/resume`  | None            | Resume suspended mission (if safe).   |

### C. Safety & Diagnostic

| Command     | Arguments  | Behavior                                  |
| :---------- | :--------- | :---------------------------------------- |
| `/panic`    | None       | Trigger soft recovery (clean buffers).    |
| `/override` | `[reason]` | Request safety override token.            |
| `/voice`    | `[on/off]` | Toggle voice output policy (Manual gate). |

## 3. Parsing Rules

- Case-insensitive (`/Focus` == `/focus`).
- Slash prefix optional for Tray, mandatory for Console mixed-mode.
- Arguments separated by space.

## 4. Response Format

- **Success**: `[OK] <Message>`
- **Error**: `[ERR] <Reason>`
- **Info**: `[INFO] <Data>`
