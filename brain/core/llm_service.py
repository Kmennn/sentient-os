
from core.local_model_engine import local_engine
from core.memory_service import memory_service
from core.agents.search_agent import SearchAgent
from core.agents.task_agent import TaskAgent
from typing import Optional
import json
import asyncio


# Templates
PROMPT_CHAT = """
System: You are Sentient OS, a helpful and intelligent AI assistant. 
You strictly follow these rules:
1. Be concise and friendly.
2. Use context from memory if relevant.
3. If unsure, admit it.

Context:
{context}

History:
{history}

User: {query}
Assistant:
"""

PROMPT_SEARCH = """
System: You are a Research Assistant. Synthesize the provided Search Results to answer the user's question.
If the results do not contain the answer, say "I couldn't find that information locally."

Search Results:
{context}

User: {query}
Assistant:
"""

PROMPT_TASK = """
System: You are an Automation Agent. Analyze the user's request and map it to a sequence of actions.
Available Actions: OPEN_APP, SCROLL_UP, SCROLL_DOWN, CLICK, TYPE_TEXT, MOUSE_MOVE.

User: {query}

Output JSON ONLY.
"""

class LLMService:
    def __init__(self):
        self._search_agent = SearchAgent()
        self._task_agent = TaskAgent()
        self._intent_cache = {}
        self._context_threshold = 0.5 # L2 Distance. Lower is better? 
        # FAISS IndexFlatL2 returns squared Euclidean distance.
        # Relevance depends on embedding normalization. 
        # Typically 0.0 is exact match. > 1.0 is far.
        # Let's assume < 1.0 is relevant for MiniLM-L6-v2 normalized?? 
        # Actually usually cosine distance is better, but L2 is okay. 
        # Let's say threshold is distance < 1.2
        self._distance_threshold = 1.2 

    def _filter_context(self, results: list, max_age_days: int = 30) -> str:
        """
        Filter vector results by relevance score and recency.
        """
        import time
        filtered = []
        now = int(time.time())
        cutoff = now - (max_age_days * 86400)
        
        for r in results:
            # Score check (L2 distance, lower is better)
            score = r.get("score", 100.0)
            if score > self._distance_threshold:
                continue
                
            # Date check
            ts = r.get("timestamp", 0)
            if ts < cutoff:
                continue
                
            filtered.append(r["text"])
            
        return "\n".join([f"- {txt[:200]}" for txt in filtered])

    async def _self_check(self, question: str, answer: str) -> bool:
        """
        Lightweight check: Does answer match question?
        """
        prompt = f"Question: {question}\nAnswer: {answer}\nDoes the answer directly address the question? YES or NO."
        try:
            # Very short timeout for check
            check = await asyncio.wait_for(local_engine.generate(prompt), timeout=10.0)
            return "YES" in check.upper()
        except:
            return True # Fallback to trusting generation on timeout

    async def _detect_intent(self, text: str) -> str:
        # Check Cache
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

        # 2. Route to Agent or Handle Chat
        if intent == "SEARCH":
            # Delegate to SearchAgent (it handles its own vector search usually, 
            # but we can enhance it here with _filter_context logic if we owned it)
            # For v1.9, SearchAgent.run() returns raw vector match objects.
            results = await self._search_agent.run(text)
            
            # Apply Filter
            # results[0]['results'] is the list
            if results and 'results' in results[0]:
                raw_list = results[0]['results']
                # But wait, search_agent implementation might return differently? 
                # Checking search_agent usage in original file:
                # results[0]['results'] was accessed.
                # Just passing context string to prompt.
                
                # I will construct context using my filter
                context_str = self._filter_context(raw_list)
                prompt = PROMPT_SEARCH.format(context=context_str, query=text)
                
                response = await local_engine.generate(prompt)
                
                # Self Check
                if not await self._self_check(text, response):
                    print("Self-check failed. Regenerating...")
                    response = await local_engine.generate(prompt + "\nRefine the answer to be more direct.")
                    
                return response
            else:
                 return "I found no results locally."

        elif intent == "TASK":
            # Delegate to TaskAgent
            plan = await self._task_agent.run(text)
            steps_str = json.dumps(plan[0], indent=2) 
            
            # --- BRIDGE INTEGRATION (v1.8) ---
            try:
                from api.ws_handlers import manager
                import uuid
                actions = plan 
                if actions:
                    first_action = actions[0]
                    action_id = str(uuid.uuid4())
                    await manager.broadcast_json({
                        "type": "action.confirmation",
                        "payload": {
                            "action_id": action_id,
                            "intent": first_action.get("action"),
                            "summary": f"Allow {first_action.get('action')} with {first_action.get('params')}?",
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
            # CHAT
            # Get Context (Vector Search + Memory)
            # 1. Memory Service (Short Term)
            recent_msgs = memory_service.get_history("user", limit=5)
            history_str = "\n".join([f"{m['role']}: {m['content']}" for m in recent_msgs])
            
            # 2. Vector Search (Long Term) - NOT in original CHAT logic, adding it for v1.9
            from core.vector_store import vector_store
            long_term_results = vector_store.search(text, k=3)
            long_term_ctx = self._filter_context(long_term_results)
            
            full_prompt = PROMPT_CHAT.format(
                context=long_term_ctx,
                history=history_str,
                query=text
            )
            
            # Generate
            if stream:
                return local_engine.generate_stream(full_prompt)
            else:
                response = await local_engine.generate(full_prompt)
                # Self Check for Chat
                if not await self._self_check(text, response):
                     # Retry once
                     response = await local_engine.generate(full_prompt + "\nSystem: Previous answer was off-topic. Try again.")
                return response

llm_service = LLMService()
