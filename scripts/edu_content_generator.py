"""
Educational Content Generator — prerequisite analysis & structured section builder.

When a question is about topic A but requires knowledge from topics A and B,
this module detects the dependencies and instructs the LLM to teach *all*
prerequisite topics in a well-structured, academically rigorous format with:

  Section A — Key Concepts & Detailed Explanations
  Section B — Definitions, Derivations of the formula used in that question (short one if the question is not about derivation ) & Formula Breakdowns
  Section C — Step-by-Step Practice Problems with Solutions with detailed explanations with also steps like taking common square both side all included and clearly mentioned and also animation of cutting e.g. 1-1 like cutting 1 and -1 and -(f+x)/-f subtract symblo cutting etc like human behaviour.
Plus cross-references, summary, and additional practice exercises with keys.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

# ══════════════════════════════════════════════════════════════════════════════
# QUESTION TYPE CLASSIFIER
# ══════════════════════════════════════════════════════════════════════════════
# Detects what KIND of question the user is asking so the LLM approach
# (derivation-heavy vs conceptual vs problem-solving vs compare/contrast)
# is tailored precisely.

QUESTION_TYPE_PATTERNS: Dict[str, List[str]] = {
    "derivation": [
        r"\bderiv(e|ation|ing)\b", r"\bprov(e|ing|oof)\b",
        r"\bshow\s+that\b", r"\bfrom\s+first\s+principles?\b",
        r"\bestablish\b", r"\bdemonstrate\s+(that|how)\b",
    ],
    "conceptual": [
        r"\bwhat\s+is\b", r"\bexplain\b", r"\bdefine\b", r"\bdescribe\b",
        r"\bwhy\s+(does|is|do|are|can)\b", r"\bhow\s+does\b",
        r"\bmeaning\s+of\b", r"\bsignificance\b", r"\binterpret\b",
        r"\bwhat\s+are\b", r"\bconcept\b", r"\bunderstand\b",
        r"\bintroduc(e|tion)\b",
    ],
    "numerical_problem": [
        r"\bcalculat(e|ion)\b", r"\bfind\s+(the|a)\b", r"\bsolve\b",
        r"\bcompute\b", r"\bdetermine\b", r"\bevaluat(e|ion)\b",
        r"\b\d+\.?\d*\s*(kg|m|s|N|J|W|V|A|mol|K|Pa|Hz|rad)\b",
        r"\bgiven\s+(that|:)\b", r"\bnumerical\b",
    ],
    "comparison": [
        r"\bcompar(e|ison|ing)\b", r"\bdifferen(ce|t|tiate)\s+between\b",
        r"\bvs\.?\b", r"\bversus\b", r"\bcontrast\b",
        r"\bsimilarit(y|ies)\b", r"\brelation\s+between\b",
        r"\bhow\s+(is|are)\s+.+\s+(different|similar|related)\b",
    ],
    "application": [
        r"\bappl(y|ication|ied)\b", r"\breal[\s-]world\b",
        r"\bexample\b", r"\bpractical\b", r"\buse\s+of\b",
        r"\bengineering\b", r"\beveryday\b", r"\bin\s+practice\b",
    ],
    "graphical": [
        r"\bgraph\b", r"\bplot\b", r"\bsketch\b", r"\bdraw\b",
        r"\bdiagram\b", r"\bvisual(i[zs]e|ly)\b", r"\bcurve\b",
        r"\bgeometric(al)?\b", r"\bshape\b",
    ],
}

# For each question type, the best pedagogical approach strategy
APPROACH_STRATEGIES: Dict[str, str] = {
    "derivation": """
APPROACH STRATEGY — DERIVATION QUESTION:
This question asks for a mathematical proof or derivation. Use the following approach:
1. STATE the target result clearly upfront so the student knows WHERE the derivation is heading.
2. IDENTIFY the starting axioms, laws, or definitions used as foundation.
3. SHOW the derivation using at LEAST 2 different methods/approaches:
   • Method 1: The standard textbook approach (rigorous, step-by-step)
   • Method 2: An alternative approach (geometric, intuitive, or using a different formalism)
4. For EVERY algebraic step: explain WHY that manipulation is valid and WHAT it achieves.
5. Show intermediate results on screen while explaining the next step verbally.
6. After the derivation, CHECK the result:
   • Dimensional analysis — do the units match?
   • Limiting cases — does it reduce to known results in special cases?
   • Physical/mathematical intuition — does the result make sense?
7. Show how changing assumptions or conditions modifies the derivation.
8. Provide a "derivation map" visual showing the logical flow from assumptions to result.
""",
    "conceptual": """
APPROACH STRATEGY — CONCEPTUAL/EXPLANATORY QUESTION:
This question asks for understanding of a concept. Use the following approach:
1. START with a concrete, relatable real-world example or analogy BEFORE formal definitions.
   The student should FEEL the concept intuitively before seeing equations.
2. Give the FORMAL DEFINITION — precise, with every term explained.
3. MULTIPLE REPRESENTATIONS: Show the same concept from at least 3 angles:
   • Verbal/intuitive description with everyday language
   • Mathematical formulation with equations
   • Visual/graphical representation with diagrams and animations
4. HISTORICAL CONTEXT: Who introduced this concept? What problem were they solving?
   This gives the student a narrative to anchor the knowledge.
5. BUILD FROM SIMPLE TO COMPLEX: Start with the simplest version of the concept
   and progressively add complexity (special cases → general case).
6. ADDRESS MISCONCEPTIONS: Explicitly state what the concept is NOT.
   List 3-5 common student errors and explain why each is wrong.
7. CONNECT to related concepts — show where this fits in the bigger picture.
8. End with "So what?" — explain why this matters and where it's used.
""",
    "numerical_problem": """
APPROACH STRATEGY — NUMERICAL PROBLEM-SOLVING QUESTION:
This question requires computing a specific numerical answer. Use the following approach:
1. READ the problem aloud and IDENTIFY every given quantity with units and symbols.
   Show a visual "Given" box on screen.
2. STATE what we need to find — the "Find" box.
3. PLAN: Before touching numbers, outline the STRATEGY:
   • Which formulas/laws are needed?
   • In what ORDER should they be applied?
   • What intermediate quantities must be calculated first?
   Show a visual "Plan/Strategy Roadmap" diagram.
4. EXECUTE step-by-step: Each algebraic step gets its own explanation.
   • Substitute values WITH UNITS (not just numbers).
   • Show cancellation of units explicitly — like a human crossing out matching units.
   • Highlight the "trick" or "key insight" at each critical step.
5. VERIFY the answer using MULTIPLE CHECKS:
   • Dimensional analysis (units check)
   • Order-of-magnitude estimate (sanity check — is 10^6 reasonable?)
   • Limiting cases (if mass→0, does the answer make sense?)
   • Alternative method (solve it a second way and compare)
6. INTERPRET the result physically/mathematically — what does this number MEAN?
7. Ask "What if?" — how would the answer change if one parameter doubled?
8. COMMON ERRORS: Show the 3 most likely places a student would make a mistake
   in THIS specific problem and demonstrate each error's consequence.
""",
    "comparison": """
APPROACH STRATEGY — COMPARISON/CONTRAST QUESTION:
This question asks to compare or differentiate between concepts. Use the following approach:
1. DEFINE each concept independently first (brief but precise).
2. SIDE-BY-SIDE VISUAL TABLE: Create a comparison table with categories:
   • Definition, Formula, Units, Conditions, Physical meaning
3. SIMILARITIES FIRST: What do the concepts share? Common roots, shared variables, same domain.
4. KEY DIFFERENCES: What makes them distinct? Organize by most important to least.
5. WHEN TO USE WHICH: Give clear decision rules — "Use A when ___, use B when ___."
6. WORKED EXAMPLE: Solve the SAME scenario using both concepts to show how results differ.
7. EDGE CASES: Where do the concepts converge? Where do they diverge?
8. COMMON CONFUSION POINTS: List specific situations where students mix them up.
9. VISUAL VENN DIAGRAM or decision flowchart showing the relationship.
10. ANALOGY: Create a memorable everyday analogy that captures the difference.
""",
    "application": """
APPROACH STRATEGY — APPLICATION/REAL-WORLD QUESTION:
This question asks about practical use or real-world relevance. Use the following approach:
1. START with a compelling real-world scenario (engineering failure, scientific discovery,
   medical breakthrough) that demonstrates why the concept matters.
2. THEORY BRIDGE: Briefly recap the underlying theory (not the full derivation,
   but enough that the application makes sense).
3. MULTIPLE APPLICATIONS: Cover at least 4-5 different domains:
   • Engineering/technology • Medical/biological • Everyday life
   • Scientific research • Industry/commercial
4. For EACH application:
   • Describe the specific scenario with real numbers and data
   • Show which formulas/principles are at work
   • Explain what would go wrong without understanding this concept
5. WALK THROUGH ONE APPLICATION IN FULL DETAIL: Set up the real-world problem,
   model it mathematically, solve it, and interpret the result.
6. Show how the concept connects to cutting-edge research or modern technology.
7. Discuss LIMITATIONS — when does the theory break down in practice?
""",
    "graphical": """
APPROACH STRATEGY — GRAPHICAL/VISUAL QUESTION:
This question involves graphs, diagrams, or geometric reasoning. Use the following approach:
1. SET UP the coordinate system/axes carefully — label everything, explain the axes' physical meaning.
2. SKETCH FIRST: Start with a rough qualitative sketch, explaining the SHAPE of the curve
   before plotting precise values. Why does it curve up/down/asymptote?
3. KEY FEATURES: Identify and annotate every important feature:
   • Intercepts, maxima, minima, inflection points, asymptotes
   • Slopes at key points and what they represent physically
   • Areas under curves and what they represent
4. PARAMETER SENSITIVITY: Show how the graph changes when parameters vary.
   Animate multiple curves overlaid to show the effect.
5. CONNECT GRAPH TO EQUATION: For each feature of the graph, point to the
   corresponding term in the equation that causes it.
6. COMPARE MULTIPLE GRAPHS side by side to contrast related concepts.
7. USE COLOR CODING consistently — same concept = same color across all diagrams.
8. GEOMETRIC INTERPRETATION: If applicable, show the geometric meaning of algebraic results.
""",
}

def classify_question(question: str) -> List[Tuple[str, float]]:
    """Classify a question into one or more types with confidence scores.

    Returns a list of (question_type, score) sorted by score descending.
    A question can match multiple types (e.g. numerical + derivation).
    """
    q = question.lower().strip()
    scores: Dict[str, float] = {}

    for qtype, patterns in QUESTION_TYPE_PATTERNS.items():
        match_count = 0
        for pat in patterns:
            if re.search(pat, q):
                match_count += 1
        if match_count > 0:
            # Score is fraction of patterns matched, boosted by absolute match count
            scores[qtype] = match_count / len(patterns) + 0.1 * min(match_count, 3)

    if not scores:
        # Default: treat as conceptual (explain the topic)
        scores["conceptual"] = 0.5

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def build_approach_strategy(question: str) -> str:
    """Build a tailored approach strategy block based on question classification."""
    classifications = classify_question(question)
    if not classifications:
        return ""

    lines: List[str] = []
    lines.append("")
    lines.append("╔══════════════════════════════════════════════════════════════╗")
    lines.append("║  QUESTION CLASSIFICATION & TAILORED APPROACH                ║")
    lines.append("╚══════════════════════════════════════════════════════════════╝")
    lines.append("")

    # Report classification
    lines.append("DETECTED QUESTION TYPE(S):")
    for qtype, score in classifications:
        bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
        lines.append(f"  [{bar}] {qtype.upper().replace('_', ' ')} (confidence: {score:.2f})")
    lines.append("")

    # Primary approach strategy
    primary_type = classifications[0][0]
    strategy = APPROACH_STRATEGIES.get(primary_type, "")
    if strategy:
        lines.append(strategy.strip())
        lines.append("")

    # If question matches multiple types, add secondary guidance
    if len(classifications) > 1 and classifications[1][1] > 0.2:
        secondary_type = classifications[1][0]
        secondary_strategy = APPROACH_STRATEGIES.get(secondary_type, "")
        if secondary_strategy:
            lines.append(f"SECONDARY APPROACH (also incorporate elements of {secondary_type.upper().replace('_', ' ')}):")
            # Include a condensed version — first 4 lines of the strategy
            condensed = secondary_strategy.strip().split("\n")
            for line in condensed[1:5]:  # skip header, take 4 key lines
                lines.append(line)
            lines.append("")

    # Universal approach elements that apply to ALL question types
    lines.append("═══ UNIVERSAL APPROACH ELEMENTS (APPLY TO EVERY QUESTION) ═══")
    lines.append("Regardless of question type, ALWAYS include:")
    lines.append("  1. HOOK: Start with why this matters — a surprising fact, paradox, or real scenario")
    lines.append("  2. PREREQUISITE CHECK: Identify what the student MUST know before this topic")
    lines.append("  3. MULTIPLE REPRESENTATIONS: Show every concept verbally, mathematically, AND visually")
    lines.append("  4. STEP-BY-STEP TRANSPARENCY: Never skip steps — show EVERY algebraic manipulation")
    lines.append("     like a human would on a whiteboard (crossing out terms, factoring, etc.)")
    lines.append("  5. METACOGNITION: Explain your THINKING PROCESS — 'Why did I choose this approach?'")
    lines.append("     'What cues in the problem told me to use this formula?'")
    lines.append("  6. PATTERN RECOGNITION: Teach students to recognize WHEN to apply each technique")
    lines.append("     by contrasting with similar problems that require DIFFERENT approaches")
    lines.append("  7. ERROR AWARENESS: For every key step, mention what could go wrong and why")
    lines.append("  8. BUILDING BLOCKS: Teach from simple → complex, concrete → abstract")
    lines.append("  9. ACTIVE RECALL: Include 'pause and think' moments before revealing solutions")
    lines.append("  10. CONNECTIONS: Link to related topics the student has already learned or will learn")
    lines.append("")

    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# PREREQUISITE / TOPIC DEPENDENCY MAP
# ══════════════════════════════════════════════════════════════════════════════
# Maps a topic keyword → list of prerequisite topic keywords that must also
# be taught when that topic appears in a question.  Kept deliberately broad
# so the fuzzy matcher catches partial overlaps.

TOPIC_DEPENDENCIES: Dict[str, List[str]] = {
    # ── Physics ──────────────────────────────────────────────────────────
    "angular momentum": ["torque", "moment of inertia", "rotational motion", "newton's laws"],
    "torque": ["force", "moment arm", "rotational equilibrium"],
    "rotational motion": ["angular velocity", "angular acceleration", "moment of inertia"],
    "moment of inertia": ["mass distribution", "rotational kinetic energy"],
    "centripetal force": ["circular motion", "newton's second law", "acceleration"],
    "circular motion": ["velocity", "acceleration", "centripetal force"],
    "projectile motion": ["kinematics", "vectors", "gravity", "newton's laws"],
    "kinematics": ["displacement", "velocity", "acceleration", "equations of motion"],
    "newton's laws": ["force", "mass", "acceleration", "momentum"],
    "momentum": ["newton's laws", "impulse", "conservation laws"],
    "impulse": ["force", "momentum", "newton's second law"],
    "conservation of energy": ["kinetic energy", "potential energy", "work"],
    "work": ["force", "displacement", "energy"],
    "kinetic energy": ["mass", "velocity", "work-energy theorem"],
    "potential energy": ["conservative forces", "gravity", "height"],
    "gravitation": ["newton's law of gravitation", "gravitational field", "potential energy"],
    "simple harmonic motion": ["restoring force", "oscillation", "energy conservation", "springs"],
    "waves": ["oscillation", "frequency", "wavelength", "simple harmonic motion"],
    "sound": ["waves", "frequency", "resonance", "doppler effect"],
    "optics": ["reflection", "refraction", "snell's law", "lenses"],
    "electrostatics": ["coulomb's law", "electric field", "electric potential"],
    "electric field": ["charge", "coulomb's law", "superposition"],
    "electric potential": ["electric field", "work", "energy"],
    "capacitance": ["electric field", "charge", "energy storage"],
    "current electricity": ["ohm's law", "resistance", "circuits"],
    "ohm's law": ["voltage", "current", "resistance"],
    "magnetic field": ["current", "lorentz force", "biot-savart law"],
    "electromagnetic induction": ["magnetic flux", "faraday's law", "lenz's law"],
    "thermodynamics": ["heat", "temperature", "internal energy", "laws of thermodynamics"],
    "entropy": ["thermodynamics", "second law", "heat engines"],
    "fluid mechanics": ["pressure", "buoyancy", "bernoulli's equation", "continuity"],
    "modern physics": ["photoelectric effect", "de broglie wavelength", "bohr model"],
    "nuclear physics": ["radioactivity", "binding energy", "mass-energy equivalence"],
    "semiconductor": ["band theory", "p-n junction", "diode"],
    "relativity": ["time dilation", "length contraction", "mass-energy equivalence"],

    # ── Mathematics ──────────────────────────────────────────────────────
    "differentiation": ["limits", "continuity", "functions", "first principles"],
    "integration": ["differentiation", "antiderivatives", "area under curve"],
    "limits": ["functions", "continuity", "infinity"],
    "matrices": ["determinant", "linear equations", "vectors"],
    "determinant": ["matrices", "linear equations"],
    "vectors": ["scalars", "dot product", "cross product", "coordinate geometry"],
    "probability": ["permutation", "combination", "sample space"],
    "trigonometry": ["angles", "trigonometric ratios", "identities"],
    "quadratic equations": ["factoring", "discriminant", "roots", "polynomials"],
    "sequences and series": ["arithmetic progression", "geometric progression", "convergence"],
    "differential equations": ["differentiation", "integration", "separable equations"],
    "complex numbers": ["imaginary unit", "argand plane", "de moivre's theorem"],
    "conic sections": ["parabola", "ellipse", "hyperbola", "coordinate geometry"],
    "coordinate geometry": ["straight lines", "distance formula", "section formula"],
    "binomial theorem": ["combinations", "pascal's triangle", "expansion"],
    "statistics": ["mean", "median", "variance", "standard deviation"],

    # ── Chemistry ────────────────────────────────────────────────────────
    "chemical bonding": ["electron configuration", "valence electrons", "electronegativity"],
    "equilibrium": ["le chatelier's principle", "equilibrium constant", "reaction rates"],
    "thermochemistry": ["enthalpy", "hess's law", "bond energy"],
    "electrochemistry": ["redox reactions", "galvanic cell", "nernst equation"],
    "organic chemistry": ["functional groups", "isomerism", "nomenclature"],
    "atomic structure": ["quantum numbers", "electron configuration", "periodic trends"],
    "periodic table": ["atomic structure", "periodicity", "electron configuration"],
    "solutions": ["concentration", "molarity", "dilution", "colligative properties"],
    "acids and bases": ["ph", "buffer solutions", "neutralization"],
    "chemical kinetics": ["rate law", "order of reaction", "activation energy"],

    # ── Economics ─────────────────────────────────────────────────────────
    "supply and demand": ["equilibrium price", "elasticity", "market structure"],
    "elasticity": ["supply and demand", "price sensitivity", "revenue"],
    "gdp": ["national income", "aggregate demand", "aggregate supply"],
    "inflation": ["money supply", "interest rates", "purchasing power"],
    "monetary policy": ["central bank", "interest rates", "money supply"],
    "fiscal policy": ["government spending", "taxation", "budget deficit"],
    "international trade": ["comparative advantage", "tariffs", "exchange rates"],
    "market structure": ["perfect competition", "monopoly", "oligopoly"],
}


# ══════════════════════════════════════════════════════════════════════════════
# TOPIC DETECTION
# ══════════════════════════════════════════════════════════════════════════════

def _normalize(text: str) -> str:
    """Lowercase + collapse whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def detect_topics(question: str) -> List[str]:
    """Find all topic keywords present in the user's question."""
    q = _normalize(question)
    found: List[str] = []
    # Sort by length descending so longer phrases match first
    for topic in sorted(TOPIC_DEPENDENCIES.keys(), key=len, reverse=True):
        if topic in q:
            found.append(topic)
    return found


def resolve_prerequisites(question: str) -> Dict[str, List[str]]:
    """Detect topics in the question and resolve their prerequisite chains.

    Returns a dict mapping each detected topic → its list of prerequisites.
    Prerequisites are also recursively resolved (depth-limited to 3 levels).
    """
    detected = detect_topics(question)
    if not detected:
        # Fallback: try word-level matching against dependency keys
        q_words = set(re.findall(r"[a-z]+", question.lower()))
        for topic in TOPIC_DEPENDENCIES:
            topic_words = set(topic.split())
            if len(topic_words & q_words) >= max(1, len(topic_words) - 1):
                detected.append(topic)

    result: Dict[str, List[str]] = {}
    visited: set = set()

    def _resolve(topic: str, depth: int = 0):
        if depth > 3 or topic in visited:
            return
        visited.add(topic)
        prereqs = TOPIC_DEPENDENCIES.get(topic, [])
        result[topic] = prereqs
        for p in prereqs:
            p_lower = _normalize(p)
            if p_lower in TOPIC_DEPENDENCIES and p_lower not in visited:
                _resolve(p_lower, depth + 1)

    for t in detected:
        _resolve(t)

    return result


# ══════════════════════════════════════════════════════════════════════════════
# EDUCATIONAL PROMPT BUILDER
# ══════════════════════════════════════════════════════════════════════════════

def _derivation_instruction(topic: str, is_main_topic: bool) -> str:
    """Derivation depth instruction: long for main question, short for prereqs."""
    if is_main_topic:
        return (
            f"  • {topic.title()}: Provide a FULL, EXHAUSTIVE derivation from first principles using "
            f"at least 2 different approaches. Show every intermediate step (15-25 steps minimum), "
            f"explain each algebraic manipulation in detail, include the physical/mathematical reasoning "
            f"behind each step, discuss why alternative approaches work, and connect each step to the "
            f"bigger picture. This is the MAIN derivation — make it the most thorough treatment possible."
        )
    return (
        f"  • {topic.title()}: Provide a MODERATE derivation (5-8 key steps) showing the essential "
        f"logic with clear reasoning. State the starting point, each key manipulation with "
        f"justification, and the final result. Include physical/mathematical intuition at each step."
    )


def build_educational_prompt(user_question: str) -> str:
    """Build a structured educational prompt injection based on topic analysis.

    This prompt block is appended to the solver prompt to instruct the LLM
    to cover all prerequisite topics and structure the output educationally.
    """
    prereqs = resolve_prerequisites(user_question)

    # Collect all unique topics (detected + their prerequisites)
    all_topics: List[str] = []
    detected_topics: List[str] = list(prereqs.keys())
    prerequisite_topics: List[str] = []
    seen: set = set()
    for topic in detected_topics:
        if topic not in seen:
            all_topics.append(topic)
            seen.add(topic)
    for topic, deps in prereqs.items():
        for dep in deps:
            dep_lower = _normalize(dep)
            if dep_lower not in seen:
                all_topics.append(dep_lower)
                prerequisite_topics.append(dep_lower)
                seen.add(dep_lower)

    if not all_topics:
        # No specific topics detected — return generic educational structure
        return build_approach_strategy(user_question) + _generic_educational_prompt(user_question)

    # ── Build the structured educational prompt ──────────────────────────
    lines: List[str] = []

    # ── Tailored approach strategy based on question type ────────────────
    approach_block = build_approach_strategy(user_question)
    if approach_block:
        lines.append(approach_block)

    lines.append("")
    lines.append("╔══════════════════════════════════════════════════════════════╗")
    lines.append("║  EDUCATIONAL CONTENT STRUCTURE — MANDATORY REQUIREMENTS     ║")
    lines.append("╚══════════════════════════════════════════════════════════════╝")
    lines.append("")

    # Topic dependency notice
    lines.append("TOPIC ANALYSIS:")
    lines.append(f"  Main topic(s): {', '.join(t.title() for t in detected_topics)}")
    if prerequisite_topics:
        lines.append(f"  Prerequisite topic(s) to also teach: {', '.join(t.title() for t in prerequisite_topics)}")
        lines.append("")
        lines.append("IMPORTANT: The question requires knowledge from MULTIPLE topics.")
        lines.append("You MUST teach ALL prerequisite topics before solving the main problem.")
        lines.append("Structure the video to build understanding progressively.")
    lines.append("")

    # ── SECTION A: Key Concepts & Explanations ───────────────────────────
    lines.append("═══ SECTION A — KEY CONCEPTS & DETAILED EXPLANATIONS ═══")
    lines.append("For EACH of the following topics, create dedicated scenes that include:")
    lines.append("  - Clear, precise definition of the concept with formal and intuitive explanations")
    lines.append("  - Physical/mathematical meaning, significance, and WHY it matters")
    lines.append("  - Key equations with explanation of every symbol, units, and dimensional analysis")
    lines.append("  - At least TWO visual diagrams or illustrations per concept")
    lines.append("  - Multiple real-world examples showing the concept in action with actual data")
    lines.append("  - Historical context: who discovered it, when, and what problem it solved")
    lines.append("  - Connection to the main problem being solved")
    lines.append("  - Common misconceptions students have about this concept")
    lines.append("  - Edge cases and special conditions where the concept behaves differently")
    lines.append("  - Analogies and visual metaphors to build deep intuition")
    lines.append("")
    lines.append("Topics to cover in Section A:")
    for t in all_topics:
        lines.append(f"  ▸ {t.title()}")
    lines.append("")

    # ── SECTION B: Definitions, Derivations & Formula Breakdowns ─────────
    lines.append("═══ SECTION B — DEFINITIONS, DERIVATIONS & FORMULA BREAKDOWNS ═══")
    lines.append("Derivation strategy: LONG derivation for the main question's formula,")
    lines.append("SHORT derivations for prerequisite/supporting formulas.")
    lines.append("")
    for t in detected_topics:
        lines.append(_derivation_instruction(t, is_main_topic=True))
    for t in prerequisite_topics:
        lines.append(_derivation_instruction(t, is_main_topic=False))
    lines.append("")
    lines.append("For EACH formula/definition:")
    lines.append("  - State the formula clearly in LaTeX")
    lines.append("  - Define every variable and constant with units")
    lines.append("  - Explain when and how to apply the formula")
    lines.append("  - Show the derivation (long or short as specified above)")
    lines.append("  - Include a 'Formula Card' element summarizing it visually")
    lines.append("")

    # ── SECTION D: MCQ & Short Answer Questions ──────────────────────────
    lines.append("═══ SECTION D — MULTIPLE-CHOICE & SHORT-ANSWER QUESTIONS ═══")
    lines.append("Generate assessment questions for EACH section/topic covered:")
    lines.append("")
    lines.append("Multiple-Choice Questions (MCQs):")
    lines.append("  - Create 3-4 MCQs per topic (minimum 12 total)")
    lines.append("  - Each MCQ has 4 options (A, B, C, D)")
    lines.append("  - Include the correct answer AND detailed explanation of why each wrong option is wrong")
    lines.append("  - Mix difficulty: 1 easy, 1-2 medium, 1 hard per topic")
    lines.append("  - Common distractors should test typical misconceptions and calculation errors")
    lines.append("")
    lines.append("Short-Answer Questions:")
    lines.append("  - Create 2-3 short-answer questions per topic (minimum 8 total)")
    lines.append("  - Require detailed, precise written responses")
    lines.append("  - Include comprehensive model answers (3-5 sentences each)")
    lines.append("")
    lines.append("Present each question in its own scene with visual elements,")
    lines.append("then reveal the answer in the following scene.")
    lines.append("")

    # ── SECTION E: Step-by-Step Practice Problems ────────────────────────
    lines.append("═══ SECTION E — STEP-BY-STEP PRACTICE PROBLEMS WITH SOLUTIONS ═══")
    lines.append("Create practice problems that test understanding of the concepts:")
    lines.append("")
    lines.append("  - Minimum 5 practice problems of increasing difficulty")
    lines.append("  - For EACH problem:")
    lines.append("    1. State the problem clearly with all necessary information")
    lines.append("    2. Identify which concepts/formulas are needed")
    lines.append("    3. Show the COMPLETE step-by-step solution with every algebraic step")
    lines.append("    4. Highlight key steps and explain the reasoning behind each one")
    lines.append("    5. State the final answer with units")
    lines.append("    6. Verify the answer (dimensional analysis or sanity check)")
    lines.append("    7. Discuss what would change if a parameter were different")
    lines.append("")
    lines.append("  Problem difficulty distribution:")
    lines.append("    Problem 1: Direct application (1-2 concepts)")
    lines.append("    Problem 2: Multi-step (2-3 concepts combined)")
    lines.append("    Problem 3: Advanced/challenge (cross-topic integration)")
    lines.append("    Problem 4: Reverse problem (given answer, find input)")
    lines.append("    Problem 5: Real-world application (messy numbers, real data)")
    lines.append("")

    # ── Cross-References ─────────────────────────────────────────────────
    lines.append("═══ CROSS-REFERENCES — CONNECTING CONCEPTS ACROSS SECTIONS ═══")
    lines.append("Throughout the video, explicitly connect related concepts:")
    lines.append("")
    for topic, deps in prereqs.items():
        if deps:
            dep_str = ", ".join(d.title() for d in deps[:4])
            lines.append(f"  ▸ {topic.title()} ←→ {dep_str}")
    lines.append("")
    lines.append("In each scene, note when a concept from one section applies to another.")
    lines.append("Use callout elements like: 'Recall from Section A: [concept]'")
    lines.append("Show visual arrows or highlights connecting related formulas.")
    lines.append("")

    # ── Summary ──────────────────────────────────────────────────────────
    lines.append("═══ SUMMARY — SECTION-BY-SECTION HIGHLIGHTS ═══")
    lines.append("Create a comprehensive summary section with:")
    lines.append("  - Key takeaway from each section (A, B, D, E)")
    lines.append("  - The most important formula and when to use it")
    lines.append("  - Common pitfalls and how to avoid them (at least 5)")
    lines.append("  - A visual 'Concept Map' showing how all topics connect")
    lines.append("  - 5-8 exam tips specific to this topic area")
    lines.append("  - Memory aids and mnemonics for key formulas")
    lines.append("  - Quick-reference formula card with all formulas covered")
    lines.append("")

    # ── Additional Practice with Answer Keys ─────────────────────────────
    lines.append("═══ ADDITIONAL PRACTICE EXERCISES WITH ANSWER KEYS ═══")
    lines.append("At the end, include 5-8 EXTRA practice exercises:")
    lines.append("  - State each problem clearly (own scene)")
    lines.append("  - Provide the answer key in a subsequent scene")
    lines.append("  - Answers should include: final value, units, key formula used, and a 2-line explanation")
    lines.append("  - These are for self-study — student should pause and try before revealing")
    lines.append("  - Add a 'PAUSE HERE and try this yourself' callout before each answer")
    lines.append("  - Include at least 2 challenge-level problems that combine multiple concepts")
    lines.append("")

    # ── Scene Ordering Guidance ──────────────────────────────────────────
    lines.append("═══ SCENE ORDERING FOR EDUCATIONAL SECTIONS ═══")
    lines.append("Organize scenes in this order:")
    lines.append("  1. Hook / real-world opener")
    lines.append("  2. Section A scenes: Prerequisite concepts first, then main topic concepts")
    lines.append("  3. Section B scenes: Short derivations for prereqs, then LONG main derivation")
    lines.append("  4. Main problem solve (full step-by-step)")
    lines.append("  5. Section D scenes: MCQs and short-answer questions with reveals")
    lines.append("  6. Section E scenes: Practice problems with step-by-step solutions")
    lines.append("  7. Cross-reference / concept map scene")
    lines.append("  8. Summary scenes (section-by-section highlights)")
    lines.append("  9. Additional practice exercises with answer keys")
    lines.append("  10. Conclusion and next steps")
    lines.append("")

    return "\n".join(lines)


def _generic_educational_prompt(user_question: str) -> str:
    """Fallback when no specific topics detected — still require educational structure."""
    return """
╔══════════════════════════════════════════════════════════════╗
║  EDUCATIONAL CONTENT STRUCTURE — MANDATORY REQUIREMENTS     ║
╚══════════════════════════════════════════════════════════════╝

IMPORTANT: Structure the video with ALL of the following educational sections: 
these are the quesstions type asked so the steps are classified ;

═══ SECTION A — KEY CONCEPTS & DETAILED EXPLANATIONS ═══
- Identify ALL prerequisite topics the student needs to understand
- Teach each prerequisite before tackling the main question
- Include clear definitions, multiple diagrams, real-world examples with actual data
- Add historical context, common misconceptions, and edge cases for each concept
- Provide analogies and visual metaphors to build deep intuition

═══ SECTION B — DEFINITIONS, DERIVATIONS & FORMULA BREAKDOWNS ═══
- For the MAIN formula: provide an EXHAUSTIVE derivation using 2+ approaches (15-25 steps minimum)
- For supporting formulas: provide MODERATE derivations (5-8 key steps)
- Define every variable with units; explain when to apply each formula
- Include dimensional analysis verification for each formula

═══ SECTION D — MULTIPLE-CHOICE & SHORT-ANSWER QUESTIONS ═══
- Generate 12+ MCQs across all topics (4 options each, with answers + detailed explanations for ALL options)
- Generate 8+ short-answer questions with comprehensive model answers (3-5 sentences each)
- Mix difficulty levels (easy, medium, hard)

═══ SECTION E — STEP-BY-STEP PRACTICE PROBLEMS WITH SOLUTIONS ═══
- Minimum 5 practice problems of increasing difficulty
- Complete step-by-step solutions with reasoning at each step
- Final answers with units, verification, and sensitivity discussion
- Include reverse problems and real-world application problems

═══ CROSS-REFERENCES ═══
- Explicitly connect concepts across sections
- Use callouts like "Recall from Section A: [concept]"
- Show a visual concept map linking all related ideas

═══ SUMMARY ═══
- Key takeaway from each section (A, B, D, E)
- Most important formula and when to use it
- 5+ common pitfalls and exam tips
- Memory aids and mnemonics for key formulas
- Quick-reference formula card

═══ ADDITIONAL PRACTICE EXERCISES WITH ANSWER KEYS ═══
- 5-8 extra problems for self-study of varying difficulty
- Include "PAUSE and try this yourself" callouts
- Provide answer keys with detailed explanations
- At least 2 challenge-level problems combining multiple concepts
"""


# ══════════════════════════════════════════════════════════════════════════════
# CLI — standalone testing
# ══════════════════════════════════════════════════════════════════════════════

def main():
    import sys
    question = " ".join(sys.argv[1:]) or "Derive the expression for centripetal acceleration and solve a problem involving circular motion"
    print(f"Question: {question}\n")

    # Show question classification
    classifications = classify_question(question)
    print("Question Classification:")
    for qtype, score in classifications:
        bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
        print(f"  [{bar}] {qtype.upper().replace('_', ' ')} ({score:.2f})")
    print()

    prereqs = resolve_prerequisites(question)
    if prereqs:
        print("Detected topics & prerequisites:")
        for topic, deps in prereqs.items():
            print(f"  {topic.title()} → {', '.join(d.title() for d in deps) if deps else '(no prerequisites)'}")
    else:
        print("No specific topics detected (will use generic educational structure)")

    prompt = build_educational_prompt(question)
    print(f"\n{'='*70}")
    print(f"Educational prompt ({len(prompt)} chars):")
    print(f"{'='*70}")
    print(prompt)


if __name__ == "__main__":
    main()
