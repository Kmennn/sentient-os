from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import re

@dataclass
class ParsedCommand:
    verb: str
    args: List[str]
    raw: str

class CommandParser:
    WHITELIST = {
        "focus", "status", "mission", "stop", "resume", "panic", "override", "voice", "macro"
    }

    def parse(self, text: str) -> ParsedCommand:
        text = text.strip()
        if not text:
            raise ValueError("Empty command")

        # Remove optional slash
        if text.startswith("/"):
            text = text[1:]
            
        parts = text.split()
        verb = parts[0].lower()
        args = parts[1:]

        if verb not in self.WHITELIST:
            raise ValueError(f"Unknown command: {verb}")
            
        return ParsedCommand(verb=verb, args=args, raw=text)
