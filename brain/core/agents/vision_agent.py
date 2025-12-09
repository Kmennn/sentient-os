
from core.agents.base_agent import BaseAgent
from core.vision.vision_engine import vision_engine
from core.llm_service import llm_service
import json

class VisionAgent(BaseAgent):
    name = "VisionAgent"

    async def plan(self, query: str):
        pass

    async def execute(self, step: dict):
        pass

    async def run(self, query: str):
        # 1. Analyze Screen
        analysis = await vision_engine.analyze()
        if "error" in analysis:
            return f"I couldn't see the screen: {analysis['error']}"

        text = analysis.get("ocr_text", "")
        summary = analysis.get("summary", "")

        # 2. Ask LLM to answer query based on visual context
        prompt = f"""
        User Question: {query}
        
        Screen Context:
        - OCR Text: {text}
        - Summary: {summary}
        
        Answer the user's question based on the screen content.
        """
        response = await llm_service.generate_response(prompt)
        return response

vision_agent = VisionAgent()
