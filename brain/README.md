# Sentient OS - Brain (v1.0)

The cognitive core of the Sentient OS. Built with FastAPI and modularized for scalability.

## Architecture

- **core/**: Business logic, configuration, and service adapters (LLM, Memory).
- **api/**: FastAPI routes and WebSocket handlers.
- **tests/**: Automated health and integration tests.

## Running the Service

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

Server listens on `http://0.0.0.0:8000`.

### Docker

```bash
docker-compose up --build
```

## API Endpoints

| Method | Path       | Description                                                                    |
| :----- | :--------- | :----------------------------------------------------------------------------- |
| `GET`  | `/health`  | System health check.                                                           |
| `POST` | `/v1/chat` | REST chat (legacy compatible). Payload: `{"user_id": "...", "message": "..."}` |
| `WS`   | `/ws`      | Real-time chat. Supports `chat` and `conversation.turn` messages.              |

## Mock Mode

To run without consuming Gemini API credits (for testing), set:

```env
MOCK_LLM=true
```

## Rollback Plan

In case of critical failure, revert to the legacy monolithic `brain_server.py` (backup pending) or checkout the `main` branch state prior to the `feat/brain-refactor` merge.
