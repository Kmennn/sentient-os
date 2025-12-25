import httpx
import asyncio
import json

async def test():
    try:
        async with httpx.AsyncClient() as client:
            print("Testing mistral:latest...")
            r = await client.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'mistral:latest',
                    'prompt': 'Say hello in one sentence',
                    'stream': False
                },
                timeout=60.0
            )
            print(f"Status: {r.status_code}")
            result = r.json()
            print(f"Response: {result.get('response', 'NO RESPONSE')}")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
