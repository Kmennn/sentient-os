
import asyncio
import logging
import os
from typing import Callable, Any, Coroutine, Dict

logger = logging.getLogger("worker_pool")

class WorkerPool:
    def __init__(self, size: int = 4):
        self._size = size
        self._queue = asyncio.Queue()
        self._workers = []
        self._running = False
        
        # Load config override
        env_size = os.getenv("AGENT_POOL_SIZE")
        if env_size:
            try:
                self._size = int(env_size)
            except ValueError:
                logger.warning(f"Invalid AGENT_POOL_SIZE {env_size}, using default {size}")

    async def start(self):
        """Start worker tasks."""
        if self._running:
            return
        self._running = True
        self._workers = [asyncio.create_task(self._worker_loop(i)) for i in range(self._size)]
        logger.info(f"WorkerPool started with {self._size} workers.")

    async def stop(self):
        """Stop all workers."""
        self._running = False
        # Send None to stop each worker
        for _ in range(self._size):
            await self._queue.put(None)
        
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers = []
        logger.info("WorkerPool stopped.")

    async def submit(self, task_func: Callable[..., Coroutine], *args, **kwargs) -> asyncio.Future:
        """
        Submit a task to the pool. Returns a Future that will hold the result.
        """
        if not self._running:
            logger.warning("WorkerPool not running, starting automatically.")
            await self.start()
            
        future = asyncio.get_running_loop().create_future()
        
        # Wrap task to set the future result
        wrapped_task = (task_func, args, kwargs, future)
        await self._queue.put(wrapped_task)
        return future

    async def _worker_loop(self, worker_id: int):
        logger.debug(f"Worker {worker_id} started.")
        while self._running:
            try:
                item = await self._queue.get()
                if item is None:
                    self._queue.task_done()
                    break
                
                func, args, kwargs, future = item
                
                try:
                    # Execute
                    result = await func(*args, **kwargs)
                    if not future.done():
                        future.set_result(result)
                except Exception as e:
                    logger.error(f"Worker {worker_id} task failed: {e}")
                    if not future.done():
                        future.set_exception(e)
                finally:
                    self._queue.task_done()
                    
            except Exception as e:
                logger.error(f"Worker {worker_id} logic error: {e}")
                
        logger.debug(f"Worker {worker_id} stopped.")
