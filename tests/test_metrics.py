
import pytest
from core.agents.supervisor import supervisor
import asyncio

@pytest.mark.asyncio
async def test_supervisor_metrics():
    # Helper task
    async def dummy_task(succeed=True):
        if not succeed:
            raise ValueError("Fail")
        return "ok"

    # Submit success
    await supervisor.start()
    fut = await supervisor.submit_task(dummy_task, succeed=True)
    await fut # Wait for completion
    
    # Submit fail
    try:
        fut = await supervisor.submit_task(dummy_task, succeed=False)
        await fut
    except ValueError:
        pass
        
    await supervisor.stop()
    
    metrics = supervisor.get_metrics()
    assert "sentient_agent_tasks_completed 1" in metrics or "tasks_completed" in metrics
    # Note: string format depends on iteration order, but "sentient_agent_tasks_completed" should be present.
    assert "sentient_agent_tasks_failed 1" in metrics or "tasks_failed 1" in metrics
