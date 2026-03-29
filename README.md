# Sentient OS

Intent-driven autonomous desktop system with local AI.

Sentient OS is organized into three layers:

- Brain: Cognitive runtime, planning, safety, routing, memory, event streaming.
- Body: Local Kernel for physical affordances (telemetry, screenshot, controlled actions).
- Face: Flutter desktop client for state, chat, diagnostics, and control.

This repository combines active implementation work with architecture docs and verification reports. Treat it as an evolving system with both stable and experimental surfaces.

## 1) What Sentient OS Is

Sentient OS is designed as infrastructure, not a chatbot:

- Runs continuously and manages digital context over time.
- Defaults to silent operation and acts when confidence and policy allow.
- Uses explicit safety gates for high-risk or physical actions.
- Supports local-first model execution (Ollama + local embeddings/OCR/tooling).

For design intent and interaction philosophy, see:

- `HOW_TO_THINK_ABOUT_SENTIENT_OS.md`
- `HUMAN_INTERFACE_CONTRACT.md`
- `VOICE_OUTPUT_POLICY.md`
- `COMMAND_SPEC.md`

## 2) Current System Shape

Top-level major modules:

- `brain/`: FastAPI cognitive backend and autonomy runtime.
- `local_kernel/`: Local machine interaction and action execution layer.
- `hello_ai_os/`: Flutter desktop app.
- `brain_data/` and `data/`: runtime/user context data artifacts.
- `tests/`, `brain/tests/`, `local_kernel/tests/`: test and verification assets.
- `docs/`, `releases/`, `*_REPORT.md`: architecture, release, and audit history.

## 3) Architecture Overview

### Brain (Python/FastAPI)

Primary responsibilities:

- Intent handling and agent routing.
- Mission scheduling and tick-based autonomy loop.
- Safety checks, trust/override/recovery policies.
- Timeline, memory, preferences, and explainability endpoints.
- WebSocket stream for real-time UI sync.

Important entrypoints:

- `brain/main.py`: launches stream-first runtime on port 8000.
- `brain/api/stream.py`: aggregate API + websocket app.
- `brain/brain_server.py`: alternate app surface used in offline/model-management workflows.

### Body (Local Kernel)

Primary responsibilities:

- Telemetry (CPU/RAM/process/system metadata).
- Screenshot capture and active window metadata.
- Gated action execution (simulated/real modes).
- Wake signal relay to Brain over websocket.

Entrypoints:

- `local_kernel/kernel.py`
- `local_kernel/action_executor.py`

### Face (Flutter)

Primary responsibilities:

- User shell, chat timeline, visual panels.
- Brain websocket session and ping/pong lifecycle.
- Telemetry and vision integrations.
- Task planner and runtime controls.

Entrypoints:

- `hello_ai_os/lib/main.dart`
- `hello_ai_os/lib/services/sync_service.dart`

## 4) Runtime Ports and Service Boundaries

Default local ports:

- Brain API + WS: `127.0.0.1:8000`
- Local Kernel API: `127.0.0.1:8001`
- Ollama API: `127.0.0.1:11434`

Notes:

- The UI uses Brain on 8000 as primary source of truth.
- Some "body-like" endpoints are also exposed through Brain routes for compatibility.
- Physical actions require Local Kernel on 8001 and explicit safety mode allowances.

## 5) Prerequisites

- Python 3.10+
- Flutter 3.x (Windows desktop enabled)
- Ollama installed and running locally
- Optional but commonly needed for full features:
   - Tesseract/EasyOCR dependencies
   - Desktop automation access for `pyautogui`

## 6) Quick Start (Recommended)

### A. Install dependencies

```powershell
pip install -r brain/requirements.txt
pip install -r local_kernel/requirements.txt
```

### B. Run migrations

```powershell
python brain/scripts/migrate_db_v1_8.py
python brain/scripts/migrate_db_v1_9.py
```

### C. Start services

Terminal 1 (Brain):

```powershell
python brain/main.py
```

Terminal 2 (Body/Kernel):

```powershell
python local_kernel/kernel.py
```

Terminal 3 (Flutter UI):

```powershell
cd hello_ai_os
flutter pub get
flutter run -d windows
```

## 7) Offline Model Setup

Ensure Ollama is serving and model is present:

```powershell
ollama serve
ollama pull mistral
```

Common environment variables:

```powershell
$env:OLLAMA_URL="http://127.0.0.1:11434"
$env:OLLAMA_MODEL="mistral"
```

Automated helper script:

- `setup_offline.ps1` (contains a full setup/run flow; review path assumptions before use).

## 8) API Surface Summary

Representative endpoints (non-exhaustive):

- Health/introspection:
   - `GET /ping`
   - `GET /local-intelligence`
   - `GET /v1/models`
- Chat:
   - `GET /reply`
   - `POST /chat`
- Real-time:
   - `WS /ws`
- Vision/tools/voice:
   - `POST /vision/analyze`
   - `GET /tools`
   - `POST /tools/run`
   - `POST /voice/transcribe`
- Body bridge and runtime controls:
   - `POST /system/mode`
   - `POST /action/request`

Kernel endpoints include:

- `GET /health`
- `GET /status`
- `GET /stream`
- `GET /screenshot`
- `POST /action/run`

## 9) Safety and Autonomy Model

Autonomy modes:

- `OFF`: action execution denied.
- `SIMULATED`: actions planned/logged but not physically executed.
- `REAL`: physical execution allowed only when safety lock permits.

Safety behavior patterns:

- High-risk actions require confirmation.
- Real execution is deny-by-default.
- Override/emergency flows are audited in runtime state and logs.

Design references:

- `COMMAND_SPEC.md`
- `VOICE_OUTPUT_POLICY.md`
- `HUMAN_INTERFACE_CONTRACT.md`
- `STABILITY_DECLARATION.md`

## 10) Testing and Verification

Run test suites:

```powershell
python -m pytest
```

Repository also contains targeted verification scripts and reports:

- Scripts: `verify_part2.py`, `verify_loop.py`, `verify_safety.py`, `test_*.py`
- Reports: `PART1_REPORT.md`, `PART2_REPORT.md`, `PART3_REPORT.md`, `SYSTEM_AUDIT_REPORT.md`, `BETA_REPORT.md`

Use reports as operational evidence snapshots, not guaranteed current runtime truth.

## 11) Known Integration Realities

- There are overlapping API compositions (`brain/main.py` + stream app, and `brain/brain_server.py`).
- Voice backend exists, but some UI paths still indicate simulated voice behavior.
- Full physical control requires Local Kernel running and correctly authorized.
- Helper scripts may contain machine-specific paths and can need edits before use.

## 12) Troubleshooting

### Brain fails with import errors

Symptoms:

- `ModuleNotFoundError` around `core` or `brain` modules.

Actions:

- Launch from repository root.
- Ensure virtual environment and dependencies are installed for both `brain` and `local_kernel`.

### UI connects but actions do not execute

Check:

- `local_kernel/kernel.py` is running on port 8001.
- Autonomy mode is not `OFF`.
- Real action safety lock is explicitly enabled where required.

### Vision or screenshot fails

Check:

- Desktop/session permissions for screenshot capture.
- OCR dependencies (`pytesseract`, binary installation) where applicable.

### Local model responses fail

Check:

- Ollama is running (`ollama serve`).
- Selected model is pulled (`ollama pull <model>`).
- `OLLAMA_URL` is reachable from Brain process.

## 13) Release and Evolution Notes

Useful project history:

- `RELEASE.md`
- `releases/v1.9.md`
- `CHANGELOG.md`

Stability policy for autonomy subsystems:

- `STABILITY_DECLARATION.md`

## 14) Suggested Day-1 Bring-Up Checklist

1. Install dependencies for Brain and Kernel.
2. Start Ollama and pull model.
3. Run database migrations.
4. Start Brain on 8000.
5. Start Kernel on 8001.
6. Start Flutter app and verify websocket connection.
7. Verify `/health`, `/status`, and chat reply path.
8. Test mode switch (`OFF` -> `SIMULATED` -> `REAL`) before physical actions.

---

If you are onboarding a new environment, begin with this README, then follow the contract docs (`H1` to `H5`) and the latest release notes for behavior expectations.
