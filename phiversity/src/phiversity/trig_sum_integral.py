TITLE = "Q11 - A TRIGONOMETRIC SUM INTEGRAL"

QUESTION = {
    "display":
        "Evaluate I = integral of "
        "(sin x + sin 3x + ... + sin 15x) / "
        "(cos x + cos 3x + ... + cos 15x) dx, "
        "using the factorisation formulae.",
    "speech":
        "Evaluate the integral of the quotient of two sums. The numerator "
        "is sine x plus sine three x, and so on up to sine fifteen x. The "
        "denominator is cosine x plus cosine three x, up to cosine fifteen "
        "x. Use the sum-to-product factorisation formulae.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 11 - TRIG SUM INTEGRAL", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"I=\int\frac{\sin x+\sin 3x+\cdots+\sin 15x}"
            r"{\cos x+\cos 3x+\cdots+\cos 15x}\,dx",
            font_size=34, color=T.constant)
        c_chem = Text("FACTORISE", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "pair symmetric angles:\n"
            "sin A + sin B = 2 sin((A+B)/2) cos((A-B)/2)\n"
            "cos A + cos B = 2 cos((A+B)/2) cos((A-B)/2)",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("KEY OBSERVATION", font_size=20,
                      color=T.highlight_secondary)
        r_math = Text(
            "every pair has midpoint 8x,\n"
            "so a common cos-sum factor cancels",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("ANSWER", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "I = integral tan(8x) dx\n"
            "= -(1/8) ln|cos 8x| + C",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, chem, maths, econ).arrange(DOWN, aligned_edge=LEFT,
                                                       buff=0.34)
        rows.move_to(UP * 0.2)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=2.2)
        self.wait(5.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(7.0)
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
        head = Text("Q11 - PAIR THE TERMS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"S=\sin x+\sin3x+\sin5x+\sin7x", font_size=30,
                     color=T.text_primary)
        r2 = MathTex(r"+\sin9x+\sin11x+\sin13x+\sin15x", font_size=30,
                     color=T.text_primary)
        r3 = MathTex(r"\sin A+\sin B=2\sin\frac{A+B}{2}\cos\frac{A-B}{2}",
                     font_size=29, color=T.text_secondary)
        r4 = MathTex(r"x\leftrightarrow15x,\ 3x\leftrightarrow13x,"
                     r"\ 5x\leftrightarrow11x,\ 7x\leftrightarrow9x",
                     font_size=27, color=T.result_intermediate)
        r5 = MathTex(r"S=2\sin8x\left(\cos x+\cos3x+\cos5x+\cos7x\right)",
                     font_size=31, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 11.8)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.4)
        self.play(Write(r2), run_time=1.4)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.5)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.5)
        self.wait(3.0)
        self.play(Write(r5), run_time=1.8)
        box5 = SurroundingRectangle(r5, buff=0.15, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q11 - THE SAME TRICK ON THE DENOMINATOR", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"C=\cos x+\cos3x+\cos5x+\cos7x", font_size=30,
                     color=T.text_primary)
        r2 = MathTex(r"+\cos9x+\cos11x+\cos13x+\cos15x", font_size=30,
                     color=T.text_primary)
        r3 = MathTex(r"\cos A+\cos B=2\cos\frac{A+B}{2}\cos\frac{A-B}{2}",
                     font_size=29, color=T.text_secondary)
        r4 = MathTex(r"C=2\cos8x\left(\cos x+\cos3x+\cos5x+\cos7x\right)",
                     font_size=31, color=T.result_final)
        r5 = Text("the bracket is exactly the factor that appeared in S",
                  font_size=24, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.4)
        self.play(Write(r2), run_time=1.4)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.5)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.8)
        box4 = SurroundingRectangle(r4, buff=0.15, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        self.wait(3.0)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.0)
        self.wait(3.6)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q11 - THE QUOTIENT COLLAPSES", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\frac{S}{C}="
                     r"\frac{2\sin8x\left(\cos x+\cdots+\cos7x\right)}"
                     r"{2\cos8x\left(\cos x+\cdots+\cos7x\right)}",
                     font_size=32, color=T.text_primary)
        r2 = MathTex(r"=\frac{\sin8x}{\cos8x}=\tan8x", font_size=34,
                     color=T.result_intermediate)
        r3 = MathTex(r"I=\int\tan8x\,dx", font_size=34, color=T.text_primary)
        r4 = MathTex(r"I=-\frac{1}{8}\ln\left|\cos8x\right|+C", font_size=36,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        fit_width(rows, 11.6)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.0)
        strike_through(self, VGroup(r1[0][0:2], r1[0][-2:]), run_time=0.8)
        self.wait(1.5)
        self.play(Write(r2), run_time=1.6)
        self.wait(3.2)
        self.play(Write(r3), run_time=1.4)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.6)
        box4 = SurroundingRectangle(r4, buff=0.18, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=1.0)
        self.wait(4.2)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q11 - WHY IT WORKS IN GENERAL", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("Odd angles 1, 3, 5, ..., (2m-1) are symmetric about m:",
                  font_size=25, color=T.text_primary)
        r2 = MathTex(r"(2k-1)+(2m-2k+1)=2m", font_size=30,
                     color=T.text_primary)
        r3 = MathTex(r"S=2\sin(mx)\sum\cos((2k-1)x)", font_size=31,
                     color=T.result_intermediate)
        r4 = MathTex(r"C=2\cos(mx)\sum\cos((2k-1)x)", font_size=31,
                     color=T.result_intermediate)
        r5 = MathTex(r"\Rightarrow \frac{S}{C}=\tan(mx)", font_size=34,
                     color=T.result_final)
        r6 = MathTex(r"\int\tan(mx)\,dx=-\frac{1}{m}\ln|\cos(mx)|+C",
                     font_size=31, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 11.8)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(FadeIn(r1, shift=0.2 * UP), run_time=1.3)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.4)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.5)
        self.play(Write(r4), run_time=1.5)
        self.wait(3.0)
        self.play(Write(r5), run_time=1.5)
        self.wait(2.8)
        self.play(Write(r6), run_time=1.6)
        box6 = SurroundingRectangle(r6, buff=0.16, color=T.result_final)
        self.play(Create(box6), run_time=0.7)
        self.wait(4.0)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Look at the numerator first. There are eight sine terms, with odd "
     "angles from x up to fifteen x. Pair each term with the one whose "
     "angle adds to sixteen x: x with fifteen x, three x with thirteen x, "
     "five x with eleven x, and seven x with nine x. Using sine A plus "
     "sine B equals two sine of the average times cosine of the "
     "half-difference, every pair has the common factor sine of eight x. "
     "So the numerator is two sine eight x, times the sum of cosines from "
     "x to seven x.",
     "visual": {"style": "numerator pairing", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Do exactly the same with the denominator. Using cosine A plus cosine "
     "B equals two cosine of the average times cosine of the "
     "half-difference, the same pairing produces two cosine eight x, times "
     "the very same bracket of cosines. The bracket is identical in the "
     "numerator and the denominator.",
     "visual": {"style": "denominator pairing", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Now divide. The common factor, two times the cosine bracket, cancels "
     "completely, leaving sine eight x over cosine eight x, which is tan "
     "eight x. The integral of tan eight x is minus one eighth, times the "
     "natural logarithm of the absolute value of cosine eight x, plus a "
     "constant.",
     "visual": {"style": "quotient and integral", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "The same argument works for any odd angular progression symmetric "
     "about m. The numerator is two sine m x times the cosine sum, and the "
     "denominator is two cosine m x times the same cosine sum. Their ratio "
     "is tan m x, and its integral is minus one over m, times ln of the "
     "absolute value of cosine m x, plus a constant. Here m equals eight, "
     "which gives our answer.",
     "visual": {"style": "generalisation", "transition": "fade"},
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
