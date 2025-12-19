from brain.sync.sync_state import SyncState
from brain.preferences.preference_store import PreferenceStore, ImportanceLevel
from brain.memory.meaning_memory import MeaningMemory
from brain.autonomy.autonomy_ledger import AutonomyLedger, DecisionType, AutonomyDecision
import time
from brain.sync.sync_conflict import SyncConflict, ConflictResolution, ConflictType
from brain.sync.conflict_resolver import ConflictResolver
import uuid

class StateImporter:
    def __init__(self, 
                 preference_store: PreferenceStore,
                 meaning_memory: MeaningMemory,
                 ledger: AutonomyLedger,
                 resolver: ConflictResolver): # v18.1
        self.preference_store = preference_store
        self.meaning_memory = meaning_memory
        self.ledger = ledger
        self.resolver = resolver
        
    def validate_and_import(self, state: SyncState) -> bool:
        # 1. Resolve Conflicts
        conflicts = self.resolver.resolve(state)
        
        # Helper to find resolution for a domain/type
        def get_resolution(domain, ctype):
            for c in conflicts:
                if c.domain == domain and c.conflict_type == ctype:
                    return c
            return None
            
        # 2. Apply Preferences
        for domain, level_str in state.preferences.items():
            conflict = get_resolution(domain, ConflictType.PREFERENCE)
            final_level = None
            
            if conflict:
                if conflict.resolution in [ConflictResolution.REMOTE_WINS, ConflictResolution.MERGED]:
                    final_level = conflict.resolved_value
                else:
                    # LOCAL_WINS or REJECTED -> Keep local (do nothing)
                    continue
            else:
                # No conflict -> Apply Remote (New Data)
                try:
                    final_level = ImportanceLevel(level_str)
                except: continue
                
            if final_level:
                try:
                    # If it was a conflict object, resolved_value might be Enum.
                    # If new data, it's Enum.
                    self.preference_store.set_preference(domain, final_level)
                except Exception as e:
                    print(f"Error applying pref {domain}: {e}")

        # 3. Apply Meaning
        for domain, score in state.meaning_memory.items():
            conflict = get_resolution(domain, ConflictType.MEANING)
            final_score = score
            
            if conflict:
                final_score = conflict.resolved_value
                
            # Apply (whether merged, remote, or new)
            # Note: If LOCAL_WINS, resolved_value == local_value. So applying 'final_score' (local) is redundant but safe.
            # Only strictly needed if we want to avoid disk IO.
            if domain not in self.meaning_memory._meanings:
                 from brain.memory.user_meaning import UserMeaning
                 self.meaning_memory._meanings[domain] = UserMeaning(domain, final_score, 0, 0)
            else:
                 self.meaning_memory._meanings[domain].relevance_score = final_score
        
        self.meaning_memory._save()
        
        # Log Logic
        if conflicts:
            decision = AutonomyDecision(
                decision_id=str(uuid.uuid4()),
                decision_type=DecisionType.SYNC_CONFLICT_RESOLVED,
                timestamp=time.time(),
                reason=f"Resolved {len(conflicts)} conflicts",
                was_auto=True
            )
            self.ledger.append(decision)
        else:
            self.ledger.append(AutonomyDecision(
                decision_id=str(uuid.uuid4()),
                decision_type=DecisionType.SYNC_STATE_IMPORT_ATTEMPT,
                timestamp=time.time(),
                reason=f"Imported Sync State from {state.device_id} (No Conflicts)",
                was_auto=True
            ))
        
        return True
