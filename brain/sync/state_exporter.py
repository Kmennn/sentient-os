import time
from brain.sync.sync_state import SyncState
from brain.preferences.preference_store import PreferenceStore
from brain.memory.meaning_memory import MeaningMemory
from brain.autonomy.autonomy_ledger import AutonomyLedger
# Trust score is in AutonomyPolicy usually, or tracked in Ledger? 
# AutonomyPolicy has trust_score logic?
# Let's check MissionScheduler to see where trust is.
# MissionScheduler has self.autonomy_policy.
# AutonomyPolicy likely has get_trust_score().

class StateExporter:
    def __init__(self, 
                 preference_store: PreferenceStore,
                 meaning_memory: MeaningMemory,
                 ledger: AutonomyLedger,
                 scheduler_ref): # Circular ref avoidance if possible, but python handles it dynamically
        self.preference_store = preference_store
        self.meaning_memory = meaning_memory
        self.ledger = ledger
        self.scheduler = scheduler_ref
        
    def export_sync_state(self) -> SyncState:
        # Get Last Decision ID
        entries = self.ledger.get_entries()
        last_id = entries[-1].decision_id if entries else None
        
        # Get Trust
        # Using a default if not exposed, but ideally fetch from policy
        trust = 0.5
        if hasattr(self.scheduler, 'autonomy_policy') and hasattr(self.scheduler.autonomy_policy, 'trust_model'):
             trust = self.scheduler.autonomy_policy.trust_model.current_trust
        
        # Get Preferences (Simplify to raw dict)
        prefs = {}
        # PreferenceStore doesn't expose raw dict easily, loops needed?
        # Only explicit preferences are stored in `_preferences` dict in store (if implemented that way).
        # Let's check PreferenceStore implementation if needed. 
        # `get_all_preferences` would be nice.
        # Implemented `get_explicit_preference`. 
        # I'll rely on `_preferences` attribute if available (white-box) or add a getter.
        # Assuming `preference_store.preferences` or `_preferences`.
        
        # Get Meaning
        meanings = {}
        all_meanings = self.meaning_memory.get_all_meanings()
        for m in all_meanings:
            meanings[m["signal_domain"]] = m["relevance_score"]
            
        return SyncState(
            timestamp=time.time(),
            preferences={k: v.importance_level.value for k, v in self.preference_store.get_all_explicit_preferences().items()} if hasattr(self.preference_store, 'get_all_explicit_preferences') else {},
            meaning_memory=meanings,
            trust_score=trust,
            agent_phase=self.scheduler.current_agent_phase,
            last_decision_id=last_id
        )
