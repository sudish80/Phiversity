TITLE = "Q10 - GABRIEL'S HORN: FINITE VOLUME, INFINITE AREA"

QUESTION = {
    "display":
        "Gabriel's horn is formed by rotating the graph y = 1/x, for "
        "x >= 1, about the x-axis. Using dV = pi y^2 dx, show that the "
        "volume of the solid of revolution is finite, and compare it with "
        "the surface area. Explain the resulting paradox.",
    "speech":
        "Gabriel's horn is formed by rotating the graph y equals one over "
        "x, for x greater than or equal to one, about the x axis. Using "
        "the disk method, dV equals pi y squared dx, show that the volume "
        "of the solid of revolution is finite, and compare it with the "
        "surface area. Explain the resulting paradox.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 10 - GABRIEL'S HORN", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(r"y=\frac{1}{x},\quad x\ge1,\quad "
                       r"\text{rotate about the }x\text{-axis}",
                       font_size=29, color=T.constant)
        c_chem = Text("METHOD", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "disk method\n"
            "dV = pi y^2 dx",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("VOLUME", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "V = integral(1..inf) pi / x^2 dx\n"
            "= pi [ -1/x ] from 1 to infinity = pi",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("SURFACE AREA", font_size=20,
                      color=T.highlight_secondary)
        r_econ = Text(
            "A = 2 pi integral(1/x) sqrt(1 + 1/x^4) dx\n"
            "> 2 pi integral dx/x -> infinity",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, chem, maths, econ).arrange(DOWN, aligned_edge=LEFT,
                                                       buff=0.32)
        rows.move_to(UP * 0.2)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=2.0)
        self.wait(5.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(8.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q10 - THE HORN AS A SOLID OF REVOLUTION", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        axes = Axes(x_range=[0, 8, 1], y_range=[0, 1.25, 0.25],
                    x_length=8.4, y_length=3.2,
                    axis_config={"color": T.text_muted, "stroke_width": 1.5,
                                 "include_tip": False})
        axes.move_to(DOWN * 0.9)
        curve = axes.plot(lambda x: 1.0 / x, x_range=[1, 7.8],
                          color=T.graph_function, stroke_width=4)
        xs = np.linspace(1, 7.8, 80)
        pts = [axes.c2p(x, 0.0) for x in xs]
        pts += [axes.c2p(x, 1.0 / x) for x in xs[::-1]]
        region = Polygon(*pts)
        region.set_fill(T.graph_function, opacity=0.18)
        region.set_stroke(width=0)
        x0 = 2.2
        y0 = 1.0 / x0
        strip = Polygon(axes.c2p(x0, 0), axes.c2p(x0 + 0.22, 0),
                        axes.c2p(x0 + 0.22, 1.0 / (x0 + 0.22)),
                        axes.c2p(x0, y0))
        strip.set_fill(T.cancel_mark, opacity=0.45)
        strip.set_stroke(T.cancel_mark, 2)
        xlab = MathTex(r"x", font_size=24, color=T.text_secondary)
        xlab.next_to(axes, DOWN, buff=0.1).shift(RIGHT * 3.7)
        ylab = MathTex(r"y=\frac{1}{x}", font_size=24, color=T.graph_function)
        ylab.next_to(axes.c2p(1.05, 1.0), RIGHT, buff=0.15)
        dlab = MathTex(r"\text{disk radius }y,\ \text{thickness }dx",
                       font_size=23, color=T.cancel_mark)
        dlab.next_to(axes.c2p(x0, y0), UP, buff=0.45)
        axlab = Text("x-axis (axis of rotation)", font_size=22,
                     color=T.text_secondary)
        axlab.next_to(axes, DOWN, buff=0.1).shift(LEFT * 2.0)
        one = DashedLine(axes.c2p(1, 0), axes.c2p(1, 1.0),
                         color=T.text_secondary, stroke_width=2)
        self.play(Create(axes), run_time=1.0)
        self.play(Create(curve), FadeIn(region), run_time=1.8)
        self.play(Create(one), Write(xlab), Write(axlab), run_time=1.0)
        self.play(Write(ylab), run_time=0.8)
        self.play(FadeIn(strip), Write(dlab), run_time=1.2)
        self.wait(4.0)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q10 - THE DISK ELEMENT", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"dV=\pi(\text{radius})^{2}\,dx", font_size=34,
                     color=T.text_primary)
        r2 = MathTex(r"\text{radius}=y=\frac{1}{x}", font_size=32,
                     color=T.text_primary)
        r3 = MathTex(r"dV=\pi\left(\frac{1}{x}\right)^{2}dx"
                     r"=\frac{\pi}{x^{2}}\,dx", font_size=34,
                     color=T.result_intermediate)
        r4 = Text("add the volumes of all the thin disks along the horn",
                  font_size=24, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        fit_width(rows, 11.0)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.4)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.15, color=T.result_intermediate)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_intermediate, run_time=0.9)
        self.wait(3.8)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.0)
        self.wait(3.4)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q10 - VOLUME OF THE HORN", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"V=\int_{1}^{\infty}\frac{\pi}{x^{2}}\,dx",
                     font_size=34, color=T.text_primary)
        r2 = MathTex(r"=\pi\left[-\frac{1}{x}\right]_{1}^{\infty}",
                     font_size=34, color=T.text_primary)
        r3 = MathTex(r"=\pi\left(0-(-1)\right)=\pi", font_size=36,
                     color=T.result_final)
        r4 = Text("the volume is finite, about 3.14 cubic units", font_size=24,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        fit_width(rows, 10.6)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.4)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.18, color=T.result_final)
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
        head = Text("Q10 - SURFACE AREA DIVERGES", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"A=2\pi\int_{1}^{\infty}y"
                     r"\sqrt{1+\left(\frac{dy}{dx}\right)^{2}}dx",
                     font_size=30, color=T.text_primary)
        r2 = MathTex(r"=2\pi\int_{1}^{\infty}\frac{1}{x}"
                     r"\sqrt{1+\frac{1}{x^{4}}}\,dx", font_size=31,
                     color=T.text_primary)
        r3 = MathTex(r">2\pi\int_{1}^{\infty}\frac{1}{x}\,dx"
                     r"=2\pi\left[\ln x\right]_{1}^{\infty}",
                     font_size=31, color=T.text_primary)
        r4 = MathTex(r"\to\infty", font_size=38, color=T.result_final)
        r5 = Text("so the horn has finite volume but infinite surface area",
                  font_size=24, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 11.4)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.6)
        self.wait(3.2)
        self.play(Write(r3), run_time=1.6)
        self.wait(3.4)
        self.play(Write(r4), run_time=1.4)
        box4 = SurroundingRectangle(r4, buff=0.18, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.8)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.0)
        self.wait(3.6)
        self.wait(6)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q10 - THE PAINTER'S PARADOX", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("You could fill the horn with pi cubic units of paint,",
                  font_size=25, color=T.text_primary)
        r2 = Text("yet you could never paint its inner surface,",
                  font_size=25, color=T.text_primary)
        r3 = Text("because that surface has infinite area.", font_size=25,
                  color=T.text_primary)
        r4 = Text("Resolution: a real paint layer has finite thickness, so",
                  font_size=24, color=T.result_final)
        r5 = Text("the mathematical surface is an idealisation, not a coat "
                  "of paint.", font_size=24, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(FadeIn(r1, shift=0.2 * UP), run_time=1.3)
        self.wait(3.4)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.3)
        self.wait(3.2)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.3)
        self.wait(3.4)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.3)
        box4 = SurroundingRectangle(VGroup(r4, r5), buff=0.14,
                                    color=T.result_final)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.3)
        self.play(Create(box4), run_time=0.7)
        self.wait(4.0)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Gabriel's horn is made by rotating the curve y equals one over x, "
     "for x greater than or equal to one, about the x-axis. Slice the "
     "solid into thin disks perpendicular to the axis. A disk at position "
     "x has radius r equal to y, that is one over x, and thickness dx. "
     "The shaded strip in the diagram is one such disk seen edge-on.",
     "visual": {"style": "horn diagram", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "The volume of a thin disk is pi times the square of its radius "
     "times its thickness, dV equals pi y squared dx. With radius y equal "
     "to one over x, this becomes pi over x squared dx. The total volume "
     "is the sum, in the limit the integral, of all these disk volumes "
     "along the horn.",
     "visual": {"style": "disk element", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "So the volume is the integral from one to infinity of pi over x "
     "squared dx. The antiderivative is minus one over x, so the volume "
     "equals pi times zero minus minus one, which is pi. The volume is "
     "finite, about three point one four cubic units.",
     "visual": {"style": "volume", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "Now the surface area. The area formula is two pi times the integral "
     "of y times the square root of one plus the square of dy by dx. Here "
     "dy by dx is minus one over x squared, so the square root factor is "
     "at least one. Therefore the area is greater than two pi times the "
     "integral of one over x, which is two pi ln x, and that diverges. "
     "The surface area is infinite.",
     "visual": {"style": "area divergence", "transition": "fade"},
     "code": SEG3},
    {"narration":
     "This is the painter's paradox. You could fill the horn with pi "
     "cubic units of paint, yet you could never paint its inner surface, "
     "because that surface has infinite area. The resolution is that a "
     "real coat of paint has finite thickness, so it would fill the thin "
     "end and close it off. The mathematical surface is an idealisation.",
     "visual": {"style": "paradox", "transition": "fade"},
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
