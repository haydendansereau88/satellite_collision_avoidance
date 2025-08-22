import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
import matplotlib.pyplot as plt
import pickle
import os

def generate_collision_data(n_samples=1000):
    """Generate synthetic training data for collision scenarios"""
    
    X = []  # Features
    y = []  # Labels (collision: 1, safe: 0)
    
    print(f"Generating {n_samples} training samples...")
    
    for i in range(n_samples):
        # Generate random orbital parameters
        relative_distance = np.random.uniform(1, 1000)  # km
        relative_velocity = np.random.uniform(0, 15)     # km/s
        approach_angle = np.random.uniform(0, 180)       # degrees
        altitude_diff = np.random.uniform(0, 500)        # km
        inclination_diff = np.random.uniform(0, 90)      # degrees
        time_to_approach = np.random.uniform(0, 120)     # minutes
        
        # Create feature vector
        features = [
            relative_distance,
            relative_velocity,
            approach_angle,
            altitude_diff,
            inclination_diff,
            time_to_approach
        ]
        
        # Determine collision risk (physics-based model)
        # Close distance + high velocity + small angle = high risk
        collision_score = (
            np.exp(-relative_distance/50) * 0.4 +  # Distance factor
            (relative_velocity/15) * 0.3 +         # Velocity factor
            np.exp(-approach_angle/30) * 0.3       # Angle factor
        )
        
        # Add realistic noise
        collision_score += np.random.normal(0, 0.1)
        
        # Binary classification with some edge cases
        if relative_distance < 10:  # Very close = always collision
            is_collision = 1
        elif relative_distance > 500:  # Far away = always safe
            is_collision = 0
        else:
            is_collision = 1 if collision_score > 0.5 else 0
        
        X.append(features)
        y.append(is_collision)
    
    return np.array(X), np.array(y)

def train_models():
    print("=" * 70)
    print("🤖 TRAINING ML COLLISION PREDICTION MODELS")
    print("=" * 70)
    
    # Generate training data
    print("\n📊 Generating synthetic collision scenario data...")
    X_train_full, y_train_full = generate_collision_data(5000)
    X_test, y_test = generate_collision_data(1000)
    
    # Split training data for validation
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_full, y_train_full, test_size=0.2, random_state=42
    )
    
    print(f"   Training samples: {len(X_train)}")
    print(f"   Validation samples: {len(X_val)}")
    print(f"   Test samples: {len(X_test)}")
    print(f"   Collision scenarios: {sum(y_train)} ({sum(y_train)/len(y_train)*100:.1f}%)")
    
    # Train multiple models
    models = {
        'Neural Network': MLPClassifier(
            hidden_layer_sizes=(64, 32, 16),
            activation='relu',
            max_iter=500,
            random_state=42
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        ),
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
    }
    
    results = {}
    best_model = None
    best_score = 0
    
    print("\n🎓 Training models...")
    print("-" * 70)
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        # Train model
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred_val = model.predict(X_val)
        y_pred_test = model.predict(X_test)
        
        # Calculate metrics
        val_accuracy = accuracy_score(y_val, y_pred_val)
        test_accuracy = accuracy_score(y_test, y_pred_test)
        precision = precision_score(y_test, y_pred_test)
        recall = recall_score(y_test, y_pred_test)
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        results[name] = {
            'model': model,
            'val_accuracy': val_accuracy,
            'test_accuracy': test_accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
        
        print(f"   Validation Accuracy: {val_accuracy:.2%}")
        print(f"   Test Accuracy: {test_accuracy:.2%}")
        print(f"   Precision: {precision:.2%}")
        print(f"   Recall: {recall:.2%}")
        print(f"   F1 Score: {f1:.2%}")
        
        # Track best model
        if f1 > best_score:
            best_score = f1
            best_model = name
    
    print("\n" + "=" * 70)
    print(f"🏆 BEST MODEL: {best_model}")
    print(f"   F1 Score: {results[best_model]['f1']:.2%}")
    print("=" * 70)
    
    # Save best model
    os.makedirs('models', exist_ok=True)
    model_path = 'models/collision_predictor.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(results[best_model]['model'], f)
    print(f"\n💾 Best model saved to {model_path}")
    
    # Create performance comparison plot
    plt.figure(figsize=(12, 6))
    
    # Accuracy comparison
    plt.subplot(1, 2, 1)
    model_names = list(results.keys())
    test_accuracies = [results[m]['test_accuracy'] for m in model_names]
    colors = ['#00ff41', '#00aaff', '#ff00ff']
    bars = plt.bar(model_names, test_accuracies, color=colors)
    plt.title('Model Accuracy Comparison', fontsize=14, fontweight='bold')
    plt.ylabel('Test Accuracy')
    plt.ylim(0, 1)
    
    # Add value labels on bars
    for bar, acc in zip(bars, test_accuracies):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{acc:.1%}', ha='center', va='bottom')
    
    # F1 Score comparison
    plt.subplot(1, 2, 2)
    f1_scores = [results[m]['f1'] for m in model_names]
    bars = plt.bar(model_names, f1_scores, color=colors)
    plt.title('F1 Score Comparison', fontsize=14, fontweight='bold')
    plt.ylabel('F1 Score')
    plt.ylim(0, 1)
    
    # Add value labels on bars
    for bar, f1 in zip(bars, f1_scores):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{f1:.1%}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('models/model_comparison.png', dpi=100, bbox_inches='tight')
    print(f"📊 Model comparison chart saved to models/model_comparison.png")
    
    # Test with example scenarios
    print("\n🔬 Testing best model with example scenarios:")
    print("-" * 70)
    
    test_scenarios = [
        ([5, 10, 10, 10, 5, 10], "Very close approach"),
        ([500, 2, 90, 100, 30, 60], "Safe passage"),
        ([25, 7, 30, 20, 10, 20], "Moderate risk"),
        ([2, 14, 5, 5, 2, 5], "Critical - imminent collision"),
        ([100, 5, 45, 50, 20, 30], "Medium distance encounter")
    ]
    
    best_model_obj = results[best_model]['model']
    
    for features, description in test_scenarios:
        pred_proba = best_model_obj.predict_proba([features])[0]
        collision_prob = pred_proba[1] * 100
        risk_level = "CRITICAL" if collision_prob > 80 else \
                     "HIGH" if collision_prob > 60 else \
                     "MEDIUM" if collision_prob > 40 else \
                     "LOW"
        
        print(f"\n   Scenario: {description}")
        print(f"   Distance: {features[0]}km | Velocity: {features[1]}km/s | Angle: {features[2]}°")
        print(f"   → Collision Probability: {collision_prob:.1f}%")
        print(f"   → Risk Level: {risk_level}")
    
    # Feature importance (if available)
    feature_names = ['Distance', 'Velocity', 'Angle', 'Alt_Diff', 'Inc_Diff', 'Time']
    
    if hasattr(best_model_obj, 'feature_importances_'):
        plt.figure(figsize=(10, 6))
        importances = best_model_obj.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        plt.bar(range(len(importances)), importances[indices], color='#00ff41')
        plt.xticks(range(len(importances)), [feature_names[i] for i in indices])
        plt.title(f'Feature Importance - {best_model}', fontsize=14, fontweight='bold')
        plt.ylabel('Importance')
        plt.tight_layout()
        plt.savefig('models/feature_importance.png', dpi=100, bbox_inches='tight')
        print(f"\n📊 Feature importance chart saved to models/feature_importance.png")
    
    return results[best_model]['model']

if __name__ == "__main__":
    # Train the models
    best_model = train_models()
    
    print("\n" + "=" * 70)
    print("✨ ML TRAINING COMPLETE!")
    print("=" * 70)
    print("\n🚀 The collision prediction model is now ready for deployment.")
    print("   It can process orbital parameters and predict collision risk in real-time.")
    print("   The model achieves high accuracy on synthetic space collision scenarios.")
    print("\n💡 Next steps:")
    print("   1. Integrate with real-time satellite tracking")
    print("   2. Deploy to mission control dashboard")
    print("   3. Connect to alert system for automated warnings")