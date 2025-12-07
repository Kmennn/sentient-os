
from core.local_model_engine import local_engine
from core.memory_service import memory_service
from core.agents.search_agent import SearchAgent
from core.agents.task_agent import TaskAgent
from typing import Optional
import json

class LLMService:
    def __init__(self):
        self._search_agent = SearchAgent()
        self._task_agent = TaskAgent()

    async def _detect_intent(self, text: str) -> str:
        """
        Classify intent: CHAT, SEARCH, or TASK.
        """
        prompt = f"""
        Classify the user intent.
        - SEARCH: asking for facts, history, or information retrieval.
        - TASK: asking to perform an action (open app, type, click, plan).
        - CHAT: casual conversation, greeting, philosophy.
        
        Query: {text}
        
        Respond with ONLY one word: CHAT, SEARCH, or TASK.
        """
        response = await local_engine.generate(prompt)
        intent = response.strip().upper()
        if "SEARCH" in intent: return "SEARCH"
        if "TASK" in intent: return "TASK"
        return "CHAT"

    async def generate_response(self, text: str, history: list = None, stream: bool = False) -> str:
        # 1. Detect Intent
        intent = await self._detect_intent(text)
        print(f"DEBUG: Intent detected: {intent}")

        # 2. Route to Agent
        if intent == "SEARCH":
            # Delegate to SearchAgent
            results = await self._search_agent.run(text)
            # Summarize results
            context_str = "\n".join([f"- {r['text'][:200]}..." for r in results[0]['results']])
            prompt = f"User asked: {text}\n\nSearch Results:\n{context_str}\n\nProvide a concise answer."
            return await local_engine.generate(prompt)

        elif intent == "TASK":
            # Delegate to TaskAgent
            # For v1.8, we just return the plan as text confirmation
            plan = await self._task_agent.run(text)
            
            # Format plan for display
            steps_str = json.dumps(plan[0], indent=2) # plan[0] because run returns list of results
            return f"I have created a plan for this task:\n\n```json\n{steps_str}\n```\n\n(Actions are pending approval)"

        else:
            # Standard Chat (CHAT)
            # Get Context
            history_context = ""
            if history: 
                # formatting... simple string concat for now
                pass 
                
            # Use Memory Service for context if not provided
            # (llm_service is usually called with history=None in current routes, 
            # but memory_service has the persistent log)
            recent_msgs = memory_service.get_history("user", limit=5)
            history_str = "\n".join([f"{m['role']}: {m['content']}" for m in recent_msgs])
            
            full_prompt = f"System: You are Sentient OS.\nHistory:\n{history_str}\nUser: {text}\nAssistant:"
            
            if stream:
                return local_engine.generate_stream(full_prompt)
            else:
                return await local_engine.generate(full_prompt)

llm_service = LLMService()
