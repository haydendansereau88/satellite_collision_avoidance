import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from satellite import Satellite

class ManeuverPlanner:
    """AI-powered orbital maneuver planning for collision avoidance"""
    
    def __init__(self):
        self.fuel_weight = 0.3  # Importance of fuel efficiency
        self.safety_weight = 0.7  # Importance of collision avoidance
        self.max_delta_v = 10.0  # Maximum velocity change (m/s)
        
    def calculate_maneuver(self, sat1, sat2, collision_time_minutes):
        """Calculate optimal avoidance maneuver using optimization"""
        
        print("\n🚀 CALCULATING OPTIMAL AVOIDANCE MANEUVER")
        print("=" * 60)
        
        # Get current orbital parameters
        current_time = datetime.now()
        pos1, vel1 = sat1.get_position(current_time)
        pos2, vel2 = sat2.get_position(current_time)
        
        # Initial separation
        initial_distance = np.linalg.norm(pos1 - pos2)
        print(f"Current separation: {initial_distance:.2f} km")
        print(f"Time to closest approach: {collision_time_minutes} minutes")
        
        # Define optimization problem
        def objective(delta_v):
            """Minimize fuel usage while maximizing separation"""
            # delta_v = [radial, along-track, cross-track] in m/s
            
            # Calculate new velocity after maneuver
            vel_change = delta_v / 1000  # Convert m/s to km/s
            new_vel = vel1 + vel_change
            
            # Simulate new trajectory (simplified)
            future_time = current_time + timedelta(minutes=collision_time_minutes)
            
            # Propagate with modified velocity (simplified orbital mechanics)
            time_delta = collision_time_minutes * 60  # seconds
            new_pos1 = pos1 + new_vel * time_delta
            
            # Get predicted position of sat2
            pos2_future, _ = sat2.get_position(future_time)
            
            # Calculate miss distance
            miss_distance = np.linalg.norm(new_pos1 - pos2_future)
            
            # Cost function: minimize fuel, maximize miss distance
            fuel_cost = np.linalg.norm(delta_v)
            safety_reward = miss_distance
            
            # Combined objective (we want to minimize this)
            total_cost = self.fuel_weight * fuel_cost - self.safety_weight * safety_reward
            
            return total_cost
        
        # Constraints
        def constraint_fuel(delta_v):
            """Ensure fuel usage is within limits"""
            return self.max_delta_v - np.linalg.norm(delta_v)
        
        def constraint_safety(delta_v):
            """Ensure minimum safe distance"""
            vel_change = delta_v / 1000
            new_vel = vel1 + vel_change
            time_delta = collision_time_minutes * 60
            new_pos1 = pos1 + new_vel * time_delta
            future_time = current_time + timedelta(minutes=collision_time_minutes)
            pos2_future, _ = sat2.get_position(future_time)
            miss_distance = np.linalg.norm(new_pos1 - pos2_future)
            return miss_distance - 25  # Minimum 25 km separation
        
        # Initial guess (small prograde burn)
        x0 = np.array([0, 2, 0])  # m/s in each direction
        
        # Optimization bounds
        bounds = [(-self.max_delta_v, self.max_delta_v)] * 3
        
        # Constraints
        constraints = [
            {'type': 'ineq', 'fun': constraint_fuel},
            {'type': 'ineq', 'fun': constraint_safety}
        ]
        
        # Run optimization
        print("\n🧮 Running optimization algorithm...")
        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 100}
        )
        
        optimal_delta_v = result.x
        
        # Calculate results
        fuel_used = np.linalg.norm(optimal_delta_v)
        
        # Calculate new miss distance
        vel_change = optimal_delta_v / 1000
        new_vel = vel1 + vel_change
        time_delta = collision_time_minutes * 60
        new_pos1 = pos1 + new_vel * time_delta
        future_time = current_time + timedelta(minutes=collision_time_minutes)
        pos2_future, _ = sat2.get_position(future_time)
        new_miss_distance = np.linalg.norm(new_pos1 - pos2_future)
        
        # Determine burn direction
        burn_components = {
            'Radial': optimal_delta_v[0],
            'Along-track': optimal_delta_v[1],
            'Cross-track': optimal_delta_v[2]
        }
        
        primary_burn = max(burn_components.items(), key=lambda x: abs(x[1]))
        
        print("\n✅ MANEUVER CALCULATED SUCCESSFULLY")
        print("-" * 60)
        print(f"Optimal ΔV: {fuel_used:.2f} m/s")
        print(f"Primary burn direction: {primary_burn[0]} ({primary_burn[1]:.2f} m/s)")
        print(f"New miss distance: {new_miss_distance:.2f} km")
        print(f"Fuel efficiency: {(1 - fuel_used/self.max_delta_v)*100:.1f}%")
        
        maneuver = {
            'delta_v': optimal_delta_v,
            'magnitude': fuel_used,
            'direction': primary_burn[0],
            'components': burn_components,
            'new_miss_distance': new_miss_distance,
            'fuel_efficiency': (1 - fuel_used/self.max_delta_v)*100,
            'execution_time': current_time + timedelta(minutes=collision_time_minutes/2)
        }
        
        return maneuver
    
    def generate_maneuver_options(self, sat1, sat2, collision_time):
        """Generate multiple maneuver options with different trade-offs"""
        
        print("\n📋 GENERATING MANEUVER OPTIONS")
        print("=" * 60)
        
        options = []
        
        # Option 1: Minimum fuel
        self.fuel_weight = 0.7
        self.safety_weight = 0.3
        min_fuel = self.calculate_maneuver(sat1, sat2, collision_time)
        min_fuel['name'] = "Fuel Efficient"
        min_fuel['description'] = "Minimum fuel consumption"
        options.append(min_fuel)
        
        # Option 2: Maximum safety
        self.fuel_weight = 0.1
        self.safety_weight = 0.9
        max_safety = self.calculate_maneuver(sat1, sat2, collision_time)
        max_safety['name'] = "Maximum Safety"
        max_safety['description'] = "Largest miss distance"
        options.append(max_safety)
        
        # Option 3: Balanced
        self.fuel_weight = 0.5
        self.safety_weight = 0.5
        balanced = self.calculate_maneuver(sat1, sat2, collision_time)
        balanced['name'] = "Balanced"
        balanced['description'] = "Optimal trade-off"
        options.append(balanced)
        
        return options
    
    def visualize_maneuver(self, maneuver):
        """Create visualization of the maneuver plan"""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Maneuver components
        components = list(maneuver['components'].keys())
        values = list(maneuver['components'].values())
        colors = ['#ff4444', '#44ff44', '#4444ff']
        
        ax1.bar(components, values, color=colors)
        ax1.set_title('Maneuver Components', fontweight='bold')
        ax1.set_ylabel('ΔV (m/s)')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        # Performance metrics
        metrics = {
            'Miss Distance': maneuver['new_miss_distance'],
            'Fuel Used': maneuver['magnitude'],
            'Efficiency': maneuver['fuel_efficiency']
        }
        
        # Create spider plot
        angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False).tolist()
        values_norm = [
            min(100, maneuver['new_miss_distance'] / 2),  # Normalize to 0-100
            (1 - maneuver['magnitude'] / 10) * 100,  # Inverse fuel (less is better)
            maneuver['fuel_efficiency']
        ]
        
        angles += angles[:1]
        values_norm += values_norm[:1]
        
        ax2 = plt.subplot(122, projection='polar')
        ax2.plot(angles, values_norm, 'o-', linewidth=2, color='#00ff41')
        ax2.fill(angles, values_norm, alpha=0.25, color='#00ff41')
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(metrics.keys())
        ax2.set_ylim(0, 100)
        ax2.set_title('Performance Metrics', fontweight='bold', pad=20)
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig('models/maneuver_plan.png', dpi=100, bbox_inches='tight')
        print(f"\n📊 Maneuver visualization saved to models/maneuver_plan.png")
        
        return fig
    
    def calculate_burn_schedule(self, maneuver):
        """Calculate detailed burn schedule for execution"""
        
        schedule = []
        execution_time = maneuver['execution_time']
        
        # Split maneuver into multiple burns if needed
        total_dv = maneuver['magnitude']
        
        if total_dv > 5:  # Split large maneuvers
            # Initial burn
            schedule.append({
                'time': execution_time - timedelta(minutes=10),
                'duration': 30,  # seconds
                'delta_v': maneuver['delta_v'] * 0.6,
                'type': 'Primary burn'
            })
            
            # Correction burn
            schedule.append({
                'time': execution_time,
                'duration': 20,
                'delta_v': maneuver['delta_v'] * 0.4,
                'type': 'Correction burn'
            })
        else:
            # Single burn
            schedule.append({
                'time': execution_time,
                'duration': int(total_dv * 10),  # seconds
                'delta_v': maneuver['delta_v'],
                'type': 'Single burn'
            })
        
        return schedule


def demonstrate_maneuver_planning():
    """Demonstration of maneuver planning capabilities"""
    
    print("=" * 70)
    print("🎯 COLLISION AVOIDANCE MANEUVER PLANNING DEMONSTRATION")
    print("=" * 70)
    
    # Create two satellites on collision course
    iss_tle = [
        "1 25544U 98067A   24001.00000000  .00012345  00000-0  22456-3 0  9990",
        "2 25544  51.6416 339.5000 0001234  45.0000 315.0000 15.54477500300000"
    ]
    
    debris_tle = [
        "1 99999U 09001A   24001.00000000  .00001234  00000-0  12345-4 0  9999",
        "2 99999  51.6400 339.4900 0001450  45.0100 315.0100 15.54475000200000"
    ]
    
    iss = Satellite(iss_tle[0], iss_tle[1], "ISS")
    debris = Satellite(debris_tle[0], debris_tle[1], "DEBRIS-ALPHA")
    
    # Initialize planner
    planner = ManeuverPlanner()
    
    # Calculate maneuver options
    collision_time = 45  # minutes
    options = planner.generate_maneuver_options(iss, debris, collision_time)
    
    print("\n" + "=" * 70)
    print("📊 MANEUVER OPTIONS COMPARISON")
    print("=" * 70)
    
    for i, option in enumerate(options, 1):
        print(f"\n Option {i}: {option['name']}")
        print(f"   Description: {option['description']}")
        print(f"   ΔV Required: {option['magnitude']:.2f} m/s")
        print(f"   Miss Distance: {option['new_miss_distance']:.2f} km")
        print(f"   Fuel Efficiency: {option['fuel_efficiency']:.1f}%")
        print(f"   Primary Burn: {option['direction']}")
    
    # Select optimal maneuver
    optimal = options[2]  # Balanced option
    print(f"\n✅ RECOMMENDED: {optimal['name']} approach")
    
    # Generate burn schedule
    schedule = planner.calculate_burn_schedule(optimal)
    
    print("\n🔥 BURN SCHEDULE")
    print("-" * 60)
    for burn in schedule:
        print(f"   {burn['type']}")
        print(f"   Time: {burn['time'].strftime('%H:%M:%S')}")
        print(f"   Duration: {burn['duration']} seconds")
        print(f"   ΔV: {np.linalg.norm(burn['delta_v']):.2f} m/s")
    
    # Visualize the maneuver
    planner.visualize_maneuver(optimal)
    
    print("\n✨ Maneuver planning complete!")
    print("   The AI has calculated optimal collision avoidance strategies")
    print("   balancing fuel efficiency with safety margins.")
    
    return optimal


if __name__ == "__main__":
    # Run demonstration
    maneuver = demonstrate_maneuver_planning()
    
    print("\n" + "=" * 70)
    print("🚀 MANEUVER PLANNER READY FOR INTEGRATION")
    print("=" * 70)
    print("\nThis AI-powered maneuver planner can be integrated with:")
    print("  • Real-time collision detection system")
    print("  • Mission control dashboard")
    print("  • Automated collision avoidance system")
    print("  • Satellite command & control interface")