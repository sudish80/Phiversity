TITLE = "Q12 - A DETERMINANT LIMIT"

QUESTION = {
    "display":
        "Let L = lim(n->inf) (1/n^4) times the sum from r=1 to n of "
        "det [[r(r-1), 2(r+2), 2026], [r, 1, -6], [r^2, 4r, 0]]. "
        "Find L.",
    "speech":
        "Let L be the limit, as n tends to infinity, of one over n to the "
        "fourth, times the sum from r equals one to n of a three by three "
        "determinant. The first row is r times r minus one, two times r "
        "plus two, and 2026. The second row is r, one, minus six. The "
        "third row is r squared, four r, zero. Find the limit L.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 12 - DETERMINANT LIMIT", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"L=\lim_{n\to\infty}\frac{1}{n^{4}}\sum_{r=1}^{n}"
            r"\det\begin{pmatrix}r(r-1)&2(r+2)&2026\\"
            r"r&1&-6\\ r^{2}&4r&0\end{pmatrix}",
            font_size=32, color=T.constant)
        c_chem = Text("STEP 1", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "expand the determinant;\n"
            "it is a polynomial in r",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("STEP 2", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "det = 12 r^3 + 6030 r^2\n"
            "sum with standard power-sum formulae",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("STEP 3", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "only the n^4 term survives\n"
            "after dividing by n^4",
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
        self.wait(6.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(5.0)
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
        head = Text("Q12 - EXPAND THE DETERMINANT", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        mat = MathTex(
            r"D_r=\det\begin{pmatrix}r(r-1)&2(r+2)&2026\\"
            r"r&1&-6\\ r^{2}&4r&0\end{pmatrix}",
            font_size=30, color=T.text_primary)
        r1 = MathTex(
            r"=r(r-1)\bigl(0-(-6)(4r)\bigr)"
            r"-2(r+2)\bigl(r\cdot0-(-6)r^{2}\bigr)",
            font_size=27, color=T.text_primary)
        r2 = MathTex(
            r"+2026\bigl(r\cdot4r-1\cdot r^{2}\bigr)",
            font_size=27, color=T.text_primary)
        r3 = Text("expand by the first row", font_size=23,
                  color=T.text_secondary)
        rows = VGroup(mat, r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(mat), run_time=2.0)
        self.wait(3.5)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.6)
        self.wait(3.0)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=0.9)
        self.wait(3.0)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q12 - SIMPLIFY THE POLYNOMIAL", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"=r(r-1)(24r)-2(r+2)(6r^{2})+2026(3r^{2})",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"=24r^{2}(r-1)-12r^{2}(r+2)+6078r^{2}",
                     font_size=29, color=T.text_primary)
        r3 = MathTex(r"=24r^{3}-24r^{2}-12r^{3}-24r^{2}+6078r^{2}",
                     font_size=28, color=T.text_primary)
        r4 = MathTex(r"D_r=12r^{3}+6030r^{2}", font_size=34,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 11.8)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.6)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.6)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.6)
        box4 = SurroundingRectangle(r4, buff=0.16, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.8)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q12 - SUM OVER r", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\sum_{r=1}^{n}r^{2}=\frac{n(n+1)(2n+1)}{6},\quad"
                     r"\sum_{r=1}^{n}r^{3}=\frac{n^{2}(n+1)^{2}}{4}",
                     font_size=28, color=T.text_secondary)
        r2 = MathTex(r"\sum_{r=1}^{n}D_r"
                     r"=12\cdot\frac{n^{2}(n+1)^{2}}{4}"
                     r"+6030\cdot\frac{n(n+1)(2n+1)}{6}",
                     font_size=28, color=T.text_primary)
        r3 = MathTex(r"=3n^{2}(n+1)^{2}+1005\,n(n+1)(2n+1)",
                     font_size=29, color=T.text_primary)
        r4 = Text("expand only the leading powers of n", font_size=23,
                  color=T.text_secondary)
        r5 = MathTex(r"=3n^{4}+2010n^{3}+\cdots", font_size=30,
                     color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.8)
        self.wait(3.2)
        self.play(Write(r3), run_time=1.5)
        self.wait(3.0)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=0.9)
        self.wait(2.4)
        self.play(Write(r5), run_time=1.5)
        box5 = SurroundingRectangle(r5, buff=0.15, color=T.result_intermediate)
        self.play(Create(box5), run_time=0.7)
        self.wait(3.6)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q12 - TAKE THE LIMIT", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"L=\lim_{n\to\infty}\frac{3n^{4}+2010n^{3}+\cdots}{n^{4}}",
                     font_size=32, color=T.text_primary)
        r2 = MathTex(r"=\lim_{n\to\infty}\left(3+\frac{2010}{n}+\cdots\right)",
                     font_size=32, color=T.text_primary)
        r3 = MathTex(r"L=3", font_size=40, color=T.result_final)
        r4 = Text("lower-order terms vanish as n grows without bound",
                  font_size=24, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        fit_width(rows, 11.6)
        rows.next_to(rule, DOWN, buff=0.6)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.6)
        self.wait(3.2)
        self.play(Write(r3), run_time=1.4)
        box3 = SurroundingRectangle(r3, buff=0.2, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=0.9)
        self.wait(3.4)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Expand the determinant along the first row. The first minor is one "
     "times zero minus minus six times four r, giving twenty-four r. The "
     "second minor is r times zero minus minus six times r squared, giving "
     "six r squared. The third minor is r times four r minus one times r "
     "squared, giving three r squared. Multiply each minor by its "
     "cofactor from the first row.",
     "visual": {"style": "determinant expansion", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Now simplify. The first term gives twenty-four r squared times r "
     "minus one. The second gives minus twelve r squared times r plus two. "
     "The third gives six thousand and seventy-eight r squared. Collecting "
     "like powers, the determinant is twelve r cubed plus six thousand and "
     "thirty r squared.",
     "visual": {"style": "polynomial", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Sum from r equals one to n. Use the standard sums of squares and "
     "cubes. The sum of r cubed gives n squared times n plus one squared "
     "over four, and the sum of r squared gives n times n plus one times "
     "two n plus one over six. The total is three n squared times n plus "
     "one squared, plus one thousand and five n times n plus one times two "
     "n plus one. Expanding, the leading term is three n to the fourth, "
     "plus two thousand and ten n cubed, and lower powers.",
     "visual": {"style": "power sums", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "Finally, divide by n to the fourth and let n tend to infinity. Every "
     "term except the leading three n to the fourth contains a positive "
     "power of n in the denominator, so it vanishes. The limit L is "
     "three.",
     "visual": {"style": "limit", "transition": "fade"},
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
