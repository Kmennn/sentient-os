
import sys
import os
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

# Imports
from core.tools.registry import registry
from core.tools.process_list import ProcessListTool, DiskUsageTool
from core.agents.deep_research_agent import DeepResearchAgent

@pytest.mark.asyncio
async def test_deep_research_agent():
    agent = DeepResearchAgent()
    
    # Mock LLM
    with patch("core.agents.deep_research_agent.local_engine.generate", new_callable=AsyncMock) as mock_gen:
        # Mock planning response
        mock_gen.side_effect = [
            '{"steps": ["step1", "step2"]}', # Plan
            'Insight 1', # Step 1
            'Insight 2', # Step 2
            '{"final_answer": "Result", "citations": []}' # Synthesize
        ]
        
        # We also need to mock memory_service.vector_store.search return empty or some list
        with patch("core.agents.deep_research_agent.memory_service") as mock_mem:
            mock_mem.vector_store.search.return_value = []
            
            res = await agent.run("Research Python")
            assert "final_answer" in res or "steps" in res
            assert len(res.get("steps", [])) == 2

def test_system_tools():
    # Process List
    proc_tool = ProcessListTool()
    procs = proc_tool.run({"limit": 2})
    assert len(procs) <= 2
    assert isinstance(procs, list)
    if len(procs) > 0:
        assert "name" in procs[0]

    # Disk Usage
    disk_tool = DiskUsageTool()
    usage = disk_tool.run({})
    assert "total_gb" in usage
    assert "percent" in usage

@pytest.mark.asyncio
async def test_voice_engine_mock():
    # Mock Vosk
    with patch("core.voice.voice_engine.Model") as mock_model, \
         patch("core.voice.voice_engine.KaldiRecognizer") as mock_rec, \
         patch("os.path.exists", return_value=True):
         
         from core.voice.voice_engine import VoiceEngine
         # Re-init to use mocks
         engine = VoiceEngine()
         engine.model = MagicMock() # Ensure model loaded
         
         mock_rec_inst = mock_rec.return_value
         mock_rec_inst.FinalResult.return_value = '{"text": "hello world"}'
         
         res = await engine.transcribe(b"fake_audio_bytes")
         assert res["text"] == "hello world"

@pytest.mark.asyncio
async def test_autonomy_chaining():
    # Test LLMService state
    from core.llm_service import LLMService, TaskAgent
    
    with patch("core.llm_service.local_engine.generate", new_callable=AsyncMock) as mock_gen, \
         patch("core.llm_service.TaskAgent.run", new_callable=AsyncMock) as mock_task_run:
        
        # Setup
        mock_gen.return_value = "TASK" # Intent
        mock_task_run.return_value = [{"action": "A1"}, {"action": "A2"}] # 2 steps
        
        llm = LLMService()
        
        # 1. Trigger Task
        # Mocking ws manager to avoid broadcast error
        with patch("api.ws_handlers.manager.broadcast_json", new_callable=AsyncMock) as mock_broadcast:
             resp = await llm.generate_response("Do A and B")
             assert "created a plan" in resp
             
             # Check state
             assert len(llm._active_plans) == 1
             plan_id = list(llm._active_plans.keys())[0]
             assert len(llm._pending_actions) == 1 # 1 pending
             
             # Verify broadcast called for 1st action
             assert mock_broadcast.called
             
             # 2. Confirm Step 1
             action_id_1 = list(llm._pending_actions.keys())[0]
             
             # Mock execution
             with patch("httpx.AsyncClient.post", new_callable=AsyncMock):
                 await llm.confirm_action(action_id_1)
                 
             # Check progress
             assert llm._plan_progress[plan_id] == 1
             
             # Should fail if it triggered next step immediately?
             # Yes, confirm_action calls _trigger_step.
             # So now Step 2 should be pending
             assert len(llm._pending_actions) == 1
             action_id_2 = list(llm._pending_actions.keys())[0]
             assert action_id_2 != action_id_1

