"""
QA Metrics Module for Phiversity

Calculates quality metrics for layout and collision detection:
- Overlap Ratio (OR): % of frames where overlap detected (target: 0%)
- Readability Index (RI): Font legibility + visibility score (target: 1.0)
- Layer Accuracy (LA): % of elements on correct z-order (target: 100%)
- Timing Accuracy (TA): Text display vs narration alignment (target: ±0.2s)

These metrics drive continuous improvement of visual quality.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any
import math


class MetricType(Enum):
    """Types of QA metrics."""
    OVERLAP_RATIO = "overlap_ratio"
    READABILITY_INDEX = "readability_index"
    LAYER_ACCURACY = "layer_accuracy"
    TIMING_ACCURACY = "timing_accuracy"


@dataclass
class MetricResult:
    """Result of a single metric calculation."""
    metric_type: MetricType
    score: float              # Score on 0.0-1.0 scale (higher is better)
    name: str                 # Human-readable name
    target: float             # Target score
    status: str               # "pass", "warning", "fail"
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0    # When measured
    
    def __post_init__(self):
        """Determine status based on score vs target."""
        tolerance = 0.05  # Within 5% of target is passing
        
        if self.score >= self.target - tolerance:
            self.status = "pass"
        elif self.score >= self.target * 0.75:  # 75% of target
            self.status = "warning"
        else:
            self.status = "fail"


@dataclass
class FrameAnalysis:
    """Analysis of a single video frame."""
    frame_number: int
    timestamp: float
    has_overlap: bool = False
    overlap_count: int = 0      # Number of overlapping regions
    overlap_area: float = 0.0   # Total overlap area in pixels
    unreadable_text: List[str] = field(default_factory=list)  # Elements with low readability
    layer_violations: List[Tuple[str, str]] = field(default_factory=list)  # (elem1, elem2) wrong order
    timing_issues: List[str] = field(default_factory=list)  # Elements displayed at wrong time


@dataclass
class QAReport:
    """Complete QA report for a video/animation."""
    total_frames: int
    duration_seconds: float
    metrics: Dict[MetricType, MetricResult] = field(default_factory=dict)
    overall_score: float = 0.0       # Weighted average of all metrics
    quality_level: str = "unknown"   # "excellent", "good", "fair", "poor"
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    frame_analyses: List[FrameAnalysis] = field(default_factory=list)


class OverlapRatioCalculator:
    """
    Calculates Overlap Ratio (OR) metric.
    
    OR = (frames_with_overlap / total_frames) * 100
    Target: 0% (no overlapping frames)
    Acceptable: < 5% (occasional overlaps)
    Fail: > 20% (frequent overlaps)
    """
    
    @staticmethod
    def calculate(frame_analyses: List[FrameAnalysis]) -> MetricResult:
        """
        Calculate overlap ratio from frame analyses.
        
        Args:
            frame_analyses: List of FrameAnalysis objects
        
        Returns:
            MetricResult with OR score
        """
        if not frame_analyses:
            return MetricResult(
                metric_type=MetricType.OVERLAP_RATIO,
                score=1.0,
                name="Overlap Ratio",
                target=1.0,  # 1.0 = 0% overlap
                status="pass",
                details={"frames_analyzed": 0}
            )
        
        overlap_frames = sum(1 for f in frame_analyses if f.has_overlap)
        total_frames = len(frame_analyses)
        
        # Calculate score: 1.0 (0% overlap) down to 0.0 (100% overlap)
        overlap_percentage = (overlap_frames / total_frames) * 100
        score = max(0.0, 1.0 - (overlap_percentage / 100))
        
        return MetricResult(
            metric_type=MetricType.OVERLAP_RATIO,
            score=score,
            name="Overlap Ratio (OR)",
            target=1.0,
            details={
                "overlap_frames": overlap_frames,
                "total_frames": total_frames,
                "overlap_percentage": overlap_percentage,
                "first_overlap_at": frame_analyses[[f.has_overlap for f in frame_analyses].index(True)].frame_number
                    if any(f.has_overlap for f in frame_analyses) else -1
            }
        )
    
    @staticmethod
    def calculate_from_collision_data(
        collisions_per_frame: Dict[int, List[Tuple[str, str]]]
    ) -> MetricResult:
        """
        Calculate OR from collision data per frame.
        
        Args:
            collisions_per_frame: Dict of frame_number -> list of (elem1, elem2) collisions
        
        Returns:
            MetricResult with OR score
        """
        total_frames = max(collisions_per_frame.keys()) + 1 if collisions_per_frame else 1
        frames_with_collision = len([f for f, c in collisions_per_frame.items() if c])
        
        overlap_percentage = (frames_with_collision / total_frames) * 100
        score = max(0.0, 1.0 - (overlap_percentage / 100))
        
        return MetricResult(
            metric_type=MetricType.OVERLAP_RATIO,
            score=score,
            name="Overlap Ratio (OR)",
            target=1.0,
            details={
                "collision_frames": frames_with_collision,
                "total_frames": total_frames,
                "overlap_percentage": overlap_percentage,
            }
        )


class ReadabilityIndexCalculator:
    """
    Calculates Readability Index (RI) metric.
    
    RI combines:
    - Font size (larger = more readable, minimum 12pt)
    - Contrast (text color vs background)
    - Visibility (not hidden by other elements)
    
    Score: 0.0 (unreadable) to 1.0 (highly readable)
    Target: 1.0 (all text readable)
    Acceptable: > 0.85 (mostly readable)
    Fail: < 0.60 (significant readability issues)
    """
    
    MIN_READABLE_FONT = 12  # Minimum font size for readability
    MIN_READABLE_CONTRAST = 4.5  # WCAG AA standard
    
    @staticmethod
    def calculate(text_elements: List[Dict[str, Any]]) -> MetricResult:
        """
        Calculate readability index from text element properties.
        
        Args:
            text_elements: List of dicts with: font_size, color, bg_color, is_visible
        
        Returns:
            MetricResult with RI score
        """
        if not text_elements:
            return MetricResult(
                metric_type=MetricType.READABILITY_INDEX,
                score=1.0,
                name="Readability Index",
                target=1.0,
                status="pass",
                details={"text_elements": 0}
            )
        
        readability_scores = []
        unreadable_elements = []
        
        for element in text_elements:
            font_size = element.get("font_size", 12)
            color = element.get("color", "#000000")
            bg_color = element.get("bg_color", "#FFFFFF")
            is_visible = element.get("is_visible", True)
            element_id = element.get("id", "unknown")
            
            # Font size component (12pt = 0.7, 24pt = 0.9, 48pt = 1.0)
            font_score = min(1.0, (font_size - 8) / 40)
            
            # Visibility component
            visibility_score = 1.0 if is_visible else 0.3
            
            # Contrast component (simplified - assumes luminance difference)
            contrast_score = ReadabilityIndexCalculator._calculate_contrast(color, bg_color)
            
            # Combined readability of this element
            element_readability = (font_score * 0.5 + 
                                  visibility_score * 0.3 + 
                                  contrast_score * 0.2)
            
            readability_scores.append(element_readability)
            
            if element_readability < 0.6:
                unreadable_elements.append({
                    "id": element_id,
                    "font_size": font_size,
                    "readability": element_readability,
                    "reason": "low_font_size" if font_size < 12 else "low_contrast"
                })
        
        # Overall score is average of element readabilities
        overall_score = sum(readability_scores) / len(readability_scores)
        
        return MetricResult(
            metric_type=MetricType.READABILITY_INDEX,
            score=overall_score,
            name="Readability Index (RI)",
            target=1.0,
            details={
                "text_elements": len(text_elements),
                "readable_elements": len(readability_scores) - len(unreadable_elements),
                "unreadable_elements": unreadable_elements,
                "avg_font_size": sum(e.get("font_size", 12) for e in text_elements) / len(text_elements),
            }
        )
    
    @staticmethod
    def _calculate_contrast(color1: str, color2: str) -> float:
        """
        Calculate contrast ratio between two colors (0.0 to 1.0).
        Simplified WCAG contrast calculation.
        """
        try:
            r1, g1, b1 = ReadabilityIndexCalculator._hex_to_rgb(color1)
            r2, g2, b2 = ReadabilityIndexCalculator._hex_to_rgb(color2)
            
            # Calculate luminance
            l1 = 0.299 * r1 + 0.587 * g1 + 0.114 * b1
            l2 = 0.299 * r2 + 0.587 * g2 + 0.114 * b2
            
            # Contrast ratio (0-1 scale)
            contrast = abs(l1 - l2) / 255
            return min(1.0, contrast / 0.5)  # Normalize to 0-1
        except:
            return 0.5  # Default if parsing fails
    
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to RGB."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class LayerAccuracyCalculator:
    """
    Calculates Layer Accuracy (LA) metric.
    
    LA = (elements_on_correct_layer / total_elements) * 100
    
    Checks that:
    - Text overlays are above content (higher z-index)
    - UI elements are above everything else
    - Background is below content
    
    Score: 0.0 to 1.0 (1.0 = all elements correct)
    Target: 1.0 (100% correct layering)
    Acceptable: > 0.90 (minor layering issues)
    Fail: < 0.70 (significant layering problems)
    """
    
    # Layer hierarchy rules
    HIERARCHY_RULES = [
        # (element_type1, comparison, element_type2) -> element_type1 z_index comparison element_type2 z_index
        ("text", "*", "graph"),       # Text should be > graph
        ("text", "*", "figure"),      # Text should be > figure
        ("annotation", "*", "text"),  # Annotation should be > text
        ("ui", "*", "content"),       # UI should be > content
        ("content", "*", "background"),  # Content should be > background
    ]
    
    @staticmethod
    def calculate(elements: List[Dict[str, Any]]) -> MetricResult:
        """
        Calculate layer accuracy from element assignments.
        
        Args:
            elements: List of dicts with: id, type, z_index
        
        Returns:
            MetricResult with LA score
        """
        if not elements:
            return MetricResult(
                metric_type=MetricType.LAYER_ACCURACY,
                score=1.0,
                name="Layer Accuracy",
                target=1.0,
                status="pass",
                details={"elements": 0}
            )
        
        violations = []
        
        # Check all pairwise rules
        for i, elem1 in enumerate(elements):
            for elem2 in elements[i+1:]:
                type1 = elem1.get("type", "unknown")
                type2 = elem2.get("type", "unknown")
                z1 = elem1.get("z_index", 0)
                z2 = elem2.get("z_index", 0)
                
                # Check if types match a rule
                for rule_type1, comparison, rule_type2 in LayerAccuracyCalculator.HIERARCHY_RULES:
                    if type1 == rule_type1 and type2 == rule_type2:
                        if z1 <= z2:  # Violation: type1 should be > type2
                            violations.append({
                                "elem1": elem1.get("id"),
                                "elem2": elem2.get("id"),
                                "type1": type1,
                                "type2": type2,
                                "z1": z1,
                                "z2": z2,
                            })
        
        # Calculate score
        total_pairs = len(elements) * (len(elements) - 1) / 2
        violation_count = len(violations)
        correct_count = total_pairs - violation_count
        
        score = correct_count / total_pairs if total_pairs > 0 else 1.0
        
        return MetricResult(
            metric_type=MetricType.LAYER_ACCURACY,
            score=score,
            name="Layer Accuracy (LA)",
            target=1.0,
            details={
                "total_elements": len(elements),
                "correct_layers": int(correct_count),
                "violation_count": violation_count,
                "violations": violations,
            }
        )


class TimingAccuracyCalculator:
    """
    Calculates Timing Accuracy (TA) metric.
    
    TA measures synchronization between text display and narration window.
    
    For each text element:
    TA_element = time_mismatch / expected_duration
    
    Target: ±0.2 seconds (text appears/disappears within 0.2s of narration)
    Acceptable: ±0.5 seconds
    Fail: > 1.0 second mismatch
    
    Overall TA = average of all element scores
    """
    
    TARGET_TIMING_ERROR = 0.2  # 200ms tolerance
    
    @staticmethod
    def calculate(text_elements: List[Dict[str, Any]]) -> MetricResult:
        """
        Calculate timing accuracy from text element timing data.
        
        Args:
            text_elements: List of dicts with: id, text_start, text_end, narration_start, narration_end
        
        Returns:
            MetricResult with TA score
        """
        if not text_elements:
            return MetricResult(
                metric_type=MetricType.TIMING_ACCURACY,
                score=1.0,
                name="Timing Accuracy",
                target=1.0,
                status="pass",
                details={"text_elements": 0}
            )
        
        timing_mismatches = []
        
        for element in text_elements:
            element_id = element.get("id", "unknown")
            text_start = element.get("text_start", 0.0)
            text_end = element.get("text_end", 0.0)
            narration_start = element.get("narration_start", 0.0)
            narration_end = element.get("narration_end", text_end)
            
            # Expected duration
            expected_duration = narration_end - narration_start
            
            # Actual mismatches
            start_mismatch = abs(text_start - narration_start)
            end_mismatch = abs(text_end - narration_end)
            max_mismatch = max(start_mismatch, end_mismatch)
            
            # Normalize by expected duration
            if expected_duration > 0:
                normalized_error = max_mismatch / expected_duration
            else:
                normalized_error = 0.0
            
            timing_mismatches.append({
                "id": element_id,
                "max_mismatch": max_mismatch,
                "normalized_error": normalized_error,
                "status": "pass" if max_mismatch <= TimingAccuracyCalculator.TARGET_TIMING_ERROR else "fail"
            })
        
        # Calculate overall score
        if not timing_mismatches:
            avg_mismatch = 0.0
            max_mismatch_val = 0.0
        else:
            avg_mismatch = sum(m["max_mismatch"] for m in timing_mismatches) / len(timing_mismatches)
            max_mismatch_val = max(m["max_mismatch"] for m in timing_mismatches)
        
        # Convert to 0-1 scale (0.2s = 0.8 score)
        score = max(0.0, 1.0 - (avg_mismatch / 0.5))
        
        correct_timing = sum(1 for m in timing_mismatches if m["status"] == "pass")
        
        return MetricResult(
            metric_type=MetricType.TIMING_ACCURACY,
            score=score,
            name="Timing Accuracy (TA)",
            target=1.0,
            details={
                "text_elements": len(text_elements),
                "correct_timing": correct_timing,
                "avg_timing_error": avg_mismatch,
                "max_timing_error": max_mismatch_val,
                "timing_mismatches": timing_mismatches,
            }
        )


class QAMetricsEngine:
    """
    Complete QA metrics calculation engine.
    Combines all metrics into comprehensive quality report.
    """
    
    # Weights for overall score calculation
    METRIC_WEIGHTS = {
        MetricType.OVERLAP_RATIO: 0.35,      # Most important: no overlaps
        MetricType.READABILITY_INDEX: 0.30,  # Important: text must be readable
        MetricType.LAYER_ACCURACY: 0.20,     # Important: proper layering
        MetricType.TIMING_ACCURACY: 0.15,    # Nice to have: good timing
    }
    
    def __init__(self):
        """Initialize QA metrics engine."""
        self.reports: List[QAReport] = []
    
    def calculate_all_metrics(self,
                             frame_analyses: List[FrameAnalysis],
                             text_elements: List[Dict[str, Any]],
                             elements_with_layers: List[Dict[str, Any]],
                             total_duration: float) -> QAReport:
        """
        Calculate all QA metrics and generate comprehensive report.
        
        Args:
            frame_analyses: List of FrameAnalysis objects
            text_elements: List of text element dicts with timing/readability data
            elements_with_layers: List of element dicts with z-index/type
            total_duration: Total video duration in seconds
        
        Returns:
            Comprehensive QAReport
        """
        report = QAReport(
            total_frames=len(frame_analyses),
            duration_seconds=total_duration
        )
        
        # Calculate individual metrics
        or_result = OverlapRatioCalculator.calculate(frame_analyses)
        ri_result = ReadabilityIndexCalculator.calculate(text_elements)
        la_result = LayerAccuracyCalculator.calculate(elements_with_layers)
        ta_result = TimingAccuracyCalculator.calculate(text_elements)
        
        report.metrics = {
            MetricType.OVERLAP_RATIO: or_result,
            MetricType.READABILITY_INDEX: ri_result,
            MetricType.LAYER_ACCURACY: la_result,
            MetricType.TIMING_ACCURACY: ta_result,
        }
        
        # Calculate overall score (weighted average)
        total_weight = sum(self.METRIC_WEIGHTS.values())
        weighted_sum = sum(
            report.metrics[mtype].score * weight
            for mtype, weight in self.METRIC_WEIGHTS.items()
        )
        report.overall_score = weighted_sum / total_weight
        
        # Determine quality level
        if report.overall_score >= 0.9:
            report.quality_level = "excellent"
        elif report.overall_score >= 0.8:
            report.quality_level = "good"
        elif report.overall_score >= 0.7:
            report.quality_level = "fair"
        else:
            report.quality_level = "poor"
        
        # Extract issues and recommendations
        self._extract_issues(report)
        self._generate_recommendations(report)
        
        # Store frame analyses
        report.frame_analyses = frame_analyses
        
        self.reports.append(report)
        return report
    
    def _extract_issues(self, report: QAReport):
        """Extract critical issues and warnings from metrics."""
        for mtype, result in report.metrics.items():
            if result.status == "fail":
                report.critical_issues.append(f"{result.name}: {result.score:.1%} (target: {result.target:.1%})")
            elif result.status == "warning":
                report.warnings.append(f"{result.name}: {result.score:.1%} (target: {result.target:.1%})")
    
    def _generate_recommendations(self, report: QAReport):
        """Generate actionable recommendations based on metrics."""
        recommendations = []
        
        or_result = report.metrics.get(MetricType.OVERLAP_RATIO)
        if or_result and or_result.score < 0.95:
            overlap_pct = or_result.details.get("overlap_percentage", 0)
            recommendations.append(
                f"Reduce overlaps: {overlap_pct:.1f}% of frames have overlapping elements. "
                f"Use dynamic layout or increase spacing between elements."
            )
        
        ri_result = report.metrics.get(MetricType.READABILITY_INDEX)
        if ri_result and ri_result.score < 0.85:
            unreadable = ri_result.details.get("unreadable_elements", [])
            if unreadable:
                recommendations.append(
                    f"Improve text readability: {len(unreadable)} elements are hard to read. "
                    f"Increase font size (min 12pt) or improve contrast."
                )
        
        la_result = report.metrics.get(MetricType.LAYER_ACCURACY)
        if la_result and la_result.score < 0.90:
            violations = la_result.details.get("violation_count", 0)
            recommendations.append(
                f"Fix layer ordering: {violations} elements are on incorrect layers. "
                f"Ensure text is above graphs and UI is on top."
            )
        
        ta_result = report.metrics.get(MetricType.TIMING_ACCURACY)
        if ta_result and ta_result.score < 0.85:
            avg_error = ta_result.details.get("avg_timing_error", 0)
            recommendations.append(
                f"Synchronize timing: Average timing error is {avg_error:.2f}s. "
                f"Text should appear/disappear within 0.2s of narration."
            )
        
        report.recommendations = recommendations
    
    def generate_summary(self, report: QAReport) -> str:
        """Generate human-readable summary of QA report."""
        lines = [
            "=== PHIVERSITY QA REPORT ===",
            f"Duration: {report.duration_seconds:.1f}s ({report.total_frames} frames)",
            f"Overall Quality: {report.quality_level.upper()} ({report.overall_score:.1%})",
            "",
            "Metric Scores:",
        ]
        
        for mtype, result in sorted(report.metrics.items()):
            status_icon = "✓" if result.status == "pass" else "▲" if result.status == "warning" else "✗"
            lines.append(f"  {status_icon} {result.name}: {result.score:.1%}")
        
        if report.critical_issues:
            lines.extend(["", "Critical Issues:"])
            for issue in report.critical_issues:
                lines.append(f"  • {issue}")
        
        if report.warnings:
            lines.extend(["", "Warnings:"])
            for warning in report.warnings:
                lines.append(f"  • {warning}")
        
        if report.recommendations:
            lines.extend(["", "Recommendations:"])
            for i, rec in enumerate(report.recommendations, 1):
                lines.append(f"  {i}. {rec}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Example usage
    engine = QAMetricsEngine()
    
    # Create sample frame analysis
    frame_analyses = [
        FrameAnalysis(i, i * 0.033, has_overlap=(i % 20 == 0))
        for i in range(100)
    ]
    
    # Create sample text elements
    text_elements = [
        {
            "id": "text1",
            "font_size": 24,
            "color": "#FFFFFF",
            "bg_color": "#000000",
            "is_visible": True,
            "text_start": 0.0,
            "text_end": 3.0,
            "narration_start": 0.0,
            "narration_end": 3.1,
        }
    ]
    
    # Create sample element with layers
    elements = [
        {"id": "bg", "type": "background", "z_index": 0},
        {"id": "graph", "type": "graph", "z_index": 10},
        {"id": "text", "type": "text", "z_index": 20},
    ]
    
    # Generate report
    report = engine.calculate_all_metrics(frame_analyses, text_elements, elements, 3.3)
    print(engine.generate_summary(report))
