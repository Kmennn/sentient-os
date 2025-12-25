"""
Intent Router - Deterministic classification for CHAT vs TASK

Rules:
- CHAT is the default
- TASK requires:
  1. At least 2 tokens (verb + object)
  2. Starts with an action verb
  3. Has an object/target

Examples:
- "hello" -> CHAT (greeting)
- "scroll down" -> TASK (verb + direction)
- "open chrome" -> TASK (verb + app)
- "scroll" -> CHAT (no object)
- "can you scroll down" -> TASK (contains verb + object)
"""

import logging

logger = logging.getLogger(__name__)

# Action verbs that indicate tasks
ACTION_VERBS = {
    # Navigation & Scrolling
    "scroll", "navigate", "go", "move",
    
    # Application Control
    "open", "close", "launch", "start", "stop", "kill", "quit",
    
    # Input Actions
    "click", "type", "press", "enter", "select", "drag", "drop",
    
    # Window Management
    "minimize", "maximize", "resize", "switch", "focus",
    
    # File Operations
    "create", "delete", "rename", "copy", "paste", "cut", "save",
    
    # System Commands
    "run", "execute", "shutdown", "restart", "sleep",
}

# Common greetings/chat patterns
CHAT_PATTERNS = {
    "hello", "hi", "hey", "greetings", "good morning", "good afternoon", 
    "good evening", "howdy", "sup", "what's up", "how are you",
    "thanks", "thank you", "ok", "okay", "yes", "no", "why", "how",
    "what", "when", "where", "who", "please", "help"
}


def classify_intent(query: str) -> str:
    """
    Deterministic intent classification.
    
    Returns:
        "CHAT" or "TASK"
    """
    query_lower = query.lower().strip()
    tokens = query_lower.split()
    
    # Rule 1: Check greeting patterns (always CHAT)
    if query_lower in CHAT_PATTERNS or any(pattern in query_lower for pattern in CHAT_PATTERNS):
        if not any(verb in tokens for verb in ACTION_VERBS):
            logger.info(f"Intent: CHAT (greeting/chat pattern) - '{query[:50]}'")
            return "CHAT"
    
    # Rule 2: Must have at least 2 tokens for TASK
    if len(tokens) < 2:
        logger.info(f"Intent: CHAT (too short, {len(tokens)} token) - '{query[:50]}'")
        return "CHAT"
    
    # Rule 3: Check for action verb
    has_action_verb = False
    verb_position = -1
    
    for i, token in enumerate(tokens):
        # Remove punctuation for matching
        clean_token = token.strip(",.!?;:")
        if clean_token in ACTION_VERBS:
            has_action_verb = True
            verb_position = i
            break
    
    if not has_action_verb:
        logger.info(f"Intent: CHAT (no action verb) - '{query[:50]}'")
        return "CHAT"
    
    # Rule 4: Check if there's an object after the verb
    # If verb is at the end or only has stop words after it, it's incomplete
    if verb_position >= len(tokens) - 1:
        logger.info(f"Intent: CHAT (verb '{tokens[verb_position]}' has no object) - '{query[:50]}'")
        return "CHAT"
    
    # Has verb + object → TASK
    logger.info(f"Intent: TASK (verb '{tokens[verb_position]}' + object) - '{query[:50]}'")
    return "TASK"


def get_intent(query: str) -> str:
    """
    Public API for intent classification.
    Logs every decision.
    """
    intent = classify_intent(query)
    logger.info(f"INTENT_DECISION: '{query[:50]}' → {intent}")
    return intent
