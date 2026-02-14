# ML Models & Activation Functions Guide
### Overlap Resolution v3.0 - Advanced Features

---

## Overview

This guide documents the **Machine Learning (ML) models** and **Activation Functions** integrated into the overlap resolution system. These features enable:

1. **Intelligent parameter prediction** using ML regression/classification
2. **Non-linear transformations** via activation functions
3. **Hybrid optimization** combining heuristic and ML-driven approaches

---

## 1. Activation Functions

### Available Functions

The system includes **9 activation functions** for non-linear transformations:

| Function | Formula | Use Case | Derivative |
|----------|---------|----------|------------|
| **ReLU** | `max(0, x)` | Sparse gradients, fast | `1 if x>0 else 0` |
| **LeakyReLU** | `x if x>0 else 0.01x` | Prevents dead neurons | `1 if x>0 else 0.01` |
| **Sigmoid** | `1/(1+e^-x)` | Bounded outputs [0,1] | `σ(x)*(1-σ(x))` |
| **Tanh** | `tanh(x)` | Zero-centered [-1,1] | `1 - tanh²(x)` |
| **ELU** | `x if x>0 else α(e^x-1)` | Smooth negatives | `1 if x>0 else ELU(x)+α` |
| **SoftPlus** | `ln(1+e^x)` | Smooth ReLU | `1/(1+e^-x)` |
| **Swish** | `x*sigmoid(x)` | Self-gated, smooth | `swish + σ(x)*(1-swish)` |
| **GELU** | `x*Φ(x)` | Transformer standard | Complex (approximated) |
| **Linear** | `x` | No transformation | `1` |

### Usage

#### Basic Usage
```python
from scripts.overlap_resolution_v3_advanced import ActivationSelector

# Get activation function by name
selector = ActivationSelector()
relu = selector.get("relu")
swish = selector.get("swish")

# Apply activation
import numpy as np
x = np.array([-2, -1, 0, 1, 2])
activated = relu.activate(x)  # [0, 0, 0, 1, 2]
gradient = relu.derivative(x)  # [0, 0, 0, 1, 1]
```

#### In Optimization
```python
engine = AdvancedLayoutEngine()

# Apply to loss components
positions = engine.solve_with_constraints(
    elements,
    component_activation="relu",  # Activate each loss component
    loss_activation="sigmoid"     # Activate final loss
)

# Or via comprehensive solve
positions = engine.solve_comprehensive(
    elements,
    loss_activation="swish",
    component_activation="tanh"
)
```

#### In Position Refiner
```python
refiner = PositionRefiner(
    loss_activation="sigmoid",      # Final loss activation
    component_activation="leaky_relu",  # Component activation
    gradient_activation="tanh"      # Gradient activation
)

positions = refiner.refine_positions(elements, initial_positions)
```

### Integration Points

Activation functions are applied at three levels:

1. **Component Level**: Transform individual loss terms (overlap, compactness, etc.)
2. **Final Loss Level**: Transform total combined loss
3. **Gradient Level**: Transform gradients during backpropagation

---

## 2. Machine Learning Models

### Model Types

Three ML models are implemented with **hybrid sklearn/built-in** approach:

#### 2.1 Linear Regression (Ridge)
- **Purpose**: Predict continuous optimizer parameters and loss weights
- **Implementation**: Ridge regression (L2 regularization)
- **Training**: Least squares with regularization
- **Outputs**: 7 optimizer params, 10 loss weights

#### 2.2 Logistic Regression
- **Purpose**: Binary classification (quality score, use_enhanced flag)
- **Implementation**: Gradient descent with sigmoid activation
- **Training**: Binary cross-entropy loss
- **Outputs**: Quality probability [0, 1]

#### 2.3 Linear SVM
- **Purpose**: Alternative binary classification
- **Implementation**: Hinge loss optimization
- **Training**: Subgradient descent
- **Outputs**: Binary decision (+1/-1)

### Hybrid Pattern

All models follow the **hybrid pattern**:
```python
class HybridLinearRegressor(HybridModelBase):
    def __init__(self):
        super().__init__()
        self._try_sklearn_import()  # Try sklearn
        self.fallback = LinearRegressionModel()  # Built-in fallback
    
    def fit(self, X, y):
        if self.use_sklearn and self.sklearn_model:
            self.sklearn_model.fit(X, y)  # Use sklearn if available
        else:
            self.fallback.fit(X, y)  # Fallback to built-in
```

**Benefits**:
- No hard sklearn dependency
- Automatic fallback to built-in implementations
- Consistent API regardless of sklearn availability

### Feature Engineering

The system extracts **6 features** from each layout:

| Feature | Description | Range |
|---------|-------------|-------|
| `element_count` | Number of elements | 10-150 |
| `overlap_density` | Overlapping pairs / total pairs | 0.0-1.0 |
| `layout_density` | Total area / bounding box | 0.0-1.0 |
| `constraint_count` | Number of constraints | 0-20 |
| `avg_size` | Average element size | 0.0-1.0 |
| `avg_distance` | Average inter-element distance | 0.0-10.0 |

### Training and Prediction

#### Training on Synthetic Data
```python
engine = AdvancedLayoutEngine()

# Train ML models on 200 synthetic layouts
engine.train_ml_models(num_samples=200, verbose=True)

# Check if trained
if engine.ml_hub.is_trained:
    print("ML models ready!")
```

#### Making Predictions
```python
# Extract features
features = engine.ml_hub.extract_features(elements, constraints, positions)

# Predict optimizer parameters
ml_params = engine.ml_hub.predict_parameters(features)
# Returns: {'lr': 0.05, 'max_steps': 150, 'beta1': 0.9, ...}

# Predict loss weights
ml_weights = engine.ml_hub.predict_loss_weights(features)
# Returns: {'overlap': 2.5, 'compactness': 0.8, ...}

# Predict quality score
quality = engine.ml_hub.predict_quality_score(features)
# Returns: float in [0, 1]

# Predict optimizer selection
use_enhanced = engine.ml_hub.predict_use_enhanced(features)
# Returns: bool (True = use Adam, False = use GD)
```

### Blending Strategies

The system blends **heuristic** (rule-based) and **ML** predictions:

```python
def _blend_params(heuristic_params, ml_params, blend_ratio):
    """
    blend_ratio = 0.0 → 100% heuristic
    blend_ratio = 0.5 → 50% heuristic + 50% ML
    blend_ratio = 1.0 → 100% ML
    """
    return {
        key: (1 - blend_ratio) * heuristic_params[key] + blend_ratio * ml_params[key]
        for key in heuristic_params
    }
```

---

## 3. Usage Examples

### Example 1: Activation Functions Only
```python
from scripts.overlap_resolution_v3_advanced import AdvancedLayoutEngine

engine = AdvancedLayoutEngine()
elements = {...}  # Your elements

# Solve with activation functions
positions = engine.solve_comprehensive(
    elements,
    max_steps=100,
    loss_activation="sigmoid",       # Bound final loss to [0, 1]
    component_activation="leaky_relu"  # Non-negative components
)
```

### Example 2: ML Models Only
```python
engine = AdvancedLayoutEngine()

# Step 1: Train ML models
engine.train_ml_models(num_samples=200)

# Step 2: Solve with ML predictions
positions = engine.solve_comprehensive(
    elements,
    use_ml_models=True,
    ml_blend=0.5,         # 50% heuristic + 50% ML
    ml_loss_weight=0.1    # ML quality score weight in loss
)
```

### Example 3: Combined (Activation + ML)
```python
engine = AdvancedLayoutEngine()
engine.train_ml_models(num_samples=200)

positions = engine.solve_comprehensive(
    elements,
    # ML parameters
    use_ml_models=True,
    ml_blend=0.7,              # 70% ML influence
    ml_loss_weight=0.15,       # 15% ML score in loss
    # Activation parameters
    loss_activation="swish",
    component_activation="elu"
)
```

### Example 4: Comparing Strategies
```python
engine = AdvancedLayoutEngine()
engine.train_ml_models(num_samples=200)

# Baseline: Heuristic only
pos_baseline = engine.solve_comprehensive(elements, use_ml_models=False)

# Hybrid: 50% ML
pos_hybrid = engine.solve_comprehensive(
    elements, use_ml_models=True, ml_blend=0.5
)

# Pure ML: 100% ML
pos_ml = engine.solve_comprehensive(
    elements, use_ml_models=True, ml_blend=1.0
)

# Compare
from scripts.overlap_resolution_v3_advanced import LayoutAnalyzer
for name, pos in [("Baseline", pos_baseline), ("Hybrid", pos_hybrid), ("ML", pos_ml)]:
    overlap = LayoutAnalyzer.calculate_overlap_score(elements, pos)
    compactness = LayoutAnalyzer.calculate_compactness(pos)
    print(f"{name}: overlap={overlap:.4f}, compactness={compactness:.4f}")
```

---

## 4. Advanced Configuration

### Custom Synthetic Training
```python
# Generate custom training data
engine.ml_hub.generate_synthetic_training_data(
    num_samples=500,
    element_range=(20, 100),     # 20-100 elements per layout
    constraint_range=(0, 15),    # 0-15 constraints
    size_range=(0.1, 0.5)        # Element sizes
)

# Train models
engine.train_ml_models(num_samples=500)
```

### Accessing ML Info
```python
# After solving with ML
positions = engine.solve_comprehensive(elements, use_ml_models=True)

# Get ML predictions used
ml_info = engine.last_ml_info
print(f"Predicted learning rate: {ml_info['ml_params']['lr']}")
print(f"Predicted quality: {ml_info['ml_quality']}")
print(f"ML features: {ml_info['ml_features']}")
```

### Per-Stage Control (solve_comprehensive)
```python
positions = engine.solve_comprehensive(
    elements,
    # Global ML settings
    use_ml_models=True,
    ml_blend=0.5,
    # These affect all stages (constraint, gradient, physics)
    loss_activation="swish"
)
```

### Per-Call Control (solve_with_constraints)
```python
# Direct control over single-stage optimization
positions = engine.solve_with_constraints(
    elements,
    constraints=my_constraints,
    max_steps=200,
    use_enhanced=True,
    use_ml_models=True,
    ml_loss_weight=0.2,
    ml_blend=0.6,
    loss_activation="sigmoid",
    component_activation="relu"
)
```

---

## 5. Performance Tips

### When to Use Activation Functions
- **ReLU/LeakyReLU**: Fast, suitable for sparse gradients
- **Sigmoid/Tanh**: Bounded outputs, good for normalizing loss
- **Swish/GELU**: Smoother gradients, better for complex landscapes
- **ELU/SoftPlus**: When negative values need special handling

### When to Use ML Models
- **Complex layouts**: 50+ elements with constraints
- **Repeated similar problems**: Train once, reuse predictions
- **Unknown optimal parameters**: Let ML learn from synthetic data
- **Quality prediction**: Use ml_score as early stopping signal

### When to Blend
- **ml_blend=0.0**: Trust your heuristics, ignore ML (good for simple cases)
- **ml_blend=0.5**: Balanced, good starting point
- **ml_blend=1.0**: Trust ML fully (only after validating training quality)

### Training Recommendations
- **Small problems (<30 elements)**: 100-200 training samples
- **Medium problems (30-100 elements)**: 200-500 training samples
- **Large problems (>100 elements)**: 500+ training samples
- Always validate on held-out test layouts

---

## 6. API Reference

### AdvancedLayoutEngine Methods

#### `train_ml_models(num_samples=200, verbose=False)`
Train ML models on synthetic data.

**Parameters**:
- `num_samples`: Number of synthetic layouts to generate
- `verbose`: Print training progress

**Returns**: None (updates `engine.ml_hub`)

#### `solve_comprehensive(..., use_ml_models, ml_blend, ml_loss_weight, loss_activation, component_activation)`
Multi-stage comprehensive solve with ML and activation support.

**ML Parameters**:
- `use_ml_models` (bool): Enable ML predictions (default: False)
- `ml_blend` (float): Blend ratio [0.0, 1.0] (default: 0.5)
- `ml_loss_weight` (float): Weight for ML quality score (default: 0.1)

**Activation Parameters**:
- `loss_activation` (str): Activation for final loss (default: None)
- `component_activation` (str): Activation for components (default: None)

#### `solve_with_constraints(..., use_ml_models, ml_loss_weight, ml_blend, loss_activation, component_activation)`
Single-stage constraint-aware optimization.

Same parameters as `solve_comprehensive` but operates on single optimization stage.

### MLModelHub Methods

#### `extract_features(elements, constraints, positions) -> np.ndarray`
Extract 6-feature vector from layout.

#### `predict_parameters(features) -> Dict[str, float]`
Predict 7 optimizer parameters (lr, max_steps, momentum, etc.).

#### `predict_loss_weights(features) -> Dict[str, float]`
Predict 10 loss weights (overlap, compactness, etc.).

#### `predict_quality_score(features) -> float`
Predict quality score [0, 1] (higher = better predicted quality).

#### `predict_use_enhanced(features) -> bool`
Predict whether to use enhanced optimizer (Adam) vs. basic (GD).

### ActivationSelector

#### `get(name: str) -> ActivationFunction`
Get activation function by name.

**Available names**: "relu", "leaky_relu", "sigmoid", "tanh", "elu", "softplus", "swish", "gelu", "linear"

---

## 7. Implementation Details

### Model Architecture

#### Linear Regression (Ridge)
```
Input: 6 features
↓
Ridge Regression (α=1.0)
↓
Output: 7 params or 10 weights (multi-output)
```

#### Logistic Regression
```
Input: 6 features
↓
Linear: W·x + b
↓
Sigmoid: σ(z)
↓
Output: Probability [0, 1]
```

#### Linear SVM
```
Input: 6 features
↓
Linear: W·x + b
↓
Hinge Loss: max(0, 1 - y·(W·x + b))
↓
Output: Class {-1, +1}
```

### Loss Computation with ML

```python
# Standard loss computation
base_loss = overlap_loss + compactness_loss + ... + constraint_loss

# Apply component activation (optional)
if component_activation:
    overlap_loss = activation(overlap_loss)
    compactness_loss = activation(compactness_loss)
    ...
    base_loss = sum(activated_components)

# Apply final loss activation (optional)
if loss_activation:
    base_loss = activation(base_loss)

# Blend ML quality score (optional)
if ml_score is not None:
    final_loss = (1 - ml_weight) * base_loss + ml_weight * ml_score

return final_loss
```

---

## 8. Troubleshooting

### Issue: ML predictions seem random
**Solution**: Train on more samples (500+) or check feature scaling

### Issue: Activation functions cause overflow
**Solution**: Use bounded activations (sigmoid, tanh) or scale inputs

### Issue: ML blend=1.0 performs worse than blend=0.0
**Solution**: Training data doesn't match your problem; regenerate with appropriate ranges

### Issue: "sklearn not found" warnings
**Solution**: Expected behavior; built-in models are used automatically

### Issue: Gradient explosion with activation functions
**Solution**: Use gradient clipping or gentler activations (softplus, elu)

---

## 9. Full Example Script

See `scripts/overlap_integration_v3_examples.py` → **Example 10** for complete demonstration:

```bash
# Run all examples including ML demo
python scripts/overlap_integration_v3_examples.py

# Or run Example 10 specifically
python -c "from scripts.overlap_integration_v3_examples import example_10_ml_driven_optimization; example_10_ml_driven_optimization()"
```

---

## 10. References

**Activation Functions**:
- ReLU: Nair & Hinton (2010)
- Swish: Ramachandran et al. (2017)
- GELU: Hendrycks & Gimpel (2016)

**ML Models**:
- Ridge Regression: Hoerl & Kennard (1970)
- Logistic Regression: Cox (1958)
- Linear SVM: Boser et al. (1992)

**Implementation**:
- File: `scripts/overlap_resolution_v3_advanced.py`
- Examples: `scripts/overlap_integration_v3_examples.py`
- Lines: Activations (~560-800), ML Models (~341-700)

---

**Last Updated**: February 2026  
**Version**: 3.0.1  
**Author**: GitHub Copilot
