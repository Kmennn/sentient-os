
import httpx
import json
import asyncio
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("VERIFIER")

BASE_URL = "http://localhost:8000/v1"

async def test_tools():
    print("\n--- Testing Tools ---")
    async with httpx.AsyncClient(timeout=10.0) as client:
        # List
        resp = await client.get(f"{BASE_URL}/tools")
        print(f"List Tools: {resp.status_code}")
        if resp.status_code == 200:
            tools = resp.json().get("tools", [])
            print(f"Tools Found: {[t['name'] for t in tools]}")
            
        # Clipboard
        print("Testing Clipboard...")
        await client.post(f"{BASE_URL}/tools/run", json={"tool": "clipboard", "params": {"action": "write", "text": "VerificationText"}})
        resp = await client.post(f"{BASE_URL}/tools/run", json={"tool": "clipboard", "params": {"action": "read"}})
        print(f"Clipboard Read: {resp.json()}")

async def test_action_dedupe():
    print("\n--- Testing OS Action Dedupe ---")
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Send action 1
        await client.post(f"{BASE_URL}/action/request", json={"action": "MOUSE_MOVE", "params": {"x": 50, "y": 50}})
        # Send action 2 (immediate duplicate)
        resp2 = await client.post(f"{BASE_URL}/action/request", json={"action": "MOUSE_MOVE", "params": {"x": 50, "y": 50}})
        print(f"Duplicate Action Response: {resp2.json()}")

async def main():
    await test_tools()
    await test_action_dedupe()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
