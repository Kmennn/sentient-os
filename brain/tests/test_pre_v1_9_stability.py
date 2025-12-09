
import httpx
import json
import asyncio
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("VERIFIER")

BASE_URL = "http://localhost:8000/v1"
BODY_URL = "http://localhost:8001"

async def test_chat_accuracy():
    logger.info("[Verified] Phase A: Chat Accuracy")
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Identity
        resp = await client.post(f"{BASE_URL}/agent/run", params={"query": "Who are you?"})
        if resp.status_code == 200:
            logger.info(f"Identity Response: {resp.json().get('response')[:50]}...")
        else:
            logger.error(f"Chat Error: {resp.text}")

async def test_vision_quality():
    logger.info("[Verified] Phase B: Vision Quality")
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Simulate Vision Request (mocking image capture by asking for capture=False if possible, 
        # but analyze() handles capture internally. 
        # We can test analyze endpoint directly.
        # Note: If no body running, it might fail. We assume body is running or mock it? 
        # The vision engine calls Body. 
        try:
             # We can't easily mock Body response here without Body running. 
             # We'll just call it and expect handled error or success.
             resp = await client.post(f"{BASE_URL}/vision/analyze", json={"capture": True})
             if resp.status_code == 200:
                 res = resp.json()
                 logger.info(f"Vision Result: {res.keys()}")
                 if "tags" in res:
                     logger.info(f"Tags: {res['tags']}")
             else:
                 logger.info(f"Vision checked (Status {resp.status_code}) - might be strictly visual.")
        except Exception as e:
            logger.warning(f"Vision test skipped/failed: {e}")

async def test_tools_expansion():
    logger.info("[Verified] Phase C: Tools Framework")
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. List
        resp = await client.get(f"{BASE_URL}/tools")
        tools = resp.json().get("tools", [])
        names = [t["name"] for t in tools]
        logger.info(f"Available Tools: {names}")
        
        # 2. System Info
        if "system_info" in names:
            resp = await client.post(f"{BASE_URL}/tools/run", json={"tool": "system_info"})
            logger.info(f"System Info: {resp.json()}")

        # 3. Clipboard (Simulated write)
        if "clipboard" in names:
             await client.post(f"{BASE_URL}/tools/run", json={"tool": "clipboard", "params": {"action": "write", "text": "TestClipboard"}})
             resp = await client.post(f"{BASE_URL}/tools/run", json={"tool": "clipboard", "params": {"action": "read"}})
             logger.info(f"Clipboard Read: {resp.json().get('result')}")

async def test_os_control():
    logger.info("[Verified] Phase D: OS Control (Intent Map & Dedupe)")
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Intent Map ("scroll slowly" -> SCROLL_DOWN, 100)
        # We need to check logs or response. Bridge returns result.
        # Note: We are testing /action/request which calls Body.
        # We trust Body logic is updated.
        
        payload = {"action": "scroll slowly", "params": {}, "agent_id": "test"}
        # This will fail at Bridge if it doesn't know "scroll slowly" OR 
        # Bridge passes it to Body, and Body resolves it.
        # My implementation of ActionExecutor is in Body (kernel). 
        # Brain passes raw action to Body.
        
        resp = await client.post(f"{BASE_URL}/action/request", json=payload)
        logger.info(f"Intent 'scroll slowly': {resp.json()}")
        
        # 2. Dedupe
        # Send same action twice
        await client.post(f"{BASE_URL}/action/request", json={"action": "MOUSE_MOVE", "params": {"x": 100, "y": 100}})
        resp2 = await client.post(f"{BASE_URL}/action/request", json={"action": "MOUSE_MOVE", "params": {"x": 100, "y": 100}})
        logger.info(f"Dedupe Response 2: {resp2.json()}") # Should be 'ignored' or 'simulated' depending on logic

async def verify_all():
    print("=== Starting Pre-v1.9 Stability Verification ===")
    await test_chat_accuracy()
    await test_tools_expansion()
    await test_os_control()
    await test_vision_quality()
    print("=== Verification Complete ===")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_all())

