"""
Layer Management Module for Phiversity

Manages z-ordering, depth structure, and layering of content elements
to ensure proper visual hierarchy and prevent inappropriate overlaps.

Features:
- Automatic z-index assignment by element type and priority
- Layer tier system (background, content, text, ui)
- Transparency and opacity management
- Depth conflict detection and resolution
- Layer transition effects
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from abc import ABC, abstractmethod


class LayerTier(Enum):
    """Predefined layer tiers with z-index ranges."""
    
    # Background visuals (behind everything)
    BACKGROUND = (0, 10, "Background visuals and textures")
    
    # Content layer (main content)
    CONTENT = (11, 50, "Primary content (graphs, diagrams, figures)")
    
    # Text/narration overlays
    TEXT = (51, 100, "Text overlays and captions")
    
    # UI/annotations (topmost)
    UI = (101, 200, "UI elements and annotations")
    
    def __init__(self, min_z: int, max_z: int, description: str):
        self.min_z = min_z
        self.max_z = max_z
        self.description = description


class ElementType(Enum):
    """Types of elements with preferred layers."""
    
    # Background
    BACKGROUND_IMAGE = "bg_image"
    TEXTURE = "texture"
    
    # Content
    GRAPH = "graph"
    DIAGRAM = "diagram"
    FIGURE = "figure"
    CODE_BLOCK = "code"
    TABLE = "table"
    
    # Text
    TEXT = "text"
    EQUATION = "equation"
    LABEL = "label"
    CAPTION = "caption"
    
    # UI
    BUTTON = "button"
    SLIDER = "slider"
    ANNOTATION = "annotation"
    ARROW = "arrow"
    HIGHLIGHT = "highlight"


@dataclass
class LayerAssignment:
    """Assignment of an element to a layer with properties."""
    
    element_id: str
    element_type: ElementType
    z_index: int
    layer_tier: LayerTier
    opacity: float = 1.0          # 0.0 (transparent) to 1.0 (opaque)
    blend_mode: str = "normal"    # "normal", "multiply", "screen", "overlay"
    priority: int = 0             # Higher = more important (for conflicts)
    timestamp_start: float = 0.0  # When layer becomes visible
    timestamp_end: float = float('inf')  # When layer becomes hidden
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LayerConflict:
    """Information about a z-index conflict."""
    element_id_1: str
    element_id_2: str
    z_index_1: int
    z_index_2: int
    conflict_reason: str
    suggested_z_indices: Tuple[int, int]  # Suggested (z1, z2) after resolution


class LayerManager:
    """
    Manages element layering and z-ordering.
    Ensures proper visual hierarchy and prevents inappropriate overlaps.
    """
    
    # Element type to layer tier mapping
    TYPE_TO_TIER: Dict[ElementType, LayerTier] = {
        # Background
        ElementType.BACKGROUND_IMAGE: LayerTier.BACKGROUND,
        ElementType.TEXTURE: LayerTier.BACKGROUND,
        
        # Content
        ElementType.GRAPH: LayerTier.CONTENT,
        ElementType.DIAGRAM: LayerTier.CONTENT,
        ElementType.FIGURE: LayerTier.CONTENT,
        ElementType.CODE_BLOCK: LayerTier.CONTENT,
        ElementType.TABLE: LayerTier.CONTENT,
        
        # Text
        ElementType.TEXT: LayerTier.TEXT,
        ElementType.EQUATION: LayerTier.TEXT,
        ElementType.LABEL: LayerTier.TEXT,
        ElementType.CAPTION: LayerTier.TEXT,
        
        # UI
        ElementType.BUTTON: LayerTier.UI,
        ElementType.SLIDER: LayerTier.UI,
        ElementType.ANNOTATION: LayerTier.UI,
        ElementType.ARROW: LayerTier.UI,
        ElementType.HIGHLIGHT: LayerTier.UI,
    }
    
    # Priority adjustments for element types (within their tier)
    PRIORITY_ADJUSTMENTS: Dict[ElementType, int] = {
        ElementType.TEXT: 5,         # Text higher priority within TEXT tier
        ElementType.LABEL: 4,
        ElementType.CAPTION: 3,
        ElementType.EQUATION: 2,
        
        ElementType.GRAPH: 8,        # Graphs higher priority within CONTENT tier
        ElementType.TABLE: 7,
        ElementType.DIAGRAM: 6,
        ElementType.FIGURE: 5,
        ElementType.CODE_BLOCK: 4,
        
        ElementType.ANNOTATION: 10,  # Annotations very high in UI tier
        ElementType.HIGHLIGHT: 9,
        ElementType.ARROW: 8,
    }
    
    # Default opacity by layer
    DEFAULT_OPACITY: Dict[LayerTier, float] = {
        LayerTier.BACKGROUND: 0.7,
        LayerTier.CONTENT: 1.0,
        LayerTier.TEXT: 1.0,
        LayerTier.UI: 0.95,
    }
    
    def __init__(self):
        """Initialize layer manager."""
        self.assignments: Dict[str, LayerAssignment] = {}
        self.next_z_index: int = 0
        self.conflicts: List[LayerConflict] = []
        self.history: List[Dict[str, Any]] = []
    
    def assign_layer(self,
                    element_id: str,
                    element_type: ElementType,
                    priority: int = 0,
                    custom_z_index: Optional[int] = None,
                    opacity: Optional[float] = None) -> LayerAssignment:
        """
        Assign an element to a layer.
        
        Args:
            element_id: Unique element identifier
            element_type: Type of element
            priority: Priority within the layer (0-10)
            custom_z_index: Override automatic z-index assignment
            opacity: Override default opacity for tier
        
        Returns:
            LayerAssignment with assigned z-index and properties
        """
        # Determine tier
        tier = self.TYPE_TO_TIER.get(element_type, LayerTier.CONTENT)
        
        # Calculate z-index
        if custom_z_index is not None:
            z_index = custom_z_index
        else:
            # Combine tier, priority, and type-specific adjustment
            base_z = tier.min_z
            type_priority = self.PRIORITY_ADJUSTMENTS.get(element_type, 0)
            z_index = base_z + type_priority + priority
            
            # Clamp to tier range
            z_index = max(tier.min_z, min(tier.max_z, z_index))
        
        # Determine opacity
        if opacity is None:
            opacity = self.DEFAULT_OPACITY.get(tier, 1.0)
        
        # Create assignment
        assignment = LayerAssignment(
            element_id=element_id,
            element_type=element_type,
            z_index=z_index,
            layer_tier=tier,
            opacity=opacity,
            priority=priority
        )
        
        # Store assignment
        self.assignments[element_id] = assignment
        self.next_z_index = max(self.next_z_index, z_index + 1)
        
        return assignment
    
    def assign_layers_batch(self,
                           elements: List[Tuple[str, ElementType, int]]) -> Dict[str, LayerAssignment]:
        """
        Assign layers to multiple elements at once.
        
        Args:
            elements: List of (element_id, element_type, priority)
        
        Returns:
            Dict of element_id -> LayerAssignment
        """
        assignments = {}
        for element_id, element_type, priority in elements:
            assignments[element_id] = self.assign_layer(element_id, element_type, priority)
        
        return assignments
    
    def get_assignment(self, element_id: str) -> Optional[LayerAssignment]:
        """Get layer assignment for an element."""
        return self.assignments.get(element_id)
    
    def get_z_index(self, element_id: str) -> Optional[int]:
        """Get z-index for an element."""
        assignment = self.get_assignment(element_id)
        return assignment.z_index if assignment else None
    
    def update_z_index(self,
                      element_id: str,
                      new_z_index: int) -> bool:
        """
        Manually update z-index for an element.
        
        Args:
            element_id: Element to update
            new_z_index: New z-index value
        
        Returns:
            True if successful, False if element not found
        """
        if element_id not in self.assignments:
            return False
        
        self.assignments[element_id].z_index = new_z_index
        return True
    
    def update_opacity(self,
                      element_id: str,
                      opacity: float) -> bool:
        """
        Update opacity for an element.
        
        Args:
            element_id: Element to update
            opacity: New opacity (0.0-1.0)
        
        Returns:
            True if successful
        """
        if element_id not in self.assignments:
            return False
        
        self.assignments[element_id].opacity = max(0.0, min(1.0, opacity))
        return True
    
    def set_visibility_window(self,
                             element_id: str,
                             timestamp_start: float,
                             timestamp_end: float) -> bool:
        """
        Set when an element should be visible.
        
        Args:
            element_id: Element to update
            timestamp_start: Start time (seconds)
            timestamp_end: End time (seconds)
        
        Returns:
            True if successful
        """
        if element_id not in self.assignments:
            return False
        
        self.assignments[element_id].timestamp_start = timestamp_start
        self.assignments[element_id].timestamp_end = timestamp_end
        return True
    
    def detect_conflicts(self) -> List[LayerConflict]:
        """
        Detect z-index conflicts (overlapping same z-index).
        
        Returns:
            List of LayerConflict
        """
        self.conflicts = []
        
        # Group assignments by z-index
        z_index_map: Dict[int, List[LayerAssignment]] = {}
        for assignment in self.assignments.values():
            z = assignment.z_index
            if z not in z_index_map:
                z_index_map[z] = []
            z_index_map[z].append(assignment)
        
        # Check for conflicts (multiple elements at same z-index in same tier)
        for z_index, assignments in z_index_map.items():
            if len(assignments) > 1:
                # Check if they're in same tier
                tiers = [a.layer_tier for a in assignments]
                if len(set(tiers)) == 1:
                    # Same tier - conflict!
                    for i, a1 in enumerate(assignments):
                        for a2 in assignments[i+1:]:
                            conflict = LayerConflict(
                                element_id_1=a1.element_id,
                                element_id_2=a2.element_id,
                                z_index_1=a1.z_index,
                                z_index_2=a2.z_index,
                                conflict_reason=f"Both at z={z_index} in {tiers[0].name} tier",
                                suggested_z_indices=(z_index, z_index + 1)
                            )
                            self.conflicts.append(conflict)
        
        return self.conflicts
    
    def resolve_conflicts(self) -> Dict[str, int]:
        """
        Attempt to resolve detected conflicts.
        
        Returns:
            Dict of element_id -> new_z_index for elements that were reassigned
        """
        reassignments = {}
        
        self.detect_conflicts()
        
        for conflict in self.conflicts:
            # Get current assignments
            a1 = self.assignments[conflict.element_id_1]
            a2 = self.assignments[conflict.element_id_2]
            
            # Separate by priority
            if a1.priority > a2.priority:
                # Keep a1, move a2 down
                new_z = a1.z_index - 1
                self.assignments[conflict.element_id_2].z_index = new_z
                reassignments[conflict.element_id_2] = new_z
            else:
                # Keep a2, move a1 down
                new_z = a2.z_index - 1
                self.assignments[conflict.element_id_1].z_index = new_z
                reassignments[conflict.element_id_1] = new_z
        
        return reassignments
    
    def get_render_order(self, timestamp: Optional[float] = None) -> List[str]:
        """
        Get element render order (front to back).
        
        Args:
            timestamp: If provided, only include visible elements at this time
        
        Returns:
            List of element_ids ordered by z-index (back to front)
        """
        visible_assignments = []
        
        for assignment in self.assignments.values():
            if timestamp is not None:
                # Check visibility window
                if not (assignment.timestamp_start <= timestamp <= assignment.timestamp_end):
                    continue
            
            visible_assignments.append(assignment)
        
        # Sort by z-index (ascending = back to front)
        sorted_assignments = sorted(visible_assignments, key=lambda a: a.z_index)
        
        return [a.element_id for a in sorted_assignments]
    
    def get_layer_summary(self) -> Dict[LayerTier, List[str]]:
        """
        Get elements grouped by layer tier.
        
        Returns:
            Dict of LayerTier -> list of element_ids
        """
        summary = {tier: [] for tier in LayerTier}
        
        for element_id, assignment in self.assignments.items():
            summary[assignment.layer_tier].append(element_id)
        
        return summary
    
    def export_layer_config(self) -> Dict[str, Any]:
        """
        Export layer configuration as JSON-serializable dict.
        
        Returns:
            Dict with all layer assignments and properties
        """
        config = {
            "assignments": {},
            "tiers": {
                tier.name: {
                    "min_z": tier.min_z,
                    "max_z": tier.max_z,
                    "description": tier.description
                }
                for tier in LayerTier
            }
        }
        
        for element_id, assignment in self.assignments.items():
            config["assignments"][element_id] = {
                "element_type": assignment.element_type.value,
                "z_index": assignment.z_index,
                "layer_tier": assignment.layer_tier.name,
                "opacity": assignment.opacity,
                "blend_mode": assignment.blend_mode,
                "priority": assignment.priority,
                "timestamp_start": assignment.timestamp_start,
                "timestamp_end": assignment.timestamp_end,
            }
        
        return config
    
    def clear(self):
        """Clear all assignments."""
        self.assignments = {}
        self.next_z_index = 0
        self.conflicts = []
        self.history = []


class LayerTransitionEffect:
    """Manages fade-in/fade-out transitions between layers."""
    
    def __init__(self, duration: float = 0.5):
        """
        Initialize transition effect.
        
        Args:
            duration: Transition duration in seconds
        """
        self.duration = duration
    
    def calculate_opacity(self,
                         current_time: float,
                         start_time: float,
                         end_time: float) -> float:
        """
        Calculate opacity at a given time with fade-in/fade-out.
        
        Args:
            current_time: Current timestamp
            start_time: Time when element appears
            end_time: Time when element disappears
        
        Returns:
            Opacity value (0.0 to 1.0)
        """
        # Fade in phase
        if current_time < start_time:
            return 0.0
        elif current_time < start_time + self.duration:
            fade_in = (current_time - start_time) / self.duration
            return min(1.0, fade_in)
        
        # Fade out phase
        elif current_time > end_time:
            return 0.0
        elif current_time > end_time - self.duration:
            fade_out = (end_time - current_time) / self.duration
            return min(1.0, fade_out)
        
        # Steady state
        else:
            return 1.0


def recommend_layer_tier(element_type: ElementType) -> LayerTier:
    """
    Recommend layer tier for an element type.
    
    Args:
        element_type: Type of element
    
    Returns:
        Recommended LayerTier
    """
    return LayerManager.TYPE_TO_TIER.get(element_type, LayerTier.CONTENT)


if __name__ == "__main__":
    # Example usage
    manager = LayerManager()
    
    # Assign layers to elements
    elements = [
        ("bg1", ElementType.BACKGROUND_IMAGE, 0),
        ("graph1", ElementType.GRAPH, 2),
        ("text1", ElementType.TEXT, 1),
        ("label1", ElementType.LABEL, 3),
    ]
    
    assignments = manager.assign_layers_batch(elements)
    
    # Print assignments
    for element_id, assignment in assignments.items():
        print(f"{element_id}: z={assignment.z_index} ({assignment.layer_tier.name})")
    
    # Get render order (back to front)
    print("\nRender order (back to front):")
    for element_id in manager.get_render_order():
        print(f"  {element_id}")
    
    # Check for conflicts
    conflicts = manager.detect_conflicts()
    print(f"\nConflicts detected: {len(conflicts)}")
