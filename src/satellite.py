import numpy as np
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta

class Satellite:
    def __init__(self, tle_line1, tle_line2, name="UNKNOWN"):
        self.name = name
        self.satrec = Satrec.twoline2rv(tle_line1, tle_line2)
        self.positions = []
        self.times = []
    
    def get_position(self, dt):
        jd, fr = jday(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        e, r, v = self.satrec.sgp4(jd, fr)
        if e != 0:  # error check
            return np.array([0, 0, 0]), np.array([0, 0, 0])
        return np.array(r), np.array(v)  # km, km/s
    
    def propagate_orbit(self, start_time, duration_hours, step_minutes=1):
        self.positions = []
        self.times = []
        current = start_time
        end = start_time + timedelta(hours=duration_hours)
        
        while current <= end:
            pos, vel = self.get_position(current)
            self.positions.append(pos)
            self.times.append(current)
            current += timedelta(minutes=step_minutes)
        
        return np.array(self.positions)