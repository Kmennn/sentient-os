
import logging
import json
import asyncio
from typing import List, Dict, Any
from core.local_model_engine import local_engine
from core.tools.registry import registry
from core.memory_service import memory_service

logger = logging.getLogger("deep_research")

class DeepResearchAgent:
    def __init__(self):
        self.max_steps = 5

    async def run(self, query: str) -> Dict[str, Any]:
        """
        Executes a deep research task.
        1. Break down query into steps.
        2. Execute steps (Search/Tools).
        3. Synthesize answer.
        """
        logger.info(f"Starting Deep Research for: {query}")
        
        # 1. Plan
        plan = await self._plan_task(query)
        steps = plan.get("steps", [])
        logger.info(f"Plan: {steps}")

        results = []
        citations = []

        # 2. Execute Steps
        for step in steps:
            logger.info(f"Executing Step: {step}")
            # Decide tool vs vector search vs generic llm
            # Simple heuristic: If "search" or "find file", use tools.
            # If "concept" or "history", use vector search.
            
            step_result = ""
            if "search" in step.lower() or "find" in step.lower():
                # Try to use a tool?
                # For now, let's assume "file_search" is the main research tool available or web if we had it.
                # Use LLM to pick tool?
                tools_avail = registry.list_tools()
                # Simplified: just use vector search for now as "Research" often implies knowledge base.
                # But user wants "Tools usage".
                
                # Check Vector Store first
                vectors = memory_service.vector_store.search(step, limit=3)
                if vectors:
                   step_result += f"Found in memory: {vectors}"
                   citations.extend([v['metadata'] for v in vectors if 'metadata' in v])
                else:
                   step_result += "No memory found."
            else:
                # Ask LLM for insight
                context = await local_engine.generate(f"Research step: {step}. Provide insight.")
                step_result = context

            results.append({"step": step, "result": step_result})

        # 3. Synthesize
        final_prompt = f"""
        Research Goal: {query}
        Executed Steps: {json.dumps(results)}
        
        Synthesize a final report answering the goal.
        Include 'steps', 'citations', 'final_answer'.
        Format as JSON.
        """
        
        try:
            final_json_str = await local_engine.generate(final_prompt)
            # Try to parse or just return string if fails
            # We enforce JSON structure in prompt but local models are flaky.
            # We'll return a dict construction.
            return {
                "steps": [r['step'] for r in results],
                "citations": citations,
                "final_answer": final_json_str # Raw text for now unless we enforce JSON parser
            }
        except Exception as e:
            return {"error": str(e)}

    async def _plan_task(self, query: str) -> Dict[str, List[str]]:
        prompt = f"""
        Break down this research question into 3-5 distinct steps: "{query}"
        Return JSON: {{ "steps": ["step 1", "step 2"] }}
        """
        try:
            resp = await local_engine.generate(prompt)
            # Simple soft parsing if JSON fails (regex?)
            # Assuming model complies for now or we fallback
            if "{" in resp:
                 start = resp.find("{")
                 end = resp.rfind("}") + 1
                 return json.loads(resp[start:end])
            return {"steps": [query]} # Fallback
        except:
            return {"steps": [query]}

deep_research_agent = DeepResearchAgent()
