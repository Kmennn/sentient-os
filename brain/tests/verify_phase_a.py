import httpx
import time
import asyncio

URL = "http://localhost:8000/v1/agent/run"

async def test_performance():
    query = "What time is it?" # Should be TOOL intent
    
    print(f"Warmup 1: {query}")
    start = time.time()
    async with httpx.AsyncClient() as client:
        await client.post(URL, params={"query": query}, timeout=30.0)
    print(f"Warmup 1 took: {time.time() - start:.4f}s")
    
    print(f"Run 2 (Should be Cached Intent): {query}")
    start = time.time()
    async with httpx.AsyncClient() as client:
        await client.post(URL, params={"query": query}, timeout=30.0)
    print(f"Run 2 took: {time.time() - start:.4f}s")

if __name__ == "__main__":
    asyncio.run(test_performance())
