
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Optional, Set

logger = logging.getLogger(__name__)

class NodeStatus(Enum):
    PENDING = auto()
    READY = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()

@dataclass
class DAGNode:
    node_id: str
    action: str
    object_id: str
    dependencies: List[str] = field(default_factory=list)
    status: NodeStatus = NodeStatus.PENDING

class DAGRuntime:
    """
    Manages the execution of a Directed Acyclic Graph (DAG) of tasks.
    Ensures tasks only run when dependencies are satisfied.
    """
    def __init__(self):
        self.nodes: Dict[str, DAGNode] = {}
        
    def load_graph(self, nodes: List[DAGNode]):
        self.nodes = {n.node_id: n for n in nodes}
        self._update_statuses()
        
    def _update_statuses(self):
        """
        Check all PENDING nodes. If deps are COMPLETED, mark READY.
        """
        for node in self.nodes.values():
            if node.status == NodeStatus.PENDING:
                if self._are_dependencies_met(node):
                    node.status = NodeStatus.READY
                    
    def _are_dependencies_met(self, node: DAGNode) -> bool:
        for dep_id in node.dependencies:
            if dep_id not in self.nodes:
                logger.error(f"Missing dependency: {dep_id}")
                return False # Should probably fail graph
            if self.nodes[dep_id].status != NodeStatus.COMPLETED:
                return False
        return True
        
    def get_ready_nodes(self) -> List[DAGNode]:
        self._update_statuses()
        return [n for n in self.nodes.values() if n.status == NodeStatus.READY]
        
    def start_node(self, node_id: str):
        if node_id in self.nodes and self.nodes[node_id].status == NodeStatus.READY:
            self.nodes[node_id].status = NodeStatus.RUNNING
            
    def complete_node(self, node_id: str, success: bool = True):
        if node_id in self.nodes:
            self.nodes[node_id].status = NodeStatus.COMPLETED if success else NodeStatus.FAILED
            self._update_statuses()
            
    def get_progress(self) -> float:
        if not self.nodes: return 0.0
        completed = sum(1 for n in self.nodes.values() if n.status == NodeStatus.COMPLETED)
        return completed / len(self.nodes)
    
    def next_suggestion(self) -> Optional[DAGNode]:
        """
        Deterministically returns the next node to run.
        Strategy: Alphabetical ID for stability.
        """
        ready = self.get_ready_nodes()
        if not ready:
            return None
        # Sort by ID for deterministic execution
        ready.sort(key=lambda n: n.node_id)
        return ready[0]

dag_runtime = DAGRuntime()
