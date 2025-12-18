from brain.coplanning.shared_consent_manager import SharedConsentManager
from brain.governance.delegation_policy import DelegationPolicy, DelegationScope
from brain.auth.delegation_limits import DelegationLimits
from brain.monitoring.delegation_risk_monitor import DelegationRiskMonitor
from brain.governance.delegation_escalation_policy import DelegationEscalationPolicy, ApprovalStatus
from brain.audit.mission_audit import mission_audit

class GovernanceService:
    def __init__(self):
        self.shared_consent_manager = SharedConsentManager()
        self.delegation_policy = DelegationPolicy()
        self.limits = DelegationLimits()
        self.risk_monitor = DelegationRiskMonitor()
        self.escalation_policy = DelegationEscalationPolicy(self.limits, self.risk_monitor)
        self.mission_audit = mission_audit

    def check_vote_authority(self, proposal, user_id, approved):
        # Implementation of register_coplan_vote logic
        if not hasattr(proposal, "required_approvers"):
            return

        covered_approvers = []
        for approaching_target in proposal.required_approvers:
             if self.delegation_policy.check_authority(user_id, approaching_target):
                 # Safety Checks
                 active_dels = self.delegation_policy.get_active_delegations(approaching_target)
                 relevant_del = next((d for d in active_dels if d.delegate_user_id == user_id), None)
                 
                 if relevant_del:
                     status = self.escalation_policy.evaluate_delegation_usage(relevant_del, self.delegation_policy.delegations)
                     if status != ApprovalStatus.ALLOWED:
                         self.mission_audit.log_delegation_blocked(proposal.proposal_id, user_id, str(status))
                         continue 
                         
                 covered_approvers.append(approaching_target)
        
        if not covered_approvers:
            return

        for target in covered_approvers:
            self.shared_consent_manager.register_vote(proposal, target, approved)
            if target != user_id:
                 self.mission_audit.log_delegation_used(proposal.proposal_id, user_id, target)
                 
        self.mission_audit.log_shared_vote(proposal.proposal_id, user_id, approved)

    def check_quorum(self, proposal):
        if hasattr(proposal, "required_approvers") and proposal.required_approvers:
             return self.shared_consent_manager.check_quorum(proposal)
        return True
