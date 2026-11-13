PART = [
{
 "narration":
  "Rectilinear motion is motion along a straight line, the simplest "
  "kinematics. One coordinate suffices: x of t. Uniform motion means "
  "constant velocity: equal displacements in equal times, so the "
  "position-time graph is a straight line and x equals x zero plus v "
  "t. Non-uniform motion changes velocity, and uniformly accelerated "
  "motion adds a constant acceleration. The graph becomes a parabola "
  "in position-time and a straight line in velocity-time.",
 "visual": {"style": "linear motion", "transition": "fade"},
 "code": r'''
from manim import *


class Segment6(Scene):
    def construct(self):
        head = Text("LESSON 7 - RECTILINEAR MOTION, UNIFORM VS NON-UNIFORM",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{Uniform: }v=\text{const}\ \Rightarrow\ x=x_0+vt",
                     font_size=29, color=T.result_final)
        r2 = MathTex(r"\text{Uniformly accelerated: }a=\text{const}",
                     font_size=29, color=T.result_intermediate)
        r3 = MathTex(r"x=x_0+ut+\frac{1}{2}at^{2}", font_size=30,
                     color=T.result_final)
        ax = Axes(x_range=[-0.5, 6, 1], y_range=[-0.5, 5, 1],
                  x_length=5.2, y_length=3.0,
                  axis_config={"color": T.grid, "stroke_width": 2})
        ax.move_to(DOWN * 1.7 + LEFT * 3.0)
        ax.set_x_axis_label(Text("t", font_size=20, color=T.text_secondary))
        ax.set_y_axis_label(Text("x", font_size=20, color=T.text_secondary))
        line = ax.plot(lambda t: 0.6 * t, color=T.result_final, stroke_width=3)
        para = ax.plot(lambda t: 0.25 * t * t, color=T.result_intermediate, stroke_width=3)
        lL = Text("uniform", font_size=20, color=T.result_final).next_to(line.point_from_proportion(0.75), UR, buff=0.12)
        pL = Text("accelerated", font_size=20, color=T.result_intermediate).next_to(para.point_from_proportion(0.8), UR, buff=0.12)
        self.play(Create(ax), run_time=1.1)
        self.play(Create(line), Write(lL), run_time=1.3)
        self.play(Write(r1), run_time=1.4)
        self.wait(2.6)
        self.play(Create(para), Write(pL), run_time=1.4)
        self.play(Write(r2), run_time=1.3)
        self.play(Write(r3), run_time=1.5)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(3.2)
        self.wait(6)
''',
},
{
 "narration":
  "Average speed is total distance over total time; average velocity "
  "is total displacement over total time. The instantaneous velocity "
  "is the limit of the average as the interval shrinks to zero, "
  "which geometrically is the slope of the tangent to the position-"
  "time curve. On a curved position-time graph, the secant slope "
  "gives the average and the tangent slope gives the instantaneous "
  "value. Speed is the magnitude of the instantaneous velocity, so "
  "it never hurts to remember: distance is scalar, displacement is "
  "vector.",
 "visual": {"style": "average vs instantaneous", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment7(Scene):
    def construct(self):
        head = Text("LESSON 8 - AVERAGE AND INSTANTANEOUS SPEED/VELOCITY",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"v_{\text{avg}}=\frac{\Delta x}{\Delta t},\qquad "
                     r"v=\lim_{\Delta t\to0}\frac{\Delta x}{\Delta t}=\frac{dx}{dt}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"v_{\text{avg, speed}}=\frac{\text{distance}}{\text{time}}",
                     font_size=29, color=T.result_intermediate)
        ax = Axes(x_range=[-0.5, 6, 1], y_range=[-0.5, 5, 1],
                  x_length=5.4, y_length=3.2,
                  axis_config={"color": T.grid, "stroke_width": 2})
        ax.move_to(DOWN * 1.6 + LEFT * 3.4)
        ax.set_x_axis_label(Text("t", font_size=20, color=T.text_secondary))
        ax.set_y_axis_label(Text("x", font_size=20, color=T.text_secondary))
        curve = ax.plot(lambda t: 0.48 * t * t - 0.4 * t, color=T.result_final,
                        stroke_width=3)
        ta = 1.4
        tb = 3.8
        A = ax.c2p(ta, 0.48 * ta * ta - 0.4 * ta)
        B = ax.c2p(tb, 0.48 * tb * tb - 0.4 * tb)
        sec = Line(A, B, color=T.cancel_mark, stroke_width=2.5)
        tL = MathTex(r"v_{\text{avg}}=\text{slope of secant}", font_size=24,
                     color=T.cancel_mark).next_to(sec.get_center(), UP, buff=0.12)
        tc = 2.6
        C = ax.c2p(tc, 0.48 * tc * tc - 0.4 * tc)
        tang = Line(ax.c2p(1.2, 0.48 * tc * tc - 0.4 * tc - 1.8),
                    ax.c2p(4.6, 0.48 * tc * tc - 0.4 * tc + 2.6),
                    color=T.result_intermediate, stroke_width=3)
        tanL = MathTex(r"v=\text{slope of tangent}", font_size=24,
                       color=T.result_intermediate).next_to(tang, DOWN, buff=0.15)
        pdot = Dot(C, radius=0.06, color=T.result_intermediate)
        self.play(Create(ax), run_time=1.1)
        self.play(Create(curve), run_time=1.5)
        self.play(Create(sec), Write(tL), run_time=1.2)
        self.play(Write(r1), run_time=1.5)
        self.wait(3.0)
        self.play(FadeIn(pdot), Create(tang), Write(tanL), run_time=1.2)
        self.play(Write(r2), run_time=1.4)
        self.wait(3.2)
        self.wait(6)
''',
},
{
 "narration":
  "Acceleration measures how fast velocity changes. Average "
  "acceleration is the change in velocity divided by the time "
  "interval; instantaneous acceleration is its limit, the derivative "
  "of velocity with respect to time. Because velocity itself is the "
  "derivative of position, acceleration is the second derivative of "
  "position, x double dot. A body moving in a circle at constant "
  "speed has zero tangential acceleration but nonzero acceleration, "
  "because the direction keeps changing; acceleration is the rate of "
  "change of the velocity vector, not just its magnitude.",
 "visual": {"style": "acceleration", "transition": "fade"},
 "code": r'''
from manim import *


class Segment8(Scene):
    def construct(self):
        head = Text("LESSON 9 - AVERAGE AND INSTANTANEOUS ACCELERATION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"a_{\text{avg}}=\frac{\Delta v}{\Delta t},\qquad "
                     r"a=\lim_{\Delta t\to0}\frac{\Delta v}{\Delta t}=\frac{dv}{dt}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"a=\frac{d}{dt}\frac{dx}{dt}=\frac{d^{2}x}{dt^{2}}",
                     font_size=30, color=T.result_final)
        r3 = MathTex(r"\text{Uniform circular: }|v|=\text{const}\ \text{but}\ "
                     r"\vec a\neq0", font_size=29, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.46)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.48)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.7)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.8)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_intermediate)
        self.play(Create(box3), run_time=0.7)
        self.wait(3.4)
        self.wait(6)
''',
},
{
 "narration":
  "Now we derive the three equations of motion for constant "
  "acceleration, from the definitions themselves. Start from a "
  "equals d v d t. Separate and integrate from time zero to t: v "
  "equals u plus a t. Next use v equals d x d t: separate again and "
  "integrate, substituting the velocity law, so x equals x zero plus "
  "u t plus half a t squared. Third, eliminate time between the two: "
  "from the first equation t equals v minus u over a, substitute "
  "into the second, and rearrange to v squared equals u squared plus "
  "two a times x minus x zero. These three laws are the backbone of "
  "linear kinematics.",
 "visual": {"style": "derivation", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment9(Scene):
    def construct(self):
        head = Text("LESSON 10 - DERIVING THE EQUATIONS OF MOTION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"a=\frac{dv}{dt}\ \Rightarrow\ \int_u^{v}dv=a\int_0^{t}dt\ "
                     r"\Rightarrow\ v=u+at", font_size=28, color=T.text_primary)
        r2 = MathTex(r"v=\frac{dx}{dt}\ \Rightarrow\ x=x_0+\int_0^{t}(u+at)dt",
                     font_size=29, color=T.text_secondary)
        r3 = MathTex(r"x=x_0+ut+\frac{1}{2}at^{2}", font_size=31,
                     color=T.result_final)
        r4 = MathTex(r"t=\frac{v-u}{a}\ \Rightarrow\ v^{2}=u^{2}+2a(x-x_0)",
                     font_size=30, color=T.result_final)
        r5 = MathTex(r"\text{assumption: }a=\text{const}\ \text{during }[0,t]",
                     font_size=26, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.36)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.9)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.2)
        self.wait(3.0)
        self.wait(6)
''',
},
{
 "narration":
  "With constant acceleration, problems reduce to identifying u, v, "
  "a, s and t, then picking the law containing the wanted unknown. "
  "Stopping distance is the distance travelled from the moment "
  "braking begins: v equals zero, so u squared equals two a s, and "
  "s equals u squared over two a. Braking distance is that distance, "
  "while reaction distance is the distance covered during the "
  "driver's reaction time at the original speed, so the total "
  "stopping distance is u times t reaction plus u squared over two a. "
  "Doubling the speed quadruples the braking distance, a famous "
  "safety result.",
 "visual": {"style": "stopping", "transition": "fade"},
 "code": r'''
from manim import *


class Segment10(Scene):
    def construct(self):
        head = Text("LESSON 11 - STOPPING, BRAKING, REACTION DISTANCE",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"v^{2}-u^{2}=2(-a)s\ \Rightarrow\ "
                     r"s_{\text{brake}}=\frac{u^{2}}{2a}", font_size=29,
                     color=T.result_final)
        r2 = MathTex(r"s_{\text{reaction}}=u\,t_R\ \Rightarrow\ "
                     r"s_{\text{stop}}=ut_R+\frac{u^{2}}{2a}", font_size=29,
                     color=T.result_intermediate)
        r3 = MathTex(r"u\to2u\ \Rightarrow\ s_{\text{brake}}\to4s_{\text{brake}}",
                     font_size=29, color=T.result_final)
        r4 = MathTex(r"\text{assumption: }a=\text{constant braking deceleration}",
                     font_size=26, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.9)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.7)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.2)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "When acceleration varies with time, the basic definitions become "
  "integrals. If a of t is given, velocity is u plus the integral of "
  "a from zero to t, and position follows by one more integration. "
  "The boundary conditions, the initial position and initial "
  "velocity, set the integration constants. For example a equals k t "
  "gives v equals u plus k t squared over two, and x equals x zero "
  "plus u t plus k t cubed over six. Always write the limits "
  "carefully and carry the initial conditions.",
 "visual": {"style": "variable acceleration", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment11(Scene):
    def construct(self):
        head = Text("LESSON 12 - MOTION WITH VARIABLE ACCELERATION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"v(t)=u+\int_0^{t}a(t)\,dt,\qquad "
                     r"x(t)=x_0+\int_0^{t}v(t)\,dt", font_size=28,
                     color=T.text_primary)
        r2 = MathTex(r"a=kt:\ \ v=u+\frac{kt^{2}}{2},\ \ "
                     r"x=x_0+ut+\frac{kt^{3}}{6}", font_size=29,
                     color=T.result_final)
        r3 = MathTex(r"\text{initial conditions: }x(0)=x_0,\ v(0)=u",
                     font_size=29, color=T.result_intermediate)
        r4 = MathTex(r"\text{check }a=\frac{dv}{dt}=kt\ \checkmark",
                     font_size=29, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.9)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.6)
        self.wait(3.0)
        self.wait(6)
''',
},
{
 "narration":
  "Catch-up and overtaking problems are relative-motion algebra. "
  "Write the position of each body as a function of time from a "
  "common origin; meeting happens when the positions are equal. For "
  "a car chasing a truck, if the car starts behind with higher "
  "constant speed, the meeting condition yields a quadratic in time, "
  "whose solution gives the meeting time and distance. Overtaking "
  "adds the length of the overtaking vehicle and the overtaken one: "
  "the extra distance needed is the sum of the lengths.",
 "visual": {"style": "catch up", "transition": "fade"},
 "code": r'''
from manim import *


class Segment12(Scene):
    def construct(self):
        head = Text("LESSON 13 - CATCH-UP, OVERTAKING, MEETING",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"x_T(t)=d+v_T t,\qquad x_C(t)=v_C t", font_size=29,
                     color=T.text_primary)
        r2 = MathTex(r"\text{meet: }x_T=x_C\ \Rightarrow\ t=\frac{d}{v_C-v_T}",
                     font_size=29, color=T.result_final)
        r3 = MathTex(r"\text{ovetaking extra distance }=L_1+L_2", font_size=29,
                     color=T.result_intermediate)
        r4 = MathTex(r"\text{require }v_C>v_T\ \text{for catch-up}", font_size=29,
                     color=T.text_secondary)
        ax = Axes(x_range=[-0.5, 6, 1], y_range=[-0.5, 5, 1],
                  x_length=5.4, y_length=3.0,
                  axis_config={"color": T.grid, "stroke_width": 2})
        ax.move_to(DOWN * 1.7 + LEFT * 3.3)
        ax.set_x_axis_label(Text("t", font_size=20, color=T.text_secondary))
        ax.set_y_axis_label(Text("x", font_size=20, color=T.text_secondary))
        lineT = ax.plot(lambda t: 0.7 + 0.45 * t, color=T.result_intermediate,
                        stroke_width=3)
        lineC = ax.plot(lambda t: 0.95 * t, color=T.result_final, stroke_width=3)
        m = ax.c2p(1.4, 1.33)
        mdot = Dot(m, radius=0.06, color=T.text_primary)
        mL = MathTex(r"\text{meet}", font_size=22, color=T.text_primary).next_to(mdot, UP, buff=0.1)
        tL = Text("truck", font_size=20, color=T.result_intermediate).next_to(lineT.point_from_proportion(0.8), UL, buff=0.1)
        cL = Text("car", font_size=20, color=T.result_final).next_to(lineC.point_from_proportion(0.8), UR, buff=0.1)
        rows = VGroup(r1, r2, r3, r4).arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        fit_width(rows, 6.0)
        rows.next_to(ax, RIGHT, buff=0.4).align_to(ax, UP)
        if rows.height > 4.6:
            rows.scale_to_fit_height(4.6)
        self.play(Create(ax), run_time=1.0)
        self.play(Create(lineT), Write(tL), run_time=1.2)
        self.play(Create(lineC), Write(cL), run_time=1.2)
        self.play(FadeIn(mdot), Write(mL), run_time=0.9)
        self.play(Write(r1), run_time=1.5)
        self.play(Write(r2), run_time=1.6)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.5)
        self.play(Write(r4), run_time=1.4)
        self.wait(3.2)
        self.wait(6)
''',
},
{
 "narration":
  "Signs carry meaning in one-dimensional motion. Choosing a "
  "positive direction, a positive velocity moves that way and a "
  "negative velocity moves back. Negative acceleration does not "
  "always mean slowing down: if velocity is already negative, a "
  "negative acceleration speeds the object up. Motion with changing "
  "direction happens when velocity crosses zero. Retardation is "
  "acceleration opposite to the velocity vector. So sketch the axis, "
  "choose positive, then write every quantity with its correct sign.",
 "visual": {"style": "signs", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment13(Scene):
    def construct(self):
        head = Text("LESSON 14 - SIGNS, NEGATIVE ACCELERATION, DIRECTION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{choose }+\ \text{right: }v>0\ \text{right, }v<0\ \text{left}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"\text{slowing: }a\ \text{opposes }v;\ \ "
                     r"\text{retardation if }a\cdot v<0", font_size=28,
                     color=T.result_intermediate)
        r3 = MathTex(r"\text{changing direction: }v\ \text{passes through zero}",
                     font_size=28, color=T.result_final)
        r4 = MathTex(r"v=-5\ \text{m/s},\ a=-2\ \text{m/s}^{2}:\ \ "
                     r"\text{speeds up leftward}", font_size=28,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.8)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.4)
        self.wait(6)
''',
},
]
