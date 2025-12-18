from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional
import time
from brain.intents.intent import Intent
from brain.intents.temporal_intent import TemporalIntent, TimeFlexibility
from brain.intents.conflict_detector import ConflictReport

class DeferralStrategy(Enum):
    DELAY = auto()          # Push back a few minutes
    RESCHEDULE = auto()     # Move to next window or far future
    EXPIRE = auto()         # Cannot be saved
    NONE = auto()           # Not deferrable (Reject)

@dataclass
class DeferralDecision:
    strategy: DeferralStrategy
    new_start_time: Optional[float] = None
    reason: str = ""

class DeferralEngine:
    """
    Decides how to handle a conflicting intent by deferring it in time.
    """
    
    def evaluate(self, report: ConflictReport) -> DeferralDecision:
        intent = report.new_intent
        
        # Check if intent is expired already
        if intent.is_expired():
            return DeferralDecision(DeferralStrategy.EXPIRE, reason="Intent expired")
            
        # If strict timing, we probably can't delay unless window allows
        if isinstance(intent, TemporalIntent):
            if intent.flexibility == TimeFlexibility.STRICT:
                # Can we delay within window?
                # Simplify: Strict intents generally cannot be auto-deferred easily without complex solving.
                # If conflict exists NOW, and it is STRICT, it typically fails unless it can wait 1 sec?
                # For safety, Strict -> No Deferral (Reject/Expire).
                return DeferralDecision(DeferralStrategy.EXPIRE, reason="Strict timing prevents deferral")
                
            elif intent.flexibility == TimeFlexibility.FLEXIBLE:
                # Delay by fixed amount (e.g. 5 mins) or until active finishes?
                # We don't know when active finishes easily (unless we peek active intent duration).
                # Default policy: Try again in 5 minutes.
                new_time = time.time() + 300
                if intent.latest_start and new_time > intent.latest_start:
                    return DeferralDecision(DeferralStrategy.EXPIRE, reason="Deferral exceeds latest start")
                return DeferralDecision(DeferralStrategy.DELAY, new_start_time=new_time, reason="Flexible deferral")
                
        # Default non-temporal intents are assumed flexible enough to be rejected or queued.
        # But if we treat them as 'Deferrable', we can queue them.
        # Let's say default intents are NOT deferrable by this engine (Scheduler handles generic queueing).
        # This Engine is specifically for TIME based logic.
        return DeferralDecision(DeferralStrategy.NONE, reason="Not temporal intent")
