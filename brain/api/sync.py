from fastapi import APIRouter, HTTPException
from brain.missions.mission_scheduler import mission_scheduler
from brain.sync.sync_state import SyncState

router = APIRouter()

@router.get("/sync/state")
def get_sync_state():
    """
    Returns the latest exported sync state.
    """
    state = mission_scheduler.latest_sync_state
    if not state:
        # Generate on demand if missing
        state = mission_scheduler.state_exporter.export_sync_state()
        mission_scheduler.latest_sync_state = state
        
    return state.to_dict()

@router.post("/sync/state")
def import_sync_state(payload: dict):
    """
    Imports a sync state snapshot.
    """
    try:
        state = SyncState.from_dict(payload)
        success = mission_scheduler.state_importer.validate_and_import(state)
        if success:
            return {"status": "imported"}
        else:
            return {"status": "rejected"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid sync state: {e}")

@router.get("/sync/conflicts")
def get_sync_conflicts():
    """
    Returns recent sync conflicts and resolutions.
    """
    return mission_scheduler.conflict_resolver.get_conflicts()
