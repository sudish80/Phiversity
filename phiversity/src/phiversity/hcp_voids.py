TITLE = "Q26 - VOIDS IN A HEXAGONAL CLOSE-PACKED UNIT CELL"

QUESTION = {
    "display":
        "A compound forms hexagonal close-packed structure. What is the "
        "number of voids filled and unfilled per unit cell?",
    "speech":
        "A compound forms a hexagonal close-packed structure. What is the "
        "number of voids filled and unfilled per unit cell? In H C P the "
        "unit cell contains six atoms, giving six octahedral voids and "
        "twelve tetrahedral voids.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 26 - HCP VOIDS", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(r"N=6\ \text{atoms per HCP unit cell}",
                       font_size=32, color=T.constant)
        c_chem = Text("VOIDS", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "octahedral voids = N = 6\n"
            "tetrahedral voids = 2N = 12\n"
            "total = 18",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("IF OCTAHEDRAL SITES FILLED", font_size=20,
                      color=T.highlight_secondary)
        r_math = Text(
            "6 filled, 12 unfilled (tetrahedral)",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("IF TETRAHEDRAL SITES FILLED", font_size=20,
                      color=T.highlight_secondary)
        r_econ = Text(
            "12 filled, 6 unfilled (octahedral)",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, chem, maths, econ).arrange(DOWN, aligned_edge=LEFT,
                                                       buff=0.32)
        rows.move_to(UP * 0.15)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=1.6)
        self.wait(4.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(6.5)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(5.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(5.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q26 - ATOMS PER HCP UNIT CELL", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"N=12\times\frac{1}{6}+2\times\frac{1}{2}+3",
                     font_size=33, color=T.text_primary)
        r2 = MathTex(r"=2+1+3=6", font_size=34, color=T.result_final)
        r3 = Text("12 corner atoms share 6 cells each, 2 face-centre "
                  "atoms share 2 cells, 3 atoms lie fully inside.",
                  font_size=23, color=T.text_secondary)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        fit_width(rows, 11.6)
        rows.next_to(rule, DOWN, buff=0.6)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.5)
        box2 = SurroundingRectangle(r2, buff=0.17, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=1.0)
        self.wait(3.0)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.4)
        self.wait(3.6)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q26 - COUNT THE VOIDS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{octahedral voids}=N=6", font_size=33,
                     color=T.text_primary)
        r2 = MathTex(r"\text{tetrahedral voids}=2N=12", font_size=33,
                     color=T.text_primary)
        r3 = MathTex(r"\text{total voids}=6+12=18", font_size=34,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        fit_width(rows, 11.0)
        rows.next_to(rule, DOWN, buff=0.6)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.18, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q26 - FILLED AND UNFILLED", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("which voids are filled depends on the compound's "
                  "stoichiometry:", font_size=24, color=T.text_secondary)
        r2 = MathTex(r"\text{all octahedral filled: }6\text{ filled},\ "
                     r"12\text{ unfilled}", font_size=29,
                     color=T.result_intermediate)
        r3 = MathTex(r"\text{all tetrahedral filled: }12\text{ filled},\ "
                     r"6\text{ unfilled}", font_size=29,
                     color=T.result_intermediate)
        r4 = Text("e.g. a 1:1 compound (like ZnS-type arrays) uses the "
                  "tetrahedral set; a 1:1 rock-salt-type array uses the "
                  "octahedral set.", font_size=23, color=T.text_primary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(FadeIn(r1, shift=0.2 * UP), run_time=1.4)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.7)
        box3 = SurroundingRectangle(VGroup(r2, r3), buff=0.15,
                                    color=T.result_intermediate)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.4)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.4)
        self.wait(3.6)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "First count the atoms in one H C P unit cell. Twelve corner atoms "
     "are shared by six cells each, contributing two. Two face-centre "
     "atoms are shared by two cells each, contributing one. Three atoms "
     "lie completely inside. Total: six atoms per unit cell.",
     "visual": {"style": "counting", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "In any close packing, the number of octahedral voids equals the "
     "number of atoms, so here six. The number of tetrahedral voids is "
     "twice that, twelve. Total voids: eighteen.",
     "visual": {"style": "voids", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Which of these are filled depends on the compound. If all "
     "octahedral sites are occupied, six are filled and twelve remain "
     "unfilled. If all tetrahedral sites are occupied, twelve are filled "
     "and six remain unfilled. Rock-salt-type arrays use the octahedral "
     "set, zinc-blende-type arrays use the tetrahedral set.",
     "visual": {"style": "filled vs unfilled", "transition": "fade"},
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
