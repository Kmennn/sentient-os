from brain.simulation.impact_comparator import ImpactReport
from brain.load.load_model import LoadLevel

class WhatIfNarrator:
    """
    Generates neutral insights about the simulated change.
    """
    
    def narrate(self, report: ImpactReport) -> str:
        parts = []
        
        # Conflict Impact
        if report.conflict_delta > 0:
            parts.append(f"This change introduces {report.conflict_delta} new conflict(s).")
        elif report.conflict_delta < 0:
            parts.append(f"This resolves {abs(report.conflict_delta)} conflict(s).")
            
        # Load Impact
        if report.level_after != report.level_before:
            direction = "increases" if report.score_after > report.score_before else "decreases"
            parts.append(f"Daily load {direction} from {report.level_before.name} to {report.level_after.name}.")
        elif report.load_score_delta != 0:
            direction = "slightly increases" if report.load_score_delta > 0 else "slightly decreases"
            parts.append(f"Load {direction}.")
        else:
            parts.append("No significant load change.")
            
        return " ".join(parts)
