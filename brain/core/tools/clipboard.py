
from core.tools.base import BaseTool
import pyperclip

class ClipboardTool(BaseTool):
    name = "clipboard"
    description = "Reads or Writes to the clipboard. Params: {'action': 'read' | 'write', 'text': '...'}"
    
    def run(self, params: dict) -> str:
        action = params.get("action", "read").lower()
        if action == "read":
            try:
                return pyperclip.paste()
            except Exception as e:
                return f"Clipboard read error: {e}"
        elif action == "write":
            text = params.get("text", "")
            try:
                pyperclip.copy(text)
                return "Clipboard updated."
            except Exception as e:
                return f"Clipboard write error: {e}"
        else:
            return "Invalid action. Use 'read' or 'write'."
