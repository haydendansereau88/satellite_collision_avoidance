# 🛰️ Satellite Collision Avoidance System - Prototype

A **proof-of-concept** system demonstrating AI-powered satellite collision detection and avoidance planning using real orbital mechanics principles and machine learning.

## 📌 Project Status: Prototype/Educational
This is a functional prototype built to demonstrate the application of machine learning to space situational awareness. It is NOT production-ready but shows the core concepts and potential of such a system.

## 🎯 What This Project Actually Does

### ✅ Real Capabilities:
- **Orbital Propagation**: Uses SGP4 (same algorithm as NORAD) to calculate real satellite trajectories
- **Collision Detection**: Identifies when two orbital paths intersect within a danger threshold
- **ML Risk Assessment**: Trained model evaluates collision probability based on orbital parameters
- **Maneuver Calculation**: Demonstrates optimization algorithms for collision avoidance
- **3D Visualization**: Interactive display of satellites, orbits, and collision risks

### ⚠️ Current Limitations:
- Trained on **synthetic data** (real collision data is extremely rare)
- Simplified physics model (doesn't account for atmospheric drag, solar pressure, etc.)
- Basic maneuver planning (real spacecraft have complex constraints)
- Limited to 2-body orbital mechanics (doesn't include moon/sun perturbations)
- TLE data for debris is simulated (not from real space-track.org)

## 🛠️ Technical Implementation

### Core Technologies:
- **Python 3.12**: Primary language
- **SGP4**: Industry-standard orbital propagator
- **Scikit-learn**: ML model comparison (Random Forest, Neural Net, Gradient Boosting)
- **NumPy/SciPy**: Numerical computations and optimization
- **Plotly**: 3D interactive visualizations

### Architecture Decisions:
- **Why Random Forest?**: Best balance of accuracy and interpretability. Feature importance helps understand which orbital parameters matter most.
- **Why not Deep Learning?**: Our feature space is small (6 parameters) and well-understood. Classical ML is more appropriate and explainable.
- **Why SGP4?**: It's what the real space industry uses. Good balance of accuracy and computational efficiency.

## 📊 Performance Metrics

**On Synthetic Test Data:**
- Detection Accuracy: ~95% (for distances <100km)
- Processing Time: <1 second for 10 objects
- Maneuver Optimization: Converges in <100 iterations

**Important Note**: These metrics are on synthetic data generated to simulate collision scenarios. Real-world performance would require validation with actual conjunction data.

## 🚀 Future Development Roadmap

### Phase 1: Data Enhancement
- [ ] Integration with Space-Track.org API for real TLE data
- [ ] Historical conjunction analysis from NASA CARA reports
- [ ] Incorporate real debris field data

### Phase 2: Physics Improvements
- [ ] Add atmospheric drag modeling
- [ ] Include J2 perturbations (Earth's oblateness)
- [ ] Solar radiation pressure effects
- [ ] Multi-body gravitational influences

### Phase 3: ML Enhancements
- [ ] Train on real conjunction data from ESA/NASA
- [ ] Ensemble methods for uncertainty quantification
- [ ] Time-series analysis with LSTM for long-term prediction

### Phase 4: Operational Features
- [ ] Real-time TLE updates
- [ ] Alert system integration
- [ ] Monte Carlo uncertainty analysis
- [ ] Multi-satellite constellation management

## 💡 Use Cases & Applications

**Educational/Research:**
- Demonstrating space situational awareness concepts
- Testing collision avoidance algorithms
- Visualizing orbital mechanics

**Potential Real-World Applications (with further development):**
- Small satellite operators needing basic collision screening
- Educational institutions teaching orbital mechanics
- Rapid prototyping of collision avoidance strategies

## 🏃 Installation & Usage

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/satellite-collision-avoidance.git
cd satellite-collision-avoidance

# Install dependencies
pip install -r requirements.txt

# Train ML models (uses synthetic data)
python src/train_model_simple.py

# Run demonstration
python src/final_demo.py
```

## 📝 Technical Details

### Collision Detection Algorithm
```python
# Simplified explanation
1. Propagate orbits using SGP4
2. Calculate minimum distance between trajectories
3. If distance < threshold: evaluate with ML model
4. ML features: relative_distance, relative_velocity, approach_angle, etc.
5. Output: risk_level and collision_probability
```

### Maneuver Planning
Uses SciPy optimization to minimize:
- Fuel consumption (delta-v)
- While maintaining safe miss distance (>25km)

## ⚖️ Disclaimer

This is a **demonstration project** built for educational purposes and to showcase the application of AI/ML to space operations. It should NOT be used for actual satellite operations without extensive validation, testing, and enhancement.

## 🤝 Contributions

This project is open for improvements! Areas where contributions are welcome:
- Real data integration
- Physics model improvements  
- UI/UX enhancements
- Additional ML algorithms

## 📄 License

MIT License - Feel free to use this for learning and development

## 👨‍💻 Author

[Hayden Dansereau] - Aspiring ML Engineer

---

*Built in a short time span as a rapid prototype to demonstrate the intersection of AI and space technology. The goal was to show how machine learning can enhance space situational awareness, not to replace existing operational systems.*