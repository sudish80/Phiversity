TITLE = "Q16 - CONTINUITY OF A RATIONAL-IRRATIONAL PIECEWISE FUNCTION"

QUESTION = {
    "display":
        "Let pi/3 < A < pi/2. For rational x define f(x) as the limit as "
        "n -> inf of [a x^2 (sin A - sin^3 A) - (5x - b)|sin A - sin^3 A|^n]"
        " / [(sin A - sin^3 A) - |sin A - sin^3 A|^n]. For irrational x "
        "define f(x) with plus signs and |sin A + sin^3 A|. If f is "
        "continuous at x = 2 and x = 3, find b - a.",
    "speech":
        "Let A lie strictly between pi by three and pi by two. For rational "
        "x, f of x is a limit as n tends to infinity of a quotient. The "
        "numerator is a x squared times sine A minus sine cubed A, minus "
        "five x minus b, times the absolute value of sine A minus sine "
        "cubed A, to the power n. The denominator is sine A minus sine "
        "cubed A, minus the same absolute value to the power n. For "
        "irrational x, the same expression uses plus signs and the "
        "absolute value of sine A plus sine cubed A. If f is continuous at "
        "x equals two and at x equals three, find b minus a.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 16 - PIECEWISE CONTINUITY", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(r"\frac{\pi}{3}<A<\frac{\pi}{2}", font_size=30,
                       color=T.constant)
        c_chem = Text("RATIONAL x", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "limit = a x^2\n"
            "because |sinA - sin^3A| < 1",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("IRRATIONAL x", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "limit = 5x - b\n"
            "because sinA + sin^3A > 1",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("CONTINUITY", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "at x=2: 4a = 10 - b\n"
            "at x=3: 9a = 15 - b",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, chem, maths, econ).arrange(DOWN, aligned_edge=LEFT,
                                                       buff=0.36)
        rows.move_to(UP * 0.2)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=1.8)
        self.wait(4.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(5.0)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(5.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q16 - EVALUATE THE LIMITS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\frac{\pi}{3}<A<\frac{\pi}{2}"
                     r"\Rightarrow \frac{\sqrt{3}}{2}<\sin A<1",
                     font_size=30, color=T.text_secondary)
        r2 = MathTex(r"r=|\sin A-\sin^{3}A|=\sin A\cos^{2}A<1",
                     font_size=31, color=T.text_primary)
        r3 = MathTex(r"s=\sin A+\sin^{3}A>1", font_size=31,
                     color=T.text_primary)
        r4 = MathTex(r"r^{n}\to0,\qquad s^{n}\to\infty", font_size=32,
                     color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 11.4)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.5)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.5)
        box4 = SurroundingRectangle(r4, buff=0.15, color=T.result_intermediate)
        self.play(Create(box4), run_time=0.7)
        self.wait(3.8)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q16 - THE TWO BRANCHES", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("for rational x, divide by the denominator and let r^n -> 0:",
                  font_size=23, color=T.text_secondary)
        r2 = MathTex(r"f(x)=\frac{a x^{2}(\sin A-\sin^{3}A)}"
                     r"{\sin A-\sin^{3}A}=a x^{2}", font_size=32,
                     color=T.text_primary)
        r3 = Text("for irrational x, divide by s^n and let s^n -> infinity:",
                  font_size=23, color=T.text_secondary)
        r4 = MathTex(r"f(x)=\frac{5x-b}{1}=5x-b", font_size=32,
                     color=T.text_primary)
        r5 = MathTex(r"f(x)=\begin{cases}a x^{2},&x\in\mathbb{Q}\\"
                     r"5x-b,&x\notin\mathbb{Q}\end{cases}", font_size=33,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 11.6)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(FadeIn(r1, shift=0.15 * UP), run_time=1.1)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.8)
        self.play(FadeIn(r3, shift=0.15 * UP), run_time=1.1)
        self.play(Write(r4), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r5), run_time=1.8)
        box5 = SurroundingRectangle(r5, buff=0.15, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        self.wait(3.8)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q16 - IMPOSE CONTINUITY", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("rationals and irrationals are dense, so both formulas must "
                  "agree at each point of continuity:", font_size=23,
                  color=T.text_secondary)
        r2 = MathTex(r"x=2:\quad a(2)^{2}=5(2)-b"
                     r"\quad\Rightarrow\quad 4a=10-b", font_size=31,
                     color=T.text_primary)
        r3 = MathTex(r"x=3:\quad a(3)^{2}=5(3)-b"
                     r"\quad\Rightarrow\quad 9a=15-b", font_size=31,
                     color=T.text_primary)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        fit_width(rows, 11.8)
        rows.next_to(rule, DOWN, buff=0.7)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(FadeIn(r1, shift=0.2 * UP), run_time=1.4)
        self.wait(3.4)
        self.play(Write(r2), run_time=1.7)
        self.wait(3.2)
        self.play(Write(r3), run_time=1.7)
        box3 = SurroundingRectangle(VGroup(r2, r3), buff=0.16,
                                    color=T.result_intermediate)
        self.play(Create(box3), run_time=0.7)
        self.wait(4.0)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q16 - SOLVE FOR b - a", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"(9a-4a)=(15-b)-(10-b)", font_size=32,
                     color=T.text_primary)
        r2 = MathTex(r"5a=5\quad\Rightarrow\quad a=1", font_size=34,
                     color=T.result_intermediate)
        r3 = MathTex(r"4(1)=10-b\quad\Rightarrow\quad b=6", font_size=34,
                     color=T.result_intermediate)
        r4 = MathTex(r"b-a=6-1=5", font_size=40, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        fit_width(rows, 10.8)
        rows.next_to(rule, DOWN, buff=0.55)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.5)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.5)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.5)
        box4 = SurroundingRectangle(r4, buff=0.2, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=1.0)
        self.wait(4.2)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Because A lies between pi by three and pi by two, sine A lies "
     "between root three over two and one. Therefore sine A minus sine "
     "cubed A, which equals sine A cosine squared A, has absolute value "
     "less than one. But sine A plus sine cubed A is greater than one. So "
     "the power r to the n tends to zero, while the power s to the n tends "
     "to infinity.",
     "visual": {"style": "bounds", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Now evaluate each branch. For rational x, every term containing r to "
     "the n vanishes, leaving a x squared times sine A minus sine cubed A, "
     "over the same factor. That is simply a x squared. For irrational x, "
     "divide numerator and denominator by s to the n. The exponential "
     "terms disappear, leaving five x minus b. So f is a x squared on the "
     "rationals and five x minus b on the irrationals.",
     "visual": {"style": "branches", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Rationals and irrationals are both dense, so at a point of "
     "continuity the two formulas must give the same value. At x equals "
     "two, a times four must equal ten minus b. At x equals three, nine a "
     "must equal fifteen minus b.",
     "visual": {"style": "continuity equations", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "Subtract the first equation from the second. Five a equals five, so "
     "a equals one. Substituting back, four equals ten minus b, so b equals "
     "six. Therefore b minus a equals five.",
     "visual": {"style": "solve", "transition": "fade"},
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
