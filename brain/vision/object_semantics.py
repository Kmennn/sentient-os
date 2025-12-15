
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

@dataclass
class SemanticProperties:
    is_fragile: bool = False
    is_heavy: bool = False
    is_container: bool = False
    temperature: str = "ambient" # ambient, hot, cold

@dataclass
class SemanticObject:
    id: str
    label: str # e.g., "cup", "laptop"
    class_type: str # e.g., "vessel", "electronics"
    position: Dict[str, float] # {x, y, z}
    orientation: Dict[str, float] = field(default_factory=lambda: {"roll": 0, "pitch": 0, "yaw": 0})
    properties: SemanticProperties = field(default_factory=SemanticProperties)

class ObjectRegistry:
    """
    Simulated Perception Layer output.
    """
    def __init__(self):
        self._objects: Dict[str, SemanticObject] = {}
        
    def update_object(self, obj: SemanticObject):
        self._objects[obj.id] = obj
        logger.debug(f"Object Updated: {obj.label} ({obj.id})")
        
    def get_object(self, obj_id: str) -> Optional[SemanticObject]:
        return self._objects.get(obj_id)
        
    def list_objects(self) -> List[SemanticObject]:
        return list(self._objects.values())

object_registry = ObjectRegistry()
