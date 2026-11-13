PART = [
{
 "narration":
  "Relative motion compares two observers. The relative position of "
  "B with respect to A is r B minus r A, and differentiating gives "
  "the relative velocity: v BA equals v B minus v A. The same "
  "relation holds for acceleration. This one vector equation "
  "solves most chasing, crossing, and intercepting problems. If you "
  "are in a train moving at thirty metres per second and another "
  "train passes at forty, its speed relative to you is ten metres "
  "per second.",
 "visual": {"style": "relative vectors", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment32(Scene):
    def construct(self):
        head = Text("LESSON 33 - RELATIVE POSITION, VELOCITY, ACCELERATION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\vec r_{B/A}=\vec r_B-\vec r_A", font_size=31,
                     color=T.text_primary)
        r2 = MathTex(r"\vec v_{B/A}=\vec v_B-\vec v_A", font_size=31,
                     color=T.result_final)
        r3 = MathTex(r"\vec a_{B/A}=\vec a_B-\vec a_A", font_size=31,
                     color=T.result_final)
        r4 = MathTex(r"\text{observer on A measures B's motion via these}",
                     font_size=27, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.6)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.5)
        self.wait(3.0)
        self.wait(6)
''',
},
{
 "narration":
  "In one dimension, relative velocity is signed subtraction: if A "
  "moves at plus four metres per second and B at plus two, then B's "
  "velocity relative to A is minus two. The classic river-boat "
  "problem gives the boat a velocity relative to the water and the "
  "water a velocity relative to the bank; the boat's velocity "
  "relative to the bank is the vector sum of the two. Perpendicular "
  "components combine by Pythagoras.",
 "visual": {"style": "river boat", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment33(Scene):
    def construct(self):
        head = Text("LESSON 34 - 1D RELATIVE MOTION, RIVER-BOAT",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"v_{B/A}=v_B-v_A\ \text{(signed)}", font_size=30,
                     color=T.result_final)
        r2 = MathTex(r"\vec v_{\text{boat/ground}}=\vec v_{\text{boat/water}}"
                     r"+\vec v_{\text{water/ground}}", font_size=29,
                     color=T.result_final)
        r3 = MathTex(r"\text{perpendicular: }|\vec v_{\text{boat/ground}}|^{2}"
                     r"=v_b^{2}+v_r^{2}", font_size=29,
                     color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.46)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.9)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r3), run_time=1.7)
        self.wait(3.0)
        self.wait(6)
''',
},
{
 "narration":
  "Rain and man: rain falls vertically with speed v r, and a man "
  "walks with speed v m. To the man, the rain appears to come at "
  "him with velocity v rain minus v man, so he must tilt his "
  "umbrella forward by the angle whose tangent is v man over v r. "
  "The direction of the apparent rain gives the angle. This is "
  "pure vector subtraction, with the vertical component unchanged.",
 "visual": {"style": "rain man", "transition": "fade"},
 "code": r'''
from manim import *


class Segment34(Scene):
    def construct(self):
        head = Text("LESSON 35 - RAIN-MAN PROBLEM", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\vec v_{\text{rain/man}}=\vec v_{\text{rain}}"
                     r"-\vec v_{\text{man}}", font_size=31,
                     color=T.result_final)
        r2 = MathTex(r"\tan\theta=\frac{v_{\text{man}}}{v_{\text{rain}}}",
                     font_size=31, color=T.result_final)
        r3 = MathTex(r"\text{umbrella tilts forward by }\theta",
                     font_size=28, color=T.result_intermediate)
        ax = Axes(x_range=[-1, 4, 1], y_range=[-3, 1, 1],
                  x_length=4.0, y_length=3.2,
                  axis_config={"color": T.grid, "stroke_width": 2})
        ax.move_to(DOWN * 2.0 + LEFT * 3.6)
        man = Dot(ax.c2p(1.6, 0), radius=0.12, color=T.result_final)
        vs = Arrow(man.get_center(), man.get_center() + RIGHT * 1.8, buff=0.1,
                   color=T.result_intermediate, stroke_width=4)
        vL = MathTex(r"v_m", font_size=26, color=T.result_intermediate).next_to(vs, DOWN, buff=0.1)
        rain = Arrow(man.get_center() + UP * 2.2, man.get_center(), buff=0.1,
                     color=T.text_secondary, stroke_width=4)
        rL = MathTex(r"v_r", font_size=26, color=T.text_secondary).next_to(rain, LEFT, buff=0.1)
        app = Arrow(man.get_center(), man.get_center() + DOWN * 2.0 + RIGHT * 1.5,
                    buff=0.1, color=T.cancel_mark, stroke_width=4)
        aL = MathTex(r"v_{\text{apparent}}", font_size=24, color=T.cancel_mark).next_to(app, DOWN, buff=0.12)
        th = MathTex(r"\theta", font_size=26, color=T.text_primary).move_to(man.get_center() + RIGHT * 0.6 + UP * 0.55)
        rows = VGroup(r1, r2, r3).arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 6.4)
        rows.next_to(ax, RIGHT, buff=0.5).align_to(ax, UP)
        if rows.height > 4.4:
            rows.scale_to_fit_height(4.4)
        self.play(Create(ax), run_time=1.0)
        self.play(FadeIn(man), run_time=0.6)
        self.play(Create(vs), Write(vL), Create(rain), Write(rL), run_time=1.3)
        self.play(Create(app), Write(aL), Write(th), run_time=1.2)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.6)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=0.9)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.5)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "Wind and aircraft: the plane's velocity relative to the air plus "
  "the wind's velocity relative to the ground gives the ground "
  "velocity. To fly due north, the pilot must point the nose into "
  "the wind by an angle satisfying the velocity triangle. This is "
  "the same vector addition as the river-boat problem, with the "
  "air playing the role of the water.",
 "visual": {"style": "wind aircraft", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment35(Scene):
    def construct(self):
        head = Text("LESSON 36 - WIND-AIRCRAFT PROBLEM", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\vec v_{\text{plane/ground}}=\vec v_{\text{plane/air}}"
                     r"+\vec v_{\text{air/ground}}", font_size=29,
                     color=T.result_final)
        r2 = MathTex(r"\text{head into wind: }\sin\theta=\frac{w}{v_p}",
                     font_size=30, color=T.result_final)
        r3 = MathTex(r"v_{\text{ground}}=\sqrt{v_p^{2}-w^{2}}",
                     font_size=30, color=T.result_intermediate)
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
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.7)
        self.wait(3.0)
        self.wait(6)
''',
},
{
 "narration":
  "A swimmer crossing a river has three classic optimizations. For "
  "minimum time, swim straight across at full speed; the current "
  "only carries you downstream. For minimum drift, aim upstream at "
  "the angle whose sine is the current speed over the swimmer "
  "speed, so the net velocity points straight across. For shortest "
  "path, you need exactly zero drift, which is possible only if the "
  "swimmer speed exceeds the current speed.",
 "visual": {"style": "swimmer crossing", "transition": "fade"},
 "code": r'''
from manim import *


class Segment36(Scene):
    def construct(self):
        head = Text("LESSON 37 - SWIMMER CROSSING: TIME, DRIFT, PATH",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"t_{\min}=\frac{w}{v_s}\ \text{(swim straight across)}",
                     font_size=30, color=T.result_final)
        r2 = MathTex(r"\text{minimum drift: }\sin\theta=\frac{v_r}{v_s}",
                     font_size=30, color=T.result_final)
        r3 = MathTex(r"\text{zero drift requires }v_s>v_r", font_size=30,
                     color=T.result_final)
        r4 = MathTex(r"\text{drift}=\frac{w}{v_s\cos\theta}\,v_r", font_size=29,
                     color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.7)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.7)
        self.wait(3.0)
        self.wait(6)
''',
},
{
 "narration":
  "Pursuit and interception are relative-motion problems. Two bodies "
  "meet when their relative displacement reaches zero, which fixes "
  "the time. The closest approach of two particles happens when "
  "their relative velocity is perpendicular to their relative "
  "position, and the minimum separation is the perpendicular "
  "distance from one trajectory to the other. These are solved by "
  "writing the separation vector as a function of time and "
  "minimizing its squared length.",
 "visual": {"style": "pursuit", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment37(Scene):
    def construct(self):
        head = Text("LESSON 38 - PURSUIT, CLOSEST APPROACH, SEPARATION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\vec r(t)=\vec r_0+\vec v_{\text{rel}}t", font_size=30,
                     color=T.text_primary)
        r2 = MathTex(r"\text{closest when }\vec r\cdot\vec v_{\text{rel}}=0",
                     font_size=29, color=T.result_final)
        r3 = MathTex(r"d_{\min}=\sqrt{|\vec r|^{2}-\frac{(\vec r\cdot\vec v)^2}{|\vec v|^{2}}}",
                     font_size=28, color=T.result_final)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.46)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.7)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.9)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.4)
        self.wait(6)
''',
},
]
