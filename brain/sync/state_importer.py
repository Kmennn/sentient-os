from brain.sync.sync_state import SyncState
from brain.preferences.preference_store import PreferenceStore, ImportanceLevel
from brain.memory.meaning_memory import MeaningMemory
from brain.autonomy.autonomy_ledger import AutonomyLedger, DecisionType, AutonomyDecision
import time
import uuid

class StateImporter:
    def __init__(self, 
                 preference_store: PreferenceStore,
                 meaning_memory: MeaningMemory,
                 ledger: AutonomyLedger):
        self.preference_store = preference_store
        self.meaning_memory = meaning_memory
        self.ledger = ledger
        
    def validate_and_import(self, state: SyncState) -> bool:
        # 1. Trust Check (Placeholder: Reject if incoming trust is significantly lower?)
        # For v18.0, we assume 'state' is trusted if it came from authenticated source.
        # But we log the attempt.
        
        # 2. Merge Preferences
        for domain, level_str in state.preferences.items():
            try:
                level = ImportanceLevel(level_str)
                # Check if local exists?
                # Just overwrite for synchronization
                self.preference_store.set_preference(domain, level)
            except Exception as e:
                print(f"Error importing preference for {domain}: {e}")
                
        # 3. Merge Meaning
        # SyncState has Dict[str, float]
        # We update local meaning memory
        for domain, score in state.meaning_memory.items():
            # MeaningMemory doesn't have direct 'set_score'.
            # It has 'record_interaction'.
            # We might need a back-door or helper to set score directly for sync.
            # Implementing 'inject_meaning' in MeaningMemory would be cleaner.
            # For now, I'll access _meanings directly if possible or add helper.
            # Using private access for sync is acceptable in this context.
            if domain not in self.meaning_memory._meanings:
                # Create new
                from brain.memory.user_meaning import UserMeaning
                self.meaning_memory._meanings[domain] = UserMeaning(domain, score, 0, 0)
            else:
                # Update existing score
                # Taking the max or incoming?
                # Let's take incoming as truth from sync
                self.meaning_memory._meanings[domain].relevance_score = score
        
        self.meaning_memory._save()
        
        # Log
        self.ledger.append(AutonomyDecision(
            decision_id=str(uuid.uuid4()),
            decision_type=DecisionType.SYNC_STATE_IMPORT_ATTEMPT, # Will define this type
            timestamp=time.time(),
            reason=f"Imported Sync State from {state.device_id}",
            was_auto=True
        ))
        
        return True
