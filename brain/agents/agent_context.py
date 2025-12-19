from dataclasses import dataclass, field
from typing import List
from brain.agents.agent_role import AgentRole

class AgentAction(str):
    SIGNAL_DETECT = "signal_detect"
    REFLECTION_GENERATE = "reflection_generate"
    PROPOSAL_CREATE = "proposal_create"
    PREFERENCE_MUTATE = "preference_mutate"

@dataclass
class AgentContext:
    role: AgentRole
    allowed_actions: List[str]
    name: str = "Agent"
    
    def can_perform(self, action: str) -> bool:
        return action in self.allowed_actions

# Predefined Contexts
OBSERVER_CONTEXT = AgentContext(
    role=AgentRole.OBSERVER,
    allowed_actions=[AgentAction.SIGNAL_DETECT],
    name="Observer"
)

ANALYST_CONTEXT = AgentContext(
    role=AgentRole.ANALYST,
    allowed_actions=[AgentAction.REFLECTION_GENERATE],
    name="Analyst"
)

GOVERNOR_CONTEXT = AgentContext(
    role=AgentRole.GOVERNOR,
    allowed_actions=[AgentAction.PROPOSAL_CREATE],
    name="Governor"
)

# System/Omnipotent for legacy or core loops
SYSTEM_CONTEXT = AgentContext(
    role=AgentRole.SYSTEM,
    allowed_actions=[
        AgentAction.SIGNAL_DETECT,
        AgentAction.REFLECTION_GENERATE,
        AgentAction.PROPOSAL_CREATE,
        AgentAction.PREFERENCE_MUTATE
    ],
    name="SystemKernel"
)
