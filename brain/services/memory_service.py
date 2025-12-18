from brain.reflection.reflection_trigger import ReflectionTrigger
from brain.reflection.reflection_prompt import ReflectionPrompt

class MemoryService:
    def __init__(self):
        self.reflection_trigger = ReflectionTrigger()

    def check_reflection_triggers(self, week_plan, load_snapshots) -> 'ReflectionPrompt':
        return self.reflection_trigger.check_triggers(week_plan, load_snapshots)
