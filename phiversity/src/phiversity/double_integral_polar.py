TITLE = "Q14 - A DOUBLE INTEGRAL BETWEEN TWO CIRCLES"

QUESTION = {
    "display":
        "Evaluate the double integral over x from 0 to 1 and y from "
        "sqrt(x - x^2) to sqrt(1 - x^2) of "
        "xy exp(-(x^2 + y^2)) / (x^2 + y^2) dy dx.",
    "speech":
        "Evaluate the double integral, over x from zero to one, and y from "
        "the square root of x minus x squared, up to the square root of "
        "one minus x squared, of x y, times e to the power minus x squared "
        "plus y squared, divided by x squared plus y squared. The two "
        "curved limits are circles, so polar coordinates are the natural "
        "choice.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 14 - DOUBLE INTEGRAL", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"\int_{0}^{1}\!\!\int_{\sqrt{x-x^{2}}}^{\sqrt{1-x^{2}}}"
            r"\frac{xy\,e^{-(x^{2}+y^{2})}}{x^{2}+y^{2}}\,dy\,dx",
            font_size=34, color=T.constant)
        c_chem = Text("LIMITS", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "y = sqrt(1 - x^2): circle r = 1\n"
            "y = sqrt(x - x^2): circle r = cos(theta)",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("POLAR FORM", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "integrand x dy dx\n"
            "= sin(theta)cos(theta) e^(-r^2) r dr dtheta",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("ANSWER", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "(e - 2) / (4e)\n"
            "about 0.066",
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
        head = Text("Q14 - PICTURE THE REGION", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        axes = Axes(x_range=[0, 1.15, 0.25], y_range=[0, 1.15, 0.25],
                    x_length=4.6, y_length=4.0,
                    axis_config={"color": T.text_muted, "stroke_width": 1.5,
                                 "include_tip": False})
        axes.move_to(LEFT * 3.4 + DOWN * 0.5)
        outer = axes.plot(lambda x: np.sqrt(np.maximum(1 - x * x, 0)),
                          x_range=[0, 1], color=T.graph_function, stroke_width=4)
        inner = axes.plot(lambda x: np.sqrt(np.maximum(x - x * x, 0)),
                          x_range=[0, 1], color=T.graph_reference, stroke_width=4)
        xs = np.linspace(0.0, 1.0, 140)
        lo = np.sqrt(np.maximum(xs - xs * xs, 0))
        up = np.sqrt(np.maximum(1 - xs * xs, 0))
        pts = [axes.c2p(x, y) for x, y in zip(xs, lo)]
        pts += [axes.c2p(x, y) for x, y in zip(xs[::-1], up[::-1])]
        region = Polygon(*pts)
        region.set_fill(T.cancel_mark, opacity=0.28)
        region.set_stroke(width=0)
        l1 = MathTex(r"r=1", font_size=24, color=T.graph_function)
        l1.next_to(axes.c2p(0.62, 0.79), UP, buff=0.12)
        l2 = MathTex(r"r=\cos\theta", font_size=24, color=T.graph_reference)
        l2.next_to(axes.c2p(0.30, 0.42), LEFT, buff=0.1)
        t1 = Text("outer boundary: x^2 + y^2 = 1", font_size=22,
                  color=T.graph_function)
        t2 = Text("inner boundary: (x - 1/2)^2 + y^2 = 1/4", font_size=22,
                  color=T.graph_reference)
        t3 = Text("shaded region: r from cos(theta) to 1", font_size=22,
                  color=T.cancel_mark)
        texts = VGroup(t1, t2, t3).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        fit_width(texts, 6.3)
        texts.move_to(RIGHT * 3.5 + DOWN * 0.2)
        self.play(Create(axes), run_time=1.0)
        self.play(FadeIn(region), run_time=1.0)
        self.play(Create(outer), Create(inner), run_time=1.8)
        self.play(Write(l1), Write(l2), run_time=1.0)
        self.play(FadeIn(t1, shift=0.15 * UP), run_time=0.9)
        self.wait(1.8)
        self.play(FadeIn(t2, shift=0.15 * UP), run_time=0.9)
        self.wait(1.8)
        self.play(FadeIn(t3, shift=0.15 * UP), run_time=0.9)
        self.wait(3.2)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q14 - SWITCH TO POLAR", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"x=r\cos\theta,\quad y=r\sin\theta,\quad "
                     r"dx\,dy=r\,dr\,d\theta", font_size=30,
                     color=T.text_secondary)
        r2 = MathTex(r"x^{2}+y^{2}=r^{2}", font_size=30, color=T.text_primary)
        r3 = MathTex(r"\frac{xy\,e^{-(x^{2}+y^{2})}}{x^{2}+y^{2}}dx\,dy"
                     r"=\frac{r^{2}\sin\theta\cos\theta\,e^{-r^{2}}}{r^{2}}"
                     r"\,r\,dr\,d\theta", font_size=27, color=T.text_primary)
        r4 = MathTex(r"=\sin\theta\cos\theta\,e^{-r^{2}}\,r\,dr\,d\theta",
                     font_size=32, color=T.result_intermediate)
        r5 = MathTex(r"\int_{0}^{\pi/2}\!\!\int_{\cos\theta}^{1}"
                     r"\sin\theta\cos\theta\,e^{-r^{2}}\,r\,dr\,d\theta",
                     font_size=30, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.play(Write(r2), run_time=1.2)
        self.wait(2.4)
        self.play(Write(r3), run_time=2.0)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.5)
        box4 = SurroundingRectangle(r4, buff=0.14, color=T.result_intermediate)
        self.play(Create(box4), run_time=0.6)
        self.wait(2.8)
        self.play(Write(r5), run_time=1.8)
        self.wait(3.2)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q14 - THE RADIAL INTEGRAL", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\int_{\cos\theta}^{1}r\,e^{-r^{2}}dr"
                     r"=\left[-\frac{1}{2}e^{-r^{2}}\right]_{\cos\theta}^{1}",
                     font_size=30, color=T.text_primary)
        r2 = MathTex(r"=\frac{1}{2}\left(e^{-\cos^{2}\theta}-e^{-1}\right)",
                     font_size=33, color=T.result_final)
        r3 = Text("the inner integral leaves a function of theta only",
                  font_size=24, color=T.text_secondary)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        fit_width(rows, 11.4)
        rows.next_to(rule, DOWN, buff=0.7)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.6)
        box2 = SurroundingRectangle(r2, buff=0.16, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=0.9)
        self.wait(3.8)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.0)
        self.wait(3.4)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q14 - THE ANGULAR INTEGRAL", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"I=\frac{1}{2}\int_{0}^{\pi/2}\sin\theta\cos\theta"
                     r"\left(e^{-\cos^{2}\theta}-e^{-1}\right)d\theta",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"u=\cos^{2}\theta,\quad "
                     r"du=-2\sin\theta\cos\theta\,d\theta", font_size=29,
                     color=T.text_secondary)
        r3 = MathTex(r"\int_{0}^{\pi/2}\sin\theta\cos\theta\,"
                     r"e^{-\cos^{2}\theta}d\theta"
                     r"=\frac{1}{2}\int_{0}^{1}e^{-u}du"
                     r"=\frac{1}{2}\left(1-e^{-1}\right)",
                     font_size=27, color=T.text_primary)
        r4 = MathTex(r"\int_{0}^{\pi/2}\sin\theta\cos\theta\,d\theta"
                     r"=\frac{1}{2}", font_size=29, color=T.text_primary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.4)
        self.wait(2.4)
        self.play(Write(r3), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.6)
        self.wait(3.2)
        self.wait(6)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q14 - COMBINE THE PIECES", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"I=\frac{1}{2}\left[\frac{1}{2}\left(1-e^{-1}\right)"
                     r"-e^{-1}\cdot\frac{1}{2}\right]", font_size=32,
                     color=T.text_primary)
        r2 = MathTex(r"=\frac{1}{4}\left(1-2e^{-1}\right)", font_size=34,
                     color=T.text_primary)
        r3 = MathTex(r"I=\frac{e-2}{4e}", font_size=40, color=T.result_final)
        r4 = Text("numerically, (e - 2)/(4e) is about 0.066", font_size=24,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.48)
        fit_width(rows, 11.4)
        rows.next_to(rule, DOWN, buff=0.55)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.18, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.0)
        self.wait(3.4)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "First understand the region. The upper limit y equals the square "
     "root of one minus x squared is the unit circle, x squared plus y "
     "squared equals one. The lower limit y equals the square root of x "
     "minus x squared is the circle x minus one half squared plus y "
     "squared equals one quarter. In polar coordinates these become r "
     "equals one, and r equals cosine theta. So the shaded region runs "
     "from r equals cosine theta out to r equals one, with theta from zero "
     "to pi by two.",
     "visual": {"style": "region diagram", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Now convert the integrand. With x equal to r cosine theta and y "
     "equal to r sine theta, x squared plus y squared becomes r squared, "
     "and the area element dx dy becomes r dr d theta. The numerator xy "
     "becomes r squared sine theta cosine theta, and the exponential "
     "becomes e to the minus r squared. The r squared cancels, leaving "
     "sine theta cosine theta, e to the minus r squared, times r dr d "
     "theta.",
     "visual": {"style": "polar conversion", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Do the radial integral first. The integrand r e to the minus r "
     "squared has antiderivative minus one half e to the minus r squared. "
     "Evaluate from cosine theta to one. That gives one half, times e to "
     "the minus cosine squared theta, minus e to the minus one.",
     "visual": {"style": "radial integral", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "Now the theta integral. For the first piece, substitute u equals "
     "cosine squared theta, so du equals minus two sine theta cosine "
     "theta d theta. That integral becomes one half times the integral of "
     "e to the minus u from zero to one, which is one half times one minus "
     "e to the minus one. The second piece is just e to the minus one "
     "times the integral of sine theta cosine theta, which is one half.",
     "visual": {"style": "angular integral", "transition": "fade"},
     "code": SEG3},
    {"narration":
     "Assemble everything. We get one half, times one half times one minus "
     "e to the minus one, minus e to the minus one times one half. That "
     "simplifies to one quarter times one minus two e to the minus one, "
     "which is e minus two, over four e, approximately zero point zero six "
     "six.",
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
