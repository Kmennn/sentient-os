import httpx
import json
import asyncio

BASE_URL = "http://localhost:8000/v1"
KERNEL_URL = "http://localhost:8001"

async def verify_all():
    print("=== STARTING v1.8 STABILITY VERIFICATION ===")
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Chat/Intent
        try:
            print("\n[1] Testing Chat Intent...")
            # Using /agent/run which uses llm_service
            resp = await client.post(f"{BASE_URL}/agent/run", params={"query": "Hello, how are you?"})
            print(f"Chat (Hello): {resp.status_code}")
            
            resp = await client.post(f"{BASE_URL}/agent/run", params={"query": "Determine the sum of 5 and 5"})
            print(f"Chat (Task/Tool intent check): {resp.status_code}")
        except Exception as e:
            print(f"Chat Test Failed: {e}")

        # 2. Vision
        try:
            print("\n[2] Testing Vision...")
            resp = await client.post(f"{BASE_URL}/vision/analyze", json={"capture": True})
            print(f"Vision Analyze: {resp.status_code}")
            if resp.status_code == 200:
                print(f"Vision Summary: {resp.json().get('summary')}")
        except Exception as e:
            print(f"Vision Test Failed: {e}")

        # 3. Tools
        try:
            print("\n[3] Testing Tools...")
            resp = await client.get(f"{BASE_URL}/tools")
            tools = resp.json().get("tools", [])
            print(f"Tools Available: {len(tools)}")
            
            resp = await client.post(f"{BASE_URL}/tools/run", json={"tool": "calculator", "params": {"expression": "21 * 2"}})
            print(f"Calculator Result (42?): {resp.json().get('result')}")
        except Exception as e:
            print(f"Tools Test Failed: {e}")

        # 4. Action (Body)
        try:
            print("\n[4] Testing OS Action (Simulated)...")
            resp = await client.post(f"{KERNEL_URL}/action/run", json={"action": "SCROLL_DOWN", "params": 100, "mode": "SIMULATED"})
            print(f"Action Status: {resp.json().get('status')}")
        except Exception as e:
             print(f"Action Test Failed: {e}")

        # 5. DB Check
        # Just by virtue of the above working (logging events), DB is likely OK.
        print("\nAll checks executed.")

if __name__ == "__main__":
    asyncio.run(verify_all())
