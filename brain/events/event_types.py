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
    
    ACTION_CONFIRMATION_REQUEST = auto()
    
    CLIENT_CONNECTED = auto()
    CLIENT_DISCONNECTED = auto()
    
    STATE_SNAPSHOT_UPDATED = auto()
    
    # P3.2: Scheduler Stall Detection (edge-triggered)
    SCHEDULER_STALL_DETECTED = auto()
    SCHEDULER_STALL_CLEARED = auto()
    
    # P3.3: Resource Leak Detection (edge-triggered)
    RESOURCE_LEAK_SUSPECTED = auto()
    RESOURCE_LEAK_CLEARED = auto()

    # P3.5: Cold Start
    LLM_COLD_START = "llm.cold_start"
