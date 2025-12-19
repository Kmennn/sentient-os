from typing import List, Dict, Optional
import time
from brain.reflection.reflection_event import ReflectionEvent, ReflectionEventType
from brain.reflection.adjustment_proposal import AdjustmentProposal, ProposalStatus
from brain.preferences.preference_store import PreferenceStore, ImportanceLevel, ExplicitPreference
from brain.autonomy.autonomy_ledger import AutonomyLedger, DecisionType, AutonomyDecision
import uuid

class AdjustmentEngine:
    def __init__(self, preference_store: PreferenceStore, ledger: AutonomyLedger):
        self.preference_store = preference_store
        self.ledger = ledger
        self.active_proposals: Dict[str, AdjustmentProposal] = {} # id -> proposal
        self.last_check_timestamp: float = 0.0
        
        # Mapping for Importance Progression
        self.importance_order = [
            ImportanceLevel.LOW,
            ImportanceLevel.MEDIUM,
            ImportanceLevel.HIGH,
            ImportanceLevel.CRITICAL
        ]

    def _get_next_higher(self, level: ImportanceLevel) -> Optional[ImportanceLevel]:
        try:
            idx = self.importance_order.index(level)
            if idx < len(self.importance_order) - 1:
                return self.importance_order[idx + 1]
        except ValueError:
            pass
        return None

    def _get_next_lower(self, level: ImportanceLevel) -> Optional[ImportanceLevel]:
        try:
            idx = self.importance_order.index(level)
            if idx > 0:
                return self.importance_order[idx - 1]
        except ValueError:
            pass
        return None

    def evaluate_adjustments(self, reflections: List[AutonomyDecision]):
        """
        Scans recent reflections (from Ledger decisions) to find patterns.
        """
        # Group Negatives by Domain
        # We look at AutonomyDecisions where decision_type is REFLECTION_NEGATIVE
        # And timestamp > something? Or just all relevant ones not yet acted upon?
        # For simplicity v1: Look back at last N reflections or based on time.
        # Ideally we track which reflections contributed to a proposal so we don't reuse them.
        
        # Simple heuristic: Count negatives in the last batch passed in.
        domain_negatives: Dict[str, List[AutonomyDecision]] = {}
        
        for r in reflections:
            if r.decision_type == DecisionType.REFLECTION_NEGATIVE:
                # Extract domain from reason? Or we need domain to be stored better.
                # ReflectionEngine logs: f"[{TYPE}] {domain}: {reason}" in insights.
                # Ledger entries have `reason` field: "Over-filtered? User searched for 'SYSTEM'..."
                # Extracting domain from text is brittle.
                # Note: `ReflectionEngine` logged decision. But `AutonomyDecision` struct doesn't have `domain` field explicitly.
                # It has `reason`.
                # Wait, `ReflectionEvent` has `domain`.
                # But `AdjustmentEngine` consumes `AutonomyDecision` from Ledger? Or `ReflectionEvent` from buffer?
                # The prompt says "Turn Reflection data into...".
                # Providing `ReflectionEvent` buffer is better since it has structured domain.
                pass
        pass
        
    def evaluate_reflection_events(self, events: List[ReflectionEvent]):
        """
        Evaluates structured reflection events.
        """
        # 1. Group by Domain
        negatives_by_domain: Dict[str, List[ReflectionEvent]] = {}
        
        for e in events:
            # We assume events passed are from the buffer (so recent)
            # We need to map EventType to meaning.
            # But the "Negative" judgment came from ReflectionEngine logic (Rule 1 & 2).
            # ReflectionEvents are inputs processing.
            # `ReflectionEngine` generates Insights (strings) and Ledger Entries.
            # It DOES NOT emit a "Processed Reflection Event" structure back.
            # It just logs to Ledger.
            
            # Re-evaluating: `AdjustmentEngine` should perhaps process the *output* of `ReflectionEngine`.
            # Ledger decisions `REFLECTION_NEGATIVE` are the output.
            # Issue: Ledger decision lacks `domain` field.
            # I should add `domain` to `AutonomyDecision`? Or parse `reason`.
            # Parsing `reason` is okay for now if format is consistent.
            # "Over-filtered? User searched for '{domain}'..."
            # "Over-noise? User dismissed '{domain}'..."
            pass
            
            # Alternative: `ReflectionEngine` can expose a structured history or pass data to AdjustmentEngine.
            # Or `ReflectionEngine` can call `AdjustmentEngine` directly when it detects negative.
            # But "MissionScheduler: Runs AdjustmentEngine on tick".
            # So it's polling.
            
            # Let's parse Ledger decisions for now, or just look at `ReflectionEngine`'s buffer if we can infer "Negative".
            # `ReflectionEngine` determines Negative. Re-implementing logic here is bad.
            # I will Parse Ledger Decisions.
            
            # Better: Update `AutonomyDecision` to include `metadata` dict?
            # It has `action_id`? `suggestion_id`? 
            # It has `reason`.
            pass

    def scan_ledger_for_proposals(self, decisions: List[AutonomyDecision]):
        domain_issues: Dict[str, List[str]] = {} # domain -> list of reasons
        
        for d in decisions:
            if d.decision_type == DecisionType.REFLECTION_NEGATIVE:
                # heuristic parse
                txt = d.reason
                # Msg format: "Over-filtered? User searched for '{domain}'..."
                # Msg format: "Over-noise? User dismissed '{domain}'..."
                
                # Check Over-filter
                if "Over-filtered" in txt and "'" in txt:
                    parts = txt.split("'")
                    if len(parts) >= 2:
                        domain = parts[1]
                        if domain not in domain_issues: domain_issues[domain] = []
                        domain_issues[domain].append("over_filtered")
                        
                # Check Over-noise
                elif "Over-noise" in txt and "'" in txt:
                    parts = txt.split("'")
                    if len(parts) >= 2:
                        domain = parts[1]
                        if domain not in domain_issues: domain_issues[domain] = []
                        domain_issues[domain].append("over_noise")
                        
        # Check Threshold
        for domain, issues in domain_issues.items():
            if len(issues) >= 3:
                # Check if already pending
                if any(p.domain == domain and p.status == ProposalStatus.PENDING for p in self.active_proposals.values()):
                    continue
                    
                # Determine Consensus
                # If mostly over_filtered -> Increase
                # If mostly over_noise -> Decrease
                filtered_count = issues.count("over_filtered")
                noise_count = issues.count("over_noise")
                
                current_pref = self.preference_store.get_effective_preference(domain)
                curr_level_str = current_pref.get("level", "medium")
                try:
                    curr_level = ImportanceLevel(curr_level_str)
                except:
                    curr_level = ImportanceLevel.MEDIUM
                
                proposed_level = None
                reason = ""
                
                if filtered_count > noise_count:
                    # Need Increase
                    proposed_level = self._get_next_higher(curr_level)
                    reason = f"System alerts for {domain} appear over-filtered ({filtered_count} detections)."
                elif noise_count > filtered_count:
                    # Need Decrease
                    proposed_level = self._get_next_lower(curr_level)
                    reason = f"System alerts for {domain} appear too noisy ({noise_count} detections)."
                    
                if proposed_level and proposed_level != curr_level:
                    # Create Proposal
                    prop = AdjustmentProposal(
                        domain=domain,
                        current_importance=curr_level,
                        proposed_importance=proposed_level,
                        reason=reason,
                        confidence=0.8,
                        source_reflection_ids=[] # Todo: link ids
                    )
                    self.active_proposals[prop.proposal_id] = prop
                    
                    # Log
                    decision = AutonomyDecision(
                        decision_id=str(uuid.uuid4()),
                        decision_type=DecisionType.ADJUSTMENT_PROPOSED,
                        timestamp=time.time(),
                        reason=f"{domain}: {curr_level.value} -> {proposed_level.value}",
                        was_auto=True
                    )
                    self.ledger.append(decision)
                    
    def approve_proposal(self, proposal_id: str):
        if proposal_id in self.active_proposals:
            p = self.active_proposals[proposal_id]
            if p.status == ProposalStatus.PENDING:
                p.status = ProposalStatus.APPROVED
                # Apply
                self.preference_store.set_preference(p.domain, p.proposed_importance)
                # Log
                decision = AutonomyDecision(
                    decision_id=str(uuid.uuid4()),
                    decision_type=DecisionType.ADJUSTMENT_APPROVED,
                    timestamp=time.time(),
                    reason=f"{p.domain} updated to {p.proposed_importance.value}",
                    was_auto=False
                )
                self.ledger.append(decision)
                
    def reject_proposal(self, proposal_id: str):
         if proposal_id in self.active_proposals:
            p = self.active_proposals[proposal_id]
            if p.status == ProposalStatus.PENDING:
                p.status = ProposalStatus.REJECTED
                # Log
                decision = AutonomyDecision(
                    decision_id=str(uuid.uuid4()),
                    decision_type=DecisionType.ADJUSTMENT_REJECTED,
                    timestamp=time.time(),
                    reason=f"Proposal for {p.domain} rejected",
                    was_auto=False
                )
                self.ledger.append(decision)
