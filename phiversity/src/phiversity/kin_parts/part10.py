PART = [
{
 "narration":
  "Calculus is the native language of kinematics. Position is a "
  "function of time; velocity is its derivative and acceleration is "
  "the derivative of velocity. Going backward, integration of "
  "acceleration gives velocity up to a constant, fixed by the "
  "initial condition, and integration of velocity gives position. "
  "Every kinematic formula we have used is a special case of these "
  "two operations. The boundary conditions are not decoration: they "
  "are what make the answer unique.",
 "visual": {"style": "calculus kinematics", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment54(Scene):
    def construct(self):
        head = Text("LESSON 55 - DERIVATIVES AND INTEGRALS OF MOTION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"v(t)=\frac{dx}{dt},\qquad a(t)=\frac{dv}{dt}=\frac{d^{2}x}{dt^{2}}",
                     font_size=30, color=T.result_final)
        r2 = MathTex(r"v(t)=v(t_0)+\int_{t_0}^{t}a(t')\,dt'", font_size=30,
                     color=T.result_final)
        r3 = MathTex(r"x(t)=x(t_0)+\int_{t_0}^{t}v(t')\,dt'", font_size=30,
                     color=T.result_final)
        r4 = MathTex(r"\text{initial conditions set the constants}",
                     font_size=27, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.38)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.8)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.8)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.5)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "When acceleration depends on time, integrate it. If a equals k t, "
  "velocity is u plus k t squared over two, and position is x zero "
  "plus u t plus k t cubed over six. If a is sinusoidal, integrate "
  "to get velocity as a cosine and position as a sine. The "
  "procedure never changes: integrate, evaluate the constant from "
  "the initial condition, and integrate again.",
 "visual": {"style": "time-dependent a", "transition": "fade"},
 "code": r'''
from manim import *


class Segment55(Scene):
    def construct(self):
        head = Text("LESSON 56 - TIME-DEPENDENT ACCELERATION", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"a=kt:\ v=u+\frac{kt^{2}}{2},\ x=x_0+ut+\frac{kt^{3}}{6}",
                     font_size=29, color=T.result_final)
        r2 = MathTex(r"a=A\sin\omega t:\ v=u+\frac{A}{\omega}(1-\cos\omega t)",
                     font_size=29, color=T.result_final)
        r3 = MathTex(r"x=x_0+ut+\frac{A}{\omega}\left(t-\frac{\sin\omega t}{\omega}\right)",
                     font_size=27, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.9)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.9)
        self.wait(3.2)
        self.wait(6)
''',
},
{
 "narration":
  "When acceleration depends on position, use the identity a equals v "
  "d v d x. This turns the equation into a separable form in v and "
  "x, useful for springs and gravity. For a spring, a equals minus "
  "omega squared x, and the identity integrates to v squared equals "
  "omega squared times the amplitude squared minus x squared, which "
  "is the SHM velocity relation. This identity is one of the most "
  "powerful tools in kinematics.",
 "visual": {"style": "position-dependent a", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment56(Scene):
    def construct(self):
        head = Text("LESSON 57 - POSITION-DEPENDENT ACCELERATION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"a=\frac{dv}{dt}=\frac{dv}{dx}\frac{dx}{dt}=v\frac{dv}{dx}",
                     font_size=30, color=T.result_final)
        r2 = MathTex(r"\int v\,dv=\int a(x)\,dx", font_size=31,
                     color=T.result_final)
        r3 = MathTex(r"a=-\omega^{2}x:\ v^{2}=\omega^{2}(A^{2}-x^{2})",
                     font_size=29, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.7)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.8)
        self.wait(3.0)
        self.wait(6)
''',
},
{
 "narration":
  "When acceleration depends on velocity, separate variables: d v "
  "over a of v equals d t, and integrate. For a drag force "
  "proportional to velocity, a equals minus k v, and integration "
  "gives velocity decaying exponentially: v equals v zero e to the "
  "minus k t. One more integration gives position approaching a "
  "terminal value. This is the standard model for motion through "
  "resisting media.",
 "visual": {"style": "velocity-dependent a", "transition": "fade"},
 "code": r'''
from manim import *


class Segment57(Scene):
    def construct(self):
        head = Text("LESSON 58 - VELOCITY-DEPENDENT ACCELERATION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"a=-kv:\ \int_{u}^{v}\frac{dv}{v}=-k\int_0^{t}dt",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"v=u\,e^{-kt}", font_size=32, color=T.result_final)
        r3 = MathTex(r"x=x_0+\frac{u}{k}(1-e^{-kt})", font_size=31,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.6)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=0.9)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.7)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(3.0)
        self.wait(6)
''',
},
{
 "narration":
  "Higher-order derivatives refine the description of motion. Jerk "
  "is the derivative of acceleration, snap the fourth derivative of "
  "position, and crackle and pop continue the sequence. Smooth "
  "trajectory planning, for example in robotics, keeps jerk small "
  "to avoid harsh starts. Piecewise acceleration is handled by "
  "splitting the time axis, and parametric motion by the chain rule "
  "d y d x equals y dot over x dot.",
 "visual": {"style": "higher order", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment58(Scene):
    def construct(self):
        head = Text("LESSON 59 - JERK, HIGHER ORDER, PIECEWISE",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"j=\frac{da}{dt}=\frac{d^{3}x}{dt^{3}}\ \text{(jerk)}",
                     font_size=30, color=T.result_final)
        r2 = MathTex(r"s=\frac{d^{4}x}{dt^{4}}\ \text{(snap)}", font_size=30,
                     color=T.result_intermediate)
        r3 = MathTex(r"\frac{dy}{dx}=\frac{\dot y}{\dot x}\ \text{(chain)}",
                     font_size=30, color=T.result_final)
        r4 = MathTex(r"\text{piecewise: integrate per interval, match conditions}",
                     font_size=27, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.7)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.5)
        self.wait(2.8)
        self.wait(6)
''',
},
]
