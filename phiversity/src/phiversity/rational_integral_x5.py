TITLE = "Q19 - THE INTEGRAL OF 1/(1+x^5) BY PARTIAL FRACTIONS"

QUESTION = {
    "display":
        "Evaluate I = integral of dx / (1 + x^5).",
    "speech":
        "Evaluate the indefinite integral of one over one plus x to the "
        "fifth, dx. The plan is to factor one plus x to the fifth over the "
        "reals into a linear factor and two quadratics, split into partial "
        "fractions, and integrate each piece, using logarithms for the "
        "linear parts and completing the square for the arctangent parts.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 19 - RATIONAL INTEGRAL", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(r"I=\int\frac{dx}{1+x^{5}}", font_size=38,
                       color=T.constant)
        c_chem = Text("FACTORISE", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "1 + x^5 = (1+x)(x^2 + ax + 1)(x^2 + bx + 1)\n"
            "a = (sqrt5 - 1)/2,  b = -(sqrt5 + 1)/2",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("PARTIAL FRACTIONS", font_size=20,
                      color=T.highlight_secondary)
        r_math = Text(
            "A = 1/5 (put x = -1)\n"
            "solve the linear system for B, C, D, E",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("INTEGRATE", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "log terms from the linear factor,\n"
            "log + arctan terms from the quadratics",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, chem, maths, econ).arrange(DOWN, aligned_edge=LEFT,
                                                       buff=0.34)
        rows.move_to(UP * 0.2)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=1.8)
        self.wait(4.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q19 - FACTOR THE DENOMINATOR", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"x^{5}+1=(x+1)\left(x^{4}-x^{3}+x^{2}-x+1\right)",
                     font_size=30, color=T.text_primary)
        r2 = MathTex(r"x^{4}-x^{3}+x^{2}-x+1"
                     r"=\left(x^{2}+ax+1\right)\left(x^{2}+bx+1\right)",
                     font_size=29, color=T.text_primary)
        r3 = MathTex(r"a+b=-1,\qquad ab=-1", font_size=31,
                     color=T.result_intermediate)
        r4 = MathTex(r"a=\frac{\sqrt5-1}{2},\qquad "
                     r"b=-\frac{\sqrt5+1}{2}", font_size=32,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 11.8)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.5)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.6)
        box4 = SurroundingRectangle(r4, buff=0.16, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q19 - PARTIAL FRACTION COEFFICIENTS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\frac{1}{1+x^{5}}=\frac{A}{x+1}"
                     r"+\frac{Bx+C}{x^{2}+ax+1}"
                     r"+\frac{Dx+E}{x^{2}+bx+1}", font_size=28,
                     color=T.text_primary)
        r2 = MathTex(r"x=-1:\quad A=\frac{1}{(-1)^4-(-1)^3+1+1+1}"
                     r"=\frac{1}{5}", font_size=29, color=T.text_primary)
        r3 = MathTex(r"B+D=-\frac{1}{5},\quad \beta B+\alpha D=-\frac{2}{5},"
                     r"\quad C+E=\frac{4}{5},\quad \beta C+\alpha E=-\frac{2}{5}",
                     font_size=27, color=T.text_secondary)
        r4 = MathTex(r"B=\frac{\sqrt5-1}{10},\quad C=\frac{2}{5},\qquad "
                     r"D=-\frac{\sqrt5+1}{10},\quad E=\frac{2}{5}",
                     font_size=30, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.0)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.7)
        self.wait(3.0)
        self.play(Write(r3), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.8)
        box4 = SurroundingRectangle(r4, buff=0.16, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q19 - THE LOGARITHMIC PART", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\int\frac{A\,dx}{x+1}=\frac{1}{5}\ln|x+1|",
                     font_size=31, color=T.text_primary)
        r2 = MathTex(r"\int\frac{Bx+C}{x^{2}+ax+1}dx"
                     r"=\frac{B}{2}\ln\left(x^{2}+ax+1\right)"
                     r"+\left(C-\frac{B\alpha}{2}\right)"
                     r"\int\frac{dx}{x^{2}+ax+1}", font_size=27,
                     color=T.text_primary)
        r3 = MathTex(r"\frac{B}{2}=\frac{\sqrt5-1}{20},\qquad "
                     r"C-\frac{B\alpha}{2}=\frac{5+\sqrt5}{20}",
                     font_size=29, color=T.result_intermediate)
        r4 = MathTex(r"\frac{D}{2}=-\frac{\sqrt5+1}{20},\qquad "
                     r"E-\frac{D\beta}{2}=\frac{5-\sqrt5}{20}",
                     font_size=29, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r2), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.8)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.8)
        box4 = SurroundingRectangle(VGroup(r3, r4), buff=0.15,
                                    color=T.result_intermediate)
        self.play(Create(box4), run_time=0.7)
        self.wait(3.6)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q19 - COMPLETE THE SQUARE FOR THE ARCTANGENTS",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"x^{2}+ax+1=\left(x+\frac{\alpha}{2}\right)^{2}"
                     r"+\frac{5+\sqrt5}{8}", font_size=30,
                     color=T.text_primary)
        r2 = MathTex(r"x^{2}+bx+1=\left(x+\frac{\beta}{2}\right)^{2}"
                     r"+\frac{5-\sqrt5}{8}", font_size=30,
                     color=T.text_primary)
        r3 = MathTex(r"\int\frac{dx}{\left(x+c\right)^{2}+d^{2}}"
                     r"=\frac{1}{d}\arctan\frac{x+c}{d}", font_size=29,
                     color=T.text_secondary)
        r4 = MathTex(r"\frac{5+\sqrt5}{20}\cdot\sqrt{\frac{8}{5+\sqrt5}}"
                     r"=\frac{\sqrt{10+2\sqrt5}}{10}", font_size=30,
                     color=T.result_final)
        r5 = MathTex(r"\frac{5-\sqrt5}{20}\cdot\sqrt{\frac{8}{5-\sqrt5}}"
                     r"=\frac{\sqrt{10-2\sqrt5}}{10}", font_size=30,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.6)
        self.wait(2.4)
        self.play(Write(r4), run_time=1.7)
        self.play(Write(r5), run_time=1.7)
        box5 = SurroundingRectangle(VGroup(r4, r5), buff=0.15,
                                    color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        self.wait(3.8)
        self.wait(6)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q19 - ASSEMBLE THE ANSWER", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(
            r"I=\frac{1}{5}\ln|1+x|", font_size=31, color=T.text_primary)
        r2 = MathTex(
            r"+\frac{\sqrt5-1}{20}\ln\left(x^{2}+ax+1\right)"
            r"-\frac{\sqrt5+1}{20}\ln\left(x^{2}+bx+1\right)", font_size=29,
            color=T.text_primary)
        r3 = MathTex(
            r"+\frac{\sqrt{10+2\sqrt5}}{10}\arctan\!\left((2x+\alpha)"
            r"\sqrt{\tfrac{2}{5+\sqrt5}}\right)", font_size=29,
            color=T.text_primary)
        r4 = MathTex(
            r"+\frac{\sqrt{10-2\sqrt5}}{10}\arctan\!\left((2x+\beta)"
            r"\sqrt{\tfrac{2}{5-\sqrt5}}\right)+C", font_size=29,
            color=T.text_primary)
        r5 = MathTex(r"\alpha=\frac{\sqrt5-1}{2},\qquad "
                     r"\beta=-\frac{\sqrt5+1}{2}", font_size=29,
                     color=T.text_secondary)
        r6 = Text("check: differentiate at x = 0 gives 1/5 + 2/5 + 2/5 = 1",
                  font_size=23, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        fit_width(rows, 12.4)
        rows.next_to(rule, DOWN, buff=0.32)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.4)
        self.wait(2.2)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.4)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.2)
        self.play(Write(r4), run_time=1.7)
        self.wait(2.2)
        self.play(Write(r5), run_time=1.5)
        self.wait(2.4)
        self.play(FadeIn(r6, shift=0.2 * UP), run_time=1.2)
        box6 = SurroundingRectangle(r6, buff=0.14, color=T.result_final)
        self.play(Create(box6), run_time=0.7)
        self.wait(4.0)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Factor the denominator. x to the fifth plus one is x plus one, times "
     "the quartic x to the fourth minus x cubed plus x squared minus x plus "
     "one. The quartic factors over the reals into two quadratics, x "
     "squared plus a x plus one and x squared plus b x plus one, where a "
     "plus b equals minus one and a b equals minus one. Solving gives a "
     "equal to root five minus one over two, and b equal to minus root "
     "five plus one over two.",
     "visual": {"style": "factorisation", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Now set up partial fractions. Put x equal to minus one to get A "
     "equal to one fifth, because the quartic value there is five. "
     "Matching the remaining coefficients gives a linear system: B plus D "
     "is minus one fifth, and C plus E is four fifths, with the mixed "
     "equations forcing the rest. The solution is B equal to root five "
     "minus one over ten, C equal to two fifths, D equal to minus root "
     "five plus one over ten, and E equal to two fifths.",
     "visual": {"style": "coefficients", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Integrate the linear part first: that is one fifth of the logarithm "
     "of the absolute value of x plus one. For each quadratic, split the "
     "numerator into a multiple of the derivative two x plus alpha, plus a "
     "constant. The derivative part integrates to a logarithm with "
     "coefficient B over two, and the constant part feeds the arctangent "
     "integral. The constants work out to five plus root five over twenty "
     "and five minus root five over twenty.",
     "visual": {"style": "log parts", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "For the arctangent pieces, complete the square. x squared plus alpha "
     "x plus one is x plus alpha over two squared, plus five plus root "
     "five over eight. Likewise for beta, the constant is five minus root "
     "five over eight. Each integral is one over d times arctangent of x "
     "plus c over d. Multiplying the coefficients through, the two "
     "arctangent weights are root of ten plus two root five, over ten, and "
     "root of ten minus two root five, over ten.",
     "visual": {"style": "arctan parts", "transition": "fade"},
     "code": SEG3},
    {"narration":
     "Assemble the answer. The integral is one fifth of ln of one plus x, "
     "plus root five minus one over twenty times the log of the first "
     "quadratic, minus root five plus one over twenty times the log of the "
     "second, plus the two arctangent terms with the weights just found, "
     "and a constant. Here alpha is root five minus one over two and beta "
     "is minus root five plus one over two. A quick check: the "
     "antiderivative evaluated at zero is zero, and its derivative there "
     "is one fifth plus two fifths plus two fifths, which is one, "
     "exactly the integrand value.",
     "visual": {"style": "final answer", "transition": "fade"},
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
