from typing import List, NamedTuple, Any

class MacroStep(NamedTuple):
    action_type: str 
    params: dict = {}

class HumanMacroRegistry:
    MACROS = {
        "clean_system": [
             # Example: Run diagnostics, clear caches
             MacroStep("log", {"message": "Diagnostics: System Health Check OK."}),
             MacroStep("log", {"message": "Cache: Purged 120MB temp files."}),
             MacroStep("voice", {"text": "System cleanup complete."})
        ],
        "meeting_prep": [
             # Focus + Silence
             MacroStep("focus", {"duration": 45}),
             MacroStep("voice", {"text": "Meeting mode active."})
        ],
        "wrap_up": [
             # Stop work
             MacroStep("stop_mission", {}),
             MacroStep("log", {"message": "Context saved to disk."}),
             MacroStep("voice", {"text": "Work wrapped up. Have a good evening."})
        ]
    }
    
    @staticmethod
    def resolve(macro_name: str) -> List[MacroStep]:
        return HumanMacroRegistry.MACROS.get(macro_name, [])
