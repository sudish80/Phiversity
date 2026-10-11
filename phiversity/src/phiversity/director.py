"""The director: content-aware visual planning for lecture scenes.

The director decides WHEN each visual effect is used, WHERE it applies,
WHY it helps, and HOW it should appear. It provides:

  - VISUAL_PLAN_SCHEMA   the per-scene visual plan the planner fills in
  - EFFECT_PLAYBOOK      the WHEN/WHERE/HOW/WHY reference the coder follows
  - SELECTION_RULES      the rules that decide which effects are warranted
  - normalize_visual_plan()   validate + default a plan coming from the LLM
  - suggest_transition()      heuristic junction type between two scenes
  - transition_howto()         concrete realization instructions per type
  - verify_effects()           static check that planned effects exist in code
  - XFADE_MAP                 junction types realized as ffmpeg crossfades

Plans are data: the LLM planner produces them from the lesson content, the
coder prompt turns them into Manim code, and the pipeline verifies the code
against them. Nothing here is hardwired to a specific lesson.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Scene plan schema (what the planner may specify per scene)
# ---------------------------------------------------------------------------

VISUAL_PLAN_SCHEMA = """\
Each lecture segment must also carry a "visual" plan object with these fields
(all optional except "objective"; omit anything that does not apply - never
invent effects the lesson does not need):
  "objective":        one sentence - what this scene should teach visually
  "transition":       how this scene is entered from the previous one:
                      "carry-over" (continue the same objects in place),
                      "slide-up" (the question moves to the top and the work
                      begins below it), "answer-reveal" (clear the working,
                      frame the final result), "fade" | "wipe" | "dissolve"
                      (a new, unrelated topic begins), "none" (plain cut)
  "preset":           visual theme for the whole lecture: "math", "lab",
                      "spatial" (3D/molecular), "data", or "paper" (light)
  "visual_elements":  what appears: e.g. ["equation", "trajectory", "graph"]
  "diagram":          diagram to build progressively, one of: "free-body",
                      "circuit", "ray", "graph", "apparatus", "process",
                      "geometry", or "none"
  "camera_movement":  "static" | "pan" | "track" | "orbit"
  "camera_target":    what the camera moves toward / follows
  "zoom_target":      small detail the learner must inspect (term, intercept,
                      bond, cross-section...), or omit for no zoom
  "highlight":        list of elements to highlight in narration order,
                      e.g. ["coefficient a", "the discriminant"]
  "dynamic":          list of live relationships that must stay mathematically
                      connected while animating, e.g. ["secant follows both
                      points", "resultant updates as the angle changes"]
  "three_d":          true only when depth, spatial structure, surfaces or
                      volumes are essential to the explanation
  "labels":           short labels the scene needs
  "animation_beats":  ordered list pairing each narration phrase with its
                      visual action, e.g. ["write equation", "highlight b",
                      "zoom to discriminant"]
  "color_roles":      mapping of scene objects to semantic color roles,
                      e.g. {"curve": "graph_function", "secant": "graph_secant"}
  "layout":           placement constraint, e.g. "equation top, graph right"
  "outcome":          what the learner should realize from the scene"""

# ---------------------------------------------------------------------------
# Effect playbook: the WHEN / WHERE / HOW / WHY the coder must follow
# ---------------------------------------------------------------------------

EFFECT_PLAYBOOK = """\
VISUAL EFFECT PLAYBOOK - apply an effect only when its purpose is clear.

TRANSITIONS (how this scene is entered from the previous one):
- "slide-up" (question -> its solution): open with the question already
  moved to the top of the frame (smaller), then write the first equation or
  setup below it. The question card scene ends by moving its text to the
  top, so the cut reads as one continuous motion.
- "carry-over" (same objects, next step / equation -> equivalent form /
  diagram -> animated model / 2D -> 3D): re-open with the key object from
  the previous scene already on screen in the same place, then continue.
  For derivations, transform expressions IN PLACE with TransformMatchingTex
  or ReplacementTransform - keep unchanged terms stationary and animate only
  the terms that change. For equation -> graph, move the equation aside,
  create the axes, then draw the curve, keeping a shared variable visible.
- "answer-reveal" (multi-step solution concludes): FadeOut the surrounding
  working, box the final result with SurroundingRectangle, and give it a
  short emphasis (Indicate/Flash) - the result must look different from
  the intermediate steps.
- "fade"/"wipe"/"dissolve" (unrelated new topic): start the scene with a
  clear heading and a calm establishing visual; the video pipeline adds the
  actual crossfade between the clips.
- comparisons: arrange both concepts side by side (VGroup.arrange) and
  reveal features in narration order, aligned so differences line up.

CAMERA MOVEMENT (use class SegmentN(MovingCameraScene)):
- "pan": self.camera.frame.animate.move_to(target) when the discussed term
  lies outside the current view; keep surrounding context visible - frame
  width stays between 8 and 20 units.
- "track": while an object moves (a projectile, a cart), animate
  self.camera.frame.animate.move_to(obj.get_center()) together with the
  object's own animation so it stays in view along with its vectors.
- After any zoom or pan, return to a full framing when the narration moves
  on (self.camera.frame.animate.set(width=14.2).move_to(ORIGIN)).

ZOOMING (MovingCameraScene or ThreeDScene):
- zoom toward the detail under discussion:
  self.camera.frame.animate.set(width=4.5).move_to(detail) - keep enough
  context to see where the detail belongs. In 3D use
  self.move_camera(zoom=1.6, run_time=...).
- always zoom back out (or pan back) once the detail has been explained.

VISUAL HIGHLIGHTING (in narration order):
- symbols/terms as they are explained: Indicate(mobj) or Circumscribe(...)
- focus on one element: FocusOn(point), then reveal its meaning nearby
- substitution: write the formula, TransformMatchingTex the variable into
  its value, then emphasize the resulting expression
- cancellation: highlight both terms (set_color), animate them away, and
  keep the remaining expression intact
- final result: SurroundingRectangle + brief Indicate/Flash + visible units
- graph features: Dot at the intercept/extremum + short label with its
  coordinates

THREE-DIMENSIONAL SCENES (only when depth genuinely matters; use
class SegmentN(ThreeDScene)):
- build the model from Sphere / Line3D / Cube / Surface / ThreeDAxes
- establish the shape: self.set_camera_orientation(phi=75*DEGREES,
  theta=-45*DEGREES), then self.begin_ambient_camera_rotation(rate=0.12)
  for a few seconds, then stop_ambient_camera_rotation()
- zoom with self.move_camera(zoom=..., ...) and orbit with
  self.move_camera(theta=..., run_time=...)
- labels: self.add_fixed_orientation_mobjects(MathTex(...)) for
  in-scene labels, self.add_fixed_in_frame_mobjects(Text(...)) for screen
  captions/titles

DIAGRAM GENERATION (build progressively as narration introduces parts):
- draw the main object first, then add arrows/labels/components one at a
  time in narration order - never dump every element at once
- circuits: components from Rectangle/Circle/Line, current path highlighted
  as discussed; ray diagrams: elements first, then animated rays
- process diagrams: reveal stages in order, connect with arrows, highlight
  the current stage

CONTINUOUS MATHEMATICAL TRANSFORMATIONS (concepts evolve, not slide):
- transform expressions IN PLACE with TransformMatchingTex /
  ReplacementTransform so unchanged terms stay put; build the target with
  the same MathTex substring structure so corresponding pieces morph into
  each other and keep their colors.
- connect representations: an equation can become a graph (move the
  equation aside, create axes, draw its curve), a shape, or a vector - keep
  one shared element visible across the morph so the identity is obvious.
- show parameter dependence with ValueTracker: animate the tracker and let
  the curve/shape/vector update, rather than redrawing.
- abstract quantity -> concrete object: morph the symbol into the drawing
  it represents (e.g. the area under the curve filling in).

DYNAMIC GEOMETRY - LIVE OBJECTS (use the kit; require MovingCameraScene
only for the camera helpers, the geometry helpers work in any Scene):
- a point that moves along a curve: graph_point(axes, f, tracker)
- a secant that stays attached to two tracked points:
  secant_line(axes, f, x0_tracker, x1_tracker)
- a tangent computed from the real derivative:
  tangent_line(axes, f, x_tracker)
- anything else: ValueTracker(...) + mobj.add_updater(...) computing the
  object from the tracker with actual math (never approximate visually).
- animate a tracker with: self.play(tracker.animate.set_value(new), ...)
- remember to remove updaters (mobj.clear_updaters()) when the
  relationship ends, or the object will keep moving.

MULTI-SCALE EXPLANATION (e.g. secant -> tangent, zoom -> detail -> back):
  1. show the full overview,
  2. mark the region of interest, zoom_to(self, region),
  3. introduce the detail and animate the relationship,
  4. camera_reset(self) when the narration returns to the whole picture.
- zoom framing is computed for you by zoom_to(); never shrink text below
  readable size - if a label would be tiny, rewrite it larger in the same
  color role instead.

SEMANTIC COLOR (all colors come from the kit registry T.<role>):
- roles keep their meaning across scenes: T.variable (blue) for unknowns,
  T.constant (yellow) for numbers, T.operator for +,-,=, T.result_final
  (green) for final answers, T.result_intermediate (violet) for working
  results, T.warning (coral) for errors, T.auxiliary_geometry (muted) for
  helper lines, T.graph_function / T.graph_secant / T.graph_tangent /
  T.graph_point for curves and markers, T.vector_velocity /
  T.vector_force / T.vector_acceleration / T.vector_gravity for physics
  vectors, T.atom_* for elements (carbon dark gray, hydrogen off-white,
  oxygen red, nitrogen blue, sulfur yellow, chlorine green, phosphorus
  orange, bromine maroon), T.bond / T.bond_changing / T.bond_new for bonds.
- color-code equations as they are written (variables, constants, operators)
  and keep those colors when the expression transforms.
- equivalent quantities share a color (equal angles, equal sides); the
  final result gets T.result_final; never recolor the whole equation to
  highlight one term - use Indicate/Circumscribe on the piece instead.
- most scenes need only: background + text + ONE primary accent + the
  few extra roles that carry meaning. Every color must have a purpose.
- during zooms: dim_except(self, keep_list) then restore_emphasis(self);
  keep identity colors of the discussed objects.

SOLUTION FORMATS - the planner labels the lesson with a "format"; follow
the matching rules in every scene where a solution, reaction, or derivation
is shown:

FORMAT "numerical" (physics/chemistry numericals) - every worked numerical
follows this exact sequence, each stage introduced by its header:
1. "Given (Data)": list every provided parameter with standard symbols
   (m = 2 kg, u = 0, t = 5 s). If any value is in CGS or other units,
   convert to SI IMMEDIATELY and show the conversion (25 cm -> 0.25 m,
   2 min -> 120 s); otherwise state that all values are already in SI.
2. "To Find": state the unknowns with question marks (v = ?, s = ?).
3. "Formula": write the governing formula exactly (v = u + at); derive
   sub-formulas briefly when needed.
4. "Calculation": substitute the values and show intermediate steps - one
   step per line, never jumping from formula to answer. WHEN TERMS CANCEL,
   call cancel_terms(self, term) so each gets a red 45-degree strike and
   fades - use this in every lesson wherever cancellation occurs.
5. "Final Answer": box it (SurroundingRectangle, T.result_final) and
   always carry the correct SI unit inside the box.

FORMAT "derivation": begin by naming the core physical law you build on
("Starting from Newton's second law..."), use "let us consider..." when
introducing the setup, keep the algebra clean and sequential - one step
per line with connecting phrases ("Substituting (2) into (1)..."), keep
signs and vector notation correct, and support the derivation with a
diagram or graph. If one quantity is proportional to another, show it
visually: scaled_bar(label, value, scale) bars that grow together, and
zoom into the changing length. If the derivation integrates, EXPLAIN both
limits ("position runs from x0 = 0 at rest to x at time t") and visualize
the integral as riemann_rectangles(axes, f, a, b, n) refined n = 4 -> 16
-> 64 so the strips shrink toward the true area.

FORMAT "inorganic-reaction": balanced equation only (conservation of
mass); temperature and pressure ABOVE the arrow, catalyst and promoter
BELOW it (MathTex \\overset{...} and \\underset{...}); reversible
reactions use \\rightleftharpoons, irreversible use \\rightarrow; NEVER
omit inorganic byproducts (NaCl, H2O, HCl); close with the enthalpy
change - ", \\Delta H = -92.2 kJ/mol" (exothermic, negative) or
"+180.5 kJ/mol" (endothermic, positive) - or show heat as a term
(+ Heat on the product side / + Heat on the reactant side).

FORMAT "organic-reaction": use condensed structural formulas, never bare
molecular formulas (write CH3CH2OH, not C2H6O); the attacking reagent
goes on the LHS (or at the arrow when it is the medium); solvent and
catalyst BELOW the arrow (alc. KOH, dry ether, conc. H2SO4); temperature
or \\Delta ABOVE the arrow; ALL inorganic byproducts must appear and the
equation must balance (KBr + H2O, NaCl, HCl); for named reactions (Wurtz,
Cannizzaro, Aldol, Reimer-Tiemann...) state the stoichiometric
coefficients and the required medium (dry ether, conc. NaOH).
For multi-step conversions ("convert ethanol to ethanoic acid"), write
each numbered step on its own line with its own reagents and conditions.

FORMAT "aromatic" (benzene and derivatives): draw the hexagon ring with
alternating double bonds (or the inner resonance circle) - never just a
molecular formula like C6H5Cl, the substituent positions must be visible;
electrophilic aromatic substitution format: ring + electrophile reagent,
Lewis-acid catalyst BELOW the arrow, temperature/conditions ABOVE it, and
the released H+ shown as a byproduct; when a second substituent enters a
monosubstituted ring, show and name the director: activating o-/p-
directors (-OH, -NH2, -CH3 -> ortho/para products) versus deactivating
meta directors (-NO2, -COOH, -CHO -> meta product), and mark the MAJOR
product on the ring.
"""

SELECTION_RULES = """\
EFFECT SELECTION RULES:
- Add a transition only when the relationship between consecutive scenes
  calls for one; a plain cut ("none") is often best.
- Move the camera only when the important content leaves the frame or a
  different angle clarifies; otherwise keep it static.
- Zoom only for details that would be too small to read; zoom back out
  afterwards.
- Highlight only the element the narration is currently discussing.
- Use a three-dimensional scene only when depth, spatial relationships,
  molecular geometry, surfaces or volumes are the point of the explanation.
- Build diagrams progressively, in narration order.
- Prefer static visuals when motion would not improve understanding.
- Never add an effect just because it is available."""

# ---------------------------------------------------------------------------
# Transitions
# ---------------------------------------------------------------------------

# junction types realized as an ffmpeg crossfade between rendered clips
XFADE_MAP = {
    "fade": "fade",
    "dissolve": "dissolve",
    "wipe": "wipeleft",
    "topic": "fadeblack",
    "new-topic": "fadeblack",
}
# everything else (none / carry-over / slide-up / answer-reveal) is a
# straight cut: the continuity lives inside the scene code itself
CUT_TRANSITIONS = {"none", "carry-over", "carry", "slide-up", "answer-reveal"}
ALL_TRANSITIONS = sorted(set(XFADE_MAP) | CUT_TRANSITIONS)

# the question card always ends by fading the QUESTION badge and sliding
# the question text itself to the very top (the badge disappears; the
# question replaces it) so the first solution scene continues from there
DEFAULT_CARD_VISUAL = {"objective": "show the question while it is read",
                       "transition": "fade",
                       "transition_out": "slide-up",
                       "labels": ["QUESTION"],
                       "animation_beats": ["print the question below the "
                                          "QUESTION badge",
                                          "sketch the situation",
                                          "fade the badge and move the "
                                          "question to the very top"]}


SOLUTION_FORMAT_LABELS = ("numerical", "inorganic-reaction",
                          "organic-reaction", "aromatic", "derivation",
                          "conceptual", "mixed")

_FORMAT_ALIASES = {
    "numerical": "numerical", "numericals": "numerical",
    "numeric": "numerical", "word-problem": "numerical",
    "inorganic": "inorganic-reaction",
    "inorganic-reaction": "inorganic-reaction",
    "organic": "organic-reaction", "organic-reaction": "organic-reaction",
    "aromatic": "aromatic", "benzene": "aromatic", "eas": "aromatic",
    "derivation": "derivation", "derive": "derivation",
    "proof": "derivation", "conceptual": "conceptual",
    "theory": "conceptual", "mixed": "mixed", "" : "conceptual",
}


def normalize_format(value: object) -> str:
    """Validate the lesson's solution-format label."""
    text = re.sub(r"[^a-z]+", "-", str(value or "").lower()).strip("-")
    return _FORMAT_ALIASES.get(text, "conceptual")


def is_cut(transition: object) -> bool:
    return normalize_transition(transition) in CUT_TRANSITIONS


def normalize_transition(value: object) -> str:
    text = re.sub(r"[^a-z]+", "-", str(value or "").lower()).strip("-")
    if not text:
        return "none"
    aliases = {"carry": "carry-over", "topic": "new-topic",
               "fade-black": "new-topic", "fadeblack": "new-topic",
               "reveal": "answer-reveal", "slideup": "slide-up",
               "slide": "slide-up", "continuous": "carry-over"}
    text = aliases.get(text, text)
    if text in ALL_TRANSITIONS:
        return text
    return "carry-over"


def suggest_transition(previous: dict | None, current: dict) -> str:
    """Heuristic junction type when the planner did not specify one."""
    prev_kind = (previous or {}).get("kind", "body")
    if prev_kind == "question":
        return "slide-up"          # question -> its solution
    if (previous or {}).get("three_d") != current.get("three_d"):
        return "carry-over"        # e.g. 2D diagram -> 3D model
    if current.get("diagram") == "graph" and (previous or {}).get("diagram"):
        return "carry-over"        # equation -> graph handoff
    return "carry-over"


def transition_howto(transition: str, previous: dict | None = None) -> str:
    """Concrete instructions realizing this entry transition in scene code."""
    prev_summary = ""
    if previous:
        summary = previous.get("summary", "its key content centered")
        prev_summary = f" Previous scene ends with: {summary}."
    howto = {
        "slide-up":
            "Open with the question text alone at the VERY TOP of the "
            "frame (the QUESTION badge has faded away on the card; "
            "smaller, ~24-28 font), then begin the solution below it.",
        "carry-over":
            "Open with the key object from the previous scene already on "
            "screen in the same position, then continue from it." + prev_summary,
        "answer-reveal":
            "FadeOut the surrounding working first, then frame the final "
            "result with SurroundingRectangle and a short emphasis "
            "(Indicate or Flash). The result must stand apart from the "
            "intermediate steps.",
        "none": "Begin directly; keep a clean layout.",
    }
    return howto.get(transition,
                     f"Begin with a clear heading establishing the new "
                     f"topic; the pipeline crossfades into this scene "
                     f"('{transition}').")


# ---------------------------------------------------------------------------
# Plan normalization
# ---------------------------------------------------------------------------

def normalize_visual_plan(raw: object, kind: str = "body") -> dict:
    """Validate a planner-produced visual plan and fill sensible defaults."""
    if not isinstance(raw, dict):
        raw = {}
    string = lambda key, default="": _clean(raw.get(key), default)
    plan = {
        "kind": kind,
        "objective": string("objective", "illustrate this part of the lesson"),
        "transition": normalize_transition(raw.get("transition")),
        "transition_out": normalize_transition(raw.get("transition_out")),
        "preset": string("preset", "") or None,
        "visual_elements": _str_list(raw.get("visual_elements")),
        "diagram": _choice(raw.get("diagram"),
                           ("free-body", "circuit", "ray", "graph",
                            "apparatus", "process", "geometry"), "none"),
        "camera_movement": _choice(raw.get("camera_movement"),
                                   ("static", "pan", "track", "orbit"),
                                   "static"),
        "camera_target": string("camera_target"),
        "zoom_target": string("zoom_target"),
        "highlight": _str_list(raw.get("highlight")),
        "dynamic": _str_list(raw.get("dynamic")),
        "three_d": bool(raw.get("three_d", False)),
        "cancellation": bool(raw.get("cancellation", False)),
        "integration": bool(raw.get("integration", False)),
        "labels": _str_list(raw.get("labels")),
        "animation_beats": _str_list(raw.get("animation_beats")),
        "color_roles": _str_dict(raw.get("color_roles")),
        "layout": string("layout", "centered, no overlaps"),
        "outcome": string("outcome"),
    }
    return plan


def _str_dict(value) -> dict:
    if isinstance(value, dict):
        return {str(k).strip(): str(v).strip()
                for k, v in value.items() if str(v).strip()}
    return {}


def _clean(value, default: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _str_list(value) -> list:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _choice(value, options, default: str) -> str:
    text = str(value or "").strip().lower()
    return text if text in options else default


def describe_plan(plan: dict) -> str:
    """Human-readable rendering of a visual plan for the coder prompt."""
    lines = [f"objective: {plan['objective']}"]
    pairs = [("transition into scene", plan["transition"]),
             ("visual elements", ", ".join(plan["visual_elements"]) or "none"),
             ("diagram to build", plan["diagram"]),
             ("camera movement", plan["camera_movement"]),
             ("camera target", plan["camera_target"] or "-"),
             ("zoom target", plan["zoom_target"] or "-"),
             ("highlight in narration order",
              ", ".join(plan["highlight"]) or "-"),
             ("live relationships (keep mathematically connected)",
              ", ".join(plan["dynamic"]) or "-"),
             ("three-dimensional", "yes" if plan["three_d"] else "no"),
             ("labels", ", ".join(plan["labels"]) or "-"),
             ("color roles", ", ".join(f"{k}={v}"
                                       for k, v in plan["color_roles"].items())
              or "-"),
             ("layout", plan["layout"]),
             ("expected outcome", plan["outcome"] or "-")]
    for key, value in pairs:
        if value not in ("-", "", "none") or key.startswith(("transition",
                                                             "camera movement",
                                                             "diagram",
                                                             "three")):
            lines.append(f"{key}: {value}")
    if plan["animation_beats"]:
        lines.append("animation beats (in narration order):")
        lines += [f"  - {beat}" for beat in plan["animation_beats"]]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Post-render verification: did the planned effects actually get coded?
# ---------------------------------------------------------------------------

_EFFECT_CHECKS = [
    # (plan predicate, regexes required in the generated code, what to call it)
    (lambda p: p["camera_movement"] in ("pan", "track"),
     [r"MovingCameraScene",
      r"self\.camera\.frame|pan_to|follow\(|camera_reset"],
     "camera movement"),
    (lambda p: p["camera_movement"] == "track",
     [r"follow\(|ValueTracker.*\n.*updater|self\.camera\.frame"],
     "camera tracking"),
    (lambda p: p["camera_movement"] == "orbit",
     [r"begin_ambient_camera_rotation|orbit_start|move_camera"],
     "camera orbit"),
    (lambda p: bool(p["zoom_target"]),
     [r"zoom_to|\.set\(width|zoom\s*=", r"MovingCameraScene|ThreeDScene"],
     "zoom"),
    (lambda p: bool(p["highlight"]),
     [r"Indicate|FocusOn|Circumscribe|SurroundingRectangle|Flash|"
     r"emphasize\(|set_color|\.color\s*="],
     "highlighting"),
    (lambda p: bool(p["dynamic"]),
     [r"ValueTracker|add_updater|graph_point|secant_line|tangent_line"],
     "live/dynamic relationship"),
    (lambda p: p["cancellation"],
     [r"cancel_terms|strike_through"], "term cancellation strike"),
    (lambda p: p["integration"],
     [r"riemann_rectangles|integral"], "integration visualization"),
    (lambda p: p["three_d"],
     [r"ThreeDScene", r"Sphere|Surface|Line3D|Cube|Cone|ThreeDAxes|Cylinder"],
     "three-dimensional model"),
    (lambda p: p["diagram"] == "graph",
     [r"Axes|NumberPlane"], "graph"),
    (lambda p: p["diagram"] in ("free-body", "circuit", "ray", "apparatus",
                                "process", "geometry"),
     [r"Arrow|Line|Rectangle|Polygon"], "diagram"),
    (lambda p: p["transition"] == "answer-reveal",
     [r"SurroundingRectangle"], "answer framing"),
    (lambda p: bool(p["color_roles"]),
     [r"T\.\w+"], "semantic colors from the theme registry"),
]


def verify_effects(code: str, plan: dict) -> list[str]:
    """Return warnings for planned effects that do not appear in the code."""
    warnings: list[str] = []
    for predicate, patterns, label in _EFFECT_CHECKS:
        if not predicate(plan):
            continue
        if not all(re.search(pattern, code) for pattern in patterns):
            warnings.append(
                f"planned {label} not evident in the generated code")
    return warnings
