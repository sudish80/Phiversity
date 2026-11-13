PART = [
{
 "narration":
  "The position-time graph is the master graph of one-dimensional "
  "motion. Its slope at any instant is the instantaneous velocity. "
  "A horizontal line means rest; a straight, tilted line means "
  "uniform velocity; curvature means acceleration, with the curve "
  "bending upward when velocity grows. A displacement-time graph is "
  "the same plot. The distance-time graph, by contrast, never goes "
  "down, because distance accumulates; it records the path length "
  "travelled.",
 "visual": {"style": "x-t graph", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment14(Scene):
    def construct(self):
        head = Text("LESSON 15 - POSITION-TIME AND DISTANCE-TIME GRAPHS",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        ax = Axes(x_range=[-0.5, 6, 1], y_range=[-0.5, 5, 1],
                  x_length=5.6, y_length=3.2,
                  axis_config={"color": T.grid, "stroke_width": 2})
        ax.move_to(DOWN * 1.5 + LEFT * 3.6)
        ax.set_x_axis_label(Text("t", font_size=20, color=T.text_secondary))
        ax.set_y_axis_label(Text("x", font_size=20, color=T.text_secondary))
        rest = ax.plot(lambda t: 3.4, color=T.text_secondary, stroke_width=3)
        uni = ax.plot(lambda t: 0.35 + 0.8 * t, color=T.result_final, stroke_width=3)
        acc = ax.plot(lambda t: 0.3 + 0.25 * t * t, color=T.result_intermediate, stroke_width=3)
        rL = Text("rest", font_size=20, color=T.text_secondary).next_to(rest.point_from_proportion(0.5), UR, buff=0.12)
        uL = Text("uniform v", font_size=20, color=T.result_final).next_to(uni.point_from_proportion(0.7), UR, buff=0.12)
        aL = Text("accelerating", font_size=20, color=T.result_intermediate).next_to(acc.point_from_proportion(0.85), UR, buff=0.12)
        r1 = MathTex(r"\text{slope}=\frac{dx}{dt}=v(t)", font_size=29,
                     color=T.result_final)
        r2 = MathTex(r"\text{horizontal line } \Rightarrow v=0\ \text{(rest)}",
                     font_size=28, color=T.text_secondary)
        r3 = MathTex(r"\text{straight line } \Rightarrow v=\text{const}",
                     font_size=28, color=T.text_secondary)
        r4 = MathTex(r"\text{curve } \Rightarrow a\neq0", font_size=28,
                     color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        fit_width(rows, 6.0)
        rows.next_to(ax, RIGHT, buff=0.4).align_to(ax, UP)
        if rows.height > 4.6:
            rows.scale_to_fit_height(4.6)
        self.play(Create(ax), run_time=1.1)
        self.play(Create(rest), Write(rL), run_time=1.1)
        self.play(Create(uni), Write(uL), run_time=1.1)
        self.play(Create(acc), Write(aL), run_time=1.2)
        self.play(Write(r1), run_time=1.4)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.3)
        self.play(Write(r3), run_time=1.3)
        self.play(Write(r4), run_time=1.3)
        self.wait(3.2)
        self.wait(6)
''',
},
{
 "narration":
  "The velocity-time graph is the most useful. Its slope is the "
  "acceleration, and the area between the graph and the time axis "
  "is the displacement. For uniform acceleration, the graph is a "
  "straight line and the area is a trapezium, which reproduces s "
  "equals u t plus half a t squared. The speed-time graph has the "
  "same shape but its area is distance, always non-negative; if the "
  "velocity crosses zero, displacement area cancels but distance "
  "area adds.",
 "visual": {"style": "v-t graph", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment15(Scene):
    def construct(self):
        head = Text("LESSON 16 - VELOCITY-TIME GRAPH", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        ax = Axes(x_range=[-0.5, 6, 1], y_range=[-0.5, 5, 1],
                  x_length=5.6, y_length=3.2,
                  axis_config={"color": T.grid, "stroke_width": 2})
        ax.move_to(DOWN * 1.5 + LEFT * 3.6)
        ax.set_x_axis_label(Text("t", font_size=20, color=T.text_secondary))
        ax.set_y_axis_label(Text("v", font_size=20, color=T.text_secondary))
        vline = ax.plot(lambda t: 0.8 + 0.55 * t, color=T.result_final, stroke_width=3)
        fill = ax.get_area(vline, x_range=[0, 4], color=T.result_final, opacity=0.15)
        r1 = MathTex(r"\text{slope}=a(t)", font_size=29, color=T.result_final)
        r2 = MathTex(r"\text{area under curve}=\Delta x\ \text{(displacement)}",
                     font_size=28, color=T.result_intermediate)
        r3 = MathTex(r"\text{trapezium: }s=\frac{u+v}{2}t=ut+\frac{1}{2}at^{2}",
                     font_size=28, color=T.result_final)
        r4 = MathTex(r"\text{area below axis counts negative}",
                     font_size=27, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        fit_width(rows, 6.0)
        rows.next_to(ax, RIGHT, buff=0.4).align_to(ax, UP)
        if rows.height > 4.6:
            rows.scale_to_fit_height(4.6)
        self.play(Create(ax), run_time=1.1)
        self.play(Create(vline), run_time=1.3)
        self.play(FadeIn(fill), run_time=1.0)
        self.play(Write(r1), run_time=1.3)
        self.wait(2.4)
        self.play(Write(r2), run_time=1.5)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.4)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "The acceleration-time graph completes the trio. Its slope is "
  "jerk, the rate of change of acceleration. The area under the "
  "acceleration-time curve is the change in velocity, from the "
  "definition of acceleration integrated over time. A constant "
  "positive acceleration produces a horizontal line; a linearly "
  "growing acceleration gives a tilted line whose triangular area "
  "computes the velocity change.",
 "visual": {"style": "a-t graph", "transition": "fade"},
 "code": r'''
from manim import *


class Segment16(Scene):
    def construct(self):
        head = Text("LESSON 17 - ACCELERATION-TIME GRAPH", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        ax = Axes(x_range=[-0.5, 6, 1], y_range=[-0.5, 4, 1],
                  x_length=5.6, y_length=3.0,
                  axis_config={"color": T.grid, "stroke_width": 2})
        ax.move_to(DOWN * 1.5 + LEFT * 3.6)
        ax.set_x_axis_label(Text("t", font_size=20, color=T.text_secondary))
        ax.set_y_axis_label(Text("a", font_size=20, color=T.text_secondary))
        aline = ax.plot(lambda t: 1.0 + 0.45 * t, color=T.result_final, stroke_width=3)
        fill = ax.get_area(aline, x_range=[0, 3], color=T.result_final, opacity=0.15)
        r1 = MathTex(r"\text{area under curve}=\Delta v", font_size=29,
                     color=T.result_final)
        r2 = MathTex(r"\Delta v=\int_{t_1}^{t_2}a(t)\,dt", font_size=30,
                     color=T.result_intermediate)
        r3 = MathTex(r"\text{slope}=j=\frac{da}{dt}\ \text{(jerk)}",
                     font_size=29, color=T.text_secondary)
        rows = VGroup(r1, r2, r3).arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 6.0)
        rows.next_to(ax, RIGHT, buff=0.4).align_to(ax, UP)
        if rows.height > 4.6:
            rows.scale_to_fit_height(4.6)
        self.play(Create(ax), run_time=1.1)
        self.play(Create(aline), run_time=1.2)
        self.play(FadeIn(fill), run_time=1.0)
        self.play(Write(r1), run_time=1.4)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.5)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_intermediate)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.5)
        self.wait(3.0)
        self.wait(6)
''',
},
{
 "narration":
  "Real motion is often piecewise: the acceleration changes "
  "abruptly between stages. The graphs are then composed of "
  "segments, and we analyze each piece with its own law. To compare "
  "two particles, draw their graphs on the same axes: intersections "
  "of position graphs are meetings, equal slopes are equal "
  "velocities, and nested v-t areas give relative displacement. "
  "Comparing area under two v-t curves answers who is ahead and by "
  "how much.",
 "visual": {"style": "piecewise graphs", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment17(Scene):
    def construct(self):
        head = Text("LESSON 18 - PIECEWISE AND MULTI-PARTICLE GRAPHS",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{piecewise: split at }t_1,t_2,\ldots;\ \text{apply laws per piece}",
                     font_size=28, color=T.text_primary)
        r2 = MathTex(r"\text{intersection of }x-t:\ \text{meeting}",
                     font_size=29, color=T.result_final)
        r3 = MathTex(r"\text{equal slopes: equal velocities}", font_size=29,
                     color=T.result_intermediate)
        r4 = MathTex(r"\text{area between }v-t\ \text{curves: relative displacement}",
                     font_size=28, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.6)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.7)
        self.wait(3.0)
        self.wait(6)
''',
},
{
 "narration":
  "Graphical differentiation and integration reverse each other. "
  "Given a position curve, its tangent slope at every instant builds "
  "the velocity graph; doing that again builds the acceleration "
  "graph. Given an acceleration graph, the area builds velocity, and "
  "the area of that builds position. This is the entire graphical "
  "machinery: slopes go upward through derivatives, areas go "
  "downward through integrals, and both agree with the analytic "
  "definitions at every step.",
 "visual": {"style": "differentiation-integration", "transition": "fade"},
 "code": r'''
from manim import *


class Segment18(Scene):
    def construct(self):
        head = Text("LESSON 19 - GRAPHICAL DIFFERENTIATION AND INTEGRATION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"x(t)\to^{\text{slope}} v(t)\to^{\text{slope}} a(t)",
                     font_size=31, color=T.text_primary)
        r2 = MathTex(r"a(t)\to^{\text{area}} v(t)\to^{\text{area}} x(t)",
                     font_size=31, color=T.text_primary)
        r3 = MathTex(r"v=\frac{dx}{dt},\qquad a=\frac{dv}{dt}",
                     font_size=30, color=T.result_final)
        r4 = MathTex(r"v=\int a\,dt,\qquad x=\int v\,dt", font_size=30,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.6)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.wait(6)
''',
},
]
