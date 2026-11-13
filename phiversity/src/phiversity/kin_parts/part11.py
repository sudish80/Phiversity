PART = [
{
 "narration":
  "Motion in a translating frame adds the frame's velocity to the "
  "body's velocity relative to the frame. If the frame moves at "
  "constant velocity, the relative velocity is simply the "
  "difference of the absolute velocities. If the frame "
  "accelerates, fictitious forces appear for dynamics, but the "
  "kinematic statement remains: absolute equals relative plus "
  "frame. This is the master formula behind trains, lifts and "
  "moving walkways.",
 "visual": {"style": "translating frames", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment59(Scene):
    def construct(self):
        head = Text("LESSON 60 - MOTION IN A TRANSLATING FRAME",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\vec v_{\text{abs}}=\vec v_{\text{rel}}+\vec v_{\text{frame}}",
                     font_size=30, color=T.result_final)
        r2 = MathTex(r"\vec a_{\text{abs}}=\vec a_{\text{rel}}+\vec a_{\text{frame}}",
                     font_size=30, color=T.result_final)
        r3 = MathTex(r"\text{frame constant }v:\ \text{relative velocity is constant difference}",
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
        self.wait(3.2)
        self.play(Write(r2), run_time=1.8)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.6)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "Rotating frames introduce extra terms. If the frame spins at "
  "angular velocity omega, the acceleration measured in the "
  "rotating frame differs from the inertial acceleration by three "
  "terms: the centrifugal acceleration omega cross omega cross r, "
  "the Coriolis acceleration two omega cross v, and the angular "
  "acceleration term alpha cross r. The Coriolis term is why "
  "cyclones spin and why a projectile fired across a rotating "
  "planet veers sideways.",
 "visual": {"style": "rotating frames", "transition": "fade"},
 "code": r'''
from manim import *


class Segment60(Scene):
    def construct(self):
        head = Text("LESSON 61 - ROTATING FRAMES AND CORIOLIS",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\vec a_{\text{inertial}}=\vec a_{\text{rot}}"
                     r"+\vec\omega\times(\vec\omega\times\vec r)"
                     r"+2\vec\omega\times\vec v+\vec\alpha\times\vec r",
                     font_size=25, color=T.result_final)
        r2 = MathTex(r"\text{centrifugal: }\omega^{2}r\ \text{outward}",
                     font_size=28, color=T.result_intermediate)
        r3 = MathTex(r"\text{Coriolis: }2\omega v\ \text{perpendicular}",
                     font_size=28, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.2)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(3.6)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.6)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "A rigid body has two elementary motions: translation, where every "
  "point moves along parallel paths with the same velocity, and "
  "rotation, where every point moves on a circle about a common "
  "axis. General plane motion is the sum of the two: the velocity "
  "of any point is the translation of the centre of mass plus omega "
  "cross the relative position vector. This decomposition is the "
  "foundation of all rigid-body kinematics.",
 "visual": {"style": "rigid body", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment61(Scene):
    def construct(self):
        head = Text("LESSON 62 - RIGID BODY TRANSLATION AND ROTATION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\vec v_A=\vec v_{\text{cm}}+\vec\omega\times\vec r_{A/\text{cm}}",
                     font_size=30, color=T.result_final)
        r2 = MathTex(r"\text{translation: all points same }\vec v",
                     font_size=28, color=T.result_intermediate)
        r3 = MathTex(r"\text{rotation: }\vec v=\vec\omega\times\vec r",
                     font_size=28, color=T.result_intermediate)
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
        self.play(Write(r2), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.6)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "Mechanisms, cams, gears and robot arms are systems of rigid links "
  "with joints. The instantaneous centre method finds the point with "
  "zero velocity at an instant, and every other velocity is omega "
  "cross the vector from that point. Forward kinematics computes the "
  "tool position from the joint angles; inverse kinematics solves "
  "for the angles that place the tool at a desired point. "
  "Trajectory planning designs smooth curves in joint space between "
  "the two.",
 "visual": {"style": "mechanisms", "transition": "fade"},
 "code": r'''
from manim import *


class Segment62(Scene):
    def construct(self):
        head = Text("LESSON 63 - INSTANTANEOUS CENTRE, CAM, ROBOT ARM",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"v_P=\omega\times\vec r_{P/\text{IC}}", font_size=31,
                     color=T.result_final)
        r2 = MathTex(r"\text{forward: }(x,y)=f(\theta_1,\theta_2)",
                     font_size=29, color=T.result_intermediate)
        r3 = MathTex(r"\text{inverse: }(\theta_1,\theta_2)=f^{-1}(x,y)",
                     font_size=29, color=T.result_intermediate)
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
        self.wait(2.6)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "Oscillatory kinematics is the last chapter of pure motion. Simple "
  "harmonic motion has x equal A sine omega t plus phi. "
  "Differentiating gives velocity A omega cos omega t plus phi and "
  "acceleration minus omega squared x, which is the signature "
  "equation a equals minus omega squared x. Damped oscillations add "
  "an exponential envelope, so the amplitude decays while the "
  "frequency shifts slightly. These results are the kinematic "
  "core of half of physics.",
 "visual": {"style": "oscillatory", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment63(Scene):
    def construct(self):
        head = Text("LESSON 64 - OSCILLATORY MOTION AND SHM",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"x=A\sin(\omega t+\phi)", font_size=32,
                     color=T.result_final)
        r2 = MathTex(r"v=A\omega\cos(\omega t+\phi),\qquad "
                     r"a=-\omega^{2}x", font_size=30,
                     color=T.result_final)
        r3 = MathTex(r"\text{damped: }x=Ae^{-bt}\sin(\omega' t+\phi)",
                     font_size=29, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.9)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r3), run_time=1.8)
        self.wait(3.0)
        self.wait(6)
''',
},
]
