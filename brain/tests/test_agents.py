
import pytest
from unittest.mock import AsyncMock, patch
from core.agents.search_agent import SearchAgent
from core.agents.task_agent import TaskAgent
from core.llm_service import LLMService

@pytest.mark.asyncio
async def test_search_agent():
    agent = SearchAgent()
    # Mock vector_store.search
    with patch('core.agents.search_agent.vector_store.search') as mock_search:
        mock_search.return_value = [{'text': 'France capital is Paris', 'score': 0.9}]
        
        plan = await agent.plan("capital of France")
        assert plan == ["capital of France"]
        
        result = await agent.execute("capital of France")
        assert result['agent'] == "SearchAgent"
        # We expect a dict with results
        assert len(result['results']) == 1
        assert result['results'][0]['text'] == 'France capital is Paris'

@pytest.mark.asyncio
async def test_task_agent_planning():
    agent = TaskAgent()
    
    # Mock LocalModelEngine to return a JSON plan
    fake_json = '''```json
    [
        {"action": "OPEN_APP", "params": "Notepad"},
        {"action": "TYPE_TEXT", "params": "Hello"}
    ]
    ```'''
    
    with patch('core.local_model_engine.local_engine.generate', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = fake_json
        
        plan = await agent.plan("Open Notepad and type Hello")
        assert len(plan) == 2
        assert plan[0]['action'] == "OPEN_APP"
        assert plan[1]['params'] == "Hello"

@pytest.mark.asyncio
async def test_llm_service_routing_task():
    service = LLMService()
    
    # 1. Mock intent detection to return TASK
    # 2. Mock TaskAgent to return a dummy plan
    
    with patch('core.llm_service.local_engine.generate', new_callable=AsyncMock) as mock_gen:
        # First call is intent detection, second call might not happen if we mock task agent run
        # But let's just mock detect_intent method directly if possible, or mock generate return values in sequence
        mock_gen.side_effect = ["TASK", "Final Response"] 
        
        # We also need to mock TaskAgent.run because checking it calls LLM again
        with patch.object(service._task_agent, 'run', new_callable=AsyncMock) as mock_task_run:
            mock_task_run.return_value = [[{"action": "TEST"}]]
            
            response = await service.generate_response("Do something")
            
            assert "I have created a plan" in response
            assert "TEST" in response
            mock_task_run.assert_called_once()

@pytest.mark.asyncio
async def test_llm_service_routing_search():
    service = LLMService()
    
    with patch.object(service, '_detect_intent', new_callable=AsyncMock) as mock_intent:
        mock_intent.return_value = "SEARCH"
        
        with patch.object(service._search_agent, 'run', new_callable=AsyncMock) as mock_search_run:
            mock_search_run.return_value = [{"results": [{'text': 'Info'}]}]
            
            with patch('core.llm_service.local_engine.generate', new_callable=AsyncMock) as mock_gen:
                mock_gen.return_value = "The answer is Info."
                
                response = await service.generate_response("What is Info?")
                
                assert "The answer is Info." == response
                mock_search_run.assert_called_once()
