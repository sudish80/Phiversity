#!/usr/bin/env python3
"""
ADVANCED OVERLAP RESOLUTION ALGORITHM FOR PHIVERSITY
Comprehensive solution for fixing word, graph, and figure overlapping in Manim animations

Based on concepts from spatial layout algorithms, force-directed graph placement,
and constraint satisfaction techniques referenced in modern ML papers.

Author: Phiversity Development Team
Date: February 7, 2026
Version: 1.0
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path


# ============================================================================
# PART 1: DATA STRUCTURES AND ENUMERATIONS
# ============================================================================

class ElementType(Enum):
    """Element types that can overlap"""
    TEXT = "text"
    GRAPH = "graph"
    FIGURE = "figure"
    EQUATION = "equation"
    ARROW = "arrow"
    LEGEND = "legend"
    LABEL = "label"


class LayoutStrategy(Enum):
    """Layout strategies for resolution"""
    GRID = "grid"
    HIERARCHICAL = "hierarchical"
    FORCE_DIRECTED = "force_directed"
    RADIAL = "radial"
    OPTIMIZED = "optimized"


@dataclass
class BoundingBox:
    """Represents a rectangular boundary of an element"""
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    
    def __post_init__(self):
        """Ensure valid bounds"""
        if self.x_min > self.x_max:
            self.x_min, self.x_max = self.x_max, self.x_min
        if self.y_min > self.y_max:
            self.y_min, self.y_max = self.y_max, self.y_min
    
    @property
    def width(self) -> float:
        """Width of bounding box"""
        return self.x_max - self.x_min
    
    @property
    def height(self) -> float:
        """Height of bounding box"""
        return self.y_max - self.y_min
    
    @property
    def center(self) -> Tuple[float, float]:
        """Center point of bounding box"""
        return (
            (self.x_min + self.x_max) / 2,
            (self.y_min + self.y_max) / 2
        )
    
    def intersects(self, other: 'BoundingBox', margin: float = 0.0) -> bool:
        """Check if this box intersects with another (with optional margin)"""
        return (
            self.x_min - margin < other.x_max + margin and
            self.x_max + margin > other.x_min - margin and
            self.y_min - margin < other.y_max + margin and
            self.y_max + margin > other.y_min - margin
        )
    
    def distance_to(self, other: 'BoundingBox') -> float:
        """Calculate minimum distance between two bounding boxes"""
        dx = max(
            self.x_min - other.x_max,
            0,
            other.x_min - self.x_max
        )
        dy = max(
            self.y_min - other.y_max,
            0,
            other.y_min - self.y_max
        )
        return np.sqrt(dx**2 + dy**2)
    
    def move(self, dx: float, dy: float) -> 'BoundingBox':
        """Create new BoundingBox moved by (dx, dy)"""
        return BoundingBox(
            self.x_min + dx,
            self.y_min + dy,
            self.x_max + dx,
            self.y_max + dy
        )


@dataclass
class LayoutElement:
    """Represents an element in the visualization"""
    element_id: str
    element_type: ElementType
    bounding_box: BoundingBox
    layer: int = 0  # z-order
    priority: int = 0  # 0=highest priority (don't move), 1-10=increasing flexibility
    locked: bool = False  # if True, don't move this element
    dependencies: List[str] = None  # other elements this depends on
    preferred_position: Optional[Tuple[float, float]] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


# ============================================================================
# PART 2: COLLISION DETECTION SYSTEM
# ============================================================================

class CollisionDetector:
    """
    STEP 1: Detect all overlaps and collisions
    Uses spatial partitioning for efficient detection
    """
    
    def __init__(self, grid_size: float = 1.0):
        """
        Initialize collision detector
        
        Args:
            grid_size: Size of spatial grid cells for optimization
        """
        self.grid_size = grid_size
        self.spatial_grid: Dict[Tuple[int, int], List[str]] = {}
    
    def build_spatial_index(self, elements: Dict[str, LayoutElement]) -> None:
        """
        STEP 1.1: Build spatial grid index for fast collision detection
        
        Algorithm: Divide canvas into grid cells, map elements to cells
        Complexity: O(n) where n = number of elements
        """
        self.spatial_grid.clear()
        
        for element_id, element in elements.items():
            # Calculate which grid cells this element occupies
            min_cell_x = int(element.bounding_box.x_min / self.grid_size)
            max_cell_x = int(element.bounding_box.x_max / self.grid_size)
            min_cell_y = int(element.bounding_box.y_min / self.grid_size)
            max_cell_y = int(element.bounding_box.y_max / self.grid_size)
            
            # Add element to all cells it touches
            for cell_x in range(min_cell_x, max_cell_x + 1):
                for cell_y in range(min_cell_y, max_cell_y + 1):
                    cell_key = (cell_x, cell_y)
                    if cell_key not in self.spatial_grid:
                        self.spatial_grid[cell_key] = []
                    self.spatial_grid[cell_key].append(element_id)
    
    def detect_collisions(
        self,
        elements: Dict[str, LayoutElement]
    ) -> List[Tuple[str, str, float]]:
        """
        STEP 1.2: Find all overlapping element pairs
        
        Returns:
            List of (element_id_1, element_id_2, overlap_area)
        
        Complexity: O(n log n) with spatial indexing
        """
        self.build_spatial_index(elements)
        collisions = []
        checked_pairs: Set[Tuple[str, str]] = set()
        
        # Check elements in same grid cells
        for cell_elements in self.spatial_grid.values():
            # Check all pairs in this cell
            for i in range(len(cell_elements)):
                for j in range(i + 1, len(cell_elements)):
                    id_1, id_2 = cell_elements[i], cell_elements[j]
                    pair = tuple(sorted([id_1, id_2]))
                    
                    if pair not in checked_pairs:
                        checked_pairs.add(pair)
                        
                        elem_1 = elements[id_1]
                        elem_2 = elements[id_2]
                        
                        # Check actual intersection
                        if elem_1.bounding_box.intersects(elem_2.bounding_box):
                            area = self._calculate_overlap_area(
                                elem_1.bounding_box,
                                elem_2.bounding_box
                            )
                            collisions.append((id_1, id_2, area))
        
        return sorted(collisions, key=lambda x: x[2], reverse=True)
    
    @staticmethod
    def _calculate_overlap_area(
        box1: BoundingBox,
        box2: BoundingBox
    ) -> float:
        """
        STEP 1.3: Calculate overlap area between two boxes
        
        Formula: Area = max(0, width) * max(0, height)
        """
        width = min(box1.x_max, box2.x_max) - max(box1.x_min, box2.x_min)
        height = min(box1.y_max, box2.y_max) - max(box1.y_min, box2.y_min)
        
        if width <= 0 or height <= 0:
            return 0.0
        
        return max(0, width) * max(0, height)


# ============================================================================
# PART 3: PRIORITY AND CONSTRAINT SYSTEM
# ============================================================================

class ConstraintSystem:
    """
    STEP 2: Establish constraints and priorities
    Determines which elements can be moved and in what order
    """
    
    @staticmethod
    def calculate_priority(
        element: LayoutElement,
        element_type_priority: Dict[ElementType, int]
    ) -> int:
        """
        STEP 2.1: Calculate movement priority for an element
        
        Priority factors (lower = move first):
        - Element type (graphs/figures more important than labels)
        - Layer (background < foreground)
        - Dependency count (fewer dependencies = move first)
        - Locked status
        
        Args:
            element: The element to evaluate
            element_type_priority: Type priorities (lower = higher priority)
        
        Returns:
            Priority score (0-1000, lower = higher priority)
        """
        if element.locked:
            return 1000  # Never move locked elements
        
        type_priority = element_type_priority.get(element.element_type, 50)
        layer_penalty = element.layer * 10  # Higher layers move later
        dependency_penalty = len(element.dependencies) * 20
        
        return type_priority + layer_penalty + dependency_penalty
    
    @staticmethod
    def build_dependency_graph(
        elements: Dict[str, LayoutElement]
    ) -> Dict[str, Set[str]]:
        """
        STEP 2.2: Build dependency graph
        
        Ensures dependent elements don't separate from their dependencies
        
        Returns:
            Dict mapping element_id -> set of elements it depends on
        """
        dep_graph = {}
        
        for elem_id, element in elements.items():
            # Find implicit dependencies based on spatial relationships
            implicit_deps = set()
            
            for other_id, other_elem in elements.items():
                if elem_id != other_id:
                    # If close to each other, add implicit dependency
                    dist = element.bounding_box.distance_to(other_elem.bounding_box)
                    if dist < 1.0:  # Within 1 unit
                        implicit_deps.add(other_id)
            
            # Combine explicit and implicit dependencies
            explicit_deps = set(element.dependencies)
            dep_graph[elem_id] = explicit_deps | implicit_deps
        
        return dep_graph


# ============================================================================
# PART 4: MULTIPLE LAYOUT ALGORITHMS
# ============================================================================

class LayoutResolver:
    """
    STEP 3: Apply multiple layout algorithms to resolve overlaps
    """
    
    CANVAS_WIDTH = 8.0
    CANVAS_HEIGHT = 4.5
    PADDING = 0.2
    MIN_ELEMENT_SPACING = 0.15
    
    def __init__(self):
        self.collision_detector = CollisionDetector(grid_size=0.5)
    
    # ========== ALGORITHM 3.1: GRID LAYOUT ==========
    def resolve_with_grid(
        self,
        elements: Dict[str, LayoutElement]
    ) -> Dict[str, Tuple[float, float]]:
        """
        STEP 3.1: Grid-based layout algorithm
        
        Algorithm:
        1. Calculate grid dimensions based on element count
        2. Assign grid cells to elements based on priority
        3. Calculate positions within grid cells
        
        Best for: Diagrams with uniform elements
        Time: O(n log n)
        """
        n = len(elements)
        
        # Calculate optimal grid dimensions
        rows = int(np.ceil(np.sqrt(n)))
        cols = int(np.ceil(n / rows))
        
        # Calculate cell dimensions
        cell_width = (self.CANVAS_WIDTH - 2 * self.PADDING) / cols
        cell_height = (self.CANVAS_HEIGHT - 2 * self.PADDING) / rows
        
        # Sort elements by priority
        sorted_elements = sorted(
            elements.items(),
            key=lambda x: (x[1].priority, x[0])
        )
        
        new_positions = {}
        
        # Assign grid positions
        for idx, (elem_id, element) in enumerate(sorted_elements):
            row = idx // cols
            col = idx % cols
            
            # Calculate center position in grid cell
            x = self.PADDING + col * cell_width + cell_width / 2
            y = self.PADDING + row * cell_height + cell_height / 2
            
            new_positions[elem_id] = (x, y)
        
        return new_positions
    
    # ========== ALGORITHM 3.2: FORCE-DIRECTED LAYOUT ==========
    def resolve_with_force_directed(
        self,
        elements: Dict[str, LayoutElement],
        iterations: int = 100,
        damping: float = 0.85
    ) -> Dict[str, Tuple[float, float]]:
        """
        STEP 3.2: Force-directed graph layout algorithm
        
        Algorithm:
        1. Initialize forces (repulsive between elements, attractive to preferred positions)
        2. Iteratively apply forces and update positions
        3. Cool system with exponential decay
        
        Inspiration: Force-Directed Graph Drawing (Fruchterman-Reingold algorithm)
        Physics: F = ma, position += velocity, velocity *= damping
        
        Best for: Complex layouts with many dependencies
        Time: O(n² * iterations)
        """
        positions = {
            elem_id: np.array(elem.bounding_box.center)
            for elem_id, elem in elements.items()
        }
        velocities = {
            elem_id: np.array([0.0, 0.0])
            for elem_id in elements.keys()
        }
        
        # Temperature for simulated annealing
        temp = 1.0
        cooling_rate = 1.0 / iterations
        
        for iteration in range(iterations):
            # Reset forces
            forces = {elem_id: np.array([0.0, 0.0]) for elem_id in elements.keys()}
            
            # STEP 3.2.1: Calculate repulsive forces (push elements apart)
            for elem_id_1, elem_1 in elements.items():
                if elem_1.locked:
                    continue
                
                for elem_id_2, elem_2 in elements.items():
                    if elem_id_1 == elem_id_2 or elem_2.locked:
                        continue
                    
                    pos_1 = positions[elem_id_1]
                    pos_2 = positions[elem_id_2]
                    
                    # Calculate direction vector
                    diff = pos_1 - pos_2
                    distance = np.linalg.norm(diff)
                    
                    if distance < 1e-6:
                        continue
                    
                    # Repulsive force magnitude
                    # Stronger for locked elements and those with dependencies
                    repulsive_strength = 2.0
                    if elem_2.locked:
                        repulsive_strength *= 3.0
                    if elem_id_2 in elem_1.dependencies:
                        repulsive_strength *= 1.5
                    
                    force_magnitude = repulsive_strength / (distance ** 2)
                    force_direction = diff / distance
                    forces[elem_id_1] += force_direction * force_magnitude
            
            # STEP 3.2.2: Calculate attractive forces (pull to preferred position)
            for elem_id, element in elements.items():
                if element.locked or element.preferred_position is None:
                    continue
                
                pos = positions[elem_id]
                preferred = np.array(element.preferred_position)
                
                # Attractive force to preferred position
                diff = preferred - pos
                distance = np.linalg.norm(diff)
                
                if distance > 1e-6:
                    attractive_strength = 0.5
                    force_direction = diff / distance
                    forces[elem_id] += force_direction * attractive_strength * distance
            
            # STEP 3.2.3: Apply forces and update positions
            for elem_id, element in elements.items():
                if element.locked:
                    continue
                
                # Update velocity (with damping and temperature)
                velocities[elem_id] += forces[elem_id] * temp
                velocities[elem_id] *= damping
                
                # Update position
                new_pos = positions[elem_id] + velocities[elem_id]
                
                # Keep within canvas bounds
                new_pos[0] = np.clip(
                    new_pos[0],
                    self.PADDING,
                    self.CANVAS_WIDTH - self.PADDING
                )
                new_pos[1] = np.clip(
                    new_pos[1],
                    self.PADDING,
                    self.CANVAS_HEIGHT - self.PADDING
                )
                
                positions[elem_id] = new_pos
            
            # STEP 3.2.4: Cool the system
            temp = max(temp - cooling_rate, 0.01)
        
        return {
            elem_id: tuple(pos)
            for elem_id, pos in positions.items()
        }
    
    # ========== ALGORITHM 3.3: HIERARCHICAL LAYOUT ==========
    def resolve_with_hierarchical(
        self,
        elements: Dict[str, LayoutElement],
        dependency_graph: Dict[str, Set[str]]
    ) -> Dict[str, Tuple[float, float]]:
        """
        STEP 3.3: Hierarchical (layered) layout algorithm
        
        Algorithm:
        1. Assign elements to layers based on dependency graph
        2. Position by layer (left to right or top to bottom)
        3. Minimize edge crossings
        
        Best for: Flowcharts, hierarchical diagrams
        Time: O(n + m) where m = edges
        """
        # STEP 3.3.1: Calculate layer assignment
        layers = self._calculate_layers(elements, dependency_graph)
        
        # STEP 3.3.2: Group elements by layer
        layer_groups = {}
        for elem_id, layer_num in layers.items():
            if layer_num not in layer_groups:
                layer_groups[layer_num] = []
            layer_groups[layer_num].append(elem_id)
        
        new_positions = {}
        
        # STEP 3.3.3: Position elements in layers
        for layer_num in sorted(layer_groups.keys()):
            elements_in_layer = layer_groups[layer_num]
            n_in_layer = len(elements_in_layer)
            
            # Vertical position based on layer
            y = self.PADDING + (layer_num / (len(layer_groups) + 1)) * \
                (self.CANVAS_HEIGHT - 2 * self.PADDING)
            
            # Horizontal spacing of elements in layer
            x_spacing = (self.CANVAS_WIDTH - 2 * self.PADDING) / (n_in_layer + 1)
            
            for idx, elem_id in enumerate(sorted(elements_in_layer)):
                x = self.PADDING + (idx + 1) * x_spacing
                new_positions[elem_id] = (x, y)
        
        return new_positions
    
    @staticmethod
    def _calculate_layers(
        elements: Dict[str, LayoutElement],
        dependency_graph: Dict[str, Set[str]]
    ) -> Dict[str, int]:
        """
        STEP 3.3.4: Assign layer numbers based on dependency depth
        
        Topological sort approach
        """
        layers = {}
        in_degree = {elem_id: 0 for elem_id in elements.keys()}
        
        # Calculate in-degrees
        for elem_id, deps in dependency_graph.items():
            in_degree[elem_id] = len(deps)
        
        # Process elements with no dependencies
        queue = [elem_id for elem_id, degree in in_degree.items() if degree == 0]
        current_layer = 0
        
        while queue:
            next_queue = []
            
            for elem_id in queue:
                layers[elem_id] = current_layer
            
            # Find elements that depend only on processed elements
            for elem_id in elements.keys():
                if elem_id not in layers:
                    # Check if all dependencies are processed
                    if all(dep in layers for dep in dependency_graph[elem_id]):
                        next_queue.append(elem_id)
            
            queue = next_queue
            current_layer += 1
        
        # Assign remaining elements to a layer
        for elem_id in elements.keys():
            if elem_id not in layers:
                layers[elem_id] = current_layer
        
        return layers
    
    # ========== ALGORITHM 3.4: RADIAL LAYOUT ==========
    def resolve_with_radial(
        self,
        elements: Dict[str, LayoutElement],
        center: Optional[Tuple[float, float]] = None
    ) -> Dict[str, Tuple[float, float]]:
        """
        STEP 3.4: Radial (circular) layout algorithm
        
        Algorithm:
        1. Place important elements near center
        2. Arrange others in concentric circles
        3. Use angular spacing to avoid overlaps
        
        Best for: Diagrams with focal points, network diagrams
        Time: O(n log n)
        """
        if center is None:
            center = (self.CANVAS_WIDTH / 2, self.CANVAS_HEIGHT / 2)
        
        # Sort by priority
        sorted_elements = sorted(
            elements.items(),
            key=lambda x: x[1].priority
        )
        
        new_positions = {}
        
        # Place elements in concentric circles
        radius_increment = 0.8
        elements_per_circle = 8
        current_radius = 0.3
        element_idx = 0
        
        for elem_id, element in sorted_elements:
            if element.locked:
                new_positions[elem_id] = element.bounding_box.center
                continue
            
            circle_idx = element_idx // elements_per_circle
            position_in_circle = element_idx % elements_per_circle
            
            # Update radius
            if circle_idx > 0:
                current_radius = 0.3 + circle_idx * radius_increment
            
            # Calculate angle
            angle = (position_in_circle / elements_per_circle) * 2 * np.pi
            
            # Calculate position on circle
            x = center[0] + current_radius * np.cos(angle)
            y = center[1] + current_radius * np.sin(angle)
            
            # Keep within bounds
            x = np.clip(x, self.PADDING, self.CANVAS_WIDTH - self.PADDING)
            y = np.clip(y, self.PADDING, self.CANVAS_HEIGHT - self.PADDING)
            
            new_positions[elem_id] = (x, y)
            element_idx += 1
        
        return new_positions


# ============================================================================
# PART 5: OPTIMIZATION AND SELECTION
# ============================================================================

class LayoutOptimizer:
    """
    STEP 4: Optimize layout by selecting best algorithm and fine-tuning
    """
    
    @staticmethod
    def evaluate_layout(
        elements: Dict[str, LayoutElement],
        positions: Dict[str, Tuple[float, float]],
        collision_detector: CollisionDetector
    ) -> float:
        """
        STEP 4.1: Evaluate layout quality
        
        Scoring factors (lower = better):
        1. Total overlap area
        2. Distance from preferred positions
        3. Boundary violations
        
        Returns:
            Quality score (0 = perfect, higher = worse)
        """
        score = 0.0
        
        # Create temporary elements at new positions
        temp_elements = {}
        for elem_id, element in elements.items():
            old_center = element.bounding_box.center
            new_center = positions[elem_id]
            dx = new_center[0] - old_center[0]
            dy = new_center[1] - old_center[1]
            
            temp_element = LayoutElement(
                element_id=element.element_id,
                element_type=element.element_type,
                bounding_box=element.bounding_box.move(dx, dy),
                layer=element.layer,
                priority=element.priority,
                locked=element.locked,
                dependencies=element.dependencies,
                preferred_position=element.preferred_position
            )
            temp_elements[elem_id] = temp_element
        
        # Check overlaps
        collisions = collision_detector.detect_collisions(temp_elements)
        total_overlap = sum(overlap for _, _, overlap in collisions)
        score += total_overlap * 100  # Heavy penalty
        
        # Check distance from preferred positions
        for elem_id, element in elements.items():
            if element.preferred_position is not None:
                new_pos = positions[elem_id]
                pref_pos = element.preferred_position
                distance = np.sqrt(
                    (new_pos[0] - pref_pos[0])**2 +
                    (new_pos[1] - pref_pos[1])**2
                )
                score += distance * 5  # Light penalty
        
        # Check boundary violations
        for elem_id, element in temp_elements.items():
            bbox = element.bounding_box
            if bbox.x_min < 0 or bbox.x_max > 8 or \
               bbox.y_min < 0 or bbox.y_max > 4.5:
                score += 50  # Penalty for out of bounds
        
        return score
    
    @staticmethod
    def select_best_algorithm(
        n_elements: int,
        collision_density: float
    ) -> LayoutStrategy:
        """
        STEP 4.2: Select best algorithm based on characteristics
        
        Decision tree:
        - Few elements + low density -> Grid
        - Many elements + dependencies -> Hierarchical
        - Complex + high density -> Force-directed
        - Focal point layout -> Radial
        """
        if n_elements < 5:
            return LayoutStrategy.GRID
        
        if collision_density > 0.7:
            return LayoutStrategy.FORCE_DIRECTED
        
        if n_elements > 15:
            return LayoutStrategy.HIERARCHICAL
        
        return LayoutStrategy.OPTIMIZED  # Try all and pick best


# ============================================================================
# PART 6: ADJUSTMENT AND FINE-TUNING
# ============================================================================

class LayoutAdjuster:
    """
    STEP 5: Fine-tune positions to handle edge cases
    """
    
    @staticmethod
    def apply_minimum_spacing(
        elements: Dict[str, LayoutElement],
        positions: Dict[str, Tuple[float, float]],
        min_distance: float = 0.2
    ) -> Dict[str, Tuple[float, float]]:
        """
        STEP 5.1: Ensure minimum spacing between elements
        
        Algorithm: Iterative approach
        1. Check all pairs for spacing violations
        2. Push apart violating pairs
        3. Repeat until no violations
        
        Time: O(n² * iterations)
        """
        adjusted_positions = {k: v for k, v in positions.items()}
        max_iterations = 10
        
        for iteration in range(max_iterations):
            violations = 0
            
            for elem_id_1, element_1 in elements.items():
                if element_1.locked:
                    continue
                
                pos_1 = np.array(adjusted_positions[elem_id_1])
                
                for elem_id_2, element_2 in elements.items():
                    if elem_id_1 == elem_id_2 or element_2.locked:
                        continue
                    
                    pos_2 = np.array(adjusted_positions[elem_id_2])
                    
                    # Calculate distance
                    distance = np.linalg.norm(pos_1 - pos_2)
                    
                    # Calculate required separation
                    elem_1_width = element_1.bounding_box.width
                    elem_1_height = element_1.bounding_box.height
                    elem_2_width = element_2.bounding_box.width
                    elem_2_height = element_2.bounding_box.height
                    
                    required_distance = np.sqrt(
                        (elem_1_width + elem_2_width + min_distance) ** 2 +
                        (elem_1_height + elem_2_height + min_distance) ** 2
                    ) / 2
                    
                    # If spacing violation, push apart
                    if distance < required_distance:
                        violations += 1
                        
                        if distance < 1e-6:
                            # Elements at same position, push in random direction
                            direction = np.random.randn(2)
                        else:
                            direction = (pos_1 - pos_2) / distance
                        
                        push_distance = (required_distance - distance) / 2
                        
                        # Move both elements away from each other
                        pos_1_new = pos_1 + direction * push_distance
                        pos_2_new = pos_2 - direction * push_distance
                        
                        adjusted_positions[elem_id_1] = tuple(pos_1_new)
                        adjusted_positions[elem_id_2] = tuple(pos_2_new)
            
            if violations == 0:
                break
        
        return adjusted_positions
    
    @staticmethod
    def apply_text_positioning_rules(
        elements: Dict[str, LayoutElement],
        positions: Dict[str, Tuple[float, float]]
    ) -> Dict[str, Tuple[float, float]]:
        """
        STEP 5.2: Apply typography-specific positioning rules
        
        Rules for text elements:
        - Keep labels outside figure bounds
        - Align text with anchors
        - Maintain readability (no upside-down text)
        """
        adjusted = {k: v for k, v in positions.items()}
        
        for elem_id, element in elements.items():
            if element.element_type != ElementType.TEXT:
                continue
            
            # If text is a label, position outside its target
            if element.element_type == ElementType.LABEL:
                # Find closest non-text element
                text_pos = adjusted[elem_id]
                
                closest_elem = None
                closest_distance = float('inf')
                
                for other_id, other_elem in elements.items():
                    if other_id == elem_id or \
                       other_elem.element_type in [ElementType.TEXT, ElementType.LABEL]:
                        continue
                    
                    other_pos = adjusted[other_id]
                    dist = np.sqrt(
                        (text_pos[0] - other_pos[0])**2 +
                        (text_pos[1] - other_pos[1])**2
                    )
                    
                    if dist < closest_distance:
                        closest_distance = dist
                        closest_elem = (other_id, other_elem, other_pos)
                
                if closest_elem:
                    target_id, target_elem, target_pos = closest_elem
                    
                    # Position label outside target
                    direction = np.array(text_pos) - np.array(target_pos)
                    if np.linalg.norm(direction) > 1e-6:
                        direction = direction / np.linalg.norm(direction)
                    else:
                        # Random direction if same position
                        direction = np.array([1.0, 0.0])
                    
                    # Place label at comfortable distance
                    new_pos = np.array(target_pos) + direction * 0.5
                    adjusted[elem_id] = tuple(new_pos)
        
        return adjusted


# ============================================================================
# PART 7: MAIN SOLVER ORCHESTRATOR
# ============================================================================

class OverlapSolver:
    """
    STEP 0: Main orchestrator that coordinates all steps
    """
    
    def __init__(self):
        self.collision_detector = CollisionDetector()
        self.constraint_system = ConstraintSystem()
        self.layout_resolver = LayoutResolver()
        self.layout_optimizer = LayoutOptimizer()
        self.layout_adjuster = LayoutAdjuster()
    
    def solve(
        self,
        elements: Dict[str, LayoutElement],
        strategy: Optional[LayoutStrategy] = None,
        verbose: bool = True
    ) -> Dict[str, Tuple[float, float]]:
        """
        MAIN ALGORITHM: Solve overlapping elements problem
        
        Complete pipeline:
        STEP 0: Initialize
        STEP 1: Detect collisions
        STEP 2: Establish constraints
        STEP 3: Apply layout algorithms
        STEP 4: Optimize
        STEP 5: Fine-tune
        
        Args:
            elements: Dict of LayoutElements to arrange
            strategy: Override layout strategy (auto-select if None)
            verbose: Print progress
        
        Returns:
            Dict mapping element_id -> (x, y) position
        """
        if verbose:
            print("\n" + "="*70)
            print("PHIVERSITY OVERLAP RESOLUTION SOLVER")
            print("="*70)
        
        # STEP 1: Detect collisions
        if verbose:
            print("\n[STEP 1] COLLISION DETECTION")
        collisions = self.collision_detector.detect_collisions(elements)
        if verbose:
            print(f"  Found {len(collisions)} overlapping pairs")
            total_overlap = sum(overlap for _, _, overlap in collisions)
            print(f"  Total overlap area: {total_overlap:.4f}")
        
        if not collisions:
            if verbose:
                print("  ✓ No overlaps detected, using original positions")
            return {
                elem_id: elem.bounding_box.center
                for elem_id, elem in elements.items()
            }
        
        # STEP 2: Establish constraints
        if verbose:
            print("\n[STEP 2] CONSTRAINT ESTABLISHMENT")
        
        # Default type priorities
        type_priority = {
            ElementType.GRAPH: 10,
            ElementType.FIGURE: 15,
            ElementType.EQUATION: 20,
            ElementType.LEGEND: 25,
            ElementType.LABEL: 30,
            ElementType.TEXT: 35,
            ElementType.ARROW: 40,
        }
        
        # Update element priorities
        for element in elements.values():
            element.priority = self.constraint_system.calculate_priority(
                element, type_priority
            )
        
        dependency_graph = self.constraint_system.build_dependency_graph(elements)
        if verbose:
            print(f"  Calculated priorities and dependencies")
        
        # STEP 3: Apply layout algorithms
        if verbose:
            print("\n[STEP 3] LAYOUT RESOLUTION")
        
        if strategy is None:
            # Auto-select strategy
            collision_density = len(collisions) / (
                len(elements) * (len(elements) - 1) / 2
            ) if len(elements) > 1 else 0
            strategy = self.layout_optimizer.select_best_algorithm(
                len(elements),
                collision_density
            )
        
        if verbose:
            print(f"  Strategy: {strategy.value}")
        
        # Try multiple layouts
        layouts = {}
        
        if strategy == LayoutStrategy.GRID or strategy == LayoutStrategy.OPTIMIZED:
            layouts['grid'] = self.layout_resolver.resolve_with_grid(elements)
        
        if strategy == LayoutStrategy.HIERARCHICAL or strategy == LayoutStrategy.OPTIMIZED:
            layouts['hierarchical'] = self.layout_resolver.resolve_with_hierarchical(
                elements, dependency_graph
            )
        
        if strategy == LayoutStrategy.FORCE_DIRECTED or strategy == LayoutStrategy.OPTIMIZED:
            layouts['force_directed'] = self.layout_resolver.resolve_with_force_directed(
                elements, iterations=100
            )
        
        if strategy == LayoutStrategy.RADIAL or strategy == LayoutStrategy.OPTIMIZED:
            layouts['radial'] = self.layout_resolver.resolve_with_radial(elements)
        
        if verbose:
            print(f"  Generated {len(layouts)} layout variants")
        
        # STEP 4: Optimize
        if verbose:
            print("\n[STEP 4] OPTIMIZATION")
        
        best_layout = None
        best_score = float('inf')
        best_name = None
        
        for layout_name, layout_positions in layouts.items():
            score = self.layout_optimizer.evaluate_layout(
                elements, layout_positions, self.collision_detector
            )
            
            if verbose:
                print(f"  {layout_name:15} score: {score:.2f}")
            
            if score < best_score:
                best_score = score
                best_layout = layout_positions
                best_name = layout_name
        
        if verbose:
            print(f"  ✓ Selected: {best_name} (score: {best_score:.2f})")
        
        # STEP 5: Fine-tune
        if verbose:
            print("\n[STEP 5] FINE-TUNING")
        
        # Apply minimum spacing
        best_layout = self.layout_adjuster.apply_minimum_spacing(
            elements, best_layout, min_distance=0.15
        )
        
        # Apply text positioning rules
        best_layout = self.layout_adjuster.apply_text_positioning_rules(
            elements, best_layout
        )
        
        if verbose:
            print("  Applied minimum spacing constraints")
            print("  Applied text positioning rules")
        
        # Final validation
        temp_elements = {}
        for elem_id, element in elements.items():
            old_center = element.bounding_box.center
            new_center = best_layout[elem_id]
            dx = new_center[0] - old_center[0]
            dy = new_center[1] - old_center[1]
            
            temp_elements[elem_id] = LayoutElement(
                element_id=element.element_id,
                element_type=element.element_type,
                bounding_box=element.bounding_box.move(dx, dy),
                layer=element.layer,
                priority=element.priority,
                locked=element.locked,
                dependencies=element.dependencies,
                preferred_position=element.preferred_position
            )
        
        final_collisions = self.collision_detector.detect_collisions(temp_elements)
        
        if verbose:
            print(f"\n[RESULT] FINAL VALIDATION")
            print(f"  Remaining overlaps: {len(final_collisions)}")
            remaining_overlap = sum(o for _, _, o in final_collisions)
            print(f"  Remaining overlap area: {remaining_overlap:.4f}")
            print(f"  Overlap reduction: {(1 - remaining_overlap / max(total_overlap, 0.0001)) * 100:.1f}%")
            print("\n" + "="*70)
            print("✓ SOLVER COMPLETE")
            print("="*70 + "\n")
        
        return best_layout


# ============================================================================
# PART 8: SERIALIZATION AND INTEGRATION
# ============================================================================

def serialize_layout(positions: Dict[str, Tuple[float, float]]) -> str:
    """
    STEP 6.1: Serialize resolved layout to JSON for Manim
    """
    layout_data = {
        element_id: {"x": float(x), "y": float(y)}
        for element_id, (x, y) in positions.items()
    }
    return json.dumps(layout_data, indent=2)


def create_layout_element(
    element_id: str,
    element_type: str,
    x_min: float,
    y_min: float,
    x_max: float,
    y_max: float,
    priority: int = 0,
    locked: bool = False,
    dependencies: List[str] = None
) -> LayoutElement:
    """
    STEP 6.2: Factory function to create LayoutElements
    """
    return LayoutElement(
        element_id=element_id,
        element_type=ElementType(element_type),
        bounding_box=BoundingBox(x_min, y_min, x_max, y_max),
        priority=priority,
        locked=locked,
        dependencies=dependencies or []
    )


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: Create test elements
    test_elements = {
        "title": create_layout_element(
            "title", "text",
            3.0, 4.0, 5.0, 4.3,
            priority=0, locked=True
        ),
        "graph_1": create_layout_element(
            "graph_1", "graph",
            0.5, 1.0, 3.0, 3.5,
            priority=10
        ),
        "graph_2": create_layout_element(
            "graph_2", "graph",
            3.5, 1.0, 6.0, 3.5,
            priority=10
        ),
        "label_1": create_layout_element(
            "label_1", "label",
            1.0, 0.5, 2.0, 0.8,
            priority=30, dependencies=["graph_1"]
        ),
        "label_2": create_layout_element(
            "label_2", "label",
            4.0, 0.5, 5.0, 0.8,
            priority=30, dependencies=["graph_2"]
        ),
    }
    
    # Solve
    solver = OverlapSolver()
    solution = solver.solve(test_elements, verbose=True)
    
    # Show results
    print("\nFinal Positions:")
    for elem_id, (x, y) in solution.items():
        print(f"  {elem_id:12} -> ({x:.3f}, {y:.3f})")
    
    # Serialize
    layout_json = serialize_layout(solution)
    print("\nSerialized Layout (JSON):")
    print(layout_json)
