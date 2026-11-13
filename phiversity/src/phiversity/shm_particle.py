TITLE = "Q8 - SIMPLE HARMONIC MOTION: x = 0.05 sin(4 pi t)"

QUESTION = {
    "display":
        "A particle executes simple harmonic motion according to "
        "x = 0.05 sin(4 pi t) metres. Find (a) the amplitude, (b) the "
        "angular frequency, (c) the frequency, (d) the time period, "
        "(e) the maximum velocity, (f) the maximum acceleration, and "
        "(g) the velocity and acceleration at t = 0.5 s. Show all steps.",
    "speech":
        "A particle executes simple harmonic motion according to x equals "
        "zero point zero five sine four pi t. Calculate part a, the "
        "amplitude of oscillation. Part b, the angular frequency. Part c, "
        "the frequency. Part d, the time period. Part e, the maximum "
        "velocity. Part f, the maximum acceleration. Part g, the velocity "
        "and acceleration at t equals zero point five seconds. Show all "
        "necessary mathematical steps and derivations.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 8 - SIMPLE HARMONIC MOTION", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(r"x=0.05\sin(4\pi t)\ \text{m}", font_size=34,
                       color=T.constant)
        c_chem = Text("STANDARD FORM", font_size=20,
                      color=T.highlight_secondary)
        r_chem = Text(
            "x = A sin(omega t)\n"
            "compare term by term",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("FIND", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "a  amplitude A\n"
            "b  angular frequency omega\n"
            "c-d  frequency f, period T\n"
            "e-f  v_max, a_max\n"
            "g  v and a at t = 0.5 s",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("KEY RELATIONS", font_size=20,
                      color=T.highlight_secondary)
        r_econ = Text(
            "omega = 2 pi f = 2 pi / T\n"
            "v = dx/dt,  a = dv/dt\n"
            "v_max = A omega,  a_max = A omega^2",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, chem, maths, econ).arrange(DOWN, aligned_edge=LEFT,
                                                       buff=0.32)
        rows.move_to(UP * 0.2)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=2.0)
        self.wait(5.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(8.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q8 (a-b) - AMPLITUDE AND ANGULAR FREQUENCY", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"x=0.05\sin(4\pi t)", font_size=34,
                     color=T.constant)
        r2 = MathTex(r"x=A\sin(\omega t)", font_size=32,
                     color=T.text_primary)
        r3 = MathTex(r"\text{compare: }\ A=0.05\ \text{m}", font_size=32,
                     color=T.result_intermediate)
        r4 = MathTex(r"\omega=4\pi\ \text{rad/s}\approx12.57\ \text{rad/s}",
                     font_size=32, color=T.result_intermediate)
        r5 = Text("A is the maximum displacement from equilibrium; omega is "
                  "the rate of change of phase", font_size=23,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 11.6)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.15)
        self.play(Write(r2), run_time=1.4)
        self.wait(1.9)
        self.play(Write(r3), run_time=1.4)
        box3 = SurroundingRectangle(r3, buff=0.14, color=T.result_intermediate)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_intermediate, run_time=0.9)
        self.wait(2.28)
        self.play(Write(r4), run_time=1.4)
        box4 = SurroundingRectangle(r4, buff=0.14, color=T.result_intermediate)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_intermediate, run_time=0.9)
        self.wait(2.28)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.0)
        self.wait(2.15)
        self.wait(3.8)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q8 (c-d) - FREQUENCY AND TIME PERIOD", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"f=\frac{\omega}{2\pi}=\frac{4\pi}{2\pi}",
                     font_size=34, color=T.text_primary)
        r2 = MathTex(r"f=2\ \text{Hz}", font_size=34,
                     color=T.result_intermediate)
        r3 = MathTex(r"T=\frac{1}{f}=\frac{1}{2}", font_size=34,
                     color=T.text_primary)
        r4 = MathTex(r"T=0.5\ \text{s}", font_size=34, color=T.result_final)
        r5 = Text("the particle completes two oscillations every second",
                  font_size=24, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 10.6)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(1.35)
        self.play(Write(r2), run_time=1.4)
        box2 = SurroundingRectangle(r2, buff=0.14, color=T.result_intermediate)
        self.play(Create(box2), run_time=0.7)
        self.wait(1.43)
        self.play(Write(r3), run_time=1.4)
        self.wait(1.27)
        self.play(Write(r4), run_time=1.4)
        box4 = SurroundingRectangle(r4, buff=0.15, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(1.52)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.0)
        self.wait(1.43)
        self.wait(2.53)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q8 (e-f) - MAXIMUM VELOCITY AND ACCELERATION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"v=\frac{dx}{dt}=A\omega\cos(\omega t)",
                     font_size=31, color=T.text_primary)
        r2 = MathTex(r"v_{\max}=A\omega=0.05\times 4\pi", font_size=31,
                     color=T.text_primary)
        r3 = MathTex(r"v_{\max}=0.2\pi\approx0.628\ \text{m/s}",
                     font_size=31, color=T.result_intermediate)
        r4 = MathTex(r"a=\frac{dv}{dt}=-A\omega^{2}\sin(\omega t)",
                     font_size=31, color=T.text_primary)
        r5 = MathTex(r"a_{\max}=A\omega^{2}=0.05\times(4\pi)^{2}",
                     font_size=31, color=T.text_primary)
        r6 = MathTex(r"a_{\max}=0.8\pi^{2}\approx7.90\ \text{m/s}^{2}",
                     font_size=31, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        fit_width(rows, 11.6)
        rows.next_to(rule, DOWN, buff=0.38)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.4)
        self.wait(2.63)
        self.play(Write(r2), run_time=1.4)
        self.wait(2.46)
        self.play(Write(r3), run_time=1.4)
        box3 = SurroundingRectangle(r3, buff=0.13, color=T.result_intermediate)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_intermediate, run_time=0.9)
        self.wait(2.98)
        self.play(Write(r4), run_time=1.4)
        self.wait(2.63)
        self.play(Write(r5), run_time=1.4)
        self.wait(2.46)
        self.play(Write(r6), run_time=1.4)
        box6 = SurroundingRectangle(r6, buff=0.13, color=T.result_final)
        self.play(Create(box6), run_time=0.7)
        emphasize(self, r6, color=T.result_final, run_time=0.9)
        self.wait(3.16)
        self.wait(5.26)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q8 (g) - VELOCITY AND ACCELERATION AT t = 0.5 s",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\omega t=4\pi\times0.5=2\pi", font_size=32,
                     color=T.text_primary)
        r2 = MathTex(r"x=0.05\sin(2\pi)=0", font_size=32,
                     color=T.text_primary)
        r3 = MathTex(r"v=0.2\pi\cos(2\pi)=0.2\pi", font_size=32,
                     color=T.text_primary)
        r4 = MathTex(r"v\approx0.628\ \text{m/s}", font_size=32,
                     color=T.result_intermediate)
        r5 = MathTex(r"a=-0.8\pi^{2}\sin(2\pi)=0", font_size=32,
                     color=T.text_primary)
        r6 = Text("the particle is at equilibrium, moving at maximum speed; "
                  "acceleration is momentarily zero", font_size=23,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 11.6)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.4)
        self.wait(2.83)
        self.play(Write(r2), run_time=1.4)
        self.wait(2.83)
        self.play(Write(r3), run_time=1.4)
        self.wait(2.64)
        self.play(Write(r4), run_time=1.4)
        box4 = SurroundingRectangle(r4, buff=0.14, color=T.result_intermediate)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_intermediate, run_time=0.9)
        self.wait(3.21)
        self.play(Write(r5), run_time=1.4)
        box5 = SurroundingRectangle(r5, buff=0.14, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=0.9)
        self.wait(3.21)
        self.play(FadeIn(r6, shift=0.2 * UP), run_time=1.0)
        self.wait(3.4)
        self.wait(5.67)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q8 - THE MOTION AT A GLANCE", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        axes = Axes(x_range=[0, 1.0, 0.25], y_range=[-0.06, 0.06, 0.02],
                    x_length=8.2, y_length=3.0,
                    axis_config={"color": T.text_muted, "stroke_width": 1.5,
                                 "include_tip": False})
        axes.move_to(DOWN * 0.7)
        curve = axes.plot(lambda t: 0.05 * np.sin(4 * np.pi * t),
                          x_range=[0, 1.0], color=T.graph_function,
                          stroke_width=4)
        def c2p(t, x):
            return axes.c2p(t, x)
        amp_top = DashedLine(c2p(0, 0.05), c2p(1.0, 0.05),
                             color=T.text_secondary, stroke_width=2)
        amp_bot = DashedLine(c2p(0, -0.05), c2p(1.0, -0.05),
                             color=T.text_secondary, stroke_width=2)
        amp_lab = MathTex(r"A=0.05\,\text{m}", font_size=23,
                          color=T.text_secondary)
        amp_lab.next_to(amp_top, RIGHT, buff=0.1)
        T_lab = MathTex(r"T=0.5\,\text{s}", font_size=23,
                        color=T.text_secondary)
        T_lab.move_to(axes.c2p(0.5, 0.085))
        t_lab = MathTex(r"t\,(\text{s})", font_size=22, color=T.text_secondary)
        t_lab.next_to(axes, DOWN, buff=0.12).shift(RIGHT * 3.6)
        x_lab = MathTex(r"x\,(\text{m})", font_size=22, color=T.text_secondary)
        x_lab.next_to(axes, LEFT, buff=0.12).shift(UP * 1.3)
        pdot = Dot(c2p(0.5, 0.0), radius=0.08, color=T.graph_point)
        p_lab = MathTex(r"t=0.5:\ x=0,\ v=v_{\max}", font_size=22,
                        color=T.graph_point)
        p_lab.next_to(pdot, DOWN, buff=0.55)
        self.play(Create(axes), Create(curve), run_time=2.0)
        self.play(Write(amp_lab), Create(amp_top), Create(amp_bot),
                  run_time=1.2)
        self.wait(3.0)
        self.play(Write(T_lab), Write(t_lab), Write(x_lab), run_time=1.2)
        self.wait(3.0)
        self.play(FadeIn(pdot), Write(p_lab), run_time=1.2)
        self.wait(4.0)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "The given equation is x equals zero point zero five sine four pi t. "
     "Compare it term by term with the standard form x equals A sine "
     "omega t. The amplitude A is the coefficient in front, zero point "
     "zero five metres. The angular frequency omega is the coefficient of "
     "t, four pi radians per second, about twelve point five seven "
     "radians per second.",
     "visual": {"style": "comparison", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "The frequency is omega over two pi. Substituting four pi over two "
     "pi gives two hertz. The time period is the reciprocal of the "
     "frequency, one over two, which is zero point five seconds. So the "
     "particle completes two full oscillations every second.",
     "visual": {"style": "calculation", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Velocity is the derivative of displacement, giving A omega cosine "
     "omega t, so its maximum is A omega, that is zero point zero five "
     "times four pi, equal to zero point two pi, about zero point six "
     "two eight metres per second. Acceleration is the derivative of "
     "velocity, minus A omega squared sine omega t, so its maximum is A "
     "omega squared, zero point zero five times sixteen pi squared, which "
     "is zero point eight pi squared, about seven point nine metres per "
     "second squared.",
     "visual": {"style": "derivations", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "At t equals zero point five seconds, omega t equals four pi times "
     "zero point five, that is two pi radians. Then sine of two pi is "
     "zero, so the displacement is zero. The velocity is zero point two "
     "pi times cosine of two pi, which is zero point two pi, about zero "
     "point six two eight metres per second. The acceleration is minus "
     "zero point eight pi squared times sine of two pi, which is zero. "
     "The particle is at equilibrium, moving at maximum speed, with zero "
     "acceleration.",
     "visual": {"style": "evaluation", "transition": "fade"},
     "code": SEG3},
    {"narration":
     "The graph shows the displacement against time. The curve rises to "
     "the amplitude zero point zero five metres and falls to minus zero "
     "point zero five metres, repeating every zero point five seconds. "
     "Mark the instant t equals zero point five seconds: the curve passes "
     "through zero with maximum positive slope, confirming that the "
     "displacement is zero and the velocity is maximum there.",
     "visual": {"style": "x-t graph", "transition": "fade"},
     "code": SEG4},
]

LECTURE = {
    "title": TITLE,
    "preset": "lab",
    "format": "mixed",
    "question": QUESTION,
    "question_code": QUESTION_CODE,
    "segments": SEGMENTS,
}
