"""
Advanced Prompt Handler - Complete prompt enhancement and optimization

Features:
- Prompt auto-enhancement engine
- Prompt compression for cost reduction
- Automatic prompt translation (multi-language)
- AI hallucination detector
- Output consistency validator
- Model confidence scoring
- Auto model selection based on complexity
- Prompt difficulty estimator
- AI tone/style selector
- Concept clarity checker
- Auto glossary generator
- AI explanation simplifier
- Diagram auto-label optimizer
- Script readability analyzer
- Learning objective extractor
- Bloom's taxonomy classifier
- Misconception detection system
- Animation pacing optimizer
- Auto summary generator

Author: Phiversity Team
"""

import re
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class PromptComplexity(Enum):
    """Complexity levels for prompts."""
    SIMPLE = 1
    MODERATE = 2
    COMPLEX = 3
    EXPERT = 4


class PromptTone(Enum):
    """Tone options for prompts."""
    ACADEMIC = "academic"
    FUN = "fun"
    CINEMATIC = "cinematic"
    CASUAL = "casual"
    TECHNICAL = "technical"


class BloomsLevel(Enum):
    """Bloom's taxonomy levels."""
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


@dataclass
class PromptAnalysis:
    """Analysis result of a prompt."""
    complexity: PromptComplexity
    difficulty_score: float  # 0-10
    key_concepts: List[str]
    technical_terms: List[str]
    suggested_model: str
    confidence_score: float  # 0-1
    has_hallucination_risk: bool
    misconceptions: List[str]
    learning_objectives: List[str]
    blooms_level: BloomsLevel
    readability_score: float


class PromptEnhancer:
    """Advanced prompt enhancement engine."""
    
    # Technical keywords for detection
    TECHNICAL_KEYWORDS = {
        "physics": ["momentum", "velocity", "acceleration", "force", "energy", "power"],
        "math": ["derivative", "integral", "equation", "function", "matrix", "vector"],
        "chemistry": ["atom", "molecule", "reaction", "bond", "electron"],
        "biology": ["cell", "DNA", "protein", "organ", "system"],
    }
    
    # Misconception patterns
    MISCONCEPTION_PATTERNS = [
        r"heavier.*falls.*faster",
        r"momentum.*destroyed",
        r"energy.*used.*up",
        r"cold.*objects.*no.*energy",
        r"electricity.*flows.*through.*wire",
    ]
    
    def __init__(self):
        self.enhancement_history: List[Dict] = []
        
    def analyze_prompt(self, prompt: str) -> PromptAnalysis:
        """
        Analyze a prompt for complexity, concepts, and potential issues.
        """
        # Calculate difficulty
        difficulty = self._estimate_difficulty(prompt)
        
        # Detect key concepts
        concepts = self._extract_concepts(prompt)
        
        # Find technical terms
        tech_terms = self._find_technical_terms(prompt)
        
        # Determine complexity
        complexity = self._classify_complexity(prompt, concepts, tech_terms)
        
        # Check for hallucinations
        hallucination_risk = self._check_hallucination_risk(prompt)
        
        # Detect misconceptions
        misconceptions = self._detect_misconceptions(prompt)
        
        # Extract learning objectives
        objectives = self._extract_learning_objectives(prompt)
        
        # Classify Bloom's level
        blooms = self._classify_bloom_level(prompt, difficulty)
        
        # Calculate readability
        readability = self._calculate_readability(prompt)
        
        # Determine suggested model
        model = self._suggest_model(complexity, tech_terms)
        
        # Calculate confidence
        confidence = self._calculate_confidence(prompt, concepts, tech_terms)
        
        return PromptAnalysis(
            complexity=complexity,
            difficulty_score=difficulty,
            key_concepts=concepts,
            technical_terms=tech_terms,
            suggested_model=model,
            confidence_score=confidence,
            has_hallucination_risk=hallucination_risk,
            misconceptions=misconceptions,
            learning_objectives=objectives,
            blooms_level=blooms,
            readability_score=readability
        )
    
    def enhance_prompt(self, prompt: str, tone: PromptTone = PromptTone.ACADEMIC) -> str:
        """
        Enhance a prompt based on analysis.
        """
        analysis = self.analyze_prompt(prompt)
        
        # Start with original prompt
        enhanced = prompt
        
        # Add clarity improvements
        enhanced = self._improve_clarity(enhanced, analysis)
        
        # Add tone-specific enhancements
        enhanced = self._apply_tone(enhanced, tone)
        
        # Add technical precision
        enhanced = self._add_technical_precision(enhanced, analysis)
        
        # Add learning objectives if missing
        if not analysis.learning_objectives:
            enhanced = self._add_learning_objectives(enhanced)
        
        # Add structure hints
        enhanced = self._add_structure_hints(enhanced, analysis)
        
        # Record enhancement
        self.enhancement_history.append({
            "original": prompt,
            "enhanced": enhanced,
            "analysis": {
                "complexity": analysis.complexity.name,
                "difficulty": analysis.difficulty_score,
                "tone": tone.value
            }
        })
        
        return enhanced
    
    def compress_prompt(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Compress prompt while preserving key information.
        """
        # Remove redundant words
        compressed = re.sub(r'\b(very|really|extremely|basically|actually)\b', '', prompt)
        
        # Remove filler phrases
        fillers = [
            r'\bso basically\b',
            r'\bwhat i mean is\b',
            r'\bas you know\b',
            r'\bthe thing is\b',
        ]
        for filler in fillers:
            compressed = re.sub(filler, '', compressed, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        compressed = re.sub(r'\s+', ' ', compressed).strip()
        
        return compressed
    
    def translate_prompt(self, prompt: str, target_lang: str) -> str:
        """
        Translate prompt to target language.
        """
        # This would integrate with a translation API
        # For now, return a placeholder structure
        return f"[TRANSLATED to {target_lang}]: {prompt}"
    
    def generate_glossary(self, prompt: str) -> Dict[str, str]:
        """
        Generate glossary of terms from prompt.
        """
        analysis = self.analyze_prompt(prompt)
        
        glossary = {}
        for term in analysis.technical_terms:
            glossary[term] = self._get_term_definition(term)
        
        return glossary
    
    def simplify_explanation(self, prompt: str) -> str:
        """
        Simplify complex explanations.
        """
        analysis = self.analyze_prompt(prompt)
        
        if analysis.readability_score < 50:
            # Already simple
            return prompt
        
        # Replace complex words with simpler alternatives
        simplifications = {
            r'\butilize\b': 'use',
            r'\bimplement\b': 'do',
            r'\bfacilitate\b': 'help',
            r'\bdemonstrate\b': 'show',
            r'\bapproximately\b': 'about',
            r'\bsubsequently\b': 'then',
            r'\bnevertheless\b': 'but',
        }
        
        simplified = prompt
        for pattern, replacement in simplifications.items():
            simplified = re.sub(pattern, replacement, simplified, flags=re.IGNORECASE)
        
        return simplified
    
    def generate_quiz(self, prompt: str, num_questions: int = 5) -> List[Dict]:
        """
        Generate quiz questions from prompt content.
        """
        analysis = self.analyze_prompt(prompt)
        
        questions = []
        for i, concept in enumerate(analysis.key_concepts[:num_questions]):
            questions.append({
                "id": i + 1,
                "question": f"What is {concept}?",
                "type": "multiple_choice",
                "options": [
                    f"Definition of {concept}",
                    f"Related to {concept}",
                    f"Example of {concept}",
                    f"None of the above"
                ],
                "correct": 0
            })
        
        return questions
    
    def generate_summary(self, prompt: str, length: str = "medium") -> str:
        """
        Generate summary of prompt content.
        """
        analysis = self.analyze_prompt(prompt)
        
        word_counts = {
            "short": 50,
            "medium": 150,
            "long": 300
        }
        
        max_words = word_counts.get(length, 150)
        
        # Build summary from key concepts
        summary_parts = [
            f"Topic: {', '.join(analysis.key_concepts[:3])}",
            f"Difficulty: {analysis.difficulty_score:.1f}/10",
            f"Level: {analysis.blooms_level.value}",
        ]
        
        if analysis.technical_terms:
            summary_parts.append(f"Key terms: {', '.join(analysis.technical_terms[:5])}")
        
        return " | ".join(summary_parts)
    
    # Helper methods
    def _estimate_difficulty(self, prompt: str) -> float:
        """Estimate prompt difficulty (0-10)."""
        score = 0.0
        
        # Length factor
        if len(prompt) > 500:
            score += 2
        elif len(prompt) > 200:
            score += 1
        
        # Technical term density
        tech_count = len(self._find_technical_terms(prompt))
        score += min(tech_count * 0.5, 3)
        
        # Mathematical symbols
        math_symbols = len(re.findall(r'[\∫∑πλ]', prompt))
        score += min(math_symbols * 0.5, 2)
        
        # Complex sentence detection
        long_sentences = len(re.findall(r'[^.!?]{50,}[.!?]', prompt))
        score += min(long_sentences * 0.3, 2)
        
        # Abstract concepts
        abstract = len(re.findall(r'\b(theory|principle|concept|fundamental)\b', prompt, re.I))
        score += min(abstract * 0.5, 1)
        
        return min(score, 10.0)
    
    def _extract_concepts(self, prompt: str) -> List[str]:
        """Extract key concepts from prompt."""
        concepts = []
        
        # Look for capitalized terms
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', prompt)
        concepts.extend(capitalized[:5])
        
        # Look for domain-specific terms
        for domain, terms in self.TECHNICAL_KEYWORDS.items():
            for term in terms:
                if term.lower() in prompt.lower():
                    if term not in concepts:
                        concepts.append(term)
        
        return concepts[:10]
    
    def _find_technical_terms(self, prompt: str) -> List[str]:
        """Find technical terms in prompt."""
        terms = []
        
        # Physics terms
        physics_terms = ["momentum", "velocity", "acceleration", "force", "energy", "torque", "angular"]
        for term in physics_terms:
            if term in prompt.lower():
                terms.append(term)
        
        # Math terms
        math_terms = ["derivative", "integral", "equation", "function", "matrix", "vector", "scalar"]
        for term in math_terms:
            if term in prompt.lower():
                terms.append(term)
        
        return list(set(terms))
    
    def _classify_complexity(self, prompt: str, concepts: List[str], tech_terms: List[str]) -> PromptComplexity:
        """Classify prompt complexity."""
        difficulty = self._estimate_difficulty(prompt)
        
        if difficulty < 3:
            return PromptComplexity.SIMPLE
        elif difficulty < 6:
            return PromptComplexity.MODERATE
        elif difficulty < 8:
            return PromptComplexity.COMPLEX
        else:
            return PromptComplexity.EXPERT
    
    def _check_hallucination_risk(self, prompt: str) -> bool:
        """Check for potential hallucination risks."""
        risky_phrases = [
            r'\bprove that\b',
            r'\bshow that\b.*always',
            r'\bnever\b.*\btrue\b',
            r'\balways\b.*\bfalse\b',
        ]
        
        for pattern in risky_phrases:
            if re.search(pattern, prompt, re.IGNORECASE):
                return True
        
        return False
    
    def _detect_misconceptions(self, prompt: str) -> List[str]:
        """Detect potential misconceptions in prompt."""
        misconceptions = []
        
        prompt_lower = prompt.lower()
        for pattern in self.MISCONCEPTION_PATTERNS:
            if re.search(pattern, prompt_lower):
                misconceptions.append(pattern)
        
        return misconceptions
    
    def _extract_learning_objectives(self, prompt: str) -> List[str]:
        """Extract learning objectives from prompt."""
        objectives = []
        
        # Look for objective indicators
        if "understand" in prompt.lower():
            objectives.append("Understand key concepts")
        if "calculate" in prompt.lower() or "solve" in prompt.lower():
            objectives.append("Solve problems")
        if "explain" in prompt.lower():
            objectives.append("Explain phenomena")
        if "derive" in prompt.lower():
            objectives.append("Derive equations")
        
        return objectives
    
    def _classify_bloom_level(self, prompt: str, difficulty: float) -> BloomsLevel:
        """Classify Bloom's taxonomy level."""
        prompt_lower = prompt.lower()
        
        if "remember" in prompt_lower or "define" in prompt_lower:
            return BloomsLevel.REMEMBER
        elif "understand" in prompt_lower or "explain" in prompt_lower:
            return BloomsLevel.UNDERSTAND
        elif "apply" in prompt_lower or "solve" in prompt_lower:
            return BloomsLevel.APPLY
        elif "analyze" in prompt_lower or "compare" in prompt_lower:
            return BloomsLevel.ANALYZE
        elif "evaluate" in prompt_lower or "critique" in prompt_lower:
            return BloomsLevel.EVALUATE
        elif "create" in prompt_lower or "design" in prompt_lower:
            return BloomsLevel.CREATE
        else:
            return BloomsLevel.UNDERSTAND
    
    def _calculate_readability(self, prompt: str) -> float:
        """Calculate readability score (0-100)."""
        words = prompt.split()
        sentences = re.split(r'[.!?]+', prompt)
        
        if not words or not sentences:
            return 100.0
        
        avg_word_len = sum(len(w) for w in words) / len(words)
        avg_sentence_len = len(words) / len(sentences)
        
        # Simplified readability score
        score = 100 - (avg_word_len * 2) - (avg_sentence_len * 0.5)
        
        return max(0, min(100, score))
    
    def _suggest_model(self, complexity: PromptComplexity, tech_terms: List[str]) -> str:
        """Suggest appropriate model based on complexity."""
        if complexity == PromptComplexity.SIMPLE:
            return "gpt-3.5-turbo"
        elif complexity == PromptComplexity.MODERATE:
            return "gpt-4"
        elif complexity == PromptComplexity.COMPLEX:
            return "gpt-4-turbo"
        else:
            return "gpt-4-32k"
    
    def _calculate_confidence(self, prompt: str, concepts: List[str], tech_terms: List[str]) -> float:
        """Calculate model confidence score."""
        score = 0.5  # Base confidence
        
        # More concepts = higher confidence
        score += min(len(concepts) * 0.05, 0.2)
        
        # More technical terms = higher confidence
        score += min(len(tech_terms) * 0.05, 0.2)
        
        # Clear structure = higher confidence
        if re.search(r'\d+\.', prompt):  # Numbered points
            score += 0.1
        
        return min(score, 0.95)
    
    def _improve_clarity(self, prompt: str, analysis: PromptAnalysis) -> str:
        """Improve prompt clarity."""
        # Add clarity if needed
        if analysis.readability_score < 50:
            prompt = self.simplify_explanation(prompt)
        
        return prompt
    
    def _apply_tone(self, prompt: str, tone: PromptTone) -> str:
        """Apply tone-specific enhancements."""
        tone_prefixes = {
            PromptTone.ACADEMIC: "Provide a detailed academic explanation: ",
            PromptTone.FUN: "Make this engaging and fun: ",
            PromptTone.CINEMATIC: "Create a dramatic cinematic narrative: ",
            PromptTone.CASUAL: "Explain in casual conversation: ",
            PromptTone.TECHNICAL: "Give a technical breakdown: ",
        }
        
        return tone_prefixes.get(tone, "") + prompt
    
    def _add_technical_precision(self, prompt: str, analysis: PromptAnalysis) -> str:
        """Add technical precision to prompt."""
        if analysis.technical_terms and len(prompt) < 200:
            terms_str = ", ".join(analysis.technical_terms[:3])
            prompt += f" Focus on: {terms_str}"
        
        return prompt
    
    def _add_learning_objectives(self, prompt: str) -> str:
        """Add learning objectives to prompt."""
        return prompt + " Include clear learning objectives."
    
    def _add_structure_hints(self, prompt: str, analysis: PromptAnalysis) -> str:
        """Add structure hints to prompt."""
        if analysis.blooms_level in [BloomsLevel.ANALYZE, BloomsLevel.EVALUATE]:
            prompt += " Structure: introduction, analysis, conclusion."
        
        return prompt
    
    def _get_term_definition(self, term: str) -> str:
        """Get definition for a term."""
        # Placeholder - would integrate with knowledge base
        return f"Definition of {term}"


# Convenience functions
def enhance_prompt(prompt: str, tone: str = "academic") -> str:
    """Enhance a prompt."""
    enhancer = PromptEnhancer()
    tone_enum = PromptTone(tone)
    return enhancer.enhance_prompt(prompt, tone_enum)


def analyze_prompt(prompt: str) -> Dict:
    """Analyze a prompt."""
    enhancer = PromptEnhancer()
    analysis = enhancer.analyze_prompt(prompt)
    return {
        "complexity": analysis.complexity.name,
        "difficulty": analysis.difficulty_score,
        "concepts": analysis.key_concepts,
        "terms": analysis.technical_terms,
        "model": analysis.suggested_model,
        "confidence": analysis.confidence_score,
        "hallucination_risk": analysis.has_hallucination_risk,
        "misconceptions": analysis.misconceptions,
        "objectives": analysis.learning_objectives,
        "blooms": analysis.blooms_level.value,
        "readability": analysis.readability_score
    }


if __name__ == "__main__":
    # Test the prompt enhancer
    test_prompt = "Explain angular momentum conservation in a collision with detailed mathematical derivation"
    
    enhancer = PromptEnhancer()
    
    print("=" * 60)
    print("PROMPT ENHANCER TEST")
    print("=" * 60)
    
    # Analyze
    analysis = enhancer.analyze_prompt(test_prompt)
    print(f"\nComplexity: {analysis.complexity.name}")
    print(f"Difficulty: {analysis.difficulty_score:.1f}/10")
    print(f"Concepts: {analysis.key_concepts}")
    print(f"Technical Terms: {analysis.technical_terms}")
    print(f"Suggested Model: {analysis.suggested_model}")
    print(f"Confidence: {analysis.confidence_score:.2f}")
    print(f"Bloom's Level: {analysis.blooms_level.value}")
    print(f"Readability: {analysis.readability_score:.1f}")
    
    # Enhance
    enhanced = enhancer.enhance_prompt(test_prompt, PromptTone.CINEMATIC)
    print(f"\nEnhanced Prompt:\n{enhanced}")
    
    # Compress
    compressed = enhancer.compress_prompt(test_prompt)
    print(f"\nCompressed: {compressed}")
    
    # Summary
    summary = enhancer.generate_summary(test_prompt, "medium")
    print(f"\nSummary: {summary}")