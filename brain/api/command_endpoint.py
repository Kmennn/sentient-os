from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from brain.input.command_parser import CommandParser
from brain.input.intent_parser import IntentParser
from brain.missions.mission_scheduler import mission_scheduler

router = APIRouter()
cmd_parser = CommandParser()
intent_compiler = IntentParser()

class CommandRequest(BaseModel):
    text: str

@router.post("/command")
async def execute_command(cmd: CommandRequest):
    try:
        # H7: NL Compilation
        compiled_text = intent_compiler.compile(cmd.text)
        if not compiled_text:
            return {
                "status": "ERR", 
                "message": "Ambiguous intent. Try '/focus 25', '/status', or '/stop'."
            }

        parsed = cmd_parser.parse(compiled_text)
        verb = parsed.verb
        args = parsed.args

        # Dispatch
        if verb == "focus":
            duration = int(args[0]) if args else 25
            if len(args) > 0 and args[0] == "stop":
                 mission_scheduler.manual_focus_provider.stop_focus_session()
                 return {"status": "OK", "message": "Focus stopped."}
            
            mission_scheduler.manual_focus_provider.start_focus_session(duration)
            return {"status": "OK", "message": f"Focus started for {duration}m."}

        elif verb == "status":
            return {"status": "OK", "state": mission_scheduler._last_state_snapshot}

        elif verb == "mission":
            if not args:
                 return {"status": "ERR", "message": "Mission description required."}
            desc = " ".join(args)
            mission_scheduler._queue_mission({"task": desc})
            return {"status": "OK", "message": f"Queued: {desc}"}

        elif verb == "stop":
            mission_scheduler.preempt_active_mission("User Command")
            return {"status": "OK", "message": "Stopped active mission."}

        elif verb == "panic":
            return {"status": "OK", "message": "Panic logged (Simulated)."}
            
        elif verb == "voice":
            return {"status": "OK", "message": "Voice toggle not yet implemented."}

        return {"status": "OK", "message": f"Command '{verb}' parsed but not mapped."}

    except ValueError as e:
        # Expected parsing errors
        return {"status": "ERR", "message": str(e)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
