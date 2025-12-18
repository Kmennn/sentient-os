from enum import StrEnum, auto

class EventType(StrEnum):
    SCHEDULER_TICK = auto()
    MISSION_QUEUED = auto()
    MISSION_STARTED = auto()
    MISSION_PREEMPTED = auto()
    MISSION_COMPLETED = auto()
    
    COPLAN_PROPOSED = auto()
    COPLAN_VOTE_REGISTERED = auto()
    COPLAN_QUORUM_MET = auto()
    
    TRUST_UPDATED = auto()
    
    CLIENT_CONNECTED = auto()
    CLIENT_DISCONNECTED = auto()
    
    STATE_SNAPSHOT_UPDATED = auto()
