
import logging
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

class TaskGraphRuntime:
    """
    Wraps the underlying task graph execution (e.g. from v2.9).
    Provides step-by-step control for the Mission Executor.
    """
    def __init__(self):
        # In a real impl, this would load the graph from `brain/tasks/task_graph_builder.py`
        # and use `brain/skills/skill_chain_executor.py`.
        # For v4.1 integration, we mock the graph structure but ensure the interface 
        # supports the step-wise execution required by Mission Executor.
        self._steps = [] 
        self._current_index = 0
        
    def load_graph(self, steps: List[Dict]):
        """
        Load a linear sequence of steps (simplification of DAG for this iteration).
        Each step: {'action': 'pick', 'object_id': 'cup'}
        """
        self._steps = steps
        self._current_index = 0
        
    def next_step(self) -> Optional[Dict]:
        """
        Returns the next step to execute, or None if done.
        """
        if self._current_index >= len(self._steps):
            return None
            
        step = self._steps[self._current_index]
        self._current_index += 1
        return step
        
    def get_progress(self) -> float:
        if not self._steps:
            return 0.0
        return self._current_index / len(self._steps)
        
    @property
    def current_step_index(self):
        return self._current_index
        
    def set_step_index(self, index: int):
        self._current_index = index

task_graph_runtime = TaskGraphRuntime()
