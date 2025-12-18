import pytest
import datetime
import time
from brain.day.day_planner import DayPlanner
from brain.day.day_plan import DayPlan, PlanItem
from brain.routines.routine import Routine
from brain.missions.mission_scheduler import QueuedMission
from dataclasses import dataclass

def test_planner_generates_routines():
    planner = DayPlanner()
    today = datetime.date.today()
    wd = today.weekday()
    
    r1 = Routine("Morning", 32400, 3600, [wd]) # 9 AM
    r2 = Routine("Weekend", 36000, 3600, [wd-1 if wd>0 else 6]) # Different day
    
    plan = planner.generate_plan([r1, r2], [], [], today)
    
    assert len(plan.items) == 1
    assert plan.items[0].name == "Morning"
    assert plan.items[0].type == 'ROUTINE'

def test_planner_overlap_warnings():
    planner = DayPlanner()
    # Use tomorrow to ensure 'now' < 'scheduled_time'
    today = datetime.date.today() + datetime.timedelta(days=1)
    wd = today.weekday()
    
    # Routine 9:00 - 10:00
    r1 = Routine("Focus", 32400, 3600, [wd])
    
    # Task 9:30 (Scheduled via QueuedMission)
    # blocked_until = midnight + 9:30 (34200)
    midnight = datetime.datetime.combine(today, datetime.time.min).timestamp()
    qm = QueuedMission(priority=10, timestamp=midnight, mission_id="Task A", blocked_until=midnight + 34200)
    
    plan = planner.generate_plan([r1], [qm], [], today)
    
    for i, item in enumerate(plan.items):
        print(f"DEBUG: Item {i}: {item.name} ({item.type}) Start={item.start_seconds}")
    
    assert len(plan.items) == 2
    r_item = plan.items[0]
    t_item = plan.items[1]
    
    assert r_item.type == 'ROUTINE', f"Expected ROUTINE first, got {r_item.type}"
    assert t_item.type == 'TASK'
    
    # Check Warnings
    assert len(r_item.warnings) > 0
    assert "Overlaps with Task A" in r_item.warnings[0]
