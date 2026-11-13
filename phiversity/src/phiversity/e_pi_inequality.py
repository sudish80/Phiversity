TITLE = "Q5 - PROVING e^pi > pi^e BY INTEGRATION"

QUESTION = {
    "display":
        "Using integration, show that e^pi > pi^e. Draw a neat, labelled "
        "diagram to support the proof (the graph of y = ln(x)/x), and "
        "verify the result numerically.",
    "speech":
        "Using integration, show that e to the power pi is greater than pi "
        "to the power e. Also draw the relevant diagram. Support the proof "
        "with a neat, labelled graph of y equals ln x over x, and verify "
        "the result numerically.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 5 - INEQUALITY BY INTEGRATION", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(r"e^{\pi}>\pi^{e}\ ?", font_size=36,
                       color=T.constant)
        c_chem = Text("GIVEN", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "compare e^pi and pi^e using an integral\n"
            "take ln:  pi ln e   vs   e ln pi",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("METHOD", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "F(t) = t - e ln t, with F(e) = 0\n"
            "F(pi) = integral(e..pi) of (1 - e/t) dt\n"
            "integrand >= 0  =>  F(pi) > 0  =>  e^pi > pi^e",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("RESULT", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "e^pi ~ 23.141  >  pi^e ~ 22.459\n"
            "diagram: y = ln x / x, maximum at x = e",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, chem, maths, econ).arrange(DOWN, aligned_edge=LEFT,
                                                       buff=0.34)
        rows.move_to(UP * 0.2)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=2.0)
        self.wait(1.82)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(2.54)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(3.27)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(2.54)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(1)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q5 - STEP 1: REFORMULATE THE INEQUALITY", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"e^{\pi}>\pi^{e}", font_size=38, color=T.variable)
        r2 = MathTex(r"\Longleftrightarrow\ \pi\ln e>e\ln\pi"
                     r"\quad(\ln\text{ is strictly increasing})",
                     font_size=30, color=T.text_primary)
        r3 = MathTex(r"\Longleftrightarrow\ \pi>e\ln\pi"
                     r"\quad(\ln e=1)",
                     font_size=30, color=T.text_primary)
        r4 = MathTex(r"\Longleftrightarrow\ \frac{\ln e}{e}"
                     r">\frac{\ln\pi}{\pi}",
                     font_size=33, color=T.result_intermediate)
        r5 = MathTex(r"\text{set }f(x)=\frac{\ln x}{x}:"
                     r"\quad\text{need }f(e)>f(\pi)",
                     font_size=30, color=T.text_primary)
        r6 = Text("but we must prove it by integration, not by slopes",
                  font_size=23, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 11.2)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.6)
        self.play(Write(r2), run_time=1.8)
        self.wait(3.8)
        self.play(Write(r3), run_time=1.4)
        self.wait(3.2)
        self.play(Write(r4), run_time=1.8)
        box4 = SurroundingRectangle(r4, buff=0.15, color=T.result_intermediate)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_intermediate, run_time=0.9)
        self.wait(4.0)
        self.play(Write(r5), run_time=1.4)
        self.wait(3.2)
        self.play(FadeIn(r6, shift=0.2 * UP), run_time=1.0)
        self.wait(3.0)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q5 - STEP 2: BUILD THE INTEGRAL", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"F(t)=t-e\ln t", font_size=36, color=T.constant)
        r2 = MathTex(r"F(e)=e-e\ln e=e-e=0", font_size=32,
                     color=T.text_primary)
        r3 = MathTex(r"F'(t)=1-\frac{e}{t}", font_size=34,
                     color=T.text_primary)
        r4 = MathTex(r"F(\pi)-F(e)=\int_{e}^{\pi}\left(1-\frac{e}{t}\right)dt",
                     font_size=32, color=T.result_intermediate)
        r5 = MathTex(r"\Rightarrow\ F(\pi)"
                     r"=\int_{e}^{\pi}\left(1-\frac{e}{t}\right)dt",
                     font_size=33, color=T.result_final)
        r6 = Text("the whole problem now rests on the sign of this area",
                  font_size=23, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 11.0)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.82)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.82)
        self.play(Write(r3), run_time=1.4)
        self.wait(2.49)
        self.play(Write(r4), run_time=1.8)
        self.wait(2.99)
        self.play(Write(r5), run_time=1.6)
        box5 = SurroundingRectangle(r5, buff=0.15, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=0.9)
        self.wait(2.99)
        self.play(FadeIn(r6, shift=0.2 * UP), run_time=1.0)
        self.wait(2.49)
        self.wait(4.98)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q5 - STEP 3: THE INTEGRAND IS NON-NEGATIVE", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{On }[e,\pi]:\quad t\ge e",
                     font_size=30, color=T.text_primary)
        r2 = MathTex(r"\Rightarrow\ \frac{e}{t}\le 1",
                     font_size=32, color=T.text_primary)
        r3 = MathTex(r"\Rightarrow\ 1-\frac{e}{t}\ge 0"
                     r"\quad(>0\ \text{for }t>e)",
                     font_size=30, color=T.text_primary)
        r4 = MathTex(r"\text{area under a non-negative curve is positive}",
                     font_size=28, color=T.text_secondary)
        r5 = MathTex(r"\Rightarrow\ F(\pi)>0", font_size=34,
                     color=T.result_final)
        left = VGroup(r1, r2, r3, r4, r5)
        left.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(left, 6.9)
        if left.height > 6.0:
            left.scale_to_fit_height(6.0)
        left.next_to(rule, DOWN, buff=0.5)
        left.align_to(rule, LEFT).shift(RIGHT * 0.4)
        e = np.e
        pi = np.pi
        axes = Axes(x_range=[0, 4.5, 1], y_range=[0, 0.5, 0.1],
                    x_length=4.4, y_length=2.9,
                    axis_config={"color": T.text_muted, "stroke_width": 1.5,
                                 "include_tip": False})
        axes.move_to(RIGHT * 3.9 + DOWN * 0.7)
        g = lambda t: 1.0 - e / t
        curve = axes.plot(g, x_range=[e, 4.3], color=T.graph_function,
                          stroke_width=4)
        xs = np.linspace(e, pi, 60)
        pts = [axes.c2p(x, 0.0) for x in xs]
        pts += [axes.c2p(x, g(x)) for x in xs[::-1]]
        area = Polygon(*pts)
        area.set_fill(T.result_intermediate, opacity=0.5)
        area.set_stroke(width=0)
        g_lab = MathTex(r"y=1-\frac{e}{t}", font_size=24,
                        color=T.graph_function)
        g_lab.next_to(axes, UP, buff=0.2)
        e_lab = MathTex(r"e", font_size=24, color=T.text_secondary)
        e_lab.next_to(axes.c2p(e, 0), DOWN, buff=0.1)
        pi_lab = MathTex(r"\pi", font_size=24, color=T.text_secondary)
        pi_lab.next_to(axes.c2p(pi, 0), DOWN, buff=0.1)
        area_lab = MathTex(r"F(\pi)=\text{area}>0", font_size=24,
                           color=T.result_final)
        area_lab.move_to(axes.c2p(3.55, 0.33))
        self.play(Write(r1), run_time=1.6)
        self.wait(1.89)
        self.play(Write(r2), run_time=1.4)
        self.wait(1.77)
        self.play(Write(r3), run_time=1.6)
        self.wait(2)
        self.play(Create(axes), Create(curve), Write(g_lab), run_time=1.8)
        self.play(FadeIn(area), Write(e_lab), Write(pi_lab),
                  Write(area_lab), run_time=1.2)
        self.wait(2)
        self.play(Write(r4), run_time=1.4)
        self.wait(1.65)
        self.play(Write(r5), run_time=1.4)
        box5 = SurroundingRectangle(r5, buff=0.15, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=0.9)
        self.wait(2.36)
        self.wait(3.53)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q5 - STEP 4: UNWIND TO THE ANSWER", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"F(\pi)>0\ \Rightarrow\ \pi-e\ln\pi>0",
                     font_size=32, color=T.text_primary)
        r2 = MathTex(r"\Rightarrow\ \pi>e\ln\pi",
                     font_size=32, color=T.text_primary)
        r3 = MathTex(r"\Rightarrow\ \pi\ln e>e\ln\pi",
                     font_size=32, color=T.text_primary)
        r4 = MathTex(r"\Rightarrow\ \ln\!\left(e^{\pi}\right)"
                     r">\ln\!\left(\pi^{e}\right)",
                     font_size=32, color=T.text_primary)
        r5 = MathTex(r"\Rightarrow\ e^{\pi}>\pi^{e}",
                     font_size=38, color=T.result_final)
        r6 = Text("exponentiation is strictly increasing, so the "
                  "direction is preserved", font_size=23,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 11.0)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.4)
        self.wait(2.35)
        self.play(Write(r2), run_time=1.2)
        self.wait(2.19)
        self.play(Write(r3), run_time=1.2)
        self.wait(2.19)
        self.play(Write(r4), run_time=1.4)
        self.wait(2.35)
        self.play(Write(r5), run_time=1.6)
        box5 = SurroundingRectangle(r5, buff=0.18, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=1.0)
        self.wait(3.13)
        self.play(FadeIn(r6, shift=0.2 * UP), run_time=1.0)
        self.wait(2.5)
        self.wait(4.69)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q5 - THE DIAGRAM: y = ln x / x", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"f(x)=\frac{\ln x}{x},\quad "
                     r"f'(x)=\frac{1-\ln x}{x^{2}}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"f'(x)=0\ \text{at }x=e\ \Rightarrow\ "
                     r"\text{maximum}",
                     font_size=28, color=T.text_primary)
        r3 = MathTex(r"f(e)=\frac{1}{e}\approx0.3679",
                     font_size=28, color=T.text_primary)
        r4 = MathTex(r"f(\pi)=\frac{\ln\pi}{\pi}\approx0.3644",
                     font_size=28, color=T.text_primary)
        r5 = MathTex(r"f(e)>f(\pi)\ \Rightarrow\ e^{\pi}>\pi^{e}",
                     font_size=30, color=T.result_final)
        left = VGroup(r1, r2, r3, r4, r5)
        left.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(left, 6.9)
        if left.height > 6.0:
            left.scale_to_fit_height(6.0)
        left.next_to(rule, DOWN, buff=0.5)
        left.align_to(rule, LEFT).shift(RIGHT * 0.4)
        e = np.e
        pi = np.pi
        axes = Axes(x_range=[0, 6, 1], y_range=[0, 0.45, 0.1],
                    x_length=4.4, y_length=3.0,
                    axis_config={"color": T.text_muted, "stroke_width": 1.5,
                                 "include_tip": False})
        axes.move_to(RIGHT * 3.9 + DOWN * 0.7)
        f = lambda x: np.log(x) / x
        curve = axes.plot(f, x_range=[0.35, 6.2], color=T.graph_function,
                          stroke_width=4)
        curve_lab = MathTex(r"y=\frac{\ln x}{x}", font_size=24,
                            color=T.graph_function)
        curve_lab.next_to(axes, UP, buff=0.18)
        e_dot = Dot(axes.c2p(e, 1.0 / e), color=T.graph_point, radius=0.07)
        pi_dot = Dot(axes.c2p(pi, np.log(pi) / pi), color=T.graph_point,
                     radius=0.07)
        e_line = DashedLine(axes.c2p(e, 0), axes.c2p(e, 1.0 / e),
                            color=T.text_secondary, stroke_width=2)
        pi_line = DashedLine(axes.c2p(pi, 0), axes.c2p(pi, np.log(pi) / pi),
                            color=T.text_secondary, stroke_width=2)
        e_lab = MathTex(r"e", font_size=24, color=T.text_secondary)
        e_lab.next_to(axes.c2p(e, 0), DOWN, buff=0.1)
        pi_lab = MathTex(r"\pi", font_size=24, color=T.text_secondary)
        pi_lab.next_to(axes.c2p(pi, 0), DOWN, buff=0.1).shift(0.18 * RIGHT)
        ve_lab = MathTex(r"\tfrac{1}{e}", font_size=22, color=T.graph_point)
        ve_lab.next_to(e_dot, LEFT, buff=0.1)
        vpi_lab = MathTex(r"\tfrac{\ln\pi}{\pi}", font_size=22,
                          color=T.graph_point)
        vpi_lab.next_to(pi_dot, RIGHT, buff=0.12)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.78)
        self.play(Write(r2), Create(axes), Create(curve),
                  Write(curve_lab), run_time=2.0)
        self.wait(2.78)
        self.play(FadeIn(e_dot), FadeIn(pi_dot), Create(e_line),
                  Create(pi_line), Write(e_lab), Write(pi_lab),
                  run_time=1.7)
        self.wait(2.45)
        self.play(Write(r3), Write(ve_lab), run_time=1.4)
        self.wait(2.61)
        self.play(Write(r4), Write(vpi_lab), run_time=1.4)
        self.wait(2.61)
        self.play(Write(r5), run_time=1.4)
        box5 = SurroundingRectangle(r5, buff=0.15, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=0.9)
        self.wait(3.27)
        self.wait(4.9)
'''

SEG5 = r'''from manim import *


class Segment5(Scene):
    def construct(self):
        head = Text("Q5 - GENERALISATION AND NUMERICAL CHECK", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{For }e\le a<b:\quad a^{b}>b^{a}",
                     font_size=33, color=T.result_intermediate)
        r2 = MathTex(r"\text{since }f(x)=\frac{\ln x}{x}"
                     r"\text{ decreases for }x\ge e",
                     font_size=30, color=T.text_primary)
        r3 = MathTex(r"e^{\pi}\approx23.141,\qquad "
                     r"\pi^{e}\approx22.459",
                     font_size=32, color=T.text_primary)
        r4 = MathTex(r"e^{\pi}-\pi^{e}\approx0.682>0",
                     font_size=34, color=T.result_final)
        r5 = Text("e is special: it maximises ln x / x and marks the "
                  "crossover between a^b and b^a", font_size=23,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.46)
        fit_width(rows, 11.4)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(3.09)
        self.play(Write(r2), run_time=1.6)
        self.wait(3.09)
        self.play(Write(r3), run_time=1.6)
        self.wait(3.09)
        self.play(Write(r4), run_time=1.4)
        box4 = SurroundingRectangle(r4, buff=0.16, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.46)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.2)
        self.wait(3.09)
        self.wait(5.46)
'''

SEGMENTS = [
    {"narration":
     "To show that e to the pi is greater than pi to the e, we take "
     "natural logarithms. Since the logarithm is strictly increasing, the "
     "inequality is equivalent to pi times ln e greater than e times ln "
     "pi. Because ln e is one, this reduces to pi greater than e ln pi. "
     "Dividing by the positive number e pi, it becomes ln e over e "
     "greater than ln pi over pi. So define f of x equals ln x over x; we "
     "must prove that f at e exceeds f at pi. And we shall do it by "
     "integration, not by taking slopes.",
     "visual": {"style": "reformulation", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Define the function F of t equals t minus e ln t. At t equals e, F "
     "of e is e minus e times one, which is zero. Its derivative is one "
     "minus e over t. By the fundamental theorem of calculus, F of pi "
     "minus F of e equals the integral from e to pi of one minus e over "
     "t, dt. Since F of e is zero, F of pi is exactly that integral. So "
     "the whole problem now rests on the sign of this area.",
     "visual": {"style": "integral setup", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Now examine the integrand on the interval. For t between e and pi, "
     "t is at least e, so e over t is at most one, and one minus e over t "
     "is greater than or equal to zero. It is strictly positive for every "
     "t greater than e. The integral is therefore the area under a "
     "non-negative curve, and it is strictly positive. Consequently F of "
     "pi is greater than zero.",
     "visual": {"style": "area diagram", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "Unwinding this, F of pi greater than zero means pi minus e ln pi is "
     "positive, so pi is greater than e ln pi. Multiplying out, this is "
     "pi ln e greater than e ln pi, which is the same as ln of e to the "
     "pi greater than ln of pi to the e. Exponentiation is strictly "
     "increasing, so the direction is preserved, and we conclude that e "
     "to the pi is greater than pi to the e. The proof is complete.",
     "visual": {"style": "conclusion chain", "transition": "fade"},
     "code": SEG3},
    {"narration":
     "The diagram makes the same point. Plot f of x equals ln x over x. "
     "Its derivative, one minus ln x over x squared, vanishes at x equals "
     "e, giving the maximum value one over e, about zero point three six "
     "eight. At x equals pi the value is ln pi over pi, about zero point "
     "three six four, slightly lower. Because f at e is greater than f at "
     "pi, we again obtain e to the pi greater than pi to the e.",
     "visual": {"style": "curve maximum diagram", "transition": "fade"},
     "code": SEG4},
    {"narration":
     "This generalises. If a and b are at least e with a less than b, "
     "then a to the b is greater than b to the a, because ln x over x "
     "decreases beyond e. Numerically, e to the pi is about twenty three "
     "point one four, while pi to the e is about twenty two point four "
     "six, a difference of about zero point six eight. The number e is "
     "special: it maximises ln x over x and sets the crossover between a "
     "to the b and b to the a.",
     "visual": {"style": "generalisation", "transition": "fade"},
     "code": SEG5},
]

LECTURE = {
    "title": TITLE,
    "preset": "lab",
    "format": "mixed",
    "question": QUESTION,
    "question_code": QUESTION_CODE,
    "segments": SEGMENTS,
}
