from dataclasses import dataclass, field
from enum import Enum, auto

class PromptType(Enum):
    LOAD = auto()
    CONFLICT = auto()
    ROUTINE = auto()

@dataclass
class ReflectionPrompt:
    """
    Represents an optional reflection prompt for the user.
    """
    prompt_id: str
    type: PromptType
    pattern_description: str # Neutral description of what triggered it
    confidence: float
    dismissed: bool = False
