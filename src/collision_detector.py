import numpy as np
from datetime import datetime

class CollisionDetector:
    def __init__(self):
        self.risk_threshold = 50  # km
        
    def calculate_distance(self, sat1_positions, sat2_positions):
        return np.linalg.norm(sat1_positions - sat2_positions, axis=1)
    
    def check_collision_risk(self, sat1, sat2, time_horizon_hours=24):
        # Get future positions
        start = datetime.now()
        pos1 = sat1.propagate_orbit(start, time_horizon_hours, step_minutes=5)
        pos2 = sat2.propagate_orbit(start, time_horizon_hours, step_minutes=5)
        
        # Ensure same length
        min_len = min(len(pos1), len(pos2))
        pos1 = pos1[:min_len]
        pos2 = pos2[:min_len]
        
        distances = self.calculate_distance(pos1, pos2)
        min_distance = np.min(distances)
        min_time_idx = np.argmin(distances)
        
        risk_level = self.classify_risk(min_distance)
        
        return {
            'min_distance_km': min_distance,
            'time_to_closest': min_time_idx * 5,  # minutes
            'risk_level': risk_level,
            'collision_probability': self.get_probability(min_distance)
        }
    
    def classify_risk(self, distance_km):
        if distance_km < 5:
            return "CRITICAL"
        elif distance_km < 25:
            return "HIGH"
        elif distance_km < 50:
            return "MEDIUM"
        return "LOW"
    
    def get_probability(self, distance_km):
        # Simplified probability model
        if distance_km > 100:
            return 0.0
        return np.exp(-distance_km/10) * 100