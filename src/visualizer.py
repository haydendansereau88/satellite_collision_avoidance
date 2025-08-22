import plotly.graph_objects as go
import numpy as np

class EnhancedOrbitVisualizer:
    def __init__(self):
        self.fig = go.Figure()
        self.earth_radius = 6371  # km
        
    def add_earth(self):
        """Create Earth sphere with better texturing"""
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = self.earth_radius * np.outer(np.cos(u), np.sin(v))
        y = self.earth_radius * np.outer(np.sin(u), np.sin(v))
        z = self.earth_radius * np.outer(np.ones(np.size(u)), np.cos(v))
        
        self.fig.add_trace(go.Surface(
            x=x, y=y, z=z,
            colorscale=[
                [0, 'rgb(0, 0, 130)'],     # Deep ocean
                [0.5, 'rgb(0, 100, 200)'],  # Ocean
                [1, 'rgb(0, 150, 255)']     # Shallow ocean
            ],
            showscale=False,
            opacity=0.8,
            name='Earth',
            lighting=dict(
                ambient=0.6,
                diffuse=0.8,
                specular=0.2,
                roughness=0.5
            ),
            lightposition=dict(x=100000, y=100000, z=100000)
        ))
        
        # Add Earth grid lines for reference
        for lat in [-60, -30, 0, 30, 60]:
            theta = np.linspace(0, 2*np.pi, 100)
            x_lat = self.earth_radius * np.cos(np.radians(lat)) * np.cos(theta)
            y_lat = self.earth_radius * np.cos(np.radians(lat)) * np.sin(theta)
            z_lat = np.full_like(theta, self.earth_radius * np.sin(np.radians(lat)))
            
            self.fig.add_trace(go.Scatter3d(
                x=x_lat, y=y_lat, z=z_lat,
                mode='lines',
                line=dict(color='gray', width=1),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    def add_satellite_orbit_with_trail(self, satellite, color='red', show_collision_zone=False):
        """Add satellite orbit with motion trail and optional collision zone"""
        positions = np.array(satellite.positions)
        
        if len(positions) > 0:
            # Main orbit line
            self.fig.add_trace(go.Scatter3d(
                x=positions[:, 0],
                y=positions[:, 1],
                z=positions[:, 2],
                mode='lines',
                name=f'{satellite.name} orbit',
                line=dict(color=color, width=3),
                opacity=0.8,
                hovertemplate='%{hovertext}<br>Position: (%{x:.0f}, %{y:.0f}, %{z:.0f}) km',
                hovertext=[satellite.name] * len(positions)
            ))
            
            # Trail effect (last 10 positions with decreasing opacity)
            trail_length = min(10, len(positions))
            for i in range(trail_length):
                opacity = 1.0 - (i / trail_length) * 0.7
                size = 8 - i * 0.5
                
                self.fig.add_trace(go.Scatter3d(
                    x=[positions[i, 0]],
                    y=[positions[i, 1]],
                    z=[positions[i, 2]],
                    mode='markers',
                    marker=dict(size=size, color=color, opacity=opacity),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # Current position (large marker)
            self.fig.add_trace(go.Scatter3d(
                x=[positions[0, 0]],
                y=[positions[0, 1]],
                z=[positions[0, 2]],
                mode='markers+text',
                name=f'{satellite.name}',
                marker=dict(
                    size=12,
                    color=color,
                    symbol='diamond',
                    line=dict(color='white', width=2)
                ),
                text=[satellite.name],
                textposition='top center',
                textfont=dict(color=color, size=10)
            ))
            
            # Velocity vector
            if len(positions) > 1:
                vel_vector = (positions[1] - positions[0]) * 5  # Scale for visibility
                self.fig.add_trace(go.Cone(
                    x=[positions[0, 0]],
                    y=[positions[0, 1]],
                    z=[positions[0, 2]],
                    u=[vel_vector[0]],
                    v=[vel_vector[1]],
                    w=[vel_vector[2]],
                    colorscale=[[0, color], [1, color]],
                    showscale=False,
                    name=f'{satellite.name} velocity',
                    hoverinfo='skip'
                ))
    
    def add_collision_zone(self, position, risk_level, distance_km):
        """Add a collision danger zone visualization"""
        # Create a sphere around the collision point
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 20)
        
        # Size based on minimum safe distance
        radius = max(25, distance_km)  # At least 25km visualization
        
        x = radius * np.outer(np.cos(u), np.sin(v)) + position[0]
        y = radius * np.outer(np.sin(u), np.sin(v)) + position[1]
        z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + position[2]
        
        colors = {
            'CRITICAL': 'rgba(255, 0, 0, 0.3)',
            'HIGH': 'rgba(255, 165, 0, 0.3)',
            'MEDIUM': 'rgba(255, 255, 0, 0.2)',
            'LOW': 'rgba(0, 255, 0, 0.1)'
        }
        
        self.fig.add_trace(go.Surface(
            x=x, y=y, z=z,
            colorscale=[[0, colors.get(risk_level, 'rgba(128,128,128,0.2)')], 
                       [1, colors.get(risk_level, 'rgba(128,128,128,0.2)')]],
            showscale=False,
            opacity=0.3,
            name=f'Collision Zone ({risk_level})',
            hovertemplate=f'Danger Zone<br>Risk: {risk_level}<br>Min Distance: {distance_km:.1f} km'
        ))
        
        # Add warning marker at center
        self.fig.add_trace(go.Scatter3d(
            x=[position[0]],
            y=[position[1]],
            z=[position[2]],
            mode='markers+text',
            marker=dict(
                size=20,
                color='red' if risk_level == 'CRITICAL' else 'orange',
                symbol='x',
                line=dict(color='white', width=3)
            ),
            text=[f'⚠️ {risk_level}'],
            textposition='top center',
            textfont=dict(color='white', size=12),
            name=f'Collision Point',
            hovertemplate=f'Closest Approach Point<br>Risk Level: {risk_level}<br>Distance: {distance_km:.1f} km'
        ))
    
    def add_avoidance_maneuver(self, satellite_pos, delta_v, new_trajectory):
        """Visualize the avoidance maneuver"""
        # Original trajectory continues (dashed, semi-transparent)
        self.fig.add_trace(go.Scatter3d(
            x=[p[0] for p in new_trajectory],
            y=[p[1] for p in new_trajectory],
            z=[p[2] for p in new_trajectory],
            mode='lines',
            line=dict(color='green', width=4, dash='dot'),
            name='Avoidance Trajectory',
            opacity=0.7,
            hovertemplate='New safe trajectory after maneuver'
        ))
        
        # Maneuver burn vector
        burn_vector = delta_v * 1000  # Scale for visibility
        self.fig.add_trace(go.Cone(
            x=[satellite_pos[0]],
            y=[satellite_pos[1]],
            z=[satellite_pos[2]],
            u=[burn_vector[0]],
            v=[burn_vector[1]],
            w=[burn_vector[2]],
            colorscale=[[0, 'lime'], [1, 'lime']],
            showscale=False,
            name='Maneuver Burn',
            hovertemplate=f'ΔV: {np.linalg.norm(delta_v):.2f} m/s'
        ))
    
    def add_info_panel(self, satellites, collision_events):
        """Add information annotations"""
        info_text = f"<b>SPACE SITUATIONAL AWARENESS</b><br>"
        info_text += f"Tracking: {len(satellites)} objects<br>"
        
        if collision_events:
            info_text += f"<br><b>⚠️ COLLISION RISKS:</b><br>"
            for event in collision_events[:3]:
                info_text += f"• {event['risk']['risk_level']}: "
                info_text += f"{event['obj1'].name[:10]} ↔ {event['obj2'].name[:10]}<br>"
                info_text += f"  Distance: {event['risk']['min_distance_km']:.1f} km<br>"
        
        self.fig.add_annotation(
            text=info_text,
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            bordercolor="white",
            borderwidth=1,
            bgcolor="rgba(0,0,0,0.8)",
            font=dict(color="white", size=10),
            align="left"
        )
    
    def show_professional(self):
        """Display with professional settings"""
        self.fig.update_layout(
            scene=dict(
                xaxis=dict(
                    title='X (km)',
                    backgroundcolor="rgb(10, 10, 30)",
                    gridcolor="gray",
                    showbackground=True,
                    zerolinecolor="gray",
                ),
                yaxis=dict(
                    title='Y (km)',
                    backgroundcolor="rgb(10, 10, 30)",
                    gridcolor="gray",
                    showbackground=True,
                    zerolinecolor="gray"
                ),
                zaxis=dict(
                    title='Z (km)',
                    backgroundcolor="rgb(10, 10, 30)",
                    gridcolor="gray",
                    showbackground=True,
                    zerolinecolor="gray"
                ),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=0.7),
                    center=dict(x=0, y=0, z=0)
                ),
                aspectmode='cube'
            ),
            title={
                'text': '🛰️ SATELLITE COLLISION AVOIDANCE SYSTEM<br><sub>Real-Time Orbital Tracking & Collision Prevention</sub>',
                'font': {'size': 20, 'color': 'white'},
                'x': 0.5,
                'xanchor': 'center'
            },
            paper_bgcolor='rgb(10, 10, 30)',
            plot_bgcolor='rgb(10, 10, 30)',
            showlegend=True,
            legend=dict(
                bgcolor='rgba(0,0,0,0.5)',
                font=dict(color='white'),
                bordercolor='white',
                borderwidth=1
            ),
            height=800,
            margin=dict(l=0, r=0, t=60, b=0)
        )
        
        self.fig.show()