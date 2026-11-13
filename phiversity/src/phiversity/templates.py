"""Bundled Manim templates: the intro title card and offline demo lectures.

The bundled lectures make the full pipeline runnable without any API key:
each ships pre-written narration and Manim code. Currently available:
"pythagoras" (the Pythagorean theorem) and "fma" (Newton's second law).
"""

from __future__ import annotations

import re

INTRO_CODE_TEMPLATE = '''from manim import *


class IntroTitle(Scene):
    def construct(self):
        title = Text({title!r}, font_size=52, gradient=(T.variable, T.result_intermediate))
        title.to_edge(UP, buff=1.2)
        subtitle = Text("a Phiversity lecture", font_size=28, color=T.text_muted)
        subtitle.next_to(title, DOWN, buff=0.85)
        underline = Underline(title, buff=0.35)
        self.play(Write(title), run_time=2.0)
        self.play(Create(underline), run_time=0.8)
        self.play(FadeIn(subtitle, shift=0.3 * UP), run_time=0.6)
        self.wait({wait:.2f})
        self.play(FadeOut(title), FadeOut(underline), FadeOut(subtitle),
                  run_time=0.8)
'''


# A short "turning page" clip: a sheet covers the frame (masking the cut),
# then flips over to the left spine. The pipeline normalizes it and splices
# one copy between every pair of segments.
PAGE_FLIP_CODE = r'''from manim import *


class PageFlip(Scene):
    def construct(self):
        w = config.frame_width
        h = config.frame_height
        page = Rectangle(width=w, height=h, fill_color=T.panel,
                          fill_opacity=1, stroke_width=0)
        edge = Line(UP * h / 2, DOWN * h / 2)
        edge.set_stroke(T.variable, 6)
        edge.move_to(RIGHT * w / 2)
        sheet = VGroup(page, edge)
        self.add(sheet)
        self.wait(0.25)
        spine = LEFT * w / 2
        self.play(
            sheet.animate.stretch(0.02, 0, about_point=spine),
            run_time=0.65,
            rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.1)
'''


def intro_segment(title: str, audio_duration: float) -> dict:
    """Intro title card timed to a spoken one-liner."""
    wait = max(0.4, audio_duration - 4.2)
    code = INTRO_CODE_TEMPLATE.format(title=title, wait=wait)
    narration = f"Welcome. In this lecture: {title}."
    return {"scene_name": "IntroTitle", "code": code,
            "narration": narration}


# ---------------------------------------------------------------------------
# Offline demo: the Pythagorean theorem
# ---------------------------------------------------------------------------

PYTHAGOREAN_TITLE = "The Pythagorean Theorem"

PYTHAGOREAN_SEGMENTS = [
    {
        "narration": "The Pythagorean theorem is one of the oldest and most "
                     "useful results in all of geometry. It tells us something "
                     "special about right triangles, triangles with one "
                     "ninety degree angle.",
        "code": r'''from manim import *


class Segment0(Scene):
    def construct(self):
        header = Text("The Pythagorean Theorem", font_size=40, color=T.variable)
        header.to_edge(UP, buff=0.6)
        triangle = Polygon(ORIGIN, RIGHT * 3, RIGHT * 3 + UP * 2)
        triangle.set_stroke(T.text_primary, 3).set_fill(T.panel, 0.6)
        triangle.shift(DOWN * 0.4 + LEFT * 0.5)
        right = Square(side_length=0.28, stroke_color=T.highlight_primary, stroke_width=3)
        right.move_to(triangle.get_vertices()[1] + LEFT * 0.14 + UP * 0.14)
        label = Text("one angle is exactly 90 degrees", font_size=26, color=T.highlight_primary)
        label.next_to(triangle, DOWN, buff=0.5)
        self.play(Write(header), run_time=1.6)
        self.play(DrawBorderThenFill(triangle), run_time=1.6)
        self.play(Create(right), run_time=0.7)
        self.play(Write(label), run_time=1.4)
        self.wait(2.6)
''',
    },
    {
        "narration": "The theorem says: take the two shorter sides, call them "
                     "a and b, and the longest side, opposite the right "
                     "angle, call it c. Then a squared plus b squared equals "
                     "c squared.",
        "code": r'''from manim import *


class Segment1(Scene):
    def construct(self):
        tri = Polygon(ORIGIN, RIGHT * 3.2, RIGHT * 3.2 + UP * 2.2)
        tri.set_stroke(T.text_primary, 3).set_fill(T.panel, 0.5)
        tri.shift(LEFT * 3.4 + DOWN * 0.3)
        verts = tri.get_vertices()
        a = MathTex("a", color=T.stable_state, font_size=48)
        a.move_to((verts[0] + verts[1]) / 2 + DOWN * 0.35)
        b = MathTex("b", color=T.vector_force, font_size=48)
        b.move_to((verts[1] + verts[2]) / 2 + RIGHT * 0.35)
        c = MathTex("c", color=T.highlight_primary, font_size=48)
        c.move_to((verts[2] + verts[0]) / 2 + UP * 0.3 + LEFT * 0.35)
        formula = MathTex("a^2 + b^2 = c^2", font_size=60)
        formula.to_edge(RIGHT, buff=1.2).shift(UP * 1.6)
        box = SurroundingRectangle(formula, buff=0.35, color=T.highlight_primary)
        note = Text("the longest side is the hypotenuse", font_size=24, color=T.text_muted)
        note.next_to(box, DOWN, buff=0.6)
        self.play(DrawBorderThenFill(tri), run_time=1.5)
        self.play(Write(a), Write(b), Write(c), run_time=1.2)
        self.play(Write(formula), run_time=1.6)
        self.play(Create(box), run_time=0.8)
        self.play(Write(note), run_time=1.2)
        self.wait(2.4)
''',
    },
    {
        "narration": "Here is a concrete example: a right triangle with legs "
                     "three and four. Nine plus sixteen equals twenty five, "
                     "and the square root of twenty five is exactly five.",
        "code": r'''from manim import *


class Segment2(Scene):
    def construct(self):
        title = Text("Example: the 3-4-5 triangle", font_size=36, color=T.variable)
        title.to_edge(UP, buff=0.5)
        tri = Polygon(ORIGIN, RIGHT * 3, RIGHT * 3 + UP * 2.2)
        tri.set_stroke(T.text_primary, 3).set_fill(T.panel, 0.5)
        tri.shift(LEFT * 3.6 + DOWN * 0.4)
        verts = tri.get_vertices()
        l1 = MathTex("3").next_to(verts[1], DOWN, buff=0.25)
        l2 = MathTex("4").next_to(verts[2], RIGHT, buff=0.25)
        l3 = MathTex("5").move_to((verts[0] + verts[2]) / 2 + LEFT * 0.45 + DOWN * 0.35)
        calc = MathTex("3^2 + 4^2 = 9 + 16 = 25", font_size=48)
        calc.to_edge(RIGHT, buff=1.0).shift(UP * 1.0)
        result = MathTex(r"c = \sqrt{25} = 5", font_size=54, color=T.highlight_primary)
        result.next_to(calc, DOWN, buff=0.8)
        box = SurroundingRectangle(result, buff=0.3, color=T.highlight_primary)
        self.play(DrawBorderThenFill(tri), run_time=1.4)
        self.play(Write(l1), Write(l2), Write(l3), run_time=1.0)
        self.play(Write(calc), run_time=1.8)
        self.play(Write(result), run_time=1.6)
        self.play(Create(box), run_time=0.7)
        self.wait(2.0)
''',
    },
    {
        "narration": "And that is the Pythagorean theorem in a nutshell. "
                     "Whenever you see a right triangle, remember: the "
                     "squares of the legs always add up to the square of the "
                     "hypotenuse.",
        "code": r'''from manim import *


class Segment3(Scene):
    def construct(self):
        formula = MathTex("a^2 + b^2 = c^2", font_size=72)
        formula.move_to(UP * 0.9)
        glow = SurroundingRectangle(formula, buff=0.5, color=T.variable)
        takeaway = Text("only true for right triangles", font_size=30, color=T.text_muted)
        takeaway.next_to(glow, DOWN, buff=0.7)
        thanks = Text("thanks for watching", font_size=26, color=T.text_muted)
        thanks.next_to(takeaway, DOWN, buff=0.6)
        self.play(Write(formula), run_time=2.0)
        self.play(Create(glow), run_time=1.0)
        self.play(FadeIn(takeaway, shift=0.4 * UP), run_time=0.9)
        self.play(FadeIn(thanks, shift=0.4 * UP), run_time=0.9)
        self.wait(2.2)
''',
    },
]


PYTHAGOREAN_QUESTION = {
    "display": "A right triangle has legs $3$ and $4$. "
               "How long is the hypotenuse?",
    "speech": "A right triangle has legs three and four. "
              "How long is the hypotenuse?",
}

PYTHAGOREAN_QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION", font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.0)
        line = Underline(badge, buff=0.15)
        row1 = VGroup(
            Text("A right triangle has legs ", font_size=32),
            MathTex("3", font_size=36, color=T.stable_state),
            Text(" and ", font_size=32),
            MathTex("4", font_size=36, color=T.stable_state),
            Text(".", font_size=32),
        ).arrange(RIGHT, buff=0.12)
        row2 = Text("How long is the hypotenuse?", font_size=32)
        rows = VGroup(row1, row2).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        rows.move_to(UP * 1.5)
        tri = Polygon(ORIGIN, RIGHT * 2.6, RIGHT * 2.6 + UP * 1.9)
        tri.set_stroke(T.text_primary, 3).set_fill(T.panel, 0.5)
        tri.move_to(DOWN * 1.8)
        verts = tri.get_vertices()
        l3 = MathTex("3", font_size=32, color=T.stable_state)
        l3.next_to(verts[1], DOWN, buff=0.2)
        l4 = MathTex("4", font_size=32, color=T.stable_state)
        l4.next_to(verts[2], RIGHT, buff=0.2)
        q = MathTex("?", font_size=40, color=T.highlight_primary)
        q.move_to((verts[0] + verts[2]) / 2 + UP * 0.25 + LEFT * 0.3)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.8)
        self.play(Write(row1), run_time=1.6)
        self.play(Write(row2), run_time=1.2)
        self.play(DrawBorderThenFill(tri), run_time=1.2)
        self.play(Write(l3), Write(l4), Write(q), run_time=1.0)
        self.wait(0.8)
        self.play(FadeOut(VGroup(tri, l3, l4, q)), run_time=0.7)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.78).to_edge(UP, buff=0.25),
                  run_time=1.0)
        self.wait(0.6)
'''


# ---------------------------------------------------------------------------
# Offline demo: Newton's second law, F = ma
# ---------------------------------------------------------------------------

FMA_TITLE = "Newton's Second Law: F = ma"

FMA_SEGMENTS = [
    {
        "narration": "Newton's second law is one of the most famous equations "
                     "in all of physics. It says that the force you apply to "
                     "an object equals its mass times its acceleration.",
        "code": r'''from manim import *


class Segment0(Scene):
    def construct(self):
        title = Text("Newton's Second Law", font_size=40, color=T.variable)
        title.to_edge(UP, buff=0.7)
        equation = MathTex(r"F = m \, a", font_size=96)
        equation.move_to(ORIGIN)
        box = SurroundingRectangle(equation, buff=0.5, color=T.highlight_primary)
        caption = Text("force equals mass times acceleration",
                       font_size=28, color=T.text_muted)
        caption.next_to(box, DOWN, buff=0.6)
        self.play(Write(title), run_time=1.8)
        self.play(Write(equation), run_time=2.2)
        self.play(Create(box), run_time=0.9)
        self.play(FadeIn(caption, shift=0.3 * UP), run_time=1.0)
        self.wait(3.0)
''',
    },
    {
        "narration": "Here F is the net force in newtons, m is the mass in "
                     "kilograms, and a is the acceleration in meters per "
                     "second squared.",
        "code": r'''from manim import *


class Segment1(Scene):
    def construct(self):
        eq = MathTex(r"\vec{F}", "=", "m", r"\vec{a}", font_size=80)
        eq.move_to(UP * 1.2)
        eq[0].set_color(T.highlight_primary)
        eq[2].set_color(T.stable_state)
        eq[3].set_color(T.vector_force)
        rows = VGroup(
            VGroup(MathTex(r"\vec{F}", font_size=42, color=T.highlight_primary),
                   Text("net force, in newtons",
                        font_size=28, color=T.text_muted)).arrange(RIGHT, buff=0.45),
            VGroup(MathTex("m", font_size=42, color=T.stable_state),
                   Text("mass, in kilograms",
                        font_size=28, color=T.text_muted)).arrange(RIGHT, buff=0.45),
            VGroup(MathTex(r"\vec{a}", font_size=42, color=T.vector_force),
                   Text("acceleration, in m/s\u00b2",
                        font_size=28, color=T.text_muted)).arrange(RIGHT, buff=0.45),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        rows.next_to(eq, DOWN, buff=0.9)
        self.play(Write(eq), run_time=2.0)
        self.play(Write(rows[0]), run_time=1.5)
        self.play(Write(rows[1]), run_time=1.5)
        self.play(Write(rows[2]), run_time=1.5)
        self.wait(3.0)
''',
    },
    {
        "narration": "Let's see it in action. We push a two kilogram cart "
                     "with a force of ten newtons. Ten divided by two gives "
                     "an acceleration of five meters per second squared.",
        "code": r'''from manim import *


class Segment2(Scene):
    def construct(self):
        title = Text("Example: pushing a cart", font_size=34, color=T.variable)
        title.to_edge(UP, buff=0.5)
        body = RoundedRectangle(corner_radius=0.12, width=2.0, height=0.8)
        body.set_stroke(T.text_primary, 3).set_fill(T.panel, 0.8)
        w1 = Circle(radius=0.16).set_stroke(T.text_primary, 3).set_fill(T.atom_carbon, 1)
        w2 = w1.copy()
        cart = VGroup(body, w1, w2)
        body.move_to(LEFT * 3.1 + DOWN * 0.3)
        w1.move_to(body.get_bottom() + RIGHT * 0.55 + DOWN * 0.05)
        w2.move_to(body.get_bottom() + LEFT * 0.55 + DOWN * 0.05)
        mass_label = MathTex(r"m = 2\,\text{kg}", font_size=38)
        mass_label.next_to(body, UP, buff=0.25)
        arrow = Arrow(LEFT * 1.9, LEFT * 1.15, buff=0, color=T.highlight_primary,
                      stroke_width=7)
        arrow.next_to(body, LEFT, buff=0.3)
        arrow.shift(DOWN * 0.1)
        f_label = MathTex(r"F = 10\,\text{N}", font_size=38, color=T.highlight_primary)
        f_label.next_to(arrow, UP, buff=0.2)
        calc1 = MathTex(r"a = \frac{F}{m} = \frac{10\,\text{N}}{2\,\text{kg}}",
                        font_size=44)
        calc2 = MathTex(r"a = 5\,\text{m/s}^2", font_size=54, color=T.highlight_primary)
        calcs = VGroup(calc1, calc2).arrange(DOWN, buff=0.7)
        calcs.move_to(RIGHT * 2.6 + DOWN * 0.2)
        box = SurroundingRectangle(calc2, buff=0.3, color=T.highlight_primary)
        self.play(Write(title), run_time=1.3)
        self.play(DrawBorderThenFill(cart), Write(mass_label), run_time=1.6)
        self.play(GrowArrow(arrow), Write(f_label), run_time=1.2)
        self.play(cart.animate(rate_func=smooth).shift(RIGHT * 0.8),
                  run_time=1.1)
        self.play(Write(calc1), run_time=1.8)
        self.play(Write(calc2), run_time=1.6)
        self.play(Create(box), run_time=0.7)
        self.wait(2.2)
''',
    },
    {
        "narration": "The law also tells us direction: the acceleration "
                     "always points along the net force. Double the force and "
                     "you double the acceleration; double the mass and you cut "
                     "it in half. That is the heart of F equals m a.",
        "code": r'''from manim import *


class Segment3(Scene):
    def construct(self):
        f_arrow = Arrow(LEFT * 2.2, ORIGIN, buff=0, color=T.highlight_primary,
                        stroke_width=9, max_tip_length_to_length_ratio=0.3)
        a_arrow = Arrow(LEFT * 2.2, ORIGIN, buff=0, color=T.vector_force,
                        stroke_width=9, max_tip_length_to_length_ratio=0.3)
        group = VGroup(f_arrow, a_arrow).arrange(DOWN, buff=0.6)
        group.move_to(UP * 1.2)
        f_label = MathTex(r"\vec{F}", font_size=48, color=T.highlight_primary)
        f_label.next_to(f_arrow, LEFT, buff=0.25)
        a_label = MathTex(r"\vec{a}", font_size=48, color=T.vector_force)
        a_label.next_to(a_arrow, LEFT, buff=0.25)
        note = Text("the acceleration points along the net force",
                    font_size=26, color=T.text_muted)
        note.next_to(group, DOWN, buff=0.5)
        props = VGroup(
            MathTex(r"2F \Rightarrow 2a", font_size=44),
            MathTex(r"2m \Rightarrow a/2", font_size=44),
        ).arrange(RIGHT, buff=1.2)
        props.next_to(note, DOWN, buff=0.55)
        self.play(GrowArrow(f_arrow), Write(f_label), run_time=1.2)
        self.play(GrowArrow(a_arrow), Write(a_label), run_time=1.2)
        self.play(Write(note), run_time=1.2)
        self.play(Write(props[0]), run_time=1.2)
        self.play(Write(props[1]), run_time=1.2)
        self.wait(1.8)
        self.play(FadeOut(VGroup(f_arrow, a_arrow, f_label, a_label,
                                 note, props)), run_time=0.8)
        final = MathTex(r"F = m\,a", font_size=96)
        final.move_to(ORIGIN)
        thanks = Text("thanks for watching", font_size=24, color=T.text_muted)
        thanks.next_to(final, DOWN, buff=0.8)
        self.play(Write(final), run_time=1.8)
        self.play(FadeIn(thanks, shift=0.3 * UP), run_time=0.8)
        self.wait(1.6)
''',
    },
]

FMA_QUESTION = {
    "display": "A net force $F$ acts on an object of mass $m$. "
               "What is its acceleration $a$?",
    "speech": "A net force F acts on an object of mass m. "
              "What is its acceleration?",
}

FMA_QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION", font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.0)
        line = Underline(badge, buff=0.15)
        row1 = VGroup(
            Text("A net force ", font_size=32),
            MathTex("F", font_size=36, color=T.highlight_primary),
            Text(" acts on an object of mass ", font_size=32),
            MathTex("m", font_size=36, color=T.stable_state),
            Text(".", font_size=32),
        ).arrange(RIGHT, buff=0.12)
        row2 = VGroup(
            Text("What is its acceleration ", font_size=32),
            MathTex("a", font_size=36, color=T.vector_force),
            Text("?", font_size=32),
        ).arrange(RIGHT, buff=0.12)
        rows = VGroup(row1, row2).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        rows.move_to(UP * 1.5)
        block = Square(side_length=1.3)
        block.set_stroke(T.text_primary, 3).set_fill(T.panel, 0.6)
        block.move_to(DOWN * 1.7)
        push = Arrow(block.get_left() + LEFT * 1.6,
                     block.get_left() + LEFT * 0.1, buff=0,
                     color=T.highlight_primary, stroke_width=7)
        push.shift(UP * 0.05)
        f_lab = MathTex("F", font_size=40, color=T.highlight_primary)
        f_lab.next_to(push, UP, buff=0.15)
        m_lab = MathTex("m", font_size=40, color=T.stable_state)
        m_lab.next_to(block, DOWN, buff=0.25)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.8)
        self.play(Write(row1), run_time=1.6)
        self.play(Write(row2), run_time=1.2)
        self.play(DrawBorderThenFill(block), run_time=0.9)
        self.play(GrowArrow(push), Write(f_lab), Write(m_lab), run_time=1.1)
        self.wait(0.8)
        self.play(FadeOut(VGroup(block, push, f_lab, m_lab)), run_time=0.7)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.78).to_edge(UP, buff=0.25),
                  run_time=1.0)
        self.wait(0.6)
'''


# ---------------------------------------------------------------------------
# Offline demo: friction on a moving car
# ---------------------------------------------------------------------------

CAR_FRICTION_TITLE = "Car Friction: Forces on the Road"

CAR_FRICTION_QUESTION = {
    "display": "A car is moving along a road. The friction between the "
               "car and the road is $f_k = 5\\,\\mathrm{N}$. "
               "How does friction affect the car's motion?",
    "speech": "A car is moving along a road. The friction between the "
              "car and the road is five newtons. How does friction affect "
              "the car's motion?",
}

CAR_FRICTION_QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION", font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.0)
        line = Underline(badge, buff=0.15)
        row1 = Text("A car is moving along a road.", font_size=30)
        row2 = VGroup(
            Text("The friction between the car and the road is ",
                 font_size=28),
            MathTex(r"f_k = 5\,\mathrm{N}", font_size=32, color=T.highlight_primary),
            Text(".", font_size=28),
        ).arrange(RIGHT, buff=0.12)
        row3 = Text("How does friction affect the car's motion?",
                    font_size=30)
        rows = VGroup(row1, row2, row3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        rows.move_to(UP * 1.35)
        road = Line(LEFT * 5.5, RIGHT * 5.5)
        road.set_stroke(T.text_muted, 8)
        road.move_to(DOWN * 2.35)
        body = RoundedRectangle(corner_radius=0.14, width=1.7, height=0.5)
        body.set_stroke(T.text_primary, 3).set_fill(T.panel, 0.9)
        cabin = RoundedRectangle(corner_radius=0.1, width=0.8, height=0.32)
        cabin.set_stroke(T.text_primary, 3).set_fill(T.variable, 0.9)
        w1 = Circle(radius=0.14)
        w1.set_stroke(T.text_primary, 3).set_fill(T.atom_carbon, 1)
        w2 = w1.copy()
        car = VGroup(body, cabin, w1, w2)
        body.move_to(LEFT * 0.6 + DOWN * 1.85)
        cabin.move_to(body.get_top() + UP * 0.14)
        w1.move_to(body.get_bottom() + LEFT * 0.45 + DOWN * 0.06)
        w2.move_to(body.get_bottom() + RIGHT * 0.45 + DOWN * 0.06)
        vel = Arrow(car.get_right() + RIGHT * 0.3,
                    car.get_right() + RIGHT * 1.3, buff=0,
                    color=T.stable_state, stroke_width=6)
        v_lab = MathTex("v", font_size=38, color=T.stable_state)
        v_lab.next_to(vel, UP, buff=0.12)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(row1), run_time=1.1)
        self.play(Write(row2), run_time=1.5)
        self.play(Write(row3), run_time=1.1)
        self.play(Create(road), FadeIn(car, shift=0.3 * DOWN), run_time=1.0)
        self.play(GrowArrow(vel), Write(v_lab), run_time=0.9)
        self.play(car.animate(rate_func=linear).shift(RIGHT * 1.6),
                  vel.animate.shift(RIGHT * 1.6),
                  v_lab.animate.shift(RIGHT * 1.6), run_time=1.2)
        self.wait(0.9)
        self.play(FadeOut(VGroup(road, car, vel, v_lab)), run_time=0.7)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.78).to_edge(UP, buff=0.25),
                  run_time=1.0)
        self.wait(0.6)
'''

CAR_FRICTION_SEGMENTS = [
    {
        "narration": "Here is the car rolling forward. Now watch closely "
                     "at the road, because the interesting physics happens "
                     "right where the rubber meets the road. Zooming into "
                     "the tire, friction acts at the contact patch, "
                     "pointing backward, opposite to the motion, with a "
                     "magnitude of five newtons.",
        "code": r'''from manim import *


class Segment0(MovingCameraScene):
    def construct(self):
        road = Line(LEFT * 6.5, RIGHT * 6.5)
        road.set_stroke(T.text_muted, 10)
        road.move_to(DOWN * 1.8)
        body = RoundedRectangle(corner_radius=0.15, width=1.9, height=0.6)
        body.set_stroke(T.text_primary, 3).set_fill(T.panel, 0.9)
        cabin = RoundedRectangle(corner_radius=0.12, width=0.9, height=0.4)
        cabin.set_stroke(T.text_primary, 3).set_fill(T.variable, 0.9)
        w1 = Circle(radius=0.17)
        w1.set_stroke(T.text_primary, 3).set_fill(T.atom_carbon, 1)
        w2 = w1.copy()
        car = VGroup(body, cabin, w1, w2)
        body.move_to(LEFT * 1.0 + UP * 0.5)
        cabin.move_to(body.get_top() + UP * 0.17)
        w1.move_to(body.get_bottom() + LEFT * 0.5 + DOWN * 0.08)
        w2.move_to(body.get_bottom() + RIGHT * 0.5 + DOWN * 0.08)
        vel = Arrow(car.get_right() + RIGHT * 0.3,
                    car.get_right() + RIGHT * 1.3, buff=0,
                    color=T.stable_state, stroke_width=6)
        v_lab = MathTex("v", font_size=40, color=T.stable_state)
        v_lab.next_to(vel, UP, buff=0.12)
        self.add(road)
        self.play(FadeIn(car, shift=0.3 * DOWN), run_time=0.8)
        self.play(GrowArrow(vel), Write(v_lab), run_time=0.9)
        self.play(car.animate(rate_func=linear).shift(RIGHT * 2.4),
                  run_time=3.2)
        self.wait(0.5)
        zoom_rect = SurroundingRectangle(w1, buff=0.4, color=T.highlight_primary)
        self.play(Create(zoom_rect), run_time=0.8)
        frame = self.camera.frame
        self.play(frame.animate.set(width=4.4)
                  .move_to(w1.get_center() + DOWN * 0.25), run_time=1.6)
        self.wait(0.4)
        contact = w1.get_bottom() + DOWN * 0.12
        f_arrow = Arrow(contact, contact + LEFT * 1.0, buff=0,
                        color=T.vector_force, stroke_width=6)
        f_label = MathTex(r"f_k = 5\,\mathrm{N}", font_size=34, color=T.vector_force)
        f_label.next_to(f_arrow, UP, buff=0.25)
        note = Text("friction opposes the motion", font_size=22,
                    color=T.text_muted)
        note.next_to(f_label, UP, buff=0.3)
        self.play(GrowArrow(f_arrow), run_time=1.0)
        self.wait(0.3)
        self.play(Write(f_label), run_time=1.2)
        self.play(Write(note), run_time=1.2)
        self.wait(4.0)
''',
    },
    {
        "narration": "In the free body view, the car is pushed by its "
                     "weight downward, the normal force from the road "
                     "upward, and friction pointing backward. Friction is "
                     "the only horizontal force, so it is the net force, "
                     "and by Newton's second law the car decelerates. On a "
                     "velocity time graph, the speed falls along a "
                     "straight line.",
        "code": r'''from manim import *


class Segment1(Scene):
    def construct(self):
        body = RoundedRectangle(corner_radius=0.14, width=1.7, height=0.55)
        body.set_stroke(T.text_primary, 3).set_fill(T.panel, 0.35)
        cabin = RoundedRectangle(corner_radius=0.1, width=0.8, height=0.34)
        cabin.set_stroke(T.text_primary, 3).set_fill(T.variable, 0.35)
        w1 = Circle(radius=0.15)
        w1.set_stroke(T.text_primary, 3).set_fill(T.atom_carbon, 1)
        w2 = w1.copy()
        car = VGroup(body, cabin, w1, w2)
        body.move_to(LEFT * 3.9 + UP * 0.3)
        cabin.move_to(body.get_top() + UP * 0.16)
        w1.move_to(body.get_bottom() + LEFT * 0.45 + DOWN * 0.07)
        w2.move_to(body.get_bottom() + RIGHT * 0.45 + DOWN * 0.07)
        center = car.get_center()
        weight = Arrow(center, center + DOWN * 1.2, buff=0,
                       color=T.vector_force, stroke_width=5)
        w_label = MathTex("W", font_size=34, color=T.vector_force)
        w_label.next_to(weight, DOWN, buff=0.12)
        normal = Arrow(center, center + UP * 1.2, buff=0,
                       color=T.variable, stroke_width=5)
        n_label = MathTex("N", font_size=34, color=T.variable)
        n_label.next_to(normal, UP, buff=0.12)
        friction = Arrow(center + LEFT * 0.85 + UP * 0.1,
                          center + LEFT * 1.85 + UP * 0.1, buff=0,
                          color=T.highlight_primary, stroke_width=5)
        f_label = MathTex(r"f_k = 5\,\mathrm{N}", font_size=32,
                          color=T.highlight_primary)
        f_label.next_to(friction, UP, buff=0.15)
        axes = Axes(x_range=[0, 5, 1], y_range=[0, 4, 1],
                    x_length=4.2, y_length=3.0,
                    axis_config={"include_numbers": True,
                                 "font_size": 22})
        axes.move_to(RIGHT * 3.1 + DOWN * 0.7)
        x_lab = Text("t (s)", font_size=22, color=T.text_muted)
        x_lab.next_to(axes.x_axis, RIGHT, buff=0.15)
        y_lab = Text("v (m/s)", font_size=22, color=T.text_muted)
        y_lab.next_to(axes.y_axis, UP, buff=0.12)
        line = axes.plot(lambda x: 3.2 - 0.55 * x, x_range=[0, 4.6],
                         color=T.stable_state, stroke_width=5)
        slope_note = Text("v falls: friction decelerates the car",
                          font_size=22, color=T.text_muted)
        slope_note.next_to(axes, DOWN, buff=0.35)
        net_note = Text("only horizontal force, so it is the net force",
                        font_size=22, color=T.text_muted)
        net_note.next_to(w_label, DOWN, buff=0.5)
        self.play(FadeIn(car), run_time=1.0)
        self.play(GrowArrow(weight), Write(w_label), run_time=1.2)
        self.play(GrowArrow(normal), Write(n_label), run_time=1.2)
        self.play(GrowArrow(friction), Write(f_label), run_time=1.2)
        self.wait(0.6)
        self.play(Write(net_note), run_time=1.4)
        self.wait(0.5)
        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.8)
        self.play(Create(line), run_time=2.0)
        self.wait(0.4)
        self.play(Write(slope_note), run_time=1.2)
        self.wait(6.0)
''',
    },
    {
        "narration": "So friction never speeds a car up. It always pushes "
                     "against the direction of sliding. The five newton "
                     "friction force acts backward, the velocity line "
                     "slopes down, and the car slows down. That is how "
                     "friction shapes the motion of everything that moves.",
        "code": r'''from manim import *


class Segment2(MovingCameraScene):
    def construct(self):
        frame = self.camera.frame
        road = Line(LEFT * 6.5, RIGHT * 6.5)
        road.set_stroke(T.text_muted, 10)
        road.move_to(DOWN * 1.8)
        body = RoundedRectangle(corner_radius=0.15, width=1.9, height=0.6)
        body.set_stroke(T.text_primary, 3).set_fill(T.panel, 0.9)
        cabin = RoundedRectangle(corner_radius=0.12, width=0.9, height=0.4)
        cabin.set_stroke(T.text_primary, 3).set_fill(T.variable, 0.9)
        w1 = Circle(radius=0.17)
        w1.set_stroke(T.text_primary, 3).set_fill(T.atom_carbon, 1)
        w2 = w1.copy()
        car = VGroup(body, cabin, w1, w2)
        body.move_to(LEFT * 1.0 + UP * 0.5)
        cabin.move_to(body.get_top() + UP * 0.17)
        w1.move_to(body.get_bottom() + LEFT * 0.5 + DOWN * 0.08)
        w2.move_to(body.get_bottom() + RIGHT * 0.5 + DOWN * 0.08)
        contact = w1.get_bottom() + DOWN * 0.12
        f_arrow = Arrow(contact, contact + LEFT * 0.9, buff=0,
                        color=T.vector_force, stroke_width=6)
        frame.set(width=4.4).move_to(w1.get_center() + DOWN * 0.25)
        self.add(road, car, f_arrow)
        self.wait(0.9)
        self.play(frame.animate.set(width=14.0).move_to(ORIGIN),
                  run_time=2.0)
        self.wait(0.4)
        takeaway = Text("friction always opposes motion", font_size=36,
                        color=T.variable)
        takeaway.to_edge(UP, buff=0.7)
        box = SurroundingRectangle(takeaway, buff=0.35, color=T.highlight_primary)
        fk = MathTex(r"f_k = 5\,\mathrm{N}", font_size=44, color=T.vector_force)
        fk.next_to(box, DOWN, buff=0.8)
        v_arrow = Arrow(LEFT * 1.0, RIGHT * 1.0, buff=0, color=T.stable_state,
                        stroke_width=6)
        v_arrow.next_to(car, RIGHT, buff=0.7)
        v_lab = MathTex("v", font_size=38, color=T.stable_state)
        v_lab.next_to(v_arrow, UP, buff=0.12)
        self.play(Write(takeaway), run_time=1.6)
        self.play(Create(box), run_time=1.0)
        self.wait(0.3)
        self.play(Write(fk), run_time=1.4)
        self.play(GrowArrow(v_arrow), Write(v_lab), run_time=1.2)
        thanks = Text("thanks for watching", font_size=24, color=T.text_muted)
        thanks.next_to(v_arrow, DOWN, buff=0.7)
        self.play(FadeIn(thanks, shift=0.3 * UP), run_time=1.0)
        self.wait(5.5)
''',
    },
]


# ---------------------------------------------------------------------------
# Offline demo: two-block spring system with separation
# ---------------------------------------------------------------------------

SPRING_BLOCKS_TITLE = "Two-Block Spring System"

SPRING_BLOCKS_QUESTION = {
    "display": "Block A ($m_A = 0.3\\,\\mathrm{kg}$) is fixed to a wall by a "
               "spring ($k = 120\\,\\mathrm{N/m}$); block B "
               "($m_B = 0.1\\,\\mathrm{kg}$) rests against A, unattached. "
               "The spring is compressed $x_0 = 0.1\\,\\mathrm{m}$ and "
               "released from rest. Find the speed at natural length, A's "
               "maximum speed after separation, the amplitude, the period, "
               "and the energy lost.",
    "speech": "Block A, zero point three kilograms, is fixed to a wall by "
              "a spring with spring constant one hundred twenty newtons "
              "per meter. Block B, zero point one kilograms, rests "
              "against A, not attached. The spring is compressed zero "
              "point one meters and released from rest. Find the speed at "
              "natural length, A's maximum speed after separation, the "
              "amplitude, the period, and the energy lost.",
}

# Geometry shared by the scenes (1 scene unit = 0.1 m): the wall sits at
# x = -4.9, the natural spring spans 2.0 units, block A is a 0.9 square,
# block B a 0.7 square touching A.

SPRING_BLOCKS_QUESTION_CODE = r'''from manim import *


def _spring(start, end, amp=0.12, coils=7):
    pts = [start]
    n = 2 * coils
    for i in range(1, n):
        off = UP * amp if i % 2 else DOWN * amp
        pts.append(start + (end - start) * (i / n) + off)
    pts.append(end)
    m = VMobject()
    m.set_points_as_corners(pts)
    m.set_stroke(T.text_muted, 4)
    return m


def _base():
    wall = Line(LEFT * 4.9 + DOWN * 3.05, LEFT * 4.9 + UP * 0.6)
    wall.set_stroke(T.text_muted, 8)
    floor = Line(LEFT * 4.9 + DOWN * 3.05, RIGHT * 4.8 + DOWN * 3.05)
    floor.set_stroke(T.atom_carbon, 4)
    note = Text("frictionless", font_size=22, color=T.text_muted)
    note.next_to(floor, DOWN, buff=0.15)
    return VGroup(wall, floor, note)


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION", font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.0)
        line = Underline(badge, buff=0.15)
        row1 = VGroup(
            Text("Block A (", font_size=26),
            MathTex(r"m_A = 0.3\,\mathrm{kg}", font_size=28, color=T.highlight_primary),
            Text(") is fixed to a wall by a spring (", font_size=26),
            MathTex(r"k = 120\,\mathrm{N/m}", font_size=28, color=T.variable),
            Text(");", font_size=26),
        ).arrange(RIGHT, buff=0.1)
        row2 = VGroup(
            Text("block B (", font_size=26),
            MathTex(r"m_B = 0.1\,\mathrm{kg}", font_size=28, color=T.stable_state),
            Text(") rests against A, unattached.", font_size=26),
        ).arrange(RIGHT, buff=0.1)
        row3 = VGroup(
            Text("The spring is compressed ", font_size=26),
            MathTex(r"x_0 = 0.1\,\mathrm{m}", font_size=28, color=T.vector_force),
            Text(" and released from rest.", font_size=26),
        ).arrange(RIGHT, buff=0.1)
        row4 = Text("Find: speed at natural length, A's max speed after "
                    "separation,", font_size=24, color=T.text_muted)
        row5 = Text("amplitude, period, and energy lost to the "
                    "environment.", font_size=24, color=T.text_muted)
        rows = VGroup(row1, row2, row3, row4, row5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        rows.move_to(UP * 0.75)
        base = _base()
        spring = _spring(LEFT * 4.9 + DOWN * 2.55,
                         LEFT * 2.9 + DOWN * 2.55)
        blockA = Square(side_length=0.9)
        blockA.set_stroke(T.text_primary, 3).set_fill(T.panel, 0.9)
        blockA.move_to(LEFT * 2.45 + DOWN * 2.55)
        labA = Text("A", font_size=28, color=T.text_primary).move_to(blockA)
        blockB = Square(side_length=0.7)
        blockB.set_stroke(T.text_primary, 3).set_fill(GREEN_E, 0.9)
        blockB.move_to(LEFT * 1.65 + DOWN * 2.65)
        labB = Text("B", font_size=24, color=T.text_primary).move_to(blockB)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(row1), run_time=2.2)
        self.play(Write(row2), run_time=1.8)
        self.play(Write(row3), run_time=2.0)
        self.play(Write(row4), run_time=1.5)
        self.play(Write(row5), run_time=1.5)
        self.wait(0.5)
        self.play(Create(base[0]), Create(base[1]), Write(base[2]),
                  run_time=1.3)
        self.play(Create(spring), DrawBorderThenFill(blockA),
                  DrawBorderThenFill(blockB), Write(labA), Write(labB),
                  run_time=1.9)
        self.play(Transform(spring, _spring(LEFT * 4.9 + DOWN * 2.55,
                                            LEFT * 3.9 + DOWN * 2.55)),
                  blockA.animate(rate_func=rate_functions.ease_in_out_sine
                                 ).shift(LEFT * 1.0),
                  blockB.animate(rate_func=rate_functions.ease_in_out_sine
                                 ).shift(LEFT * 1.0),
                  labA.animate.shift(LEFT * 1.0),
                  labB.animate.shift(LEFT * 1.0), run_time=1.6)
        comp = DoubleArrow(LEFT * 3.9 + DOWN * 1.7, LEFT * 2.9 + DOWN * 1.7,
                           buff=0, color=T.vector_force, stroke_width=5)
        comp_lab = MathTex(r"x_0 = 0.1\,\mathrm{m}", font_size=30,
                           color=T.vector_force)
        comp_lab.next_to(comp, UP, buff=0.15)
        self.play(GrowArrow(comp), Write(comp_lab), run_time=1.2)
        self.wait(0.4)
        release = Text("released from rest", font_size=24, color=T.text_muted)
        release.next_to(comp, RIGHT, buff=0.4)
        self.play(Write(release), run_time=1.4)
        self.wait(1.2)
        self.play(FadeOut(VGroup(base, spring, blockA, blockB, labA,
                                 labB, comp, comp_lab, release)),
                  run_time=0.8)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.78).to_edge(UP, buff=0.25),
                  run_time=1.0)
        self.wait(0.6)
'''

SPRING_BLOCKS_SEGMENTS = [
    {
        "narration": "While the spring is compressed, it pushes block A, "
                     "and block A pushes block B, so both blocks slide "
                     "together. The spring's stored energy, one half k x "
                     "zero squared, is zero point six joules. Setting it "
                     "equal to the kinetic energy of both blocks gives v "
                     "equals the square root of three, about one point "
                     "seven three meters per second.",
        "code": r'''from manim import *


def _spring(start, end, amp=0.12, coils=7):
    pts = [start]
    n = 2 * coils
    for i in range(1, n):
        off = UP * amp if i % 2 else DOWN * amp
        pts.append(start + (end - start) * (i / n) + off)
    pts.append(end)
    m = VMobject()
    m.set_points_as_corners(pts)
    m.set_stroke(T.text_muted, 4)
    return m


class Segment0(Scene):
    def construct(self):
        title = Text("Phase 1: both blocks move together", font_size=30,
                      color=T.variable)
        title.to_edge(UP, buff=0.45)
        wall = Line(LEFT * 4.9 + DOWN * 3.05, LEFT * 4.9 + UP * 0.6)
        wall.set_stroke(T.text_muted, 8)
        floor = Line(LEFT * 4.9 + DOWN * 3.05, RIGHT * 4.8 + DOWN * 3.05)
        floor.set_stroke(T.atom_carbon, 4)
        spring = _spring(LEFT * 4.9 + DOWN * 2.55,
                         LEFT * 3.9 + DOWN * 2.55)
        blockA = Square(side_length=0.9)
        blockA.set_stroke(T.text_primary, 3).set_fill(T.panel, 0.9)
        blockA.move_to(LEFT * 3.45 + DOWN * 2.55)
        labA = Text("A", font_size=28, color=T.text_primary).move_to(blockA)
        blockB = Square(side_length=0.7)
        blockB.set_stroke(T.text_primary, 3).set_fill(GREEN_E, 0.9)
        blockB.move_to(LEFT * 2.65 + DOWN * 2.65)
        labB = Text("B", font_size=24, color=T.text_primary).move_to(blockB)
        massA = MathTex(r"m_A = 0.3\,\mathrm{kg}", font_size=26,
                        color=T.variable)
        massA.next_to(blockA, UP, buff=0.35)
        massB = MathTex(r"m_B = 0.1\,\mathrm{kg}", font_size=26,
                        color=T.stable_state)
        massB.next_to(blockB, UP, buff=0.35)
        marker = DashedLine(LEFT * 2.9 + DOWN * 3.05,
                            LEFT * 2.9 + DOWN * 1.45)
        marker.set_stroke(T.text_muted, 3)
        marker_lab = Text("natural length", font_size=20, color=T.text_muted)
        marker_lab.next_to(marker, UP, buff=0.1)
        e1 = MathTex(r"\tfrac{1}{2}kx_0^2 = \tfrac{1}{2}"
                     r"(m_A + m_B)\,v^2", font_size=36)
        e2 = MathTex(r"0.6\,\mathrm{J} = \tfrac{1}{2}(0.4\,"
                     r"\mathrm{kg})\,v^2", font_size=36)
        e3 = MathTex(r"v = \sqrt{3} \approx 1.73\,\mathrm{m/s}",
                     font_size=40, color=T.highlight_primary)
        eqs = VGroup(e1, e2, e3).arrange(DOWN, buff=0.55)
        eqs.move_to(RIGHT * 3.1 + UP * 0.6)
        box = SurroundingRectangle(e3, buff=0.28, color=T.highlight_primary)
        self.play(Write(title), run_time=1.1)
        self.play(Create(wall), Create(floor), Create(spring),
                  DrawBorderThenFill(blockA), Write(labA),
                  DrawBorderThenFill(blockB), Write(labB), run_time=1.6)
        self.play(Write(massA), Write(massB), run_time=1.0)
        self.wait(0.5)
        self.play(blockA.animate(rate_func=rate_functions.ease_in_out_sine
                                 ).shift(RIGHT * 1.0),
                  blockB.animate(rate_func=rate_functions.ease_in_out_sine
                                 ).shift(RIGHT * 1.0),
                  labA.animate.shift(RIGHT * 1.0),
                  labB.animate.shift(RIGHT * 1.0),
                  massA.animate.shift(RIGHT * 1.0),
                  massB.animate.shift(RIGHT * 1.0),
                  Transform(spring, _spring(LEFT * 4.9 + DOWN * 2.55,
                                            LEFT * 2.9 + DOWN * 2.55)),
                  run_time=2.8)
        self.play(Create(marker), Write(marker_lab), run_time=0.9)
        self.wait(0.4)
        self.play(Write(e1), run_time=1.8)
        self.wait(0.4)
        self.play(Write(e2), run_time=1.8)
        self.wait(0.4)
        self.play(Write(e3), Create(box), run_time=1.9)
        self.wait(5.8)
''',
    },
    {
        "narration": "At the natural length, the spring stops pushing. "
                     "Block B feels no force and flies away at root three "
                     "meters per second. Block A stays on the spring and "
                     "oscillates. The maximum speed of a simple harmonic "
                     "oscillator occurs at the equilibrium point, so A's "
                     "maximum speed after separation is also root three, "
                     "about one point seven three meters per second.",
        "code": r'''from manim import *


def _spring(start, end, amp=0.12, coils=7):
    pts = [start]
    n = 2 * coils
    for i in range(1, n):
        off = UP * amp if i % 2 else DOWN * amp
        pts.append(start + (end - start) * (i / n) + off)
    pts.append(end)
    m = VMobject()
    m.set_points_as_corners(pts)
    m.set_stroke(T.text_muted, 4)
    return m


class Segment1(Scene):
    def construct(self):
        title = Text("Separation: B leaves, A oscillates", font_size=30,
                      color=T.variable)
        title.to_edge(UP, buff=0.45)
        wall = Line(LEFT * 4.9 + DOWN * 3.05, LEFT * 4.9 + UP * 0.6)
        wall.set_stroke(T.text_muted, 8)
        floor = Line(LEFT * 4.9 + DOWN * 3.05, RIGHT * 4.8 + DOWN * 3.05)
        floor.set_stroke(T.atom_carbon, 4)
        spring = _spring(LEFT * 4.9 + DOWN * 2.55,
                         LEFT * 2.9 + DOWN * 2.55)
        blockA = Square(side_length=0.9)
        blockA.set_stroke(T.text_primary, 3).set_fill(T.panel, 0.9)
        blockA.move_to(LEFT * 2.45 + DOWN * 2.55)
        labA = Text("A", font_size=28, color=T.text_primary).move_to(blockA)
        blockB = Square(side_length=0.7)
        blockB.set_stroke(T.text_primary, 3).set_fill(GREEN_E, 0.9)
        blockB.move_to(LEFT * 1.65 + DOWN * 2.65)
        labB = Text("B", font_size=24, color=T.text_primary).move_to(blockB)
        marker = DashedLine(LEFT * 2.9 + DOWN * 3.05,
                            LEFT * 2.9 + DOWN * 1.45)
        marker.set_stroke(T.text_muted, 3)
        self.add(wall, floor, spring, blockA, labA, blockB, labB, marker)
        self.wait(0.9)
        v_arrow = Arrow(blockB.get_top() + UP * 0.2,
                        blockB.get_top() + UP * 0.2 + RIGHT * 1.2,
                        buff=0, color=T.stable_state, stroke_width=6)
        v_lab = MathTex(r"v = \sqrt{3}\,\mathrm{m/s}", font_size=32,
                        color=T.stable_state)
        v_lab.next_to(v_arrow, UP, buff=0.15)
        self.play(GrowArrow(v_arrow), run_time=0.9)
        self.play(blockB.animate(rate_func=rate_functions.linear
                                 ).shift(RIGHT * 3.3),
                  labB.animate(rate_func=rate_functions.linear
                               ).shift(RIGHT * 3.3),
                  v_arrow.animate(rate_func=rate_functions.linear
                                  ).shift(RIGHT * 3.3),
                  v_lab.animate(rate_func=rate_functions.linear
                                ).shift(RIGHT * 3.3),
                  run_time=2.2)
        self.wait(0.5)
        moves = [(RIGHT * 0.87, 1.6), (LEFT * 1.74, 1.8),
                 (RIGHT * 1.74, 1.8), (LEFT * 0.87, 1.6)]
        for shift, run in moves:
            target = _spring(LEFT * 4.9 + DOWN * 2.55,
                            blockA.get_left() + shift)
            self.play(blockA.animate(rate_func=rate_functions
                                     .ease_in_out_sine).shift(shift),
                      labA.animate(rate_func=rate_functions
                                   .ease_in_out_sine).shift(shift),
                      Transform(spring, target), run_time=run)
            spring = target
        self.wait(0.5)
        dot = Dot(blockA.get_center(), color=T.highlight_primary, radius=0.1)
        note = Text("v is max at equilibrium", font_size=22, color=T.text_muted)
        note.next_to(blockA, UP, buff=0.6)
        self.play(FadeIn(dot, scale=2), Write(note), run_time=1.4)
        answer = MathTex(r"v_{A,\max} = \sqrt{3} \approx 1.73\,"
                         r"\mathrm{m/s}", font_size=38, color=T.highlight_primary)
        answer.move_to(RIGHT * 2.9 + UP * 1.4)
        box = SurroundingRectangle(answer, buff=0.3, color=T.highlight_primary)
        self.play(Write(answer), run_time=2.1)
        self.play(Create(box), run_time=1.0)
        self.wait(5.6)
''',
    },
    {
        "narration": "A's angular frequency is the square root of k over "
                     "m, which is twenty radians per second. The amplitude "
                     "is v max over omega, about eight point seven "
                     "centimeters. The period is two pi over omega, about "
                     "zero point three one four seconds. Here is A's "
                     "position over time.",
        "code": r'''from manim import *


class Segment2(Scene):
    def construct(self):
        title = Text("A's oscillation after separation", font_size=30,
                      color=T.variable)
        title.to_edge(UP, buff=0.45)
        f1 = MathTex(r"\omega = \sqrt{k/m_A} = 20\,\mathrm{rad/s}",
                     font_size=36)
        f2 = MathTex(r"A = v_{\max}/\omega = \sqrt{3}/20 \approx 0.087\,"
                     r"\mathrm{m}", font_size=36)
        f3 = MathTex(r"T = 2\pi/\omega = \pi/10 \approx 0.314\,\mathrm{s}",
                     font_size=36)
        facts = VGroup(f1, f2, f3).arrange(DOWN, aligned_edge=LEFT,
                                           buff=0.65)
        facts.move_to(LEFT * 3.6 + DOWN * 0.4)
        self.play(Write(title), run_time=1.0)
        self.play(Write(f1), run_time=2.0)
        self.play(Write(f2), run_time=2.0)
        self.play(Write(f3), run_time=2.0)
        self.wait(0.6)
        axes = Axes(x_range=[0, 4, 1], y_range=[-1.2, 1.2, 0.6],
                    x_length=4.6, y_length=2.7,
                    axis_config={"include_numbers": True,
                                 "font_size": 20})
        axes.move_to(RIGHT * 2.9 + DOWN * 0.3)
        x_lab = Text("t", font_size=22, color=T.text_muted)
        x_lab.next_to(axes.x_axis, RIGHT, buff=0.12)
        y_lab = Text("x(t)", font_size=22, color=T.text_muted)
        y_lab.next_to(axes.y_axis, UP, buff=0.12)
        curve = axes.plot(lambda t: 0.95 * np.sin(np.pi * t),
                          x_range=[0, 4], color=T.variable, stroke_width=5)
        span = Line(axes.c2p(0, -1.35), axes.c2p(2, -1.35))
        span.set_stroke(T.text_primary, 2)
        brace = Brace(span, DOWN, buff=0.12)
        t_lab = MathTex(r"T \approx 0.314\,\mathrm{s}", font_size=28,
                        color=T.highlight_primary)
        t_lab.next_to(brace, DOWN, buff=0.12)
        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=2.2)
        self.play(Create(curve), run_time=2.4)
        self.play(Create(span), Create(brace), Write(t_lab), run_time=1.5)
        self.wait(4.6)
''',
    },
    {
        "narration": "Finally, the energy. Nothing is lost to the "
                     "environment: the surface is frictionless and the "
                     "spring is ideal. Of the original zero point six "
                     "joules, block B carries away zero point one five "
                     "joules, and the remaining zero point four five "
                     "joules stays with block A, trading between kinetic "
                     "and spring energy forever.",
        "code": r'''from manim import *


class Segment3(Scene):
    def construct(self):
        title = Text("Energy accounting", font_size=30, color=T.variable)
        title.to_edge(UP, buff=0.45)
        chart = BarChart(values=[0.6, 0.45, 0.15],
                         bar_names=["initial 0.6 J", "A+spring 0.45",
                                    "B carries 0.15"],
                         y_range=[0, 0.8, 0.2], y_length=2.9, x_length=5.0,
                         bar_colors=[T.variable, T.panel, T.stable_state],
                         axis_config={"font_size": 20})
        chart.move_to(LEFT * 2.3 + DOWN * 0.7)
        reason = Text("frictionless surface + ideal spring", font_size=26,
                      color=T.text_muted)
        reason.move_to(RIGHT * 3.0 + UP * 1.2)
        claim = Text("no energy lost to the environment", font_size=30,
                     color=T.variable)
        claim.move_to(RIGHT * 3.0 + UP * 0.2)
        box = SurroundingRectangle(claim, buff=0.3, color=T.highlight_primary)
        flow1 = MathTex(r"0.15\,\mathrm{J}", font_size=30, color=T.stable_state)
        flow1.next_to(claim, DOWN, buff=0.9)
        flow1_lab = Text("leaves with block B", font_size=22,
                         color=T.text_muted)
        flow1_lab.next_to(flow1, DOWN, buff=0.15)
        flow2 = MathTex(r"0.45\,\mathrm{J}", font_size=30, color=T.variable)
        flow2.next_to(flow1_lab, DOWN, buff=0.45)
        flow2_lab = Text("oscillates with A forever", font_size=22,
                         color=T.text_muted)
        flow2_lab.next_to(flow2, DOWN, buff=0.15)
        thanks = Text("thanks for watching", font_size=24, color=T.text_muted)
        thanks.to_edge(DOWN, buff=0.4)
        self.play(Write(title), run_time=1.0)
        self.play(Create(chart), run_time=2.6)
        self.wait(0.7)
        self.play(Write(reason), run_time=1.8)
        self.play(Write(claim), run_time=1.7)
        self.play(Create(box), run_time=1.0)
        self.play(Write(flow1), Write(flow1_lab), run_time=1.6)
        self.play(Write(flow2), Write(flow2_lab), run_time=1.6)
        self.play(FadeIn(thanks, shift=0.3 * UP), run_time=1.0)
        self.wait(6.5)
''',
    },
]


# ---------------------------------------------------------------------------
# Test lecture: the derivative as a limit of secants (multi-scale camera)
# ---------------------------------------------------------------------------

DERIVATIVE_TITLE = "The Derivative as a Limit of Secants"

DERIVATIVE_QUESTION = {
    "display": "What does the derivative of a curve at a point really "
               "mean? Use $f(x) = 0.3(x-2)^2 + 1$ at $x = 3$.",
    "speech": "What does the derivative of a curve at a point really "
              "mean? Use the curve f of x equals zero point three times "
              "the quantity x minus two squared, plus one, at x equals "
              "three.",
}

DERIVATIVE_QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION", font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.0)
        line = Underline(badge, buff=0.15)
        row1 = VGroup(
            Text("What does the derivative of a curve at a point "
                 "really mean?", font_size=26, color=T.text_primary),
        )
        row2 = VGroup(
            Text("Use ", font_size=26, color=T.text_primary),
            MathTex(r"f(x) = 0.3(x-2)^2 + 1", font_size=30,
                    color=T.variable),
            Text(" at ", font_size=26, color=T.text_primary),
            MathTex("x = 3", font_size=30, color=T.constant),
            Text(".", font_size=26, color=T.text_primary),
        ).arrange(RIGHT, buff=0.12)
        rows = VGroup(row1, row2).arrange(DOWN, aligned_edge=LEFT,
                                          buff=0.2)
        rows.move_to(UP * 1.2)
        axes = Axes(x_range=[0, 5, 1], y_range=[0, 3.5, 1],
                    x_length=6.5, y_length=3.6,
                    axis_config={"color": T.text_muted, "font_size": 18})
        axes.move_to(DOWN * 1.2)
        curve = axes.plot(lambda x: 0.3 * (x - 2) ** 2 + 1,
                          x_range=[0.4, 4.9], color=T.graph_function,
                          stroke_width=5)
        d0 = Dot(axes.c2p(3, 1.3), color=T.graph_point, radius=0.1)
        d1 = Dot(axes.c2p(4.3, 2.007), color=T.graph_point, radius=0.1)
        sec = Line(axes.c2p(2.6, 1.427), axes.c2p(4.6, 2.187),
                   color=T.graph_secant, stroke_width=4)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.8)
        self.play(Write(rows), run_time=2.4)
        self.play(Create(axes), Create(curve), run_time=1.8)
        self.play(FadeIn(d0), FadeIn(d1), Create(sec), run_time=1.2)
        self.wait(4.0)
        self.play(FadeOut(VGroup(axes, curve, d0, d1, sec)), run_time=0.8)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.78).to_edge(UP, buff=0.25),
                  run_time=1.0)
        self.wait(2.2)
'''

DERIVATIVE_SEGMENTS = [
    {
        "narration": "Here is the curve. To measure its steepness at the "
                     "yellow point, we start with a secant: a straight "
                     "line through that point and a second point on the "
                     "curve. Now zoom in, and watch what happens as the "
                     "second point slides toward the first one.",
        "visual": {"objective": "show a secant through two tracked points "
                                "and zoom into the region between them",
                   "transition": "slide-up",
                   "visual_elements": ["graph", "secant line", "two points"],
                   "diagram": "graph",
                   "camera_movement": "pan",
                   "camera_target": "the interval between the two points",
                   "zoom_target": "the secant region between the points",
                   "highlight": ["the fixed yellow point",
                                 "the moving yellow point"],
                   "dynamic": ["secant stays attached to both tracked "
                               "points while one slides"],
                   "color_roles": {"curve": "graph_function",
                                   "secant": "graph_secant",
                                   "points": "graph_point"},
                   "animation_beats": ["draw curve", "place both points",
                                       "draw live secant",
                                       "zoom into the pair",
                                       "slide second point closer",
                                       "return to overview"],
                   "outcome": "a secant measures average slope between two "
                              "points"},
        "code": r'''from manim import *


class Segment0(MovingCameraScene):
    def construct(self):
        f = lambda x: 0.3 * (x - 2) ** 2 + 1
        qline = VGroup(
            Text("derivative of ", font_size=22, color=T.text_muted),
            MathTex(r"f(x) = 0.3(x-2)^2 + 1", font_size=26,
                    color=T.variable),
            Text(" at ", font_size=22, color=T.text_muted),
            MathTex("x = 3", font_size=26, color=T.constant),
        ).arrange(RIGHT, buff=0.12)
        qline.to_edge(UP, buff=0.45)
        axes = Axes(x_range=[0, 5, 1], y_range=[0, 3.5, 1],
                    x_length=8.5, y_length=5.2,
                    axis_config={"color": T.text_secondary,
                                 "font_size": 20}, tips=False)
        axes.move_to(DOWN * 0.5)
        curve = axes.plot(f, x_range=[0.4, 4.9], color=T.graph_function,
                          stroke_width=5)
        x0 = ValueTracker(3.0)
        x1 = ValueTracker(4.3)
        p0 = graph_point(axes, f, x0, color=T.graph_point, radius=0.11)
        p1 = graph_point(axes, f, x1, color=T.graph_point, radius=0.11)
        sec = secant_line(axes, f, x0, x1, color=T.graph_secant)
        self.play(Write(qline), Create(axes), run_time=1.6)
        self.play(Create(curve), run_time=1.4)
        self.play(FadeIn(p0), run_time=0.7)
        emphasize(self, p0, color=T.graph_point, run_time=0.8)
        self.play(FadeIn(p1), Create(sec), run_time=1.1)
        emphasize(self, p1, color=T.graph_point, run_time=0.8)
        zoom_to(self, VGroup(p0, p1), run_time=1.6, context=3.2)
        self.wait(0.4)
        self.play(x1.animate.set_value(3.25), run_time=2.6)
        self.wait(0.6)
        camera_reset(self, run_time=1.3)
        self.wait(1.8)
''',
    },
    {
        "narration": "In the limit, the secant turns into the tangent "
                     "line, shown in cyan, and its slope is exactly the "
                     "derivative. For this curve, f prime of x equals "
                     "zero point six times the quantity x minus two. At "
                     "x equals three the slope is zero point six, the "
                     "green result.",
        "visual": {"objective": "reveal the tangent and the derivative "
                                "value as the final result",
                   "transition": "carry-over",
                   "visual_elements": ["graph", "tangent line",
                                       "derivative formula"],
                   "diagram": "graph",
                   "camera_movement": "static",
                   "highlight": ["the tangent line", "the final value"],
                   "dynamic": ["tangent slope computed from the real "
                               "derivative at the tracked point"],
                   "color_roles": {"tangent": "graph_tangent",
                                   "result": "result_final"},
                   "animation_beats": ["re-establish the zoomed pair",
                                       "let the point reach the limit",
                                       "draw the tangent",
                                       "clear the working",
                                       "box the final value"],
                   "outcome": "the derivative is the slope of the tangent"},
        "code": r'''from manim import *


class Segment1(MovingCameraScene):
    def construct(self):
        f = lambda x: 0.3 * (x - 2) ** 2 + 1
        axes = Axes(x_range=[0, 5, 1], y_range=[0, 3.5, 1],
                    x_length=8.5, y_length=5.2,
                    axis_config={"color": T.text_secondary,
                                 "font_size": 20}, tips=False)
        axes.move_to(DOWN * 0.5)
        curve = axes.plot(f, x_range=[0.4, 4.9], color=T.graph_function,
                          stroke_width=5)
        x0 = ValueTracker(3.0)
        x1 = ValueTracker(3.12)
        p0 = graph_point(axes, f, x0, color=T.graph_point, radius=0.11)
        p1 = graph_point(axes, f, x1, color=T.graph_point, radius=0.11)
        sec = secant_line(axes, f, x0, x1, color=T.graph_secant)
        self.add(axes, curve, p0, p1, sec)
        self.wait(0.8)
        self.play(x1.animate.set_value(3.001), run_time=1.6)
        tan = tangent_line(axes, f, x0, color=T.graph_tangent)
        self.play(Create(tan), run_time=1.2)
        emphasize(self, tan, color=T.graph_tangent, run_time=0.9)
        dim_except(self, [tan, p0, axes], opacity=0.3)
        formula = MathTex(r"f'(x) = 0.6(x-2)", font_size=40)
        formula.move_to(RIGHT * 3.6 + UP * 1.6)
        fx = formula[0][0].set_color(T.variable)
        self.play(Write(formula), run_time=1.6)
        restore_emphasis(self)
        self.play(FadeOut(sec), FadeOut(p1), run_time=0.8)
        value = MathTex(r"f'(3) = 0.6", font_size=52,
                        color=T.result_final)
        value.next_to(formula, DOWN, buff=0.9)
        box = SurroundingRectangle(value, buff=0.3, color=T.result_final)
        self.play(Write(value), run_time=1.4)
        self.play(Create(box), run_time=0.8)
        emphasize(self, value, color=T.result_final, run_time=0.9)
        self.wait(3.4)
''',
    },
]


# ---------------------------------------------------------------------------
# Test lecture: the unit circle and the sine wave (live projections)
# ---------------------------------------------------------------------------

CIRCLE_TITLE = "The Unit Circle in Motion"

CIRCLE_QUESTION = {
    "display": "Use the unit circle to explain where "
               "$\\sin t$ and $\\cos t$ come from as $t$ grows.",
    "speech": "Use the unit circle to explain where sine and cosine come "
              "from as the angle t grows.",
}

CIRCLE_QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION", font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.0)
        line = Underline(badge, buff=0.15)
        row1 = VGroup(
            Text("Use the unit circle to explain where ", font_size=26,
                 color=T.text_primary),
            MathTex(r"\sin t", font_size=30, color=T.vector_velocity),
            Text(" and ", font_size=26, color=T.text_primary),
            MathTex(r"\cos t", font_size=30, color=T.variable),
            Text(" come from as ", font_size=26, color=T.text_primary),
            MathTex("t", font_size=30, color=T.constant),
            Text(" grows.", font_size=26, color=T.text_primary),
        ).arrange(RIGHT, buff=0.12)
        row1.move_to(UP * 1.1)
        circ = Circle(radius=1.8, color=T.graph_function, stroke_width=4)
        circ.move_to(DOWN * 1.3)
        radius = Line(circ.get_center(),
                      circ.get_center() + RIGHT * 1.8,
                      color=T.text_primary, stroke_width=4)
        dot = Dot(circ.get_center() + RIGHT * 1.8, color=T.graph_point,
                  radius=0.1)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.8)
        self.play(Write(row1), run_time=2.4)
        self.play(Create(circ), Create(radius), FadeIn(dot), run_time=1.6)
        self.wait(4.0)
        self.play(FadeOut(VGroup(circ, radius, dot)), run_time=0.8)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(row1.animate.scale(0.78).to_edge(UP, buff=0.25),
                  run_time=1.0)
        self.wait(2.0)
'''

CIRCLE_SEGMENTS = [
    {
        "narration": "On the unit circle, the angle t rotates a radius "
                     "around the center. The horizontal projection of the "
                     "moving point is cos t, in blue, and the vertical "
                     "projection is sin t, in cyan. Both projections "
                     "change together as the radius turns.",
        "visual": {"objective": "rotating radius with live cos/sin "
                                "projections",
                   "transition": "slide-up",
                   "visual_elements": ["unit circle", "rotating radius",
                                       "projection lines"],
                   "diagram": "geometry",
                   "camera_movement": "static",
                   "highlight": ["the cos projection", "the sin projection"],
                   "dynamic": ["radius, projections, arc and labels all "
                               "driven by one angle tracker"],
                   "color_roles": {"circle": "graph_function",
                                   "cos projection": "variable",
                                   "sin projection": "vector_velocity",
                                   "moving point": "graph_point"},
                   "animation_beats": ["draw circle", "rotate the radius",
                                       "show cos projection",
                                       "show sin projection",
                                       "rotate further"],
                   "outcome": "sine and cosine are coordinates of the "
                              "moving point"},
        "code": r'''from manim import *


class Segment0(Scene):
    def construct(self):
        theta = ValueTracker(0.7)
        center = LEFT * 3.2 + DOWN * 0.4

        def point():
            a = theta.get_value()
            return center + 2.0 * np.array([np.cos(a), np.sin(a), 0])

        def radius_line():
            return Line(center, point(), color=T.text_primary,
                        stroke_width=5)

        def cos_line():
            p = point()
            return Line(center + (p - center) * np.array([1, 0, 0]), p,
                        color=T.variable, stroke_width=6)

        def sin_line():
            p = point()
            return Line(p, np.array([center[0], p[1], 0]),
                        color=T.vector_velocity, stroke_width=6)

        def arc_mobj():
            return Arc(radius=0.7, start_angle=0,
                       angle=theta.get_value(), color=T.constant,
                       stroke_width=4).shift(center)

        circle = Circle(radius=2.0, color=T.graph_function, stroke_width=4)
        circle.move_to(center)
        radius = radius_line()
        cosleg = cos_line()
        sinleg = sin_line()
        arc = arc_mobj()
        dot = Dot(point(), color=T.graph_point, radius=0.12)
        t_label = MathTex("t", font_size=36, color=T.constant)
        t_label.next_to(arc, RIGHT, buff=0.2)
        cos_label = MathTex(r"\cos t", font_size=34, color=T.variable)
        sin_label = MathTex(r"\sin t", font_size=34,
                            color=T.vector_velocity)
        cos_label.move_to(center + DOWN * 2.6)
        sin_label.move_to(center + UP * 2.5)
        radius.add_updater(lambda m: m.become(radius_line()))
        cosleg.add_updater(lambda m: m.become(cos_line()))
        sinleg.add_updater(lambda m: m.become(sin_line()))
        arc.add_updater(lambda m: m.become(arc_mobj()))
        dot.add_updater(lambda m: m.move_to(point()))
        t_label.add_updater(lambda m: m.next_to(arc, RIGHT, buff=0.2))
        self.play(Create(circle), run_time=1.2)
        self.play(Create(radius), FadeIn(dot), run_time=0.9)
        self.play(Create(cosleg), Write(cos_label), run_time=1.0)
        emphasize(self, cosleg, color=T.variable, run_time=0.8)
        self.play(Create(sinleg), Write(sin_label), run_time=1.0)
        emphasize(self, sinleg, color=T.vector_velocity, run_time=0.8)
        self.play(Create(arc), FadeIn(t_label), run_time=0.8)
        self.play(theta.animate.set_value(2.2), run_time=2.6)
        self.wait(2.6)
''',
    },
    {
        "narration": "Now sweep the angle through a full turn. The height "
                     "of the moving point, plotted against the angle "
                     "itself, traces the sine wave on the right. Notice "
                     "the circle and the wave stay perfectly in step. And "
                     "since the radius is always one, sin squared plus "
                     "cos squared equals one, for every angle.",
        "visual": {"objective": "trace the sine wave while the circle "
                                "rotates; reveal the Pythagorean identity",
                   "transition": "carry-over",
                   "visual_elements": ["unit circle", "sine graph",
                                       "identity"],
                   "diagram": "graph",
                   "camera_movement": "static",
                   "highlight": ["the traced sine wave",
                                 "the identity"],
                   "dynamic": ["wave dot and circle point driven by the "
                               "same tracker"],
                   "color_roles": {"reference curve": "graph_reference",
                                   "traced dot": "graph_point",
                                   "identity": "result_final"},
                   "animation_beats": ["re-establish circle and projections",
                                       "sweep one full turn",
                                       "trace the sine wave",
                                       "reveal the identity in green"],
                   "outcome": "the sine wave is the height of the moving "
                              "point"},
        "code": r'''from manim import *


class Segment1(Scene):
    def construct(self):
        theta = ValueTracker(2.2)
        center = LEFT * 3.2 + DOWN * 0.4

        def point():
            a = theta.get_value()
            return center + 2.0 * np.array([np.cos(a), np.sin(a), 0])

        def radius_line():
            return Line(center, point(), color=T.text_primary,
                        stroke_width=5)

        def sin_line():
            p = point()
            return Line(p, np.array([center[0], p[1], 0]),
                         color=T.vector_velocity, stroke_width=6)

        circle = Circle(radius=2.0, color=T.graph_function, stroke_width=4)
        circle.move_to(center)
        radius = radius_line()
        sinleg = sin_line()
        dot = Dot(point(), color=T.graph_point, radius=0.12)
        radius.add_updater(lambda m: m.become(radius_line()))
        sinleg.add_updater(lambda m: m.become(sin_line()))
        dot.add_updater(lambda m: m.move_to(point()))
        axes = Axes(x_range=[0, 6.8, 1.57], y_range=[-1.3, 1.3, 1],
                    x_length=6.0, y_length=4.2,
                    axis_config={"color": T.text_secondary,
                                 "font_size": 18}, tips=False)
        axes.move_to(RIGHT * 3.2 + DOWN * 0.4)
        wave_ref = axes.plot(lambda t: np.sin(t), x_range=[0, 6.28],
                             color=T.graph_reference, stroke_width=2)
        wave_dot = Dot(axes.c2p(theta.get_value(),
                                np.sin(theta.get_value())),
                       color=T.graph_point, radius=0.12)
        wave_dot.add_updater(lambda m: m.move_to(
            axes.c2p(theta.get_value(), np.sin(theta.get_value()))))
        traced = TracedPath(wave_dot.get_center, stroke_color=(
            T.vector_velocity), stroke_width=5)
        self.add(circle, radius, sinleg, dot)
        self.play(Create(axes), Create(wave_ref), run_time=1.4)
        self.add(traced, wave_dot)
        self.play(theta.animate.set_value(2.2 + TAU), run_time=4.2)
        emphasize(self, wave_dot, color=T.graph_point, run_time=0.8)
        identity = MathTex(r"\sin^2 t + \cos^2 t = 1", font_size=44,
                           color=T.result_final)
        identity.to_edge(UP, buff=0.6)
        box = SurroundingRectangle(identity, buff=0.3, color=T.result_final)
        self.play(Write(identity), run_time=1.4)
        self.play(Create(box), run_time=0.8)
        self.wait(3.0)
''',
    },
]


# ---------------------------------------------------------------------------
# Test lecture: a 3D surface, orbiting camera, and a cross-section
# ---------------------------------------------------------------------------

SURFACE3D_TITLE = "Exploring a 3D Surface"

SURFACE3D_QUESTION = {
    "display": "Explore the surface $z = \\frac{x^2 + y^2}{8}$. What is "
               "its cross-section along the plane $y = 0$?",
    "speech": "Explore the surface z equals x squared plus y squared, all "
              "over eight. What is its cross section along the plane y "
              "equals zero?",
}

SURFACE3D_QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION", font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.0)
        line = Underline(badge, buff=0.15)
        row1 = VGroup(
            Text("Explore the surface ", font_size=26,
                 color=T.text_primary),
            MathTex(r"z = \frac{x^2 + y^2}{8}", font_size=32,
                    color=T.variable),
            Text(".", font_size=26, color=T.text_primary),
        ).arrange(RIGHT, buff=0.12)
        row2 = VGroup(
            Text("What is its cross-section along the plane ",
                 font_size=26, color=T.text_primary),
            MathTex("y = 0", font_size=30, color=T.constant),
            Text("?", font_size=26, color=T.text_primary),
        ).arrange(RIGHT, buff=0.12)
        rows = VGroup(row1, row2).arrange(DOWN, aligned_edge=LEFT,
                                          buff=0.2)
        rows.move_to(UP * 1.1)
        bowl = Ellipse(width=5.4, height=2.4, color=T.graph_function,
                       stroke_width=4)
        bowl.move_to(DOWN * 1.4)
        inner = Ellipse(width=3.0, height=1.2, color=T.graph_reference,
                        stroke_width=2)
        inner.move_to(bowl.get_center() + UP * 0.3)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.8)
        self.play(Write(rows), run_time=2.4)
        self.play(Create(bowl), Create(inner), run_time=1.6)
        self.wait(3.6)
        self.play(FadeOut(VGroup(bowl, inner)), run_time=0.8)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.78).to_edge(UP, buff=0.25),
                  run_time=1.0)
        self.wait(2.0)
'''

SURFACE3D_SEGMENTS = [
    {
        "narration": "This is the surface in three dimensions. Let the "
                     "camera orbit: the shape is a bowl that rises the "
                     "same way in every direction, because x and y enter "
                     "the formula symmetrically. Moving closer shows the "
                     "smooth rim of the bowl near the z axis.",
        "visual": {"objective": "establish the 3D bowl shape with an "
                                "orbiting, zooming camera",
                   "transition": "slide-up",
                   "visual_elements": ["3D surface", "3D axes"],
                   "diagram": "none",
                   "camera_movement": "orbit",
                   "camera_target": "the whole surface",
                   "zoom_target": "the region near the z axis",
                   "three_d": True,
                   "color_roles": {"surface": "graph_function",
                                   "axes": "text_secondary"},
                   "animation_beats": ["build the surface", "orbit the "
                                       "camera", "zoom closer", "zoom back"],
                   "outcome": "the surface is a symmetric bowl"},
        "code": r'''from manim import *


class Segment0(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)
        axes = ThreeDAxes(x_range=[-4, 4, 1], y_range=[-4, 4, 1],
                          z_range=[0, 4, 1], x_length=7, y_length=7,
                          z_length=4.5,
                          axis_config={"color": T.text_secondary})
        surface = Surface(
            lambda u, v: axes.c2p(u, v, (u ** 2 + v ** 2) / 8),
            u_range=[-3, 3], v_range=[-3, 3], resolution=(14, 14),
            fill_opacity=0.55, stroke_width=0.5,
            checkerboard_colors=[T.graph_function, T.panel])
        caption = Text("z = (x\u00b2 + y\u00b2)/8", font_size=30,
                       color=T.text_primary)
        caption.to_corner(UL)
        self.add_fixed_in_frame_mobjects(caption)
        self.play(Create(axes), run_time=1.2)
        self.play(DrawBorderThenFill(surface), run_time=2.2)
        orbit_start(self, rate=0.14)
        self.wait(2.6)
        orbit_stop(self)
        zoom_3d(self, zoom=1.45, run_time=1.4)
        self.wait(1.2)
        zoom_3d(self, zoom=1.0, run_time=1.2)
        self.wait(2.2)
''',
    },
    {
        "narration": "Now slice the bowl with the vertical plane y equals "
                     "zero. The cut is a curve: a parabola, highlighted "
                     "in yellow. Flattened into two dimensions it is z "
                     "equals x squared over eight, the skeleton of the "
                     "bowl. The green formula is the final result.",
        "visual": {"objective": "reveal the cross-section and connect it "
                                "to its 2D parabola",
                   "transition": "carry-over",
                   "visual_elements": ["cross-section curve",
                                       "2D parabola", "formula"],
                   "diagram": "graph",
                   "camera_movement": "orbit",
                   "zoom_target": "the cross-section curve",
                   "three_d": True,
                   "highlight": ["the cross-section curve",
                                 "the final formula"],
                   "color_roles": {"cross-section": "graph_point",
                                   "2D parabola": "graph_point",
                                   "result": "result_final"},
                   "animation_beats": ["re-establish the bowl",
                                       "draw the slicing curve",
                                       "orbit to view it",
                                       "show the matching 2D parabola",
                                       "reveal the formula"],
                   "outcome": "the y = 0 slice of the bowl is the parabola "
                              "z = x\u00b2/8"},
        "code": r'''from manim import *


class Segment1(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)
        axes = ThreeDAxes(x_range=[-4, 4, 1], y_range=[-4, 4, 1],
                          z_range=[0, 4, 1], x_length=7, y_length=7,
                          z_length=4.5,
                          axis_config={"color": T.text_secondary})
        surface = Surface(
            lambda u, v: axes.c2p(u, v, (u ** 2 + v ** 2) / 8),
            u_range=[-3, 3], v_range=[-3, 3], resolution=(14, 14),
            fill_opacity=0.3, stroke_width=0.5,
            checkerboard_colors=[T.graph_function, T.panel])
        slice_curve = ParametricFunction(
            lambda t: axes.c2p(t, 0, t ** 2 / 8), t_range=[-3, 3],
            color=T.graph_point, stroke_width=7)
        self.add(axes, surface)
        self.play(Create(slice_curve), run_time=1.8)
        emphasize(self, slice_curve, color=T.graph_point, run_time=0.9)
        zoom_3d(self, zoom=1.4, run_time=1.2)
        self.wait(0.8)
        zoom_3d(self, zoom=1.0, run_time=1.0)
        orbit_start(self, rate=0.14)
        self.wait(2.2)
        orbit_stop(self)
        flat_axes = Axes(x_range=[-3.5, 3.5, 1], y_range=[0, 1.5, 0.5],
                         x_length=3.4, y_length=1.6,
                         axis_config={"color": T.text_muted,
                                      "font_size": 14}, tips=False)
        flat_axes.to_corner(DR, buff=0.5)
        flat_curve = flat_axes.plot(lambda x: x ** 2 / 8,
                                    x_range=[-3, 3],
                                    color=T.graph_point, stroke_width=5)
        flat_label = Text("the y = 0 slice", font_size=20,
                          color=T.text_secondary)
        flat_label.next_to(flat_axes, UP, buff=0.15)
        self.add_fixed_in_frame_mobjects(flat_axes, flat_curve, flat_label)
        self.play(Create(flat_axes), Write(flat_label), run_time=1.0)
        self.play(Create(flat_curve), run_time=1.2)
        result = MathTex(r"z = \frac{x^2}{8}", font_size=44,
                         color=T.result_final)
        result.to_corner(UR, buff=0.7)
        box = SurroundingRectangle(result, buff=0.28, color=T.result_final)
        self.add_fixed_in_frame_mobjects(result, box)
        self.play(Write(result), run_time=1.2)
        self.play(Create(box), run_time=0.7)
        self.wait(2.8)
''',
    },
]


# ---------------------------------------------------------------------------
# Test lecture: solving a quadratic step by step (color-graded algebra)
# ---------------------------------------------------------------------------

QUADRATIC_TITLE = "Solving a Quadratic by Factoring"

QUADRATIC_QUESTION = {
    "display": "Solve $x^2 - 5x + 6 = 0$ by factoring.",
    "speech": "Solve x squared minus five x plus six equals zero by "
              "factoring.",
}

QUADRATIC_QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION", font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.0)
        line = Underline(badge, buff=0.15)
        row1 = VGroup(
            Text("Solve ", font_size=26, color=T.text_primary),
            MathTex(r"x^2 - 5x + 6 = 0", font_size=34),
            Text(" by factoring.", font_size=26, color=T.text_primary),
        ).arrange(RIGHT, buff=0.15)
        row1.move_to(UP * 0.6)
        big = MathTex("x", "^2", "-", "5", "x", "+", "6", "=", "0",
                      font_size=72)
        big.move_to(DOWN * 1.2)
        big[0].set_color(T.variable)
        big[4].set_color(T.variable)
        big[3].set_color(T.constant)
        big[5].set_color(T.constant)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.8)
        self.play(Write(row1), run_time=1.8)
        self.play(Write(big), run_time=2.2)
        self.wait(3.2)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(row1.animate.scale(0.78).to_edge(UP, buff=0.25),
                  big.animate.scale(0.5).to_edge(UP, buff=1.05),
                  run_time=1.0)
        self.wait(2.0)
'''

QUADRATIC_SEGMENTS = [
    {
        "narration": "The equation is color graded: unknowns in blue, "
                     "numbers in yellow. Two numbers that multiply to six "
                     "but add to minus five are minus two and minus "
                     "three, so the left side factors in place, term by "
                     "term, into x minus two times x minus three.",
        "visual": {"objective": "factor the quadratic in place with "
                                "color-graded terms",
                   "transition": "slide-up",
                   "visual_elements": ["color-graded equation",
                                       "factored form"],
                   "diagram": "none",
                   "camera_movement": "static",
                   "highlight": ["the coefficients", "each factor"],
                   "color_roles": {"variables": "variable",
                                   "constants": "constant",
                                   "operators": "operator",
                                   "working": "result_intermediate"},
                   "animation_beats": ["restate the graded equation",
                                       "transform it into factored form "
                                       "in place",
                                       "highlight each factor"],
                   "outcome": "the equation factors into (x-2)(x-3) = 0"},
        "code": r'''from manim import *


class Segment0(Scene):
    def construct(self):
        title = Text("step 1: factor in place", font_size=28,
                     color=T.text_secondary)
        title.to_edge(UP, buff=0.4)
        eq = MathTex("x", "^2", "-", "5", "x", "+", "6", "=", "0",
                     font_size=64)
        eq.move_to(UP * 0.9)
        eq[0].set_color(T.variable)
        eq[4].set_color(T.variable)
        eq[3].set_color(T.constant)
        eq[5].set_color(T.constant)
        self.play(Write(title), run_time=1.0)
        self.play(Write(eq), run_time=1.8)
        emphasize(self, eq[3], color=T.constant, run_time=0.7)
        emphasize(self, eq[5], color=T.constant, run_time=0.7)
        factored = MathTex("(x", "-", "2", ")", "(x", "-", "3", ")",
                           "=", "0", font_size=64)
        factored.move_to(UP * 0.9)
        factored[0].set_color(T.operator)
        factored[3].set_color(T.operator)
        factored[1].set_color(T.variable)
        factored[4].set_color(T.variable)
        factored[2].set_color(T.constant)
        factored[6].set_color(T.constant)
        self.play(TransformMatchingTex(eq, factored), run_time=1.8)
        emphasize(self, factored[0:4], color=T.result_intermediate,
                  run_time=0.8)
        emphasize(self, factored[4:8], color=T.result_intermediate,
                  run_time=0.8)
        note = Text("numbers that multiply to 6 and add to -5",
                    font_size=24, color=T.text_muted)
        note.next_to(factored, DOWN, buff=0.8)
        self.play(Write(note), run_time=1.2)
        self.wait(3.2)
''',
    },
    {
        "narration": "A product equals zero when one of its factors is "
                     "zero, so either x minus two is zero, or x minus "
                     "three is zero. The solutions are x equals two and "
                     "x equals three, emphasized in green. Check the "
                     "first one: four minus ten plus six is indeed zero.",
        "visual": {"objective": "derive the roots and reveal them as the "
                                "final result",
                   "transition": "carry-over",
                   "visual_elements": ["zero-product lines", "roots",
                                       "verification"],
                   "diagram": "none",
                   "camera_movement": "static",
                   "highlight": ["each zero-product factor",
                                 "the final roots"],
                   "color_roles": {"working": "result_intermediate",
                                   "roots": "result_final",
                                   "check": "text_muted"},
                   "animation_beats": ["write the zero-product cases",
                                       "clear the working",
                                       "box the roots in green",
                                       "verify by substitution"],
                   "outcome": "x = 2 or x = 3"},
        "code": r'''from manim import *


class Segment1(Scene):
    def construct(self):
        title = Text("step 2: zero product, then the roots", font_size=28,
                     color=T.text_secondary)
        title.to_edge(UP, buff=0.4)
        factored = MathTex("(x", "-", "2", ")", "(x", "-", "3", ")",
                           "=", "0", font_size=56)
        factored.move_to(UP * 1.8)
        factored[1].set_color(T.variable)
        factored[4].set_color(T.variable)
        factored[2].set_color(T.constant)
        factored[6].set_color(T.constant)
        case1 = MathTex("x", "-", "2", "=", "0", font_size=44,
                        color=T.result_intermediate)
        case2 = MathTex("x", "-", "3", "=", "0", font_size=44,
                        color=T.result_intermediate)
        cases = VGroup(case1, case2).arrange(RIGHT, buff=1.2)
        cases.move_to(UP * 0.5)
        self.play(Write(title), run_time=1.0)
        self.play(Write(factored), run_time=1.4)
        emphasize(self, factored[0:4], color=T.result_intermediate,
                  run_time=0.7)
        self.play(Write(case1), run_time=1.1)
        emphasize(self, factored[4:8], color=T.result_intermediate,
                  run_time=0.7)
        self.play(Write(case2), run_time=1.1)
        self.wait(0.8)
        roots = MathTex("x = 2", font_size=56, color=T.result_final)
        roots2 = MathTex("x = 3", font_size=56, color=T.result_final)
        pair = VGroup(roots, roots2).arrange(RIGHT, buff=1.0)
        pair.move_to(DOWN * 0.9)
        box = SurroundingRectangle(pair, buff=0.35, color=T.result_final)
        self.play(FadeOut(VGroup(factored, case1, case2, title)),
                  run_time=0.9)
        self.play(Write(roots), Write(roots2), run_time=1.4)
        self.play(Create(box), run_time=0.8)
        emphasize(self, pair, color=T.result_final, run_time=0.9)
        check = MathTex("2^2 - 5 \\cdot 2 + 6 = 4 - 10 + 6 = 0",
                        font_size=32, color=T.text_muted)
        check.next_to(box, DOWN, buff=0.8)
        self.play(Write(check), run_time=1.6)
        self.wait(3.2)
''',
    },
]


# ---------------------------------------------------------------------------
# Test lecture: dynamic vector addition (physics)
# ---------------------------------------------------------------------------

VECTORS_TITLE = "Adding Forces: a Live Vector Diagram"

VECTORS_QUESTION = {
    "display": "Two forces act on a point: $F_1 = 4\\,\\mathrm{N}$ along "
               "the x-axis and $F_2 = 3\\,\\mathrm{N}$ at $90^\\circ$. "
               "What is their resultant?",
    "speech": "Two forces act on a point: F one equals four newtons "
              "along the x axis, and F two equals three newtons at "
              "ninety degrees. What is their resultant?",
}

VECTORS_QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION", font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.0)
        line = Underline(badge, buff=0.15)
        row1 = VGroup(
            Text("Two forces act on a point: ", font_size=26,
                 color=T.text_primary),
            MathTex(r"F_1 = 4\,\mathrm{N}", font_size=30,
                    color=T.vector_force),
            Text(" along the x-axis and ", font_size=26,
                 color=T.text_primary),
            MathTex(r"F_2 = 3\,\mathrm{N}", font_size=30,
                    color=T.vector_force),
            Text(" at ", font_size=26, color=T.text_primary),
            MathTex(r"90^\circ", font_size=30, color=T.constant),
            Text(".", font_size=26, color=T.text_primary),
        ).arrange(RIGHT, buff=0.1)
        row2 = Text("What is their resultant?", font_size=26,
                    color=T.text_primary)
        row1.move_to(UP * 1.35)
        row2.next_to(row1, DOWN, buff=0.25)
        origin = DOWN * 1.3
        f1 = Arrow(origin, origin + RIGHT * 2.8, buff=0,
                   color=T.vector_force, stroke_width=7)
        f2 = Arrow(origin, origin + UP * 2.1, buff=0,
                   color=T.vector_force, stroke_width=7)
        res = DashedLine(origin + RIGHT * 2.8, origin + UP * 2.1,
                         color=T.result_intermediate, stroke_width=5)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.8)
        self.play(Write(row1), run_time=2.6)
        self.play(GrowArrow(f1), GrowArrow(f2), run_time=1.4)
        self.play(Create(res), run_time=0.9)
        self.wait(3.4)
        self.play(FadeOut(VGroup(f1, f2, res)), run_time=0.8)
        rows = VGroup(row1, row2)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.78).to_edge(UP, buff=0.25),
                  run_time=1.0)
        self.wait(2.0)
'''

VECTORS_SEGMENTS = [
    {
        "narration": "Here is the vector diagram. Both forces, in coral, "
                     "act on the same point. The resultant is the vector "
                     "from the origin to the far corner of the "
                     "parallelogram, shown in violet. Watch what happens "
                     "to the resultant as the angle of the second force "
                     "changes: the diagram stays live and correct.",
        "visual": {"objective": "live resultant that responds as the "
                                "force angle changes",
                   "transition": "slide-up",
                   "visual_elements": ["force vectors", "resultant",
                                       "angle arc"],
                   "diagram": "free-body",
                   "camera_movement": "static",
                   "highlight": ["the resultant"],
                   "dynamic": ["the second force, the resultant and the "
                               "angle label all update from one tracker"],
                   "color_roles": {"forces": "vector_force",
                                   "resultant": "result_intermediate",
                                   "angle": "constant"},
                   "animation_beats": ["draw both forces", "draw the live "
                                       "resultant", "sweep the angle",
                                       "highlight the resultant"],
                   "outcome": "the resultant closes the vector triangle"},
        "code": r'''from manim import *


class Segment0(Scene):
    def construct(self):
        origin = LEFT * 1.4 + DOWN * 0.9
        theta = ValueTracker(90 * DEGREES)

        def f2_end():
            a = theta.get_value()
            return origin + 2.1 * np.array([np.cos(a), np.sin(a), 0])

        def tip():
            return origin + RIGHT * 2.8 + (f2_end() - origin)

        f1 = Arrow(origin, origin + RIGHT * 2.8, buff=0,
                   color=T.vector_force, stroke_width=7)
        f2 = Arrow(origin, f2_end(), buff=0, color=T.vector_force,
                   stroke_width=7)
        f2.add_updater(lambda m: m.become(
            Arrow(origin, f2_end(), buff=0, color=T.vector_force,
                  stroke_width=7)))
        result = Arrow(origin, tip(), buff=0, color=T.result_intermediate,
                       stroke_width=8)
        result.add_updater(lambda m: m.become(
            Arrow(origin, tip(), buff=0, color=T.result_intermediate,
                  stroke_width=8)))
        closure = DashedLine(origin + RIGHT * 2.8, tip(),
                             color=T.text_muted, stroke_width=4)
        closure.add_updater(lambda m: m.become(
            DashedLine(origin + RIGHT * 2.8, tip(), color=T.text_muted,
                       stroke_width=4)))

        def arc_now():
            return Arc(radius=0.85, start_angle=0,
                        angle=theta.get_value(), color=T.constant,
                        stroke_width=4).shift(origin)
        arc = arc_now()
        arc.add_updater(lambda m: m.become(arc_now()))
        f1_lab = MathTex(r"F_1 = 4\,\mathrm{N}", font_size=32,
                         color=T.vector_force)
        f1_lab.next_to(f1, DOWN, buff=0.25)
        f2_lab = MathTex(r"F_2 = 3\,\mathrm{N}", font_size=32,
                         color=T.vector_force)
        f2_lab.next_to(f2, LEFT, buff=0.3)
        res_lab = MathTex("R", font_size=38, color=T.result_intermediate)
        res_lab.add_updater(lambda m: m.next_to(result, RIGHT, buff=0.25))
        self.play(GrowArrow(f1), Write(f1_lab), run_time=1.0)
        self.play(GrowArrow(f2), Write(f2_lab), run_time=1.0)
        self.play(Create(arc), run_time=0.7)
        self.play(GrowArrow(result), FadeIn(res_lab), run_time=1.1)
        emphasize(self, result, color=T.result_intermediate, run_time=0.9)
        self.play(theta.animate.set_value(140 * DEGREES), run_time=2.0)
        self.play(theta.animate.set_value(60 * DEGREES), run_time=2.0)
        self.play(theta.animate.set_value(90 * DEGREES), run_time=1.6)
        self.wait(2.4)
''',
    },
    {
        "narration": "Back at ninety degrees the forces are perpendicular, "
                     "so the resultant follows the Pythagorean theorem: "
                     "R squared equals four squared plus three squared, "
                     "which gives R equals five newtons. The green box "
                     "marks the final answer. Sweep the angle again and "
                     "the resultant changes, but the construction always "
                     "stays valid.",
        "visual": {"objective": "compute the resultant at 90 degrees and "
                                "reveal it as the final result",
                   "transition": "fade",
                   "visual_elements": ["Pythagoras formula", "resultant",
                                       "final answer"],
                   "diagram": "free-body",
                   "camera_movement": "static",
                   "highlight": ["the final resultant"],
                   "dynamic": ["the resultant still tracks the angle"],
                   "color_roles": {"working": "result_intermediate",
                                   "final": "result_final"},
                   "animation_beats": ["re-establish the 90 degree case",
                                       "write Pythagoras",
                                       "reveal R = 5 N in green"],
                   "outcome": "at 90 degrees the resultant is 5 N"},
        "code": r'''from manim import *


class Segment1(Scene):
    def construct(self):
        origin = LEFT * 3.2 + DOWN * 0.9
        theta = ValueTracker(90 * DEGREES)

        def f2_end():
            a = theta.get_value()
            return origin + 2.1 * np.array([np.cos(a), np.sin(a), 0])

        def tip():
            return origin + RIGHT * 2.8 + (f2_end() - origin)

        f1 = Arrow(origin, origin + RIGHT * 2.8, buff=0,
                   color=T.vector_force, stroke_width=7)
        f2 = Arrow(origin, f2_end(), buff=0, color=T.vector_force,
                   stroke_width=7)
        f2.add_updater(lambda m: m.become(
            Arrow(origin, f2_end(), buff=0, color=T.vector_force,
                  stroke_width=7)))
        result = Arrow(origin, tip(), buff=0, color=T.result_final,
                       stroke_width=8)
        result.add_updater(lambda m: m.become(
            Arrow(origin, tip(), buff=0, color=T.result_final,
                  stroke_width=8)))
        self.add(f1, f2, result)
        self.wait(0.9)
        pyth = MathTex(r"R^2 = 4^2 + 3^2", font_size=40,
                       color=T.result_intermediate)
        pyth.move_to(RIGHT * 3.0 + UP * 1.4)
        ans = MathTex(r"R = 5\,\mathrm{N}", font_size=52,
                      color=T.result_final)
        ans.next_to(pyth, DOWN, buff=0.8)
        box = SurroundingRectangle(ans, buff=0.3, color=T.result_final)
        self.play(Write(pyth), run_time=1.5)
        emphasize(self, result, color=T.result_final, run_time=0.9)
        self.play(Write(ans), run_time=1.3)
        self.play(Create(box), run_time=0.8)
        self.play(theta.animate.set_value(130 * DEGREES), run_time=1.6)
        self.play(theta.animate.set_value(90 * DEGREES), run_time=1.6)
        self.wait(2.6)
''',
    },
]


# ---------------------------------------------------------------------------
# Test lecture: molecular geometry of methane (2D -> 3D, chemistry)
# ---------------------------------------------------------------------------

METHANE_TITLE = "Methane: from Flat Drawing to 3D Geometry"

METHANE_QUESTION = {
    "display": "Describe the three-dimensional shape of methane, "
               "$\\mathrm{CH}_4$, and its bond angles.",
    "speech": "Describe the three dimensional shape of methane, C H "
              "four, and its bond angles.",
}

METHANE_QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION", font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.0)
        line = Underline(badge, buff=0.15)
        row1 = VGroup(
            Text("Describe the 3D shape of methane, ", font_size=26,
                 color=T.text_primary),
            MathTex(r"\mathrm{CH}_4", font_size=32, color=T.variable),
            Text(", and its bond angles.", font_size=26,
                 color=T.text_primary),
        ).arrange(RIGHT, buff=0.12)
        row1.move_to(UP * 0.9)
        center = DOWN * 1.4
        carbon = Circle(radius=0.34, color=T.atom_carbon,
                        fill_color=T.atom_carbon, fill_opacity=1,
                        stroke_width=2)
        carbon.move_to(center)
        c_lab = Text("C", font_size=26, color=T.text_primary)
        c_lab.move_to(carbon)
        bonds = VGroup()
        hydrogens = VGroup()
        for direction in (UP, DOWN, LEFT, RIGHT):
            h_pos = center + direction * 1.7
            bond = Line(center + direction * 0.34,
                        h_pos - direction * 0.26, color=T.bond,
                        stroke_width=5)
            h = Circle(radius=0.24, color=T.atom_hydrogen,
                       fill_color=T.atom_hydrogen, fill_opacity=1,
                       stroke_width=2)
            h.move_to(h_pos)
            h_lab = Text("H", font_size=20, color=T.text_primary)
            h_lab.move_to(h)
            bonds.add(bond)
            hydrogens.add(VGroup(h, h_lab))
        flat_note = Text("a flat drawing hides the real geometry",
                         font_size=22, color=T.text_muted)
        flat_note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.8)
        self.play(Write(row1), run_time=2.2)
        self.play(DrawBorderThenFill(carbon), Write(c_lab), run_time=0.9)
        self.play(Create(bonds), DrawBorderThenFill(hydrogens),
                  run_time=1.6)
        self.play(Write(flat_note), run_time=1.1)
        self.wait(3.2)
        self.play(FadeOut(VGroup(carbon, c_lab, bonds, hydrogens,
                                 flat_note)), run_time=0.8)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(row1.animate.scale(0.78).to_edge(UP, buff=0.25),
                  run_time=1.0)
        self.wait(2.0)
'''

METHANE_SEGMENTS = [
    {
        "narration": "Textbooks draw methane as a flat cross: one carbon "
                     "bonded to four hydrogens in a plane. But atoms are "
                     "not flat stickers. The four bonds really push away "
                     "from each other in three dimensional space, so we "
                     "must rebuild the molecule properly.",
        "visual": {"objective": "show the conventional flat drawing and "
                                "its limitation",
                   "transition": "slide-up",
                   "visual_elements": ["flat structural diagram"],
                   "diagram": "geometry",
                   "camera_movement": "static",
                   "highlight": ["the flat cross arrangement"],
                   "color_roles": {"carbon": "atom_carbon",
                                   "hydrogens": "atom_hydrogen",
                                   "bonds": "bond"},
                   "animation_beats": ["draw the flat CH4 cross",
                                       "highlight the flatness",
                                       "announce the 3D rebuild"],
                   "outcome": "the flat drawing is only a convention"},
        "code": r'''from manim import *


class Segment0(Scene):
    def construct(self):
        title = Text("the flat drawing", font_size=28,
                     color=T.text_secondary)
        title.to_edge(UP, buff=0.4)
        center = DOWN * 0.5
        carbon = Circle(radius=0.4, color=T.atom_carbon,
                       fill_color=T.atom_carbon, fill_opacity=1,
                       stroke_width=2)
        carbon.move_to(center)
        c_lab = Text("C", font_size=28, color=T.text_primary)
        c_lab.move_to(carbon)
        cross = VGroup()
        for direction in (UP, DOWN, LEFT, RIGHT):
            h_pos = center + direction * 1.9
            bond = Line(center + direction * 0.4,
                        h_pos - direction * 0.28, color=T.bond,
                        stroke_width=6)
            h = Circle(radius=0.27, color=T.atom_hydrogen,
                       fill_color=T.atom_hydrogen, fill_opacity=1,
                       stroke_width=2)
            h.move_to(h_pos)
            h_lab = Text("H", font_size=22, color=T.text_primary)
            h_lab.move_to(h)
            cross.add(VGroup(bond, h, h_lab))
        self.play(Write(title), run_time=1.0)
        self.play(DrawBorderThenFill(carbon), Write(c_lab), run_time=1.0)
        self.play(Create(cross), run_time=2.0)
        emphasize(self, cross, color=T.atom_highlight, run_time=1.0)
        note = Text("but molecules are not flat", font_size=26,
                    color=T.warning)
        note.to_edge(DOWN, buff=0.5)
        self.play(Write(note), run_time=1.2)
        emphasize(self, note, color=T.warning, run_time=0.9)
        self.wait(3.2)
''',
    },
    {
        "narration": "Rebuild it in three dimensions: the four carbon "
                     "hydrogen bonds point to the corners of a "
                     "tetrahedron, as far apart as they can get. Let the "
                     "camera orbit to show the depth. Every angle between "
                     "two bonds is one hundred nine point five degrees, "
                     "the green result. Zooming toward one bond shows the "
                     "hydrogen pointing straight out of the cage.",
        "visual": {"objective": "build the tetrahedral 3D model, orbit "
                                "it, and reveal the bond angle",
                   "transition": "carry-over",
                   "visual_elements": ["3D tetrahedral model",
                                       "bond angle"],
                   "diagram": "geometry",
                   "camera_movement": "orbit",
                   "zoom_target": "one C-H bond",
                   "three_d": True,
                   "highlight": ["the bond angle"],
                   "color_roles": {"carbon": "atom_carbon",
                                   "hydrogens": "atom_hydrogen",
                                   "bonds": "bond",
                                   "angle": "result_final"},
                   "animation_beats": ["rebuild in 3D", "orbit the model",
                                       "zoom to a bond",
                                       "reveal 109.5\u00b0 in green"],
                   "outcome": "methane is tetrahedral, 109.5\u00b0"},
        "code": r'''from manim import *


class Segment1(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=72 * DEGREES, theta=-45 * DEGREES)
        verts = [np.array(v) for v in
                 [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]]
        verts = [v / np.linalg.norm(v) * 1.6 for v in verts]
        carbon = Sphere(radius=0.42, color=T.atom_carbon,
                        resolution=(8, 8))
        bonds = VGroup(*[Line(ORIGIN, v, color=T.bond, stroke_width=7)
                         for v in verts])
        hydrogens = VGroup(*[Sphere(radius=0.26, color=T.atom_hydrogen,
                                     resolution=(6, 6)).move_to(v)
                              for v in verts])
        caption = Text("tetrahedral geometry", font_size=28,
                       color=T.text_primary)
        caption.to_corner(UL)
        self.add_fixed_in_frame_mobjects(caption)
        self.play(DrawBorderThenFill(carbon), run_time=1.0)
        self.play(Create(bonds), DrawBorderThenFill(hydrogens),
                  run_time=2.0)
        orbit_start(self, rate=0.15)
        self.wait(2.6)
        orbit_stop(self)
        angle = MathTex(r"109.5^\circ", font_size=48, color=T.result_final)
        angle.to_corner(UR, buff=0.7)
        box = SurroundingRectangle(angle, buff=0.28, color=T.result_final)
        self.add_fixed_in_frame_mobjects(angle, box)
        self.play(Write(angle), run_time=1.2)
        self.play(Create(box), run_time=0.7)
        zoom_3d(self, zoom=1.5, phi=60 * DEGREES, run_time=1.4)
        self.wait(1.0)
        zoom_3d(self, zoom=1.0, phi=72 * DEGREES, run_time=1.2)
        self.wait(1.6)
''',
    },
]


# ---------------------------------------------------------------------------
# Test lecture: Markovnikov addition of HBr to propene (chemistry)
# ---------------------------------------------------------------------------

HBR_PROPENE_TITLE = "Why HBr Gives 2-Bromopropane"

HBR_PROPENE_QUESTION = {
    "display": "Explain why $\\mathrm{HBr}$ adds to propene to give "
               "2-bromopropane rather than 1-bromopropane.",
    "speech": "Explain why H Br adds to propene to give two "
              "bromopropane rather than one bromopropane.",
}

HBR_PROPENE_QUESTION_CODE = r'''from manim import *


def _atom(radius, role, label, label_size=18):
    circle = Circle(radius=radius, color=role, fill_color=role,
                    fill_opacity=1, stroke_width=2)
    text = Text(label, font_size=label_size, color=T.text_primary)
    text.move_to(circle)
    return VGroup(circle, text)


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION", font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.0)
        line = Underline(badge, buff=0.15)
        row1 = VGroup(
            Text("Explain why ", font_size=26, color=T.text_primary),
            MathTex(r"\mathrm{HBr}", font_size=30, color=T.text_primary),
            Text(" adds to propene to give ", font_size=26,
                 color=T.text_primary),
            MathTex(r"\text{2-bromopropane}", font_size=26,
                    color=T.result_final),
            Text(" rather than ", font_size=26, color=T.text_primary),
            MathTex(r"\text{1-bromopropane}", font_size=26,
                    color=T.warning),
            Text(".", font_size=26, color=T.text_primary),
        ).arrange(RIGHT, buff=0.1)
        row1.move_to(UP * 0.9)
        chain = MathTex(r"\mathrm{CH_3{-}CH{=}CH_2}", font_size=52,
                        color=T.text_primary)
        chain.move_to(DOWN * 1.0)
        hbr = VGroup(
            _atom(0.19, T.atom_hydrogen, "H", 14),
            _atom(0.26, T.atom_bromine, "Br", 16),
        ).arrange(RIGHT, buff=0.35)
        hbr.move_to(DOWN * 2.3)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(row1), run_time=2.2)
        self.play(Write(chain), FadeIn(hbr, shift=0.3 * DOWN), run_time=1.6)
        self.wait(1.4)
        self.play(hbr.animate.shift(LEFT * 1.4 + UP * 0.5), run_time=0.8)
        self.wait(2.0)
        self.play(FadeOut(VGroup(chain, hbr)), run_time=0.7)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(row1.animate.scale(0.78).to_edge(UP, buff=0.25),
                  run_time=1.0)
        self.wait(1.4)
'''

HBR_PROPENE_SEGMENTS = [
    {
        "narration": "Propene is a three carbon chain with a double bond "
                     "between the middle and the end carbon. Hydrogen "
                     "bromide approaches this pi bond, and the first step "
                     "is electrophilic: the proton attaches to one of the "
                     "double bond carbons, which breaks the pi bond and "
                     "leaves a carbocation behind. There are two ways "
                     "this can happen.",
        "visual": {"objective": "build propene progressively and show the "
                                "two double-bond carbons HBr can attack",
                   "transition": "slide-up",
                   "visual_elements": ["structural diagram of propene",
                                       "HBr molecule", "curved arrow"],
                   "diagram": "geometry",
                   "camera_movement": "static",
                   "highlight": ["the middle carbon",
                                 "the end carbon with more hydrogens"],
                   "color_roles": {"carbons": "atom_carbon",
                                   "hydrogens": "atom_hydrogen",
                                   "bromine": "atom_bromine",
                                   "bonds": "bond"},
                   "animation_beats": ["draw the propene chain",
                                       "highlight both alkene carbons",
                                       "bring in HBr",
                                       "curved arrow from pi bond to H"],
                   "outcome": "protonation can happen two ways"},
        "code": r'''from manim import *


def _atom(radius, role, label, label_size=18):
    circle = Circle(radius=radius, color=role, fill_color=role,
                    fill_opacity=1, stroke_width=2)
    text = Text(label, font_size=label_size, color=T.text_primary)
    text.move_to(circle)
    return VGroup(circle, text)


class Segment0(Scene):
    def construct(self):
        qline = VGroup(
            Text("why ", font_size=22, color=T.text_muted),
            MathTex(r"\mathrm{HBr}", font_size=24, color=T.text_primary),
            Text(" + propene gives 2-bromopropane?", font_size=22,
                 color=T.text_muted),
        ).arrange(RIGHT, buff=0.1)
        qline.to_edge(UP, buff=0.45)
        row_y = DOWN * 0.8
        ch3 = MathTex(r"\mathrm{CH_3}", font_size=32, color=T.text_primary)
        ch3.move_to(LEFT * 4.3 + row_y)
        b1 = Line(LEFT * 3.55 + row_y, LEFT * 2.75 + row_y, color=T.bond,
                  stroke_width=5)
        c2 = _atom(0.3, T.atom_carbon, "C", 20)
        c2.move_to(LEFT * 2.4 + row_y)
        h2 = _atom(0.17, T.atom_hydrogen, "H", 13)
        h2.move_to(c2.get_top() + UP * 0.42)
        bh2 = Line(c2.get_top() + UP * 0.1, c2.get_top() + UP * 0.25,
                   color=T.bond, stroke_width=4)
        dbl = VGroup(
            Line(LEFT * 2.05 + row_y + UP * 0.07,
                 LEFT * 0.75 + row_y + UP * 0.07, color=T.bond,
                 stroke_width=5),
            Line(LEFT * 2.05 + row_y + DOWN * 0.07,
                 LEFT * 0.75 + row_y + DOWN * 0.07, color=T.bond,
                 stroke_width=5))
        c3 = _atom(0.3, T.atom_carbon, "C", 20)
        c3.move_to(LEFT * 0.4 + row_y)
        h3a = _atom(0.17, T.atom_hydrogen, "H", 13)
        h3a.move_to(c3.get_top() + UP * 0.42)
        bh3a = Line(c3.get_top() + UP * 0.1, c3.get_top() + UP * 0.25,
                    color=T.bond, stroke_width=4)
        h3b = _atom(0.17, T.atom_hydrogen, "H", 13)
        h3b.move_to(c3.get_bottom() + DOWN * 0.42)
        bh3b = Line(c3.get_bottom() + DOWN * 0.1,
                    c3.get_bottom() + DOWN * 0.25, color=T.bond,
                    stroke_width=4)
        chain = VGroup(ch3, b1, c2, h2, bh2, dbl, c3, h3a, bh3a, h3b, bh3b)
        self.play(Write(qline), run_time=1.0)
        self.play(Write(ch3), Create(b1), DrawBorderThenFill(c2),
                  run_time=1.2)
        self.play(FadeIn(h2), Create(bh2), Create(dbl),
                  DrawBorderThenFill(c3), run_time=1.6)
        self.play(FadeIn(h3a), Create(bh3a), FadeIn(h3b), Create(bh3b),
                  run_time=1.0)
        emphasize(self, c2, color=T.atom_highlight, run_time=0.9)
        more = Text("this carbon has two H's", font_size=20,
                    color=T.text_muted)
        more.next_to(h3b, DOWN, buff=0.35)
        emphasize(self, c3, color=T.atom_highlight, run_time=0.9)
        self.play(Write(more), run_time=0.9)
        self.wait(0.6)
        hbr = VGroup(_atom(0.18, T.atom_hydrogen, "H", 13),
                     _atom(0.26, T.atom_bromine, "Br", 15))
        hbr.arrange(RIGHT, buff=0.3)
        hbr.move_to(RIGHT * 3.4 + UP * 1.7)
        self.play(FadeIn(hbr, shift=0.3 * LEFT), run_time=1.0)
        self.play(hbr.animate.move_to(RIGHT * 1.9 + UP * 0.5),
                  run_time=1.2)
        arrow = CurvedArrow(dbl.get_center() + UP * 0.4,
                            hbr[0].get_center() + DOWN * 0.2,
                            color=T.highlight_secondary, stroke_width=4)
        cleave = CurvedArrow(hbr[0].get_center() + RIGHT * 0.15,
                             hbr[1].get_center() + UP * 0.15, angle=-TAU / 6,
                             color=T.highlight_secondary, stroke_width=4)
        self.play(Create(arrow), run_time=1.0)
        self.play(Create(cleave), run_time=0.9)
        self.wait(4.2)
''',
    },
    {
        "narration": "Pathway A: the proton attaches to the end carbon, "
                     "the one with more hydrogens. The positive charge "
                     "lands on the middle carbon, giving a secondary "
                     "carbocation stabilized by two surrounding carbon "
                     "groups. Pathway B: the proton attaches to the "
                     "middle carbon, leaving the charge on the end "
                     "carbon: a primary carbocation with only one carbon "
                     "group to stabilize it. The secondary ion is far "
                     "more stable, so pathway A dominates.",
        "visual": {"objective": "compare the two protonation pathways "
                                "side by side",
                   "transition": "carry-over",
                   "visual_elements": ["two pathway panels",
                                       "carbocation structures",
                                       "stability verdicts"],
                   "diagram": "geometry",
                   "camera_movement": "static",
                   "highlight": ["pathway A's secondary carbocation",
                                 "pathway B's primary carbocation"],
                   "color_roles": {"stable pathway": "stable_state",
                                   "unstable pathway": "warning",
                                   "charges": "constant"},
                   "animation_beats": ["reveal pathway A",
                                       "show its 2\u00b0 stabilization",
                                       "reveal pathway B",
                                       "mark it 1\u00b0 and unstable",
                                       "declare A the winner"],
                   "outcome": "the secondary carbocation is the stable "
                              "route"},
        "code": r'''from manim import *


def _atom(radius, role, label, label_size=18):
    circle = Circle(radius=radius, color=role, fill_color=role,
                    fill_opacity=1, stroke_width=2)
    text = Text(label, font_size=label_size, color=T.text_primary)
    text.move_to(circle)
    return VGroup(circle, text)


class Segment1(Scene):
    def construct(self):
        title = Text("two possible protonations", font_size=28,
                     color=T.text_secondary)
        title.to_edge(UP, buff=0.45)

        def panel_a():
            head = Text("pathway A:  H to the end carbon", font_size=22,
                        color=T.text_secondary)
            left = MathTex(r"\mathrm{CH_3}", font_size=30,
                           color=T.text_primary)
            right = MathTex(r"\mathrm{CH_3}", font_size=30,
                            color=T.text_primary)
            cation = _atom(0.32, T.atom_carbon, "C", 20)
            plus = MathTex("+", font_size=36, color=T.constant)
            h = _atom(0.17, T.atom_hydrogen, "H", 13)
            row = VGroup(left, cation, right).arrange(RIGHT, buff=0.75)
            h.next_to(cation, UP, buff=0.4)
            plus.next_to(cation, DOWN, buff=0.4)
            bond_l = Line(left.get_right() + RIGHT * 0.05,
                          cation.get_left() + LEFT * 0.05, color=T.bond,
                          stroke_width=5)
            bond_r = Line(cation.get_right() + RIGHT * 0.05,
                          right.get_left() + LEFT * 0.05, color=T.bond,
                          stroke_width=5)
            return VGroup(head, row, h, plus, bond_l, bond_r)

        def panel_b():
            head = Text("pathway B:  H to the middle carbon", font_size=22,
                        color=T.text_secondary)
            left = MathTex(r"\mathrm{CH_3{,}CH_2}", font_size=30,
                           color=T.text_primary)
            cation = _atom(0.32, T.atom_carbon, "C", 20)
            plus = MathTex("+", font_size=36, color=T.constant)
            ha = _atom(0.17, T.atom_hydrogen, "H", 13)
            hb = _atom(0.17, T.atom_hydrogen, "H", 13)
            row = VGroup(left, cation).arrange(RIGHT, buff=0.85)
            ha.next_to(cation, UP, buff=0.4)
            hb.next_to(cation, DOWN, buff=0.4)
            plus.next_to(hb, DOWN, buff=0.3)
            bond = Line(left.get_right() + RIGHT * 0.05,
                        cation.get_left() + LEFT * 0.05, color=T.bond,
                        stroke_width=5)
            return VGroup(head, row, ha, hb, plus, bond)

        pa = panel_a()
        pa.move_to(LEFT * 3.4 + DOWN * 0.4)
        pb = panel_b()
        pb.move_to(RIGHT * 3.4 + DOWN * 0.4)
        subtitle = Text("same alkene, two possible cations", font_size=20,
                        color=T.text_muted)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), run_time=1.0)
        self.play(Write(subtitle), run_time=0.9)
        self.play(FadeIn(pa, shift=0.3 * RIGHT), run_time=1.4)
        hyp = VGroup(
            CurvedArrow(pa[1][0].get_top() + UP * 0.15,
                        pa[1][1].get_left() + UP * 0.3, angle=-TAU / 10,
                        color=T.text_muted, stroke_width=3),
            CurvedArrow(pa[1][2].get_top() + UP * 0.15,
                        pa[1][1].get_right() + UP * 0.3, angle=TAU / 10,
                        color=T.text_muted, stroke_width=3))
        self.play(Create(hyp), run_time=1.2)
        emphasize(self, pa[1][0], color=T.atom_highlight, run_time=0.8)
        emphasize(self, pa[1][2], color=T.atom_highlight, run_time=0.8)
        verdict_a = Text("secondary 2\u00b0 carbocation \u2014 stable",
                         font_size=22, color=T.stable_state)
        verdict_a.next_to(pa, DOWN, buff=0.5)
        self.play(Write(verdict_a), run_time=1.2)
        emphasize(self, pa[1][1], color=T.stable_state, run_time=0.9)
        note_a = Text("two alkyl groups donate electron density",
                      font_size=18, color=T.text_muted)
        note_a.next_to(verdict_a, DOWN, buff=0.25)
        self.play(Write(note_a), run_time=1.0)
        self.wait(1.6)
        self.play(FadeIn(pb, shift=0.3 * LEFT), run_time=1.4)
        verdict_b = Text("primary 1\u00b0 carbocation \u2014 unstable",
                         font_size=22, color=T.warning)
        verdict_b.next_to(pb, DOWN, buff=0.5)
        self.play(Write(verdict_b), run_time=1.2)
        emphasize(self, pb[1][1], color=T.warning, run_time=0.9)
        note_b = Text("only one alkyl group to stabilize the charge",
                      font_size=18, color=T.text_muted)
        note_b.next_to(verdict_b, DOWN, buff=0.25)
        self.play(Write(note_b), run_time=1.0)
        self.wait(1.4)
        winner = Text("pathway A wins", font_size=26, color=T.stable_state)
        winner.to_edge(DOWN, buff=0.35)
        self.play(Write(winner), run_time=1.0)
        emphasize(self, winner, color=T.stable_state, run_time=0.9)
        self.wait(3.6)
''',
    },
    {
        "narration": "On the energy profile, the route through the "
                     "secondary carbocation has the lower activation "
                     "barrier, in green, while the primary route must "
                     "climb the higher one. Bromide then attacks the "
                     "secondary center, giving two bromopropane as the "
                     "major product; the primary route yields only "
                     "traces of one bromopropane. This is Markovnikov's "
                     "rule: when H X adds to an alkene, the hydrogen "
                     "goes to the carbon that already has more "
                     "hydrogens, because that placement forms the more "
                     "stable carbocation.",
        "visual": {"objective": "show the energy profile with both "
                                "barriers, the bromide attack, both "
                                "products, and Markovnikov's rule",
                   "transition": "answer-reveal",
                   "visual_elements": ["energy profile graph",
                                       "activation energies",
                                       "bromide attack",
                                       "major + minor products", "axiom"],
                   "diagram": "graph",
                   "camera_movement": "static",
                   "highlight": ["the lower green pathway",
                                 "the final products"],
                   "color_roles": {"major route": "stable_state",
                                   "minor route": "warning",
                                   "bromine": "atom_bromine",
                                   "rule": "result_final"},
                   "animation_beats": ["draw the energy profile",
                                       "label both plateaus and barriers",
                                       "show Br\u207b attacking",
                                       "draw the major product",
                                       "draw the minor product",
                                       "reveal Markovnikov's rule"],
                   "outcome": "2-bromopropane is the kinetic product via "
                              "the stable cation"},
        "code": r'''from manim import *


def _atom(radius, role, label, label_size=18):
    circle = Circle(radius=radius, color=role, fill_color=role,
                    fill_opacity=1, stroke_width=2)
    text = Text(label, font_size=label_size, color=T.text_primary)
    text.move_to(circle)
    return VGroup(circle, text)


class Segment2(Scene):
    def construct(self):
        axes = Axes(x_range=[0, 4, 1], y_range=[0, 1.8, 0.5],
                    x_length=5.2, y_length=3.1,
                    axis_config={"color": T.text_secondary,
                                 "font_size": 16}, tips=False)
        axes.move_to(LEFT * 2.9 + DOWN * 0.2)
        x_lab = Text("reaction progress", font_size=18, color=T.text_muted)
        x_lab.next_to(axes, DOWN, buff=0.2)
        y_lab = Text("energy", font_size=18, color=T.text_muted)
        y_lab.next_to(axes, UP, buff=0.15)
        pts_a = [axes.c2p(0, 0.05), axes.c2p(0.7, 0.45),
                 axes.c2p(1.0, 1.02), axes.c2p(1.6, 0.40),
                 axes.c2p(2.0, 0.36), axes.c2p(2.4, 0.45),
                 axes.c2p(2.7, 0.70), axes.c2p(3.4, 0.12),
                 axes.c2p(4, 0.05)]
        pts_b = [axes.c2p(0, 0.05), axes.c2p(0.7, 0.75),
                 axes.c2p(1.0, 1.48), axes.c2p(1.6, 0.88),
                 axes.c2p(2.0, 0.84), axes.c2p(2.4, 0.94),
                 axes.c2p(2.7, 1.18), axes.c2p(3.4, 0.12),
                 axes.c2p(4, 0.05)]
        curve_a = VMobject().set_points_smoothly(pts_a)
        curve_a.set_stroke(T.stable_state, 5)
        curve_b = VMobject().set_points_smoothly(pts_b)
        curve_b.set_stroke(T.warning, 5)
        lab_2 = MathTex(r"2^\circ", font_size=26, color=T.stable_state)
        lab_2.next_to(axes.c2p(2.0, 0.36), DOWN, buff=0.3)
        lab_1 = MathTex(r"1^\circ", font_size=26, color=T.warning)
        lab_1.next_to(axes.c2p(2.0, 0.84), UP, buff=0.15)
        ea_low = DoubleArrow(axes.c2p(0.55, 0.05), axes.c2p(0.55, 0.72),
                             buff=0, color=T.stable_state, stroke_width=3)
        ea_low_lab = MathTex(r"E_a\ \text{low}", font_size=22,
                             color=T.stable_state)
        ea_low_lab.next_to(ea_low, LEFT, buff=0.15)
        ea_high = DoubleArrow(axes.c2p(1.45, 0.05), axes.c2p(1.45, 1.20),
                              buff=0, color=T.warning, stroke_width=3)
        ea_high_lab = MathTex(r"E_a\ \text{high}", font_size=22,
                              color=T.warning)
        ea_high_lab.next_to(ea_high, RIGHT, buff=0.15)
        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.4)
        self.play(Create(curve_a), run_time=1.6)
        emphasize(self, curve_a, color=T.stable_state, run_time=0.8)
        self.play(Create(curve_b), run_time=1.6)
        self.play(Write(lab_2), Write(lab_1), run_time=0.9)
        self.play(Create(ea_low), Write(ea_low_lab), run_time=1.0)
        self.play(Create(ea_high), Write(ea_high_lab), run_time=1.0)
        self.wait(0.8)
        br = _atom(0.26, T.atom_bromine, "Br", 15)
        br.move_to(RIGHT * 4.9 + UP * 2.0)
        minus = MathTex("-", font_size=34, color=T.constant)
        minus.next_to(br, RIGHT, buff=0.05)
        attack_label = Text("Br\u207b attacks the 2\u00b0 center",
                            font_size=20, color=T.text_muted)
        attack_label.move_to(RIGHT * 2.9 + UP * 1.05)
        self.play(FadeIn(br, shift=0.3 * LEFT), FadeIn(minus),
                  run_time=0.9)
        self.play(Write(attack_label), run_time=0.9)
        product_head = MathTex(r"\mathrm{CH_3{-}CH(Br){-}CH_3}",
                               font_size=36, color=T.text_primary)
        product_head.move_to(RIGHT * 2.9 + UP * 0.1)
        attack_arrow = CurvedArrow(br.get_bottom() + DOWN * 0.1,
                                   product_head.get_right() + UP * 0.15,
                                   angle=TAU / 6, color=T.highlight_secondary,
                                   stroke_width=4)
        self.play(Create(attack_arrow),
                  br.animate.move_to(RIGHT * 4.0 + UP * 1.35),
                  minus.animate.shift(LEFT * 0.9), run_time=1.2)
        self.play(Write(product_head), run_time=1.6)
        verdict = Text("2-bromopropane \u2014 major product", font_size=22,
                       color=T.result_final)
        verdict.move_to(RIGHT * 2.9 + DOWN * 0.9)
        box = SurroundingRectangle(verdict, buff=0.25, color=T.result_final)
        self.play(Write(verdict), run_time=1.1)
        self.play(Create(box), run_time=0.8)
        emphasize(self, verdict, color=T.result_final, run_time=0.8)
        minor = VGroup(
            MathTex(r"\mathrm{CH_3{-}CH_2{-}CH_2Br}", font_size=24,
                    color=T.text_primary),
            Text("minor", font_size=18, color=T.warning),
        ).arrange(RIGHT, buff=0.3)
        minor.move_to(RIGHT * 2.9 + DOWN * 1.75)
        self.play(Write(minor[0]), Write(minor[1]), run_time=1.2)
        reaction = MathTex(
            r"\mathrm{CH_3CH{=}CH_2 + HBr \rightarrow "
            r"CH_3CHBrCH_3 + CH_3CH_2CH_2Br}",
            font_size=22, color=T.text_secondary)
        reaction.move_to(RIGHT * 2.9 + DOWN * 2.5)
        self.play(Write(reaction), run_time=1.4)
        rule = Text("Markovnikov: H adds to the carbon with more H's "
                    "\u2014 via the more stable carbocation",
                    font_size=22, color=T.text_primary)
        rule.to_edge(DOWN, buff=0.3)
        rule_box = SurroundingRectangle(rule, buff=0.2,
                                        color=T.result_final)
        self.play(Write(rule), run_time=1.8)
        self.play(Create(rule_box), run_time=0.8)
        self.wait(2.5)
''',
    },
]


# ---------------------------------------------------------------------------
# Test lecture: numerical solved in exam format (kinematics)
# ---------------------------------------------------------------------------

KINEMATICS_TITLE = "Uniform Acceleration: a Numerical in Exam Format"

KINEMATICS_QUESTION = {
    "display": "A body starts from rest and accelerates uniformly at "
               "$3\\,\\mathrm{m/s^2}$ for $4\\,\\mathrm{s}$. Find its "
               "final velocity and the distance covered.",
    "speech": "A body starts from rest and accelerates uniformly at "
              "three meters per second squared for four seconds. Find "
              "its final velocity and the distance covered.",
}

KINEMATICS_QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION", font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.0)
        line = Underline(badge, buff=0.15)
        row1 = VGroup(
            Text("A body starts from rest and accelerates uniformly at ",
                 font_size=26, color=T.text_primary),
            MathTex(r"3\,\mathrm{m/s^2}", font_size=30, color=T.constant),
            Text(" for ", font_size=26, color=T.text_primary),
            MathTex(r"4\,\mathrm{s}", font_size=30, color=T.constant),
            Text(".", font_size=26, color=T.text_primary),
        ).arrange(RIGHT, buff=0.1)
        row2 = Text("Find its final velocity and the distance covered.",
                    font_size=26, color=T.text_primary)
        row1.move_to(UP * 1.35)
        row2.next_to(row1, DOWN, buff=0.25)
        ground = Line(LEFT * 4.5, RIGHT * 4.5, color=T.text_muted,
                       stroke_width=4)
        ground.move_to(DOWN * 1.6)
        block = RoundedRectangle(corner_radius=0.1, width=1.1, height=0.7)
        block.set_stroke(T.text_primary, 3).set_fill(T.panel, 0.9)
        block.move_to(LEFT * 2.6 + DOWN * 1.1)
        acc = Arrow(block.get_right() + RIGHT * 0.2,
                    block.get_right() + RIGHT * 1.4, buff=0,
                    color=T.vector_acceleration, stroke_width=6)
        acc_lab = MathTex("a", font_size=34, color=T.vector_acceleration)
        acc_lab.next_to(acc, UP, buff=0.15)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(row1), run_time=2.6)
        self.play(Create(ground), DrawBorderThenFill(block), run_time=1.2)
        self.play(GrowArrow(acc), Write(acc_lab), run_time=0.9)
        self.play(block.animate(rate_func=rate_functions.ease_in_out_sine
                                ).shift(RIGHT * 1.6),
                  acc.animate.shift(RIGHT * 1.6),
                  acc_lab.animate.shift(RIGHT * 1.6), run_time=1.2)
        self.wait(1.2)
        self.play(FadeOut(VGroup(ground, block, acc, acc_lab)),
                  run_time=0.7)
        rows = VGroup(row1, row2)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.78).to_edge(UP, buff=0.25),
                  run_time=1.0)
        self.wait(0.8)
'''

KINEMATICS_SEGMENTS = [
    {
        "narration": "List the given data with standard symbols. The body "
                     "starts from rest, so the initial velocity u is zero. "
                     "The acceleration a is three meters per second "
                     "squared, and the time t is four seconds. All values "
                     "are already in S I units, so no conversion is "
                     "needed. We need to find the final velocity v, and "
                     "the distance s. The governing formulas: v equals u "
                     "plus a t, and s equals u t plus one half a t "
                     "squared.",
        "visual": {"objective": "present the Given / To Find / Formula "
                                "stages of the numerical format",
                   "transition": "slide-up",
                   "visual_elements": ["given data list", "unknowns",
                                       "formulas"],
                   "diagram": "none",
                   "camera_movement": "static",
                   "highlight": ["each given symbol",
                                 "each unknown with its question mark"],
                   "color_roles": {"symbols": "variable",
                                   "values": "constant",
                                   "headers": "text_secondary"},
                   "animation_beats": ["write the Given (Data) block",
                                       "note that values are in SI",
                                       "write the To Find block",
                                       "write both formulas"],
                   "outcome": "the problem is fully set up"},
        "code": r'''from manim import *


class Segment0(Scene):
    def construct(self):
        qline = VGroup(
            Text("a body accelerates from rest at ", font_size=20,
                 color=T.text_muted),
            MathTex(r"3\,\mathrm{m/s^2}", font_size=22,
                    color=T.constant),
            Text(" for ", font_size=20, color=T.text_muted),
            MathTex(r"4\,\mathrm{s}", font_size=22, color=T.constant),
            Text(" \u2014 find v and s", font_size=20,
                 color=T.text_muted),
        ).arrange(RIGHT, buff=0.08)
        qline.to_edge(UP, buff=0.3)
        given_head = Text("Given (Data)", font_size=28,
                          color=T.text_secondary)
        given_head.move_to(LEFT * 3.3 + UP * 1.5)
        g1 = MathTex("u = 0", font_size=34, color=T.variable)
        g1_note = Text("(starts from rest)", font_size=18,
                        color=T.text_muted)
        g2 = MathTex(r"a = 3\,\mathrm{m/s^2}", font_size=34,
                     color=T.variable)
        g3 = MathTex(r"t = 4\,\mathrm{s}", font_size=34,
                     color=T.variable)
        given = VGroup(g1, g2, g3).arrange(DOWN, aligned_edge=LEFT,
                                           buff=0.4)
        given.next_to(given_head, DOWN, buff=0.4)
        g1_note.next_to(g1, RIGHT, buff=0.3)
        si_note = Text("all values already in SI units", font_size=18,
                       color=T.text_muted)
        si_note.next_to(given, DOWN, buff=0.4)
        find_head = Text("To Find", font_size=28, color=T.text_secondary)
        find_head.move_to(RIGHT * 3.3 + UP * 1.5)
        f1 = MathTex(r"v = ?", font_size=40, color=T.constant)
        f2 = MathTex(r"s = ?", font_size=40, color=T.constant)
        finds = VGroup(f1, f2).arrange(DOWN, buff=0.5)
        finds.next_to(find_head, DOWN, buff=0.5)
        formula_head = Text("Formula", font_size=28,
                            color=T.text_secondary)
        formula_head.move_to(DOWN * 1.4)
        form1 = MathTex(r"v = u + at", font_size=40, color=T.variable)
        form2 = MathTex(r"s = ut + \tfrac{1}{2}at^2", font_size=40,
                        color=T.variable)
        forms = VGroup(form1, form2).arrange(RIGHT, buff=1.2)
        forms.next_to(formula_head, DOWN, buff=0.4)
        self.play(Write(qline), run_time=1.0)
        self.play(Write(given_head), run_time=0.9)
        self.play(Write(g1), FadeIn(g1_note), run_time=1.0)
        emphasize(self, g1, color=T.variable, run_time=0.7)
        self.play(Write(g2), run_time=0.9)
        self.play(Write(g3), run_time=0.9)
        self.play(Write(si_note), run_time=0.9)
        self.play(Write(find_head), run_time=0.8)
        self.play(Write(f1), run_time=0.8)
        emphasize(self, f1, color=T.constant, run_time=0.6)
        self.play(Write(f2), run_time=0.8)
        emphasize(self, f2, color=T.constant, run_time=0.6)
        self.play(Write(formula_head), run_time=0.8)
        self.play(Write(form1), run_time=1.2)
        self.play(Write(form2), run_time=1.4)
        self.wait(2.6)
''',
    },
    {
        "narration": "Substitute into the first formula: v equals zero "
                     "plus three times four, which gives twelve meters "
                     "per second. For the distance, since u is zero, the "
                     "u t term cancels, struck through in red, leaving s "
                     "equals one half a t squared. One half of three "
                     "times sixteen gives twenty four meters. On the "
                     "velocity time graph, the area under the line is "
                     "exactly this distance: watch the rectangles narrow "
                     "as the sum approaches the true area.",
        "visual": {"objective": "substitute step by step, cancel the "
                                "zero term with a red strike, and show "
                                "the area under the v-t curve as "
                                "narrowing Riemann rectangles",
                   "transition": "carry-over",
                   "visual_elements": ["calculation steps",
                                       "cancellation strike",
                                       "v-t graph with Riemann sum"],
                   "diagram": "graph",
                   "camera_movement": "static",
                   "highlight": ["the substituted values",
                                 "the cancelled term",
                                 "the rectangles under the line"],
                   "cancellation": True,
                   "integration": True,
                   "color_roles": {"working": "result_intermediate",
                                   "cancel mark": "cancel_mark",
                                   "graph line": "graph_function"},
                   "animation_beats": ["write the Calculation header",
                                       "substitute into v = u + at",
                                       "strike and remove the zero term",
                                       "evaluate s",
                                       "refine the Riemann rectangles"],
                   "outcome": "v = 12 m/s and s = 24 m, with the graph "
                              "explaining why"},
        "code": r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Calculation", font_size=28, color=T.text_secondary)
        head.to_corner(UL, buff=0.5)
        c1 = MathTex("v = u + at", font_size=34, color=T.variable)
        c2 = MathTex(r"v = 0 + (3)(4)", font_size=34,
                     color=T.result_intermediate)
        c3 = MathTex(r"v = 12\,\mathrm{m/s}", font_size=36,
                      color=T.result_intermediate)
        s1 = MathTex("s", "=", "0", r"\cdot", "t", "+",
                     r"\tfrac{1}{2}", "a", "t^2", font_size=34)
        s1[0].set_color(T.variable)
        s1[2].set_color(T.constant)
        s1[7].set_color(T.variable)
        zero_term = VGroup(s1[2], s1[3], s1[4])
        s_clean = MathTex("s", "=", r"\tfrac{1}{2}", "a", "t^2",
                          font_size=34)
        s_clean[0].set_color(T.variable)
        s_clean[2].set_color(T.constant)
        s2 = MathTex(r"s = \tfrac{1}{2}(3)(4^2)", font_size=34,
                     color=T.result_intermediate)
        s3 = MathTex(r"s = \tfrac{1}{2}(3)(16) = 24\,\mathrm{m}",
                     font_size=36, color=T.result_intermediate)
        steps = VGroup(c1, c2, c3, s1, s2, s3)
        steps.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        steps.next_to(head, DOWN, buff=0.45).to_edge(LEFT, buff=0.6)
        s_clean.move_to(s1)
        axes = Axes(x_range=[0, 5, 1], y_range=[0, 14, 2],
                    x_length=4.6, y_length=3.4,
                    axis_config={"color": T.text_secondary,
                                 "font_size": 16}, tips=False)
        axes.move_to(RIGHT * 3.1 + DOWN * 0.4)
        x_lab = Text("t (s)", font_size=16, color=T.text_muted)
        x_lab.next_to(axes.x_axis, RIGHT, buff=0.1)
        y_lab = Text("v (m/s)", font_size=16, color=T.text_muted)
        y_lab.next_to(axes.y_axis, UP, buff=0.1)
        vt = axes.plot(lambda t: 3 * t, x_range=[0, 4],
                       color=T.graph_function, stroke_width=5)
        area_lab = Text("area = distance = 24 m", font_size=18,
                        color=T.text_muted)
        area_lab.next_to(axes, DOWN, buff=0.35)
        self.play(Write(head), run_time=0.9)
        self.play(Write(c1), run_time=1.0)
        self.play(Write(c2), run_time=1.1)
        self.play(Write(c3), run_time=1.0)
        emphasize(self, c3, color=T.result_intermediate, run_time=0.7)
        self.play(Write(s1), run_time=1.2)
        cancel_terms(self, zero_term)
        self.play(FadeOut(VGroup(s1[0], s1[1], s1[5:])), run_time=0.5)
        self.play(Write(s_clean), run_time=1.0)
        self.play(Write(s2), run_time=1.0)
        self.play(Write(s3), run_time=1.0)
        self.wait(0.5)
        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)
        self.play(Create(vt), run_time=1.1)
        rects = riemann_rectangles(axes, lambda t: 3 * t, 0, 4, 4)
        self.play(FadeIn(rects), run_time=0.9)
        self.play(Transform(rects, riemann_rectangles(axes,
                                                      lambda t: 3 * t,
                                                      0, 4, 12)),
                  run_time=1.4)
        self.play(Write(area_lab), run_time=0.9)
        self.wait(2.4)
''',
    },
    {
        "narration": "Boxing the final answers with their units: the "
                     "final velocity is twelve meters per second, and "
                     "the distance covered is twenty four meters. "
                     "Always carry the S I unit into the boxed answer.",
        "visual": {"objective": "reveal the boxed final answers with SI "
                                "units",
                   "transition": "answer-reveal",
                   "visual_elements": ["boxed results"],
                   "diagram": "none",
                   "camera_movement": "static",
                   "highlight": ["both boxed answers"],
                   "color_roles": {"answers": "result_final"},
                   "animation_beats": ["clear the working",
                                       "box v = 12 m/s",
                                       "box s = 24 m",
                                       "close with the units reminder"],
                   "outcome": "the numerical is complete"},
        "code": r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Final Answer", font_size=30, color=T.text_secondary)
        head.to_edge(UP, buff=0.6)
        v_ans = MathTex(r"v = 12\,\mathrm{m/s}", font_size=52,
                        color=T.result_final)
        s_ans = MathTex(r"s = 24\,\mathrm{m}", font_size=52,
                        color=T.result_final)
        pair = VGroup(v_ans, s_ans).arrange(RIGHT, buff=1.4)
        pair.move_to(UP * 0.6)
        v_box = SurroundingRectangle(v_ans, buff=0.3,
                                    color=T.result_final)
        s_box = SurroundingRectangle(s_ans, buff=0.3,
                                     color=T.result_final)
        note = Text("always include the SI unit in the boxed answer",
                    font_size=22, color=T.text_muted)
        note.next_to(pair, DOWN, buff=0.9)
        thanks = Text("thanks for watching", font_size=24,
                      color=T.text_muted)
        thanks.to_edge(DOWN, buff=0.5)
        self.play(Write(head), run_time=0.9)
        self.play(Write(v_ans), run_time=1.2)
        self.play(Create(v_box), run_time=0.7)
        emphasize(self, v_ans, color=T.result_final, run_time=0.8)
        self.play(Write(s_ans), run_time=1.2)
        self.play(Create(s_box), run_time=0.7)
        emphasize(self, s_ans, color=T.result_final, run_time=0.8)
        self.play(Write(note), run_time=1.1)
        self.play(FadeIn(thanks, shift=0.3 * UP), run_time=0.8)
        self.wait(2.4)
''',
    },
]


# ---------------------------------------------------------------------------
# Bundled lecture registry
# ---------------------------------------------------------------------------

from .charged_spheres import LECTURE as _CHARGED_SPHERES  # noqa: E402
from .hard_problem_set import LECTURE as _HARD_PROBLEM_SET  # noqa: E402
from .diels_alder import LECTURE as _DIELS_ALDER  # noqa: E402
from .lens_mirror import LECTURE as _LENS_MIRROR  # noqa: E402
from .heat_plate import LECTURE as _HEAT_PLATE  # noqa: E402
from .biot_savart import LECTURE as _BIOT_SAVART  # noqa: E402
from .e_pi_inequality import LECTURE as _E_PI_INEQUALITY  # noqa: E402
from .car_circular_road import LECTURE as _CAR_CIRCULAR_ROAD  # noqa: E402
from .macro_economy import LECTURE as _MACRO_ECONOMY  # noqa: E402
from .shm_particle import LECTURE as _SHM_PARTICLE  # noqa: E402
from .two_discs_rotation import LECTURE as _TWO_DISCS_ROTATION  # noqa: E402
from .gabriels_horn import LECTURE as _GABRIELS_HORN  # noqa: E402
from .trig_sum_integral import LECTURE as _TRIG_SUM_INTEGRAL  # noqa: E402
from .determinant_limit import LECTURE as _DETERMINANT_LIMIT  # noqa: E402
from .triple_integral import LECTURE as _TRIPLE_INTEGRAL  # noqa: E402
from .double_integral_polar import LECTURE as _DOUBLE_INTEGRAL_POLAR  # noqa: E402
from .de_phi import LECTURE as _DE_PHI  # noqa: E402
from .piecewise_continuity import LECTURE as _PIECEWISE_CONTINUITY  # noqa: E402
from .calc2_limits import LECTURE as _CALC2_LIMITS  # noqa: E402
from .calc3_limits import LECTURE as _CALC3_LIMITS  # noqa: E402
from .rational_integral_x5 import LECTURE as _RATIONAL_INTEGRAL_X5  # noqa: E402
from .norbornyl_bromide import LECTURE as _NORBORNYL_BROMIDE  # noqa: E402
from .keto_enol import LECTURE as _KETO_ENOL  # noqa: E402
from .diacid_decarboxylation import LECTURE as _DIACID_DECARBOXYLATION  # noqa: E402
from .locked_bromide import LECTURE as _LOCKED_BROMIDE  # noqa: E402
from .molarity_acetate import LECTURE as _MOLARITY_ACETATE  # noqa: E402
from .sugar_molarity import LECTURE as _SUGAR_MOLARITY  # noqa: E402
from .hcp_voids import LECTURE as _HCP_VOIDS  # noqa: E402
from .packing_efficiency import LECTURE as _PACKING_EFFICIENCY  # noqa: E402
from .ionisation_n2 import LECTURE as _IONISATION_N2  # noqa: E402
from .periodic_trends import LECTURE as _PERIODIC_TRENDS  # noqa: E402
from .hess_law import LECTURE as _HESS_LAW  # noqa: E402
from .vsepr_angles import LECTURE as _VSEPR_ANGLES  # noqa: E402
from .redox_oxidation import LECTURE as _REDOX_OXIDATION  # noqa: E402
from .mass_action import LECTURE as _MASS_ACTION  # noqa: E402
from .mech_marathon import LECTURE as _MECH_MARATHON  # noqa: E402
from .navier_stokes_blowup import LECTURE as _NAVIER_STOKES_BLOWUP  # noqa: E402
from .thirty_formulas import LECTURE as _THIRTY_FORMULAS  # noqa: E402
from .kinematics_chapter import LECTURE as _KINEMATICS_CHAPTER  # noqa: E402
from .work_energy_theorem import LECTURE as _WORK_ENERGY_THEOREM  # noqa: E402

BUNDLED_LECTURES = {
    "pythagoras": {
        "title": PYTHAGOREAN_TITLE,
        "preset": "math",
        "question": PYTHAGOREAN_QUESTION,
        "question_code": PYTHAGOREAN_QUESTION_CODE,
        "segments": PYTHAGOREAN_SEGMENTS,
    },
    "fma": {
        "title": FMA_TITLE,
        "preset": "math",
        "question": FMA_QUESTION,
        "question_code": FMA_QUESTION_CODE,
        "segments": FMA_SEGMENTS,
    },
    "car-friction": {
        "title": CAR_FRICTION_TITLE,
        "preset": "lab",
        "question": CAR_FRICTION_QUESTION,
        "question_code": CAR_FRICTION_QUESTION_CODE,
        "segments": CAR_FRICTION_SEGMENTS,
    },
    "spring-blocks": {
        "title": SPRING_BLOCKS_TITLE,
        "preset": "math",
        "question": SPRING_BLOCKS_QUESTION,
        "question_code": SPRING_BLOCKS_QUESTION_CODE,
        "segments": SPRING_BLOCKS_SEGMENTS,
    },
    "derivative": {
        "title": DERIVATIVE_TITLE,
        "preset": "math",
        "format": "derivation",
        "question": DERIVATIVE_QUESTION,
        "question_code": DERIVATIVE_QUESTION_CODE,
        "segments": DERIVATIVE_SEGMENTS,
    },
    "unit-circle": {
        "title": CIRCLE_TITLE,
        "preset": "math",
        "question": CIRCLE_QUESTION,
        "question_code": CIRCLE_QUESTION_CODE,
        "segments": CIRCLE_SEGMENTS,
    },
    "surface3d": {
        "title": SURFACE3D_TITLE,
        "preset": "spatial",
        "question": SURFACE3D_QUESTION,
        "question_code": SURFACE3D_QUESTION_CODE,
        "segments": SURFACE3D_SEGMENTS,
    },
    "quadratic": {
        "title": QUADRATIC_TITLE,
        "preset": "math",
        "question": QUADRATIC_QUESTION,
        "question_code": QUADRATIC_QUESTION_CODE,
        "segments": QUADRATIC_SEGMENTS,
    },
    "vectors": {
        "title": VECTORS_TITLE,
        "preset": "lab",
        "question": VECTORS_QUESTION,
        "question_code": VECTORS_QUESTION_CODE,
        "segments": VECTORS_SEGMENTS,
    },
    "methane": {
        "title": METHANE_TITLE,
        "preset": "spatial",
        "question": METHANE_QUESTION,
        "question_code": METHANE_QUESTION_CODE,
        "segments": METHANE_SEGMENTS,
    },
    "hbr-propene": {
        "title": HBR_PROPENE_TITLE,
        "preset": "lab",
        "format": "organic-reaction",
        "question": HBR_PROPENE_QUESTION,
        "question_code": HBR_PROPENE_QUESTION_CODE,
        "segments": HBR_PROPENE_SEGMENTS,
    },
    "kinematics-numerical": {
        "title": KINEMATICS_TITLE,
        "preset": "lab",
        "format": "numerical",
        "question": KINEMATICS_QUESTION,
        "question_code": KINEMATICS_QUESTION_CODE,
        "segments": KINEMATICS_SEGMENTS,
    },
    "charged-spheres": _CHARGED_SPHERES,
    "hard-problem-set": _HARD_PROBLEM_SET,
    "diels-alder": _DIELS_ALDER,
    "lens-mirror": _LENS_MIRROR,
    "heat-plate": _HEAT_PLATE,
    "biot-savart": _BIOT_SAVART,
    "e-pi-inequality": _E_PI_INEQUALITY,
    "car-circular-road": _CAR_CIRCULAR_ROAD,
    "macro-economy": _MACRO_ECONOMY,
    "shm-particle": _SHM_PARTICLE,
    "two-discs-rotation": _TWO_DISCS_ROTATION,
    "gabriels-horn": _GABRIELS_HORN,
    "trig-sum-integral": _TRIG_SUM_INTEGRAL,
    "determinant-limit": _DETERMINANT_LIMIT,
    "triple-integral": _TRIPLE_INTEGRAL,
    "double-integral-polar": _DOUBLE_INTEGRAL_POLAR,
    "de-phi": _DE_PHI,
    "piecewise-continuity": _PIECEWISE_CONTINUITY,
    "calc2-limits": _CALC2_LIMITS,
    "calc3-limits": _CALC3_LIMITS,
    "rational-integral-x5": _RATIONAL_INTEGRAL_X5,
    "norbornyl-bromide": _NORBORNYL_BROMIDE,
    "keto-enol": _KETO_ENOL,
    "diacid-decarboxylation": _DIACID_DECARBOXYLATION,
    "locked-bromide": _LOCKED_BROMIDE,
    "molarity-acetate": _MOLARITY_ACETATE,
    "sugar-molarity": _SUGAR_MOLARITY,
    "hcp-voids": _HCP_VOIDS,
    "packing-efficiency": _PACKING_EFFICIENCY,
    "ionisation-n2": _IONISATION_N2,
    "periodic-trends": _PERIODIC_TRENDS,
    "hess-law": _HESS_LAW,
    "vsepr-angles": _VSEPR_ANGLES,
    "redox-oxidation": _REDOX_OXIDATION,
    "mass-action": _MASS_ACTION,
    "mechanics-marathon": _MECH_MARATHON,
    "navier-stokes-blowup": _NAVIER_STOKES_BLOWUP,
    "thirty-formulas": _THIRTY_FORMULAS,
    "kinematics-chapter": _KINEMATICS_CHAPTER,
    "work-energy-theorem": _WORK_ENERGY_THEOREM,
}

_TOPIC_ALIASES = {
    "charged-spheres": "charged-spheres",
    "charged": "charged-spheres",
    "spheres": "charged-spheres",
    "electrostatics": "charged-spheres",
    "coulomb": "charged-spheres",
    "gauss": "charged-spheres",
    "gauss-law": "charged-spheres",
    "pythagorean": "pythagoras",
    "pythagorean-theorem": "pythagoras",
    "fma": "fma",
    "f-ma": "fma",
    "newton": "fma",
    "newton-s-second-law": "fma",
    "newtons-second-law": "fma",
    "force": "fma",
    "car": "car-friction",
    "friction": "car-friction",
    "car-friction": "car-friction",
    "moving-car": "car-friction",
    "tire": "car-friction",
    "spring": "spring-blocks",
    "springs": "spring-blocks",
    "blocks": "spring-blocks",
    "two-block": "spring-blocks",
    "two-block-spring": "spring-blocks",
    "spring-block-system": "spring-blocks",
    "collision": "spring-blocks",
    "derivative": "derivative",
    "derivatives": "derivative",
    "secant": "derivative",
    "tangent": "derivative",
    "calculus": "derivative",
    "differentiation": "derivative",
    "circle": "unit-circle",
    "unitcircle": "unit-circle",
    "unit-circle": "unit-circle",
    "trig": "unit-circle",
    "trigonometry": "unit-circle",
    "sine": "unit-circle",
    "cosine": "unit-circle",
    "surface": "surface3d",
    "3d-surface": "surface3d",
    "surfaces": "surface3d",
    "paraboloid": "surface3d",
    "quadratic": "quadratic",
    "quadratics": "quadratic",
    "factor": "quadratic",
    "factoring": "quadratic",
    "quadratic-equation": "quadratic",
    "solve": "quadratic",
    "vector": "vectors",
    "vectors": "vectors",
    "vector-addition": "vectors",
    "resultant": "vectors",
    "forces": "vectors",
    "methane": "methane",
    "ch4": "methane",
    "molecule": "methane",
    "molecular": "methane",
    "tetrahedral": "methane",
    "chemistry": "methane",
    "bond-angle": "methane",
    "hbr": "hbr-propene",
    "markovnikov": "hbr-propene",
    "propene": "hbr-propene",
    "alkene": "hbr-propene",
    "addition": "hbr-propene",
    "bromopropane": "hbr-propene",
    "numerical": "kinematics-numerical",
    "numericals": "kinematics-numerical",
    "kinematics": "kinematics-numerical",
    "acceleration": "kinematics-numerical",
    "given-data": "kinematics-numerical",
    "problem-set": "hard-problem-set",
    "hard-problems": "hard-problem-set",
    "hps": "hard-problem-set",
    "diels-alder": "diels-alder",
    "dielsalder": "diels-alder",
    "cycloaddition": "diels-alder",
    "butadiene": "diels-alder",
    "maleic": "diels-alder",
    "malic-anhydride": "diels-alder",
    "d-a": "diels-alder",
    "lens-mirror": "lens-mirror",
    "lensmirror": "lens-mirror",
    "optics": "lens-mirror",
    "lens": "lens-mirror",
    "mirror": "lens-mirror",
    "plane-mirror": "lens-mirror",
    "heat-equation": "heat-plate",
    "heat-plate": "heat-plate",
    "pde": "heat-plate",
    "heat": "heat-plate",
    "temperature": "heat-plate",
    "biot": "biot-savart",
    "biot-savart-law": "biot-savart",
    "magnetic-field": "biot-savart",
    "bsl": "biot-savart",
    "e-pi": "e-pi-inequality",
    "epi": "e-pi-inequality",
    "e-to-pi": "e-pi-inequality",
    "exponential-inequality": "e-pi-inequality",
    "lnx-x": "e-pi-inequality",
    "integration-inequality": "e-pi-inequality",
    "circular-road": "car-circular-road",
    "centripetal": "car-circular-road",
    "circular-motion": "car-circular-road",
    "inflation": "macro-economy",
    "macroeconomics": "macro-economy",
    "economy": "macro-economy",
    "unemployment": "macro-economy",
    "shm": "shm-particle",
    "simple-harmonic-motion": "shm-particle",
    "oscillation": "shm-particle",
    "harmonic": "shm-particle",
    "two-discs": "two-discs-rotation",
    "discs": "two-discs-rotation",
    "rotational-motion": "two-discs-rotation",
    "angular-momentum": "two-discs-rotation",
    "gabriel": "gabriels-horn",
    "gabriels-horn-paradox": "gabriels-horn",
    "horn": "gabriels-horn",
    "surface-of-revolution": "gabriels-horn",
    "solid-of-revolution": "gabriels-horn",
    "trig-sum": "trig-sum-integral",
    "trigonometric-sum": "trig-sum-integral",
    "tan8x": "trig-sum-integral",
    "determinant": "determinant-limit",
    "determinant-sum": "determinant-limit",
    "det-limit": "determinant-limit",
    "triple-integral": "triple-integral",
    "spherical-integral": "triple-integral",
    "spherical-coordinates": "triple-integral",
    "double-integral": "double-integral-polar",
    "polar-double-integral": "double-integral-polar",
    "two-circles": "double-integral-polar",
    "phi-differential-equation": "de-phi",
    "ode-phi": "de-phi",
    "differential-equation": "de-phi",
    "piecewise": "piecewise-continuity",
    "continuity": "piecewise-continuity",
    "rational-irrational": "piecewise-continuity",
    "calculus-2": "calc2-limits",
    "nested-limit": "calc2-limits",
    "telescoping-sum": "calc2-limits",
    "calculus-3": "calc3-limits",
    "multivariable-limits": "calc3-limits",
    "path-dependence": "calc3-limits",
    "x5-integral": "rational-integral-x5",
    "rational-integral": "rational-integral-x5",
    "partial-fractions": "rational-integral-x5",
    "bicyclo": "norbornyl-bromide",
    "norbornane": "norbornyl-bromide",
    "bridged-halide": "norbornyl-bromide",
    "enol": "keto-enol",
    "tautomerism": "keto-enol",
    "acetylacetone": "keto-enol",
    "malonic": "diacid-decarboxylation",
    "decarboxylation": "diacid-decarboxylation",
    "dicarboxylic": "diacid-decarboxylation",
    "e2-elimination": "locked-bromide",
    "chair-flip": "locked-bromide",
    "equatorial-bromide": "locked-bromide",
    "molarity": "molarity-acetate",
    "sodium-acetate": "molarity-acetate",
    "sugar": "sugar-molarity",
    "sucrose": "sugar-molarity",
    "close-packing": "hcp-voids",
    "voids": "hcp-voids",
    "tetrahedral-voids": "hcp-voids",
    "octahedral-voids": "hcp-voids",
    "packing": "packing-efficiency",
    "close-packed": "packing-efficiency",
    "ionisation-enthalpy": "ionisation-n2",
    "bohr-energy": "ionisation-n2",
    "trends": "periodic-trends",
    "periodic-properties": "periodic-trends",
    "enthalpy": "hess-law",
    "thermochemistry": "hess-law",
    "vsepr": "vsepr-angles",
    "hybridisation": "vsepr-angles",
    "redox": "redox-oxidation",
    "oxidation-numbers": "redox-oxidation",
    "equilibrium": "mass-action",
    "kc": "mass-action",
    "ammonia-equilibrium": "mass-action",
    "mechanics": "mechanics-marathon",
    "marathon": "mechanics-marathon",
    "inclined-wedge": "mechanics-marathon",
    "loop-the-loop": "mechanics-marathon",
    "rotational-dynamics": "mechanics-marathon",
    "restitution": "mechanics-marathon",
    "projectile": "mechanics-marathon",
    "kepler": "mechanics-marathon",
    "terminal-velocity": "mechanics-marathon",
    "stokes-law": "mechanics-marathon",
    "bernoulli": "mechanics-marathon",
    "buoyancy": "mechanics-marathon",
    "elasticity": "mechanics-marathon",
    "navier-stokes": "navier-stokes-blowup",
    "ns-equations": "navier-stokes-blowup",
    "millennium-prize": "navier-stokes-blowup",
    "clay-problems": "navier-stokes-blowup",
    "blowup": "navier-stokes-blowup",
    "euler-equations": "navier-stokes-blowup",
    "regularity": "navier-stokes-blowup",
    "vortex-stretching": "navier-stokes-blowup",
    "formula-derivations": "thirty-formulas",
    "theorem-derivations": "thirty-formulas",
    "first-principles": "thirty-formulas",
    "algebra-calculus": "thirty-formulas",
    "sine-rule": "thirty-formulas",
    "cosine-rule": "thirty-formulas",
    "parabola-equation": "thirty-formulas",
    "ellipse-equation": "thirty-formulas",
    "distance-formula": "thirty-formulas",
    "section-formula": "thirty-formulas",
    "circle-equation": "thirty-formulas",
    "integration-by-parts": "thirty-formulas",
    "chain-rule": "thirty-formulas",
    "product-rule": "thirty-formulas",
    "quotient-rule": "thirty-formulas",
    "power-rule": "thirty-formulas",
    "fundamental-theorem-calculus": "thirty-formulas",
    "disk-method": "thirty-formulas",
    "volume-revolution": "thirty-formulas",
    "dot-product": "thirty-formulas",
    "cross-product": "thirty-formulas",
    "plane-equation": "thirty-formulas",
    "herons-formula": "thirty-formulas",
    "bayes-theorem": "thirty-formulas",
    "euler-polyhedra": "thirty-formulas",
    "kinematics-chapter-course": "kinematics-chapter",
    "kinematics-course": "kinematics-chapter",
    "chapter-lecture": "kinematics-chapter",
    "motion-chapter": "kinematics-chapter",
    "rectilinear-motion": "kinematics-chapter",
    "projectile-motion": "kinematics-chapter",
    "relative-motion": "kinematics-chapter",
    "constrained-motion": "kinematics-chapter",
    "free-fall-motion": "kinematics-chapter",
    "rain-man-problem": "kinematics-chapter",
    "river-boat-problem": "kinematics-chapter",
    "reference-frames": "kinematics-chapter",
    "equations-of-motion": "kinematics-chapter",
    "overtaking": "kinematics-chapter",
    "catch-up-problems": "kinematics-chapter",
    "trajectory": "kinematics-chapter",
    "envelope-of-projectiles": "kinematics-chapter",
    "pursuit-problems": "kinematics-chapter",
    "pulley-systems": "kinematics-chapter",
    "angular-velocity": "kinematics-chapter",
    "jerk-kinematics": "kinematics-chapter",
    "motion-graphs": "kinematics-chapter",
    "work-energy": "work-energy-theorem",
    "kinetic-energy": "work-energy-theorem",
    "work-done": "work-energy-theorem",
    "energy-theorem": "work-energy-theorem",
    "work-energy-application": "work-energy-theorem",
}


def normalize_topic(topic: object) -> str:
    """Map user input like 'F=ma' (or the bare --demo flag) to a lecture key."""
    if topic is True or not topic:
        return "pythagoras"
    key = re.sub(r"[^a-z0-9]+", "-", str(topic).lower()).strip("-")
    if not key:
        return "pythagoras"
    if key in BUNDLED_LECTURES:
        return key
    if key in _TOPIC_ALIASES:
        return _TOPIC_ALIASES[key]
    available = ", ".join(sorted(BUNDLED_LECTURES))
    raise ValueError(f"no bundled lecture for {topic!r} (available: {available})")


def bundled_topics() -> list[str]:
    return sorted(BUNDLED_LECTURES)


def demo_plan(topic: object = "pythagoras") -> dict:
    """Offline lecture plan used by `--demo [TOPIC]`.

    Returns {"title", "preset", "format", "question", "segments"} where
    each segment may carry a "visual" plan for the director.
    """
    lecture = BUNDLED_LECTURES[normalize_topic(topic)]
    return {"title": lecture["title"],
            "preset": lecture.get("preset", "math"),
            "format": lecture.get("format", "conceptual"),
            "question": lecture.get("question"),
            "segments": [{"index": i, "narration": seg["narration"],
                          "visual": seg.get("visual")}
                         for i, seg in enumerate(lecture["segments"])]}


def demo_question_code(topic: object) -> str:
    return BUNDLED_LECTURES[normalize_topic(topic)]["question_code"]


def demo_code(topic: object, index: int) -> str:
    return BUNDLED_LECTURES[normalize_topic(topic)]["segments"][index]["code"]
