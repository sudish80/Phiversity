PART = [
{
 "narration":
  "In two and three dimensions, position, displacement, velocity and "
  "acceleration are vectors. Differentiation is performed component "
  "by component: velocity is the derivative of the position vector, "
  "acceleration the derivative of velocity. The same is true for "
  "integration. Everything that held in one dimension still holds, "
  "with each Cartesian component obeying its own scalar law. The "
  "geometry enters through the components, not through new physics.",
 "visual": {"style": "vector motion", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment38(Scene):
    def construct(self):
        head = Text("LESSON 39 - VECTOR POSITION, VELOCITY, ACCELERATION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\vec r(t)=x(t)\hat i+y(t)\hat j+z(t)\hat k",
                     font_size=31, color=T.text_primary)
        r2 = MathTex(r"\vec v=\frac{d\vec r}{dt}=\dot x\hat i+\dot y\hat j+\dot z\hat k",
                     font_size=30, color=T.result_final)
        r3 = MathTex(r"\vec a=\frac{d\vec v}{dt}=\ddot x\hat i+\ddot y\hat j+\ddot z\hat k",
                     font_size=30, color=T.result_final)
        r4 = MathTex(r"\Delta\vec r=\vec r(t_2)-\vec r(t_1)", font_size=30,
                     color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.38)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.8)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.8)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.6)
        self.wait(3.0)
        self.wait(6)
''',
},
{
 "narration":
  "Motion can be given parametrically: x of t, y of t. Differentiating "
  "gives the velocity components, and the speed is the square root "
  "of the sum of their squares. Eliminating the parameter recovers "
  "the path equation in the plane. A circle of radius R traced at "
  "constant angular speed has x equal R cos omega t and y equal R "
  "sin omega t, whose derivatives produce exactly the expected "
  "velocity direction, tangent to the circle.",
 "visual": {"style": "parametric motion", "transition": "fade"},
 "code": r'''
from manim import *


class Segment39(Scene):
    def construct(self):
        head = Text("LESSON 40 - PARAMETRIC MOTION IN THE PLANE",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"x=f(t),\quad y=g(t)\ \Rightarrow\ "
                     r"\vec v=(\dot f,\dot g)", font_size=30,
                     color=T.result_final)
        r2 = MathTex(r"|\vec v|=\sqrt{\dot f^{2}+\dot g^{2}}", font_size=30,
                     color=T.result_intermediate)
        r3 = MathTex(r"x=R\cos\omega t,\ y=R\sin\omega t\ \Rightarrow\ "
                     r"\vec v=(-R\omega\sin\omega t,\ R\omega\cos\omega t)",
                     font_size=27, color=T.result_final)
        rows = VGroup(r1, r2, r3)
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
        self.play(Write(r3), run_time=1.9)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.4)
        self.wait(6)
''',
},
{
 "narration":
  "Polar coordinates suit circular and central motion. The position "
  "is r times r hat. Crucially, the unit vector r hat rotates, and "
  "its derivative is theta dot times theta hat. Differentiating "
  "position therefore yields velocity with a radial part r dot and "
  "a transverse part r theta dot. Differentiating again gives "
  "acceleration with the radial part r double dot minus r theta dot "
  "squared, the centripetal term, and the transverse part r theta "
  "double dot plus two r dot theta dot, containing the Coriolis "
  "term.",
 "visual": {"style": "polar motion", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment40(Scene):
    def construct(self):
        head = Text("LESSON 41 - MOTION IN POLAR COORDINATES",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\vec r=r\hat r,\qquad \dot{\hat r}=\dot\theta\hat\theta",
                     font_size=30, color=T.text_primary)
        r2 = MathTex(r"\vec v=\dot r\hat r+r\dot\theta\hat\theta",
                     font_size=31, color=T.result_final)
        r3 = MathTex(r"\vec a=(\ddot r-r\dot\theta^{2})\hat r"
                     r"+(r\ddot\theta+2\dot r\dot\theta)\hat\theta",
                     font_size=27, color=T.result_final)
        r4 = MathTex(r"\text{radial term }-r\dot\theta^{2}:\ \text{centripetal}",
                     font_size=27, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.36)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.7)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=2.0)
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
  "Along a curved path, acceleration splits into a tangential part, "
  "which changes the speed, and a normal part, which changes the "
  "direction. The tangential acceleration is the derivative of the "
  "speed, and the normal acceleration is speed squared over the "
  "radius of curvature, pointing toward the center of the osculating "
  "circle. For a plane curve y of x, the radius of curvature is one "
  "plus the slope squared, to the three halves, over the second "
  "derivative.",
 "visual": {"style": "tangential and normal", "transition": "fade"},
 "code": r'''
from manim import *


class Segment41(Scene):
    def construct(self):
        head = Text("LESSON 42 - TANGENTIAL AND NORMAL COMPONENTS",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\vec a=a_t\hat T+a_n\hat N", font_size=31,
                     color=T.result_final)
        r2 = MathTex(r"a_t=\frac{dv}{dt},\qquad a_n=\frac{v^{2}}{\rho}",
                     font_size=31, color=T.result_final)
        r3 = MathTex(r"\rho=\frac{(1+y'^{2})^{3/2}}{|y''|}",
                     font_size=31, color=T.result_intermediate)
        r4 = MathTex(r"\text{tangent changes }|\vec v|;\ \text{normal turns }"
                     r"\vec v", font_size=27, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.8)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.8)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_intermediate)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.5)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "The Frenet-Serret frame is the moving basis attached to a space "
  "curve: the unit tangent T, the principal normal N, and the "
  "binormal B, which is T cross N. The frame rotates as the curve "
  "twists; the curvature measures how fast T turns, and the torsion "
  "measures how fast the plane of T and N tilts. This is the full "
  "language of motion along arbitrary space curves, and it extends "
  "everything we did in the plane.",
 "visual": {"style": "frenet serret", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment42(Scene):
    def construct(self):
        head = Text("LESSON 43 - FRENET-SERRET FRAME", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\hat T=\frac{\vec v}{|\vec v|},\qquad "
                     r"\hat N=\frac{d\hat T/dt}{|d\hat T/dt|},\qquad "
                     r"\hat B=\hat T\times\hat N", font_size=28,
                     color=T.result_final)
        r2 = MathTex(r"\frac{d\hat T}{ds}=\kappa\hat N,\qquad "
                     r"\frac{d\hat B}{ds}=-\tau\hat N", font_size=29,
                     color=T.result_final)
        r3 = MathTex(r"\kappa\ \text{curvature},\qquad \tau\ \text{torsion}",
                     font_size=29, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.0)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.9)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.6)
        self.wait(2.8)
        self.wait(6)
''',
},
]
