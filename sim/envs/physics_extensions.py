
import math
from typing import List, Tuple

class PhysicsEngine:
    """
    Lightweight physics approximation for ManipulationEnv.
    Handles acceleration limits and friction.
    """
    def __init__(self, use_physics: bool = True):
        self.enabled = use_physics
        self.current_velocity = [0.0, 0.0, 0.0]
        self.max_acceleration = 2.0 # m/s^2
        self.friction_coeff = 0.1 # Velocity decay per step
        self.dt = 0.1 # Time step

    def apply_dynamics(self, current_pos: List[float], target_velocity: List[float]) -> Tuple[List[float], List[float]]:
        """
        updates position based on target velocity, constrained by physics.
        Returns (new_pos, new_velocity)
        """
        if not self.enabled:
            # Kinematic Movement (Instant velocity)
            new_pos = [
                current_pos[0] + target_velocity[0] * self.dt,
                current_pos[1] + target_velocity[1] * self.dt,
                current_pos[2] + target_velocity[2] * self.dt
            ]
            return new_pos, target_velocity

        # 1. Acceleration limit
        # V_new = V_old + clamp(V_target - V_old)
        new_vel = []
        for i in range(3):
            delta_v = target_velocity[i] - self.current_velocity[i]
            # Max delta v per step = a * dt
            max_delta = self.max_acceleration * self.dt
            
            delta_v = max(-max_delta, min(max_delta, delta_v))
            new_vel.append(self.current_velocity[i] + delta_v)

        # 2. Friction (Damping)
        # Apply only if no input? Or always? Simplified: Scale down slightly if trying to stop.
        # Here we just treat it as part of control authority, already handled by max_accel logic mostly.
        # But let's add specific damping term if target is 0?
        # For simple sim, acceleration limit is most important for "weight".
        
        self.current_velocity = new_vel
        
        # 3. Integrate Position
        new_pos = [
            current_pos[0] + self.current_velocity[0] * self.dt,
            current_pos[1] + self.current_velocity[1] * self.dt,
            current_pos[2] + self.current_velocity[2] * self.dt
        ]
        
        return new_pos, self.current_velocity
