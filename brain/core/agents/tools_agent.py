
from core.agents.base_agent import BaseAgent
from core.tools.registry import registry
from core.llm_service import llm_service
import json

class ToolsAgent(BaseAgent):
    name = "ToolsAgent"

    async def run(self, query: str):
        # 1. Select Tool
        tools = registry.list_tools()
        tools_desc = json.dumps(tools)
        
        # Simple selection prompt
        # In prod: use structured outputs or function calling API
        prompt = f"""
        History: []
        User Query: {query}
        Available Tools: {tools_desc}
        
        Select the best tool to answer the query.
        Return ONLY a JSON object with:
        {{
            "tool": "tool_name",
            "params": {{ ... }}
        }}
        If no tool fits, return {{ "tool": null }}.
        """
        
        response = await llm_service.generate_response(prompt)
        # Clean response (remove markdown)
        json_str = response.strip().replace("```json", "").replace("```", "")
        
        try:
            plan = json.loads(json_str)
            tool_name = plan.get("tool")
            
            if not tool_name:
                return "I don't have a tool for that."
                
            tool = registry.get_tool(tool_name)
            if not tool:
                return f"Tool {tool_name} not found."
            
            # 2. Execute
            result = tool.run(plan.get("params", {}))
            return f"Tool {tool_name} returned: {result}"
            
        except Exception as e:
            return f"Failed to execute tool: {e}"

tools_agent = ToolsAgent()
