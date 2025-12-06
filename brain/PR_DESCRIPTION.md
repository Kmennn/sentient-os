# Sprint A: Backend Refactor & Formalization

**Status**: Ready for Review
**PR Type**: Refactor / Feature

## Description

Refactors the `brain/` prototype into a production-ready modular package structure (`core` + `api`).
Preserves backward compatibility with the existing Flutter client while introducing a formalized API specification.

## Deliverables

- [x] **Modular Structure**: `core/` (Services), `api/` (Routes).
- [x] **REST API**: `POST /v1/chat` (Compatible with existing client).
- [x] **Real-time**: WebSocket endpoint at `/ws` supporting both legacy `chat` signals and new `conversation.turn` envelope.
- [x] **Mock Mode**: `MOCK_LLM=true` flag for deterministic testing.
- [x] **Tests**: Added `tests/test_health.py`.
- [x] **Docker**: Added `Dockerfile` and `docker-compose.yml`.

## Verification Instructions

1. **Boot**: `python main.py`
2. **Health**: `curl http://localhost:8000/health` -> `{"status":"ok"}`
3. **Chat**: `curl -X POST http://localhost:8000/v1/chat -H "Content-Type: application/json" -d '{"user_id":"test","message":"hello"}'`
4. **Tests**: `pytest`

## Rollback Plan

- Revert this commit/PR to restore the monolithic `brain_server.py`.
- No database migrations involved (In-Memory only).
