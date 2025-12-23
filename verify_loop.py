
import asyncio
import websockets
import json
import requests
import sys

BRAIN_URL = "http://localhost:8000"
BODY_URL = "http://localhost:8001"
WS_URL = "ws://localhost:8000/ws"

async def verify_loop():
    print("--- Verifying End-to-End Loop ---")
    print("Waiting 5s for Browser to be ready...")
    import time
    time.sleep(5)
    
    # Retry Helper
    def wait_for_connection(url, name, retries=10, delay=2):
        for i in range(retries):
            try:
                requests.get(f"{url}/docs", timeout=5) # Simple check
                print(f"Connected to {name}.")
                return True
            except:
                print(f"Waiting for {name}... ({i+1}/{retries})")
                time.sleep(delay)
        return False

    if not wait_for_connection(BODY_URL, "Body"):
        print("Body unreachable.")
        return False
        
    if not wait_for_connection(BRAIN_URL, "Brain"):
        print("Brain unreachable.")
        return False

    # 0a. Enable Body Actions
    try:
        requests.post(f"{BODY_URL}/admin/toggle-actions?enable=true")
        print("Body Actions Enabled.")
    except Exception as e:
        print(f"Warning: Failed to toggle body actions: {e}")

    # 0b. Set Mode to REAL (Autonomy)
    try:
        requests.post(f"{BRAIN_URL}/system/mode", json={"mode": "REAL"})
        print("Autonomy Mode set to REAL.")
    except Exception as e:
        print(f"Failed to set mode: {e}")
        return False

    async with websockets.connect(WS_URL) as websocket:
        print("Connected to WebSocket.")
        
        # 1. Trigger Task via API
        # We use /agent/run to simulate a user asking "Scroll down"
        # This triggers LLMService -> TaskAgent -> Plan -> Step Trigger (Confirmation Request)
        
        # Concurrency Fix: Start listening BEFORE triggering
        
        # Shared state for result
        loop_result = {"success": False}
        
        async def listen_for_confirmation():
            print("Listener started...")
            action_id = None
            try:
                while True:
                    # Short timeout to allow check for cancellation or success 
                    try:
                         # We use a shorter recv timeout to check success flag occasionally if needed,
                         # but here we just wait.
                         message = await asyncio.wait_for(websocket.recv(), timeout=30.0) 
                    except asyncio.TimeoutError:
                        print("Timeout waiting for WS message.")
                        return

                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    if msg_type == "action.confirmation":
                        payload = data.get("payload", {})
                        action_id = payload.get("action_id")
                        intent = payload.get("intent")
                        print(f"Received Confirmation Request: {intent} (ID: {action_id})")
                        
                        # 3. Send Confirmation
                        print(f"Confirming Action {action_id}...")
                        confirm_msg = {
                            "type": "action.confirm",
                            "payload": {"action_id": action_id}
                        }
                        await websocket.send(json.dumps(confirm_msg))
                        
                    elif msg_type == "notification":
                        content = data.get("content", "")
                        print(f"Notification: {content}")
                        if "Status: Executed" in content:
                            print("SUCCESS: Loop Verified.")
                            loop_result["success"] = True
                            return
                            
            except Exception as e:
                print(f"Listener error: {e}")

        async def trigger_task():
            # Wait a bit for listener to be ready
            await asyncio.sleep(2)
            print(f"Sending Task Query: '{task_query}'...")
            try:
                # Use to_thread to avoid blocking async loop with sync requests
                resp = await asyncio.to_thread(requests.post, f"{BRAIN_URL}/agent/run", params={"query": task_query})
                print(f"Agent Response: {resp.text}")
            except Exception as e:
                print(f"Trigger failed: {e}")

        task_query = "Scroll down"
        
        # Run both
        listener_task = asyncio.create_task(listen_for_confirmation())
        trigger_task = asyncio.create_task(trigger_task())
        
        # Wait for listener to complete (success or timeout) or trigger to fail
        done, pending = await asyncio.wait([listener_task, trigger_task], return_when=asyncio.FIRST_COMPLETED)
        
        # If listener finished, check result
        if loop_result["success"]:
            return True
        
        # If we are here, maybe listener timed out?
        # Give it a bit more time if trigger just finished?
        # Actually trigger finishes quickly. Listener is the main one.
        if listener_task in pending:
             print("Trigger done, waiting for confirmation...")
             try:
                 await asyncio.wait_for(listener_task, timeout=10.0)
             except:
                 pass
                 
        if loop_result["success"]:
            return True
            
        print("Loop Verification Failed.")
        return False

    return False

if __name__ == "__main__":
    try:
        if asyncio.run(verify_loop()):
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)
