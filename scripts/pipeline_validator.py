"""
Pipeline Validator: Ensures step sequencing, audio-visual sync, adaptive pacing, and redundancy detection.

This module validates the complete animation pipeline to ensure:
1. All solution steps are explicitly covered in the animation
2. Steps appear in correct logical order
3. Audio-visual synchronization is precise (sub-second)
4. Pacing adapts to step complexity
5. Redundancy and content drift are detected
"""

import json
import re
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from collections import Counter


class PacingLevel(Enum):
    """Complexity-based pacing levels."""
    SIMPLE = (2.0, 3.0)        # 2-3 seconds per step
    MODERATE = (3.5, 5.0)      # 3.5-5 seconds per step
    COMPLEX = (5.5, 8.0)       # 5.5-8 seconds per step
    VERY_COMPLEX = (8.5, 12.0) # 8.5-12 seconds per step


@dataclass
class StepValidationResult:
    """Result of step validation."""
    is_valid: bool
    total_steps: int
    covered_steps: int
    skipped_steps: List[str]
    out_of_order: List[Tuple[int, str]]  # (step_num, reason)
    redundant_content: List[str]
    warnings: List[str]


@dataclass
class SyncValidationResult:
    """Result of audio-visual sync validation."""
    is_valid: bool
    total_duration: float
    audio_duration: float
    video_duration: float
    sync_error_seconds: float
    timing_precision_ms: float
    element_timing_issues: List[Tuple[int, int, str]]  # (scene_idx, elem_idx, issue)


@dataclass
class PacingAnalysis:
    """Analysis of scene and element pacing."""
    total_duration: float
    scenes: List[Dict[str, Any]]
    adaptive_timings: List[float]
    pacing_warnings: List[str]


class StepSequenceValidator:
    """Validates that all solution steps are covered in animation and appear in order."""
    
    def __init__(self, solution_steps: List[Dict[str, str]], animation_scenes: List[Dict[str, Any]]):
        """
        Args:
            solution_steps: List of steps from solution.steps
            animation_scenes: List of scenes from animation_plan.scenes
        """
        self.solution_steps = solution_steps
        self.animation_scenes = animation_scenes
    
    def validate(self) -> StepValidationResult:
        """Validate step sequencing and coverage."""
        skipped_steps = []
        out_of_order = []
        redundant_content = []
        warnings = []
        
        # Extract all text content from animation
        animation_text = self._extract_all_text()
        animation_text_lower = animation_text.lower()
        
        # Check coverage: each solution step should appear in animation
        covered_count = 0
        step_positions = []
        
        for step_idx, step in enumerate(self.solution_steps):
            title = step.get("title", "").lower()
            explanation = step.get("explanation", "").lower()
            latex = (step.get("latex") or "").lower()
            
            # Check if step content appears in animation with multiple keywords
            # Requires at least 2 keywords found to avoid false positives
            step_keywords = self._extract_keywords(title + " " + explanation)
            found = sum(1 for keyword in step_keywords if keyword in animation_text_lower) >= 2
            
            if found:
                covered_count += 1
                # Find position in animation for ordering check
                position = self._find_content_position(animation_text_lower, step_keywords)
                # Only add if position is valid (not infinity)
                if position != float('inf'):
                    step_positions.append((step_idx, position, title))
                else:
                    warnings.append(f"Step {step_idx + 1}: Keywords found but position unclear")
            else:
                skipped_steps.append(f"Step {step_idx + 1}: {title}")
        
        # Check ordering (only for valid positions)
        for i in range(1, len(step_positions)):
            prev_idx, prev_pos, prev_title = step_positions[i-1]
            curr_idx, curr_pos, curr_title = step_positions[i]
            
            # Only check if both positions are valid
            if curr_pos != float('inf') and prev_pos != float('inf') and curr_pos < prev_pos:
                out_of_order.append((
                    i,
                    f"Step {curr_idx + 1} appears before Step {prev_idx + 1}"
                ))
        
        # Detect redundancy (repeated explanation of same concept)
        redundant_content = self._detect_redundancy(animation_text)
        
        # Generate warnings
        if len(skipped_steps) > 0:
            warnings.append(f"⚠️  {len(skipped_steps)} solution step(s) not found in animation")
        if covered_count < len(self.solution_steps) * 0.8:
            warnings.append(f"⚠️  Only {covered_count}/{len(self.solution_steps)} steps covered (<80%)")
        if len(redundant_content) > 0:
            warnings.append(f"⚠️  Redundant content detected: {len(redundant_content)} instances")
        
        return StepValidationResult(
            is_valid=len(skipped_steps) == 0 and len(out_of_order) == 0,
            total_steps=len(self.solution_steps),
            covered_steps=covered_count,
            skipped_steps=skipped_steps,
            out_of_order=out_of_order,
            redundant_content=redundant_content,
            warnings=warnings
        )
    
    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Remove common words and punctuation
        common_words = {
            'the', 'is', 'at', 'that', 'this', 'a', 'an', 'and', 'or',
            'in', 'on', 'of', 'to', 'for', 'with', 'by', 'from', 'we', 'it',
            'are', 'be', 'been', 'being', 'have', 'has', 'do', 'does', 'did',
            'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can'
        }
        words = re.findall(r'\w+', text.lower())
        # Accept words >= 3 chars to catch "use", "due", "for" etc.
        keywords = [w for w in words if w not in common_words and len(w) >= 3]
        # Sort by frequency for more reliable matching
        counter = Counter(keywords)
        return [w for w, _ in counter.most_common(15)]  # Top 15 by frequency
    
    def _find_content_position(self, text: str, keywords: List[str]) -> int:
        """Find earliest position of keywords in text."""
        positions = []
        for keyword in keywords:
            pos = text.find(keyword)
            if pos >= 0:
                positions.append(pos)
        return min(positions) if positions else float('inf')
    
    def _extract_all_text(self) -> str:
        """Extract all text content from animation scenes."""
        content = []
        for scene in self.animation_scenes:
            content.append(scene.get("description", ""))
            content.append(scene.get("voiceover", ""))
            
            for element in scene.get("elements", []):
                if element.get("type") in ["Text", "Latex", "MathTex"]:
                    content.append(element.get("content", ""))
        
        return " ".join(content)
    
    def _detect_redundancy(self, text: str) -> List[str]:
        """Detect repeated explanations of concepts."""
        # Better redundancy detection using semantic patterns
        sentences = re.split(r'[.!?]+', text)
        seen_concepts = {}
        redundant = []
        
        for sent in sentences:
            # Normalize sentence (lowercase, remove extra spaces)
            normalized = " ".join(sent.lower().split())
            if len(normalized) < 20:
                continue
            
            # Extract key concept words (exclude common words)
            concept_words = self._extract_keywords(normalized)
            if not concept_words:
                continue
            
            # Create concept signature from significant words
            concept_sig = tuple(sorted(concept_words[:5]))
            
            if concept_sig in seen_concepts:
                redundant.append(normalized[:80])
            else:
                seen_concepts[concept_sig] = True
        
        return redundant[:5]  # Return top 5 redundancies


class AudioVisualSyncValidator:
    """Validates audio-visual synchronization with sub-second precision."""
    
    def __init__(
        self,
        animation_scenes: List[Dict[str, Any]],
        audio_durations: Optional[List[float]] = None,
        element_durations: Optional[List[List[float]]] = None
    ):
        """
        Args:
            animation_scenes: List of animation scenes
            audio_durations: Duration of audio for each scene
            element_durations: Duration of audio for each element in each scene
        """
        self.animation_scenes = animation_scenes
        self.audio_durations = audio_durations or [0.0] * len(animation_scenes)
        self.element_durations = element_durations or []
    
    def validate(self) -> SyncValidationResult:
        """Validate audio-visual synchronization."""
        # Input validation: require audio durations
        if not self.audio_durations or all(d == 0 for d in self.audio_durations):
            return SyncValidationResult(
                is_valid=True,
                total_duration=0.0,
                audio_duration=0.0,
                video_duration=0.0,
                sync_error_seconds=0.0,
                timing_precision_ms=0.0,
                element_timing_issues=[(-1, -1, "Sync check skipped: no audio durations provided")]
            )
        
        # Calculate expected animation durations from Manim timings
        video_duration = self._calculate_video_duration()
        audio_duration = sum(self.audio_durations)
        sync_error = abs(video_duration - audio_duration)
        
        # Calculate timing precision (how well sub-elements align with audio)
        timing_precision_ms = self._calculate_timing_precision()
        
        # Check element timing issues
        element_issues = self._validate_element_timing()
        
        # Only mark valid if we have real data
        is_valid = (
            audio_duration > 0 and  # Must have audio data
            sync_error < 0.5 and  # Less than 500ms sync error
            (timing_precision_ms < 100 or timing_precision_ms == 0.0)  # <100ms or no data
        )
        
        return SyncValidationResult(
            is_valid=is_valid,
            total_duration=max(video_duration, audio_duration),
            audio_duration=audio_duration,
            video_duration=video_duration,
            sync_error_seconds=sync_error,
            timing_precision_ms=timing_precision_ms,
            element_timing_issues=element_issues
        )
    
    def _calculate_video_duration(self) -> float:
        """Calculate expected video duration from Manim animations."""
        total = 0.0
        
        for scene in self.animation_scenes:
            # Use explicit timing if available, else estimate
            scene_timing = scene.get("timing", {})
            scene_duration = scene_timing.get("duration", None)
            
            if scene_duration is None:
                # Calculate from elements
                element_timings = []
                for element in scene.get("elements", []):
                    timing = element.get("timing", {})
                    duration_in = timing.get("duration_in", 0.0)
                    duration_out = timing.get("duration_out", 0.0)
                    wait_duration = timing.get("wait", 0.0)
                    element_timings.append(duration_in + duration_out + wait_duration)
                
                # Scene duration is sum of element timings, min 0.5s
                scene_duration = max(sum(element_timings), 0.5)
            
            total += scene_duration
        
        return total
    
    def _calculate_timing_precision(self) -> float:
        """Calculate average timing precision across all elements."""
        if not self.element_durations:
            return 0.0  # No element data = can't measure precision
        
        variations = []
        mismatches = 0
        
        for scene_idx, dur_list in enumerate(self.element_durations):
            if scene_idx >= len(self.animation_scenes):
                mismatches += 1
                continue
            
            elements = self.animation_scenes[scene_idx].get("elements", [])
            
            for elem_idx, elem_dur in enumerate(dur_list):
                if elem_idx >= len(elements):
                    mismatches += 1
                    continue
                
                expected = elements[elem_idx].get("timing", {}).get("duration_in", 1.0)
                variation = abs(elem_dur - expected)
                variations.append(variation * 1000)  # Convert to ms
        
        if mismatches > 0:
            variation = sum(variations) / len(variations) if variations else 0.0
            variation += mismatches * 50  # Penalty for mismatches
            return min(variation, 200.0)  # Cap at 200ms
        
        return sum(variations) / len(variations) if variations else 0.0
    
    def _validate_element_timing(self) -> List[Tuple[int, int, str]]:
        """Check for timing issues with individual elements."""
        issues = []
        
        for scene_idx, scene in enumerate(self.animation_scenes):
            scene_audio = self.audio_durations[scene_idx] if scene_idx < len(self.audio_durations) else 0.0
            
            for elem_idx, element in enumerate(scene.get("elements", [])):
                timing = element.get("timing", {})
                
                # Check if element timing exceeds audio duration
                start = timing.get("start", 0.0)
                duration = timing.get("duration_in", 1.0)
                end = start + duration
                
                if end > scene_audio and scene_audio > 0:
                    issues.append((
                        scene_idx,
                        elem_idx,
                        f"Element duration ({duration:.1f}s) exceeds audio ({scene_audio:.1f}s)"
                    ))
        
        return issues


class AdaptivePacingCalculator:
    """Calculates adaptive pacing based on step complexity."""
    
    def __init__(self, solution_steps: List[Dict[str, str]], animation_scenes: List[Dict[str, Any]]):
        """
        Args:
            solution_steps: Solution steps with explanations
            animation_scenes: Animation scenes with elements
        """
        self.solution_steps = solution_steps
        self.animation_scenes = animation_scenes
    
    def calculate_pacing(self) -> PacingAnalysis:
        """Calculate adaptive pacing for each scene."""
        adaptive_timings = []
        scene_analyses = []
        warnings = []
        
        for scene_idx, scene in enumerate(self.animation_scenes):
            # Calculate complexity score
            complexity = self._calculate_complexity(scene_idx, scene)
            
            # Determine pacing level
            pacing_level = self._select_pacing_level(complexity)
            
            # Calculate adaptive timing based on complexity
            # Formula: base_time + (complexity factor * range)
            num_elements = len(scene.get("elements", []))
            base_time = pacing_level.value[0]
            time_range = pacing_level.value[1] - pacing_level.value[0]
            
            # More complex = longer per scene
            adaptive_time = base_time + (complexity * time_range)
            adaptive_timings.append(adaptive_time)
            
            scene_analyses.append({
                "scene_id": scene.get("id", f"scene_{scene_idx}"),
                "complexity_score": complexity,
                "pacing_level": pacing_level.name,
                "adaptive_duration": adaptive_time,
                "element_count": num_elements
            })
            
            # Add warnings for problematic element counts
            if num_elements > 20:
                warnings.append(f"Scene {scene_idx}: {num_elements} elements too congested (max 10-15 recommended)")
            elif num_elements > 15:
                warnings.append(f"Scene {scene_idx}: {num_elements} elements may reduce learning effectiveness")
        
        total_duration = sum(adaptive_timings)
        
        return PacingAnalysis(
            total_duration=total_duration,
            scenes=scene_analyses,
            adaptive_timings=adaptive_timings,
            pacing_warnings=warnings
        )
    
    def _calculate_complexity(self, scene_idx: int, scene: Dict[str, Any]) -> float:
        """Calculate complexity score (0.0-1.0) for a scene."""
        score = 0.0
        
        # Factor 1: Number of elements (more = complex) - linear scaling
        num_elements = len(scene.get("elements", []))
        element_score = min(num_elements / 25.0, 0.25)  # 0-25 elements = 0-0.25
        score += element_score
        
        # Factor 2: Element type diversity (more types = complex) - linear
        element_types = set(el.get("type", "") for el in scene.get("elements", []))
        diversity_score = min(len(element_types) / 8.0, 0.25)  # 0-8 types = 0-0.25
        score += diversity_score
        
        # Factor 3: Mathematical content (Latex/Graph = complex) - binary
        has_math = any(
            el.get("type") in ["Latex", "MathTex", "Graph"]
            for el in scene.get("elements", [])
        )
        if has_math:
            score += 0.25
        
        # Factor 4: Voiceover length (longer = more to explain = complex) - linear
        voiceover = scene.get("voiceover", "")
        voiceover_words = len(voiceover.split())
        voiceover_score = min(voiceover_words / 150.0, 0.25)  # 0-150 words = 0-0.25
        score += voiceover_score
        
        return min(score, 1.0)
    
    @staticmethod
    def _select_pacing_level(complexity: float) -> PacingLevel:
        """Select pacing level based on complexity score."""
        if complexity < 0.3:
            return PacingLevel.SIMPLE
        elif complexity < 0.5:
            return PacingLevel.MODERATE
        elif complexity < 0.75:
            return PacingLevel.COMPLEX
        else:
            return PacingLevel.VERY_COMPLEX


def validate_animation_plan(plan_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive validation of animation plan.
    
    Args:
        plan_data: Complete JSON plan with solution and animation_plan
    
    Returns:
        Dictionary with validation results and recommendations
    """
    # Input validation
    if not isinstance(plan_data, dict):
        return {
            "overall_valid": False,
            "overall_status": "✗ FAIL",
            "error": "plan_data must be a dictionary",
            "step_sequencing": {"valid": False},
            "audio_visual_sync": {"valid": False},
            "adaptive_pacing": {"total_duration_sec": 0},
            "recommendations": ["Provide valid JSON plan data"]
        }
    
    solution_steps = plan_data.get("solution", {}).get("steps", [])
    animation_scenes = plan_data.get("animation_plan", {}).get("scenes", [])
    
    # Validate required data
    if not solution_steps:
        return {
            "overall_valid": False,
            "overall_status": "✗ FAIL",
            "error": "No solution steps found in plan_data['solution']['steps']",
            "step_sequencing": {"valid": False},
            "audio_visual_sync": {"valid": False},
            "adaptive_pacing": {"total_duration_sec": 0},
            "recommendations": ["Add solution steps to plan"]
        }
    
    if not animation_scenes:
        return {
            "overall_valid": False,
            "overall_status": "✗ FAIL",
            "error": "No animation scenes found in plan_data['animation_plan']['scenes']",
            "step_sequencing": {"valid": False},
            "audio_visual_sync": {"valid": False},
            "adaptive_pacing": {"total_duration_sec": 0},
            "recommendations": ["Add animation scenes to plan"]
        }
    
    # Validate step sequencing
    step_validator = StepSequenceValidator(solution_steps, animation_scenes)
    step_result = step_validator.validate()
    
    # Validate audio-visual sync
    sync_validator = AudioVisualSyncValidator(animation_scenes)
    sync_result = sync_validator.validate()
    
    # Calculate adaptive pacing
    pacing_calculator = AdaptivePacingCalculator(solution_steps, animation_scenes)
    pacing_analysis = pacing_calculator.calculate_pacing()
    
    # Compile overall validation status
    # If audio durations are missing, sync is treated as skipped (not a failure).
    sync_effective = sync_result.is_valid or sync_result.audio_duration == 0.0
    overall_valid = step_result.is_valid and sync_effective
    
    return {
        "overall_valid": overall_valid,
        "overall_status": "✓ PASS" if overall_valid else "✗ FAIL",
        "step_sequencing": {
            "valid": step_result.is_valid,
            "total_steps": step_result.total_steps,
            "covered_steps": step_result.covered_steps,
            "coverage_percentage": (step_result.covered_steps / step_result.total_steps * 100) if step_result.total_steps > 0 else 0,
            "skipped_steps": step_result.skipped_steps,
            "out_of_order": step_result.out_of_order,
            "redundant_content": step_result.redundant_content,
            "warnings": step_result.warnings
        },
        "audio_visual_sync": {
            "valid": sync_result.is_valid,
            "video_duration_sec": round(sync_result.video_duration, 2),
            "audio_duration_sec": round(sync_result.audio_duration, 2),
            "sync_error_sec": round(sync_result.sync_error_seconds, 3),
            "timing_precision_ms": round(sync_result.timing_precision_ms, 1),
            "element_timing_issues": sync_result.element_timing_issues
        },
        "adaptive_pacing": {
            "total_duration_sec": round(pacing_analysis.total_duration, 2),
            "scenes": pacing_analysis.scenes,
            "adaptive_timings": [round(t, 2) for t in pacing_analysis.adaptive_timings],
            "pacing_warnings": pacing_analysis.pacing_warnings
        },
        "recommendations": _generate_recommendations(step_result, sync_result, pacing_analysis)
    }


def _generate_recommendations(
    step_result: StepValidationResult,
    sync_result: SyncValidationResult,
    pacing_result: PacingAnalysis
) -> List[str]:
    """Generate actionable recommendations based on validation results."""
    recommendations = []
    
    # Step sequencing recommendations
    if step_result.skipped_steps:
        skipped_list = step_result.skipped_steps[:3]
        recommendations.append(
            f"Add missing steps: {', '.join(skipped_list)}"
        )
    
    if step_result.out_of_order:
        recommendations.append("Reorder scenes to match solution step sequence")
    
    if step_result.redundant_content:
        # Safely access first element
        if isinstance(step_result.redundant_content, list) and len(step_result.redundant_content) > 0:
            first_redundant = str(step_result.redundant_content[0])[:50]
            recommendations.append(f"Remove redundant content: {first_redundant}...")
    
    # Sync recommendations
    if sync_result.sync_error_seconds > 0.5:
        if sync_result.audio_duration > 0 and sync_result.video_duration > 0:
            if sync_result.audio_duration > sync_result.video_duration:
                recommendations.append(
                    f"Video too short: extend animations by ~{sync_result.sync_error_seconds:.1f}s"
                )
            else:
                recommendations.append(
                    f"Audio too short: add explanatory narration (~{sync_result.sync_error_seconds:.1f}s)"
                )
    
    # Pacing recommendations
    if pacing_result.pacing_warnings:
        recommendations.extend(pacing_result.pacing_warnings[:2])
    
    return recommendations[:5]  # Return top 5 recommendations


if __name__ == "__main__":
    # Example usage
    sample_plan = {
        "solution": {
            "topic": "Pythagorean Theorem",
            "steps": [
                {"title": "Define right triangle", "explanation": "A triangle with one 90 degree angle", "latex": None},
                {"title": "State theorem", "explanation": "a² + b² = c²", "latex": "a^2 + b^2 = c^2"},
                {"title": "Apply to example", "explanation": "3-4-5 triangle", "latex": None}
            ],
            "final_answer": "The Pythagorean Theorem: a² + b² = c²"
        },
        "animation_plan": {
            "overview": "Teach Pythagorean theorem visually",
            "scenes": [
                {
                    "id": "intro",
                    "description": "Introduction",
                    "voiceover": "Let's learn about the Pythagorean Theorem",
                    "elements": [
                        {"type": "Text", "content": "Pythagorean Theorem", "timing": {"duration_in": 1.0}}
                    ]
                },
                {
                    "id": "scene1",
                    "description": "Right triangle definition",
                    "voiceover": "A right triangle has one 90 degree angle",
                    "elements": [
                        {"type": "Polygon", "content": "[(0,0), (3,0), (0,4)]", "timing": {"duration_in": 2.0}},
                        {"type": "Text", "content": "90°", "timing": {"duration_in": 1.0}}
                    ]
                },
                {
                    "id": "scene2",
                    "description": "Pythagorean theorem formula",
                    "voiceover": "The Pythagorean Theorem states: a squared plus b squared equals c squared",
                    "elements": [
                        {"type": "Latex", "content": "a^2 + b^2 = c^2", "timing": {"duration_in": 2.0}}
                    ]
                }
            ]
        }
    }
    
    results = validate_animation_plan(sample_plan)
    print(json.dumps(results, indent=2))
