
import asyncio
import websockets
import argparse
import sys
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_voice_stream(uri):
    logger.info(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected successfully.")
            
            # 1. Send Control Message
            msg = {"type": "control", "text": "ping"}
            await websocket.send(json.dumps({"text": json.dumps(msg)}))
            logger.info("Sent control ping.")
            
            # 2. Send Dummy Audio (Silence)
            # Create 1 second of silence (16kHz, 16-bit mono = 32000 bytes)
            silence = b'\x00' * 32000
            await websocket.send(silence)
            logger.info("Sent 1s of audio silence.")
            
            # 3. Wait for response (optional)
            # await asyncio.sleep(1)
            
            logger.info("Smoke test passed: Connection and Send OK.")
            return True
            
    except Exception as e:
        logger.error(f"Smoke test failed: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voice Stream Smoke Test")
    parser.add_argument("--ws", default="ws://localhost:8000/v1/voice/stream", help="WebSocket URI")
    args = parser.parse_args()
    
    success = asyncio.run(test_voice_stream(args.ws))
    sys.exit(0 if success else 1)
