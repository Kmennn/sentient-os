import logging
import sys
import os
import asyncio
import threading
import uvicorn

# Ensure brain can be imported
sys.path.append(os.getcwd())

from brain.missions.mission_scheduler import mission_scheduler
from brain.api.stream import app

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HeadlessBrain")

@app.on_event("startup")
async def start_scheduler():
    asyncio.create_task(run_scheduler_loop())

async def run_scheduler_loop():
    """Async loop for scheduler ticking"""
    logger.info("Scheduler Loop Started (Async)")
    try:
        while True:
            # Run tick synchronously. 
            # Note: This blocks the event loop for the duration of a tick.
            # Ideally tick() should be fast.
            # HACK: If tick is slow, API latencies increase. 
            # But this fixes 'No Loop' event bus errors.
            action = mission_scheduler.tick()
            if action:
                logger.info(f"Tick Action: {action}")
            
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.error(f"Scheduler Loop Crash: {e}")

def main():
    logger.info("Initializing Headless Brain v7.1 (w/ Stream)...")
    logger.info("Starting Stream API on 0.0.0.0:8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")

if __name__ == "__main__":
    main()
