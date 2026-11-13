PART = [
{
 "narration":
  "A projectile moves under gravity alone after launch. The key "
  "insight: the horizontal and vertical motions are independent. "
  "Horizontally there is no acceleration, so the horizontal velocity "
  "component stays constant; vertically, gravity acts alone, so the "
  "vertical component follows free-fall equations. The path that "
  "results is a parabola. We resolve the launch velocity into "
  "components and treat the two axes separately, joining them only "
  "through the common time.",
 "visual": {"style": "projectile intro", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment24(Scene):
    def construct(self):
        head = Text("LESSON 25 - PROJECTILE MOTION: INDEPENDENCE",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"a_x=0\ \Rightarrow\ v_x=u\cos\theta=\text{const}",
                     font_size=29, color=T.result_final)
        r2 = MathTex(r"a_y=-g\ \Rightarrow\ v_y=u\sin\theta-gt",
                     font_size=29, color=T.result_final)
        r3 = MathTex(r"x=u\cos\theta\,t,\qquad y=u\sin\theta\,t-\frac{1}{2}gt^{2}",
                     font_size=29, color=T.result_final)
        ax = Axes(x_range=[-0.5, 6, 1], y_range=[-0.5, 4, 1],
                  x_length=5.4, y_length=3.2,
                  axis_config={"color": T.grid, "stroke_width": 2})
        ax.move_to(DOWN * 1.4 + LEFT * 3.5)
        ax.set_x_axis_label(Text("x", font_size=20, color=T.text_secondary))
        ax.set_y_axis_label(Text("y", font_size=20, color=T.text_secondary))
        proj = ax.plot(lambda t: -0.4 * t * (t - 5.2), color=T.result_final,
                       stroke_width=3)
        p0 = ax.c2p(0, 0)
        u0 = 0.9
        v0 = 2.6
        arr = Arrow(p0, p0 + RIGHT * u0 + UP * v0, buff=0, color=T.result_intermediate,
                    stroke_width=3.5)
        uL = MathTex(r"\vec u", font_size=26, color=T.result_intermediate).next_to(p0 + RIGHT * u0 + UP * v0, UR, buff=0.08)
        th = MathTex(r"\theta", font_size=24, color=T.text_primary).move_to(p0 + RIGHT * 0.7 + UP * 0.5)
        rows = VGroup(r1, r2, r3).arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        fit_width(rows, 5.6)
        rows.next_to(ax, RIGHT, buff=0.4).align_to(ax, UP)
        if rows.height > 4.2:
            rows.scale_to_fit_height(4.2)
        self.play(Create(ax), run_time=1.1)
        self.play(Create(proj), run_time=1.5)
        self.play(Create(arr), Write(uL), Write(th), run_time=1.1)
        self.play(Write(r1), run_time=1.5)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.5)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.7)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(3.2)
        self.wait(6)
''',
},
{
 "narration":
  "Derive the trajectory. From x equals u cos theta t, solve for t "
  "and substitute into the vertical law. After simplifying, y "
  "equals x tan theta minus g x squared over two u squared cos "
  "squared theta. This is a quadratic in x, so the path is a "
  "parabola opening downward. The three terms have clean meanings: "
  "the linear term sets the initial slope, and the quadratic term "
  "bends the path down under gravity.",
 "visual": {"style": "trajectory derivation", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment25(Scene):
    def construct(self):
        head = Text("LESSON 26 - EQUATION OF TRAJECTORY", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"t=\frac{x}{u\cos\theta}", font_size=30,
                     color=T.text_primary)
        r2 = MathTex(r"y=u\sin\theta\left(\frac{x}{u\cos\theta}\right)"
                     r"-\frac{1}{2}g\left(\frac{x}{u\cos\theta}\right)^{2}",
                     font_size=26, color=T.text_primary)
        r3 = MathTex(r"y=x\tan\theta-\frac{gx^{2}}{2u^{2}\cos^{2}\theta}",
                     font_size=30, color=T.result_final)
        r4 = MathTex(r"\text{quadratic in }x\ \Rightarrow\ \text{parabola}",
                     font_size=28, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r2), run_time=2.0)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.8)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r4), run_time=1.5)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "Time of flight comes from the vertical motion: the projectile "
  "returns to height zero, so set y equals zero in the vertical law. "
  "The nonzero solution gives T equals two u sine theta over g. "
  "Maximum height comes from the top where the vertical velocity is "
  "zero: H equals u squared sine squared theta over two g. Both "
  "depend on sine theta, so steep launches stay up longer and climb "
  "higher.",
 "visual": {"style": "T and H", "transition": "fade"},
 "code": r'''
from manim import *


class Segment26(Scene):
    def construct(self):
        head = Text("LESSON 27 - TIME OF FLIGHT AND MAXIMUM HEIGHT",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"y=0:\ 0=u\sin\theta\,T-\frac{1}{2}gT^{2}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"T=\frac{2u\sin\theta}{g}", font_size=31,
                     color=T.result_final)
        r3 = MathTex(r"v_y=0:\ H=u\sin\theta\frac{u\sin\theta}{g}"
                     r"-\frac{1}{2}g\left(\frac{u\sin\theta}{g}\right)^{2}",
                     font_size=25, color=T.text_primary)
        r4 = MathTex(r"H=\frac{u^{2}\sin^{2}\theta}{2g}", font_size=31,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.38)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.6)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=2.0)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.7)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.wait(6)
''',
},
{
 "narration":
  "The horizontal range is the landing distance, R equals the "
  "horizontal velocity times the flight time, which gives u squared "
  "sine two theta over g. Since sine two theta peaks at one, the "
  "maximum range happens at forty-five degrees and equals u squared "
  "over g. Two angles that add to ninety degrees give the same "
  "range, because sine two theta is the same for theta and ninety "
  "minus theta. The forty-five-degree launch is the champion for "
  "distance on flat ground.",
 "visual": {"style": "range", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment27(Scene):
    def construct(self):
        head = Text("LESSON 28 - RANGE, MAXIMUM RANGE, COMPLEMENTARY ANGLES",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"R=u\cos\theta\cdot\frac{2u\sin\theta}{g}"
                     r"=\frac{u^{2}\sin2\theta}{g}", font_size=30,
                     color=T.result_final)
        r2 = MathTex(r"R_{\max}=\frac{u^{2}}{g}\ \text{at }\theta=45^{\circ}",
                     font_size=30, color=T.result_final)
        r3 = MathTex(r"R(\theta)=R(90^{\circ}-\theta)", font_size=29,
                     color=T.result_intermediate)
        r4 = MathTex(r"\text{assumption: flat ground, no air resistance}",
                     font_size=26, color=T.text_secondary)
        ax = Axes(x_range=[-0.5, 6, 1], y_range=[-0.5, 3, 1],
                  x_length=5.4, y_length=2.8,
                  axis_config={"color": T.grid, "stroke_width": 2})
        ax.move_to(DOWN * 1.6 + LEFT * 3.3)
        ax.set_x_axis_label(Text("x", font_size=20, color=T.text_secondary))
        ax.set_y_axis_label(Text("y", font_size=20, color=T.text_secondary))
        p1 = ax.plot(lambda t: -0.38 * t * (t - 5.0), color=T.result_final, stroke_width=3)
        p2 = ax.plot(lambda t: -0.28 * t * (t - 5.0), color=T.result_intermediate, stroke_width=3)
        thA = Text("30 deg", font_size=18, color=T.result_intermediate).next_to(p2.point_from_proportion(0.55), UR, buff=0.1)
        thB = Text("60 deg", font_size=18, color=T.result_final).next_to(p1.point_from_proportion(0.6), UR, buff=0.1)
        rows = VGroup(r1, r2, r3, r4).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        fit_width(rows, 6.0)
        rows.next_to(ax, RIGHT, buff=0.4).align_to(ax, UP)
        if rows.height > 4.4:
            rows.scale_to_fit_height(4.4)
        self.play(Create(ax), run_time=1.0)
        self.play(Create(p1), Write(thB), run_time=1.3)
        self.play(Create(p2), Write(thA), run_time=1.3)
        self.play(Write(r1), run_time=1.6)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.6)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=0.9)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.5)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.4)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "At any point of the trajectory, the velocity is the vector sum of "
  "a constant horizontal component and a vertical component that "
  "changes linearly. Its magnitude is the square root of u squared "
  "cos squared theta plus the vertical component squared, and its "
  "direction is the arctangent of the ratio. The acceleration is "
  "constant throughout: straight down at g. This constancy is what "
  "makes the projectile analysis so clean.",
 "visual": {"style": "velocity at a point", "transition": "fade"},
 "code": r'''
from manim import *


class Segment28(Scene):
    def construct(self):
        head = Text("LESSON 29 - VELOCITY AND ACCELERATION AT ANY POINT",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"v_x=u\cos\theta,\qquad v_y=u\sin\theta-gt",
                     font_size=30, color=T.text_primary)
        r2 = MathTex(r"v=\sqrt{u^{2}\cos^{2}\theta+(u\sin\theta-gt)^{2}}",
                     font_size=30, color=T.result_final)
        r3 = MathTex(r"\tan\phi=\frac{u\sin\theta-gt}{u\cos\theta}",
                     font_size=30, color=T.result_intermediate)
        r4 = MathTex(r"a_x=0,\qquad a_y=-g\ \text{(constant everywhere)}",
                     font_size=30, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.38)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.8)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.8)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.4)
        self.wait(6)
''',
},
{
 "narration":
  "If the projectile starts from a height h, the landing condition "
  "is y equals minus h, and the flight time satisfies h equals u "
  "sine theta t plus half g t squared. Launching from an inclined "
  "plane changes the landing geometry: the projectile meets the "
  "plane when its coordinates satisfy the plane's equation, y "
  "equals minus x tan alpha if the plane slopes down at alpha. The "
  "range along the plane follows by substituting the path into the "
  "line equation and solving.",
 "visual": {"style": "elevated and inclined", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment29(Scene):
    def construct(self):
        head = Text("LESSON 30 - FROM A HEIGHT AND ON AN INCLINED PLANE",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{from height }h:\ -h=u\sin\theta\,t-\frac{1}{2}gt^{2}",
                     font_size=29, color=T.result_final)
        r2 = MathTex(r"\text{plane }y=-x\tan\alpha:\ \text{range along plane}",
                     font_size=29, color=T.result_intermediate)
        r3 = MathTex(r"R_{\text{plane}}=\frac{2u^{2}\sin(\theta+\alpha)\cos\theta}"
                     r"{g\cos^{2}\alpha}", font_size=28,
                     color=T.result_final)
        r4 = MathTex(r"\text{check: }\alpha=0\ \text{recovers }R=\frac{u^{2}\sin2\theta}{g}",
                     font_size=27, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.38)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.9)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.8)
        emphasize(self, r4, color=T.text_secondary, run_time=0.9)
        self.wait(3.2)
        self.wait(6)
''',
},
{
 "narration":
  "For a moving target, the projectile must intercept a body whose "
  "position changes with time; equate the two position vectors and "
  "solve for the launch parameters. From a moving platform, add the "
  "platform velocity to the launch velocity at the instant of "
  "release. The envelope of all trajectories from a point at fixed "
  "speed is the parabola y equals u squared over two g minus g x "
  "squared over two u squared: points above the envelope cannot be "
  "reached with that speed at any angle.",
 "visual": {"style": "target and envelope", "transition": "fade"},
 "code": r'''
from manim import *


class Segment30(Scene):
    def construct(self):
        head = Text("LESSON 31 - MOVING TARGETS AND THE ENVELOPE",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{target: }\vec r_T(t)=\vec r_{T0}+\vec v_T t",
                     font_size=28, color=T.text_primary)
        r2 = MathTex(r"\text{intercept: }\vec r_P(t)=\vec r_T(t)",
                     font_size=28, color=T.result_intermediate)
        r3 = MathTex(r"\text{envelope: }y=\frac{u^{2}}{2g}-\frac{gx^{2}}{2u^{2}}",
                     font_size=29, color=T.result_final)
        r4 = MathTex(r"\text{above envelope: unreachable at speed }u",
                     font_size=28, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.8)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r4), run_time=1.5)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "Minimum speed to reach a given point is found from the trajectory "
  "equation solved as a quadratic in u squared; the point is "
  "reachable only when the discriminant is non-negative, which "
  "selects the minimum launch speed. Successive projectiles from the "
  "same point are handled by writing each with its own launch time "
  "and imposing the meeting condition. These are textbook "
  "optimization problems built on the same parabola.",
 "visual": {"style": "minimum speed", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment31(Scene):
    def construct(self):
        head = Text("LESSON 32 - MINIMUM SPEED, SUCCESSIVE PROJECTILES",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"y=x\tan\theta-\frac{gx^{2}}{2u^{2}\cos^{2}\theta}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"\text{quadratic in }u^{2}:\ \Delta\geq0\ \text{for reachability}",
                     font_size=28, color=T.result_intermediate)
        r3 = MathTex(r"u_{\min}^{2}=g(y+\sqrt{x^{2}+y^{2}})", font_size=30,
                     color=T.result_final)
        r4 = MathTex(r"\text{successive: }x_P(t)=x_T(t+t_0)", font_size=29,
                     color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.7)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.6)
        self.wait(2.8)
        self.wait(6)
''',
},
]
