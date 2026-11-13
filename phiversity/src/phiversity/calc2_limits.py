TITLE = "Q17 - TWO CALCULUS LIMITS: NESTED LIMIT AND A TELESCOPING SUM"

QUESTION = {
    "display":
        "(1) Find lim(n->inf) lim(x->0) "
        "(1 + sum_{k=1}^{n} sin^2(kx))^{1/(n^3 x^2)}. "
        "(2) Let x_1 > 0 and x_{n+1} = x_n + 4. If "
        "sum_{k=1}^{inf} 1/(x_{k+1} x_{k+2}) = 1/24, find x_1.",
    "speech":
        "Part one. Find the limit as n tends to infinity, of the limit as "
        "x tends to zero, of one plus the sum from k equals one to n of "
        "sine squared k x, all raised to the power one over n cubed x "
        "squared. Part two. Let x one be positive, and x n plus one equals "
        "x n plus four. If the infinite sum of one over x k plus one times "
        "x k plus two equals one over twenty-four, find x one.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 17 - TWO CALCULUS PROBLEMS", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"\lim_{n\to\infty}\lim_{x\to0}"
            r"\left(1+\sum_{k=1}^{n}\sin^{2}(kx)\right)^{\frac{1}{n^{3}x^{2}}}",
            font_size=31, color=T.constant)
        data2 = MathTex(
            r"x_{n+1}=x_{n}+4,\qquad "
            r"\sum_{k=1}^{\infty}\frac{1}{x_{k+1}x_{k+2}}=\frac{1}{24}",
            font_size=30, color=T.constant)
        c_chem = Text("PART 1", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "sum sin^2(kx) ~ x^2 sum k^2\n"
            "take logarithms",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("PART 2", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "the terms are an arithmetic progression\n"
            "telescope with difference 4",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("ANSWERS", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "part 1: e^(1/3)\n"
            "part 2: x_1 = 2",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, data2, chem, maths, econ).arrange(
            DOWN, aligned_edge=LEFT, buff=0.3)
        rows.move_to(UP * 0.1)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=2.0)
        self.wait(3.5)
        self.play(Write(data2), run_time=1.8)
        self.wait(4.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(4.0)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(4.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(5.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.6).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q17 - PART 1: THE INNER LIMIT", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"L_n=\lim_{x\to0}\left(1+\sum_{k=1}^{n}"
                     r"\sin^{2}(kx)\right)^{\frac{1}{n^{3}x^{2}}}",
                     font_size=30, color=T.text_primary)
        r2 = MathTex(r"\sin(kx)=kx+O(x^{3})", font_size=30,
                     color=T.text_secondary)
        r3 = MathTex(r"\sum_{k=1}^{n}\sin^{2}(kx)=x^{2}\sum_{k=1}^{n}k^{2}"
                     r"+o(x^{2})", font_size=30, color=T.text_primary)
        r4 = MathTex(r"\sum_{k=1}^{n}k^{2}=\frac{n(n+1)(2n+1)}{6}",
                     font_size=31, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 11.8)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.4)
        self.wait(2.4)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.6)
        box4 = SurroundingRectangle(r4, buff=0.15, color=T.result_intermediate)
        self.play(Create(box4), run_time=0.7)
        self.wait(3.6)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q17 - PART 1: LOGARITHM AND OUTER LIMIT", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\ln L_n=\lim_{x\to0}\frac{\ln\left(1+x^{2}S_2"
                     r"+o(x^{2})\right)}{n^{3}x^{2}}", font_size=28,
                     color=T.text_primary)
        r2 = MathTex(r"=\frac{S_2}{n^{3}},\qquad S_2=\sum_{k=1}^{n}k^{2}",
                     font_size=30, color=T.text_primary)
        r3 = MathTex(r"L_n=e^{S_2/n^{3}}", font_size=32,
                     color=T.result_intermediate)
        r4 = MathTex(r"\lim_{n\to\infty}\frac{S_2}{n^{3}}"
                     r"=\lim_{n\to\infty}\frac{n(n+1)(2n+1)}{6n^{3}}"
                     r"=\frac{1}{3}", font_size=29, color=T.text_primary)
        r5 = MathTex(r"L=e^{1/3}", font_size=40, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.5)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.4)
        self.wait(2.4)
        self.play(Write(r4), run_time=1.8)
        self.wait(3.0)
        self.play(Write(r5), run_time=1.5)
        box5 = SurroundingRectangle(r5, buff=0.18, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q17 - PART 2: TELESCOPING", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"x_{n}=x_{1}+4(n-1)", font_size=32,
                     color=T.text_primary)
        r2 = MathTex(r"x_{k+2}-x_{k+1}=4", font_size=30,
                     color=T.text_secondary)
        r3 = MathTex(r"\frac{1}{x_{k+1}x_{k+2}}"
                     r"=\frac{1}{4}\left(\frac{1}{x_{k+1}}"
                     r"-\frac{1}{x_{k+2}}\right)", font_size=31,
                     color=T.result_intermediate)
        r4 = MathTex(r"\sum_{k=1}^{n}\frac{1}{x_{k+1}x_{k+2}}"
                     r"=\frac{1}{4}\left(\frac{1}{x_{2}}"
                     r"-\frac{1}{x_{n+2}}\right)", font_size=30,
                     color=T.text_primary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 11.8)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.4)
        self.wait(2.4)
        self.play(Write(r3), run_time=1.7)
        box3 = SurroundingRectangle(r3, buff=0.15, color=T.result_intermediate)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.7)
        self.wait(3.2)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q17 - PART 2: FIND x_1", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"n\to\infty:\quad x_{n+2}\to\infty"
                     r"\Rightarrow \frac{1}{x_{n+2}}\to0",
                     font_size=30, color=T.text_secondary)
        r2 = MathTex(r"\frac{1}{4x_{2}}=\frac{1}{24}"
                     r"\quad\Rightarrow\quad x_{2}=6", font_size=34,
                     color=T.text_primary)
        r3 = MathTex(r"x_{2}=x_{1}+4\quad\Rightarrow\quad x_{1}=2",
                     font_size=34, color=T.result_intermediate)
        r4 = MathTex(r"x_{1}=2", font_size=40, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        fit_width(rows, 10.8)
        rows.next_to(rule, DOWN, buff=0.55)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.5)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.4)
        box4 = SurroundingRectangle(r4, buff=0.2, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=1.0)
        self.wait(4.2)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Start with the inner limit. For small x, sine k x is approximately k "
     "x, so sine squared k x is approximately k squared x squared. Hence "
     "the sum is x squared times the sum of k squared, plus a smaller "
     "error. The sum of k squared from one to n is n times n plus one, "
     "times two n plus one, over six.",
     "visual": {"style": "inner limit", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Take the natural logarithm. Since log of one plus small is "
     "approximately the small quantity, the logarithm of the expression is "
     "x squared S two over n cubed x squared, which is S two over n cubed. "
     "So the inner limit is e to the S two over n cubed. Now let n go to "
     "infinity. S two over n cubed is n times n plus one times two n plus "
     "one, over six n cubed, which tends to one third. The nested limit is "
     "e to the one third.",
     "visual": {"style": "outer limit", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Part two. The recurrence x n plus one equals x n plus four is an "
     "arithmetic progression, so x n equals x one plus four n minus one. In "
     "particular, consecutive terms differ by four. Therefore one over x k "
     "plus one times x k plus two equals one quarter, times one over x k "
     "plus one minus one over x k plus two. The sum telescopes.",
     "visual": {"style": "telescoping", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "After telescoping, the partial sum is one quarter, times one over x "
     "two minus one over x n plus two. As n tends to infinity, x n plus two "
     "grows without bound, so the second term vanishes. We are given that "
     "the limit is one over twenty-four. Thus one over four x two equals "
     "one over twenty-four, so x two is six. Since x two equals x one plus "
     "four, x one equals two.",
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
