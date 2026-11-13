TITLE = "Q2 - LENS + PLANE MIRROR COMBINATION"

QUESTION = {
    "display":
        "A point object is placed 30 cm in front of a convex lens of focal "
        "length 20 cm. A plane mirror is placed 40 cm behind the lens, "
        "perpendicular to the principal axis. Light from the object passes "
        "through the lens, reflects off the mirror, and passes back through "
        "the lens. Find the position and nature of the final image.",
    "speech":
        "A point object is placed thirty centimetres in front of a convex "
        "lens of focal length twenty centimetres. A plane mirror is placed "
        "forty centimetres behind the lens, perpendicular to the principal "
        "axis. Light from the object passes through the lens, reflects off "
        "the mirror, and passes back through the lens. Find the position "
        "and nature of the final image.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 2 - LENS + PLANE MIRROR", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(r"\text{object 30 cm before convex lens, }f=20\ \text{cm};"
                       r"\ \text{plane mirror 40 cm behind the lens}",
                       font_size=27, color=T.constant)
        c_chem = Text("SETUP", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "convex lens f = +20 cm at x = 0\n"
            "object at x = -30 cm (in front)\n"
            "plane mirror at x = +40 cm (behind)",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("STEPS", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "1  lens first: 1/v - 1/u = 1/f -> v = +60 cm (real)\n"
            "2  mirror: image of I1 lies 20 cm behind the lens\n"
            "3  second lens pass: object at 20 cm = f -> parallel rays",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("ANSWER", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "final image: at infinity (collimated beam)\n"
            "no finite real or virtual image forms",
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
        self.wait(9.0)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(10.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(10.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q2 - THE SETUP AND PLAN", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{light travels left-to-right, then back after}"
                     r"\ \text{the mirror}",
                     font_size=27, color=T.text_primary)
        r2 = MathTex(r"\text{three steps: lens, mirror, lens again}",
                     font_size=27, color=T.text_primary)
        rows = VGroup(r1, r2)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 11.0)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        axis = Line(LEFT * 6.6, RIGHT * 6.6, color=T.text_muted,
                    stroke_width=2)
        axis.move_to(DOWN * 1.2)
        obj = Arrow(LEFT * 4.9 + DOWN * 1.2, LEFT * 4.9 + UP * 0.9,
                    color=T.graph_point, stroke_width=5)
        objlab = Text("object", font_size=20, color=T.graph_point)
        objlab.next_to(obj, LEFT, buff=0.15)
        lens = VGroup(
            Line(UP * 1.1, DOWN * 1.1, color=T.text_primary, stroke_width=4),
            Polygon([0.28, 0.2, 0], [1.05, 0, 0], [0.28, -0.2, 0],
                    color=T.text_primary, stroke_width=2),
            Polygon([-0.28, 0.2, 0], [-1.05, 0, 0], [-0.28, -0.2, 0],
                    color=T.text_primary, stroke_width=2))
        lens.move_to(DOWN * 1.2)
        lenslab = Text("lens f = 20", font_size=20, color=T.text_primary)
        lenslab.next_to(lens, UP, buff=0.2)
        mirr = VGroup(
            Line(UP * 1.1, DOWN * 1.1, color=T.graph_function, stroke_width=5),
            Line(UP * 1.05, UP * 0.95, color=T.graph_function, stroke_width=2),
            Line(UP * 0.85, UP * 0.75, color=T.graph_function, stroke_width=2),
            Line(UP * 0.65, UP * 0.55, color=T.graph_function, stroke_width=2),
            Line(UP * 0.45, UP * 0.35, color=T.graph_function, stroke_width=2),
            Line(UP * 0.25, UP * 0.15, color=T.graph_function, stroke_width=2),
            Line(UP * 0.05, DOWN * 0.05, color=T.graph_function, stroke_width=2),
            Line(DOWN * 0.25, DOWN * 0.35, color=T.graph_function, stroke_width=2),
            Line(DOWN * 0.45, DOWN * 0.55, color=T.graph_function, stroke_width=2),
            Line(DOWN * 0.65, DOWN * 0.75, color=T.graph_function, stroke_width=2),
            Line(DOWN * 0.85, DOWN * 0.95, color=T.graph_function, stroke_width=2))
        mirr.move_to(RIGHT * 2.85 + DOWN * 1.2)
        mirrlab = Text("plane mirror", font_size=20, color=T.graph_function)
        mirrlab.next_to(mirr, UP, buff=0.2)
        d1 = Line(LEFT * 4.9 + DOWN * 1.35, DOWN * 1.35,
                  color=T.text_secondary, stroke_width=2)
        d1lab = MathTex(r"30\ \text{cm}", font_size=20, color=T.text_secondary)
        d1lab.next_to(d1, DOWN, buff=0.08)
        d2 = Line(DOWN * 1.35, RIGHT * 2.85 + DOWN * 1.35,
                  color=T.text_secondary, stroke_width=2)
        d2lab = MathTex(r"40\ \text{cm}", font_size=20, color=T.text_secondary)
        d2lab.next_to(d2, DOWN, buff=0.08)
        self.play(Write(r1), run_time=1.6)
        self.wait(3.5)
        self.play(Write(r2), run_time=1.2)
        self.wait(3.5)
        self.play(Create(axis), run_time=1.0)
        self.play(Create(obj), Write(objlab), run_time=1.2)
        self.wait(3.0)
        self.play(Create(lens), Write(lenslab), run_time=1.2)
        self.wait(3.0)
        self.play(Create(mirr), Write(mirrlab), run_time=1.2)
        self.play(Write(d1lab), Write(d2lab), run_time=1.0)
        self.wait(3.5)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q2 - FIRST PASS THROUGH THE LENS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{thin lens equation: }\frac{1}{v}-\frac{1}{u}"
                     r"=\frac{1}{f}",
                     font_size=30, color=T.variable)
        r2 = MathTex(r"u=-30\ \text{cm (real object, incident side)},\qquad "
                     r"f=+20\ \text{cm}",
                     font_size=29, color=T.text_primary)
        r3 = MathTex(r"\frac{1}{v}=\frac{1}{20}-\frac{1}{30}"
                     r"=\frac{3-2}{60}=\frac{1}{60}",
                     font_size=29, color=T.text_primary)
        r4 = MathTex(r"v=+60\ \text{cm}",
                     font_size=31, color=T.result_intermediate)
        r5 = MathTex(r"\text{first image I1: real, 60 cm behind the lens,}"
                     r"\ \text{inverted, }m=-2",
                     font_size=28, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 11.0)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(4.0)
        self.play(Write(r2), run_time=1.6)
        self.wait(4.0)
        self.play(Write(r3), run_time=1.8)
        self.wait(4.5)
        self.play(Write(r4), run_time=1.6)
        self.wait(3.5)
        self.play(Write(r5), run_time=1.6)
        box5 = SurroundingRectangle(r5, buff=0.13, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q2 - REFLECTION BY THE PLANE MIRROR", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{mirror at 40 cm behind the lens; }"
                     r"\text{I1 at 60 cm behind the lens}",
                     font_size=28, color=T.text_primary)
        r2 = MathTex(r"\text{I1 is 20 cm in front of the mirror}",
                     font_size=28, color=T.text_primary)
        r3 = MathTex(r"\text{plane mirror: the reflected rays diverge as if}"
                     r"\ \text{from the mirror image}",
                     font_size=28, color=T.text_primary)
        r4 = MathTex(r"\text{I2 lies 20 cm in front of the mirror,}"
                     r"\ \text{i.e. 20 cm behind the lens}",
                     font_size=28, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 11.5)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(4.0)
        self.play(Write(r2), run_time=1.2)
        self.wait(3.5)
        self.play(Write(r3), run_time=1.6)
        self.wait(4.0)
        self.play(Write(r4), run_time=1.6)
        box4 = SurroundingRectangle(r4, buff=0.13, color=T.result_intermediate)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_intermediate, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q2 - SECOND PASS THROUGH THE LENS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{returning light travels right-to-left; I2 is}"
                     r"\ \text{the object for the second pass}",
                     font_size=28, color=T.text_primary)
        r2 = MathTex(r"\text{I2 sits exactly at the focal point: }"
                     r"\text{distance }=20\ \text{cm} = f",
                     font_size=28, color=T.result_intermediate)
        r3 = MathTex(r"\text{a real object at the focus gives parallel rays:}"
                     r"\ \frac{1}{v}=\frac{1}{f}+\frac{1}{u}=0\ \Rightarrow\ "
                     r"v=\infty",
                     font_size=28, color=T.text_primary)
        r4 = MathTex(r"\text{therefore the final image is at infinity - a}"
                     r"\ \text{collimated beam}",
                     font_size=30, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 11.5)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(4.0)
        self.play(Write(r2), run_time=1.4)
        self.wait(3.5)
        self.play(Write(r3), run_time=1.8)
        self.wait(4.5)
        self.play(Write(r4), run_time=1.6)
        box4 = SurroundingRectangle(r4, buff=0.13, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q2 - FINAL ANSWER", font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{position: the final image is at infinity}",
                     font_size=31, color=T.result_final)
        r2 = MathTex(r"\text{nature: emergent rays travel as a parallel beam;}",
                     r"\ \text{no finite real or virtual image forms}",
                     font_size=29, color=T.result_final)
        r3 = MathTex(r"\text{the mirror image happens to land exactly on the}"
                     r"\ \text{focal plane - that is the key trick}",
                     font_size=27, color=T.text_secondary)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 11.5)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        box1 = SurroundingRectangle(r1, buff=0.16, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(4.5)
        self.play(Write(r2), run_time=1.8)
        self.wait(4.5)
        self.play(Write(r3), run_time=1.4)
        self.wait(4.0)
        self.wait(6)
'''

SEGMENTS = [
    {"narration": "Let us set up the problem. Light from a point object "
     "travels left to right, passes through a convex lens of focal length "
     "twenty centimetres, hits a plane mirror forty centimetres behind the "
     "lens, reflects, and returns through the lens. We solve it in three "
     "steps: first the lens, then the mirror, then the lens again.",
     "visual": {"style": "optical diagram", "transition": "slide-up"},
     "code": SEG0},
    {"narration": "First pass through the lens. Use the thin lens equation: "
     "one over v minus one over u equals one over f. The object is a real "
     "object on the incident side, so u equals minus thirty centimetres, and "
     "f is plus twenty. One over v equals one over twenty minus one over "
     "thirty, which is one over sixty, so v equals plus sixty centimetres. "
     "The first image I1 is real, sixty centimetres behind the lens, "
     "inverted, with magnification minus two.",
     "visual": {"style": "equations", "transition": "fade"},
     "code": SEG1},
    {"narration": "Now the mirror. The mirror sits forty centimetres behind "
     "the lens, and I1 is sixty centimetres behind the lens, so I1 is "
     "twenty centimetres in front of the mirror. A plane mirror makes the "
     "reflected rays diverge as if they came from the mirror image, which "
     "lies twenty centimetres in front of the mirror, that is, twenty "
     "centimetres behind the lens. Call this point I2.",
     "visual": {"style": "equations", "transition": "carry-over"},
     "code": SEG2},
    {"narration": "Second pass through the lens. The returning light travels "
     "right to left, and I2 is the object for this pass. But I2 lies "
     "exactly at the focal point, twenty centimetres from the lens. A real "
     "object placed at the focus produces parallel rays: one over v equals "
     "zero, so v is infinity. The rays therefore emerge as a collimated "
     "beam, and the final image is at infinity.",
     "visual": {"style": "equations", "transition": "fade"},
     "code": SEG3},
    {"narration": "Final answer. Position: the final image is at infinity. "
     "Nature: the emergent rays travel as a parallel beam, so no finite "
     "real or virtual image forms. The key trick of this problem is that "
     "the mirror image lands exactly on the focal plane, which turns the "
     "returning rays parallel.",
     "visual": {"style": "summary card", "transition": "fade"},
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
