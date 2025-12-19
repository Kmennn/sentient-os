import uuid
import time
from typing import List, Optional, Any
from brain.sync.sync_conflict import SyncConflict, ConflictType, ConflictResolution
from brain.sync.sync_state import SyncState
from brain.preferences.preference_store import PreferenceStore, ImportanceLevel
from brain.memory.meaning_memory import MeaningMemory

class ConflictResolver:
    def __init__(self, preference_store: PreferenceStore, meaning_memory: MeaningMemory):
        self.preference_store = preference_store
        self.meaning_memory = meaning_memory
        self.history: List[SyncConflict] = []
        
    def resolve(self, remote_state: SyncState) -> List[SyncConflict]:
        conflicts = []
        
        # 1. Resolve Preferences
        local_prefs = self.preference_store.get_all_explicit_preferences()
        for domain, rem_level_str in remote_state.preferences.items():
            try:
                rem_level = ImportanceLevel(rem_level_str)
                
                if domain in local_prefs:
                    # Conflict!
                    loc_pref = local_prefs[domain]
                    if loc_pref.importance_level != rem_level:
                        # Logic: Higher Timestamp Wins
                        # Remote Timestamp comes from sync_state.timestamp ? 
                        # Or do we assume remote is "newer" if it arrived?
                        # SyncState.timestamp is when export happened.
                        
                        resolution = ConflictResolution.LOCAL_WINS
                        res_val = loc_pref.importance_level
                        reason = "Local is newer"
                        
                        if remote_state.timestamp > loc_pref.updated_at:
                            resolution = ConflictResolution.REMOTE_WINS
                            res_val = rem_level
                            reason = "Remote is newer"
                        
                        conflicts.append(SyncConflict(
                            conflict_id=str(uuid.uuid4()),
                            domain=domain,
                            conflict_type=ConflictType.PREFERENCE,
                            local_value=loc_pref.importance_level,
                            remote_value=rem_level,
                            resolution=resolution,
                            resolved_value=res_val,
                            reason=reason
                        ))
                else:
                    # No conflict, just new. Not creating conflict object.
                    pass
            except Exception as e:
                # Malformed remote? REJECT
                pass

        # 2. Resolve Meaning (Merge)
        # Iterate REMOTE meanings
        for domain, rem_score in remote_state.meaning_memory.items():
            loc_score = self.meaning_memory.get_relevance(domain)
            # Check if local actually has data (get_relevance returns default 0.5)
            # MeaningMemory check logic:
            if domain in self.meaning_memory._meanings:
                 # Real conflict
                 if abs(loc_score - rem_score) > 0.01: # diff exists
                     merged = (loc_score + rem_score) / 2.0
                     conflicts.append(SyncConflict(
                        conflict_id=str(uuid.uuid4()),
                        domain=domain,
                        conflict_type=ConflictType.MEANING,
                        local_value=loc_score,
                        remote_value=rem_score,
                        resolution=ConflictResolution.MERGED,
                        resolved_value=merged,
                        reason=f"Weighted Avg: ({loc_score:.2f} + {rem_score:.2f})/2"
                     ))
            
        # 3. Resolve Trust (No Downgrade)
        # Trust is global (domain="GLOBAL")
        # Where is local trust?
        # In importer we assumed trusted or just imported.
        # But here we simulate trust logic.
        # We don't have easy access to "Local Trust" value via components passed (Preferences/Meaning).
        # We ignored this in `StateExporter` (hardcoded 0.5 or read from scheduler).
        # `ConflictResolver` should ideally have `current_trust`.
        # I'll enable passing `current_trust` to `resolve` method or `__init__`.
        
        self.record_history(conflicts)
        return conflicts

    def record_history(self, conflicts: List[SyncConflict]):
        self.history.extend(conflicts)
        # Keep last 100
        if len(self.history) > 100:
            self.history = self.history[-100:]
            
    def get_conflicts(self) -> List[dict]:
        return [c.to_dict() for c in self.history]
