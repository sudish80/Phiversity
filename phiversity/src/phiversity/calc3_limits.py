TITLE = "Q18 - TWO MULTIVARIABLE LIMITS"

QUESTION = {
    "display":
        "(1) Find lim(x,y)->(0,0) (x^2 + y^2) / "
        "(sqrt(x^2 + y^2 + 4) - 2). "
        "(2) Find lim(x,y)->(1,0) (2xy - 2y) / "
        "(x^2 + y^2 - 2x + 1).",
    "speech":
        "Part one. Find the limit as the point x, y tends to zero, zero, of "
        "x squared plus y squared, divided by the square root of x squared "
        "plus y squared plus four, minus two. Part two. Find the limit as "
        "x, y tends to one, zero, of two x y minus two y, divided by x "
        "squared plus y squared minus two x plus one.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 18 - MULTIVARIABLE LIMITS", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"\lim_{(x,y)\to(0,0)}\frac{x^{2}+y^{2}}"
            r"{\sqrt{x^{2}+y^{2}+4}-2}", font_size=32, color=T.constant)
        data2 = MathTex(
            r"\lim_{(x,y)\to(1,0)}\frac{2xy-2y}"
            r"{x^{2}+y^{2}-2x+1}", font_size=32, color=T.constant)
        c_chem = Text("PART 1", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "rationalise the denominator;\n"
            "the singularity cancels",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("PART 2", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "centre u = x - 1, v = y\n"
            "then the denominator is u^2 + v^2",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("ANSWERS", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "part 1: 4\n"
            "part 2: does not exist",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, data2, chem, maths, econ).arrange(
            DOWN, aligned_edge=LEFT, buff=0.3)
        rows.move_to(UP * 0.1)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=1.8)
        self.wait(3.0)
        self.play(Write(data2), run_time=1.8)
        self.wait(3.5)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(4.0)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(4.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(5.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.61).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q18 - PART 1: RATIONALISE", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"L=\lim_{(x,y)\to(0,0)}\frac{x^{2}+y^{2}}"
                     r"{\sqrt{x^{2}+y^{2}+4}-2}", font_size=31,
                     color=T.text_primary)
        r2 = MathTex(r"=\lim\frac{(x^{2}+y^{2})"
                     r"\left(\sqrt{x^{2}+y^{2}+4}+2\right)}"
                     r"{\left(x^{2}+y^{2}+4\right)-4}", font_size=29,
                     color=T.text_primary)
        r3 = MathTex(r"=\lim\frac{(x^{2}+y^{2})"
                     r"\left(\sqrt{x^{2}+y^{2}+4}+2\right)}"
                     r"{x^{2}+y^{2}}", font_size=30, color=T.text_primary)
        r4 = Text("multiply above and below by the conjugate", font_size=23,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r2), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.8)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.0)
        self.wait(3.2)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q18 - PART 1: CANCEL AND SUBSTITUTE", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"L=\lim_{(x,y)\to(0,0)}"
                     r"\left(\sqrt{x^{2}+y^{2}+4}+2\right)",
                     font_size=32, color=T.text_primary)
        r2 = MathTex(r"=\sqrt{4}+2=2+2=4", font_size=34,
                     color=T.text_primary)
        r3 = MathTex(r"L=4", font_size=42, color=T.result_final)
        r4 = Text("the x^2 + y^2 factor cancels exactly", font_size=24,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        fit_width(rows, 11.0)
        rows.next_to(rule, DOWN, buff=0.6)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.5)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.4)
        box3 = SurroundingRectangle(r3, buff=0.2, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.0)
        self.wait(3.4)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q18 - PART 2: SHIFT THE ORIGIN", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"u=x-1,\qquad v=y", font_size=32,
                     color=T.text_secondary)
        r2 = MathTex(r"2xy-2y=2y(x-1)=2vu", font_size=31,
                     color=T.text_primary)
        r3 = MathTex(r"x^{2}+y^{2}-2x+1=(x-1)^{2}+y^{2}=u^{2}+v^{2}",
                     font_size=31, color=T.text_primary)
        r4 = MathTex(r"\lim_{(u,v)\to(0,0)}\frac{2uv}{u^{2}+v^{2}}",
                     font_size=33, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 11.8)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.5)
        self.wait(2.4)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.6)
        box4 = SurroundingRectangle(r4, buff=0.15, color=T.result_intermediate)
        self.play(Create(box4), run_time=0.7)
        self.wait(3.6)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q18 - PART 2: TWO PATHS, TWO ANSWERS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{path }v=0:\quad "
                     r"\frac{2u(0)}{u^{2}+0}=0", font_size=30,
                     color=T.text_primary)
        r2 = MathTex(r"\text{path }v=u:\quad "
                     r"\frac{2u^{2}}{u^{2}+u^{2}}=\frac{2u^{2}}{2u^{2}}=1",
                     font_size=30, color=T.text_primary)
        r3 = MathTex(r"0\ne1\quad\Rightarrow\quad "
                     r"\text{the limit does not exist}", font_size=33,
                     color=T.result_final)
        r4 = Text("different paths give different limiting values, so the "
                  "limit fails to exist", font_size=23, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.16, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.0)
        self.wait(3.6)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "For the first limit, the square root is what makes it look "
     "indeterminate, so rationalise. Multiply numerator and denominator by "
     "the conjugate, square root of x squared plus y squared plus four, "
     "plus two. The denominator becomes x squared plus y squared plus four, "
     "minus four, which is exactly x squared plus y squared. That cancels "
     "the numerator.",
     "visual": {"style": "rationalise", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "After cancelling, we are left with the square root of x squared plus "
     "y squared plus four, plus two. Now let x and y tend to zero. The "
     "square root tends to the square root of four, which is two, and "
     "adding two gives four. So the first limit is four.",
     "visual": {"style": "first answer", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "For the second limit, shift the origin to one, zero. Set u equals x "
     "minus one and v equals y. The numerator two x y minus two y factors "
     "as two y times x minus one, which is two v u. The denominator x "
     "squared minus two x plus one plus y squared is simply u squared plus "
     "v squared. So the limit becomes two u v over u squared plus v "
     "squared, as u and v tend to zero.",
     "visual": {"style": "shift origin", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "Now test paths. Along v equals zero the expression is zero for every "
     "nonzero u, so the limit along that path is zero. Along v equals u the "
     "expression is two u squared over two u squared, which is one. Two "
     "different paths give two different values, zero and one. Therefore "
     "the second limit does not exist.",
     "visual": {"style": "path dependence", "transition": "fade"},
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
