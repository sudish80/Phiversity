TITLE = "Q27 - PACKING EFFICIENCY: SC, BCC AND FCC"

QUESTION = {
    "display":
        "Calculate the efficiency of packing in case of a metal crystal "
        "for (i) simple cubic (ii) body-centred cubic (iii) "
        "face-centred cubic, with the assumption that atoms are touching "
        "each other.",
    "speech":
        "Calculate the packing efficiency of a metal crystal for simple "
        "cubic, body-centred cubic, and face-centred cubic lattices, "
        "assuming the atoms touch each other. The answers are fifty two "
        "point four percent, sixty eight percent, and seventy four "
        "percent.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 27 - PACKING EFFICIENCY", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"\text{packing fraction}=\frac{z\cdot\frac{4}{3}\pi r^{3}}"
            r"{a^{3}}", font_size=32, color=T.constant)
        c_chem = Text("SIMPLE CUBIC", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "a = 2r, z = 1  ->  pi/6 = 52.4%",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("BCC AND FCC", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "bcc: 4r = sqrt3 a, z = 2  ->  68%\n"
            "fcc: 4r = sqrt2 a, z = 4  ->  74%",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("RANKING", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "52.4% < 68% < 74%",
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
        self.wait(4.5)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(5.5)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(6.5)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=0.9)
        self.wait(5.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q27 - SIMPLE CUBIC", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{atoms touch along the edge: }a=2r,\quad z=1",
                     font_size=30, color=T.text_primary)
        r2 = MathTex(r"PF=\frac{\frac{4}{3}\pi r^{3}}{(2r)^{3}}"
                     r"=\frac{\frac{4}{3}\pi r^{3}}{8r^{3}}=\frac{\pi}{6}",
                     font_size=30, color=T.text_primary)
        r3 = MathTex(r"=0.524\ \text{or}\ 52.4\%", font_size=34,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        fit_width(rows, 11.6)
        rows.next_to(rule, DOWN, buff=0.6)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r2), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.5)
        box3 = SurroundingRectangle(r3, buff=0.17, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q27 - BODY-CENTRED CUBIC", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{atoms touch along the body diagonal:}"
                     r"\quad 4r=\sqrt3\,a", font_size=30,
                     color=T.text_primary)
        r2 = MathTex(r"z=2,\qquad PF=\frac{2\cdot\frac{4}{3}\pi r^{3}}"
                     r"{\left(\frac{4r}{\sqrt3}\right)^{3}}"
                     r"=\frac{\pi\sqrt3}{16}", font_size=29,
                     color=T.text_primary)
        r3 = MathTex(r"=0.68\ \text{or}\ 68\%", font_size=34,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.46)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.55)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.5)
        box3 = SurroundingRectangle(r3, buff=0.17, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q27 - FACE-CENTRED CUBIC", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{atoms touch along the face diagonal:}"
                     r"\quad 4r=\sqrt2\,a", font_size=30,
                     color=T.text_primary)
        r2 = MathTex(r"z=4,\qquad PF=\frac{4\cdot\frac{4}{3}\pi r^{3}}"
                     r"{\left(\frac{4r}{\sqrt2}\right)^{3}}"
                     r"=\frac{\pi}{3\sqrt2}", font_size=29,
                     color=T.text_primary)
        r3 = MathTex(r"=0.74\ \text{or}\ 74\%", font_size=34,
                     color=T.result_final)
        r4 = MathTex(r"52.4\%<68\%<74\%", font_size=32,
                     color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.5)
        box3 = SurroundingRectangle(r3, buff=0.17, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=1.0)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.5)
        box4 = SurroundingRectangle(r4, buff=0.15, color=T.result_intermediate)
        self.play(Create(box4), run_time=0.7)
        self.wait(3.6)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Simple cubic. Atoms touch along the cube edge, so the edge a equals "
     "two r, and the unit cell holds one atom, eight corners times one "
     "eighth. The packing fraction is the volume of one sphere over the "
     "cell volume: four thirds pi r cubed over eight r cubed, which is pi "
     "over six, about fifty two point four percent.",
     "visual": {"style": "simple cubic", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Body-centred cubic. Atoms touch along the body diagonal, which has "
     "length four r, so four r equals root three times a. There are two "
     "atoms per cell. The packing fraction comes to pi root three over "
     "sixteen, about sixty eight percent.",
     "visual": {"style": "bcc", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Face-centred cubic. Atoms touch along the face diagonal, four r "
     "equals root two times a, and there are four atoms per cell. The "
     "packing fraction is pi over three root two, about seventy four "
     "percent, the maximum possible for equal spheres. So the efficiency "
     "rises from fifty two point four percent, to sixty eight percent, to "
     "seventy four percent.",
     "visual": {"style": "fcc", "transition": "fade"},
     "code": SEG2},
]

LECTURE = {
    "title": TITLE,
    "preset": "lab",
    "format": "mixed",
    "question": QUESTION,
    "question_code": QUESTION_CODE,
    "segments": SEGMENTS,
}
