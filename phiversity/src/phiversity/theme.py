"""Centralized visual theme: semantic color registry + rendering presets.

Every visual component (LLM-written scenes, bundled lectures, transitions)
resolves colors through this registry instead of hardcoding hex values, so
roles keep their meaning across scenes and a theme change updates the whole
lecture consistently.

The resolved palette is injected into every rendered scene as a small "kit"
preamble (see kit_source()) that exposes:

  - T.<role>            ManimColor per semantic role (T.variable, T.text, ...)
  - zoom_to/pan_to/...  camera framing computed from target dimensions
  - follow/unfollow     camera tracking of moving objects
  - graph_point/secant_line/tangent_line   live, math-attached geometry
  - dim_except/restore_emphasis            context-aware emphasis control

Presets control the overall cinematic grading; semantic roles control the
meaning. Changing the background (e.g. the light "paper" preset) also swaps
text/auxiliary roles so contrast is preserved.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Palettes
# ---------------------------------------------------------------------------

_BASE_DARK = {
    "background_primary": "#101319",
    "background_secondary": "#171C25",
    "panel": "#202735",
    "grid": "#343B49",
    "text_primary": "#F4F2ED",
    "text_secondary": "#B8C0CC",
    "text_muted": "#858FA0",
    "variable": "#65A9FF",
    "constant": "#FFD166",
    "operator": "#F4F2ED",
    "result_intermediate": "#B69CFF",
    "result_final": "#75D6A0",
    "warning": "#FF6B78",
    "highlight_primary": "#FFD166",
    "highlight_secondary": "#55DDE0",
    "object_active": "#65A9FF",
    "object_inactive": "#858FA0",
    "auxiliary_geometry": "#858FA0",
    # graphs
    "graph_function": "#65A9FF",
    "graph_reference": "#858FA0",
    "graph_point": "#FFD166",
    "graph_tangent": "#55DDE0",
    "graph_secant": "#B69CFF",
    "graph_intersection": "#FFD166",
    # physics quantities
    "vector_velocity": "#55DDE0",
    "vector_acceleration": "#FF9F68",
    "vector_force": "#FF6B78",
    "vector_gravity": "#B69CFF",
    "vector_momentum": "#FFD166",
    "displacement": "#65A9FF",
    "stable_state": "#75D6A0",
    # chemistry
    "atom_carbon": "#5A6472",
    "atom_hydrogen": "#F4F2ED",
    "atom_oxygen": "#FF6B78",
    "atom_nitrogen": "#65A9FF",
    "atom_sulfur": "#FFD166",
    "atom_chlorine": "#75D6A0",
    "atom_phosphorus": "#FF9F68",
    "atom_bromine": "#A64632",
    "bond": "#B8C0CC",
    "atom_highlight": "#FFD166",
    "bond_changing": "#FF9F68",
    "bond_new": "#75D6A0",
    "cancel_mark": "#FF6B78",
}

# light "paper and notebook" theme: same roles, adjusted for contrast
_PAPER = dict(_BASE_DARK, **{
    "background_primary": "#F5F1E8",
    "background_secondary": "#EDE7DA",
    "panel": "#E4DDCC",
    "grid": "#C9C2B2",
    "text_primary": "#202733",
    "text_secondary": "#4A5468",
    "text_muted": "#8B8577",
    "variable": "#2463A6",
    "constant": "#A87411",
    "operator": "#202733",
    "result_intermediate": "#7554A6",
    "result_final": "#287A50",
    "warning": "#C0392B",
    "highlight_primary": "#B67F10",
    "highlight_secondary": "#1B8A93",
    "object_active": "#2463A6",
    "object_inactive": "#8B8577",
    "auxiliary_geometry": "#8B8577",
    "graph_function": "#2463A6",
    "graph_reference": "#8B8577",
    "graph_point": "#D89B19",
    "graph_tangent": "#1B8A93",
    "graph_secant": "#7554A6",
    "graph_intersection": "#D89B19",
    "vector_velocity": "#1B8A93",
    "vector_acceleration": "#B26329",
    "vector_force": "#C0392B",
    "vector_gravity": "#7554A6",
    "vector_momentum": "#D89B19",
    "displacement": "#2463A6",
    "stable_state": "#287A50",
    "atom_carbon": "#3E444E",
    "atom_hydrogen": "#202733",
    "atom_oxygen": "#C0392B",
    "atom_nitrogen": "#2463A6",
    "atom_sulfur": "#D89B19",
    "atom_chlorine": "#287A50",
    "atom_phosphorus": "#B26329",
    "atom_bromine": "#8F3A28",
    "bond": "#4A5468",
    "atom_highlight": "#D89B19",
    "bond_changing": "#B26329",
    "bond_new": "#287A50",
    "cancel_mark": "#C0392B",
})

PRESETS = {
    # A. Mathematical Focus - algebra, calculus, geometry
    "math": dict(_BASE_DARK),
    # B. Scientific Laboratory - apparatus, processes, physics
    "lab": dict(_BASE_DARK, background_primary="#0F1216",
                background_secondary="#151A20", panel="#1B222C"),
    # C. Spatial Exploration - 3D solids, molecules, cross-sections
    "spatial": dict(_BASE_DARK, background_primary="#14161C",
                    background_secondary="#1A1D25", panel="#232833"),
    # D. Data Visualization - statistics, comparisons
    "data": dict(_BASE_DARK, background_primary="#101319"),
    # E. Paper and Notebook - light theme
    "paper": _PAPER,
}

PRESET_ALIASES = {
    "mathematical": "math", "mathematical-focus": "math", "focus": "math",
    "scientific": "lab", "laboratory": "lab", "science": "lab",
    "spatial-exploration": "spatial", "3d": "spatial", "space": "spatial",
    "dataviz": "data", "visualization": "data", "charts": "data",
    "notebook": "paper", "light": "paper", "paper-theme": "paper",
    "dark": "math",
}

DEFAULT_PRESET = "math"

# roles whose contrast against the background matters most for readability
_READABILITY_ROLES = ("text_primary", "text_secondary", "variable",
                      "constant", "operator", "result_intermediate",
                      "result_final", "warning", "graph_function",
                      "graph_tangent", "graph_secant")

# curve-like roles that must stay pairwise distinguishable
_DISTINCT_ROLES = ("graph_function", "graph_secant", "graph_tangent",
                   "graph_point", "graph_reference")


def normalize_preset(name: object) -> str:
    text = str(name or "").strip().lower()
    if not text or text == "auto":
        return DEFAULT_PRESET
    return PRESET_ALIASES.get(text, text) if text in PRESET_ALIASES else (
        text if text in PRESETS else DEFAULT_PRESET)


def roles(preset: str = DEFAULT_PRESET) -> dict:
    """Full semantic role -> hex mapping for a preset."""
    return dict(PRESETS[normalize_preset(preset)])


# ---------------------------------------------------------------------------
# Accessibility helpers
# ---------------------------------------------------------------------------

def _hex_to_rgb01(hex_color: str) -> tuple:
    text = hex_color.lstrip("#")
    return tuple(int(text[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def relative_luminance(hex_color: str) -> float:
    def channel(value: float) -> float:
        return value / 12.92 if value <= 0.04045 else (
            (value + 0.055) / 1.055) ** 2.4
    r, g, b = _hex_to_rgb01(hex_color)
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    """WCAG contrast ratio between two hex colors (>=1, <=21)."""
    la, lb = relative_luminance(hex_a), relative_luminance(hex_b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def validate_preset(preset: str, min_text_contrast: float = 4.5,
                    min_accent_contrast: float = 2.5) -> list[str]:
    """Return a list of contrast/distinguishability problems for a preset."""
    palette = roles(preset)
    bg = palette["background_primary"]
    problems = []
    for role in ("text_primary", "text_secondary"):
        ratio = contrast_ratio(palette[role], bg)
        if ratio < min_text_contrast:
            problems.append(f"{role} contrast {ratio:.2f} < {min_text_contrast}")
    for role in _READABILITY_ROLES:
        ratio = contrast_ratio(palette[role], bg)
        if ratio < min_accent_contrast:
            problems.append(f"{role} contrast {ratio:.2f} < "
                            f"{min_accent_contrast}")
    seen = {}
    for role in _DISTINCT_ROLES:
        color = palette[role]
        for other_role, other_color in seen.items():
            if color == other_color:
                problems.append(f"{role} and {other_role} share color {color}")
        seen[role] = color
    return problems


# ---------------------------------------------------------------------------
# Kit source builder: the preamble injected into every scene file
# ---------------------------------------------------------------------------

def kit_source(preset: str = DEFAULT_PRESET) -> str:
    """Python preamble embedded at the top of every rendered scene.

    Exposes the resolved palette as `T.<role>` ManimColor attributes plus
    reusable camera, dynamic-geometry, and emphasis helpers. All helpers
    degrade gracefully when the scene class does not support them.
    """
    palette = roles(preset)
    color_lines = "\n".join(
        f"    {role} = ManimColor('{value}')" for role, value in palette.items())
    return f'''from manim import *

config.background_color = "{palette['background_primary']}"


class _Theme:
{color_lines}

T = _Theme()

FRAME_WIDTH = config.frame_width


# ---------------------------------------------------------------- camera ----
# These require class SceneName(MovingCameraScene). They compute the framing
# from the target's position and dimensions, clamp it to sane bounds, and
# always leave context around the target.

def zoom_to(scene, target, run_time=1.4, context=2.6, min_width=4.0):
    """Zoom so `target` fills the view with `context`x margin around it."""
    frame = getattr(scene.camera, "frame", None)
    if frame is None:
        return
    w = getattr(target, "width", 1.0)
    h = getattr(target, "height", 1.0) or 1.0
    width = max(w * context, h * context * 16.0 / 9.0, min_width)
    width = min(width, FRAME_WIDTH)
    center = target.get_center() if hasattr(target, "get_center") \\
        else np.array(target, dtype=float)
    scene.play(frame.animate.set(width=width).move_to(center),
               run_time=run_time)


def pan_to(scene, target, run_time=1.2):
    """Slide the view to `target` keeping the current zoom level."""
    frame = getattr(scene.camera, "frame", None)
    if frame is None:
        return
    center = target.get_center() if hasattr(target, "get_center") \\
        else np.array(target, dtype=float)
    scene.play(frame.animate.move_to(center), run_time=run_time)


def camera_reset(scene, run_time=1.2):
    """Return smoothly to the full overview."""
    frame = getattr(scene.camera, "frame", None)
    if frame is None:
        return
    scene.play(frame.animate.set(width=FRAME_WIDTH).move_to(ORIGIN),
               run_time=run_time)


def follow(scene, mobj):
    """Keep the moving `mobj` centered (call unfollow afterwards)."""
    frame = getattr(scene.camera, "frame", None)
    if frame is None:
        return
    frame.add_updater(lambda f: f.move_to(mobj.get_center()))


def unfollow(scene):
    frame = getattr(scene.camera, "frame", None)
    if frame is not None:
        frame.clear_updaters()


def orbit_start(scene, rate=0.12):
    """3D only: slow ambient camera rotation."""
    if hasattr(scene, "begin_ambient_camera_rotation"):
        scene.begin_ambient_camera_rotation(rate=rate)


def orbit_stop(scene):
    if hasattr(scene, "stop_ambient_camera_rotation"):
        scene.stop_ambient_camera_rotation()


def zoom_3d(scene, zoom=1.6, phi=None, theta=None, run_time=1.4):
    """3D only: move_camera with zoom (angle arguments optional)."""
    if not hasattr(scene, "move_camera"):
        return
    kwargs = {{"zoom": zoom, "run_time": run_time}}
    if phi is not None:
        kwargs["phi"] = phi
    if theta is not None:
        kwargs["theta"] = theta
    scene.move_camera(**kwargs)


# ------------------------------------------------------- dynamic geometry ----
# Live objects bound by real mathematical relationships (trackers +
# updaters), never visually approximated with unrelated objects.

def graph_point(axes, func, tracker, color=T.graph_point, radius=0.09):
    """Dot that follows func(tracker_value) on the given axes."""
    dot = Dot(axes.c2p(tracker.get_value(), func(tracker.get_value())),
              color=color, radius=radius)
    dot.add_updater(lambda d: d.move_to(
        axes.c2p(tracker.get_value(), func(tracker.get_value()))))
    return dot


def secant_line(axes, func, x0_tracker, x1_tracker,
                color=T.graph_secant, extend=0.35, stroke=5):
    """Secant through the two tracked points, extended and live-updating."""
    def build():
        x0 = x0_tracker.get_value()
        x1 = x1_tracker.get_value()
        p0 = np.array(axes.c2p(x0, func(x0)))
        p1 = np.array(axes.c2p(x1, func(x1)))
        direction = p1 - p0
        norm = np.linalg.norm(direction)
        if norm < 1e-6:
            direction = RIGHT * 1e-6
            norm = 1e-6
        step = direction / norm * extend
        return Line(p0 - step, p1 + step, color=color, stroke_width=stroke)
    line = build()
    line.add_updater(lambda l: l.become(build()))
    return line


def tangent_line(axes, func, x_tracker, color=T.graph_tangent,
                 half_length=1.6, stroke=5):
    """Tangent at the tracked point, slope from a central difference."""
    def slope(x):
        h = 1e-4
        return (func(x + h) - func(x - h)) / (2 * h)
    def build():
        x = x_tracker.get_value()
        p = np.array(axes.c2p(x, func(x)))
        direction = np.array(axes.c2p(x + 1, func(x) + slope(x))) - p
        direction = direction / np.linalg.norm(direction) * half_length
        return Line(p - direction, p + direction, color=color,
                    stroke_width=stroke)
    line = build()
    line.add_updater(lambda l: l.become(build()))
    return line


def numeric_slope(func, x, h=1e-4):
    return (func(x + h) - func(x - h)) / (2 * h)


# -------------------------------------------------------------- emphasis ----

_DIMMED = []


def dim_except(scene, keep, opacity=0.25):
    """Temporarily fade everything not in `keep` so the target stands out."""
    keep = keep if isinstance(keep, (list, tuple)) else [keep]
    _DIMMED.clear()
    for mobj in list(scene.mobjects):
        if mobj in keep or not hasattr(mobj, "fill_opacity"):
            continue
        _DIMMED.append((mobj, mobj.fill_opacity, mobj.stroke_opacity))
        mobj.set_fill(opacity=opacity)
        mobj.set_stroke(opacity=opacity)


def restore_emphasis(scene):
    """Undo dim_except, returning the wider scene to normal prominence."""
    for mobj, fill, stroke in _DIMMED:
        mobj.set_fill(opacity=fill)
        mobj.set_stroke(opacity=stroke)
    _DIMMED.clear()


def emphasize(scene, mobj, color=None, run_time=0.9):
    """Short purposeful emphasis of one element (keeps its role color)."""
    scene.play(Indicate(mobj, color=color, scale_factor=1.08),
               run_time=run_time)


# ------------------------------------------------------- exam mechanics ----

def wrap_text(text, font_size=26, max_width=12.5):
    """Split a long text into row strings that fit the frame. Use this for
    any user-entered question or long sentence so nothing runs off screen:
        rows = VGroup(*[Text(r, font_size=fs) for r in
                        wrap_text(long_text, fs)]).arrange(DOWN, buff=0.2)
    """
    char_w = font_size * 0.0042
    max_chars = max(12, int(max_width / char_w))
    words = str(text).split()
    rows, current = [], ""
    for word in words:
        if current and len(current) + 1 + len(word) > max_chars:
            rows.append(current)
            current = word
        else:
            current = (current + " " + word).strip()
    if current:
        rows.append(current)
    return rows


def fit_width(mobj, max_width=12.8):
    """Safety net: shrink any mobject wider than the usable frame."""
    if mobj.width > max_width:
        mobj.scale_to_fit_width(max_width)
    return mobj


def strike_through(scene, mobj, run_time=0.5):
    """Red 45-degree slash through a term - the cancellation mark."""
    diag = np.array([mobj.width * 0.58, mobj.height * 0.85, 0])
    slash = Line(mobj.get_center() - diag, mobj.get_center() + diag,
                 color=T.cancel_mark, stroke_width=5)
    scene.play(Create(slash), run_time=run_time)
    return slash


def cancel_terms(scene, a, b=None, run_time=0.5, remove=True):
    """Cancel terms visually: each gets a red 45-degree strike, then (by
    default) the struck terms fade away so the remaining expression is
    clear. Use this EVERY time terms cancel in an algebra step."""
    targets = [a] + ([b] if b is not None else [])
    slashes = []
    for target in targets:
        slashes.append(strike_through(scene, target, run_time=run_time))
    if remove:
        scene.play(FadeOut(VGroup(*targets, *slashes)), run_time=0.6)


def riemann_rectangles(axes, func, x_start, x_end, n,
                       color=T.graph_function, opacity=0.35):
    """n midpoint rectangles under func between the integration limits -
    the area the integral measures. Refine with:
        rects = riemann_rectangles(axes, f, a, b, 4)
        self.play(Transform(rects, riemann_rectangles(axes, f, a, b, 16)))
    so the viewer sees the strips getting narrower toward the true area."""
    rects = VGroup()
    width = (x_end - x_start) / n
    for i in range(n):
        x0 = x_start + i * width
        x1 = x0 + width
        height = func((x0 + x1) / 2)
        rect = Polygon(axes.c2p(x0, 0), axes.c2p(x1, 0),
                       axes.c2p(x1, height), axes.c2p(x0, height))
        rect.set_stroke(color, 1.5, opacity=0.9)
        rect.set_fill(color, opacity)
        rects.add(rect)
    return rects


def scaled_bar(label, value, scale=1.0, color=T.graph_function,
               height=0.26):
    """Bar whose WIDTH is proportional to value - makes direct
    proportionality visible. Transform between values to show the
    relationship (e.g. zoom into how the length grows)."""
    bar = Rectangle(width=max(0.05, value * scale), height=height)
    bar.set_stroke(color, 1.5)
    bar.set_fill(color, 0.8)
    text = Text(label, font_size=20, color=T.text_secondary)
    return VGroup(text, bar).arrange(DOWN, buff=0.12)
'''
