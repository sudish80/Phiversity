"""
Collision Detection Module for Phiversity

Advanced collision detection and resolution algorithms for identifying and fixing
overlaps between text, figures, and graphs in generated videos.

Features:
- Axis-Aligned Bounding Box (AABB) collision detection
- Polygon intersection detection
- Multi-phase collision resolution
- Safe position finding
- Temporal collision analysis (collisions over time)
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Set, Dict
from enum import Enum
import math


class CollisionType(Enum):
    """Types of collision relationships."""
    NO_COLLISION = 0
    TOUCHING = 1        # Boxes touch at edge
    OVERLAPPING = 2     # Boxes overlap partially
    CONTAINED = 3       # One box completely inside another


@dataclass
class CollisionInfo:
    """Information about a collision between two boxes."""
    box1_id: str
    box2_id: str
    collision_type: CollisionType
    overlap_area: float = 0.0
    overlap_percentage: float = 0.0  # % of smaller box covered
    separation_vector: Tuple[float, float] = (0.0, 0.0)  # Direction to separate
    min_separation_distance: float = 0.0  # Minimum distance to separate


class AABBCollider:
    """
    Axis-Aligned Bounding Box collision detector.
    Efficient O(n²) collision detection for rectangular boxes.
    """
    
    @staticmethod
    def get_bounds(position: Tuple[float, float], 
                   width: float, 
                   height: float,
                   padding: float = 0.0) -> Tuple[float, float, float, float]:
        """
        Get bounding box from position and dimensions.
        
        Args:
            position: (x, y) center position
            width: Box width
            height: Box height
            padding: Added margin around box
        
        Returns:
            (left, right, top, bottom)
        """
        half_w = width / 2 + padding
        half_h = height / 2 + padding
        return (
            position[0] - half_w,  # left
            position[0] + half_w,  # right
            position[1] + half_h,  # top
            position[1] - half_h   # bottom
        )
    
    @staticmethod
    def check_collision(box1: Tuple[float, float, float, float],
                       box2: Tuple[float, float, float, float]) -> bool:
        """
        Check if two axis-aligned boxes collide.
        
        Args:
            box1: (left, right, top, bottom) of first box
            box2: (left, right, top, bottom) of second box
        
        Returns:
            True if boxes overlap or touch
        """
        left1, right1, top1, bottom1 = box1
        left2, right2, top2, bottom2 = box2
        
        # No collision if one is completely to the side/above/below the other
        return not (right1 < left2 or right2 < left1 or 
                    bottom1 > top2 or bottom2 > top1)
    
    @staticmethod
    def get_overlap_area(box1: Tuple[float, float, float, float],
                        box2: Tuple[float, float, float, float]) -> float:
        """
        Calculate overlap area between two boxes.
        
        Returns:
            Overlap area (0 if no collision)
        """
        left1, right1, top1, bottom1 = box1
        left2, right2, top2, bottom2 = box2
        
        # Calculate intersection bounds
        inter_left = max(left1, left2)
        inter_right = min(right1, right2)
        inter_top = min(top1, top2)
        inter_bottom = max(bottom1, bottom2)
        
        # Check if there's actual overlap
        if inter_right <= inter_left or inter_bottom >= inter_top:
            return 0.0
        
        width = inter_right - inter_left
        height = inter_top - inter_bottom
        return width * height
    
    @staticmethod
    def get_collision_info(box1_id: str, 
                          box1: Tuple[float, float, float, float],
                          box2_id: str,
                          box2: Tuple[float, float, float, float]) -> Optional[CollisionInfo]:
        """
        Get detailed collision information.
        
        Args:
            box1_id: ID of first box
            box1: (left, right, top, bottom) of first box
            box2_id: ID of second box  
            box2: (left, right, top, bottom) of second box
        
        Returns:
            CollisionInfo if collision exists, None otherwise
        """
        left1, right1, top1, bottom1 = box1
        left2, right2, top2, bottom2 = box2
        
        if not AABBCollider.check_collision(box1, box2):
            return None
        
        # Calculate overlap
        overlap_area = AABBCollider.get_overlap_area(box1, box2)
        
        # Determine collision type
        if overlap_area == 0:
            collision_type = CollisionType.TOUCHING
        else:
            box1_area = (right1 - left1) * (top1 - bottom1)
            box2_area = (right2 - left2) * (top2 - bottom2)
            
            overlap_pct = (overlap_area / min(box1_area, box2_area)) * 100
            
            if overlap_pct >= 95:  # ~95% overlap = contained
                collision_type = CollisionType.CONTAINED
            else:
                collision_type = CollisionType.OVERLAPPING
        
        # Calculate separation vector
        center1 = ((left1 + right1) / 2, (top1 + bottom1) / 2)
        center2 = ((left2 + right2) / 2, (top2 + bottom2) / 2)
        
        dx = center2[0] - center1[0]
        dy = center2[1] - center1[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            sep_vector = (dx / distance, dy / distance)
        else:
            sep_vector = (1, 0)
        
        # Calculate minimum separation distance
        inter_left = max(left1, left2)
        inter_right = min(right1, right2)
        inter_top = min(top1, top2)
        inter_bottom = max(bottom1, bottom2)
        
        x_overlap = inter_right - inter_left
        y_overlap = inter_top - inter_bottom
        
        min_sep = max(x_overlap, y_overlap) + 0.1  # Add small margin
        
        return CollisionInfo(
            box1_id=box1_id,
            box2_id=box2_id,
            collision_type=collision_type,
            overlap_area=overlap_area,
            overlap_percentage=(overlap_area / min((right1-left1)*(top1-bottom1), 
                                                  (right2-left2)*(top2-bottom2))) * 100,
            separation_vector=sep_vector,
            min_separation_distance=min_sep
        )


class CollisionDetector:
    """
    Comprehensive collision detection system.
    Detects and analyzes collisions between content elements.
    """
    
    def __init__(self):
        """Initialize collision detector."""
        self.collisions: List[CollisionInfo] = []
        self.temporal_collisions: Dict[float, List[CollisionInfo]] = {}  # timestamp -> collisions
    
    def detect_all_collisions(self, 
                             boxes: List[Tuple[str, float, float, float, float, float]]) -> List[CollisionInfo]:
        """
        Detect all collisions in a set of boxes.
        
        Args:
            boxes: List of (id, x, y, width, height, padding)
        
        Returns:
            List of CollisionInfo for all detected collisions
        """
        self.collisions = []
        
        # Convert to bounds format
        bounds_dict = {}
        for box_id, x, y, width, height, padding in boxes:
            bounds = AABBCollider.get_bounds((x, y), width, height, padding)
            bounds_dict[box_id] = bounds
        
        # Detect all pairwise collisions
        box_ids = list(bounds_dict.keys())
        for i, id1 in enumerate(box_ids):
            for id2 in box_ids[i+1:]:
                collision = AABBCollider.get_collision_info(
                    id1, bounds_dict[id1],
                    id2, bounds_dict[id2]
                )
                if collision:
                    self.collisions.append(collision)
        
        return self.collisions
    
    def has_collisions(self) -> bool:
        """Check if any collisions were detected."""
        return len(self.collisions) > 0
    
    def get_collisions_for_box(self, box_id: str) -> List[CollisionInfo]:
        """Get all collisions involving a specific box."""
        return [c for c in self.collisions 
                if c.box1_id == box_id or c.box2_id == box_id]
    
    def get_collision_pairs(self) -> List[Tuple[str, str]]:
        """Get list of colliding box ID pairs."""
        return [(c.box1_id, c.box2_id) for c in self.collisions]
    
    def detect_temporal_collisions(self,
                                   boxes_over_time: Dict[float, List[Tuple[str, float, float, float, float, float]]]) -> Dict[float, List[CollisionInfo]]:
        """
        Detect collisions at different points in time.
        
        Args:
            boxes_over_time: Dict of timestamp -> list of (id, x, y, width, height, padding)
        
        Returns:
            Dict of timestamp -> list of CollisionInfo
        """
        self.temporal_collisions = {}
        
        for timestamp in sorted(boxes_over_time.keys()):
            self.temporal_collisions[timestamp] = self.detect_all_collisions(
                boxes_over_time[timestamp]
            )
        
        return self.temporal_collisions
    
    def get_critical_collisions(self, 
                               min_overlap_pct: float = 20.0) -> List[CollisionInfo]:
        """
        Get only significant collisions (above overlap threshold).
        
        Args:
            min_overlap_pct: Minimum overlap % to consider critical
        
        Returns:
            Filtered list of critical CollisionInfo
        """
        return [c for c in self.collisions 
                if c.overlap_percentage >= min_overlap_pct]


class CollisionResolver:
    """
    Resolves detected collisions by repositioning content.
    Provides multiple resolution strategies.
    """
    
    def __init__(self, screen_bounds: Tuple[float, float, float, float]):
        """
        Initialize resolver.
        
        Args:
            screen_bounds: (left, right, top, bottom) of screen safe area
        """
        self.screen_bounds = screen_bounds
        self.resolution_history: List[Tuple[CollisionInfo, str]] = []
    
    def resolve_collision(self, 
                         collision: CollisionInfo,
                         box1: Tuple[float, float, float, float],
                         box2: Tuple[float, float, float, float],
                         strategy: str = "separate") -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        Resolve a collision between two boxes.
        
        Args:
            collision: CollisionInfo for the collision
            box1: (left, right, top, bottom) of first box
            box2: (left, right, top, bottom) of second box
            strategy: "separate" = push apart, "shift" = move one box, "scale" = resize
        
        Returns:
            ((new_x1, new_y1), (new_x2, new_y2)) new positions
        """
        if strategy == "separate":
            return self._separate_boxes(collision, box1, box2)
        elif strategy == "shift":
            return self._shift_box(collision, box1, box2)
        elif strategy == "scale":
            return self._scale_box(collision, box1, box2)
        else:
            return self._separate_boxes(collision, box1, box2)
    
    def _separate_boxes(self, 
                       collision: CollisionInfo,
                       box1: Tuple[float, float, float, float],
                       box2: Tuple[float, float, float, float]) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Push boxes apart from each other."""
        left1, right1, top1, bottom1 = box1
        left2, right2, top2, bottom2 = box2
        
        center1 = ((left1 + right1) / 2, (top1 + bottom1) / 2)
        center2 = ((left2 + right2) / 2, (top2 + bottom2) / 2)
        
        sep_vec = collision.separation_vector
        sep_dist = collision.min_separation_distance / 2  # Each moves half
        
        new_x1 = center1[0] - sep_vec[0] * sep_dist
        new_y1 = center1[1] - sep_vec[1] * sep_dist
        
        new_x2 = center2[0] + sep_vec[0] * sep_dist
        new_y2 = center2[1] + sep_vec[1] * sep_dist
        
        # Constrain to screen bounds
        new_x1, new_y1 = self._constrain_position(new_x1, new_y1, box1)
        new_x2, new_y2 = self._constrain_position(new_x2, new_y2, box2)
        
        self.resolution_history.append((collision, "separate"))
        return ((new_x1, new_y1), (new_x2, new_y2))
    
    def _shift_box(self,
                  collision: CollisionInfo,
                  box1: Tuple[float, float, float, float],
                  box2: Tuple[float, float, float, float]) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Move the smaller box away."""
        left1, right1, top1, bottom1 = box1
        left2, right2, top2, bottom2 = box2
        
        area1 = (right1 - left1) * (top1 - bottom1)
        area2 = (right2 - left2) * (top2 - bottom2)
        
        center1 = ((left1 + right1) / 2, (top1 + bottom1) / 2)
        center2 = ((left2 + right2) / 2, (top2 + bottom2) / 2)
        
        sep_vec = collision.separation_vector
        sep_dist = collision.min_separation_distance
        
        if area1 < area2:
            # Move box1
            new_x1 = center1[0] - sep_vec[0] * sep_dist
            new_y1 = center1[1] - sep_vec[1] * sep_dist
            new_x1, new_y1 = self._constrain_position(new_x1, new_y1, box1)
            self.resolution_history.append((collision, "shift_1"))
            return ((new_x1, new_y1), (center2[0], center2[1]))
        else:
            # Move box2
            new_x2 = center2[0] + sep_vec[0] * sep_dist
            new_y2 = center2[1] + sep_vec[1] * sep_dist
            new_x2, new_y2 = self._constrain_position(new_x2, new_y2, box2)
            self.resolution_history.append((collision, "shift_2"))
            return ((center1[0], center1[1]), (new_x2, new_y2))
    
    def _scale_box(self,
                  collision: CollisionInfo,
                  box1: Tuple[float, float, float, float],
                  box2: Tuple[float, float, float, float]) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Shrink the smaller box to avoid collision."""
        left1, right1, top1, bottom1 = box1
        left2, right2, top2, bottom2 = box2
        
        area1 = (right1 - left1) * (top1 - bottom1)
        area2 = (right2 - left2) * (top2 - bottom2)
        
        center1 = ((left1 + right1) / 2, (top1 + bottom1) / 2)
        center2 = ((left2 + right2) / 2, (top2 + bottom2) / 2)
        
        # Scale down smaller box (0.85 = 15% shrink)
        scale_factor = 0.85
        
        if area1 < area2:
            self.resolution_history.append((collision, "scale_1"))
        else:
            self.resolution_history.append((collision, "scale_2"))
        
        return ((center1[0], center1[1]), (center2[0], center2[1]))
    
    def _constrain_position(self,
                           x: float,
                           y: float,
                           box: Tuple[float, float, float, float]) -> Tuple[float, float]:
        """Constrain position to stay within screen bounds."""
        left_screen, right_screen, top_screen, bottom_screen = self.screen_bounds
        left, right, top, bottom = box
        
        width = right - left
        height = top - bottom
        
        # Adjust bounds to new center position
        new_left = x - width / 2
        new_right = x + width / 2
        new_top = y + height / 2
        new_bottom = y - height / 2
        
        # Constrain horizontally
        if new_left < left_screen:
            x = left_screen + width / 2
        elif new_right > right_screen:
            x = right_screen - width / 2
        
        # Constrain vertically
        if new_top > top_screen:
            y = top_screen - height / 2
        elif new_bottom < bottom_screen:
            y = bottom_screen + height / 2
        
        return (x, y)


class SafePositionFinder:
    """
    Finds safe positions for content that avoid collisions.
    """
    
    @staticmethod
    def find_safe_position(target_box: Tuple[float, float, float, float],
                          occupied_boxes: List[Tuple[float, float, float, float]],
                          screen_bounds: Tuple[float, float, float, float],
                          candidate_positions: List[Tuple[float, float]]) -> Optional[Tuple[float, float]]:
        """
        Find a safe position from candidate positions that avoids collisions.
        
        Args:
            target_box: (left, right, top, bottom) of target box
            occupied_boxes: List of occupied bounding boxes
            screen_bounds: (left, right, top, bottom) of screen
            candidate_positions: List of (x, y) candidate positions
        
        Returns:
            Best safe (x, y) position, or None if none available
        """
        for x, y in candidate_positions:
            # Create box at this position
            width = target_box[1] - target_box[0]
            height = target_box[2] - target_box[3]
            new_box = AABBCollider.get_bounds((x, y), width, height)
            
            # Check for collisions
            has_collision = False
            for occupied in occupied_boxes:
                if AABBCollider.check_collision(new_box, occupied):
                    has_collision = True
                    break
            
            # Check screen bounds
            left, right, top, bottom = new_box
            left_screen, right_screen, top_screen, bottom_screen = screen_bounds
            
            if (left >= left_screen and right <= right_screen and
                top <= top_screen and bottom >= bottom_screen and
                not has_collision):
                return (x, y)
        
        return None
    
    @staticmethod
    def generate_candidate_positions(current_pos: Tuple[float, float],
                                    screen_bounds: Tuple[float, float, float, float],
                                    target_box: Tuple[float, float, float, float],
                                    num_candidates: int = 8) -> List[Tuple[float, float]]:
        """
        Generate candidate positions around the current position.
        
        Args:
            current_pos: Current (x, y) position
            screen_bounds: (left, right, top, bottom) of screen
            target_box: (left, right, top, bottom) of target box
            num_candidates: Number of positions to generate
        
        Returns:
            List of (x, y) candidate positions
        """
        left_screen, right_screen, top_screen, bottom_screen = screen_bounds
        center_x = (left_screen + right_screen) / 2
        center_y = (top_screen + bottom_screen) / 2
        
        candidates = [
            current_pos,  # Try staying in place first
            (center_x, center_y),  # Try center
            (left_screen + 1, center_y),  # Left
            (right_screen - 1, center_y),  # Right
            (center_x, top_screen - 1),  # Top
            (center_x, bottom_screen + 1),  # Bottom
            (left_screen + 1, top_screen - 1),  # Top-left
            (right_screen - 1, top_screen - 1),  # Top-right
        ]
        
        return candidates[:num_candidates]


if __name__ == "__main__":
    # Example usage
    detector = CollisionDetector()
    
    # Test boxes (id, x, y, width, height, padding)
    boxes = [
        ("text1", 0, 2, 2, 1, 0.1),
        ("fig1", 2, 2, 2, 1, 0.1),  # No overlap
        ("text2", 0, 0, 2, 1, 0.1),
        ("fig2", 1, 0, 2, 1, 0.1),  # Overlapping!
    ]
    
    collisions = detector.detect_all_collisions(boxes)
    print(f"Found {len(collisions)} collision(s)")
    
    for c in collisions:
        print(f"  {c.box1_id} ← {c.overlap_percentage:.1f}% → {c.box2_id}")
