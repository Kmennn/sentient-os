
from typing import List, Dict, Any
import json
from .base_agent import BaseAgent
from core.local_model_engine import local_engine

class TaskAgent(BaseAgent):
    """
    Agent responsible for breaking down complex requests into actionable steps.
    """
    def __init__(self):
        super().__init__("TaskAgent")

    async def plan(self, query: str) -> List[Dict]:
        """
        Uses LLM to generate a JSON plan of actions.
        """
        prompt = f"""
        You are an AI task planner. Break down the user's request into a sequential list of actions.
        Available Actions:
        - OPEN_APP(app_name)
        - TYPE_TEXT(text)
        - CLICK_ICON(icon_name)
        
        Request: {query}
        
        Respond ONLY with a JSON list of objects, e.g.:
        [
            {{"action": "OPEN_APP", "params": "Notepad"}},
            {{"action": "TYPE_TEXT", "params": "Hello World"}}
        ]
        """
        
        response_text = await local_engine.generate(prompt)
        
        # Simple parsing logic (robustness improvements needed for prod)
        try:
            # Extract JSON if wrapped in markdown code blocks
            if "```" in response_text:
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            plan = json.loads(response_text)
            if isinstance(plan, list):
                return plan
            return []
        except Exception as e:
            print(f"TaskAgent planning error: {e}")
            # Fallback: simple echo or error step
            return [{"action": "ERROR", "params": "Could not parse plan"}]

    async def execute(self, step: Dict) -> Dict[str, Any]:
        """
        For v1.8, 'execution' basically means validating the step 
        and preparing it for the Bridge (routes.py will handle dispatch).
        """
        return {
            "agent": self.name,
            "step": "prepare_action",
            "action": step.get("action"),
            "params": step.get("params"),
            "status": "pending_approval" # Actions default to pending
        }
