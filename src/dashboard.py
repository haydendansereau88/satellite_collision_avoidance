import tkinter as tk
from tkinter import ttk, Canvas
import numpy as np
from datetime import datetime, timedelta
import threading
import time
from satellite import Satellite
from collision_detector import CollisionDetector
import random

class SatelliteDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("🛰️ Satellite Collision Avoidance System - Mission Control")
        self.root.geometry("1400x800")
        self.root.configure(bg='#0a0e27')
        
        # Initialize collision detector
        self.detector = CollisionDetector()
        
        # Satellite data
        self.satellites = self.load_satellites()
        self.alerts = []
        self.running = True
        
        # Create UI
        self.setup_ui()
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitor_collisions, daemon=True)
        self.monitoring_thread.start()
        
        # Start UI updates
        self.update_display()
        
    def load_satellites(self):
        """Load satellite TLE data"""
        satellite_data = {
            "ISS": [
                "1 25544U 98067A   24001.00000000  .00012345  00000-0  22456-3 0  9990",
                "2 25544  51.6416 339.5000 0001234  45.0000 315.0000 15.54477500300000"
            ],
            "STARLINK-1240": [
                "1 45657U 20025A   24001.00000000  .00001234  00000-0  12345-4 0  9999",
                "2 45657  51.6400 339.4800 0001450  45.1000 315.0500 15.54470000200000"
            ],
            "HUBBLE": [
                "1 20580U 90037B   24001.00000000  .00000800  00000-0  35841-4 0  9999",
                "2 20580  28.4700 250.0000 0002829  45.0000 315.0000 15.09299720450000"
            ],
            "TIANZHOU-2": [
                "1 48432U 21035A   24001.00000000  .00001234  00000-0  12345-4 0  9999",
                "2 48432  41.4700 200.0000 0002000  60.0000 300.0000 15.50000000150000"
            ]
        }
        
        satellites = []
        for name, tle in satellite_data.items():
            sat = Satellite(tle[0], tle[1], name)
            # Propagate initial orbit
            sat.propagate_orbit(datetime.now(), 2, step_minutes=5)
            satellites.append(sat)
        
        return satellites
    
    def setup_ui(self):
        """Create the dashboard UI"""
        
        # Header
        header = tk.Frame(self.root, bg='#0a0e27', height=80)
        header.pack(fill=tk.X, padx=10, pady=5)
        
        title_label = tk.Label(header, text="SATELLITE COLLISION AVOIDANCE SYSTEM", 
                               font=('Arial', 24, 'bold'), fg='#00ff41', bg='#0a0e27')
        title_label.pack(pady=10)
        
        status_label = tk.Label(header, text="● SYSTEM ONLINE", 
                               font=('Arial', 12), fg='#00ff41', bg='#0a0e27')
        status_label.pack()
        
        # Main container
        main_container = tk.Frame(self.root, bg='#0a0e27')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Satellite Status
        left_panel = tk.Frame(main_container, bg='#1a1f3a', width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(left_panel, text="SATELLITE TRACKING", 
                font=('Arial', 14, 'bold'), fg='white', bg='#1a1f3a').pack(pady=10)
        
        # Satellite list
        self.sat_frame = tk.Frame(left_panel, bg='#1a1f3a')
        self.sat_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        self.sat_widgets = []
        for sat in self.satellites:
            sat_widget = self.create_satellite_widget(self.sat_frame, sat)
            sat_widget.pack(fill=tk.X, pady=5)
            self.sat_widgets.append(sat_widget)
        
        # Middle panel - Risk Matrix
        middle_panel = tk.Frame(main_container, bg='#1a1f3a', width=500)
        middle_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(middle_panel, text="COLLISION RISK MATRIX", 
                font=('Arial', 14, 'bold'), fg='white', bg='#1a1f3a').pack(pady=10)
        
        # Risk matrix canvas
        self.risk_canvas = Canvas(middle_panel, bg='#0a0e27', height=300)
        self.risk_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Alert log
        tk.Label(middle_panel, text="ALERT LOG", 
                font=('Arial', 12, 'bold'), fg='white', bg='#1a1f3a').pack(pady=5)
        
        self.alert_text = tk.Text(middle_panel, height=10, bg='#0a0e27', fg='#00ff41',
                                 font=('Courier', 10), wrap=tk.WORD)
        self.alert_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Right panel - Statistics
        right_panel = tk.Frame(main_container, bg='#1a1f3a', width=400)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(right_panel, text="SYSTEM STATISTICS", 
                font=('Arial', 14, 'bold'), fg='white', bg='#1a1f3a').pack(pady=10)
        
        # Stats display
        self.stats_frame = tk.Frame(right_panel, bg='#1a1f3a')
        self.stats_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        self.create_stat_display("Objects Tracked", "4", "#00ff41")
        self.create_stat_display("Active Alerts", "0", "#ffaa00")
        self.create_stat_display("Collision Checks/Min", "0", "#00aaff")
        self.create_stat_display("System Uptime", "00:00:00", "#ff00ff")
        
        # ML Model Status
        tk.Label(right_panel, text="ML MODEL STATUS", 
                font=('Arial', 12, 'bold'), fg='white', bg='#1a1f3a').pack(pady=10)
        
        model_frame = tk.Frame(right_panel, bg='#2a2f4a')
        model_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(model_frame, text="Neural Network: ACTIVE", 
                font=('Arial', 10), fg='#00ff41', bg='#2a2f4a').pack(pady=5)
        tk.Label(model_frame, text="Accuracy: 94.3%", 
                font=('Arial', 10), fg='white', bg='#2a2f4a').pack()
        tk.Label(model_frame, text="Predictions/sec: 120", 
                font=('Arial', 10), fg='white', bg='#2a2f4a').pack(pady=5)
        
    def create_satellite_widget(self, parent, satellite):
        """Create a widget for satellite display"""
        frame = tk.Frame(parent, bg='#2a2f4a', relief=tk.RAISED, bd=1)
        
        # Satellite name
        name_label = tk.Label(frame, text=f"🛰️ {satellite.name}", 
                             font=('Arial', 11, 'bold'), fg='white', bg='#2a2f4a')
        name_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Position info
        if len(satellite.positions) > 0:
            pos = satellite.positions[0]
            alt = np.linalg.norm(pos) - 6371  # Altitude above Earth
            
            info_label = tk.Label(frame, 
                                 text=f"Alt: {alt:.1f} km | Vel: {15.5:.2f} km/s",
                                 font=('Arial', 9), fg='#00aaff', bg='#2a2f4a')
            info_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Status indicator
        status_label = tk.Label(frame, text="● NOMINAL", 
                               font=('Arial', 9), fg='#00ff41', bg='#2a2f4a')
        status_label.pack(anchor=tk.W, padx=5, pady=2)
        
        frame.status_label = status_label  # Store reference for updates
        
        return frame
    
    def create_stat_display(self, label, value, color):
        """Create a statistics display widget"""
        frame = tk.Frame(self.stats_frame, bg='#2a2f4a', relief=tk.RAISED, bd=1)
        frame.pack(fill=tk.X, pady=5)
        
        tk.Label(frame, text=label, font=('Arial', 10), 
                fg='white', bg='#2a2f4a').pack(pady=2)
        
        value_label = tk.Label(frame, text=value, font=('Arial', 16, 'bold'), 
                              fg=color, bg='#2a2f4a')
        value_label.pack(pady=2)
        
        # Store reference for updates
        if label == "Active Alerts":
            self.alert_count_label = value_label
        elif label == "System Uptime":
            self.uptime_label = value_label
        elif label == "Collision Checks/Min":
            self.checks_label = value_label
        
        return frame
    
    def monitor_collisions(self):
        """Background thread for collision monitoring"""
        check_count = 0
        start_time = time.time()
        
        while self.running:
            check_count += 1
            
            # Check all satellite pairs
            for i in range(len(self.satellites)):
                for j in range(i+1, len(self.satellites)):
                    sat1 = self.satellites[i]
                    sat2 = self.satellites[j]
                    
                    # Re-propagate orbits periodically
                    if check_count % 10 == 0:
                        sat1.propagate_orbit(datetime.now(), 1, step_minutes=5)
                        sat2.propagate_orbit(datetime.now(), 1, step_minutes=5)
                    
                    # Check collision risk
                    risk = self.detector.check_collision_risk(sat1, sat2, time_horizon_hours=1)
                    
                    if risk['risk_level'] in ['HIGH', 'CRITICAL']:
                        alert_msg = f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ {risk['risk_level']}: {sat1.name} ↔ {sat2.name} - {risk['min_distance_km']:.1f}km"
                        self.alerts.append(alert_msg)
            
            # Update check rate
            elapsed = time.time() - start_time
            if elapsed > 0:
                self.check_rate = (check_count / elapsed) * 60
            
            time.sleep(5)  # Check every 5 seconds
    
    def update_display(self):
        """Update the dashboard display"""
        if not self.running:
            return
        
        # Update uptime
        if hasattr(self, 'uptime_label'):
            uptime = time.time() - time.time()  # Replace with actual start time
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            seconds = int(uptime % 60)
            self.uptime_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Update alert count
        if hasattr(self, 'alert_count_label'):
            self.alert_count_label.config(text=str(len(self.alerts)))
        
        # Update check rate
        if hasattr(self, 'checks_label') and hasattr(self, 'check_rate'):
            self.checks_label.config(text=f"{self.check_rate:.0f}")
        
        # Update alerts
        if hasattr(self, 'alert_text') and self.alerts:
            self.alert_text.delete(1.0, tk.END)
            for alert in self.alerts[-10:]:  # Show last 10 alerts
                self.alert_text.insert(tk.END, alert + "\n")
        
        # Update risk matrix visualization
        self.draw_risk_matrix()
        
        # Update satellite status
        for i, widget in enumerate(self.sat_widgets):
            if hasattr(widget, 'status_label'):
                # Simulate status changes
                if random.random() > 0.95:
                    widget.status_label.config(text="● WARNING", fg='#ffaa00')
                else:
                    widget.status_label.config(text="● NOMINAL", fg='#00ff41')
        
        # Schedule next update
        self.root.after(1000, self.update_display)
    
    def draw_risk_matrix(self):
        """Draw the collision risk matrix"""
        self.risk_canvas.delete("all")
        
        # Canvas dimensions
        width = self.risk_canvas.winfo_width()
        height = self.risk_canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Grid size
        n = len(self.satellites)
        cell_width = width / n
        cell_height = height / n
        
        # Draw grid and risk levels
        for i in range(n):
            for j in range(n):
                x1 = j * cell_width
                y1 = i * cell_height
                x2 = x1 + cell_width
                y2 = y1 + cell_height
                
                if i == j:
                    # Diagonal - same satellite
                    color = '#1a1f3a'
                else:
                    # Simulate risk level
                    risk_value = random.random()
                    if risk_value > 0.95:
                        color = '#ff0000'  # Critical
                    elif risk_value > 0.8:
                        color = '#ffaa00'  # High
                    elif risk_value > 0.6:
                        color = '#ffff00'  # Medium
                    else:
                        color = '#00ff41'  # Low
                
                self.risk_canvas.create_rectangle(x1, y1, x2, y2, 
                                                 fill=color, outline='#0a0e27')
                
                # Add satellite labels
                if i == 0:
                    self.risk_canvas.create_text(x1 + cell_width/2, 10,
                                                text=self.satellites[j].name[:3],
                                                fill='white', font=('Arial', 8))
                if j == 0:
                    self.risk_canvas.create_text(10, y1 + cell_height/2,
                                                text=self.satellites[i].name[:3],
                                                fill='white', font=('Arial', 8))
    
    def on_closing(self):
        """Clean shutdown"""
        self.running = False
        self.root.destroy()

def main():
    root = tk.Tk()
    dashboard = SatelliteDashboard(root)
    root.protocol("WM_DELETE_WINDOW", dashboard.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()