
import logging
from typing import List, Dict
from dataclasses import asdict, dataclass
from brain.skills.demonstration_recorder import DemoPoint

logger = logging.getLogger(__name__)

@dataclass
class SkillData:
    name: str
    points: List[Dict[str, float]] # Normalized points
    metadata: Dict[str, float] # stats

class SkillAbstraction:
    """
    Converts raw demonstration into reusable skill.
    """
    def abstract(self, raw_points: List[DemoPoint], name: str = "skill_01") -> SkillData:
        if not raw_points:
            return SkillData(name, [], {})
            
        start_pt = raw_points[0]
        
        # 1. Normalize (Relative to Start)
        normalized = []
        max_speed = 0.0
        
        for i, pt in enumerate(raw_points):
            # Calc relative pose
            rel_x = pt.x - start_pt.x
            rel_y = pt.y - start_pt.y
            rel_z = pt.z - start_pt.z
            
            normalized.append({
                "t": pt.timestamp - start_pt.timestamp,
                "x": rel_x,
                "y": rel_y,
                "z": rel_z
            })
            
            # Simple speed check (stats)
            if i > 0:
                dt = pt.timestamp - raw_points[i-1].timestamp
                if dt > 0:
                    dist = ((pt.x - raw_points[i-1].x)**2 + (pt.y - raw_points[i-1].y)**2 + (pt.z - raw_points[i-1].z)**2)**0.5
                    speed = dist / dt
                    if speed > max_speed:
                        max_speed = speed

        # 2. Keyframe Simplification (Douglas-Peucker would go here)
        # For now, just decimate (keep every Nth point to reduce size)
        simplified = normalized[::2] # Keep 50%
        if normalized and simplified[-1] != normalized[-1]:
            simplified.append(normalized[-1])

        # 3. Stats
        metadata = {
            "duration": normalized[-1]["t"],
            "max_speed": max_speed,
            "point_count": len(simplified)
        }
        
        logger.info(f"Skill '{name}' abstracted. {len(simplified)} points.")
        return SkillData(name, simplified, metadata)

skill_abstraction = SkillAbstraction()
