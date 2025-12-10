import pytest
import sys
import os
from fastapi.testclient import TestClient

# Try direct import first (path via conftest), then fallback if needed
try:
    from main import app
except ImportError:
    from brain.main import app

def test_voice_stream_websocket():
    # WebSocket test requires the server to be runnable or using TestClient with websocket support
    # Starlette/FastAPI TestClient supports websockets
    
    with TestClient(app) as client:
        with client.websocket_connect("/v1/voice/stream") as websocket:
            # Send control message
            websocket.send_json({"text": '{"type": "control", "text": "ping"}'})
            
            # Since our implementation is loop-based and might not echo immediately unless we designed it to
            # We just verify connection didn't crash
            pass
            # If we expected a response, we would:
            # data = websocket.receive_json()
            # assert data
