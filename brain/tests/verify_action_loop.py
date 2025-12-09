
import asyncio
import websockets
import json
import uuid

async def verify_loop():
    uri = "ws://127.0.0.1:8000/ws"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected.")
            
            # 1. Simulate "OPEN NOTEPAD" request (Optional, usually LLM triggers this)
            # But here we just want to test if CONFIRMATION triggers EXECUTION.
            
            action_id = str(uuid.uuid4())
            print(f"Simulating UI Confirmation for Action ID: {action_id}")
            
            # 2. Send "action.confirm" (Mimicking User clicking "Allow")
            confirm_msg = {
                "type": "action.confirm",
                "payload": {
                    "action_id": action_id,
                    "authorized_by": "test_script"
                }
            }
            await websocket.send(json.dumps(confirm_msg))
            
            # 3. Wait for "notification" or check if Body executed
            # Since we can't easily see Body side effects (Notepad opening) from here programmatically 
            # without complex os checks, we listen for the Brain's acknowledgment.
            
            print("Waiting for response...")
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                print(f"Received: {response}")
                data = json.loads(response)
                
                if data.get("type") == "notification" and "Executing" in data.get("content", ""):
                    print("SUCCESS: Brain accepted confirmation and triggering Body.")
                else:
                    print("WARNING: unexpected response.")
            except asyncio.TimeoutError:
                print("TIMEOUT: No confirmation response from Brain.")
                
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(verify_loop())
