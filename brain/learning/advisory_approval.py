
import logging
import uuid
from typing import Dict, List, Optional
from enum import Enum
from brain.learning.policy_advisor import AdvisorySuggestion

logger = logging.getLogger(__name__)

class AdvisoryStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class AdvisoryApprovalManager:
    """
    Manages the lifecycle of Policy Advisory suggestions.
    Ensures no suggestion is applied without explicit approval.
    """
    def __init__(self):
        self._suggestions: Dict[str, AdvisorySuggestion] = {}
        self._statuses: Dict[str, AdvisoryStatus] = {}
        
    def submit_suggestion(self, suggestion: AdvisorySuggestion) -> str:
        """
        Submits suggestion for review. Returns ID.
        """
        s_id = str(uuid.uuid4())
        self._suggestions[s_id] = suggestion
        self._statuses[s_id] = AdvisoryStatus.PENDING
        logger.info(f"Advisory Pending: {s_id} - {suggestion.parameter} {suggestion.delta}")
        return s_id
        
    def approve_suggestion(self, s_id: str) -> bool:
        if s_id in self._suggestions and self._statuses[s_id] == AdvisoryStatus.PENDING:
            self._statuses[s_id] = AdvisoryStatus.APPROVED
            logger.info(f"Advisory APPROVED: {s_id}")
            return True
        return False

    def reject_suggestion(self, s_id: str) -> bool:
        if s_id in self._suggestions:
            self._statuses[s_id] = AdvisoryStatus.REJECTED
            logger.info(f"Advisory REJECTED: {s_id}")
            return True
        return False
        
    def get_pending_suggestions(self) -> Dict[str, AdvisorySuggestion]:
        return {
            k: v for k, v in self._suggestions.items() 
            if self._statuses[k] == AdvisoryStatus.PENDING
        }
        
    def get_approved_suggestions(self) -> List[AdvisorySuggestion]:
        # Return approved suggestions that haven't been consumed yet?
        # For simplicity, returning all approved.
        return [
            self._suggestions[k] for k, v in self._statuses.items()
            if v == AdvisoryStatus.APPROVED
        ]

advisory_manager = AdvisoryApprovalManager()
