PART = [
{
 "narration":
  "Circular motion is described by angles. Angular position theta, "
  "angular displacement delta theta, angular velocity omega equals d "
  "theta d t, and angular acceleration alpha equals d omega d t. "
  "These mirror the linear quantities exactly: omega is the "
  "velocity of the angle, alpha is the acceleration of the angle. "
  "All the kinematic laws we derived for x carry over to theta, with "
  "omega in place of v and alpha in place of a.",
 "visual": {"style": "angular quantities", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment43(Scene):
    def construct(self):
        head = Text("LESSON 44 - ANGULAR POSITION, VELOCITY, ACCELERATION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\omega=\lim_{\Delta t\to0}\frac{\Delta\theta}{\Delta t}"
                     r"=\frac{d\theta}{dt}", font_size=31,
                     color=T.result_final)
        r2 = MathTex(r"\alpha=\lim_{\Delta t\to0}\frac{\Delta\omega}{\Delta t}"
                     r"=\frac{d\omega}{dt}=\frac{d^{2}\theta}{dt^{2}}",
                     font_size=30, color=T.result_final)
        r3 = MathTex(r"\text{constant }\alpha:\ \omega=\omega_0+\alpha t,\ "
                     r"\theta=\theta_0+\omega_0 t+\frac{1}{2}\alpha t^{2}",
                     font_size=27, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
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
        self.play(Write(r3), run_time=1.9)
        self.wait(3.2)
        self.wait(6)
''',
},
{
 "narration":
  "Linear and angular quantities are linked by the radius. Arc length "
  "s equals r theta, and differentiating gives the tangential speed "
  "v equals r omega. Differentiating again gives tangential "
  "acceleration a t equals r alpha. These relations assume the "
  "radius is constant, which it is for fixed circular motion. The "
  "angular speed is shared by every point of a rigid rotating body, "
  "while the linear speed grows with the distance from the axis.",
 "visual": {"style": "linear-angular", "transition": "fade"},
 "code": r'''
from manim import *


class Segment44(Scene):
    def construct(self):
        head = Text("LESSON 45 - RELATING LINEAR AND ANGULAR MOTION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"s=r\theta\ \Rightarrow\ v=r\omega\ \Rightarrow\ "
                     r"a_t=r\alpha", font_size=31, color=T.result_final)
        r2 = MathTex(r"\omega\ \text{same for all points; }v\ \text{grows with }r",
                     font_size=28, color=T.result_intermediate)
        r3 = MathTex(r"\text{assumption: }r=\text{const}", font_size=28,
                     color=T.text_secondary)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.46)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.5)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "Derive centripetal acceleration. A particle moving on a circle at "
  "speed v has velocity vectors at two nearby times that differ in "
  "direction by the small angle delta theta. The change in velocity "
  "is perpendicular to the velocity, pointing toward the center, "
  "and its magnitude is v delta theta. Dividing by delta t gives "
  "the magnitude v omega, which is v squared over r. The direction "
  "is always radial inward, which is why uniform circular motion has "
  "acceleration even at constant speed.",
 "visual": {"style": "centripetal derivation", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment45(Scene):
    def construct(self):
        head = Text("LESSON 46 - DERIVING CENTRIPETAL ACCELERATION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"|\Delta\vec v|\approx v\,\Delta\theta", font_size=30,
                     color=T.text_primary)
        r2 = MathTex(r"a=\lim_{\Delta t\to0}\frac{v\,\Delta\theta}{\Delta t}"
                     r"=v\omega=\frac{v^{2}}{r}", font_size=30,
                     color=T.result_final)
        r3 = MathTex(r"\vec a_c=-\omega^{2}\vec r", font_size=31,
                     color=T.result_final)
        r4 = MathTex(r"\text{uniform: }a_t=0,\ \text{only }a_c", font_size=28,
                     color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.9)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.6)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "Non-uniform circular motion has both accelerations: tangential a "
  "t equals r alpha changes the speed, and centripetal a c equals v "
  "squared over r changes the direction. The total acceleration is "
  "the vector sum, and its magnitude is the square root of the sum "
  "of the squares. The angle the total acceleration makes with the "
  "radius is the arctangent of the ratio a t over a c.",
 "visual": {"style": "non-uniform circular", "transition": "fade"},
 "code": r'''
from manim import *


class Segment46(Scene):
    def construct(self):
        head = Text("LESSON 47 - NON-UNIFORM CIRCULAR MOTION", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"a_t=r\alpha,\qquad a_c=\frac{v^{2}}{r}",
                     font_size=31, color=T.result_final)
        r2 = MathTex(r"|\vec a|=\sqrt{a_t^{2}+a_c^{2}}", font_size=31,
                     color=T.result_final)
        r3 = MathTex(r"\tan\phi=\frac{a_t}{a_c}", font_size=31,
                     color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.46)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.7)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=0.9)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "A full revolution is two pi radians. The period T is the time for "
  "one revolution, and the frequency f is the number of revolutions "
  "per second, so T equals one over f. The angular frequency omega "
  "is two pi f, and the speed is omega r, which is two pi r over "
  "T. Rotational kinematics with constant angular acceleration "
  "mirrors linear kinematics exactly, with theta, omega, alpha "
  "playing the roles of x, v, a.",
 "visual": {"style": "period frequency", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment47(Scene):
    def construct(self):
        head = Text("LESSON 48 - PERIOD, FREQUENCY, ANGULAR FREQUENCY",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"T=\frac{2\pi}{\omega},\qquad f=\frac{1}{T},\qquad "
                     r"\omega=2\pi f", font_size=31, color=T.result_final)
        r2 = MathTex(r"v=\omega r=\frac{2\pi r}{T}", font_size=31,
                     color=T.result_final)
        r3 = MathTex(r"\omega=\omega_0+\alpha t,\quad "
                     r"\theta=\theta_0+\omega_0 t+\frac{1}{2}\alpha t^{2},\quad "
                     r"\omega^{2}=\omega_0^{2}+2\alpha\theta",
                     font_size=27, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.9)
        self.wait(3.2)
        self.wait(6)
''',
},
{
 "narration":
  "Rolling without slipping connects translation and rotation: if a "
  "wheel rolls, the point of contact is instantaneously at rest, "
  "and the center moves at omega R. The instantaneous centre of "
  "rotation is the point of contact itself, so every point of the "
  "wheel momentarily moves on a circle around it. For a wheel of "
  "radius R rolling at speed v, the top point moves at two v and "
  "the bottom point at zero. This single idea solves gear, belt and "
  "rolling problems.",
 "visual": {"style": "rolling", "transition": "fade"},
 "code": r'''
from manim import *


class Segment48(Scene):
    def construct(self):
        head = Text("LESSON 49 - ROLLING KINEMATICS, INSTANTANEOUS CENTRE",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{no slipping: }v_{\text{cm}}=\omega R",
                     font_size=31, color=T.result_final)
        r2 = MathTex(r"v_{\text{top}}=2v_{\text{cm}},\qquad "
                     r"v_{\text{bottom}}=0", font_size=31,
                     color=T.result_final)
        r3 = MathTex(r"v_{\text{point}}=v_{\text{cm}}+\omega\times\vec r",
                     font_size=31, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.46)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.8)
        self.wait(3.0)
        self.wait(6)
''',
},
]
