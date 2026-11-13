PART = [
{
 "narration":
  "Near the Earth's surface, gravity gives every freely falling body "
  "the same downward acceleration g, about nine point eight metres "
  "per second squared. Free fall is motion under gravity alone, "
  "starting from rest, so velocity after time t is g t and distance "
  "fallen is half g t squared. The equations of motion apply with u "
  "equals zero and a equals g. We always choose the downward "
  "direction as positive in this situation, so that g enters with a "
  "positive sign.",
 "visual": {"style": "free fall", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment19(Scene):
    def construct(self):
        head = Text("LESSON 20 - ACCELERATION DUE TO GRAVITY, FREE FALL",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"g\approx9.8\ \text{m/s}^{2}\ \text{(downward)}",
                     font_size=30, color=T.result_final)
        r2 = MathTex(r"u=0:\ v=gt,\qquad h=\frac{1}{2}gt^{2},\qquad "
                     r"v^{2}=2gh", font_size=30, color=T.result_final)
        r3 = MathTex(r"\text{independent of mass: }a_{\text{free fall}}=g",
                     font_size=29, color=T.result_intermediate)
        r4 = MathTex(r"\text{air resistance neglected; }g\ \text{constant near surface}",
                     font_size=27, color=T.text_secondary)
        lines = VGroup()
        for i in range(6):
            y0 = 3.2 - 0.75 * i
            line = Line(LEFT * 0.9 + UP * y0, RIGHT * 0.9 + UP * y0,
                        color=T.graph_function, stroke_width=2.5)
            lines.add(line)
        dot = Dot(UP * 3.2, radius=0.12, color=T.result_final)
        arr = Arrow(dot.get_center(), dot.get_center() + DOWN * 2.6, buff=0.1,
                    color=T.result_final, stroke_width=4)
        gL = MathTex(r"g", font_size=28, color=T.result_final).next_to(arr, LEFT, buff=0.12)
        stack = VGroup(lines, dot, arr, gL).move_to(RIGHT * 4.6 + UP * 0.3)
        rows = VGroup(r1, r2, r3, r4).arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 8.2)
        rows.move_to(LEFT * 1.2 + UP * 0.3)
        self.play(Write(r1), run_time=1.5)
        self.wait(2.4)
        self.play(Write(r2), run_time=1.8)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(FadeIn(dot), Create(arr), Write(gL), run_time=1.1)
        self.play(Write(r3), run_time=1.5)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.4)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "A body thrown straight up with speed u decelerates at g. At the "
  "top the velocity is zero, so the time of ascent is u over g and "
  "the maximum height is u squared over two g. Because the motion is "
  "symmetric, the time of descent equals the time of ascent and the "
  "total time of flight is twice u over g. The return speed equals "
  "the launch speed. These results come straight from the equations "
  "with v equals zero at the top and the same displacement back to "
  "the ground.",
 "visual": {"style": "vertical projection", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment20(Scene):
    def construct(self):
        head = Text("LESSON 21 - VERTICAL PROJECTION UPWARD", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"v=u-gt,\qquad h=ut-\frac{1}{2}gt^{2}", font_size=29,
                     color=T.text_primary)
        r2 = MathTex(r"v=0\ \text{at top: }\ t_{\text{ascent}}=\frac{u}{g}",
                     font_size=29, color=T.result_intermediate)
        r3 = MathTex(r"H=u\frac{u}{g}-\frac{1}{2}g\frac{u^{2}}{g^{2}}"
                     r"=\frac{u^{2}}{2g}", font_size=29,
                     color=T.result_final)
        r4 = MathTex(r"t_{\text{descent}}=t_{\text{ascent}},\qquad "
                     r"T_{\text{flight}}=\frac{2u}{g}", font_size=29,
                     color=T.result_final)
        r5 = MathTex(r"\text{symmetry: return speed }=u", font_size=29,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.36)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.9)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.8)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r5), run_time=1.6)
        emphasize(self, r5, color=T.result_final, run_time=0.9)
        self.wait(3.0)
        self.wait(6)
''',
},
{
 "narration":
  "Motion from a tower adds an initial height. If a stone is dropped "
  "from a tower of height H, it hits the ground when the displacement "
  "equals H, so the time is root two H over g. Thrown downward with "
  "speed u, the equation H equals u t plus half g t squared decides "
  "the time. From a moving platform, the object's initial velocity "
  "is the platform's velocity: a balloon rising at V, dropping a "
  "stone, leaves the stone with initial velocity V upward, and the "
  "stone first rises before falling.",
 "visual": {"style": "tower motion", "transition": "fade"},
 "code": r'''
from manim import *


class Segment21(Scene):
    def construct(self):
        head = Text("LESSON 22 - MOTION FROM A TOWER AND MOVING PLATFORM",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{dropped from height }H:\ H=\frac{1}{2}gt^{2}\ "
                     r"\Rightarrow\ t=\sqrt{\frac{2H}{g}}", font_size=29,
                     color=T.result_final)
        r2 = MathTex(r"\text{thrown down: }H=ut+\frac{1}{2}gt^{2}",
                     font_size=29, color=T.result_intermediate)
        r3 = MathTex(r"\text{from moving platform: }u_{\text{object}}=v_{\text{platform}}",
                     font_size=29, color=T.result_final)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.46)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.7)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.wait(6)
''',
},
{
 "narration":
  "Two bodies in free fall move with the same acceleration g, so "
  "their relative acceleration is zero. That means their relative "
  "velocity stays constant. If a ball is dropped and a second ball "
  "is dropped one second later, the gap between them grows linearly: "
  "after t seconds the first has fallen half g t squared and the "
  "second half g times t minus one squared, so the separation is g "
  "times t minus half g, which widens forever. Relative motion under "
  "gravity is the cleanest application of relative acceleration.",
 "visual": {"style": "two body free fall", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment22(Scene):
    def construct(self):
        head = Text("LESSON 23 - TWO-BODY FREE FALL", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"a_{AB}=a_A-a_B=g-g=0", font_size=31,
                     color=T.result_final)
        r2 = MathTex(r"v_{AB}=\text{const}", font_size=31,
                     color=T.result_intermediate)
        r3 = MathTex(r"\text{dropped at }t=0\ \text{and }t=1s:", font_size=28,
                     color=T.text_primary)
        r4 = MathTex(r"s_1-s_2=\frac{1}{2}gt^{2}-\frac{1}{2}g(t-1)^{2}"
                     r"=gt-\frac{1}{2}g", font_size=28,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.4)
        self.wait(2.4)
        self.play(Write(r3), run_time=1.4)
        self.wait(2.4)
        self.play(Write(r4), run_time=1.9)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        self.wait(3.2)
        self.wait(6)
''',
},
{
 "narration":
  "Gravity changes with distance from a planet. On another planet "
  "with mass M and radius R, the surface value is G M over R "
  "squared, so all the free-fall formulas still hold, only with g "
  "replaced by that value. High above the surface, acceleration "
  "varies as one over r squared, and the motion is no longer "
  "uniformly accelerated: the equations of constant acceleration "
  "fail, and one must integrate. The falling time from a great "
  "height follows from energy or from solving the differential "
  "equation.",
 "visual": {"style": "variable gravity", "transition": "fade"},
 "code": r'''
from manim import *


class Segment23(Scene):
    def construct(self):
        head = Text("LESSON 24 - GRAVITY ON OTHER PLANETS, VARIABLE g",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"g_{\text{surface}}=\frac{GM}{R^{2}}\ \Rightarrow\ "
                     r"t_{\text{fall}}=\sqrt{\frac{2H}{g_{\text{surface}}}}",
                     font_size=29, color=T.result_final)
        r2 = MathTex(r"g(r)=\frac{GM}{r^{2}}\ \ \text{for }r>R",
                     font_size=30, color=T.result_intermediate)
        r3 = MathTex(r"\text{then }a=\text{const}\ \text{fails; integrate}",
                     font_size=28, color=T.text_secondary)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.46)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.7)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_intermediate)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.6)
        self.wait(3.0)
        self.wait(6)
''',
},
]
