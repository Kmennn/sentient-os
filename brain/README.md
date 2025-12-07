# Sentient OS - Brain (v1.6 Offline)

The cognitive core of the Sentient OS. Updated for **Full Offline Mode** using local inference (Ollama, SentenceTransformer, Tesseract).

## Architecture

- **core/**: Business logic, configuration, and `LocalModelEngine`.
- **api/**: FastAPI routes and WebSocket handlers.
- **tests/**: Automated health and integration tests.

## Prerequisites

Before running, ensure you have the following installed:

1.  **Ollama** (Local LLM)
    - Download from [ollama.com](https://ollama.com).

```

## API Endpoints

| Method | Path                  | Description                                |
| :----- | :-------------------- | :----------------------------------------- |
| `GET`  | `/local-intelligence` | Returns local model status & memory usage. |
| `GET`  | `/health`             | System health check.                       |
| `POST` | `/v1/chat`            | REST chat.                                 |
| `WS`   | `/ws`                 | Real-time chat.                            |

## Rollback

To revert to cloud-dependency mode, checkout the `main` branch tag `v1.5`.
```
