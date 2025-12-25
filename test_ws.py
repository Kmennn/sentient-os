import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://127.0.0.1:8000/ws"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            # Send a ping
            await websocket.send(json.dumps({"type": "status.ping"}))
            print("Sent ping")
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"Received: {response}")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test_ws())
