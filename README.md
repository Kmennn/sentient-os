# Sentient OS (v1.9)

An Autonomous AI Operating System.
"Brain" (Python/FastAPI) + "Body" (Local Kernel) + "Face" (Flutter).

## Features (v1.9)

- **Deep Research Agent**: Autonomous multi-step research.
- **Vision**: Enhanced screen analysis with active window detection.
- **Tools**: Advanced system integration (Process, Disk, Web History).
- **Voice**: Offline desktop voice input (Vosk).

## Installation

### Prerequisites

- Python 3.10+
- Flutter 3.x
- Ollama (running locally)

### Setup

1. Clone repo.
2. Install Python deps:
   ```bash
   pip install -r brain/requirements.txt
   pip install -r local_kernel/requirements.txt
   ```
3. Run Database Migration (v1.9):
   ```bash
   python brain/scripts/migrate_db_v1_9.py
   ```

### Running

1. Start Brain:
   ```bash
   python brain/main.py
   ```
2. Start Kernel (Admin recommended):
   ```bash
   python local_kernel/kernel.py
   ```
3. Start UI:
   ```bash
   cd hello_ai_os
   flutter run -d windows
   ```

## Development

- Tests: `python -m pytest`
- Release Notes: `releases/v1.9.md`
