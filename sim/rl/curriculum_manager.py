
import logging

logger = logging.getLogger(__name__)

class CurriculumManager:
    """
    Manages difficulty progression.
    """
    def __init__(self):
        self.current_stage = 0
        self.max_stage = 3
        self.history = []
        self.window_size = 10
        self.promotion_threshold = 0.8
        
    def record_success(self, success: bool):
        self.history.append(1 if success else 0)
        if len(self.history) > self.window_size:
            self.history.pop(0)
            
        self._check_promotion()
        
    def _check_promotion(self):
        if len(self.history) < self.window_size:
            return
            
        success_rate = sum(self.history) / len(self.history)
        
        if success_rate >= self.promotion_threshold and self.current_stage < self.max_stage:
            self.current_stage += 1
            self.history = [] # Reset history for new stage
            logger.info(f"Promoted to Stage {self.current_stage}!")
            
    def get_difficulty(self) -> int:
        return self.current_stage

curriculum_manager = CurriculumManager()
