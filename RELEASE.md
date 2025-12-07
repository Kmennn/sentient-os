# Release Notes - Sentient OS v1.8 "Autonomy"

**Date:** 2025-12-07
**Branch:** `feat/v1.8-autonomy`

## 🚀 Key Features

### 1. Agentic Capabilities

The Brain now has dedicated Agents for different tasks:

- **SearchAgent**: Uses Vector Memory to retrieve context.
- **TaskAgent**: Breaks down complex requests into steps (Plans).
- **Routing**: `LLMService` automatically detects intent (CHAT vs TASK vs SEARCH).

### 2. Action Execution Bridge (Body)

- **ActionExecutor**: A new component in `local_kernel` that can perform real keyboard/mouse actions.
- **Security**: Actions are **DENIED** by default.
- **Autonomy Modes**:
  - **OFF**: No actions processed.
  - **SIMULATED**: Actions logged but not executed (Safe Mode).
  - **REAL**: Actions executed on the User's PC (Requires User Authorization).

### 3. Task Planner UI

- New "Task Planner" screen in the Flutter App.
- Visualizes Agent steps.
- Toggle Autonomy Mode directly from the UI.

### 4. Database Updates

- New tables: `agent_logs` and `action_records`.
- Migration script included: `scripts/migrate_db_v1_8.py`.

## 🛠 Setup & Migration

1.  **Migrate DB**:

    ```powershell
    python brain/scripts/migrate_db_v1_8.py
    ```

2.  **Restart Services**:

    - Restart Brain (`uvicorn brain.brain_server:app ...`)
    - Restart Body (`uvicorn local_kernel.kernel:app ...`)

3.  **Use**:
    - Ask "Open Notepad" to see the planner in action.
    - Go to "Task Planner" page to enable REAL mode if you dare.

## ⚠️ Known Limitations

- "REAL" mode uses `pyautogui` which takes control of your mouse. Use with caution.
- Task planning is basic (one-shot JSON generation).
