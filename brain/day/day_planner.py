import time
import datetime
from typing import List, Any
from brain.day.day_plan import DayPlan, PlanItem
from brain.routines.routine import Routine
# Forward ref for Scheduler to avoid circular import if possible, 
# but usually we pass instances or data.
# Planner needs access to RoutineApproval, MissionQueue, Deferrals.

class DayPlanner:
    """
    Aggregates data to form a DayPlan.
    """
    
    def generate_plan(self, routines: List[Routine], queued_missions: List[Any], deferred_intents: List[Any], date: datetime.date = None) -> DayPlan:
        if date is None:
            date = datetime.date.today()
            
        plan = DayPlan(date_str=date.isoformat())
        
        # 1. Routines
        for r in routines:
            # Check if routine applies to this day? Validating routine days of week could be done here.
            # Assuming passed routines are valid for today or we check `days_of_week`.
            # For MVP, assume caller filters or we add simple check if routine has that field.
            # Routine object from v4.8 has days_of_week.
            if hasattr(r, 'days_of_week') and r.days_of_week:
                 if date.weekday() not in r.days_of_week:
                     continue
                     
            item = PlanItem(
                id=r.routine_id,
                type='ROUTINE',
                name=r.name,
                start_seconds=r.time_of_day_seconds,
                duration_seconds=r.duration_seconds,
                details={"protected": getattr(r, 'protected', False)}
            )
            plan.items.append(item)
            
        # 2. Queued Missions (Scheduled)
        # These usually have execution timestamps? 
        # MissionQueue might not have explicit start times unless valid "blocked_until" or optimizer hints.
        # But we can assume they *could* run now or soon.
        # For visualization, maybe place them at "Now" or "Next Available"?
        # Or if they have a 'start_after' (blocked_until).
        
        # Let's visualize strictly scheduled things (delayed) or active.
        # active/queued without delay might be hard to visualize on a timeline without simulation.
        # We'll map them based on blocked_until if set, or "Now" if ready.
        
        now = time.time()
        midnight = datetime.datetime(date.year, date.month, date.day).timestamp()
        
        for qm in queued_missions:
            # qm is QueuedMission
            # if blocked_until > now, map it.
            start_ts = max(now, qm.blocked_until)
            # If timestamp is far in future (beyond today), skip?
            # 24h * 3600 = 86400
            
            # Mission time of day relative to THIS day
            # If mission is scheduled for tomorrow, it shouldn't appear on today's plan unless we look ahead.
            # Simple check: start_ts < midnight + 86400
            
            if start_ts < midnight + 86400:
                # Convert to seconds from midnight
                secs = int(start_ts - midnight)
                print(f"DEBUG PLANNER: Task {qm.mission_id} StartTS={start_ts} Midnight={midnight} Secs={secs}")
                if secs < 0: secs = 0 # carry over from yesterday?
                
                item = PlanItem(
                    id=qm.mission_id,
                    type='TASK',
                    name=qm.mission_id, # Or description from payload if avail
                    start_seconds=secs,
                    duration_seconds=1800, # Default duration estimate?
                    details={"priority": qm.priority}
                )
                plan.items.append(item)

        # 3. Detect Conflicts (Visual Overlaps)
        # Sort by start time
        plan.items.sort(key=lambda x: x.start_seconds)
        
        # Simple overlap check
        for i in range(len(plan.items) - 1):
            curr = plan.items[i]
            next_item = plan.items[i+1]
            
            curr_end = curr.start_seconds + curr.duration_seconds
            if curr_end > next_item.start_seconds:
                # Overlap!
                msg = f"Overlaps with {next_item.name}"
                curr.warnings.append(msg)
                next_item.warnings.append(f"Overlaps with {curr.name}")
                
        return plan
