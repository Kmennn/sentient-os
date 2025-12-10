
import pytest
from unittest.mock import MagicMock, AsyncMock
from sync.broadcast import SyncBroadcastService

@pytest.mark.asyncio
async def test_broadcast_service_connect_disconnect():
    service = SyncBroadcastService()
    mock_ws = AsyncMock()
    
    await service.connect(mock_ws)
    assert mock_ws in service.active_connections
    assert len(service.active_connections) == 1
    
    service.disconnect(mock_ws)
    assert mock_ws not in service.active_connections
    assert len(service.active_connections) == 0

@pytest.mark.asyncio
async def test_broadcast_logic():
    service = SyncBroadcastService()
    mock_ws = AsyncMock()
    await service.connect(mock_ws)
    
    await service.broadcast_agent_event("test_agent", "idle")
    
    mock_ws.send_text.assert_called()
    args = mock_ws.send_text.call_args[0][0]
    assert "agent:event" in args
