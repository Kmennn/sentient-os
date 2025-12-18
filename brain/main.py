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

def run_scheduler_tick():
    """Blocking loop for scheduler ticking"""
    try:
        while True:
            # We must be careful if EventBus emission calls Async code from Sync context.
            # Ideally scheduler should be async too or EventBus uses call_soon_threadsafe if loop exists.
            # But here we are in a Thread.
            # For v7.1 MVP: Simple Loop.
            
            action = mission_scheduler.tick()
            if action:
                logger.info(f"Tick Action: {action}")
            import time
            time.sleep(1.0)
    except Exception as e:
        logger.error(f"Scheduler Loop Crash: {e}")

def main():
    logger.info("Initializing Headless Brain v7.1 (w/ Stream)...")
    
    # Start Scheduler in separate thread so it doesn't block API
    scheduler_thread = threading.Thread(target=run_scheduler_tick, daemon=True)
    scheduler_thread.start()
    
    logger.info("Starting Stream API on 0.0.0.0:8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")

if __name__ == "__main__":
    main()
