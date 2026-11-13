TITLE = "Q15 - A DIFFERENTIAL EQUATION WITH A FUNCTION phi"

QUESTION = {
    "display":
        "Let y and phi be differentiable on (0, inf) with "
        "y' phi - y phi' + y^2 = 0, y(1) = 1, phi(1) = 0, phi(2) = 4. "
        "(a) Find y(2). "
        "(b) Evaluate the integral from 1 to 2 of "
        "(phi/y) / (x^2 sqrt(x^2 + (phi/y)^2)) dx.",
    "speech":
        "Let y and phi be differentiable functions with y prime times phi, "
        "minus y times phi prime, plus y squared, equal to zero. We are "
        "given y of one equals one, phi of one equals zero, and phi of two "
        "equals four. Part a: find y of two. Part b: evaluate the integral "
        "from one to two of phi over y, divided by x squared times the "
        "square root of x squared plus phi over y squared.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 15 - DIFFERENTIAL EQUATION", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"y'\phi-y\phi'+y^{2}=0,\quad y(1)=1,\quad "
            r"\phi(1)=0,\quad \phi(2)=4",
            font_size=29, color=T.constant)
        c_chem = Text("KEY IDENTITY", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "y' phi - y phi' = -y^2 (phi/y)'\n"
            "so the equation says (phi/y)' = 1",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("PART (a)", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "phi/y = x - 1, so y = phi/(x - 1)\n"
            "y(2) = phi(2)/1 = 4",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("PART (b)", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "substitute t = (phi/y)/x\n"
            "integral = (sqrt5 - 2)/2",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, chem, maths, econ).arrange(DOWN, aligned_edge=LEFT,
                                                       buff=0.32)
        rows.move_to(UP * 0.15)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=2.2)
        self.wait(5.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.61).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q15 - SPOT THE DERIVATIVE", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"y'\phi-y\phi'+y^{2}=0", font_size=34,
                     color=T.text_primary)
        r2 = MathTex(r"\left(\frac{\phi}{y}\right)'"
                     r"=\frac{\phi'y-\phi y'}{y^{2}}"
                     r"=\frac{\phi'}{y}-\frac{\phi y'}{y^{2}}",
                     font_size=32, color=T.text_secondary)
        r3 = MathTex(r"\frac{y'\phi-y\phi'}{y^{2}}"
                     r"=-\left(\frac{\phi}{y}\right)'", font_size=32,
                     color=T.text_primary)
        r4 = MathTex(r"-\left(\frac{\phi}{y}\right)'+1=0"
                     r"\quad\Rightarrow\quad"
                     r"\left(\frac{\phi}{y}\right)'=1", font_size=33,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        fit_width(rows, 11.8)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.5)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.8)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.5)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.8)
        box4 = SurroundingRectangle(r4, buff=0.16, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q15 - INTEGRATE AND USE THE DATA", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\frac{\phi}{y}=x+C", font_size=34,
                     color=T.text_primary)
        r2 = MathTex(r"x=1:\quad \frac{\phi(1)}{y(1)}=\frac{0}{1}=0"
                     r"\quad\Rightarrow\quad 0=1+C", font_size=30,
                     color=T.text_primary)
        r3 = MathTex(r"C=-1", font_size=32, color=T.result_intermediate)
        r4 = MathTex(r"\frac{\phi}{y}=x-1\quad\Rightarrow\quad "
                     r"y=\frac{\phi}{x-1}", font_size=34,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        fit_width(rows, 11.4)
        rows.next_to(rule, DOWN, buff=0.55)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.8)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.3)
        self.wait(2.2)
        self.play(Write(r4), run_time=1.7)
        box4 = SurroundingRectangle(r4, buff=0.16, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        self.wait(3.8)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q15 - PART (a): FIND y(2)", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"y(x)=\frac{\phi(x)}{x-1}", font_size=34,
                     color=T.text_primary)
        r2 = MathTex(r"y(2)=\frac{\phi(2)}{2-1}=\frac{4}{1}=4",
                     font_size=36, color=T.text_primary)
        r3 = MathTex(r"y(2)=4", font_size=42, color=T.result_final)
        r4 = Text("the value phi(2) = 4 is exactly what part (a) needs",
                  font_size=24, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        fit_width(rows, 10.8)
        rows.next_to(rule, DOWN, buff=0.65)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.5)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.4)
        box3 = SurroundingRectangle(r3, buff=0.2, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.0)
        self.wait(3.4)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q15 - PART (b): SET UP THE INTEGRAL", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"I=\int_{1}^{2}\frac{\phi/y}{x^{2}"
                     r"\sqrt{x^{2}+(\phi/y)^{2}}}\,dx", font_size=30,
                     color=T.text_primary)
        r2 = MathTex(r"\frac{\phi}{y}=x-1", font_size=30, color=T.text_secondary)
        r3 = MathTex(r"t=\frac{\phi/y}{x}=\frac{x-1}{x}=1-\frac{1}{x}",
                     font_size=32, color=T.result_intermediate)
        r4 = MathTex(r"x=\frac{1}{1-t},\quad dx=\frac{dt}{(1-t)^{2}},\quad "
                     r"x^{2}+(\phi/y)^{2}=\frac{1+t^{2}}{(1-t)^{2}}",
                     font_size=28, color=T.text_primary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 11.8)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.3)
        self.wait(2.4)
        self.play(Write(r3), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r4), run_time=2.0)
        self.wait(3.2)
        self.wait(6)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q15 - PART (b): SIMPLIFY AND EVALUATE", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"I=\int_{0}^{1/2}\frac{t}{\sqrt{1+t^{2}}}\,dt",
                     font_size=34, color=T.text_primary)
        r2 = MathTex(r"=\left[\sqrt{1+t^{2}}\right]_{0}^{1/2}",
                     font_size=34, color=T.text_primary)
        r3 = MathTex(r"=\frac{\sqrt{5}}{2}-1=\frac{\sqrt{5}-2}{2}",
                     font_size=38, color=T.result_final)
        r4 = Text("answers: y(2) = 4 and the integral is "
                  "(sqrt5 - 2)/2, about 0.118",
                  font_size=23, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        fit_width(rows, 11.2)
        rows.next_to(rule, DOWN, buff=0.55)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.5)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.18, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.0)
        self.wait(3.6)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "The whole problem turns on one identity. Divide the equation by y "
     "squared. The combination y prime phi minus y phi prime over y "
     "squared is minus the derivative of phi over y, because the quotient "
     "rule gives phi prime over y minus phi y prime over y squared. So the "
     "equation becomes minus the derivative of phi over y, plus one, equals "
     "zero. Therefore the derivative of phi over y is one.",
     "visual": {"style": "identity", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Integrate once. phi over y equals x plus a constant. Use the initial "
     "data at x equals one: phi of one is zero and y of one is one, so phi "
     "over y is zero at x equals one. Therefore zero equals one plus C, and "
     "C is minus one. We obtain phi over y equals x minus one, or "
     "equivalently y equals phi divided by x minus one.",
     "visual": {"style": "integrate", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Part a is now immediate. At x equals two, y of two equals phi of two "
     "divided by two minus one. Since phi of two is four, y of two is four "
     "over one, which is four.",
     "visual": {"style": "part a", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "For part b, write phi over y as x minus one. The natural substitution "
     "is t equals phi over y, divided by x, which is x minus one over x. "
     "Then x equals one over one minus t, dx is dt over one minus t "
     "squared, and x squared plus phi over y squared becomes one plus t "
     "squared, over one minus t squared.",
     "visual": {"style": "substitution", "transition": "fade"},
     "code": SEG3},
    {"narration":
     "Making the substitution, the integral collapses to t over the square "
     "root of one plus t squared, dt, with t running from zero to one half. "
     "The antiderivative is the square root of one plus t squared. At one "
     "half this is root five over two, and at zero it is one. So the "
     "integral is root five over two minus one, that is root five minus "
     "two, all over two.",
     "visual": {"style": "final evaluation", "transition": "fade"},
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
