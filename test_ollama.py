import httpx
import asyncio

async def test_ollama():
    try:
        print("Testing Ollama connection...")
        async with httpx.AsyncClient() as client:
            # Test 1: Check if Ollama is responding
            response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
            print(f"Status: {response.status_code}")
            print(f"Models: {response.text[:200]}")
            
            # Test 2: Try generating
            print("\nTesting generation...")
            gen_response = await client.post(
                "http://localhost:11434/api/generate",
                json={"model": "mistral", "prompt": "Say hello", "stream": False},
                timeout=30.0
            )
            print(f"Generation status: {gen_response.status_code}")
            print(f"Response: {gen_response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test_ollama())
