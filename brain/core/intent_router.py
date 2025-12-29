"""
Intent Router - P2.4 Intent Boundary Lock

CRITICAL SAFETY RULES:
1. Default Intent = CHAT (if anything unclear → CHAT)
2. TASK requires ALL 3:
   - Explicit action verb (scroll, open, close, click, type, press, delete)
   - Explicit object (down, up, chrome, file, window, tab, etc.)
   - Imperative tone (no questions, no polite phrases)
3. Hard blocks ALWAYS → CHAT:
   - Greetings (hello, hi, hey)
   - Questions ("can you", "could you", "would you")
   - Polite phrases ("please", "would you mind")
   - Single-word commands ("scroll", "open")
"""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@dataclass
class IntentDecision:
    """Logged decision for every intent classification"""
    input: str
    intent: str
    reason: str
    
    def __str__(self):
        return f"IntentDecision(input=\"{self.input[:50]}\", intent={self.intent}, reason=\"{self.reason}\")"


# Explicit action verbs (must be present for TASK)
ACTION_VERBS = {
    "scroll", "open", "close", "click", "type", "press", "delete",
    "move", "drag", "drop", "minimize", "maximize", "resize",
    "launch", "start", "stop", "kill", "quit", "navigate",
    "run", "execute", "switch", "focus", "select", "copy", "paste", "cut"
}

# Explicit objects (must be present for TASK)
VALID_OBJECTS = {
    # Directions
    "up", "down", "left", "right", "top", "bottom",
    # Apps
    "chrome", "firefox", "edge", "safari", "browser",
    "notepad", "word", "excel", "terminal", "cmd", "powershell",
    "vscode", "code", "spotify", "discord", "slack", "teams",
    # UI Elements
    "window", "tab", "file", "folder", "button", "link", "menu",
    "screen", "desktop", "taskbar", "start",
    # Generic
    "app", "application", "program"
}

# Hard blocks - ALWAYS CHAT
GREETINGS = {"hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening", "howdy", "sup"}

# Question patterns - ALWAYS CHAT
QUESTION_STARTERS = {"can you", "could you", "would you", "will you", "what", "how", "why", "when", "where", "who"}

# Polite modifiers - ALWAYS CHAT  
POLITE_WORDS = {"please", "kindly", "would you mind", "could you please"}


def classify_intent(query: str) -> IntentDecision:
    """
    Strict intent classification with safety-first approach.
    Returns IntentDecision with logged reason.
    """
    query_lower = query.lower().strip()
    tokens = query_lower.split()
    
    # RULE 1: Hard block - Greetings (ALWAYS CHAT)
    if query_lower in GREETINGS:
        decision = IntentDecision(query, "CHAT", "greeting (hard block)")
        logger.info(str(decision))
        return decision
    
    # Also check if starts with greeting
    for greeting in GREETINGS:
        if query_lower.startswith(greeting + " ") or query_lower == greeting:
            decision = IntentDecision(query, "CHAT", f"starts with greeting '{greeting}' (hard block)")
            logger.info(str(decision))
            return decision
    
    # RULE 2: Hard block - Questions (ALWAYS CHAT)
    for question in QUESTION_STARTERS:
        if query_lower.startswith(question):
            decision = IntentDecision(query, "CHAT", f"question pattern '{question}' (hard block)")
            logger.info(str(decision))
            return decision
    
    # RULE 3: Hard block - Polite phrases (ALWAYS CHAT)
    for polite in POLITE_WORDS:
        if polite in query_lower:
            decision = IntentDecision(query, "CHAT", f"polite phrase '{polite}' (hard block)")
            logger.info(str(decision))
            return decision
    
    # RULE 4: Hard block - Single word (ALWAYS CHAT)
    if len(tokens) < 2:
        decision = IntentDecision(query, "CHAT", "single word (missing object)")
        logger.info(str(decision))
        return decision
    
    # RULE 5: Check for action verb
    found_verb: Optional[str] = None
    verb_position = -1
    for i, token in enumerate(tokens):
        clean_token = token.strip(",.!?;:")
        if clean_token in ACTION_VERBS:
            found_verb = clean_token
            verb_position = i
            break
    
    if not found_verb:
        decision = IntentDecision(query, "CHAT", "no action verb")
        logger.info(str(decision))
        return decision
    
    # RULE 6: Check for object AFTER verb
    found_object: Optional[str] = None
    for i in range(verb_position + 1, len(tokens)):
        clean_token = tokens[i].strip(",.!?;:")
        if clean_token in VALID_OBJECTS:
            found_object = clean_token
            break
    
    if not found_object:
        decision = IntentDecision(query, "CHAT", f"verb '{found_verb}' but missing valid object")
        logger.info(str(decision))
        return decision
    
    # RULE 7: Imperative tone check - verb should be near start (first 3 words)
    if verb_position > 2:
        decision = IntentDecision(query, "CHAT", f"verb '{found_verb}' not in imperative position (pos={verb_position})")
        logger.info(str(decision))
        return decision
    
    # ALL RULES PASSED → TASK
    decision = IntentDecision(query, "TASK", f"verb '{found_verb}' + object '{found_object}' (imperative)")
    logger.info(str(decision))
    return decision


def get_intent(query: str) -> str:
    """
    Public API for intent classification.
    Returns "CHAT" or "TASK" only.
    """
    decision = classify_intent(query)
    return decision.intent
