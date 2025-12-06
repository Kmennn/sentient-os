from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_mock():
    # Only runs if LLM is mocked or keys are present
    response = client.post("/v1/chat", json={"user_id": "test_user", "message": "hello"})
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 0
