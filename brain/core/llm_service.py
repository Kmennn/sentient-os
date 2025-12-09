
from core.local_model_engine import local_engine
from core.memory_service import memory_service
from core.agents.search_agent import SearchAgent
from core.agents.task_agent import TaskAgent
from typing import Optional
import json
import asyncio

class LLMService:
    def __init__(self):
        self._search_agent = SearchAgent()
        self._task_agent = TaskAgent()
        self._intent_cache = {}

    async def _detect_intent(self, text: str) -> str:
        """
        Classify intent: CHAT, SEARCH, or TASK.
        """
        if text in self._intent_cache:
            return self._intent_cache[text]

        prompt = f"""
        Classify the user intent.
        - SEARCH: asking for facts, history, or information retrieval.
        - TASK: asking to perform an action (open app, type, click, plan).
        - CHAT: casual conversation, greeting, philosophy.
        - VISION: asking about screen content, what you see.
        - TOOL: asking for time, searching files, utilities.
        
        Query: {text}
        
        Respond with ONLY one word: CHAT, SEARCH, TASK, VISION, or TOOL.
        """
        try:
            # Short timeout for classification
            response = await asyncio.wait_for(local_engine.generate(prompt), timeout=5.0)
            intent = response.strip().upper()
        except asyncio.TimeoutError:
            print("Intent detection timeout, defaulting to CHAT")
            intent = "CHAT"
        except Exception:
            intent = "CHAT"

        final_intent = "CHAT"
        if "SEARCH" in intent: final_intent = "SEARCH"
        if "TASK" in intent: final_intent = "TASK"
        if "VISION" in intent: final_intent = "VISION"
        if "TOOL" in intent: final_intent = "TOOL"
        
        # Cache result
        if len(self._intent_cache) > 100:
            self._intent_cache.clear()
        self._intent_cache[text] = final_intent
        
        return final_intent

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
            plan = await self._task_agent.run(text)
            
            # Format plan for display
            steps_str = json.dumps(plan[0], indent=2) 
            
            # --- BRIDGE INTEGRATION (v1.8) ---
            # If we have actions, we should trigger a confirmation request to the UI.
            # We need to import the manager here to avoid circular imports at top level if possible, 
            # or move manager to a shared module.
            try:
                from api.ws_handlers import manager
                import uuid
                
                # Check for actions
                actions = plan 
                if actions:
                    # For v1.8 MVP, we confirm the FIRST action. 
                    # Complex plans would need a loop or bulk confirmation.
                    first_action = actions[0]
                    action_id = str(uuid.uuid4())
                    
                    # Store pending action intent if needed?
                    # Ideally we persist pending actions in DB. 
                    
                    await manager.broadcast_json({
                        "type": "action.confirmation",
                        "payload": {
                            "action_id": action_id,
                            "intent": first_action.get("action"),
                            "summary": f"Allow {first_action.get('action')} with {first_action.get('params')}?",
                            # Pass the actual execution params so we can run it on confirm
                            "execution_data": first_action
                        }
                    })
            except Exception as e:
                print(f"Failed to trigger bridge: {e}")

            return f"I have created a plan for this task:\n\n```json\n{steps_str}\n```\n\n(Check your screen for confirmation dialog)"

        elif intent == "VISION":
            from core.agents.vision_agent import vision_agent
            return await vision_agent.run(text)

        elif intent == "TOOL":
            from core.agents.tools_agent import tools_agent
            return await tools_agent.run(text)

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
