
import pytest
import httpx
import asyncio
import os

# Config
BRAIN_URL = "http://localhost:8000"
BODY_URL = "http://localhost:8001"

@pytest.mark.asyncio
async def test_body_screenshot_returns_bytes_and_saves_file():
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{BODY_URL}/vision/screenshot")
        assert resp.status_code == 200
        data = resp.json()
        assert "image" in data
        assert "path" in data
        
        # Verify file exists
        saved_path = data["path"]
        assert os.path.exists(saved_path), f"Screenshot not saved at {saved_path}"
        # Cleanup
        try:
            os.remove(saved_path)
        except:
            pass

@pytest.mark.asyncio
async def test_brain_vision_analyze_pipeline():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Trigger capture=True
        payload = {"capture": True}
        resp = await client.post(f"{BRAIN_URL}/v1/vision/analyze", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        
        assert "event_id" in data
        assert "ocr_text" in data
        assert "tags" in data
        assert "has_text" in data["tags"] or "screen_content" in data["tags"]

@pytest.mark.asyncio
async def test_tools_registry_datetime():
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "tool": "date_time",
            "params": {},
            "user_id": "test_user"
        }
        resp = await client.post(f"{BRAIN_URL}/v1/tools/run", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert ":" in data["result"] # Contains time-like string

@pytest.mark.asyncio
async def test_tools_registry_filesearch():
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "tool": "file_search",
            "params": {"query": "*.py"},
            "user_id": "test_user"
        }
        resp = await client.post(f"{BRAIN_URL}/v1/tools/run", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        # Should find at least this test file or others
        assert "verify_vision_tools" in str(data["result"]) or "kernel.py" in str(data["result"])
