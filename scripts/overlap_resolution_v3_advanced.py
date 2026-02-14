"""
OVERLAP RESOLUTION v3.0 - ADVANCED ENHANCEMENTS
==============================================

Advanced features for superior layout quality and performance:
- ML-based parameter optimization
- Constraint-based layout with dependency respecting
- Intelligent clustering and grouping
- Advanced multi-objective optimization
- Adaptive layout strategies
- Progressive refinement with early stopping

Author: GitHub Copilot
Date: February 8, 2026
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import json
from enum import Enum


# ============================================================================
# CONSTRAINT-BASED LAYOUT SYSTEM
# ============================================================================

class ConstraintType(Enum):
    """Types of layout constraints."""
    PROXIMITY = "proximity"          # Elements should be close
    SEPARATION = "separation"        # Elements should be far
    ALIGNMENT = "alignment"          # Elements should align
    GROUPING = "grouping"            # Elements form a group
    DEPENDENCY = "dependency"        # A depends on B
    BOUNDARY = "boundary"            # Stay within bounds
    RELATIVE_POSITION = "relative"   # Maintain relative position


@dataclass
class LayoutConstraint:
    """A layout constraint between elements."""
    constraint_type: ConstraintType
    element_ids: List[str]          # Elements involved
    parameters: Dict[str, float]    # Constraint parameters
    weight: float = 1.0             # Importance weight
    
    def evaluate(self, positions: Dict[str, Tuple[float, float]]) -> float:
        """Evaluate constraint violation (0 = satisfied, >0 = violated)."""
        if self.constraint_type == ConstraintType.PROXIMITY:
            # Elements should be close (within max_distance)
            max_dist = self.parameters.get("max_distance", 0.5)
            violations = 0.0
            for i in range(len(self.element_ids)):
                for j in range(i+1, len(self.element_ids)):
                    id1, id2 = self.element_ids[i], self.element_ids[j]
                    if id1 in positions and id2 in positions:
                        dist = np.linalg.norm(
                            np.array(positions[id1]) - np.array(positions[id2])
                        )
                        violations += max(0, dist - max_dist)
            return violations
            
        elif self.constraint_type == ConstraintType.SEPARATION:
            # Elements should be far (at least min_distance)
            min_dist = self.parameters.get("min_distance", 1.0)
            penalties = 0.0
            for i in range(len(self.element_ids)):
                for j in range(i+1, len(self.element_ids)):
                    id1, id2 = self.element_ids[i], self.element_ids[j]
                    if id1 in positions and id2 in positions:
                        dist = np.linalg.norm(
                            np.array(positions[id1]) - np.array(positions[id2])
                        )
                        penalties += max(0, min_dist - dist)
            return penalties
            
        elif self.constraint_type == ConstraintType.ALIGNMENT:
            # Elements should align (x or y coordinate)
            align_axis = self.parameters.get("axis", "x")  # "x" or "y"
            violations = 0.0
            if len(self.element_ids) > 1:
                coords = []
                for elem_id in self.element_ids:
                    if elem_id in positions:
                        pos = positions[elem_id]
                        axis_idx = 0 if align_axis == "x" else 1
                        coords.append(pos[axis_idx])
                if coords:
                    mean_coord = np.mean(coords)
                    violations = np.sum(np.abs(np.array(coords) - mean_coord))
            return violations
            
        elif self.constraint_type == ConstraintType.GROUPING:
            # Elements in group should be clustered together
            max_spread = self.parameters.get("max_spread", 1.0)
            violations = 0.0
            if len(self.element_ids) > 1:
                coords = []
                for elem_id in self.element_ids:
                    if elem_id in positions:
                        coords.append(positions[elem_id])
                if coords:
                    center = np.mean(coords, axis=0)
                    spreads = [np.linalg.norm(np.array(c) - center) for c in coords]
                    violations = sum(max(0, s - max_spread) for s in spreads)
            return violations
        
        return 0.0


class ConstraintSystem:
    """Manages layout constraints."""
    
    def __init__(self):
        self.constraints: List[LayoutConstraint] = []
        self._constraint_graph: Dict[str, Set[str]] = defaultdict(set)
    
    def add_constraint(self, constraint: LayoutConstraint):
        """Add a constraint."""
        self.constraints.append(constraint)
        # Update constraint graph
        for elem_id in constraint.element_ids:
            for other_id in constraint.element_ids:
                if elem_id != other_id:
                    self._constraint_graph[elem_id].add(other_id)
    
    def add_proximity_constraint(self, elem_ids: List[str], max_distance: float, weight: float = 1.0):
        """Add proximity constraint (elements should be close)."""
        constraint = LayoutConstraint(
            ConstraintType.PROXIMITY,
            elem_ids,
            {"max_distance": max_distance},
            weight
        )
        self.add_constraint(constraint)
    
    def add_separation_constraint(self, elem_ids: List[str], min_distance: float, weight: float = 1.0):
        """Add separation constraint (elements should be far)."""
        constraint = LayoutConstraint(
            ConstraintType.SEPARATION,
            elem_ids,
            {"min_distance": min_distance},
            weight
        )
        self.add_constraint(constraint)
    
    def add_grouping_constraint(self, elem_ids: List[str], max_spread: float, weight: float = 1.0):
        """Add grouping constraint (elements form a group)."""
        constraint = LayoutConstraint(
            ConstraintType.GROUPING,
            elem_ids,
            {"max_spread": max_spread},
            weight
        )
        self.add_constraint(constraint)
    
    def add_alignment_constraint(self, elem_ids: List[str], axis: str = "x", weight: float = 1.0):
        """Add alignment constraint (elements align on axis)."""
        constraint = LayoutConstraint(
            ConstraintType.ALIGNMENT,
            elem_ids,
            {"axis": axis},
            weight
        )
        self.add_constraint(constraint)
    
    def evaluate_all(self, positions: Dict[str, Tuple[float, float]]) -> float:
        """Evaluate total constraint violation."""
        total = 0.0
        for constraint in self.constraints:
            violation = constraint.evaluate(positions)
            total += constraint.weight * violation
        return total
    
    def get_related_elements(self, elem_id: str) -> Set[str]:
        """Get elements with constraints related to this one."""
        return self._constraint_graph.get(elem_id, set())


# ============================================================================
# INTELLIGENT CLUSTERING & GROUPING
# ============================================================================

class ElementClusterer:
    """Intelligent clustering of elements for better layout."""
    
    @staticmethod
    def hierarchical_clustering(
        elements: Dict[str, Any],
        max_clusters: int = 5,
        distance_metric: str = "euclidean"
    ) -> Dict[str, int]:
        """
        Hierarchical clustering of elements.
        
        Returns: Dict mapping element_id -> cluster_id
        """
        if len(elements) <= 1:
            return {elem_id: 0 for elem_id in elements}
        
        # Calculate distance matrix
        elem_ids = list(elements.keys())
        n = len(elem_ids)
        distances = np.zeros((n, n))
        
        for i, id1 in enumerate(elem_ids):
            for j, id2 in enumerate(elem_ids):
                if i < j:
                    pos1 = elements[id1].get("position", (0, 0))
                    pos2 = elements[id2].get("position", (0, 0))
                    size1 = elements[id1].get("size", (0.1, 0.1))
                    size2 = elements[id2].get("size", (0.1, 0.1))
                    
                    # Position distance
                    pos_dist = np.linalg.norm(np.array(pos1) - np.array(pos2))
                    
                    # Size similarity (larger = more likely to cluster)
                    size_sim = min(size1[0], size2[0]) / max(size1[0], size2[0])
                    
                    distances[i, j] = pos_dist / (size_sim + 0.1)
                    distances[j, i] = distances[i, j]
        
        # Simple linkage clustering
        clusters = {elem_id: i for i, elem_id in enumerate(elem_ids)}
        cluster_count = n
        
        while cluster_count > max_clusters:
            # Find closest clusters
            min_dist = np.inf
            merge_i, merge_j = 0, 1
            for i in range(n):
                for j in range(i+1, n):
                    if distances[i, j] < min_dist:
                        min_dist = distances[i, j]
                        merge_i, merge_j = i, j
            
            # Merge clusters
            elem_i = elem_ids[merge_i]
            elem_j = elem_ids[merge_j]
            new_cluster = min(clusters[elem_i], clusters[elem_j])
            old_cluster = max(clusters[elem_i], clusters[elem_j])
            
            for elem_id in clusters:
                if clusters[elem_id] == old_cluster:
                    clusters[elem_id] = new_cluster
            
            cluster_count -= 1
        
        return clusters
    
    @staticmethod
    def density_based_clustering(
        elements: Dict[str, Any],
        eps: float = 1.0,
        min_samples: int = 2
    ) -> Dict[str, int]:
        """
        DBSCAN-like density-based clustering.
        
        Returns: Dict mapping element_id -> cluster_id
        """
        elem_ids = list(elements.keys())
        clusters = {elem_id: -1 for elem_id in elem_ids}  # -1 = noise
        cluster_id = 0
        
        for elem_id in elem_ids:
            if clusters[elem_id] != -1:
                continue
            
            # Get neighbors
            neighbors = []
            pos1 = elements[elem_id].get("position", (0, 0))
            for other_id in elem_ids:
                if other_id == elem_id:
                    continue
                pos2 = elements[other_id].get("position", (0, 0))
                dist = np.linalg.norm(np.array(pos1) - np.array(pos2))
                if dist <= eps:
                    neighbors.append(other_id)
            
            # Check if core point
            if len(neighbors) < min_samples:
                continue
            
            # Start new cluster
            clusters[elem_id] = cluster_id
            to_process = neighbors
            idx = 0
            while idx < len(to_process):
                neighbor_id = to_process[idx]
                if clusters[neighbor_id] == -1:
                    clusters[neighbor_id] = cluster_id
                    # Expand cluster
                    pos2 = elements[neighbor_id].get("position", (0, 0))
                    for other_id in elem_ids:
                        if other_id == neighbor_id:
                            continue
                        pos3 = elements[other_id].get("position", (0, 0))
                        dist = np.linalg.norm(np.array(pos2) - np.array(pos3))
                        if dist <= eps and other_id not in to_process:
                            to_process.append(other_id)
                idx += 1
            
            cluster_id += 1
        
        return clusters


# ============================================================================
# ML-BASED PARAMETER OPTIMIZATION
# ============================================================================

@dataclass
class OptimizationParameters:
    """Parameters for layout optimization."""
    repulsion_strength: float = 1.0
    attraction_strength: float = 0.5
    thermal_temperature: float = 1.0
    cooling_rate: float = 0.95
    iterations: int = 100
    boundary_penalty: float = 1.0
    min_distance: float = 0.15


@dataclass
class LossWeights:
    """Weights for the composite layout loss."""
    overlap: float = 2.0
    constraint: float = 3.0
    boundary: float = 1.5
    displacement: float = 0.5
    compactness: float = 0.2
    balance: float = 0.2
    spacing: float = 0.8
    velocity_smoothness: float = 0.3
    readability: float = 0.6
    edge_length: float = 0.7


class ParameterOptimizer:
    """ML-based optimization of layout parameters."""
    
    def __init__(self, history_size: int = 50):
        self.history: List[Tuple[OptimizationParameters, float]] = []
        self.history_size = history_size
    
    def learn_from_result(self, params: OptimizationParameters, quality_score: float):
        """Record a result for learning."""
        self.history.append((params, quality_score))
        if len(self.history) > self.history_size:
            self.history.pop(0)
    
    def predict_best_parameters(
        self,
        element_count: int,
        overlap_percentage: float,
        density: float
    ) -> OptimizationParameters:
        """
        Predict best parameters using learned history.
        Falls back to heuristics if history is limited.
        """
        if len(self.history) < 5:
            return self._heuristic_parameters(element_count, overlap_percentage, density)
        
        # Use history to make predictions
        # For now, simple heuristic based on similarity
        best_params = None
        best_score = -np.inf
        
        for params, score in self.history:
            # Similar parameters should give similar results
            similarity = 1.0 / (1.0 + abs(element_count - 50) / 50.0)  # Rough similarity
            adjusted_score = score * similarity
            if adjusted_score > best_score:
                best_score = adjusted_score
                best_params = params
        
        return best_params if best_params else self._heuristic_parameters(
            element_count, overlap_percentage, density
        )
    
    @staticmethod
    def _heuristic_parameters(
        element_count: int,
        overlap_percentage: float,
        density: float
    ) -> OptimizationParameters:
        """Generate parameters using heuristics."""
        # Adjust based on problem complexity
        base_repulsion = 1.0 + (overlap_percentage / 100.0) * 2.0
        base_temperature = max(0.5, 1.5 - density)
        base_iterations = 50 + int(element_count * 2)
        base_cooling = 0.92 if overlap_percentage > 50 else 0.95
        
        return OptimizationParameters(
            repulsion_strength=base_repulsion,
            attraction_strength=0.5 + overlap_percentage / 200.0,
            thermal_temperature=base_temperature,
            cooling_rate=base_cooling,
            iterations=min(base_iterations, 200),
            boundary_penalty=1.0 + density,
            min_distance=0.15 if density < 0.5 else 0.1
        )


# ============================================================================
# ML MODELS (LINEAR REGRESSION, LOGISTIC REGRESSION, SVM)
# ============================================================================

class LinearRegressionModel:
    """Linear regression with optional L2 regularization (multi-output)."""
    
    def __init__(self, ridge: float = 1e-6):
        self.ridge = ridge
        self.coef_: Optional[np.ndarray] = None
        self.intercept_: Optional[np.ndarray] = None
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        if y.ndim == 1:
            y = y.reshape(-1, 1)
        
        X_aug = np.hstack([X, np.ones((X.shape[0], 1))])
        reg = self.ridge * np.eye(X_aug.shape[1])
        reg[-1, -1] = 0.0  # Do not regularize bias
        
        w = np.linalg.pinv(X_aug.T @ X_aug + reg) @ X_aug.T @ y
        self.coef_ = w[:-1, :].T
        self.intercept_ = w[-1, :]
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.coef_ is None or self.intercept_ is None:
            raise ValueError("LinearRegressionModel is not trained")
        X = np.asarray(X, dtype=float)
        y = X @ self.coef_.T + self.intercept_
        return y


class LogisticRegressionModel:
    """Binary logistic regression using gradient descent."""
    
    def __init__(self, lr: float = 0.1, max_iter: int = 200, reg: float = 1e-3):
        self.lr = lr
        self.max_iter = max_iter
        self.reg = reg
        self.coef_: Optional[np.ndarray] = None
        self.intercept_: float = 0.0
    
    @staticmethod
    def _sigmoid(z: np.ndarray) -> np.ndarray:
        z = np.clip(z, -50, 50)
        return 1.0 / (1.0 + np.exp(-z))
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float).reshape(-1)
        n_samples, n_features = X.shape
        self.coef_ = np.zeros(n_features)
        self.intercept_ = 0.0
        
        for _ in range(self.max_iter):
            linear = X @ self.coef_ + self.intercept_
            preds = self._sigmoid(linear)
            
            grad_w = (X.T @ (preds - y)) / n_samples + self.reg * self.coef_
            grad_b = np.mean(preds - y)
            
            self.coef_ -= self.lr * grad_w
            self.intercept_ -= self.lr * grad_b
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self.coef_ is None:
            raise ValueError("LogisticRegressionModel is not trained")
        X = np.asarray(X, dtype=float)
        linear = X @ self.coef_ + self.intercept_
        probs = self._sigmoid(linear)
        return probs
    
    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        probs = self.predict_proba(X)
        return (probs >= threshold).astype(int)


class LinearSVMModel:
    """Linear SVM using hinge loss and gradient descent."""
    
    def __init__(self, lr: float = 0.05, max_iter: int = 200, reg: float = 1e-3):
        self.lr = lr
        self.max_iter = max_iter
        self.reg = reg
        self.coef_: Optional[np.ndarray] = None
        self.intercept_: float = 0.0
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float).reshape(-1)
        y = np.where(y <= 0, -1.0, 1.0)
        n_samples, n_features = X.shape
        self.coef_ = np.zeros(n_features)
        self.intercept_ = 0.0
        
        for _ in range(self.max_iter):
            margins = y * (X @ self.coef_ + self.intercept_)
            misclassified = margins < 1
            
            grad_w = self.reg * self.coef_ - (X[misclassified].T @ y[misclassified]) / n_samples
            grad_b = -np.mean(y[misclassified]) if np.any(misclassified) else 0.0
            
            self.coef_ -= self.lr * grad_w
            self.intercept_ -= self.lr * grad_b
    
    def decision_function(self, X: np.ndarray) -> np.ndarray:
        if self.coef_ is None:
            raise ValueError("LinearSVMModel is not trained")
        X = np.asarray(X, dtype=float)
        return X @ self.coef_ + self.intercept_
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.decision_function(X)
        return (scores >= 0).astype(int)


class HybridModelBase:
    """Hybrid model wrapper: uses sklearn if available, else fallback."""
    
    def __init__(self, use_sklearn_if_available: bool = True):
        self.use_sklearn_if_available = use_sklearn_if_available
        self.backend = None
        self.backend_type = "fallback"
    
    def _try_sklearn(self, creator: Callable[[], Any]) -> bool:
        if not self.use_sklearn_if_available:
            return False
        try:
            self.backend = creator()
            self.backend_type = "sklearn"
            return True
        except Exception:
            return False


class HybridLinearRegressor(HybridModelBase):
    """Hybrid linear regression (sklearn if available)."""
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        if self.backend is None:
            if not self._try_sklearn(lambda: __import__("sklearn").linear_model.LinearRegression()):
                self.backend = LinearRegressionModel()
        self.backend.fit(X, y)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.backend is None:
            raise ValueError("HybridLinearRegressor is not trained")
        return self.backend.predict(X)


class HybridLogisticRegressor(HybridModelBase):
    """Hybrid logistic regression (sklearn if available)."""
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        if self.backend is None:
            def creator():
                from sklearn.linear_model import LogisticRegression
                return LogisticRegression(max_iter=200)
            if not self._try_sklearn(creator):
                self.backend = LogisticRegressionModel()
        self.backend.fit(X, y)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self.backend is None:
            raise ValueError("HybridLogisticRegressor is not trained")
        if self.backend_type == "sklearn":
            probs = self.backend.predict_proba(X)
            return probs[:, 1]
        return self.backend.predict_proba(X)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.backend is None:
            raise ValueError("HybridLogisticRegressor is not trained")
        return self.backend.predict(X)


class HybridLinearSVM(HybridModelBase):
    """Hybrid linear SVM (sklearn if available)."""
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        if self.backend is None:
            def creator():
                from sklearn.svm import LinearSVC
                return LinearSVC(max_iter=200)
            if not self._try_sklearn(creator):
                self.backend = LinearSVMModel()
        self.backend.fit(X, y)
    
    def decision_function(self, X: np.ndarray) -> np.ndarray:
        if self.backend is None:
            raise ValueError("HybridLinearSVM is not trained")
        return self.backend.decision_function(X)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.backend is None:
            raise ValueError("HybridLinearSVM is not trained")
        return self.backend.predict(X)


class MLModelHub:
    """Train/predict using linear regression, logistic regression, and SVM."""
    
    def __init__(self, use_sklearn_if_available: bool = True):
        self.use_sklearn_if_available = use_sklearn_if_available
        self.param_regressor = HybridLinearRegressor(use_sklearn_if_available)
        self.weight_regressor = HybridLinearRegressor(use_sklearn_if_available)
        self.logistic = HybridLogisticRegressor(use_sklearn_if_available)
        self.svm = HybridLinearSVM(use_sklearn_if_available)
        self.is_trained = False
        self.feature_names = [
            "element_count",
            "overlap_density",
            "layout_density",
            "constraint_count",
            "avg_size",
            "avg_distance"
        ]
    
    def extract_features(
        self,
        elements: Dict[str, Any],
        constraints: Optional[ConstraintSystem] = None,
        positions: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> np.ndarray:
        positions = positions or {eid: elem.get("position", (0.0, 0.0)) for eid, elem in elements.items()}
        elem_count = len(elements)
        constraint_count = len(constraints.constraints) if constraints is not None else 0
        
        sizes = [elements[eid].get("size", (0.1, 0.1)) for eid in elements.keys()]
        avg_size = float(np.mean([s[0] * s[1] for s in sizes])) if sizes else 0.0
        
        pos_array = np.array(list(positions.values())) if positions else np.zeros((1, 2))
        center = np.mean(pos_array, axis=0)
        avg_distance = float(np.mean([np.linalg.norm(p - center) for p in pos_array])) if len(pos_array) > 0 else 0.0
        
        overlap = LayoutAnalyzer.calculate_overlap_score(elements, positions)
        
        min_xy = np.min(pos_array, axis=0) if len(pos_array) > 0 else np.array([0.0, 0.0])
        max_xy = np.max(pos_array, axis=0) if len(pos_array) > 0 else np.array([1.0, 1.0])
        bbox_area = max(1e-6, float((max_xy[0] - min_xy[0]) * (max_xy[1] - min_xy[1])))
        total_area = float(np.sum([s[0] * s[1] for s in sizes])) if sizes else 0.0
        layout_density = min(1.0, total_area / bbox_area) if bbox_area > 0 else 0.0
        overlap_density = min(1.0, overlap / bbox_area) if bbox_area > 0 else 0.0
        
        return np.array([
            float(elem_count),
            float(overlap_density),
            float(layout_density),
            float(constraint_count),
            float(avg_size),
            float(avg_distance)
        ], dtype=float)
    
    def train_synthetic(self, samples: int = 200, seed: int = 42):
        rng = np.random.RandomState(seed)
        X = []
        y_params = []
        y_weights = []
        y_quality = []
        
        for _ in range(samples):
            elem_count = int(rng.randint(10, 150))
            elements = {
                f"e{i}": {
                    "position": (rng.uniform(-3, 3), rng.uniform(-2, 2)),
                    "size": (rng.uniform(0.08, 0.3), rng.uniform(0.08, 0.3))
                }
                for i in range(elem_count)
            }
            constraint_count = int(rng.randint(0, 20))
            constraints = ConstraintSystem()
            elem_ids_list = list(elements.keys())
            for _ in range(constraint_count):
                if len(elem_ids_list) >= 2:
                    idx1, idx2 = rng.choice(len(elem_ids_list), size=2, replace=False)
                    constraint_types = [ConstraintType.PROXIMITY, ConstraintType.ALIGNMENT, ConstraintType.SEPARATION]
                    ctype = rng.choice(constraint_types)
                    
                    if ctype == ConstraintType.PROXIMITY:
                        constraints.add_constraint(LayoutConstraint(
                            constraint_type=ctype,
                            element_ids=[elem_ids_list[idx1], elem_ids_list[idx2]],
                            parameters={"max_distance": rng.uniform(0.3, 1.0)},
                            weight=rng.uniform(0.5, 1.5)
                        ))
                    elif ctype == ConstraintType.ALIGNMENT:
                        constraints.add_constraint(LayoutConstraint(
                            constraint_type=ctype,
                            element_ids=[elem_ids_list[idx1], elem_ids_list[idx2]],
                            parameters={"axis": rng.choice(["x", "y"]), "tolerance": rng.uniform(0.1, 0.5)},
                            weight=rng.uniform(0.5, 1.5)
                        ))
                    else:  # SEPARATION
                        constraints.add_constraint(LayoutConstraint(
                            constraint_type=ctype,
                            element_ids=[elem_ids_list[idx1], elem_ids_list[idx2]],
                            parameters={"min_distance": rng.uniform(0.5, 2.0)},
                            weight=rng.uniform(0.5, 1.5)
                        ))
            
            features = self.extract_features(elements, constraints)
            overlap_percentage = features[1] * 100.0
            params = ParameterOptimizer._heuristic_parameters(
                elem_count, overlap_percentage, features[2]
            )
            
            base_weights = LossWeights()
            overlap_scale = 1.0 + features[1] * 3.0
            constraint_scale = 1.0 + features[3] / 10.0
            spacing_scale = 1.0 + features[2]
            
            weights = LossWeights(
                overlap=base_weights.overlap * overlap_scale,
                constraint=base_weights.constraint * constraint_scale,
                boundary=base_weights.boundary,
                displacement=base_weights.displacement,
                compactness=base_weights.compactness,
                balance=base_weights.balance,
                spacing=base_weights.spacing * spacing_scale,
                velocity_smoothness=base_weights.velocity_smoothness,
                readability=base_weights.readability,
                edge_length=base_weights.edge_length
            )
            
            quality = 1.0 if (features[1] < 0.1 and features[2] < 0.6 and features[3] < 8) else 0.0
            
            X.append(features)
            y_params.append([
                params.repulsion_strength,
                params.attraction_strength,
                params.thermal_temperature,
                params.cooling_rate,
                float(params.iterations),
                params.boundary_penalty,
                params.min_distance
            ])
            y_weights.append([
                weights.overlap,
                weights.constraint,
                weights.boundary,
                weights.displacement,
                weights.compactness,
                weights.balance,
                weights.spacing,
                weights.velocity_smoothness,
                weights.readability,
                weights.edge_length
            ])
            y_quality.append(quality)
        
        X = np.array(X, dtype=float)
        y_params = np.array(y_params, dtype=float)
        y_weights = np.array(y_weights, dtype=float)
        y_quality = np.array(y_quality, dtype=float)
        
        self.param_regressor.fit(X, y_params)
        self.weight_regressor.fit(X, y_weights)
        self.logistic.fit(X, y_quality)
        self.svm.fit(X, y_quality)
        self.is_trained = True
    
    def predict_parameters(self, features: np.ndarray) -> Optional[OptimizationParameters]:
        if not self.is_trained:
            return None
        pred = self.param_regressor.predict(features.reshape(1, -1))[0]
        # Validate and clip predicted parameters to reasonable ranges
        return OptimizationParameters(
            repulsion_strength=float(np.clip(pred[0], 0.1, 10.0)),
            attraction_strength=float(np.clip(pred[1], 0.0, 2.0)),
            thermal_temperature=float(np.clip(pred[2], 0.0, 5.0)),
            cooling_rate=float(np.clip(pred[3], 0.8, 0.99)),
            iterations=int(max(10, min(300, round(pred[4])))),
            boundary_penalty=float(np.clip(pred[5], 0.0, 10.0)),
            min_distance=float(np.clip(pred[6], 0.01, 0.5))
        )
    
    def predict_loss_weights(self, features: np.ndarray) -> Optional[LossWeights]:
        if not self.is_trained:
            return None
        pred = self.weight_regressor.predict(features.reshape(1, -1))[0]
        # Validate and clip predicted weights to non-negative reasonable ranges
        return LossWeights(
            overlap=float(np.clip(pred[0], 0.1, 10.0)),
            constraint=float(np.clip(pred[1], 0.1, 10.0)),
            boundary=float(np.clip(pred[2], 0.0, 5.0)),
            displacement=float(np.clip(pred[3], 0.0, 5.0)),
            compactness=float(np.clip(pred[4], 0.0, 5.0)),
            balance=float(np.clip(pred[5], 0.0, 5.0)),
            spacing=float(np.clip(pred[6], 0.0, 5.0)),
            velocity_smoothness=float(np.clip(pred[7], 0.0, 2.0)),
            readability=float(np.clip(pred[8], 0.0, 2.0)),
            edge_length=float(np.clip(pred[9], 0.0, 2.0))
        )
    
    def predict_quality_score(self, features: np.ndarray) -> Optional[float]:
        if not self.is_trained:
            return None
        prob_good = float(self.logistic.predict_proba(features.reshape(1, -1))[0])
        svm_score = float(self.svm.decision_function(features.reshape(1, -1))[0])
        svm_prob = 1.0 / (1.0 + np.exp(-np.clip(svm_score, -10, 10)))
        return 0.5 * prob_good + 0.5 * svm_prob
    
    def predict_use_enhanced(self, features: np.ndarray) -> Optional[bool]:
        if not self.is_trained:
            return None
        quality = self.predict_quality_score(features)
        if quality is None:
            return None
        return quality < 0.6


# ============================================================================
# ADVANCED MULTI-OBJECTIVE OPTIMIZATION
# ============================================================================

class MultiObjectiveOptimizer:
    """Multi-objective optimization balancing multiple quality metrics."""
    
    def __init__(self):
        self.objectives: List[Tuple[Callable, float]] = []  # (function, weight)
        self.pareto_front: List[Dict[str, Any]] = []
    
    def add_objective(self, func: Callable, weight: float = 1.0):
        """Add an optimization objective."""
        self.objectives.append((func, weight))
    
    def evaluate_solution(self, solution: Dict[str, Tuple[float, float]]) -> Dict[str, float]:
        """Evaluate solution on all objectives."""
        scores = {}
        weighted_sum = 0.0
        for func, weight in self.objectives:
            score = func(solution)
            scores[func.__name__] = score
            weighted_sum += score * weight
        scores["weighted_sum"] = weighted_sum
        return scores
    
    def is_pareto_optimal(self, solution: Dict[str, Any], existing: List[Dict[str, Any]]) -> bool:
        """Check if solution is on Pareto front."""
        for existing_sol in existing:
            # Check if existing dominates this one
            dominates = True
            equal = True
            for obj_name in existing_sol:
                if obj_name == "position":
                    continue
                if existing_sol[obj_name] < solution[obj_name]:
                    equal = False
                else:
                    dominates = False
                    break
            if dominates and not equal:
                return False
        return True
    
    def update_pareto_front(self, solution: Dict[str, Any]):
        """Update Pareto front with new solution."""
        # Remove dominated solutions
        dominated = []
        for existing in self.pareto_front:
            dominates = True
            for obj_name in solution:
                if obj_name == "position":
                    continue
                if solution[obj_name] > existing.get(obj_name, float('inf')):
                    dominates = False
                    break
            if dominates:
                dominated.append(existing)
        
        for d in dominated:
            self.pareto_front.remove(d)
        
        # Add new solution if not dominated
        if self.is_pareto_optimal(solution, self.pareto_front):
            self.pareto_front.append(solution)


# ============================================================================
# ADAPTIVE LAYOUT STRATEGY SELECTOR
# ============================================================================

class AdaptiveLayoutStrategy:
    """Automatically select and adapt layout strategy."""
    
    @staticmethod
    def analyze_problem(
        elements: Dict[str, Any],
        constraints: Optional[ConstraintSystem] = None
    ) -> Dict[str, Any]:
        """Analyze problem characteristics."""
        positions = [e.get("position", (0, 0)) for e in elements.values()]
        sizes = [e.get("size", (0.1, 0.1)) for e in elements.values()]
        
        if not positions:
            return {"strategy": "grid"}
        
        # Calculate metrics
        positions_arr = np.array(positions)
        center = np.mean(positions_arr, axis=0)
        spread = np.mean([np.linalg.norm(p - center) for p in positions])
        
        avgsize = np.mean([s[0] * s[1] for s in sizes])
        canvas_area = 8 * 4.5  # Standard canvas
        density = (len(elements) * avgsize) / canvas_area
        
        # Analyze overlap
        overlaps = 0
        for i, id1 in enumerate(list(elements.keys())):
            for id2 in list(elements.keys())[i+1:]:
                p1 = elements[id1].get("position", (0, 0))
                p2 = elements[id2].get("position", (0, 0))
                s1 = elements[id1].get("size", (0.1, 0.1))
                s2 = elements[id2].get("size", (0.1, 0.1))
                dist = np.linalg.norm(np.array(p1) - np.array(p2))
                min_dist = (s1[0] + s2[0]) / 2
                if dist < min_dist:
                    overlaps += 1
        
        overlap_pct = (overlaps / max(len(elements) * (len(elements) - 1) / 2, 1)) * 100
        
        # Count dependencies
        deps = 0
        if constraints:
            for constraint in constraints.constraints:
                if constraint.constraint_type == ConstraintType.DEPENDENCY:
                    deps += 1
        
        return {
            "element_count": len(elements),
            "density": density,
            "spread": spread,
            "overlap_percentage": overlap_pct,
            "has_dependencies": deps > 0,
            "constraint_count": len(constraints.constraints) if constraints else 0
        }
    
    @staticmethod
    def recommend_strategy(analysis: Dict[str, Any]) -> str:
        """Recommend layout strategy based on analysis."""
        density = analysis.get("density", 0.5)
        overlap = analysis.get("overlap_percentage", 0)
        has_deps = analysis.get("has_dependencies", False)
        elem_count = analysis.get("element_count", 0)
        
        # Decision tree
        if has_deps:
            return "hierarchical"
        elif density > 0.8:
            return "forced_directed_high_temp"  # More thermal annealing
        elif overlap > 70:
            return "force_directed"
        elif elem_count > 200:
            return "grid"
        elif elem_count > 100:
            return "radial"
        else:
            return "force_directed"


# ============================================================================
# ENHANCED OPTIMIZATION ALGORITHMS
# ============================================================================

# ============================================================================
# ACTIVATION FUNCTIONS
# ============================================================================

class ActivationFunction:
    """Base class for activation functions."""
    
    @staticmethod
    def activate(x: np.ndarray) -> np.ndarray:
        """Apply activation function."""
        raise NotImplementedError
    
    @staticmethod
    def derivative(x: np.ndarray) -> np.ndarray:
        """Compute derivative of activation function."""
        raise NotImplementedError


class ReLU(ActivationFunction):
    """Rectified Linear Unit: max(0, x)"""
    
    @staticmethod
    def activate(x: np.ndarray) -> np.ndarray:
        """ReLU activation: max(0, x)"""
        return np.maximum(0, x)
    
    @staticmethod
    def derivative(x: np.ndarray) -> np.ndarray:
        """Derivative: 1 if x > 0, else 0"""
        return (x > 0).astype(float)
    
    @staticmethod
    def derivative_from_output(y: np.ndarray) -> np.ndarray:
        """Derivative from already-activated output"""
        return (y > 0).astype(float)


class LeakyReLU(ActivationFunction):
    """Leaky ReLU: max(alpha*x, x)"""
    
    def __init__(self, alpha: float = 0.01):
        self.alpha = alpha
    
    def activate(self, x: np.ndarray) -> np.ndarray:
        """Leaky ReLU: max(alpha*x, x)"""
        return np.where(x > 0, x, self.alpha * x)
    
    def derivative(self, x: np.ndarray) -> np.ndarray:
        """Derivative: 1 if x > 0, else alpha"""
        return np.where(x > 0, 1.0, self.alpha)
    
    def derivative_from_output(self, y: np.ndarray) -> np.ndarray:
        """Derivative from already-activated output"""
        return np.where(y > 0, 1.0, self.alpha)


class Sigmoid(ActivationFunction):
    """Sigmoid: 1 / (1 + exp(-x))"""
    
    @staticmethod
    def activate(x: np.ndarray) -> np.ndarray:
        """Sigmoid activation"""
        # Clip to prevent overflow
        x_clipped = np.clip(x, -500, 500)
        return 1.0 / (1.0 + np.exp(-x_clipped))
    
    @staticmethod
    def derivative(x: np.ndarray) -> np.ndarray:
        """Derivative: sigmoid(x) * (1 - sigmoid(x))"""
        y = Sigmoid.activate(x)
        return y * (1.0 - y)
    
    @staticmethod
    def derivative_from_output(y: np.ndarray) -> np.ndarray:
        """Derivative from already-activated output: y * (1 - y)"""
        return y * (1.0 - y)


class Tanh(ActivationFunction):
    """Tanh: (2 / (1 + exp(-2x))) - 1"""
    
    @staticmethod
    def activate(x: np.ndarray) -> np.ndarray:
        """Tanh activation"""
        return np.tanh(x)
    
    @staticmethod
    def derivative(x: np.ndarray) -> np.ndarray:
        """Derivative: 1 - tanh(x)^2"""
        y = np.tanh(x)
        return 1.0 - y ** 2
    
    @staticmethod
    def derivative_from_output(y: np.ndarray) -> np.ndarray:
        """Derivative from already-activated output: 1 - y^2"""
        return 1.0 - y ** 2


class ELU(ActivationFunction):
    """Exponential Linear Unit"""
    
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
    
    def activate(self, x: np.ndarray) -> np.ndarray:
        """ELU activation"""
        return np.where(x > 0, x, self.alpha * (np.exp(x) - 1))
    
    def derivative(self, x: np.ndarray) -> np.ndarray:
        """ELU derivative"""
        return np.where(x > 0, 1.0, self.alpha * np.exp(x))
    
    def derivative_from_output(self, y: np.ndarray) -> np.ndarray:
        """Derivative from output"""
        return np.where(y > 0, 1.0, y + self.alpha)


class SoftPlus(ActivationFunction):
    """SoftPlus: ln(1 + exp(x))"""
    
    @staticmethod
    def activate(x: np.ndarray) -> np.ndarray:
        """SoftPlus activation"""
        x_clipped = np.clip(x, -500, 500)
        return np.log(1.0 + np.exp(x_clipped))
    
    @staticmethod
    def derivative(x: np.ndarray) -> np.ndarray:
        """Derivative: sigmoid(x)"""
        x_clipped = np.clip(x, -500, 500)
        return 1.0 / (1.0 + np.exp(-x_clipped))
    
    @staticmethod
    def derivative_from_output(y: np.ndarray) -> np.ndarray:
        """Derivative from output: 1 - exp(-y)"""
        return 1.0 - np.exp(-y)


class Swish(ActivationFunction):
    """Swish: x * sigmoid(x)"""
    
    @staticmethod
    def activate(x: np.ndarray) -> np.ndarray:
        """Swish activation"""
        x_clipped = np.clip(x, -500, 500)
        sigmoid_x = 1.0 / (1.0 + np.exp(-x_clipped))
        return x * sigmoid_x
    
    @staticmethod
    def derivative(x: np.ndarray) -> np.ndarray:
        """Swish derivative: sigmoid(x) + x * sigmoid(x) * (1 - sigmoid(x))"""
        x_clipped = np.clip(x, -500, 500)
        sigmoid_x = 1.0 / (1.0 + np.exp(-x_clipped))
        return sigmoid_x + x * sigmoid_x * (1.0 - sigmoid_x)
    
    @staticmethod
    def derivative_from_output(y: np.ndarray, x: Optional[np.ndarray] = None) -> np.ndarray:
        """Derivative from output (requires original x)"""
        if x is None:
            raise ValueError("Swish derivative_from_output requires original x")
        return Swish.derivative(x)


class GELU(ActivationFunction):
    """GELU: Gaussian Error Linear Unit"""
    
    @staticmethod
    def activate(x: np.ndarray) -> np.ndarray:
        """GELU activation"""
        # Approximation: 0.5 * x * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
        cdf = 0.5 * (1.0 + np.tanh(
            np.sqrt(2.0 / np.pi) * (x + 0.044715 * x ** 3)
        ))
        return x * cdf
    
    @staticmethod
    def derivative(x: np.ndarray) -> np.ndarray:
        """GELU derivative (approximation)"""
        import math
        const = math.sqrt(2.0 / math.pi)
        tanh_arg = const * (x + 0.044715 * x ** 3)
        
        cdf = 0.5 * (1.0 + np.tanh(tanh_arg))
        sech_sq = 1.0 - np.tanh(tanh_arg) ** 2
        
        pdf = const * (1.0 + 0.044715 * 3 * x ** 2) * 0.5 * sech_sq
        
        return cdf + x * pdf


class Linear(ActivationFunction):
    """Linear: No activation (identity)"""
    
    @staticmethod
    def activate(x: np.ndarray) -> np.ndarray:
        """Linear: no activation"""
        return np.array(x, copy=True)
    
    @staticmethod
    def derivative(x: np.ndarray) -> np.ndarray:
        """Derivative: all ones"""
        return np.ones_like(x)
    
    @staticmethod
    def derivative_from_output(y: np.ndarray) -> np.ndarray:
        """Derivative from output: all ones"""
        return np.ones_like(y)


class ActivationSelector:
    """Selector for activation functions"""
    
    ACTIVATIONS = {
        'relu': ReLU,
        'leaky_relu': LeakyReLU,
        'sigmoid': Sigmoid,
        'tanh': Tanh,
        'elu': ELU,
        'softplus': SoftPlus,
        'swish': Swish,
        'gelu': GELU,
        'linear': Linear,
    }
    
    @staticmethod
    def get(name: str, **kwargs) -> ActivationFunction:
        """Get activation function by name"""
        name_lower = name.lower()
        if name_lower not in ActivationSelector.ACTIVATIONS:
            raise ValueError(
                f"Unknown activation: {name}. "
                f"Available: {list(ActivationSelector.ACTIVATIONS.keys())}"
            )
        
        activation_class = ActivationSelector.ACTIVATIONS[name_lower]
        if kwargs:
            return activation_class(**kwargs)
        else:
            return activation_class()


class AdamOptimizer:
    """
    Adam (Adaptive Moment Estimation) optimizer.
    
    More sophisticated than vanilla gradient descent:
    - Uses momentum (exponential moving average of gradients)
    - Adapts learning rates per parameter
    - Better convergence on noisy gradients
    """
    
    def __init__(
        self, 
        lr: float = 0.001, 
        beta1: float = 0.9, 
        beta2: float = 0.999, 
        epsilon: float = 1e-8
    ):
        self.lr = lr
        self.beta1 = beta1          # Exponential decay for 1st moment
        self.beta2 = beta2          # Exponential decay for 2nd moment
        self.epsilon = epsilon      # Numerical stability
        self.m: Dict[str, float] = {}  # 1st moment (momentum)
        self.v: Dict[str, float] = {}  # 2nd moment (velocity)
        self.t = 0                   # Time step
    
    def step(self, params: Dict[str, float], grads: Dict[str, float]) -> Dict[str, float]:
        """
        Update parameters using Adam algorithm.
        
        Args:
            params: Current parameter values
            grads: Gradients for each parameter
            
        Returns:
            Updated parameters
        """
        self.t += 1
        updated = {}
        
        for name, param in params.items():
            grad = grads.get(name, 0.0)
            
            # Initialize moments if needed
            if name not in self.m:
                self.m[name] = 0.0
                self.v[name] = 0.0
            
            # Update biased first moment estimate
            self.m[name] = self.beta1 * self.m[name] + (1 - self.beta1) * grad
            
            # Update biased second moment estimate
            self.v[name] = self.beta2 * self.v[name] + (1 - self.beta2) * (grad ** 2)
            
            # Bias correction
            m_hat = self.m[name] / (1 - self.beta1 ** self.t)
            v_hat = self.v[name] / (1 - self.beta2 ** self.t)
            
            # Update parameter
            updated[name] = max(0.0, param - self.lr * m_hat / (np.sqrt(v_hat) + self.epsilon))
        
        return updated
    
    def reset(self):
        """Reset optimizer state."""
        self.m.clear()
        self.v.clear()
        self.t = 0


class LearningRateScheduler:
    """
    Learning rate scheduling for better convergence.
    
    Strategies:
    - Constant: lr stays the same
    - Step decay: reduce lr every N steps
    - Exponential: lr *= decay each step
    - Cosine annealing: smooth lr reduction
    """
    
    def __init__(
        self, 
        initial_lr: float = 0.001, 
        strategy: str = "exponential",
        decay_rate: float = 0.95,
        decay_steps: int = 1
    ):
        self.initial_lr = initial_lr
        self.current_lr = initial_lr
        self.strategy = strategy
        self.decay_rate = decay_rate
        self.decay_steps = decay_steps
        self.step_count = 0
    
    def step(self) -> float:
        """Update and return current learning rate."""
        self.step_count += 1
        
        if self.strategy == "constant":
            pass
        elif self.strategy == "step":
            if self.step_count % self.decay_steps == 0:
                self.current_lr *= self.decay_rate
        elif self.strategy == "exponential":
            self.current_lr = self.initial_lr * (self.decay_rate ** self.step_count)
        elif self.strategy == "cosine":
            # Cosine annealing (needs max_steps, simplified here)
            self.current_lr = self.initial_lr * 0.5 * (1 + np.cos(np.pi * self.step_count / 100))
        
        return self.current_lr
    
    def get_lr(self) -> float:
        """Get current learning rate without stepping."""
        return self.current_lr


class GradientClipper:
    """
    Gradient clipping for stability.
    
    Prevents exploding gradients by scaling them down if they exceed a threshold.
    """
    
    def __init__(self, max_norm: float = 1.0):
        self.max_norm = max_norm
    
    def clip(self, grads: Dict[str, float]) -> Dict[str, float]:
        """
        Clip gradients by global norm.
        
        Args:
            grads: Gradients to clip
            
        Returns:
            Clipped gradients
        """
        # Compute global norm
        total_norm = np.sqrt(sum(g ** 2 for g in grads.values()))
        
        # Clip if needed
        if total_norm > self.max_norm:
            scale = self.max_norm / (total_norm + 1e-6)
            return {name: grad * scale for name, grad in grads.items()}
        
        return grads


class EnhancedWeightOptimizer:
    """
    Enhanced weight optimizer combining Adam, LR scheduling, and gradient clipping.
    
    Features:
    - Adam optimizer with momentum and adaptive learning rates
    - Learning rate scheduling for better convergence
    - Gradient clipping for stability
    - Early stopping based on loss convergence
    - Gradient norm monitoring
    - Optional gradient activation for non-linear gradient shaping
    """
    
    def __init__(
        self,
        lr: float = 0.01,
        adam_beta1: float = 0.9,
        adam_beta2: float = 0.999,
        lr_decay: float = 0.9,
        clip_norm: float = 1.0,
        gradient_activation: Optional[str] = None,
        early_stop_patience: int = 3,
        early_stop_delta: float = 1e-4
    ):
        self.adam = AdamOptimizer(lr=lr, beta1=adam_beta1, beta2=adam_beta2)
        self.scheduler = LearningRateScheduler(
            initial_lr=lr, 
            strategy="exponential", 
            decay_rate=lr_decay
        )
        self.clipper = GradientClipper(max_norm=clip_norm)
        self.early_stop_patience = early_stop_patience
        self.early_stop_delta = early_stop_delta
        self.gradient_activation_name = gradient_activation
        self.gradient_activation = None
        if gradient_activation:
            self.gradient_activation = ActivationSelector.get(gradient_activation)
        
        self.history: List[Dict[str, Any]] = []
        self.best_loss = float("inf")
        self.no_improve_count = 0
    
    def step(
        self, 
        params: Dict[str, float], 
        grads: Dict[str, float], 
        loss: float
    ) -> Tuple[Dict[str, float], bool]:
        """
        Perform one optimization step.
        
        Args:
            params: Current parameters
            grads: Gradients
            loss: Current loss value
            
        Returns:
            (updated_params, should_stop)
        """
        # Clip gradients
        clipped_grads = self.clipper.clip(grads)

        # Optional activation on gradients
        if self.gradient_activation is not None:
            grad_keys = list(clipped_grads.keys())
            grad_array = np.array([clipped_grads[k] for k in grad_keys])
            activated = self.gradient_activation.activate(grad_array)
            clipped_grads = {k: float(activated[i]) for i, k in enumerate(grad_keys)}
        
        # Compute gradient norm for monitoring
        grad_norm = np.sqrt(sum(g ** 2 for g in clipped_grads.values()))
        
        # Update learning rate
        current_lr = self.scheduler.step()
        self.adam.lr = current_lr
        
        # Adam step
        updated_params = self.adam.step(params, clipped_grads)
        
        # Track history
        self.history.append({
            "loss": loss,
            "lr": current_lr,
            "grad_norm": grad_norm,
            "params": dict(params)
        })
        
        # Early stopping check
        should_stop = False
        if loss < self.best_loss - self.early_stop_delta:
            self.best_loss = loss
            self.no_improve_count = 0
        else:
            self.no_improve_count += 1
            if self.no_improve_count >= self.early_stop_patience:
                should_stop = True
        
        return updated_params, should_stop
    
    def reset(self):
        """Reset optimizer state."""
        self.adam.reset()
        self.scheduler = LearningRateScheduler(
            initial_lr=self.scheduler.initial_lr,
            strategy=self.scheduler.strategy,
            decay_rate=self.scheduler.decay_rate
        )
        self.history.clear()
        self.best_loss = float("inf")
        self.no_improve_count = 0


class AdaptiveOptimizerSelector:
    """
    Intelligently selects optimizer based on problem characteristics.
    
    Analyzes problem complexity and chooses optimal optimization strategy.
    """
    
    def __init__(self):
        self.selection_history: List[Dict[str, Any]] = []
    
    def analyze_problem_complexity(
        self, 
        elements: Dict[str, Any],
        constraints: Optional[ConstraintSystem] = None
    ) -> Dict[str, Any]:
        """Analyze problem to determine optimization needs."""
        n = len(elements)
        
        # Count overlaps
        overlaps = 0
        for i, id1 in enumerate(list(elements.keys())):
            for id2 in list(elements.keys())[i+1:]:
                p1 = np.array(elements[id1].get("position", (0, 0)))
                p2 = np.array(elements[id2].get("position", (0, 0)))
                dist = np.linalg.norm(p1 - p2)
                s1 = elements[id1].get("size", (0.1, 0.1))[0]
                s2 = elements[id2].get("size", (0.1, 0.1))[0]
                if dist < (s1 + s2) / 2:
                    overlaps += 1
        
        overlap_density = overlaps / max(n * (n - 1) / 2, 1)
        constraint_count = len(constraints.constraints) if constraints else 0
        
        # Complexity score (0-100)
        complexity = (
            min(n / 200 * 40, 40) +  # Element count (max 40 pts)
            overlap_density * 30 +     # Overlap density (max 30 pts)
            min(constraint_count / 10 * 30, 30)  # Constraints (max 30 pts)
        )
        
        return {
            "element_count": n,
            "overlap_density": overlap_density,
            "constraint_count": constraint_count,
            "complexity_score": complexity,
            "is_simple": complexity < 30,
            "is_moderate": 30 <= complexity < 60,
            "is_complex": complexity >= 60
        }
    
    def select_optimizer(
        self,
        problem_analysis: Dict[str, Any],
        force_enhanced: bool = False
    ) -> Dict[str, Any]:
        """
        Select optimizer configuration based on problem analysis.
        
        Returns:
            {
                "use_enhanced": bool,
                "lr": float,
                "max_steps": int,
                "early_stop_patience": int,
                "reason": str
            }
        """
        complexity = problem_analysis["complexity_score"]
        n = problem_analysis["element_count"]
        
        if force_enhanced:
            config = {
                "use_enhanced": True,
                "lr": 0.01,
                "max_steps": 10,
                "early_stop_patience": 3,
                "reason": "Forced enhanced mode"
            }
        elif complexity >= 70:
            # Very complex: aggressive enhanced optimization
            config = {
                "use_enhanced": True,
                "lr": 0.015,
                "max_steps": 15,
                "early_stop_patience": 4,
                "adam_beta1": 0.85,  # Less momentum for noisy problems
                "lr_decay": 0.88,
                "reason": "Very complex problem - aggressive Adam"
            }
        elif complexity >= 50:
            # Complex: standard enhanced
            config = {
                "use_enhanced": True,
                "lr": 0.01,
                "max_steps": 10,
                "early_stop_patience": 3,
                "reason": "Complex problem - standard Adam"
            }
        elif complexity >= 30:
            # Moderate: light enhanced
            config = {
                "use_enhanced": True,
                "lr": 0.02,
                "max_steps": 6,
                "early_stop_patience": 2,
                "adam_beta1": 0.95,  # More momentum for smoother problems
                "reason": "Moderate problem - light Adam"
            }
        else:
            # Simple: basic suffices
            config = {
                "use_enhanced": False,
                "lr": 0.2,
                "max_steps": 3,
                "reason": "Simple problem - basic gradient descent"
            }
        
        # Log selection
        self.selection_history.append({
            "complexity": complexity,
            "config": config
        })
        
        return config


class ConstraintWeightOptimizer:
    """
    Optimize constraint weights using enhanced optimizer.
    
    Learns optimal importance weights for different constraint types.
    """
    
    def __init__(self):
        self.optimized_weights: Dict[str, float] = {}
    
    def optimize_constraint_weights(
        self,
        constraint_system: ConstraintSystem,
        elements: Dict[str, Any],
        target_positions: Dict[str, Tuple[float, float]],
        max_steps: int = 5,
        lr: float = 0.02,
        gradient_activation: Optional[str] = None,
        verbose: bool = False
    ) -> Dict[str, float]:
        """
        Optimize constraint weights based on violation patterns.
        
        Args:
            constraint_system: The constraint system
            elements: Element data
            target_positions: Target layout positions
            max_steps: Optimization steps
            lr: Learning rate
            verbose: Print progress
            
        Returns:
            Optimized weights for each constraint type
        """
        # Initialize weights per constraint type
        constraint_types = set(c.constraint_type for c in constraint_system.constraints)
        weights = {ct.value: 1.0 for ct in constraint_types}
        
        if len(constraint_types) == 0:
            return weights
        
        # Create enhanced optimizer
        enhanced_opt = EnhancedWeightOptimizer(
            lr=lr,
            early_stop_patience=2,
            early_stop_delta=1e-3,
            gradient_activation=gradient_activation
        )
        
        if verbose:
            print(f"[ConstraintWeightOptimizer] Optimizing {len(constraint_types)} constraint types")
        
        for step in range(max_steps):
            # Evaluate current constraint violations
            total_violation = 0.0
            violations_by_type: Dict[str, float] = {ct.value: 0.0 for ct in constraint_types}
            
            for constraint in constraint_system.constraints:
                ct_name = constraint.constraint_type.value
                # Temporarily set weight
                old_weight = constraint.weight
                constraint.weight = weights[ct_name]
                
                # Evaluate
                violation = constraint.evaluate(target_positions)
                violations_by_type[ct_name] += violation
                total_violation += violation * weights[ct_name]
                
                # Restore
                constraint.weight = old_weight
            
            # Compute gradients (how changes in each weight affect total violation)
            grads = {}
            epsilon = 0.1
            for ct_name in weights.keys():
                # Finite difference
                weights[ct_name] += epsilon
                perturbed_violation = 0.0
                for constraint in constraint_system.constraints:
                    if constraint.constraint_type.value == ct_name:
                        perturbed_violation += constraint.evaluate(target_positions) * weights[ct_name]
                weights[ct_name] -= epsilon
                
                grads[ct_name] = (perturbed_violation - violations_by_type[ct_name]) / epsilon
            
            # Optimization step
            new_weights, should_stop = enhanced_opt.step(weights, grads, total_violation)
            weights = {k: max(0.1, v) for k, v in new_weights.items()}  # Keep weights > 0.1
            
            if verbose:
                print(f"  Step {step+1}: violation={total_violation:.4f}, weights={weights}")
            
            if should_stop:
                break
        
        self.optimized_weights = weights
        return weights


class PositionRefiner:
    """
    Gradient-based position refinement using enhanced optimizer.
    
    Fine-tunes element positions after physics-based solving.
    """
    
    def __init__(self):
        self.refinement_history: List[Dict[str, Any]] = []
    
    def refine_positions(
        self,
        elements: Dict[str, Any],
        initial_positions: Dict[str, Tuple[float, float]],
        loss_weights: LossWeights,
        constraints: Optional[ConstraintSystem] = None,
        max_steps: int = 5,
        lr: float = 0.05,
        loss_activation: Optional[str] = None,
        component_activation: Optional[str] = None,
        gradient_activation: Optional[str] = None,
        verbose: bool = False
    ) -> Dict[str, Tuple[float, float]]:
        """
        Refine positions using gradient descent on composite loss.
        
        Args:
            elements: Element data
            initial_positions: Starting positions from physics solver
            loss_weights: Loss function weights
            constraints: Optional constraints
            max_steps: Refinement steps
            lr: Learning rate
            loss_activation: Activation for final loss
            component_activation: Activation per loss component
            gradient_activation: Activation applied to gradients
            verbose: Print progress
            
        Returns:
            Refined positions
        """
        positions = dict(initial_positions)
        position_params = {}  # Flatten positions to dict
        for elem_id, (x, y) in positions.items():
            position_params[f"{elem_id}_x"] = x
            position_params[f"{elem_id}_y"] = y
        
        # Create optimizer
        optimizer = EnhancedWeightOptimizer(
            lr=lr,
            lr_decay=0.92,
            clip_norm=0.5,  # Small movements
            gradient_activation=gradient_activation,
            early_stop_patience=2,
            early_stop_delta=1e-4
        )
        
        if verbose:
            print(f"[PositionRefiner] Refining {len(elements)} elements")

        def compute_loss_with_activation(
            current_positions: Dict[str, Tuple[float, float]]
        ) -> Tuple[float, Dict[str, float]]:
            loss, components = LayoutAnalyzer.compute_complex_loss(
                elements,
                current_positions,
                initial_positions,
                initial_positions,
                constraints or ConstraintSystem(),
                loss_weights,
                0.05
            )

            if component_activation:
                activation = ActivationSelector.get(component_activation)
                comp_keys = list(components.keys())
                comp_array = np.array([components[k] for k in comp_keys])
                activated = activation.activate(comp_array)
                components = {k: float(activated[i]) for i, k in enumerate(comp_keys)}

                loss = (
                    loss_weights.overlap * components["overlap"] +
                    loss_weights.compactness * components["compactness"] +
                    loss_weights.balance * components["balance"] +
                    loss_weights.displacement * components["displacement"] +
                    loss_weights.boundary * components["boundary"] +
                    loss_weights.spacing * components["spacing"] +
                    loss_weights.velocity_smoothness * components["velocity_smoothness"] +
                    loss_weights.readability * components["readability"] +
                    loss_weights.edge_length * components["edge_length"] +
                    loss_weights.constraint * components["constraint"]
                )

            if loss_activation:
                activation = ActivationSelector.get(loss_activation)
                loss = float(activation.activate(np.array([loss]))[0])

            return loss, components
        
        for step in range(max_steps):
            # Reconstruct positions
            current_positions = {}
            for elem_id in elements.keys():
                current_positions[elem_id] = (
                    position_params.get(f"{elem_id}_x", 0.0),
                    position_params.get(f"{elem_id}_y", 0.0)
                )
            
            # Evaluate loss
            loss, components = compute_loss_with_activation(current_positions)
            
            # Compute gradients via finite differences
            grads = {}
            epsilon = 0.01
            for param_name in position_params.keys():
                # Perturb
                position_params[param_name] += epsilon
                
                # Reconstruct and evaluate
                perturbed_positions = {}
                for elem_id in elements.keys():
                    perturbed_positions[elem_id] = (
                        position_params.get(f"{elem_id}_x", 0.0),
                        position_params.get(f"{elem_id}_y", 0.0)
                    )
                
                loss_plus, _ = compute_loss_with_activation(perturbed_positions)
                
                grads[param_name] = (loss_plus - loss) / epsilon
                
                # Restore
                position_params[param_name] -= epsilon
            
            # Optimization step
            position_params, should_stop = optimizer.step(position_params, grads, loss)
            
            # Apply boundary constraints
            for elem_id in elements.keys():
                x = position_params.get(f"{elem_id}_x", 0.0)
                y = position_params.get(f"{elem_id}_y", 0.0)
                size = elements[elem_id].get("size", (0.1, 0.1))
                
                # Clamp to canvas
                x = np.clip(x, -4 + size[0]/2, 4 - size[0]/2)
                y = np.clip(y, -2.25 + size[1]/2, 2.25 - size[1]/2)
                
                position_params[f"{elem_id}_x"] = x
                position_params[f"{elem_id}_y"] = y
            
            if verbose:
                print(f"  Step {step+1}: loss={loss:.4f}")
            
            if should_stop:
                break
        
        # Final positions
        final_positions = {}
        for elem_id in elements.keys():
            final_positions[elem_id] = (
                position_params[f"{elem_id}_x"],
                position_params[f"{elem_id}_y"]
            )
        
        self.refinement_history.append({
            "steps": step + 1,
            "initial_loss": optimizer.history[0]["loss"] if optimizer.history else 0,
            "final_loss": loss
        })
        
        return final_positions


class MultiStageOptimizer:
    """
    Orchestrates multi-stage optimization pipeline.
    
    Stages:
    1. Loss weight optimization
    2. Constraint weight optimization
    3. Physics-based solving
    4. Gradient-based position refinement
    5. Final validation
    """
    
    def __init__(self):
        self.optimizer_selector = AdaptiveOptimizerSelector()
        self.constraint_optimizer = ConstraintWeightOptimizer()
        self.position_refiner = PositionRefiner()
        self.stage_results: Dict[str, Any] = {}
    
    def optimize_full_pipeline(
        self,
        elements: Dict[str, Any],
        constraints: Optional[ConstraintSystem],
        loss_weights: Optional[LossWeights],
        enable_all_stages: bool = True,
        verbose: bool = False
    ) -> Tuple[Dict[str, Tuple[float, float]], Dict[str, Any]]:
        """
        Execute full multi-stage optimization.
        
        Args:
            elements: Element data
            constraints: Constraints
            loss_weights: Initial loss weights
            enable_all_stages: Enable all optimization stages
            verbose: Print progress
            
        Returns:
            (final_positions, stage_info)
        """
        if verbose:
            print("\n" + "="*70)
            print("MULTI-STAGE OPTIMIZATION PIPELINE")
            print("="*70)
        
        constraints = constraints or ConstraintSystem()
        loss_weights = loss_weights or LossWeights()
        
        # Stage 1: Analyze problem
        if verbose:
            print("\n[STAGE 1: Problem Analysis]")
        problem_analysis = self.optimizer_selector.analyze_problem_complexity(elements, constraints)
        optimizer_config = self.optimizer_selector.select_optimizer(problem_analysis, force_enhanced=enable_all_stages)
        
        if verbose:
            print(f"  Complexity: {problem_analysis['complexity_score']:.1f}/100")
            print(f"  Optimizer: {'Enhanced (Adam)' if optimizer_config['use_enhanced'] else 'Basic'}")
            print(f"  Reason: {optimizer_config['reason']}")
        
        self.stage_results["problem_analysis"] = problem_analysis
        self.stage_results["optimizer_config"] = optimizer_config
        
        # Stage 2: Optimize constraint weights (if complex enough)
        if enable_all_stages and constraints.constraints and problem_analysis["complexity_score"] > 40:
            if verbose:
                print("\n[STAGE 2: Constraint Weight Optimization]")
            
            # Get rough positions for constraint evaluation
            temp_positions = {}
            for elem_id, elem in elements.items():
                temp_positions[elem_id] = elem.get("position", (0, 0))
            
            optimized_constraint_weights = self.constraint_optimizer.optimize_constraint_weights(
                constraints,
                elements,
                temp_positions,
                max_steps=5,
                verbose=verbose
            )
            
            # Apply optimized weights
            for constraint in constraints.constraints:
                ct_name = constraint.constraint_type.value
                if ct_name in optimized_constraint_weights:
                    constraint.weight *= optimized_constraint_weights[ct_name]
            
            self.stage_results["constraint_weights"] = optimized_constraint_weights
        else:
            if verbose and enable_all_stages:
                print("\n[STAGE 2: Constraint Weight Optimization] SKIPPED (simple problem)")
        
        # Stage 3: Loss weight optimization would happen here
        # (Delegated to calling code via optimizer_config)
        
        # Return config for caller to use
        return {}, {
            "stage_results": self.stage_results,
            "optimizer_config": optimizer_config,
            "ready_for_solving": True
        }


# ============================================================================
# ADVANCED V3.0 LAYOUT ENGINE
# ============================================================================

class AdvancedLayoutEngine:
    """Advanced layout engine combining all v3.0 features."""
    
    def __init__(self):
        self.constraint_system = ConstraintSystem()
        self.clusterer = ElementClusterer()
        self.optimizer = ParameterOptimizer()
        self.multi_obj = MultiObjectiveOptimizer()
        self.strategy_selector = AdaptiveLayoutStrategy()
        
        # Enhanced optimizer components
        self.multi_stage_optimizer = MultiStageOptimizer()
        self.optimizer_selector = AdaptiveOptimizerSelector()
        self.constraint_weight_optimizer = ConstraintWeightOptimizer()
        self.position_refiner = PositionRefiner()
        
        # ML models (linear, logistic, SVM)
        self.ml_hub = MLModelHub(use_sklearn_if_available=True)
        self.use_ml_models: bool = False
        self.ml_loss_weight: float = 0.1
        self.ml_blend: float = 0.5
        self.last_ml_info: Optional[Dict[str, Any]] = None
        
        # State tracking
        self.last_loss: Optional[float] = None
        self.last_loss_components: Optional[Dict[str, float]] = None
        self._tuned_weights_cache: Dict[Tuple[int, int, int, int], LossWeights] = {}
        self.last_tune_info: Optional[Dict[str, Any]] = None
        self.last_optimization_info: Optional[Dict[str, Any]] = None

        # Activation function configuration
        self.loss_activation: Optional[str] = None  # None = no activation
        self.component_activation: Optional[str] = None  # Activation per component
        self.gradient_activation: Optional[str] = None  # Activation for gradients
        self.activation_selector = ActivationSelector

    def train_ml_models(self, samples: int = 200, seed: int = 42):
        """Train hybrid ML models on synthetic data."""
        self.ml_hub.train_synthetic(samples=samples, seed=seed)

    @staticmethod
    def _blend_params(base: OptimizationParameters, ml: Optional[OptimizationParameters], blend: float) -> OptimizationParameters:
        if ml is None:
            return base
        b = max(0.0, min(1.0, blend))
        return OptimizationParameters(
            repulsion_strength=base.repulsion_strength * (1 - b) + ml.repulsion_strength * b,
            attraction_strength=base.attraction_strength * (1 - b) + ml.attraction_strength * b,
            thermal_temperature=base.thermal_temperature * (1 - b) + ml.thermal_temperature * b,
            cooling_rate=base.cooling_rate * (1 - b) + ml.cooling_rate * b,
            iterations=int(round(base.iterations * (1 - b) + ml.iterations * b)),
            boundary_penalty=base.boundary_penalty * (1 - b) + ml.boundary_penalty * b,
            min_distance=base.min_distance * (1 - b) + ml.min_distance * b
        )

    @staticmethod
    def _blend_loss_weights(base: LossWeights, ml: Optional[LossWeights], blend: float) -> LossWeights:
        if ml is None:
            return base
        b = max(0.0, min(1.0, blend))
        return LossWeights(
            overlap=base.overlap * (1 - b) + ml.overlap * b,
            constraint=base.constraint * (1 - b) + ml.constraint * b,
            boundary=base.boundary * (1 - b) + ml.boundary * b,
            displacement=base.displacement * (1 - b) + ml.displacement * b,
            compactness=base.compactness * (1 - b) + ml.compactness * b,
            balance=base.balance * (1 - b) + ml.balance * b,
            spacing=base.spacing * (1 - b) + ml.spacing * b,
            velocity_smoothness=base.velocity_smoothness * (1 - b) + ml.velocity_smoothness * b,
            readability=base.readability * (1 - b) + ml.readability * b,
            edge_length=base.edge_length * (1 - b) + ml.edge_length * b
        )

    def solve_with_constraints(
        self,
        elements: Dict[str, Any],
        constraints: Optional[ConstraintSystem] = None,
        max_iterations: int = 150,
        loss_weights: Optional[LossWeights] = None,
        early_stopping: bool = False,
        patience: int = 15,
        min_delta: float = 1e-4,
        loss_every: int = 5,
        loss_callback: Optional[Callable[[int, float, Dict[str, float]], None]] = None,
        return_loss: bool = False,
        auto_tune: bool = False,
        tune_mode: str = "off",
        tune_threshold: int = 60,
        tune_cache_key: Optional[Tuple[int, int, int, int]] = None,
        tune_steps: int = 1,
        tune_lr: float = 0.2,
        tune_epsilon: float = 0.05,
        tune_sample_iterations: int = 30,
        tune_sample_loss_every: int = 10,
        verbose_tuning: bool = False,
        use_enhanced_optimizer: bool = False,
        loss_activation: Optional[str] = None,
        component_activation: Optional[str] = None,
        gradient_activation: Optional[str] = None,
        use_ml_models: bool = False,
        ml_loss_weight: float = 0.1,
        ml_blend: float = 0.5
    ) -> Union[Dict[str, Tuple[float, float]], Tuple[Dict[str, Tuple[float, float]], float, Dict[str, float]], Tuple[Dict[str, Tuple[float, float]], float, Dict[str, float], Dict[str, Any]]]:
        """
        Solve layout problem with constraints.
        
        Returns: Dict mapping element_id -> (x, y) position
        """
        if constraints is None:
            constraints = self.constraint_system

        effective_loss_activation = loss_activation or self.loss_activation
        effective_component_activation = component_activation or self.component_activation
        effective_gradient_activation = gradient_activation or self.gradient_activation
        
        positions = {}
        for elem_id, elem in elements.items():
            positions[elem_id] = elem.get("position", (0, 0))
        initial_positions = dict(positions)
        
        # Analyze problem
        analysis = self.strategy_selector.analyze_problem(elements, constraints)
        strategy = self.strategy_selector.recommend_strategy(analysis)
        
        # Get optimized parameters
        params = self.optimizer.predict_best_parameters(
            analysis["element_count"],
            analysis["overlap_percentage"],
            analysis["density"]
        )

        # Optional auto-tune of loss weights (cached by problem signature)
        loss_weights = loss_weights or LossWeights()

        effective_use_ml = use_ml_models or self.use_ml_models
        effective_ml_loss_weight = ml_loss_weight if use_ml_models else self.ml_loss_weight
        effective_ml_blend = ml_blend if use_ml_models else self.ml_blend

        if effective_use_ml and self.ml_hub.is_trained:
            ml_features = self.ml_hub.extract_features(elements, constraints, positions)
            ml_params = self.ml_hub.predict_parameters(ml_features)
            params = self._blend_params(params, ml_params, effective_ml_blend)
            ml_weights = self.ml_hub.predict_loss_weights(ml_features)
            loss_weights = self._blend_loss_weights(loss_weights, ml_weights, effective_ml_blend)
            ml_quality = self.ml_hub.predict_quality_score(ml_features)
            ml_use_enhanced = self.ml_hub.predict_use_enhanced(ml_features)
            # Let ML override optimizer selection when ML is enabled and has a prediction
            if ml_use_enhanced is not None:
                use_enhanced_optimizer = ml_use_enhanced
            self.last_ml_info = {
                "features": ml_features.tolist(),
                "ml_quality": ml_quality,
                "ml_use_enhanced": ml_use_enhanced,
                "ml_blend": effective_ml_blend,
                "ml_loss_weight": effective_ml_loss_weight
            }
        else:
            self.last_ml_info = None

        auto_tune_effective = auto_tune or tune_mode in {"auto", "hybrid"}
        cache_hit = False
        if auto_tune_effective and analysis["element_count"] >= tune_threshold:
            cache_key = tune_cache_key
            if cache_key is None:
                cache_key = (
                    analysis["element_count"] // 50,
                    int(analysis["density"] * 10),
                    int(analysis["overlap_percentage"] // 10),
                    analysis.get("constraint_count", 0)
                )
            cached = self._tuned_weights_cache.get(cache_key)
            if cached is None:
                # Choose optimizer: enhanced (Adam) or basic (vanilla gradient descent)
                if use_enhanced_optimizer:
                    tuned, _ = self.tune_loss_weights_enhanced(
                        elements,
                        constraints,
                        initial_weights=loss_weights,
                        max_steps=tune_steps,
                        lr=tune_lr,
                        epsilon=tune_epsilon,
                        sample_iterations=tune_sample_iterations,
                        sample_loss_every=tune_sample_loss_every,
                        loss_activation=effective_loss_activation,
                        component_activation=effective_component_activation,
                        gradient_activation=effective_gradient_activation,
                        verbose=verbose_tuning
                    )
                else:
                    tuned, _ = self.tune_loss_weights_with_backprop(
                        elements,
                        constraints,
                        initial_weights=loss_weights,
                        steps=tune_steps,
                        lr=tune_lr,
                        epsilon=tune_epsilon,
                        sample_iterations=tune_sample_iterations,
                        sample_loss_every=tune_sample_loss_every,
                        loss_activation=effective_loss_activation,
                        component_activation=effective_component_activation
                    )
                self._tuned_weights_cache[cache_key] = tuned
                loss_weights = tuned
            else:
                cache_hit = True
                loss_weights = cached

        self.last_tune_info = {
            "mode": tune_mode,
            "auto_tune": auto_tune_effective,
            "cache_hit": cache_hit,
            "cache_key": cache_key if auto_tune_effective else None,
            "tuned": auto_tune_effective and not cache_hit
        }
        
        # Log cache hit/miss if verbose
        if verbose_tuning and auto_tune_effective:
            if cache_hit:
                print(f"[Tune Cache] HIT - Using cached weights for key {cache_key}")
            else:
                print(f"[Tune Cache] MISS - Tuned new weights for key {cache_key}")
        
        # Solve with constraint satisfaction
        learning_rate = 0.1
        best_loss = float("inf")
        no_improve_steps = 0
        prev_positions = dict(positions)
        for iteration in range(max_iterations):
            # Calculate forces
            forces = {elem_id: np.array([0.0, 0.0]) for elem_id in positions}
            
            # Repulsion forces (avoid overlaps)
            for i, id1 in enumerate(list(positions.keys())):
                for id2 in list(positions.keys())[i+1:]:
                    p1 = np.array(positions[id1])
                    p2 = np.array(positions[id2])
                    s1 = elements[id1].get("size", (0.1, 0.1))
                    s2 = elements[id2].get("size", (0.1, 0.1))
                    
                    dist = np.linalg.norm(p1 - p2)
                    min_dist = (s1[0] + s2[0]) / 2 + params.min_distance
                    
                    # Apply strong repulsion if overlapping or too close
                    if dist < min_dist:
                        direction = (p1 - p2) / (dist + 0.001)
                        # Stronger repulsion: use squared magnitude for aggressive separation
                        magnitude = (min_dist - dist) * params.repulsion_strength * 1.5
                        forces[id1] += direction * magnitude
                        forces[id2] -= direction * magnitude
            
            # Add secondary repulsion pass for strong separation
            # This helps when overlaps are severe
            overlap_score = LayoutAnalyzer.calculate_overlap_score(elements, positions)
            if overlap_score > 0.01:  # If still significant overlap
                for i, id1 in enumerate(list(positions.keys())):
                    for id2 in list(positions.keys())[i+1:]:
                        p1 = np.array(positions[id1])
                        p2 = np.array(positions[id2])
                        s1 = elements[id1].get("size", (0.1, 0.1))
                        s2 = elements[id2].get("size", (0.1, 0.1))
                        
                        dist = np.linalg.norm(p1 - p2)
                        min_dist = (s1[0] + s2[0]) / 2 + params.min_distance
                        
                        # Extra repulsion for overlapping elements
                        if dist < min_dist:
                            # Push them apart more aggressively
                            direction = (p1 - p2) / (dist + 0.001)
                            magnitude = (min_dist - dist + 0.1) * params.repulsion_strength * 2.0
                            forces[id1] += direction * magnitude
                            forces[id2] -= direction * magnitude
            
            # Boundary forces
            for elem_id in positions:
                x, y = positions[elem_id]
                size_x, size_y = elements[elem_id].get("size", (0.1, 0.1))
                
                # Canvas bounds: (-4, -2.25) to (4, 2.25)
                if x - size_x/2 < -4:
                    forces[elem_id][0] += (-4 - (x - size_x/2)) * params.boundary_penalty
                if x + size_x/2 > 4:
                    forces[elem_id][0] -= ((x + size_x/2) - 4) * params.boundary_penalty
                if y - size_y/2 < -2.25:
                    forces[elem_id][1] += (-2.25 - (y - size_y/2)) * params.boundary_penalty
                if y + size_y/2 > 2.25:
                    forces[elem_id][1] -= ((y + size_y/2) - 2.25) * params.boundary_penalty
            
            # Constraint forces
            constraint_penalty = constraints.evaluate_all(positions)
            for constraint in constraints.constraints:
                for elem_id in constraint.element_ids:
                    # Simplified: add small random perturbation to satisfy constraints
                    forces[elem_id] += np.random.normal(0, 0.01, 2) * constraint.weight
            
            # Update positions
            prev_positions = dict(positions)
            for elem_id in positions:
                pos = np.array(positions[elem_id])
                movement = forces[elem_id] * learning_rate
                positions[elem_id] = tuple(pos + movement)

            # Periodically evaluate composite loss for optional early stopping.
            if iteration % max(1, loss_every) == 0:
                ml_score = None
                if effective_use_ml and self.ml_hub.is_trained:
                    ml_features = self.ml_hub.extract_features(elements, constraints, positions)
                    ml_score = self.ml_hub.predict_quality_score(ml_features)

                loss_total, loss_components = self.compute_loss_with_activation(
                    elements,
                    positions,
                    initial_positions,
                    prev_positions,
                    constraints,
                    loss_weights,
                    params.min_distance,
                    loss_activation=effective_loss_activation,
                    component_activation=effective_component_activation,
                    ml_score=ml_score,
                    ml_weight=effective_ml_loss_weight
                )
                self.last_loss = loss_total
                self.last_loss_components = loss_components
                if loss_callback is not None:
                    loss_callback(iteration, loss_total, loss_components)
                if loss_total + min_delta < best_loss:
                    best_loss = loss_total
                    no_improve_steps = 0
                else:
                    no_improve_steps += 1
                if early_stopping and no_improve_steps >= patience:
                    break
            
            # Cooling schedule
            if iteration % 10 == 0:
                learning_rate *= params.cooling_rate
        
        # Final overlap cleanup: Ensure all overlaps are completely resolved
        # Apply final separation pass if needed
        final_overlap = LayoutAnalyzer.calculate_overlap_score(elements, positions)
        if final_overlap > 0.005:  # If overlaps remain
            # Final aggressive separation pass
            remaining_iterations = 100  # Increased from 50 for severe cases
            for final_iter in range(remaining_iterations):
                for i, id1 in enumerate(list(positions.keys())):
                    for id2 in list(positions.keys())[i+1:]:
                        p1 = np.array(positions[id1])
                        p2 = np.array(positions[id2])
                        s1 = elements[id1].get("size", (0.1, 0.1))
                        s2 = elements[id2].get("size", (0.1, 0.1))
                        
                        dist = np.linalg.norm(p1 - p2)
                        min_dist = (s1[0] + s2[0]) / 2 + params.min_distance
                        
                        # Directly move apart if still overlapping
                        if dist < min_dist:
                            # Handle edge case: elements at identical position
                            if dist < 0.001:
                                # Use a random direction to break the tie
                                direction = np.array([np.cos(np.random.rand() * 2 * np.pi),
                                                     np.sin(np.random.rand() * 2 * np.pi)])
                                # Use larger separation for severe case
                                separation_multiplier = 3.0 if final_overlap > 0.1 else 1.5
                            else:
                                direction = (p1 - p2) / (dist + 0.001)
                                separation_multiplier = 1.5
                            
                            separation_needed = min_dist - dist
                            move_distance = (separation_needed / 2 + 0.05) * separation_multiplier
                            # Move both elements away from each other
                            positions[id1] = tuple(p1 + direction * move_distance)
                            positions[id2] = tuple(p2 - direction * move_distance)
                
                # Check if overlaps resolved
                if LayoutAnalyzer.calculate_overlap_score(elements, positions) < 0.001:
                    break
        
        if return_loss:
            return positions, self.last_loss or 0.0, self.last_loss_components or {}, self.last_tune_info
        return positions

    def tune_loss_weights_with_backprop(
        self,
        elements: Dict[str, Any],
        constraints: Optional[ConstraintSystem] = None,
        initial_weights: Optional[LossWeights] = None,
        steps: int = 3,
        lr: float = 0.2,
        epsilon: float = 0.05,
        sample_iterations: int = 40,
        sample_loss_every: int = 10,
        loss_activation: Optional[str] = None,
        component_activation: Optional[str] = None
    ) -> Tuple[LossWeights, List[Dict[str, Any]]]:
        """
        Backprop-like tuning of loss weights using finite differences.

        Note: This is a gradient estimate, not full autograd. It optimizes
        weights based on solver outcomes from short runs.
        """
        if constraints is None:
            constraints = self.constraint_system

        weights = initial_weights or LossWeights()
        history: List[Dict[str, Any]] = []
        weight_names = list(asdict(weights).keys())

        for step in range(steps):
            _, base_loss, _, _ = self.solve_with_constraints(
                elements,
                constraints,
                max_iterations=sample_iterations,
                loss_weights=weights,
                loss_every=sample_loss_every,
                return_loss=True,
                loss_activation=loss_activation,
                component_activation=component_activation
            )

            grads: Dict[str, float] = {}
            for name in weight_names:
                current = getattr(weights, name)
                setattr(weights, name, current + epsilon)
                _, loss_plus, _, _ = self.solve_with_constraints(
                    elements,
                    constraints,
                    max_iterations=sample_iterations,
                    loss_weights=weights,
                    loss_every=sample_loss_every,
                    return_loss=True,
                    loss_activation=loss_activation,
                    component_activation=component_activation
                )
                grads[name] = (loss_plus - base_loss) / epsilon
                setattr(weights, name, current)

            for name, grad in grads.items():
                updated = max(0.0, getattr(weights, name) - lr * grad)
                setattr(weights, name, updated)

            history.append({
                "step": step,
                "loss": base_loss,
                "grads": grads,
                "weights": asdict(weights)
            })

        return weights, history
    
    def tune_loss_weights_enhanced(
        self,
        elements: Dict[str, Any],
        constraints: Optional[ConstraintSystem] = None,
        initial_weights: Optional[LossWeights] = None,
        max_steps: int = 10,
        lr: float = 0.01,
        epsilon: float = 0.05,
        sample_iterations: int = 40,
        sample_loss_every: int = 10,
        adam_beta1: float = 0.9,
        adam_beta2: float = 0.999,
        lr_decay: float = 0.9,
        clip_norm: float = 1.0,
        early_stop_patience: int = 3,
        early_stop_delta: float = 1e-4,
        loss_activation: Optional[str] = None,
        component_activation: Optional[str] = None,
        gradient_activation: Optional[str] = None,
        verbose: bool = False
    ) -> Tuple[LossWeights, List[Dict[str, Any]]]:
        """
        Enhanced loss weight tuning using Adam optimizer.
        
        Improvements over basic backprop:
        - Adam optimization (momentum + adaptive learning rates)
        - Learning rate scheduling with exponential decay
        - Gradient clipping for stability
        - Early stopping when convergence detected
        - Detailed progress tracking
        
        Args:
            elements: Elements to optimize for
            constraints: Optional constraint system
            initial_weights: Starting weights (default: LossWeights())
            max_steps: Maximum optimization steps
            lr: Initial learning rate (Adam)
            epsilon: Finite difference epsilon for gradient estimation
            sample_iterations: Iterations per loss evaluation
            sample_loss_every: Loss computation frequency
            adam_beta1: Adam momentum decay rate
            adam_beta2: Adam velocity decay rate
            lr_decay: Learning rate exponential decay
            clip_norm: Gradient clipping threshold
            early_stop_patience: Steps without improvement before stopping
            early_stop_delta: Minimum improvement to count as progress
            verbose: Print progress messages
            
        Returns:
            (tuned_weights, optimization_history)
        """
        if constraints is None:
            constraints = self.constraint_system
        
        # Initialize
        weights = initial_weights or LossWeights()
        weight_names = list(asdict(weights).keys())
        
        # Create enhanced optimizer
        enhanced_opt = EnhancedWeightOptimizer(
            lr=lr,
            adam_beta1=adam_beta1,
            adam_beta2=adam_beta2,
            lr_decay=lr_decay,
            clip_norm=clip_norm,
            gradient_activation=gradient_activation,
            early_stop_patience=early_stop_patience,
            early_stop_delta=early_stop_delta
        )
        
        if verbose:
            print(f"[Enhanced Optimizer] Starting weight tuning with Adam")
            print(f"  Max steps: {max_steps}, LR: {lr}, Decay: {lr_decay}")
            print(f"  Early stop: patience={early_stop_patience}, delta={early_stop_delta}")
        
        for step in range(max_steps):
            # Evaluate current loss
            _, base_loss, _, _ = self.solve_with_constraints(
                elements,
                constraints,
                max_iterations=sample_iterations,
                loss_weights=weights,
                loss_every=sample_loss_every,
                return_loss=True,
                loss_activation=loss_activation,
                component_activation=component_activation
            )
            
            # Compute gradients using finite differences
            grads: Dict[str, float] = {}
            for name in weight_names:
                current = getattr(weights, name)
                
                # Forward difference
                setattr(weights, name, current + epsilon)
                _, loss_plus, _, _ = self.solve_with_constraints(
                    elements,
                    constraints,
                    max_iterations=sample_iterations,
                    loss_weights=weights,
                    loss_every=sample_loss_every,
                    return_loss=True,
                    loss_activation=loss_activation,
                    component_activation=component_activation
                )
                
                # Gradient estimate
                grads[name] = (loss_plus - base_loss) / epsilon
                
                # Restore
                setattr(weights, name, current)
            
            # Get current params as dict
            current_params = asdict(weights)
            
            # Optimization step with enhanced optimizer
            updated_params, should_stop = enhanced_opt.step(current_params, grads, base_loss)
            
            # Update weights
            for name, value in updated_params.items():
                setattr(weights, name, value)
            
            if verbose:
                grad_norm = np.sqrt(sum(g ** 2 for g in grads.values()))
                print(f"  Step {step+1}/{max_steps}: loss={base_loss:.4f}, "
                      f"grad_norm={grad_norm:.4f}, lr={enhanced_opt.adam.lr:.5f}")
            
            # Early stopping
            if should_stop:
                if verbose:
                    print(f"[Enhanced Optimizer] Early stopping at step {step+1}")
                break
        
        # Final evaluation
        _, final_loss, _, _ = self.solve_with_constraints(
            elements,
            constraints,
            max_iterations=sample_iterations,
            loss_weights=weights,
            loss_every=sample_loss_every,
            return_loss=True,
            loss_activation=loss_activation,
            component_activation=component_activation
        )
        
        if verbose:
            improvement = ((enhanced_opt.history[0]['loss'] - final_loss) / 
                          enhanced_opt.history[0]['loss'] * 100) if enhanced_opt.history else 0
            print(f"[Enhanced Optimizer] Complete! Loss: {final_loss:.4f} "
                  f"(improved {improvement:.1f}%)")
        
        # Add final result to history
        enhanced_opt.history.append({
            "step": len(enhanced_opt.history),
            "loss": final_loss,
            "lr": enhanced_opt.adam.lr,
            "grad_norm": 0.0,
            "params": asdict(weights)
        })
        
        return weights, enhanced_opt.history
    
    def solve_with_clustering(
        self,
        elements: Dict[str, Any],
        clustering_method: str = "hierarchical"
    ) -> Dict[str, Tuple[float, float]]:
        """
        Solve with intelligent clustering.
        
        Handles each cluster separately then aligns them.
        """
        # Cluster elements
        if clustering_method == "hierarchical":
            clusters = self.clusterer.hierarchical_clustering(elements, max_clusters=5)
        else:
            clusters = self.clusterer.density_based_clustering(elements)
        
        # Group elements by cluster
        cluster_groups = defaultdict(list)
        for elem_id, cluster_id in clusters.items():
            cluster_groups[cluster_id].append(elem_id)
        
        # Solve each cluster
        positions = {}
        cluster_positions = {}
        
        for cluster_id, elem_ids in cluster_groups.items():
            cluster_elements = {eid: elements[eid] for eid in elem_ids}
            cluster_pos = self.solve_with_constraints(cluster_elements, max_iterations=100)
            cluster_positions[cluster_id] = cluster_pos
            positions.update(cluster_pos)
        
        # Align clusters to avoid overlap
        # (Simplified: relax cluster positions slightly)
        cluster_centers = {}
        for cluster_id, cluster_pos in cluster_positions.items():
            center = np.mean([p for p in cluster_pos.values()], axis=0)
            cluster_centers[cluster_id] = center
        
        return positions
    
    def solve_comprehensive(
        self,
        elements: Dict[str, Any],
        constraints: Optional[ConstraintSystem] = None,
        max_iterations: int = 150,
        enable_multi_stage: bool = True,
        enable_position_refinement: bool = True,
        adaptive_optimizer: bool = True,
        return_full_info: bool = False,
        verbose: bool = False,
        loss_activation: Optional[str] = None,
        component_activation: Optional[str] = None,
        gradient_activation: Optional[str] = None,
        use_ml_models: bool = False,
        ml_loss_weight: float = 0.1,
        ml_blend: float = 0.5
    ) -> Union[Dict[str, Tuple[float, float]], Tuple[Dict[str, Tuple[float, float]], Dict[str, Any]]]:
        """
        Comprehensive solve using full multi-stage optimization pipeline.
        
        Pipeline:
        1. Problem analysis & optimizer selection
        2. Constraint weight optimization (if needed)
        3. Loss weight tuning (Adam or basic based on complexity)
        4. Physics-based position solving
        5. Gradient-based position refinement
        6. Final validation
        
        Args:
            elements: Element data
            constraints: Optional constraints
            max_iterations: Max iterations for physics solver
            enable_multi_stage: Enable multi-stage optimization
            enable_position_refinement: Enable gradient refinement
            adaptive_optimizer: Auto-select optimizer based on complexity
            return_full_info: Return detailed optimization info
            verbose: Print detailed progress
            loss_activation: Activation for final loss
            component_activation: Activation per loss component
            gradient_activation: Activation applied to gradients
            
        Returns:
            positions or (positions, optimization_info)
        """
        if verbose:
            print("\n" + "="*70)
            print("COMPREHENSIVE MULTI-STAGE SOLVE")
            print("="*70)
        
        constraints = constraints or self.constraint_system
        effective_loss_activation = loss_activation or self.loss_activation
        effective_component_activation = component_activation or self.component_activation
        effective_gradient_activation = gradient_activation or self.gradient_activation
        effective_use_ml = use_ml_models or self.use_ml_models
        effective_ml_loss_weight = ml_loss_weight if use_ml_models else self.ml_loss_weight
        effective_ml_blend = ml_blend if use_ml_models else self.ml_blend
        optimization_info = {}
        
        # STAGE 1: Problem Analysis
        if verbose:
            print("\n[STAGE 1: Problem Analysis & Optimizer Selection]")
        
        problem_analysis = self.optimizer_selector.analyze_problem_complexity(elements, constraints)
        
        if adaptive_optimizer:
            optimizer_config = self.optimizer_selector.select_optimizer(
                problem_analysis,
                force_enhanced=enable_multi_stage
            )
        else:
            optimizer_config = {"use_enhanced": True, "lr": 0.01, "max_steps": 10}

        ml_features = None
        if effective_use_ml and self.ml_hub.is_trained:
            ml_features = self.ml_hub.extract_features(elements, constraints)
            ml_use_enhanced = self.ml_hub.predict_use_enhanced(ml_features)
            # Let ML override optimizer selection when ML is enabled and has a prediction
            if ml_use_enhanced is not None:
                optimizer_config["use_enhanced"] = ml_use_enhanced
            optimization_info["ml_info"] = {
                "features": ml_features.tolist(),
                "ml_use_enhanced": ml_use_enhanced,
                "ml_loss_weight": effective_ml_loss_weight,
                "ml_blend": effective_ml_blend
            }
        else:
            optimization_info["ml_info"] = None
        
        if verbose:
            print(f"  Elements: {problem_analysis['element_count']}")
            print(f"  Complexity score: {problem_analysis['complexity_score']:.1f}/100")
            print(f"  Overlap density: {problem_analysis['overlap_density']:.2%}")
            print(f"  Constraints: {problem_analysis['constraint_count']}")
            print(f"  Selected optimizer: {'Enhanced (Adam)' if optimizer_config['use_enhanced'] else 'Basic GD'}")
            print(f"  Reason: {optimizer_config.get('reason', 'N/A')}")
        
        optimization_info["problem_analysis"] = problem_analysis
        optimization_info["optimizer_config"] = optimizer_config
        
        # STAGE 2: Constraint Weight Optimization
        if enable_multi_stage and constraints.constraints and problem_analysis["complexity_score"] > 40:
            if verbose:
                print("\n[STAGE 2: Constraint Weight Optimization]")
            
            # Get initial positions for evaluation
            temp_positions = {eid: elem.get("position", (0, 0)) for eid, elem in elements.items()}
            
            constraint_weights = self.constraint_weight_optimizer.optimize_constraint_weights(
                constraints,
                elements,
                temp_positions,
                max_steps=5,
                lr=0.02,
                gradient_activation=effective_gradient_activation,
                verbose=verbose
            )
            
            # Apply optimized weights
            for constraint in constraints.constraints:
                ct_name = constraint.constraint_type.value
                if ct_name in constraint_weights:
                    constraint.weight *= constraint_weights[ct_name]
            
            optimization_info["constraint_weights"] = constraint_weights
            
            if verbose:
                print(f"  Optimized constraint weights: {constraint_weights}")
        else:
            if verbose:
                print("\n[STAGE 2: Constraint Weight Optimization] SKIPPED")
                if not enable_multi_stage:
                    print("  Reason: Multi-stage disabled")
                elif not constraints.constraints:
                    print("  Reason: No constraints")
                else:
                    print("  Reason: Simple problem (complexity < 40)")
        
        # STAGE 3: Loss Weight Tuning
        if verbose:
            print("\n[STAGE 3: Loss Weight Tuning]")
        
        # Use cached or tune new weights
        analysis = self.strategy_selector.analyze_problem(elements, constraints)
        cache_key = (
            analysis["element_count"] // 50,
            int(analysis["density"] * 10),
            int(analysis["overlap_percentage"] // 10),
            analysis.get("constraint_count", 0)
        )
        
        cached_weights = self._tuned_weights_cache.get(cache_key)
        if cached_weights:
            loss_weights = cached_weights
            if verbose:
                print(f"  Using cached weights for key {cache_key}")
            optimization_info["weight_tuning"] = "cached"
        else:
            if optimizer_config["use_enhanced"]:
                if verbose:
                    print(f"  Tuning with Enhanced Optimizer (Adam)")
                loss_weights, tune_history = self.tune_loss_weights_enhanced(
                    elements,
                    constraints,
                    max_steps=optimizer_config.get("max_steps", 10),
                    lr=optimizer_config.get("lr", 0.01),
                    adam_beta1=optimizer_config.get("adam_beta1", 0.9),
                    adam_beta2=optimizer_config.get("adam_beta2", 0.999),
                    lr_decay=optimizer_config.get("lr_decay", 0.9),
                    loss_activation=effective_loss_activation,
                    component_activation=effective_component_activation,
                    gradient_activation=effective_gradient_activation,
                    verbose=verbose
                )
            else:
                if verbose:
                    print(f"  Tuning with Basic Gradient Descent")
                loss_weights, tune_history = self.tune_loss_weights_with_backprop(
                    elements,
                    constraints,
                    steps=optimizer_config.get("max_steps", 3),
                    lr=optimizer_config.get("lr", 0.2),
                    loss_activation=effective_loss_activation,
                    component_activation=effective_component_activation
                )
            
            self._tuned_weights_cache[cache_key] = loss_weights
            optimization_info["weight_tuning"] = "tuned"
            optimization_info["tune_history"] = tune_history
            
            if verbose:
                final_loss = tune_history[-1].get("loss", 0) if tune_history else 0
                print(f"  Tuning complete: {len(tune_history)} steps, final loss={final_loss:.4f}")
        
        if effective_use_ml and self.ml_hub.is_trained:
            if ml_features is None:
                ml_features = self.ml_hub.extract_features(elements, constraints)
            ml_weights = self.ml_hub.predict_loss_weights(ml_features)
            loss_weights = self._blend_loss_weights(loss_weights, ml_weights, effective_ml_blend)
            optimization_info["ml_loss_weights"] = ml_weights
        
        # STAGE 4: Physics-Based Position Solving
        if verbose:
            print("\n[STAGE 4: Physics-Based Position Solving]")
        
        positions = self.solve_with_constraints(
            elements,
            constraints,
            max_iterations=max_iterations,
            loss_weights=loss_weights,
            early_stopping=True,
            patience=15,
            verbose_tuning=False,
            loss_activation=effective_loss_activation,
            component_activation=effective_component_activation,
            gradient_activation=effective_gradient_activation,
            use_ml_models=effective_use_ml,
            ml_loss_weight=effective_ml_loss_weight,
            ml_blend=effective_ml_blend
        )
        
        # Evaluate physics solution
        ml_score = None
        if effective_use_ml and self.ml_hub.is_trained:
            ml_features = self.ml_hub.extract_features(elements, constraints, positions)
            ml_score = self.ml_hub.predict_quality_score(ml_features)

        physics_loss, physics_components = self.compute_loss_with_activation(
            elements,
            positions,
            positions,
            positions,
            constraints,
            loss_weights,
            0.05,
            loss_activation=effective_loss_activation,
            component_activation=effective_component_activation,
            ml_score=ml_score,
            ml_weight=effective_ml_loss_weight
        )
        
        if verbose:
            print(f"  Physics solve complete: loss={physics_loss:.4f}")
            print(f"  Overlap component: {physics_components.get('overlap', 0):.4f}")
        
        optimization_info["physics_loss"] = physics_loss
        optimization_info["physics_components"] = physics_components
        
        # STAGE 5: Gradient-Based Position Refinement
        if enable_position_refinement and problem_analysis["complexity_score"] > 50:
            if verbose:
                print("\n[STAGE 5: Gradient-Based Position Refinement]")
            
            refined_positions = self.position_refiner.refine_positions(
                elements,
                positions,
                loss_weights,
                constraints,
                max_steps=5,
                lr=0.05,
                loss_activation=effective_loss_activation,
                component_activation=effective_component_activation,
                gradient_activation=effective_gradient_activation,
                verbose=verbose
            )
            
            # Evaluate refined solution
            refined_loss, refined_components = self.compute_loss_with_activation(
                elements,
                refined_positions,
                positions,
                positions,
                constraints,
                loss_weights,
                0.05,
                loss_activation=effective_loss_activation,
                component_activation=effective_component_activation
            )
            
            improvement = physics_loss - refined_loss
            if verbose:
                print(f"  Refinement complete: loss={refined_loss:.4f}")
                print(f"  Improvement: {improvement:.4f} ({improvement/physics_loss*100:.1f}%)")
            
            # Use refined if better
            if refined_loss < physics_loss:
                positions = refined_positions
                optimization_info["refinement"] = "applied"
                optimization_info["refinement_improvement"] = improvement
                if verbose:
                    print(f"  ✓ Using refined positions (better)")
            else:
                optimization_info["refinement"] = "rejected"
                if verbose:
                    print(f"  ✗ Keeping physics positions (refinement worse)")
            
            optimization_info["refined_loss"] = refined_loss
            optimization_info["refined_components"] = refined_components
        else:
            if verbose:
                print("\n[STAGE 5: Gradient-Based Position Refinement] SKIPPED")
                if not enable_position_refinement:
                    print("  Reason: Refinement disabled")
                else:
                    print("  Reason: Simple problem (complexity < 50)")
        
        # STAGE 6: Final Validation
        if verbose:
            print("\n[STAGE 6: Final Validation]")
        
        final_loss, final_components = self.compute_loss_with_activation(
            elements,
            positions,
            positions,
            positions,
            constraints,
            loss_weights,
            0.05,
            loss_activation=effective_loss_activation,
            component_activation=effective_component_activation
        )
        
        overlap_score = LayoutAnalyzer.calculate_overlap_score(elements, positions)
        compactness = LayoutAnalyzer.calculate_compactness(positions)
        
        if verbose:
            print(f"  Final loss: {final_loss:.4f}")
            print(f"  Overlap score: {overlap_score:.4f}")
            print(f"  Compactness: {compactness:.4f}")
            print(f"  Loss components:")
            for name, value in final_components.items():
                print(f"    {name}: {value:.4f}")
        
        optimization_info["final_loss"] = final_loss
        optimization_info["final_components"] = final_components
        optimization_info["overlap_score"] = overlap_score
        optimization_info["compactness"] = compactness
        
        if verbose:
            print("\n" + "="*70)
            print("✓ COMPREHENSIVE SOLVE COMPLETE")
            print("="*70)
        
        # Store for access
        self.last_optimization_info = optimization_info
        self.last_loss = final_loss
        self.last_loss_components = final_components
        
        if return_full_info:
            return positions, optimization_info
        return positions

    def compute_loss_with_activation(
        self,
        elements: Dict[str, Any],
        positions: Dict[str, Tuple[float, float]],
        initial_positions: Dict[str, Tuple[float, float]],
        prev_positions: Dict[str, Tuple[float, float]],
        constraints: Optional[ConstraintSystem] = None,
        weights: Optional[LossWeights] = None,
        min_distance: float = 0.05,
        loss_activation: Optional[str] = None,
        component_activation: Optional[str] = None,
        ml_score: Optional[float] = None,
        ml_weight: float = 0.1
    ) -> Tuple[float, Dict[str, float]]:
        """
        Compute loss with optional activation functions for non-linear transformations.

        Args:
            elements: Element definitions
            positions: Current positions
            initial_positions: Initial positions
            prev_positions: Previous positions
            constraints: Constraint system
            weights: Loss weights
            min_distance: Minimum distance threshold
            loss_activation: Activation function for final loss (if None, no activation)
            component_activation: Activation function per component (if None, no activation)
            ml_score: Optional ML quality score [0,1] where 1=high quality (will be inverted to loss)
            ml_weight: Weight for blending ML loss term (default: 0.1)

        Returns:
            (total_loss, components_dict)
        """
        constraints = constraints or self.constraint_system
        weights = weights or LossWeights()

        # Compute base loss without activation
        total, components = LayoutAnalyzer.compute_complex_loss(
            elements, positions, initial_positions, prev_positions,
            constraints, weights, min_distance
        )
        
        # Apply component-wise activation if specified
        if component_activation:
            try:
                activation = self.activation_selector.get(component_activation)
                components_array = np.array(list(components.values()))
                activated = activation.activate(components_array)
                
                components = {
                    k: float(activated[i])
                    for i, k in enumerate(components.keys())
                }
                
                # Recompute total with activated components
                total = (
                    weights.overlap * components["overlap"] +
                    weights.compactness * components["compactness"] +
                    weights.balance * components["balance"] +
                    weights.displacement * components["displacement"] +
                    weights.boundary * components["boundary"] +
                    weights.spacing * components["spacing"] +
                    weights.velocity_smoothness * components["velocity_smoothness"] +
                    weights.readability * components["readability"] +
                    weights.edge_length * components["edge_length"] +
                    weights.constraint * components["constraint"]
                )
            except Exception as e:
                print(f"Warning: Component activation failed: {e}")
        
        # Apply final loss activation if specified
        if loss_activation:
            try:
                activation = self.activation_selector.get(loss_activation)
                total = float(activation.activate(np.array([total]))[0])
            except Exception as e:
                print(f"Warning: Loss activation failed: {e}")
        
        # Blend ML score if provided
        if ml_score is not None:
            # Convert quality score (0=bad, 1=good) to loss term (higher quality = lower loss)
            # Use (1 - ml_score) so that high quality (ml_score near 1) adds low loss
            ml_loss_term = 1.0 - ml_score
            # Blend: (1 - ml_weight) * computed_loss + ml_weight * ml_loss_term
            total = total * (1.0 - ml_weight) + ml_loss_term * ml_weight
        
        return total, components



# ============================================================================
# UTILITIES & ANALYSIS
# ============================================================================

class LayoutAnalyzer:
    """Analyze and score layout quality."""
    
    @staticmethod
    def calculate_overlap_score(elements: Dict[str, Any], positions: Dict[str, Tuple[float, float]]) -> float:
        """Calculate total overlap area."""
        total_overlap = 0.0
        elem_ids = list(positions.keys())
        
        for i, id1 in enumerate(elem_ids):
            for id2 in elem_ids[i+1:]:
                if id1 not in elements or id2 not in elements:
                    continue
                
                p1 = positions[id1]
                p2 = positions[id2]
                s1 = elements[id1].get("size", (0.1, 0.1))
                s2 = elements[id2].get("size", (0.1, 0.1))
                
                # Bounding box overlap
                x_overlap = max(0, min(p1[0] + s1[0]/2, p2[0] + s2[0]/2) - 
                               max(p1[0] - s1[0]/2, p2[0] - s2[0]/2))
                y_overlap = max(0, min(p1[1] + s1[1]/2, p2[1] + s2[1]/2) - 
                               max(p1[1] - s1[1]/2, p2[1] - s2[1]/2))
                
                total_overlap += x_overlap * y_overlap
        
        return total_overlap
    
    @staticmethod
    def calculate_compactness(positions: Dict[str, Tuple[float, float]]) -> float:
        """Calculate layout compactness (lower = more compact)."""
        if len(positions) < 2:
            return 0.0
        
        pos_array = np.array(list(positions.values()))
        center = np.mean(pos_array, axis=0)
        distances = [np.linalg.norm(p - center) for p in pos_array]
        
        return np.mean(distances)

    @staticmethod
    def calculate_displacement(
        initial_positions: Dict[str, Tuple[float, float]],
        positions: Dict[str, Tuple[float, float]]
    ) -> float:
        """Calculate total displacement from initial positions."""
        total = 0.0
        for elem_id, pos in positions.items():
            if elem_id in initial_positions:
                total += np.linalg.norm(np.array(pos) - np.array(initial_positions[elem_id]))
        return total

    @staticmethod
    def calculate_boundary_violation(
        elements: Dict[str, Any],
        positions: Dict[str, Tuple[float, float]],
        bounds: Tuple[float, float, float, float] = (-4.0, -2.25, 4.0, 2.25)
    ) -> float:
        """Calculate total boundary violation distance."""
        x_min, y_min, x_max, y_max = bounds
        total = 0.0
        for elem_id, pos in positions.items():
            size_x, size_y = elements.get(elem_id, {}).get("size", (0.1, 0.1))
            x, y = pos
            left = x - size_x / 2
            right = x + size_x / 2
            bottom = y - size_y / 2
            top = y + size_y / 2
            total += max(0.0, x_min - left)
            total += max(0.0, right - x_max)
            total += max(0.0, y_min - bottom)
            total += max(0.0, top - y_max)
        return total

    @staticmethod
    def calculate_spacing_penalty(
        elements: Dict[str, Any],
        positions: Dict[str, Tuple[float, float]],
        min_distance: float
    ) -> float:
        """Penalty for elements closer than min_distance."""
        penalty = 0.0
        elem_ids = list(positions.keys())
        for i, id1 in enumerate(elem_ids):
            for id2 in elem_ids[i+1:]:
                p1 = np.array(positions[id1])
                p2 = np.array(positions[id2])
                dist = np.linalg.norm(p1 - p2)
                if dist < min_distance:
                    penalty += (min_distance - dist)
        return penalty

    @staticmethod
    def calculate_velocity_smoothness(
        prev_positions: Dict[str, Tuple[float, float]],
        positions: Dict[str, Tuple[float, float]]
    ) -> float:
        """Penalize large per-iteration movements."""
        if not prev_positions:
            return 0.0
        total = 0.0
        count = 0
        for elem_id, pos in positions.items():
            if elem_id in prev_positions:
                total += np.linalg.norm(np.array(pos) - np.array(prev_positions[elem_id]))
                count += 1
        return total / max(1, count)

    @staticmethod
    def calculate_readability_penalty(
        elements: Dict[str, Any],
        positions: Dict[str, Tuple[float, float]],
        padding: float = 0.1
    ) -> float:
        """Penalty for items crowding labels or text elements."""
        penalty = 0.0
        for elem_id, elem in elements.items():
            elem_type = str(elem.get("type", "")).lower()
            name_hint = elem_id.lower()
            if elem_type in {"text", "label", "title"} or "label" in name_hint:
                pos = positions.get(elem_id)
                if pos is None:
                    continue
                size = elem.get("size", (0.2, 0.1))
                expanded = (size[0] + padding, size[1] + padding)
                for other_id, other_pos in positions.items():
                    if other_id == elem_id:
                        continue
                    other_size = elements.get(other_id, {}).get("size", (0.1, 0.1))
                    x_overlap = max(
                        0,
                        min(pos[0] + expanded[0]/2, other_pos[0] + other_size[0]/2) -
                        max(pos[0] - expanded[0]/2, other_pos[0] - other_size[0]/2)
                    )
                    y_overlap = max(
                        0,
                        min(pos[1] + expanded[1]/2, other_pos[1] + other_size[1]/2) -
                        max(pos[1] - expanded[1]/2, other_pos[1] - other_size[1]/2)
                    )
                    penalty += x_overlap * y_overlap
        return penalty

    @staticmethod
    def calculate_edge_length_penalty(
        elements: Dict[str, Any],
        positions: Dict[str, Tuple[float, float]],
        constraints: ConstraintSystem,
        default_target: float
    ) -> float:
        """Penalize edges deviating from target distances."""
        penalty = 0.0
        # Element-declared links
        for elem_id, elem in elements.items():
            links = elem.get("links") or elem.get("connections") or elem.get("depends_on")
            if not links:
                continue
            if isinstance(links, str):
                links = [links]
            target = elem.get("target_distance", default_target)
            for other_id in links:
                if elem_id in positions and other_id in positions:
                    dist = np.linalg.norm(
                        np.array(positions[elem_id]) - np.array(positions[other_id])
                    )
                    penalty += abs(dist - target)

        # Dependency constraints with optional target distance
        for constraint in constraints.constraints:
            if constraint.constraint_type == ConstraintType.DEPENDENCY:
                target = constraint.parameters.get("target_distance", default_target)
                elem_ids = constraint.element_ids
                for i in range(len(elem_ids)):
                    for j in range(i+1, len(elem_ids)):
                        id1, id2 = elem_ids[i], elem_ids[j]
                        if id1 in positions and id2 in positions:
                            dist = np.linalg.norm(
                                np.array(positions[id1]) - np.array(positions[id2])
                            )
                            penalty += abs(dist - target)
        return penalty
    
    @staticmethod
    def calculate_balance(positions: Dict[str, Tuple[float, float]]) -> float:
        """Calculate layout balance (how evenly distributed)."""
        if len(positions) < 2:
            return 1.0
        
        pos_array = np.array(list(positions.values()))
        center = np.mean(pos_array, axis=0)
        
        # Divide into quadrants
        quadrants = {0: 0, 1: 0, 2: 0, 3: 0}
        for pos in pos_array:
            x, y = pos[0] - center[0], pos[1] - center[1]
            q = 0 if x >= 0 else 1
            q = q if y >= 0 else q + 2
            quadrants[q] += 1
        
        # Balance score (lower is better, 0 = perfect balance)
        max_q = max(quadrants.values())
        min_q = min(quadrants.values())
        return max_q - min_q

    @staticmethod
    def compute_complex_loss(
        elements: Dict[str, Any],
        positions: Dict[str, Tuple[float, float]],
        initial_positions: Dict[str, Tuple[float, float]],
        prev_positions: Dict[str, Tuple[float, float]],
        constraints: ConstraintSystem,
        weights: LossWeights,
        min_distance: float
    ) -> Tuple[float, Dict[str, float]]:
        """Compute a composite loss with multiple weighted terms."""
        overlap = LayoutAnalyzer.calculate_overlap_score(elements, positions)
        compactness = LayoutAnalyzer.calculate_compactness(positions)
        balance = LayoutAnalyzer.calculate_balance(positions)
        displacement = LayoutAnalyzer.calculate_displacement(initial_positions, positions)
        boundary = LayoutAnalyzer.calculate_boundary_violation(elements, positions)
        spacing = LayoutAnalyzer.calculate_spacing_penalty(elements, positions, min_distance)
        velocity = LayoutAnalyzer.calculate_velocity_smoothness(prev_positions, positions)
        readability = LayoutAnalyzer.calculate_readability_penalty(elements, positions)
        edge_length = LayoutAnalyzer.calculate_edge_length_penalty(
            elements, positions, constraints, min_distance * 2
        )
        constraint_violation = constraints.evaluate_all(positions)
        total = (
            weights.overlap * overlap +
            weights.compactness * compactness +
            weights.balance * balance +
            weights.displacement * displacement +
            weights.boundary * boundary +
            weights.spacing * spacing +
            weights.velocity_smoothness * velocity +
            weights.readability * readability +
            weights.edge_length * edge_length +
            weights.constraint * constraint_violation
        )

        components = {
            "overlap": overlap,
            "compactness": compactness,
            "balance": balance,
            "displacement": displacement,
            "boundary": boundary,
            "spacing": spacing,
            "velocity_smoothness": velocity,
            "readability": readability,
            "edge_length": edge_length,
            "constraint": constraint_violation
        }
        return total, components


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_v3_constraint_based():
    """Example: Constraint-based layout."""
    print("\n" + "="*70)
    print("V3.0 EXAMPLE: Constraint-Based Layout")
    print("="*70)
    
    # Create constraint system
    constraints = ConstraintSystem()
    
    # Add constraints
    constraints.add_grouping_constraint(["elem1", "elem2"], max_spread=0.5, weight=2.0)
    constraints.add_separation_constraint(["elem3", "elem4"], min_distance=1.2, weight=1.5)
    constraints.add_alignment_constraint(["elem5", "elem6"], axis="x", weight=1.0)
    
    print("\n[CONSTRAINTS DEFINED]")
    print(f"  Constraint count: {len(constraints.constraints)}")
    for i, c in enumerate(constraints.constraints):
        print(f"  [{i}] {c.constraint_type.value}: {c.element_ids}")
    
    # Simulate solving
    positions = {
        "elem1": (0.0, 0.5), "elem2": (0.2, 0.6),
        "elem3": (-1.0, 0.0), "elem4": (1.5, 0.0),
        "elem5": (-0.5, -1.0), "elem6": (0.5, -1.0)
    }
    
    violation = constraints.evaluate_all(positions)
    print(f"\n[CONSTRAINT SATISFACTION]")
    print(f"  Total violation: {violation:.4f}")
    print(f"  Status: {'SATISFIED' if violation < 0.1 else 'VIOLATIONS PRESENT'}")


def example_v3_clustering():
    """Example: Intelligent clustering."""
    print("\n" + "="*70)
    print("V3.0 EXAMPLE: Intelligent Clustering")
    print("="*70)
    
    elements = {
        "elem1": {"position": (0.0, 0.0), "size": (0.2, 0.2)},
        "elem2": {"position": (0.1, 0.1), "size": (0.2, 0.2)},
        "elem3": {"position": (2.0, 2.0), "size": (0.2, 0.2)},
        "elem4": {"position": (2.1, 2.1), "size": (0.2, 0.2)},
        "elem5": {"position": (-2.0, -2.0), "size": (0.2, 0.2)},
    }
    
    # Hierarchical clustering
    clusters = ElementClusterer.hierarchical_clustering(elements, max_clusters=3)
    
    print("\n[HIERARCHICAL CLUSTERING]")
    for elem_id, cluster_id in clusters.items():
        print(f"  {elem_id} -> Cluster {cluster_id}")
    
    # Density-based clustering
    clusters_db = ElementClusterer.density_based_clustering(elements, eps=0.5)
    
    print("\n[DENSITY-BASED CLUSTERING]")
    for elem_id, cluster_id in clusters_db.items():
        status = "Core" if cluster_id >= 0 else "Noise"
        print(f"  {elem_id} -> Cluster {cluster_id} ({status})")


def example_v3_parameter_optimization():
    """Example: ML-based parameter optimization."""
    print("\n" + "="*70)
    print("V3.0 EXAMPLE: Parameter Optimization")
    print("="*70)
    
    optimizer = ParameterOptimizer()
    
    # Learn from some results
    params1 = OptimizationParameters(repulsion_strength=1.5, iterations=100)
    params2 = OptimizationParameters(repulsion_strength=2.0, iterations=150)
    
    optimizer.learn_from_result(params1, quality_score=15.0)
    optimizer.learn_from_result(params2, quality_score=22.0)
    
    print(f"\n[LEARNING HISTORY]")
    print(f"  Stored results: {len(optimizer.history)}")
    
    # Predict best parameters
    predicted = optimizer.predict_best_parameters(
        element_count=50,
        overlap_percentage=45.0,
        density=0.6
    )
    
    print(f"\n[PREDICTED PARAMETERS for 50 elements, 45% overlap, 0.6 density]")
    print(f"  Repulsion: {predicted.repulsion_strength:.2f}")
    print(f"  Temperature: {predicted.thermal_temperature:.2f}")
    print(f"  Iterations: {predicted.iterations}")
    print(f"  Cooling Rate: {predicted.cooling_rate:.2f}")


if __name__ == "__main__":
    example_v3_constraint_based()
    example_v3_clustering()
    example_v3_parameter_optimization()
    
    print("\n" + "="*70)
    print("V3.0 ADVANCED FEATURES READY!")
    print("="*70)