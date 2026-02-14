"""
Dynamic Layout Engine for Phiversity

Manages automatic positioning, sizing, and spacing of text, figures, and graphs
to prevent overlaps and ensure optimal readability in educational videos.

Core Components:
- LayoutZone: Predefined screen regions (safe areas)
- ContentBox: Bounded content (text, figure, graph)
- LayoutEngine: Positions and sizes content dynamically
- LayoutStrategy: Different layout modes (side-by-side, stacked, floating)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple, Optional, Any
import math


class LayoutStrategy(Enum):
    """Layout positioning strategies."""
    SIDE_BY_SIDE = "side_by_side"        # Text left, figure right (or vice versa)
    STACKED = "stacked"                    # Text top, figure bottom (or vice versa)
    FLOATING = "floating"                  # Floating text boxes with collision detection
    GRID = "grid"                          # Multi-column grid layout
    CENTERED = "centered"                  # Centered content with margins
    CUSTOM = "custom"                      # User-specified positions


class TextAnchor(Enum):
    """Text anchor points for positioning."""
    TOP_LEFT = (0, 1)
    TOP_CENTER = (0.5, 1)
    TOP_RIGHT = (1, 1)
    CENTER_LEFT = (0, 0.5)
    CENTER = (0.5, 0.5)
    CENTER_RIGHT = (1, 0.5)
    BOTTOM_LEFT = (0, 0)
    BOTTOM_CENTER = (0.5, 0)
    BOTTOM_RIGHT = (1, 0)


@dataclass
class ScreenBounds:
    """Screen dimensions and safe area constraints."""
    width: float          # Screen width in pixels or Manim units
    height: float         # Screen height in pixels or Manim units
    margin: float = 0.5   # Margin from edges (percentage of dimension)
    
    # Safe area where content should fit
    left: float = field(init=False)
    right: float = field(init=False)
    top: float = field(init=False)
    bottom: float = field(init=False)
    
    def __post_init__(self):
        """Calculate safe area bounds."""
        margin_x = self.width * self.margin / 100
        margin_y = self.height * self.margin / 100
        
        self.left = -self.width / 2 + margin_x
        self.right = self.width / 2 - margin_x
        self.top = self.height / 2 - margin_y
        self.bottom = -self.height / 2 + margin_y
    
    def get_safe_width(self) -> float:
        """Get usable width within safe area."""
        return self.right - self.left
    
    def get_safe_height(self) -> float:
        """Get usable height within safe area."""
        return self.top - self.bottom


@dataclass
class ContentBox:
    """Represents a piece of content (text, figure, graph)."""
    id: str                          # Unique identifier
    type: str                        # "text", "figure", "graph", "code"
    content: str                     # Content data (text or reference)
    width: Optional[float] = None    # Content width (None = auto)
    height: Optional[float] = None   # Content height (None = auto)
    position: Tuple[float, float] = field(default=(0, 0))  # (x, y) center position
    anchor: TextAnchor = TextAnchor.CENTER
    layer: int = 0                   # Z-order (higher = on top)
    timestamp_start: float = 0.0     # When to appear (seconds)
    timestamp_end: float = float('inf')  # When to disappear
    font_size: int = 24
    color: str = "#FFFFFF"
    background_color: Optional[str] = None
    opacity: float = 1.0
    padding: float = 0.2             # Padding around content
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get bounding box as (left, right, top, bottom)."""
        if self.width is None or self.height is None:
            return (self.position[0], self.position[0], self.position[1], self.position[1])
        
        # Calculate position based on anchor
        anchor_x, anchor_y = self.anchor.value
        left = self.position[0] - self.width * anchor_x
        right = left + self.width
        top = self.position[1] + self.height * (1 - anchor_y)
        bottom = top - self.height
        
        return (left, right, top, bottom)
    
    def set_bounds(self, left: float, right: float, top: float, bottom: float):
        """Set position and size from bounds."""
        self.width = right - left
        self.height = top - bottom
        self.position = ((left + right) / 2, (top + bottom) / 2)
    
    def intersects(self, other: 'ContentBox') -> bool:
        """Check if this box intersects with another."""
        left1, right1, top1, bottom1 = self.get_bounds()
        left2, right2, top2, bottom2 = other.get_bounds()
        
        # Add padding to create buffer zones
        left1 -= self.padding
        right1 += self.padding
        top1 += self.padding
        bottom1 -= self.padding
        
        left2 -= other.padding
        right2 += other.padding
        top2 += other.padding
        bottom2 -= other.padding
        
        return not (right1 < left2 or right2 < left1 or bottom1 > top2 or bottom2 > top1)
    
    def center_of_box(self) -> Tuple[float, float]:
        """Get center position of bounding box."""
        return self.position  # Already stored as center


@dataclass
class LayoutZone:
    """A predefined region for placing content."""
    name: str                    # Zone identifier
    bounds: Tuple[float, float, float, float]  # (left, right, top, bottom)
    priority: int = 0            # Higher = preferred for placement
    max_occupancy: float = 1.0   # Max % of zone that can be filled
    
    def get_center(self) -> Tuple[float, float]:
        """Get center of this zone."""
        left, right, top, bottom = self.bounds
        return ((left + right) / 2, (top + bottom) / 2)
    
    def get_width(self) -> float:
        """Get width of zone."""
        return self.bounds[1] - self.bounds[0]
    
    def get_height(self) -> float:
        """Get height of zone."""
        return self.bounds[2] - self.bounds[3]


class LayoutEngine:
    """
    Dynamic layout engine for positioning content on screen.
    
    Handles:
    - Automatic positioning based on strategy
    - Collision detection and resolution
    - Adaptive sizing based on available space
    - Layer management
    - Temporal synchronization
    """
    
    def __init__(self, screen_bounds: ScreenBounds, strategy: LayoutStrategy = LayoutStrategy.FLOATING):
        """
        Initialize layout engine.
        
        Args:
            screen_bounds: Screen dimensions and safe area
            strategy: Layout positioning strategy
        """
        self.screen_bounds = screen_bounds
        self.strategy = strategy
        self.content_boxes: List[ContentBox] = []
        self.zones: Dict[str, LayoutZone] = self._create_default_zones()
        self.history: List[Dict[str, Any]] = []  # For debugging and metrics
    
    def _create_default_zones(self) -> Dict[str, LayoutZone]:
        """Create predefined layout zones for common arrangements."""
        width = self.screen_bounds.get_safe_width()
        height = self.screen_bounds.get_safe_height()
        
        left_edge = self.screen_bounds.left
        right_edge = self.screen_bounds.right
        top_edge = self.screen_bounds.top
        bottom_edge = self.screen_bounds.bottom
        
        return {
            "left": LayoutZone("left", (left_edge, left_edge + width * 0.45, top_edge, bottom_edge), priority=10),
            "right": LayoutZone("right", (right_edge - width * 0.45, right_edge, top_edge, bottom_edge), priority=10),
            "center": LayoutZone("center", (left_edge + width * 0.25, right_edge - width * 0.25, top_edge, bottom_edge), priority=5),
            "top": LayoutZone("top", (left_edge, right_edge, top_edge, top_edge - height * 0.4), priority=8),
            "bottom": LayoutZone("bottom", (left_edge, right_edge, bottom_edge + height * 0.4, bottom_edge), priority=8),
            "full": LayoutZone("full", (left_edge, right_edge, top_edge, bottom_edge), priority=0),
        }
    
    def add_content(self, box: ContentBox):
        """Add content box to layout."""
        self.content_boxes.append(box)
    
    def add_contents(self, boxes: List[ContentBox]):
        """Add multiple content boxes."""
        for box in boxes:
            self.add_content(box)
    
    def clear(self):
        """Clear all content."""
        self.content_boxes = []
        self.history = []
    
    def layout(self) -> List[ContentBox]:
        """
        Execute layout algorithm based on strategy.
        Returns positioned and sized content boxes.
        """
        if not self.content_boxes:
            return []
        
        if self.strategy == LayoutStrategy.SIDE_BY_SIDE:
            return self._layout_side_by_side()
        elif self.strategy == LayoutStrategy.STACKED:
            return self._layout_stacked()
        elif self.strategy == LayoutStrategy.FLOATING:
            return self._layout_floating()
        elif self.strategy == LayoutStrategy.GRID:
            return self._layout_grid()
        elif self.strategy == LayoutStrategy.CENTERED:
            return self._layout_centered()
        elif self.strategy == LayoutStrategy.CUSTOM:
            return self._validate_custom_layout()
        else:
            return self._layout_floating()  # Default fallback
    
    def _layout_side_by_side(self) -> List[ContentBox]:
        """Position content left and right."""
        # Separate by type: text usually goes left, figures right
        text_items = [b for b in self.content_boxes if b.type == "text"]
        figure_items = [b for b in self.content_boxes if b.type in ["figure", "graph", "code"]]
        other_items = [b for b in self.content_boxes if b.type not in ["text", "figure", "graph", "code"]]
        
        positioned = []
        
        # Position text on left
        left_zone = self.zones["left"]
        for i, item in enumerate(text_items):
            y_offset = left_zone.bounds[2] - (i + 0.5) * (left_zone.get_height() / len(text_items))
            item.position = (left_zone.get_center()[0], y_offset)
            item.width = left_zone.get_width() * 0.9
            self._constrain_height(item)
            self._constrain_position(item)
            positioned.append(item)
        
        # Position figures on right
        right_zone = self.zones["right"]
        for i, item in enumerate(figure_items):
            y_offset = right_zone.bounds[2] - (i + 0.5) * (right_zone.get_height() / len(figure_items))
            item.position = (right_zone.get_center()[0], y_offset)
            item.width = right_zone.get_width() * 0.9
            self._constrain_height(item)
            self._constrain_position(item)
            positioned.append(item)
        
        # Position other items in center
        center_zone = self.zones["center"]
        for i, item in enumerate(other_items):
            y_offset = center_zone.bounds[2] - (i + 0.5) * (center_zone.get_height() / len(other_items))
            item.position = (center_zone.get_center()[0], y_offset)
            item.width = center_zone.get_width() * 0.9
            self._constrain_height(item)
            self._constrain_position(item)
            positioned.append(item)
        
        # Resolve any remaining collisions
        self._resolve_collisions(positioned)
        
        return positioned
    
    def _layout_stacked(self) -> List[ContentBox]:
        """Position content vertically (top to bottom)."""
        positioned = []
        current_y = self.screen_bounds.top
        
        for item in self.content_boxes:
            item.width = self.screen_bounds.get_safe_width() * 0.9
            self._constrain_height(item)
            
            # Place item, ensuring it doesn't exceed screen bounds
            item_height = item.height or 1.0
            if current_y - item_height < self.screen_bounds.bottom:
                # Not enough vertical space, scale down or skip
                item.height = max(0.5, current_y - self.screen_bounds.bottom - 0.2)
            
            item.position = (self.screen_bounds.left + self.screen_bounds.get_safe_width() / 2, 
                           current_y - item_height / 2)
            current_y -= item_height + 0.3  # Add spacing
            
            self._constrain_position(item)
            positioned.append(item)
        
        return positioned
    
    def _layout_floating(self) -> List[ContentBox]:
        """
        Floating layout with collision detection.
        Positions items freely and resolves overlaps.
        """
        positioned = []
        
        # Start with content items in their preferred or default positions
        for item in self.content_boxes:
            if item.width is None:
                item.width = 2.0  # Default width in Manim units
            if item.height is None:
                item.height = 1.0
            
            # Use zone-based initial positioning
            if item.type == "text":
                zone = self.zones.get("left", self.zones["center"])
            elif item.type in ["figure", "graph"]:
                zone = self.zones.get("right", self.zones["center"])
            else:
                zone = self.zones["center"]
            
            # Place at zone center if position not explicitly set
            if item.position == (0, 0):
                item.position = zone.get_center()
            
            positioned.append(item)
        
        # Resolve collisions
        self._resolve_collisions(positioned)
        
        # Constrain to screen bounds
        for item in positioned:
            self._constrain_position(item)
        
        return positioned
    
    def _layout_grid(self) -> List[ContentBox]:
        """Position content in grid layout."""
        if not self.content_boxes:
            return []
        
        # Determine grid dimensions
        n = len(self.content_boxes)
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)
        
        cell_width = self.screen_bounds.get_safe_width() / cols
        cell_height = self.screen_bounds.get_safe_height() / rows
        
        positioned = []
        for i, item in enumerate(self.content_boxes):
            row = i // cols
            col = i % cols
            
            x = self.screen_bounds.left + col * cell_width + cell_width / 2
            y = self.screen_bounds.top - row * cell_height - cell_height / 2
            
            item.position = (x, y)
            item.width = cell_width * 0.9
            item.height = cell_height * 0.9
            
            self._constrain_position(item)
            positioned.append(item)
        
        return positioned
    
    def _layout_centered(self) -> List[ContentBox]:
        """Center content with margins."""
        positioned = []
        
        for item in self.content_boxes:
            if item.width is None:
                item.width = self.screen_bounds.get_safe_width() * 0.7
            if item.height is None:
                item.height = self.screen_bounds.get_safe_height() * 0.5
            
            # Center in screen
            item.position = (0, 0)
            item.anchor = TextAnchor.CENTER
            
            self._constrain_position(item)
            positioned.append(item)
        
        return positioned
    
    def _validate_custom_layout(self) -> List[ContentBox]:
        """Validate and adjust custom-positioned layout."""
        positioned = self.content_boxes.copy()
        
        # Check each item stays within bounds
        for item in positioned:
            self._constrain_position(item)
        
        # Resolve collisions
        self._resolve_collisions(positioned)
        
        return positioned
    
    def _constrain_height(self, box: ContentBox):
        """Ensure content height fits screen."""
        if box.height is None:
            box.height = 1.0
        
        max_height = self.screen_bounds.get_safe_height() - 0.5
        if box.height > max_height:
            box.height = max_height
    
    def _constrain_position(self, box: ContentBox):
        """Ensure content stays within screen bounds."""
        if box.width is None:
            box.width = 2.0
        if box.height is None:
            box.height = 1.0
        
        left, right, top, bottom = box.get_bounds()
        
        # Shift horizontally if out of bounds
        if left < self.screen_bounds.left:
            offset = self.screen_bounds.left - left
            box.position = (box.position[0] + offset, box.position[1])
        elif right > self.screen_bounds.right:
            offset = right - self.screen_bounds.right
            box.position = (box.position[0] - offset, box.position[1])
        
        # Shift vertically if out of bounds
        if top > self.screen_bounds.top:
            offset = top - self.screen_bounds.top
            box.position = (box.position[0], box.position[1] - offset)
        elif bottom < self.screen_bounds.bottom:
            offset = self.screen_bounds.bottom - bottom
            box.position = (box.position[0], box.position[1] + offset)
    
    def _resolve_collisions(self, boxes: List[ContentBox]):
        """
        Resolve collisions between content boxes.
        Uses separation and repositioning.
        """
        max_iterations = 10
        for iteration in range(max_iterations):
            collisions = []
            
            # Detect all collisions
            for i, box1 in enumerate(boxes):
                for j, box2 in enumerate(boxes[i+1:], start=i+1):
                    if box1.intersects(box2):
                        collisions.append((i, j, box1, box2))
            
            if not collisions:
                break  # No more collisions
            
            # Resolve each collision
            for i, j, box1, box2 in collisions:
                self._separate_boxes(box1, box2)
    
    def _separate_boxes(self, box1: ContentBox, box2: ContentBox):
        """Separate two overlapping boxes."""
        b1_left, b1_right, b1_top, b1_bottom = box1.get_bounds()
        b2_left, b2_right, b2_top, b2_bottom = box2.get_bounds()
        
        # Calculate overlap
        overlap_left = max(b1_left, b2_left)
        overlap_right = min(b1_right, b2_right)
        overlap_top = min(b1_top, b2_top)
        overlap_bottom = max(b1_bottom, b2_bottom)
        
        overlap_x = overlap_right - overlap_left
        overlap_y = overlap_top - overlap_bottom
        
        # Move boxes apart in direction of smallest overlap
        if overlap_x < overlap_y:
            # Separate horizontally - determine which box is more to the left
            if box1.position[0] < box2.position[0]:
                # box1 is more to the left, push left/right
                box1.position = (box1.position[0] - overlap_x / 2 - 0.1, box1.position[1])
                box2.position = (box2.position[0] + overlap_x / 2 + 0.1, box2.position[1])
            else:
                # box2 is more to the left, push right/left
                box1.position = (box1.position[0] + overlap_x / 2 + 0.1, box1.position[1])
                box2.position = (box2.position[0] - overlap_x / 2 - 0.1, box2.position[1])
        else:
            # Separate vertically - determine which box is more above
            if box1.position[1] > box2.position[1]:
                # box1 is above box2, push up/down
                box1.position = (box1.position[0], box1.position[1] + overlap_y / 2 + 0.1)
                box2.position = (box2.position[0], box2.position[1] - overlap_y / 2 - 0.1)
            else:
                # box2 is above box1, push down/up
                box1.position = (box1.position[0], box1.position[1] - overlap_y / 2 - 0.1)
                box2.position = (box2.position[0], box2.position[1] + overlap_y / 2 + 0.1)
        
        # Re-constrain positions
        self._constrain_position(box1)
        self._constrain_position(box2)


def create_responsive_layout(
    content_type_counts: Dict[str, int],
    screen_bounds: ScreenBounds
) -> LayoutStrategy:
    """
    Recommend layout strategy based on content composition.
    
    Args:
        content_type_counts: e.g., {"text": 2, "figure": 1}
        screen_bounds: Screen dimensions
    
    Returns:
        Recommended LayoutStrategy
    """
    total = sum(content_type_counts.values())
    text_count = content_type_counts.get("text", 0)
    figure_count = content_type_counts.get("figure", 0)
    
    # Logic for choosing strategy
    if text_count > 0 and figure_count > 0 and text_count + figure_count == total:
        # Mix of text and figures
        return LayoutStrategy.SIDE_BY_SIDE
    elif total <= 2:
        # Few items, center them
        return LayoutStrategy.CENTERED
    elif total <= 4:
        # Medium items, use grid
        return LayoutStrategy.GRID
    else:
        # Many items, use floating with collision
        return LayoutStrategy.FLOATING


if __name__ == "__main__":
    # Example usage
    screen = ScreenBounds(width=16.0, height=9.0, margin=0.5)
    engine = LayoutEngine(screen, LayoutStrategy.SIDE_BY_SIDE)
    
    # Add content
    text_box = ContentBox(
        id="text1",
        type="text",
        content="The derivative measures rate of change",
        font_size=24,
        timestamp_start=0.0,
        timestamp_end=5.0
    )
    
    figure_box = ContentBox(
        id="fig1",
        type="figure",
        content="graph_data",
        width=3.0,
        height=2.0,
        timestamp_start=0.0,
        timestamp_end=5.0
    )
    
    engine.add_contents([text_box, figure_box])
    
    # Layout and display
    positioned = engine.layout()
    for box in positioned:
        print(f"{box.id}: pos={box.position}, bounds={box.get_bounds()}")
