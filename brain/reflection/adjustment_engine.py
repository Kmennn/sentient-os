from typing import List, Dict, Optional
import time
from brain.reflection.reflection_event import ReflectionEvent, ReflectionEventType
from brain.reflection.adjustment_proposal import AdjustmentProposal, ProposalStatus
from brain.preferences.preference_store import PreferenceStore, ImportanceLevel, ExplicitPreference
from brain.autonomy.autonomy_ledger import AutonomyLedger, DecisionType, AutonomyDecision
from brain.agents.agent_context import AgentContext, AgentAction
import uuid
import time


class AdjustmentEngine:
    def __init__(self, preference_store: PreferenceStore, ledger: AutonomyLedger):
        self.preference_store = preference_store
        self.ledger = ledger
        self.active_proposals: Dict[str, AdjustmentProposal] = {} # id -> proposal
        self.last_check_timestamp: float = 0.0
        
        # ... (Mappings)
        self.importance_order = [
            ImportanceLevel.LOW,
            ImportanceLevel.MEDIUM,
            ImportanceLevel.HIGH,
            ImportanceLevel.CRITICAL
        ]
        
    # ... (Helpers)

    def scan_ledger_for_proposals(self, decisions: List[AutonomyDecision], context: AgentContext = None):
        # v17.0 Boundary Check
        if context and not context.can_perform(AgentAction.PROPOSAL_CREATE):
            self._log_violation(context, "Cannot create proposals")
            return
            
        domain_issues: Dict[str, List[str]] = {} # domain -> list of reasons
        
        for d in decisions:
            if d.decision_type == DecisionType.REFLECTION_NEGATIVE:
                # heuristic parse
                txt = d.reason or ""
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

    def _log_violation(self, context: AgentContext, msg: str):
        decision = AutonomyDecision(
            decision_id=str(uuid.uuid4()),
            decision_type=DecisionType.AGENT_BOUNDARY_VIOLATION,
            timestamp=time.time(),
            reason=f"[{context.role.value.upper()}] Violation: {msg}",
            was_auto=True
        )
        self.ledger.append(decision)
