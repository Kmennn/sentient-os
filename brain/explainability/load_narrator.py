from brain.load.load_model import LoadSnapshot, LoadLevel

class LoadNarrator:
    """
    Generates non-judgmental text for load snapshots.
    """
    
    def narrate(self, snapshot: LoadSnapshot) -> str:
        date = snapshot.date_str
        density = snapshot.density_label
        
        if snapshot.level == LoadLevel.HIGH:
            return f"Observation: {date} shows {density.lower()} activity levels."
        elif snapshot.level == LoadLevel.MED:
            return f"Observation: {date} has a moderate schedule."
        else:
            return f"Observation: {date} appears relatively light."
