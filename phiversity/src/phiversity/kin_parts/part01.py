PART = [
{
 "narration":
  "Welcome to the complete kinematics chapter. Mechanics is the study "
  "of motion and the forces behind it. Kinematics is the part that "
  "describes motion without asking what causes it: position, velocity, "
  "acceleration, and time. Dynamics, which comes later, adds force. A "
  "body is at rest when its position does not change with time, in "
  "motion when it does. Importantly, rest and motion are always "
  "relative to some observer. The same ball can be at rest for a "
  "passenger but in motion for a person standing on the platform.",
 "visual": {"style": "lesson intro", "transition": "fade"},
 "code": r'''
from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("LESSON 1 - MECHANICS, KINEMATICS, REST AND MOTION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{Mechanics}=\text{Kinematics}+\text{Dynamics}",
                     font_size=31, color=T.text_primary)
        r2 = MathTex(r"\text{Kinematics: describe motion - }x(t),\ v(t),\ a(t)",
                     font_size=28, color=T.result_intermediate)
        r3 = MathTex(r"\text{Dynamics: why motion happens - }F=ma",
                     font_size=29, color=T.text_primary)
        r4 = MathTex(r"\text{Rest: }\Delta\vec r=0\ \text{in the chosen frame}",
                     font_size=29, color=T.text_secondary)
        r5 = MathTex(r"\text{Motion: }\Delta\vec r\neq0\ \text{in the chosen frame}",
                     font_size=29, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r5), run_time=1.6)
        self.wait(2.8)
        self.play(FadeOut(VGroup(rows)), run_time=0.5)
        ask = MathTex(r"\text{Key idea: there is no absolute rest.}",
                      font_size=36, color=T.result_final)
        ask.move_to(UP * 0.4)
        self.play(Write(ask), run_time=1.5)
        box = SurroundingRectangle(ask, buff=0.2, color=T.result_final)
        self.play(Create(box), run_time=0.7)
        emphasize(self, ask, color=T.result_final, run_time=1.0)
        self.wait(4.5)
        self.wait(6)
''',
},
{
 "narration":
  "A reference frame is a coordinate system and a clock that an "
  "observer uses to label events. Inertial frames are frames moving "
  "with constant velocity, where Newton's first law holds: an object "
  "with no net force keeps its state of motion. Non-inertial frames "
  "accelerate, and inside them fictitious forces appear. A car "
  "suddenly braking is non-inertial; a passenger feels thrown forward "
  "even though no real force acts on him. For kinematics, any frame "
  "gives valid positions and velocities, but acceleration "
  "measurements take their simplest meaning in inertial frames.",
 "visual": {"style": "frames", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("LESSON 2 - REFERENCE FRAMES, INERTIAL VS NON-INERTIAL",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{Frame = axes + clock}",
                     font_size=30, color=T.text_primary)
        r2 = MathTex(r"\text{Inertial: }\vec v_{\text{frame}}=\text{const}\ \Rightarrow\ "
                     r"\text{Newton's 1st law holds}", font_size=27,
                     color=T.result_final)
        r3 = MathTex(r"\text{Non-inertial: }\vec a_{\text{frame}}\neq0\ \Rightarrow\ "
                     r"\text{fictitious force }-m\vec a_{\text{frame}}",
                     font_size=27, color=T.result_intermediate)
        r4 = MathTex(r"\text{Rotation: centrifugal }m\omega^{2}r\ \text{and Coriolis }"
                     r"2m\vec\omega\times\vec v", font_size=27,
                     color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.5)
        self.wait(2.4)
        self.play(Write(r2), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.9)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.9)
        self.wait(3.0)
        self.play(FadeOut(VGroup(rows)), run_time=0.5)
        car = Polygon([-1.6, -0.6, 0], [1.6, -0.6, 0], [1.6, 0.2, 0],
                      [0.5, 0.6, 0], [-1.2, 0.6, 0], [-1.6, 0.2, 0],
                      stroke_color=T.graph_function, stroke_width=3)
        car.set_fill(T.graph_function, opacity=0.12)
        car.move_to(DOWN * 1.6)
        w1 = Circle(radius=0.3, stroke_color=T.text_primary, stroke_width=2).move_to(car.get_center() + LEFT * 0.9 + DOWN * 0.65)
        w2 = w1.copy().move_to(car.get_center() + RIGHT * 0.9 + DOWN * 0.65)
        arr = Arrow(car.get_center() + LEFT * 2.4, car.get_center() + LEFT * 0.7,
                    buff=0, color=T.cancel_mark, stroke_width=4)
        lab = Text("braking: non-inertial", font_size=22,
                   color=T.cancel_mark).next_to(car, UP, buff=0.15)
        pax = Text("passenger 'thrown forward'", font_size=20,
                   color=T.text_secondary).next_to(car, DOWN, buff=0.6)
        scene = VGroup(car, w1, w2, arr, lab, pax)
        self.play(Create(car), Create(w1), Create(w2), run_time=1.4)
        self.play(Create(arr), FadeIn(lab), FadeIn(pax), run_time=1.2)
        self.wait(4.0)
        self.wait(6)
''',
},
{
 "narration":
  "Coordinate systems are the grids on which we read motion. In "
  "Cartesian coordinates we use x, y, z with perpendicular axes: "
  "perfect for straight-line and rectangular motion. Polar "
  "coordinates place a point by radius r and angle theta: most "
  "natural for circular motion; the unit vectors r hat and theta hat "
  "rotate as the point moves. Cylindrical coordinates add a z-axis "
  "to polar, and spherical coordinates use two angles plus a radius. "
  "Choosing the right system is the first victory in any problem: "
  "rectilinear problems in Cartesian, circular in polar.",
 "visual": {"style": "coordinate systems", "transition": "fade"},
 "code": r'''
from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("LESSON 3 - COORDINATE SYSTEMS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        ax = Axes(x_range=[-0.5, 4, 1], y_range=[-0.5, 3, 1],
                  x_length=3.6, y_length=2.7,
                  axis_config={"color": T.grid, "stroke_width": 2})
        ax.move_to(DOWN * 1.4 + LEFT * 4.2)
        P = ax.c2p(2.4, 1.8)
        pdot = Dot(P, radius=0.06, color=T.result_final)
        pL = MathTex(r"P(x,y)", font_size=22, color=T.result_final).next_to(P, UR, buff=0.12)
        rx = DashedLine(ax.c2p(0, 0), (P[0], 0, 0), color=T.cancel_mark, stroke_width=2)
        ry = DashedLine(ax.c2p(0, 0), (0, P[1], 0), color=T.cancel_mark, stroke_width=2)
        xL = MathTex(r"x", font_size=22, color=T.cancel_mark).move_to(ax.c2p(1.2, -0.35))
        yL = MathTex(r"y", font_size=22, color=T.cancel_mark).move_to(ax.c2p(-0.4, 0.9))
        r1 = MathTex(r"\text{Cartesian: }P=(x,y,z)", font_size=27,
                     color=T.text_primary)
        ax2 = Axes(x_range=[-0.5, 4, 1], y_range=[-0.5, 3, 1],
                   x_length=3.6, y_length=2.7,
                   axis_config={"color": T.grid, "stroke_width": 2})
        ax2.move_to(DOWN * 1.4 + RIGHT * 4.2)
        P2 = ax2.c2p(2.5, 1.5)
        rad = Arrow(ax2.c2p(0, 0), P2, buff=0, color=T.result_final, stroke_width=3.5)
        p2dot = Dot(P2, radius=0.06, color=T.result_final)
        rL = MathTex(r"r", font_size=24, color=T.result_final).next_to((P2 + ax2.c2p(0, 0)) / 2, UP, buff=0.08)
        th = MathTex(r"\theta", font_size=24, color=T.text_primary).move_to(ax2.c2p(0.65, 0.55))
        p2L = MathTex(r"P(r,\theta)", font_size=22, color=T.result_final).next_to(P2, UR, buff=0.12)
        r2 = MathTex(r"\text{Polar: }P=(r,\theta),\ \hat r,\ \hat\theta",
                     font_size=27, color=T.text_primary)
        r3 = MathTex(r"\text{Cylindrical: }P=(r,\theta,z)", font_size=27,
                     color=T.text_secondary)
        r4 = MathTex(r"\text{Spherical: }P=(R,\theta,\phi)", font_size=27,
                     color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4).arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        fit_width(rows, 12.4)
        rows.move_to(UP * 2.4)
        self.play(Create(ax), run_time=1.0)
        self.play(Create(rx), Create(ry), FadeIn(pdot), Write(pL), Write(xL), Write(yL), run_time=1.4)
        self.play(Write(r1), run_time=1.4)
        self.wait(2.6)
        self.play(Create(ax2), run_time=1.0)
        self.play(Create(rad), FadeIn(p2dot), Write(rL), Write(th), Write(p2L), run_time=1.4)
        self.play(Write(r2), run_time=1.4)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.3)
        self.play(Write(r4), run_time=1.3)
        self.wait(3.4)
        self.wait(6)
''',
},
{
 "narration":
  "Scalars have only magnitude: time, distance, speed, mass. Vectors "
  "have magnitude and direction: displacement, velocity, "
  "acceleration. The position vector r of a point points from the "
  "origin to the point. Path length is the total distance actually "
  "travelled along the path; displacement is the straight-line "
  "vector from the initial to the final position. A runner who "
  "completes a lap of a circular track has path length two pi R but "
  "displacement zero, because the start and end match.",
 "visual": {"style": "vectors", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("LESSON 4 - SCALARS, VECTORS, DISTANCE, DISPLACEMENT",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{Scalar: magnitude only - }t,\ d,\ s", font_size=28,
                     color=T.text_primary)
        r2 = MathTex(r"\text{Vector: magnitude + direction - }\vec r,\ \vec v,\ \vec a",
                     font_size=28, color=T.text_primary)
        r3 = MathTex(r"\text{Path length: total distance along the path}",
                     font_size=28, color=T.result_intermediate)
        r4 = MathTex(r"\text{Displacement: }\Delta\vec r=\vec r_2-\vec r_1",
                     font_size=30, color=T.result_final)
        O = DOWN * 1.9 + LEFT * 4.4
        P1 = O + RIGHT * 2.2 + UP * 0.9
        P2 = O + RIGHT * 4.6 + UP * 2.2
        r1v = Arrow(O, P1, buff=0, color=T.text_secondary, stroke_width=3)
        r2v = Arrow(O, P2, buff=0, color=T.text_secondary, stroke_width=3)
        dr = Arrow(P1, P2, buff=0, color=T.result_final, stroke_width=4)
        r1L = MathTex(r"\vec r_1", font_size=24, color=T.text_secondary).next_to(P1, DL, buff=0.1)
        r2L = MathTex(r"\vec r_2", font_size=24, color=T.text_secondary).next_to(P2, UR, buff=0.1)
        drL = MathTex(r"\Delta\vec r", font_size=24, color=T.result_final).next_to((P1 + P2) / 2, UP, buff=0.1)
        path = VMobject(stroke_color=T.cancel_mark, stroke_width=3)
        path.set_points_smoothly([O + RIGHT * 0.3, O + RIGHT * 1.4 + UP * 0.8,
                                  P1, O + RIGHT * 3.0 + UP * 0.4, P2])
        pL = MathTex(r"\text{path length}", font_size=22, color=T.cancel_mark).next_to(path, DOWN, buff=0.15)
        fig = VGroup(r1v, r2v, dr, r1L, r2L, drL, path, pL)
        rows = VGroup(r1, r2, r3, r4).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 6.2)
        rows.next_to(O, RIGHT, buff=2.6).align_to(O, UP)
        if rows.height > 4.6:
            rows.scale_to_fit_height(4.6)
        self.play(Write(r1), run_time=1.5)
        self.wait(2.4)
        self.play(Write(r2), run_time=1.5)
        self.wait(2.4)
        self.play(Create(path), Write(pL), run_time=1.3)
        self.play(Create(r1v), Create(r2v), Write(r1L), Write(r2L), run_time=1.2)
        self.play(Write(r3), run_time=1.5)
        self.wait(2.6)
        self.play(Create(dr), Write(drL), run_time=1.1)
        self.play(Write(r4), run_time=1.5)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.4)
        self.wait(6)
''',
},
{
 "narration":
  "Speed is distance per time, a scalar. Velocity is displacement "
  "per time, a vector, so it carries direction and can be negative "
  "along a chosen axis. Acceleration is the rate of change of "
  "velocity, and retardation is just acceleration opposing the "
  "velocity, which we call deceleration in one dimension. The "
  "distinction will drive every graph later: distance adds, "
  "displacement adds with signs, and a body can have zero "
  "displacement yet nonzero path length.",
 "visual": {"style": "definitions", "transition": "fade"},
 "code": r'''
from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("LESSON 5 - SPEED, VELOCITY, ACCELERATION, RETARDATION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{speed}=\frac{\text{distance}}{\text{time}},\qquad "
                     r"\text{velocity}=\frac{\Delta\vec r}{\Delta t}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"\vec v=\lim_{\Delta t\to0}\frac{\Delta\vec r}{\Delta t}"
                     r"=\frac{d\vec r}{dt}", font_size=29,
                     color=T.result_intermediate)
        r3 = MathTex(r"\vec a=\lim_{\Delta t\to0}\frac{\Delta\vec v}{\Delta t}"
                     r"=\frac{d\vec v}{dt}", font_size=29,
                     color=T.result_intermediate)
        r4 = MathTex(r"\text{Retardation: }\vec a\cdot\vec v<0",
                     font_size=29, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.7)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.4)
        self.wait(6)
''',
},
{
 "narration":
  "Dimensions are the powers of mass, length and time in a physical "
  "quantity, written M L T. Position has dimension L, velocity L T "
  "minus one, acceleration L T minus two. A dimensionally "
  "homogeneous equation has the same dimensions on both sides; this "
  "is the fastest check on any derived formula. Units make dimensions "
  "concrete: metres, seconds, kilometres per hour. Always convert "
  "before using an equation, because every formula assumes one "
  "consistent unit system.",
 "visual": {"style": "dimensions", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment5(Scene):
    def construct(self):
        head = Text("LESSON 6 - DIMENSIONS AND UNITS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"[x]=L,\qquad [v]=LT^{-1},\qquad [a]=LT^{-2}",
                     font_size=30, color=T.text_primary)
        r2 = MathTex(r"[v^{2}]=L^{2}T^{-2},\qquad [2as]=L\cdot LT^{-2}=L^{2}T^{-2}",
                     font_size=29, color=T.result_intermediate)
        r3 = MathTex(r"v^{2}=u^{2}+2as:\ \ \text{both sides }L^{2}T^{-2}\ \checkmark",
                     font_size=29, color=T.result_final)
        r4 = MathTex(r"\text{SI base units: m, kg, s, A, K, mol, cd}",
                     font_size=28, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.8)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r4), run_time=1.6)
        self.wait(3.0)
        self.wait(6)
''',
},
]
