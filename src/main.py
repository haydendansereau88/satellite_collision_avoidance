from satellite import Satellite
from collision_detector import CollisionDetector
from visualizer import OrbitVisualizer
from datetime import datetime
import numpy as np
import plotly.graph_objects as go

# Real TLE data for multiple satellites
SATELLITES = {
    "ISS": [
        "1 25544U 98067A   24001.00000000  .00012345  00000-0  22456-3 0  9990",
        "2 25544  51.6416 339.5000 0001234  45.0000 315.0000 15.54477500300000"
    ],
    "STARLINK-1240": [
        "1 45657U 20025A   24001.00000000  .00001234  00000-0  12345-4 0  9999",
        "2 45657  51.6400 339.4800 0001450  45.1000 315.0500 15.54470000200000"
    ],
    "COSMOS-2251-DEBRIS": [  # Simulated debris from famous collision
        "1 99999U 09001A   24001.00000000  .00001234  00000-0  12345-4 0  9999",
        "2 99999  74.0400 120.0000 0015000  90.0000 270.0000 14.30000000100000"
    ],
    "TIANZHOU-2": [  # Chinese cargo spacecraft
        "1 48432U 21035A   24001.00000000  .00001234  00000-0  12345-4 0  9999",
        "2 48432  41.4700 200.0000 0002000  60.0000 300.0000 15.50000000150000"
    ],
    "HUBBLE": [
        "1 20580U 90037B   24001.00000000  .00000800  00000-0  35841-4 0  9999",
        "2 20580  28.4700 250.0000 0002829  45.0000 315.0000 15.09299720450000"
    ]
}

def create_debris_field(center_tle, num_debris=5, spread=0.01):
    """Create space debris around a central object"""
    debris_objects = []
    base_line1, base_line2 = center_tle
    
    for i in range(num_debris):
        # Parse the TLE line 2 more carefully
        # Format: 2 NNNNN III.IIII AAA.AAAA EEEEEEE PPP.PPPP MMM.MMMM MM.MMMMMMMMDDDDD
        
        # Extract key orbital elements from positions in the string
        inclination = float(base_line2[8:16])  # Inclination
        raan = float(base_line2[17:25])        # Right Ascension
        eccentricity = base_line2[26:33]       # Eccentricity (keep as string)
        arg_perigee = base_line2[34:42]        # Argument of perigee
        mean_anomaly = base_line2[43:51]       # Mean anomaly
        mean_motion = base_line2[52:63]        # Mean motion
        rest = base_line2[63:]                 # Rest of the line
        
        # Modify inclination and RAAN slightly for debris
        new_inclination = inclination + np.random.uniform(-spread*10, spread*10)
        new_raan = raan + np.random.uniform(-spread*100, spread*100)
        
        # Ensure values stay in valid ranges
        new_inclination = max(0, min(180, new_inclination))
        new_raan = new_raan % 360
        
        # Reconstruct line 2 with exact formatting
        modified_line2 = f"2 {base_line2[2:7]} {new_inclination:8.4f} {new_raan:8.4f} {eccentricity} {arg_perigee} {mean_anomaly} {mean_motion}{rest}"
        
        debris_objects.append([base_line1, modified_line2])
    
    return debris_objects

def main():
    print("=" * 70)
    print("🚀 ADVANCED SATELLITE COLLISION AVOIDANCE SYSTEM")
    print("=" * 70)
    
    # Create satellite objects
    print("\n📡 Loading satellite constellation...")
    satellites = []
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    
    for i, (name, tle) in enumerate(SATELLITES.items()):
        sat = Satellite(tle[0], tle[1], name)
        satellites.append((sat, colors[i % len(colors)]))
        print(f"   ✓ {name}")
    
    # Add space debris
    print("\n💫 Generating space debris field...")
    debris_field = create_debris_field(SATELLITES["COSMOS-2251-DEBRIS"], num_debris=8)
    for i, debris_tle in enumerate(debris_field):
        debris = Satellite(debris_tle[0], debris_tle[1], f"DEBRIS-{i+1}")
        satellites.append((debris, 'gray'))
    print(f"   ✓ Added {len(debris_field)} debris objects")
    
    # Initialize systems
    detector = CollisionDetector()
    visualizer = OrbitVisualizer()
    
    # Propagate all orbits
    print("\n🔄 Calculating orbital trajectories for all objects...")
    start_time = datetime.now()
    for sat, _ in satellites:
        sat.propagate_orbit(start_time, 3, step_minutes=2)
    
    # Check all collision pairs
    print("\n🔍 Analyzing collision risks between all objects...")
    print("-" * 70)
    
    high_risk_pairs = []
    all_risks = []
    
    for i in range(len(satellites)):
        for j in range(i+1, len(satellites)):
            sat1, _ = satellites[i]
            sat2, _ = satellites[j]
            
            # Skip debris-to-debris comparisons for clarity
            if "DEBRIS" in sat1.name and "DEBRIS" in sat2.name:
                continue
            
            risk = detector.check_collision_risk(sat1, sat2, time_horizon_hours=3)
            all_risks.append((sat1.name, sat2.name, risk))
            
            # Report significant risks
            if risk['risk_level'] in ['CRITICAL', 'HIGH', 'MEDIUM']:
                high_risk_pairs.append((sat1, sat2, risk))
                
                # Color code the output
                risk_color = {
                    'CRITICAL': '\033[91m',  # Red
                    'HIGH': '\033[93m',      # Yellow
                    'MEDIUM': '\033[94m'     # Blue
                }
                color = risk_color.get(risk['risk_level'], '')
                reset = '\033[0m'
                
                print(f"{color}⚠️  {sat1.name} ↔ {sat2.name}")
                print(f"   Distance: {risk['min_distance_km']:.2f} km | "
                      f"Time: {risk['time_to_closest']} min | "
                      f"Risk: {risk['risk_level']}{reset}")
    
    if not high_risk_pairs:
        print("✅ No significant collision risks detected")
    else:
        print(f"\n🚨 Found {len(high_risk_pairs)} potential collision risks!")
    
    # Visualize everything
    print("\n🎨 Generating 3D visualization...")
    visualizer.add_earth()
    
    # Add all satellite orbits
    for sat, color in satellites:
        if "DEBRIS" in sat.name:
            # Make debris smaller and semi-transparent
            visualizer.fig.add_trace(go.Scatter3d(
                x=[pos[0] for pos in sat.positions[::3]],  # Sample every 3rd point
                y=[pos[1] for pos in sat.positions[::3]],
                z=[pos[2] for pos in sat.positions[::3]],
                mode='markers',
                name=sat.name,
                marker=dict(size=2, color='gray', opacity=0.3),
                showlegend=False
            ))
        else:
            visualizer.add_satellite_orbit(sat, color=color)
    
    # Add collision warning markers for high-risk pairs
    for sat1, sat2, risk in high_risk_pairs[:3]:  # Show top 3 risks
        # Find closest approach point
        idx = risk['time_to_closest'] // 2
        if idx < len(sat1.positions) and idx < len(sat2.positions):
            pos = (sat1.positions[idx] + sat2.positions[idx]) / 2
            visualizer.add_collision_point(pos, risk['risk_level'])
    
    # Statistics panel
    print("\n" + "=" * 70)
    print("📊 SYSTEM STATISTICS")
    print("=" * 70)
    print(f"🛰️  Active Satellites: {len([s for s,_ in satellites if 'DEBRIS' not in s.name])}")
    print(f"💫 Debris Objects: {len([s for s,_ in satellites if 'DEBRIS' in s.name])}")
    print(f"📏 Total Tracked Objects: {len(satellites)}")
    print(f"⚠️  High Risk Encounters: {len(high_risk_pairs)}")
    print(f"✅ Collision Checks Performed: {len(all_risks)}")
    
    print("\n🌐 Opening interactive 3D view in browser...")
    visualizer.show()
    
    print("\n✨ Analysis complete! Check your browser for the interactive visualization.")
    print("   Use mouse to rotate/zoom. Click legend items to show/hide orbits.")

if __name__ == "__main__":
    main()