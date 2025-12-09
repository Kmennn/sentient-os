
import logging
from typing import Dict, Any
from .worker_pool import WorkerPool

logger = logging.getLogger("supervisor")

class Supervisor:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Supervisor, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.pool = WorkerPool()
        self.metrics: Dict[str, int] = {
            "tasks_queued": 0,
            "tasks_running": 0, # Hard to track precisely without hooks
            "tasks_completed": 0,
            "tasks_failed": 0
        }

    async def start(self):
        await self.pool.start()
        
    async def stop(self):
        await self.pool.stop()

    async def submit_task(self, task_func, *args, **kwargs):
        """
        Submit a task to the pool and track metrics.
        """
        self.metrics["tasks_queued"] += 1
        
        # We need a wrapper to track completion/failure for metrics
        async def _metric_wrapper(*w_args, **w_kwargs):
            self.metrics["tasks_running"] += 1 # Approximation (increment on start)
            try:
                res = await task_func(*w_args, **w_kwargs)
                self.metrics["tasks_completed"] += 1
                return res
            except Exception as e:
                self.metrics["tasks_failed"] += 1
                raise e
            finally:
                 if self.metrics["tasks_running"] > 0:
                     self.metrics["tasks_running"] -= 1

        return await self.pool.submit(_metric_wrapper, *args, **kwargs)

    def get_metrics(self) -> str:
        """Return Prometheus text format metrics."""
        lines = []
        for k, v in self.metrics.items():
            lines.append(f"sentient_agent_{k} {v}")
        return "\n".join(lines)

supervisor = Supervisor()
