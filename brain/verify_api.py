
import httpx
import asyncio
import sys

async def verify():
    print("Testing Brain API connection...")
    try:
        async with httpx.AsyncClient() as client:
            # 1. Ping
            print("Pinging Brain...")
            try:
                pong = await client.get("http://127.0.0.1:8000/ping", timeout=5)
                print(f"Ping Status: {pong.status_code}")
            except Exception as e:
                print(f"Ping Failed: {e}")
                return

            # 2. Agent Run
            print("Testing Agent Endpoint...")
            resp = await client.post(
                "http://127.0.0.1:8000/v1/agent/run?query=hello", 
                timeout=60
            )
            print(f"Status Code: {resp.status_code}")
            print(f"Response: {resp.text}")
            
            if resp.status_code == 200:
                print("SUCCESS: Brain responded.")
            else:
                print("FAILURE: Brain returned error code.")
    except Exception as e:
        print(f"ERROR: Failed to connect to Brain: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
