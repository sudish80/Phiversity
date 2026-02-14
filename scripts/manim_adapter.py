import argparse
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Layout and collision detection modules (Phase 3)
from .layout_engine import (
    LayoutEngine, LayoutStrategy, ScreenBounds, ContentBox, TextAnchor, LayoutZone
)
from .collision_detector import CollisionDetector, AABBCollider, CollisionResolver
from .layer_manager import LayerManager, ElementType
from .qa_metrics import QAMetricsEngine, FrameAnalysis

# Consistent naming for video outputs
# Used when render_with_manim() is called with out_path parameter
FINAL_VIDEO_NAME = "final.mp4"

# Manim screen dimensions (standard 16:9)
MANIM_SCREEN_WIDTH = 8.0   # Manim units (pixels = units * 100)
MANIM_SCREEN_HEIGHT = 4.5  # Manim units


POSITION_MAP = {
    "center": "ORIGIN",
    "top": "UP",
    "bottom": "DOWN",
    "left": "LEFT",
    "right": "RIGHT",
    "top-left": "UP+LEFT",
    "top-right": "UP+RIGHT",
    "bottom-left": "DOWN+LEFT",
    "bottom-right": "DOWN+RIGHT",
}


def apply_layout_and_collision_detection(scene: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply dynamic layout, collision detection, and layer management to scene elements.
    
    This function:
    1. Extracts elements from scene
    2. Creates ContentBox objects for each
    3. Applies layout algorithm to position elements
    4. Detects and resolves collisions
    5. Assigns z-indices based on layer hierarchy
    
    Args:
        scene: Scene dict with elements
    
    Returns:
        Updated scene dict with optimized positions and layer assignments
    """
    elements = scene.get("elements", [])
    if not elements:
        return scene
    
    try:
        # Initialize layout engine with screen bounds
        screen_bounds = ScreenBounds(
            width=MANIM_SCREEN_WIDTH,
            height=MANIM_SCREEN_HEIGHT,
            margin=0.5  # 0.5% margin from edges
        )
        # Reserve space for the scene header at the top.
        header_buffer = 0.6
        screen_bounds.top -= header_buffer
        layout_engine = LayoutEngine(screen_bounds, LayoutStrategy.FLOATING)
        
        # Initialize collision detector and resolver
        collision_detector = CollisionDetector()
        collision_resolver = CollisionResolver((screen_bounds.left, screen_bounds.right, 
                                               screen_bounds.top, screen_bounds.bottom))
        
        # Initialize layer manager
        layer_manager = LayerManager()
        
        # Convert scene elements to ContentBox objects
        content_boxes: List[Tuple[ContentBox, int]] = []  # (box, original_index)
        
        for idx, element in enumerate(elements):
            element_type = str(element.get("type", "text")).lower()
            element_id = element.get("id", f"elem_{idx}")
            content = str(element.get("content", ""))[:100]
            
            # Estimate dimensions based on type
            if element_type in ("text", "mathtex", "label"):
                lines = content.split("\n") if content else [""]
                max_len = max(len(line) for line in lines)
                width = min(6.5, 0.12 * max_len + 1.0)
                height = max(0.5, 0.4 * len(lines))
                element_class = ElementType.LABEL if element_type == "label" else ElementType.TEXT
            elif element_type == "axes":
                width = 3.0
                height = 2.5
                element_class = ElementType.GRAPH
            elif element_type in ("graph", "parametric"):
                width = 3.5
                height = 3.0
                element_class = ElementType.GRAPH
            elif element_type in ("figure", "image"):
                width = 2.5
                height = 2.0
                element_class = ElementType.FIGURE
            else:
                width = 2.0
                height = 1.0
                element_class = ElementType.DIAGRAM
            
            # Get timing info
            timing = element.get("timing", {})
            start_time = timing.get("start", 0.0) if isinstance(timing, dict) else 0.0
            end_time = timing.get("end", float('inf')) if isinstance(timing, dict) else float('inf')
            
            # Create ContentBox
            box = ContentBox(
                id=element_id,
                type=element_type,
                content=content,
                width=width,
                height=height,
                position=(0, 0),  # Will be updated by layout engine
                anchor=TextAnchor.CENTER,
                timestamp_start=start_time,
                timestamp_end=end_time,
                metadata={
                    "original_position": element.get("position"),
                    "style": element.get("style", {}),
                }
            )
            
            layout_engine.add_content(box)
            content_boxes.append((box, idx))
            
            # Assign layer
            layer_manager.assign_layer(element_id, element_class, priority=0)
        
        # Apply layout algorithm
        positioned_boxes = layout_engine.layout()
        # (Layout engine already handles collision detection and resolution internally)
        
        # Check for conflicts in layer assignments
        layer_manager.detect_conflicts()
        layer_manager.resolve_conflicts()
        
        # Update original scene with optimized positions and layers
        for box, original_idx in content_boxes:
            if original_idx < len(elements):
                element = elements[original_idx]
                
                # Update position (convert from Manim units to string position)
                x, y = box.position
                
                # Store optimized position for later use
                element["_layout_position"] = (x, y)
                element["_layout_width"] = box.width
                element["_layout_height"] = box.height
                
                # Add z-index
                z_index = layer_manager.get_z_index(box.id)
                if z_index is not None:
                    element["_layout_z_index"] = z_index
        
        return scene
        
    except Exception as e:
        # If layout fails, return original scene unchanged
        print(f"[manim_adapter] Layout warning: {str(e)}", file=sys.stderr)
        return scene


def _safe_str(s: str) -> str:
    # Basic sanitize
    cleaned = s.replace("\\", " ").replace("'", "\\'")
    # Wrap text that is too long to avoid overflowing the screen (approx 50 chars for font size 0.6)
    if len(cleaned) > 50:
        return "\\n".join(textwrap.wrap(cleaned, width=50))
    return cleaned


def _color_expr(style: Dict[str, Any] | None) -> Optional[str]:
    if not style or not isinstance(style, dict):
        return None
    color = style.get("color")
    if not color:
        return None
    c = str(color)
    if c.startswith("#"):
        return f"Color('{c}')"
    return c.upper()


def _pos_expr(p: Optional[str]) -> str:
    if not p:
        return "ORIGIN"
    return POSITION_MAP.get(str(p).lower(), "ORIGIN")


def _anim_in_default(etype: str) -> str:
    return "Create" if etype in {"axes", "graph", "vectorfield", "streamlines", "parametric3d", "highlight"} else "Write"


def _anim_out_default(etype: str) -> str:
    return "FadeOut" if etype in {"text", "mathtex", "highlight"} else "Uncreate"


def _normalize_anim(name: Optional[str], default: str) -> str:
    if not name:
        return default
    n = name.strip().lower()
    mapping = {
        "write": "Write",
        "fadein": "FadeIn",
        "create": "Create",
        "fadeout": "FadeOut",
        "uncreate": "Uncreate",
        "growfromcenter": "GrowFromCenter",
    }
    return mapping.get(n, default)


def _rate_func(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    n = name.strip().lower()
    mapping = {
        "linear": "rf.linear",
        "smooth": "rf.smooth",
        "rush_from": "rf.rush_from",
        "rush_into": "rf.rush_into",
        "there_and_back": "rf.there_and_back",
        "ease_in_sine": "rf.ease_in_sine",
        "ease_out_sine": "rf.ease_out_sine",
    }
    return mapping.get(n)


def generate_scene_script(
    data: Dict[str, Any],
    scene_durations: Optional[List[float]] = None,
    element_durations: Optional[List[List[float]]] = None,
) -> str:
    scenes: List[Dict[str, Any]] = data.get("animation_plan", {}).get("scenes", [])
    solution = data.get("solution", {})
    topic = solution.get("topic") or "Generated Solution"

    # Determine if any 3D element is present
    needs_3d = any(
        (str(el.get("type") or "").lower() in ("parametric3d",))
        for sc in scenes
        for el in sc.get("elements", [])
    )

    scene_cls = "ThreeDScene" if needs_3d else "Scene"

    # Inject intro scene with voiceover if not present
    scenes_with_intro = scenes.copy()
    if not scenes or (scenes and scenes[0].get('description', '').lower() != 'intro'):
        intro_scene = {
            "id": "intro",
            "description": "intro",
            "voiceover": "Welcome to Phiversity. Where Physics Education is made simple.",
            "elements": []
        }
        scenes_with_intro.insert(0, intro_scene)
        # Also inject into the original data so voiceover generation picks it up
        if "animation_plan" not in data:
            data["animation_plan"] = {}
        if "scenes" not in data["animation_plan"]:
            data["animation_plan"]["scenes"] = []
        data["animation_plan"]["scenes"].insert(0, intro_scene)
    
    lines: List[str] = [
        "from manim import *",
        "from manim import rate_functions as rf",
        "from manim.utils.color import ManimColor as Color",
        "",
        f"class GeneratedScene({scene_cls}):",
        "    def construct(self):",
        "        # Add watermark",
        "        watermark = Text('Phiversity', font_size=18, color=GRAY).set_opacity(0.5)",
        "        watermark.to_corner(DR, buff=0.2)",
        "        self.add(watermark)",
        "",
    ]
    if needs_3d:
        lines.append("        self.set_camera_orientation(phi=60*DEGREES, theta=45*DEGREES)")

    for sidx, sc in enumerate(scenes_with_intro, start=1):
        desc = sc.get("description", "")
        scene_id = sc.get("id", "")
        
        # Special handling for intro scene
        if scene_id == "intro" or desc.lower() == "intro":
            lines.append("        # Intro screen")
            lines.append("        intro = Text('Phiversity', font_size=72, color=BLUE)")
            lines.append("        tagline = Text('Physics Education Made Simple', font_size=28, color=WHITE).next_to(intro, DOWN)")
            lines.append("        self.play(FadeIn(intro, scale=0.5))")
            lines.append("        self.play(Write(tagline))")
            lines.append("        self.wait(1)")
            lines.append("        self.play(FadeOut(intro), FadeOut(tagline))")
            lines.append("        self.wait(0.3)")
            continue
        
        scene_title = _safe_str(desc[:80]) or sc.get("id", f"Scene {sidx}")
        lines.append(f"        header = Text('{scene_title}').scale(0.6).to_edge(UP)")
        lines.append("        self.play(FadeIn(header, shift=DOWN))")
        lines.append("        objs = []  # track elements for potential highlighting")
        lines.append("        idmap = {}  # id -> mobject var name")
        lines.append("        axes = None  # last created Axes")
        lines.append("        import math")
        lines.append("        import numpy as np")
        lines.append("        t = 0.0  # scene timeline in seconds")
        lines.append("        R = 2.0  # Const radius")
        lines.append("        r = 1.0  # Var radius")
        lines.append("        dr = 0.2 # Thickness")

        dur_list = element_durations[sidx-1] if element_durations and len(element_durations) >= sidx else None
        acc = 0.0

        # PHASE 3: Apply layout and collision detection to scene elements
        sc_with_layout = apply_layout_and_collision_detection(sc)

        for eidx, el in enumerate(sc_with_layout.get("elements", []), start=1):
            etype = str(el.get("type") or "").lower()
            content = _safe_str(el.get("content") or "")
            
            # Use layout-optimized position if available, otherwise use original position
            if "_layout_position" in el:
                layout_x, layout_y = el["_layout_position"]
                p = f"np.array([{layout_x:.3f}, {layout_y:.3f}, 0.0])"
                # Store layout position in element for later use if needed
                el["_optimized_position"] = (layout_x, layout_y)
            else:
                p = _pos_expr(el.get("position"))
            
            style = el.get("style") if isinstance(el, dict) else None
            color_e = _color_expr(style if isinstance(style, dict) else None)
            timing = el.get("timing") if isinstance(el, dict) else None
            start = timing.get("start") if isinstance(timing, dict) else None
            end = timing.get("end") if isinstance(timing, dict) else None
            tin = (timing.get("transition_in") if isinstance(timing, dict) else None) or ""
            tout = (timing.get("transition_out") if isinstance(timing, dict) else None) or ""
            easing = (timing.get("easing") if isinstance(timing, dict) else None) or ""
            dur_in = timing.get("duration_in") if isinstance(timing, dict) else None
            dur_out = timing.get("duration_out") if isinstance(timing, dict) else None
            el_id = (el.get("id") if isinstance(el, dict) else None) or None

            if start is None and dur_list and len(dur_list) >= eidx:
                start = acc
                end = acc + float(dur_list[eidx - 1])
                acc = end if end is not None else acc

            var = f"obj_{sidx}_{eidx}"
            in_anim = _normalize_anim(tin, _anim_in_default(etype))
            out_anim = _normalize_anim(tout, _anim_out_default(etype))
            rfname = _rate_func(easing)

            def _extras(rt: Optional[float]) -> str:
                ex: List[str] = []
                if rfname:
                    ex.append(f"rate_func={rfname}")
                if rt is not None:
                    ex.append(f"run_time={float(rt):.3f}")
                return (", " + ", ".join(ex)) if ex else ""

            if etype in ("text", ""):
                lines.append(f"        {var} = Text('{content}').scale(0.6).move_to({p})")
                if color_e:
                    lines.append(f"        {var}.set_color({color_e})")
                if start is not None:
                    lines.append(f"        if t < {start:.3f}: self.wait({start:.3f} - t); t = {start:.3f}")
                lines.append(f"        self.play({in_anim}({var}){_extras(dur_in)})")
                if end is not None and (start is None or end > start) and tout:
                    lines.append(f"        if t < {end:.3f}: self.wait({end:.3f} - t); t = {end:.3f}")
                    lines.append(f"        self.play({out_anim}({var}){_extras(dur_out)})")
                lines.append(f"        objs.append({var})")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = {var}")

            elif etype in ("mathtex", "latex"):
                lines.append("        try:")
                lines.append(f"            {var} = MathTex(r'''{content}''').scale(0.8).move_to({p})")
                lines.append("        except Exception:")
                lines.append(f"            {var} = Text('{content}').scale(0.6).move_to({p})")
                if color_e:
                    lines.append(f"        {var}.set_color({color_e})")
                if start is not None:
                    lines.append(f"        if t < {start:.3f}: self.wait({start:.3f} - t); t = {start:.3f}")
                lines.append(f"        self.play({in_anim}({var}){_extras(dur_in)})")
                if end is not None and (start is None or end > start) and tout:
                    lines.append(f"        if t < {end:.3f}: self.wait({end:.3f} - t); t = {end:.3f}")
                    lines.append(f"        self.play({out_anim}({var}){_extras(dur_out)})")
                lines.append(f"        objs.append({var})")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = {var}")

            elif etype == "axes":
                xr = style.get("x_range", [-5, 5, 1]) if isinstance(style, dict) else [-5, 5, 1]
                yr = style.get("y_range", [-3, 3, 1]) if isinstance(style, dict) else [-3, 3, 1]
                lines.append(f"        axes = Axes(x_range={xr}, y_range={yr})")
                lines.append(f"        axes.move_to({p})")
                if color_e:
                    lines.append(f"        axes.set_color({color_e})")
                xlab = style.get("x_label") if isinstance(style, dict) else None
                ylab = style.get("y_label") if isinstance(style, dict) else None
                if start is not None:
                    lines.append(f"        if t < {start:.3f}: self.wait({start:.3f} - t); t = {start:.3f}")
                if xlab or ylab:
                    xl = _safe_str(xlab or "x")
                    yl = _safe_str(ylab or "y")
                    lines.append(f"        lbls = axes.get_axis_labels(MathTex('{xl}'), MathTex('{yl}'))")
                    lines.append("        self.play(Create(axes), FadeIn(lbls))")
                else:
                    lines.append("        self.play(Create(axes))")
                if end is not None and (start is None or end > start) and tout:
                    lines.append(f"        if t < {end:.3f}: self.wait({end:.3f} - t); t = {end:.3f}")
                    lines.append("        self.play(Uncreate(axes))")
                lines.append("        objs.append(axes)")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = axes")

            elif etype == "graph":
                lines.append("        if axes is None:")
                lines.append("            axes = Axes(x_range=[-5,5,1], y_range=[-3,3,1])")
                lines.append("            self.play(Create(axes))")
                curves = (style.get('curves') if isinstance(style, dict) else None) or []
                single = {"content": content, **(style or {})}
                items = curves if curves else [single]
                lines.append("        legend_items = []")
                lines.append("        import math, numpy as np")
                for_i = [
                    "        for cv in (items := " + str([{
                        'mode': (cv.get('mode') or 'function') if isinstance(cv, dict) else 'function',
                        'content': (cv.get('content') if isinstance(cv, dict) else None) or content,
                        'x': (cv.get('x') if isinstance(cv, dict) else None),
                        'y': (cv.get('y') if isinstance(cv, dict) else None),
                        't_range': (cv.get('t_range') if isinstance(cv, dict) else None) or [0, 6.283],
                        'x_range': (cv.get('x_range') if isinstance(cv, dict) else None) or [-5, 5],
                        'color': (cv.get('color') if isinstance(cv, dict) else None),
                        'label': (cv.get('label') if isinstance(cv, dict) else None),
                    } for cv in items]) + "):",
                ]
                lines.extend(for_i)
                lines.append("            mode = (cv.get('mode') or 'function').lower()")
                lines.append("            color = cv.get('color')")
                lines.append("            label = cv.get('label')")
                lines.append("            if mode == 'parametric':")
                lines.append("                ex = cv.get('x') or 'cos(t)'")
                lines.append("                ey = cv.get('y') or 'sin(t)'")
                lines.append("                tr = cv.get('t_range') or [0, 6.283]")
                lines.append("                def _fx(t): return eval(ex, {'__builtins__': None, 'math': math, 'np': np}, {'t': t})")
                lines.append("                def _fy(t): return eval(ey, {'__builtins__': None, 'math': math, 'np': np}, {'t': t})")
                lines.append("                curve = axes.plot_parametric_curve(lambda t: np.array([_fx(t), _fy(t), 0]), t_range=tr)")
                lines.append("            else:")
                lines.append("                ex = cv.get('content') or 'sin(x)'")
                lines.append("                xr = cv.get('x_range') or [-5, 5]")
                lines.append("                def _f(x):")
                lines.append("                    try:")
                lines.append("                        return eval(ex, {'__builtins__': None, 'math': math, 'np': np, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan, 'exp': math.exp, 'log': math.log, 'pi': math.pi, 'e': math.e}, {'x': x})")
                lines.append("                    except:")
                lines.append("                        return math.sin(x)")
                lines.append("                curve = axes.plot(_f, x_range=xr)")
                lines.append("            if color: curve.set_color(Color(color) if str(color).startswith('#') else str(color).upper())")
                if start is not None:
                    lines.append(f"        if t < {start:.3f}: self.wait({start:.3f} - t); t = {start:.3f}")
                lines.append("        self.play(Create(curve))")
                if end is not None and (start is None or end > start) and tout:
                    lines.append(f"        if t < {end:.3f}: self.wait({end:.3f} - t); t = {end:.3f}")
                    lines.append("        self.play(Uncreate(curve))")
                lines.append("        objs.append(curve)")
                lines.append("        if label: legend_items.append((curve, label))")
                lines.append("        if legend_items:")
                lines.append("            items2 = []")
                lines.append("            for curve2, lbl in legend_items:")
                lines.append("                dot = Dot(color=curve2.get_color()).scale(0.7)")
                lines.append("                txt = Text(str(lbl)).scale(0.4)")
                lines.append("                items2.append(VGroup(dot, txt).arrange(RIGHT, buff=0.2))")
                lines.append("            legend = VGroup(*items2).arrange(DOWN, aligned_edge=LEFT).to_corner(UR)")
                lines.append("            self.play(FadeIn(legend))")
                lines.append("            objs.append(legend)")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = axes")
            elif etype == "vectorfield":
                # 2D vector field based on fx, fy or content like "[y,-x]"
                fx = None
                fy = None
                if isinstance(style, dict):
                    fx = style.get('fx')
                    fy = style.get('fy')
                if not fx or not fy:
                    parts = content.strip().strip('[]').split(',') if content else []
                    if len(parts) == 2:
                        fx, fy = parts[0].strip(), parts[1].strip()
                if not fx or not fy:
                    fx, fy = 'y', '-x'
                xr = style.get('x_range', [-5,5,1]) if isinstance(style, dict) else [-5,5,1]
                yr = style.get('y_range', [-3,3,1]) if isinstance(style, dict) else [-3,3,1]
                lines.append(f"        def _fx(x,y):\n            return eval({repr(fx)}, {{'__builtins__': None, 'math': math, 'np': np}}, {{'x': x, 'y': y}})")
                lines.append(f"        def _fy(x,y):\n            return eval({repr(fy)}, {{'__builtins__': None, 'math': math, 'np': np}}, {{'x': x, 'y': y}})")
                lines.append("        vf = VectorField(lambda p: np.array([_fx(p[0], p[1]), _fy(p[0], p[1]), 0]), x_range=" + str(xr) + ", y_range=" + str(yr) + ")")
                if color_e:
                    lines.append(f"        vf.set_color({color_e})")
                if start is not None:
                    lines.append(f"        if t < {start:.3f}: self.wait({start:.3f} - t); t = {start:.3f}")
                lines.append("        self.play(Create(vf))")
                if end is not None and (start is None or end > start) and tout:
                    lines.append(f"        if t < {end:.3f}: self.wait({end:.3f} - t); t = {end:.3f}")
                    lines.append("        self.play(Uncreate(vf))")
                lines.append("        objs.append(vf)")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = vf")
            elif etype == "streamlines":
                fx = None
                fy = None
                if isinstance(style, dict):
                    fx = style.get('fx')
                    fy = style.get('fy')
                if not fx or not fy:
                    parts = content.strip().strip('[]').split(',') if content else []
                    if len(parts) == 2:
                        fx, fy = parts[0].strip(), parts[1].strip()
                if not fx or not fy:
                    fx, fy = 'y', '-x'
                xr = style.get('x_range', [-5,5,1]) if isinstance(style, dict) else [-5,5,1]
                yr = style.get('y_range', [-3,3,1]) if isinstance(style, dict) else [-3,3,1]
                lines.append(f"        def _fx(x,y):\n            return eval({repr(fx)}, {{'__builtins__': None, 'math': math, 'np': np}}, {{'x': x, 'y': y}})")
                lines.append(f"        def _fy(x,y):\n            return eval({repr(fy)}, {{'__builtins__': None, 'math': math, 'np': np}}, {{'x': x, 'y': y}})")
                lines.append("        stream = StreamLines(lambda p: np.array([_fx(p[0], p[1]), _fy(p[0], p[1]), 0]), x_range=" + str(xr) + ", y_range=" + str(yr) + ")")
                if color_e:
                    lines.append(f"        stream.set_color({color_e})")
                if start is not None:
                    lines.append(f"        if t < {start:.3f}: self.wait({start:.3f} - t); t = {start:.3f}")
                lines.append("        self.play(Create(stream))")
                if end is not None and (start is None or end > start) and tout:
                    lines.append(f"        if t < {end:.3f}: self.wait({end:.3f} - t); t = {end:.3f}")
                    lines.append("        self.play(Uncreate(stream))")
                lines.append("        objs.append(stream)")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = stream")
            elif etype == "parametric3d":
                lines.append("        axes3d = ThreeDAxes()")
                lines.append("        self.play(Create(axes3d))")
                ex = (style.get('x') if isinstance(style, dict) else None) or 'cos(t)'
                ey = (style.get('y') if isinstance(style, dict) else None) or 'sin(t)'
                ez = (style.get('z') if isinstance(style, dict) else None) or '0.2*t'
                tr = (style.get('t_range') if isinstance(style, dict) else None) or [0, 6.283]
                lines.append(f"        def fx(t):\n            return eval({repr(ex)}, {{'__builtins__': None, 'math': math, 'np': np}}, {{'t': t}})")
                lines.append(f"        def fy(t):\n            return eval({repr(ey)}, {{'__builtins__': None, 'math': math, 'np': np}}, {{'t': t}})")
                lines.append(f"        def fz(t):\n            return eval({repr(ez)}, {{'__builtins__': None, 'math': math, 'np': np}}, {{'t': t}})")
                lines.append("        curve3d = ParametricFunction(lambda t: np.array([fx(t), fy(t), fz(t)]), t_range=tr, use_smoothing=False)")
                if color_e:
                    lines.append("        curve3d.set_color(" + color_e + ")")
                if start is not None:
                    lines.append(f"        if t < {start:.3f}: self.wait({start:.3f} - t); t = {start:.3f}")
                lines.append("        self.play(Create(curve3d))")
                if end is not None and (start is None or end > start) and tout:
                    lines.append(f"        if t < {end:.3f}: self.wait({end:.3f} - t); t = {end:.3f}")
                    lines.append("        self.play(Uncreate(curve3d))")
                lines.append("        objs.append(curve3d)")
            elif etype == "highlight":
                lines.append("        target = None")
                lines.append("        if objs:\n            target = objs[-1]")
                lines.append(f"        match_text = {repr(content)}")
                lines.append("        if match_text:\n            for o in objs:\n                try:\n                    if hasattr(o, 'text') and o.text == match_text:\n                        target = o\n                        break\n                except Exception:\n                    pass")
                lines.append("        if target is not None:")
                lines.append(f"            {var} = SurroundingRectangle(target, buff=0.2)")
                if color_e:
                    lines.append(f"            {var}.set_color({color_e})")
                if start is not None:
                    lines.append(f"            if t < {start:.3f}: self.wait({start:.3f} - t); t = {start:.3f}")
                lines.append(f"            self.play(Create({var}))")
                if end is not None and (start is None or end > start) and tout:
                    lines.append(f"            if t < {end:.3f}: self.wait({end:.3f} - t); t = {end:.3f}")
                    lines.append(f"            self.play(Uncreate({var}))")
                lines.append(f"            objs.append({var})")
                if el_id:
                    lines.append(f"            idmap['{el_id}'] = {var}")

            elif etype == "polygon":
                sanitized = content.replace("\\pi", "np.pi")
                lines.append(f"        try:")
                lines.append(f"            pts_list = eval('{sanitized}', {{'__builtins__': None, 'np': np, 'R': R, 'r': r, 'dr': dr}})")
                lines.append(f"            {var} = Polygon(*[np.array([x,y,0]) for x,y in pts_list])")
                if p: # Apply position shift if present
                    lines.append(f"            {var}.move_to({p})")
                if color_e:
                    lines.append(f"            {var}.set_color({color_e})")
                if style and 'fill_opacity' in style:
                    lines.append(f"            {var}.set_fill({color_e or 'WHITE'}, opacity={style['fill_opacity']})")
                lines.append(f"        except Exception:")
                lines.append(f"            {var} = Text('Polygon Error')")
                
                if start is not None:
                    lines.append(f"        if t < {start:.3f}: self.wait({start:.3f} - t); t = {start:.3f}")
                lines.append(f"        self.play(Create({var}))")
                if end is not None and (start is None or end > start) and tout:
                    lines.append(f"        if t < {end:.3f}: self.wait({end:.3f} - t); t = {end:.3f}")
                    lines.append(f"        self.play(Uncreate({var}))")
                lines.append(f"        objs.append({var})")
                
            elif etype == "circle":
                lines.append(f"        {var} = Circle(radius=R)")
                if p: lines.append(f"        {var}.move_to({p})")
                if color_e:
                    lines.append(f"        {var}.set_color({color_e})")
                if start is not None:
                    lines.append(f"        if t < {start:.3f}: self.wait({start:.3f} - t); t = {start:.3f}")
                lines.append(f"        self.play(Create({var}))")
                if end is not None and (start is None or end > start) and tout:
                    lines.append(f"        if t < {end:.3f}: self.wait({end:.3f} - t); t = {end:.3f}")
                    lines.append(f"        self.play(Uncreate({var}))")
                lines.append(f"        objs.append({var})")

            elif etype == "annulus":
                lines.append(f"        {var} = Annulus(inner_radius=r, outer_radius=r+dr)")
                if p: lines.append(f"        {var}.move_to({p})")
                if color_e:
                     lines.append(f"        {var}.set_color({color_e})")
                if style and 'fill_opacity' in style:
                     lines.append(f"        {var}.set_fill({color_e or 'YELLOW'}, opacity={style['fill_opacity']})")
                if start is not None:
                    lines.append(f"        if t < {start:.3f}: self.wait({start:.3f} - t); t = {start:.3f}")
                lines.append(f"        self.play(Create({var}))")
                if end is not None and (start is None or end > start) and tout:
                    lines.append(f"        if t < {end:.3f}: self.wait({end:.3f} - t); t = {end:.3f}")
                    lines.append(f"        self.play(Uncreate({var}))")
                lines.append(f"        objs.append({var})")

            elif etype == "rectangle":
                # Fallback implementation
                lines.append(f"        {var} = Rectangle(width=2*np.pi*r, height=dr)")
                lines.append(f"        {var}.move_to({p})")
                if color_e:
                     lines.append(f"        {var}.set_color({color_e})")
                if style and 'fill_opacity' in style:
                     lines.append(f"        {var}.set_fill({color_e or 'BLUE'}, opacity={style['fill_opacity']})")
                if start is not None:
                    lines.append(f"        if t < {start:.3f}: self.wait({start:.3f} - t); t = {start:.3f}")
                lines.append(f"        self.play(Create({var}))")
                if end is not None and (start is None or end > start) and tout:
                     lines.append(f"        if t < {end:.3f}: self.wait({end:.3f} - t); t = {end:.3f}")
                     lines.append(f"        self.play(Uncreate({var}))")
                lines.append(f"        objs.append({var})")

            else:
                lines.append(f"        {var} = Text('{content}').scale(0.6).move_to({p})")
                if color_e:
                    lines.append(f"        {var}.set_color({color_e})")
                if start is not None:
                    lines.append(f"        if t < {start:.3f}: self.wait({start:.3f} - t); t = {start:.3f}")
                lines.append(f"        self.play(Write({var}))")
                if end is not None and (start is None or end > start) and tout:
                    lines.append(f"        if t < {end:.3f}: self.wait({end:.3f} - t); t = {end:.3f}")
                    lines.append(f"        self.play(FadeOut({var}))")
                lines.append(f"        objs.append({var})")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = {var}")

        if scene_durations and len(scene_durations) >= sidx:
            lines.append(f"        if t < {scene_durations[sidx-1]:.3f}: self.wait({scene_durations[sidx-1]:.3f} - t); t = {scene_durations[sidx-1]:.3f}")
        else:
            lines.append("        self.wait(1.0)")

        # Clear scene at end to prevent overlapping text in next scene
        lines.append("        self.play(FadeOut(Group(*self.mobjects)))")
        lines.append("        self.play(FadeOut(header))")

    lines.append("        self.wait(0.5)")
    return "\n".join(lines) + "\n"


def render_with_manim(script_path: Path, scene_name: str, out_path: Optional[Path] = None, quality: Optional[str] = None) -> Path:
    """Render a Manim scene to video.
    
    Args:
        script_path: Path to the Manim scene script
        scene_name: Name of the scene class to render
        out_path: Output path for the video. If provided, video will be moved to this location.
                  If not provided, returns the generated video from media/videos/
        quality: Manim quality setting (low, medium, high, production)
    
    Returns:
        Path to the generated video file (at out_path if specified, otherwise in media/videos/)
    """
    # Ensure FFMPEG from imageio-ffmpeg is in PATH for Manim
    ffmpeg_bin = os.getenv("FFMPEG_BINARY")
    env = os.environ.copy()
    if ffmpeg_bin and os.path.exists(ffmpeg_bin):
        ffmpeg_dir = str(Path(ffmpeg_bin).parent)
        if ffmpeg_dir not in env["PATH"]:
            env["PATH"] = ffmpeg_dir + os.pathsep + env["PATH"]

    quality_flag = {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "production": "-qp",
    }.get((quality or os.getenv("MANIM_QUALITY", "medium")).lower(), "-qm")

    output_flag: List[str] = []
    if out_path:
        output_flag = ["-o", out_path.name]

    cmd = [sys.executable, "-m", "manim", quality_flag, *output_flag, str(script_path), scene_name]
    
    # Add timeout to prevent indefinite hangs (15 minutes max)
    timeout_seconds = int(os.getenv("MANIM_TIMEOUT", "900"))  # 15 minutes default
    
    # Ensure proper encoding for subprocess streams
    if 'PYTHONIOENCODING' not in env:
        env['PYTHONIOENCODING'] = 'utf-8'
    
    try:
        print(f"[manim_adapter] Starting Manim render with {timeout_seconds}s timeout...")
        # Explicitly configure streams to prevent initialization errors on Windows
        result = subprocess.run(
            cmd,
            check=False,
            env=env,
            timeout=timeout_seconds,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print(f"[manim_adapter] Manim failed with return code {result.returncode}")
            if result.stdout:
                print(f"[manim_adapter] Manim stdout:\n{result.stdout}")
            if result.stderr:
                print(f"[manim_adapter] Manim stderr:\n{result.stderr}")
            raise RuntimeError(f"Manim rendering failed with exit code {result.returncode}. See logs above.")
        print(f"[manim_adapter] Manim render completed successfully")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Manim rendering exceeded timeout of {timeout_seconds} seconds. Try reducing scene complexity or quality.")

    if out_path:
        produced_dir = Path("media") / "videos" / script_path.stem
        candidates = sorted(produced_dir.rglob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if candidates:
            # Ensure output directory exists
            out_path.parent.mkdir(parents=True, exist_ok=True)
            # Use replace to move/rename the file to the exact output path
            candidates[0].replace(out_path)
            print(f"[manim_adapter] Video saved to {out_path}")
            return out_path
        else:
            raise RuntimeError(f"Manim generated a scene but could not locate output video in {produced_dir}")
    else:
        produced_dir = Path("media") / "videos" / script_path.stem
        candidates = sorted(produced_dir.rglob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not candidates:
            raise RuntimeError("Could not locate rendered video file.")
        final_output = candidates[0]
        print(f"[manim_adapter] Video saved to {final_output}")
        return final_output


def main():
    parser = argparse.ArgumentParser(description="Generate and render a Manim scene from structured JSON")
    parser.add_argument("json", help="Path to structured JSON (SolverOutput)")
    parser.add_argument("--out", dest="out", default=None, help="Output mp4 path")
    parser.add_argument("--quality", dest="quality", default=None, help="Manim quality: low|medium|high|production")
    parser.add_argument("--durations", dest="durations", default=None, help="Optional JSON file with per-scene durations (seconds)")
    args = parser.parse_args()

    data = json.loads(Path(args.json).read_text(encoding="utf-8"))
    scene_durations = None
    if args.durations:
        scene_durations = json.loads(Path(args.durations).read_text(encoding="utf-8"))
    script_text = generate_scene_script(data, scene_durations=scene_durations)

    gen_dir = Path("scripts") / "_generated"
    gen_dir.mkdir(parents=True, exist_ok=True)
    script_path = gen_dir / "generated_scene.py"
    script_path.write_text(script_text, encoding="utf-8")

    out_path = Path(args.out) if args.out else None
    video = render_with_manim(script_path, "GeneratedScene", out_path=out_path, quality=args.quality)
    print(f"Rendered video: {video}")


if __name__ == "__main__":
    main()
