TITLE = "Q13 - A SEPARABLE TRIPLE INTEGRAL IN SPHERICAL FORM"

QUESTION = {
    "display":
        "Evaluate the triple integral of r^2 sin(theta) / (1 + r^2)^2 "
        "over r from 0 to infinity, theta from 0 to pi/2, and phi from 0 "
        "to pi/2.",
    "speech":
        "Evaluate the triple integral, over r from zero to infinity, theta "
        "from zero to pi by two, and phi from zero to pi by two, of r "
        "squared sine theta, divided by the square of one plus r squared. "
        "Notice that r squared sine theta is exactly the spherical volume "
        "element, so the integral separates into three one-dimensional "
        "integrals.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 13 - TRIPLE INTEGRAL", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"\iiint\frac{r^{2}\sin\theta}{(1+r^{2})^{2}}\,dr\,d\theta\,d\phi",
            font_size=36, color=T.constant)
        limits = MathTex(
            r"r:0\to\infty,\quad \theta:0\to\frac{\pi}{2},\quad "
            r"\phi:0\to\frac{\pi}{2}",
            font_size=30, color=T.text_secondary)
        c_chem = Text("MEASURE", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "r^2 sin(theta) dr dtheta dphi\n"
            "is the spherical volume element",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("SEPARATE", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "the integrand is a product:\n"
            "(radial part)(sin theta)(1)",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("RESULT", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "pi^2 / 8",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, limits, chem, maths, econ).arrange(
            DOWN, aligned_edge=LEFT, buff=0.32)
        rows.move_to(UP * 0.15)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=2.2)
        self.wait(3.5)
        self.play(Write(limits), run_time=1.6)
        self.wait(4.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(5.0)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(5.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(5.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.6).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q13 - SPHERICAL COORDINATES", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"dV=r^{2}\sin\theta\,dr\,d\theta\,d\phi",
                     font_size=34, color=T.result_intermediate)
        r2 = MathTex(r"I=\int_{0}^{\pi/2}\!\!d\phi"
                     r"\int_{0}^{\pi/2}\!\!\sin\theta\,d\theta"
                     r"\int_{0}^{\infty}\frac{r^{2}}{(1+r^{2})^{2}}\,dr",
                     font_size=32, color=T.text_primary)
        r3 = Text("the limits are independent, so the integral factorises",
                  font_size=24, color=T.text_secondary)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        fit_width(rows, 11.8)
        rows.next_to(rule, DOWN, buff=0.6)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        box1 = SurroundingRectangle(r1, buff=0.15, color=T.result_intermediate)
        self.play(Create(box1), run_time=0.7)
        self.wait(3.2)
        self.play(Write(r2), run_time=2.0)
        self.wait(3.5)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.0)
        self.wait(3.6)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q13 - THE ANGULAR INTEGRALS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\int_{0}^{\pi/2}d\phi=\frac{\pi}{2}", font_size=34,
                     color=T.text_primary)
        r2 = MathTex(r"\int_{0}^{\pi/2}\sin\theta\,d\theta"
                     r"=\left[-\cos\theta\right]_{0}^{\pi/2}"
                     r"=0-(-1)=1", font_size=32, color=T.text_primary)
        r3 = Text("so the angular part contributes pi/2", font_size=26,
                  color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        fit_width(rows, 10.8)
        rows.next_to(rule, DOWN, buff=0.7)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.8)
        self.wait(3.4)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.0)
        box3 = SurroundingRectangle(r3, buff=0.15, color=T.result_intermediate)
        self.play(Create(box3), run_time=0.7)
        self.wait(3.8)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q13 - THE RADIAL INTEGRAL", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"J=\int_{0}^{\infty}\frac{r^{2}}{(1+r^{2})^{2}}\,dr",
                     font_size=32, color=T.text_primary)
        r2 = MathTex(r"r=\tan u,\quad dr=\sec^{2}u\,du", font_size=30,
                     color=T.text_secondary)
        r3 = MathTex(r"\frac{r^{2}}{(1+r^{2})^{2}}\,dr"
                     r"=\frac{\tan^{2}u}{\sec^{4}u}\sec^{2}u\,du"
                     r"=\frac{\tan^{2}u}{\sec^{2}u}\,du"
                     r"=\sin^{2}u\,du",
                     font_size=27, color=T.text_primary)
        r4 = MathTex(r"J=\int_{0}^{\pi/2}\sin^{2}u\,du=\frac{\pi}{4}",
                     font_size=33, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.5)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.4)
        self.wait(2.6)
        self.play(Write(r3), run_time=2.0)
        self.wait(3.2)
        self.play(Write(r4), run_time=1.6)
        box4 = SurroundingRectangle(r4, buff=0.16, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q13 - MULTIPLY THE PIECES", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"I=\left(\frac{\pi}{2}\right)(1)\left(\frac{\pi}{4}\right)",
                     font_size=36, color=T.text_primary)
        r2 = MathTex(r"I=\frac{\pi^{2}}{8}", font_size=40,
                     color=T.result_final)
        r3 = Text("numerically, pi squared over eight is about 1.234",
                  font_size=24, color=T.text_secondary)
        r4 = Text("the fast decay of 1/(1+r^2)^2 keeps the radial "
                  "integral finite", font_size=23, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        fit_width(rows, 11.6)
        rows.next_to(rule, DOWN, buff=0.6)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.5)
        box2 = SurroundingRectangle(r2, buff=0.2, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.0)
        self.wait(3.0)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.0)
        self.wait(3.6)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Recognise the measure. In spherical coordinates the volume element "
     "is r squared sine theta, dr d theta d phi. That is exactly the factor "
     "multiplying one over one plus r squared squared. The integrand is a "
     "product of a function of r, a function of theta, and a constant in "
     "phi. Since all the limits are constants, the triple integral "
     "factorises into three one-dimensional integrals.",
     "visual": {"style": "spherical element", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "The phi integral from zero to pi by two is simply pi by two. The "
     "theta integral is the integral of sine theta, which is minus cosine "
     "theta, evaluated from zero to pi by two. That gives zero minus minus "
     "one, which is one. So the angular part contributes pi by two.",
     "visual": {"style": "angular integrals", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "For the radial integral, substitute r equals tan u, so dr equals sec "
     "squared u du. Then one plus r squared is sec squared u, and the whole "
     "expression simplifies beautifully to sine squared u du. The limits "
     "become zero to pi by two. The integral of sine squared u over that "
     "range is pi by four.",
     "visual": {"style": "radial substitution", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "Multiply the three pieces: pi by two, times one, times pi by four. "
     "The result is pi squared over eight, approximately one point two "
     "three four. The rapid decay of one over one plus r squared squared "
     "is what keeps the radial integral finite out to infinity.",
     "visual": {"style": "final product", "transition": "fade"},
     "code": SEG3},
]

LECTURE = {
    "title": TITLE,
    "preset": "lab",
    "format": "mixed",
    "question": QUESTION,
    "question_code": QUESTION_CODE,
    "segments": SEGMENTS,
}
