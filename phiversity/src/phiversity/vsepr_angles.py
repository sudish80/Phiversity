TITLE = "Q31 - MOLECULAR SHAPES, HYBRIDISATION AND BOND ANGLES"

QUESTION = {
    "display":
        "(i) Predict the shape and hybridization of SF4, ClF3, XeF4 and "
        "BrF5. (ii) Explain why NH3 has a higher boiling point than PH3. "
        "(iii) Arrange H2O, NH3, CH4, CO2 in increasing order of bond "
        "angle and justify.",
    "speech":
        "Part one, predict the shape and hybridisation of S F four, C l F "
        "three, X e F four and B r F five. Part two, explain why N H three "
        "has a higher boiling point than P H three. Part three, arrange "
        "water, ammonia, methane and carbon dioxide in increasing order "
        "of bond angle and justify.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 31 - VSEPR AND INTERMOLECULAR FORCES",
                     font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = Text("SF4, ClF3, XeF4, BrF5 / NH3 vs PH3 / bond angles",
                    font_size=27, color=T.constant)
        c_chem = Text("SHAPES", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "SF4 see-saw sp3d; ClF3 T-shape sp3d;\n"
            "XeF4 square planar sp3d2; BrF5 square\n"
            "pyramidal sp3d2",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("NH3 > PH3 (b.p.)", font_size=20,
                      color=T.highlight_secondary)
        r_math = Text(
            "NH3 hydrogen-bonds; PH3 has only\n"
            "weak dipole/dispersion forces",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("BOND ANGLES", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "H2O 104.5 < NH3 107 < CH4 109.5 < CO2 180",
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
        self.wait(7.0)
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
        head = Text("Q31 - FOUR HYPOVALENT SHAPES", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        rows = []
        specs = [
            (r"\mathrm{SF_4}", "4 bp + 1 lp", "see-saw", r"sp^{3}d"),
            (r"\mathrm{ClF_3}", "3 bp + 2 lp", "T-shaped", r"sp^{3}d"),
            (r"\mathrm{XeF_4}", "4 bp + 2 lp", "square planar", r"sp^{3}d^{2}"),
            (r"\mathrm{BrF_5}", "5 bp + 1 lp", "square pyramidal", r"sp^{3}d^{2}"),
        ]
        for sym, cnt, shape, hyb in specs:
            a = MathTex(sym, font_size=30, color=T.text_primary)
            b = MathTex(cnt, font_size=26, color=T.text_secondary)
            c = Text(shape, font_size=24, color=T.result_final)
            d = MathTex(hyb, font_size=28, color=T.result_intermediate)
            row = VGroup(a, b, c, d).arrange(RIGHT, buff=0.5)
            rows.append(row)
        grp = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(grp, 12.4)
        grp.next_to(rule, DOWN, buff=0.45)
        grp.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if grp.height > 6.0:
            grp.scale_to_fit_height(6.0)
        for row in rows:
            self.play(FadeIn(row, shift=0.15 * UP), run_time=1.1)
            self.wait(1.6)
        self.wait(3.6)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q31 - WHY NH3 BOILS HIGHER THAN PH3", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\mathrm{NH_3}\ \text{b.p.}\ 240\,\text{K}>\ "
                     r"\mathrm{PH_3}\ 185\,\text{K}", font_size=30,
                     color=T.text_primary)
        r2 = Text("N is small and electronegative: N-H bonds are polar "
                  "enough for hydrogen bonding between molecules.",
                  font_size=23, color=T.text_secondary)
        r3 = Text("P is larger and less electronegative: PH3 has only "
                  "weak dipole-dipole and dispersion forces.",
                  font_size=23, color=T.text_primary)
        r4 = MathTex(r"\Rightarrow\ \text{H-bonds cost extra energy to "
                     r"break at boiling}", font_size=28,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.6)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.5)
        self.wait(3.0)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.5)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.6)
        box4 = SurroundingRectangle(r4, buff=0.15, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q31 - BOND ANGLES IN ORDER", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        r1 = MathTex(r"\mathrm{H_2O}\ 104.5^{\circ}"
                     r"<\mathrm{NH_3}\ 107^{\circ}"
                     r"<\mathrm{CH_4}\ 109.5^{\circ}"
                     r"<\mathrm{CO_2}\ 180^{\circ}", font_size=28,
                     color=T.result_final)
        rows = VGroup(r1)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.4)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        self.play(Write(r1), run_time=2.2)
        box1 = SurroundingRectangle(r1, buff=0.18, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        r2 = Text("water: 2 lone pairs squeeze the angle most;",
                  font_size=24, color=T.text_primary)
        r3 = Text("ammonia: 1 lone pair squeezes less;",
                  font_size=24, color=T.text_primary)
        r4 = Text("methane: no lone pairs, perfect tetrahedron;",
                  font_size=24, color=T.text_primary)
        r5 = Text("CO2: linear sp2... rather sp-hybridised C with two "
                  "double bonds.", font_size=24, color=T.text_secondary)
        r5b = Text("CO2 is sp-hybridised carbon, two double bonds, "
                   "linear.", font_size=24, color=T.text_secondary)
        rows2 = VGroup(r2, r3, r4, r5b).arrange(DOWN, aligned_edge=LEFT,
                                                buff=0.32)
        fit_width(rows2, 11.6)
        rows2.next_to(VGroup(r1, box1), DOWN, buff=0.45)
        if rows2.height > 3.6:
            rows2.scale_to_fit_height(3.6)
        self.play(FadeIn(r2, shift=0.15 * UP), run_time=1.2)
        self.wait(2.2)
        self.play(FadeIn(r3, shift=0.15 * UP), run_time=1.2)
        self.wait(2.2)
        self.play(FadeIn(r4, shift=0.15 * UP), run_time=1.2)
        self.wait(2.2)
        self.play(FadeIn(r5b, shift=0.15 * UP), run_time=1.2)
        self.wait(3.4)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Apply V S E P R. S F four has four bond pairs and one lone pair on "
     "sulfur: trigonal bipyramidal electron geometry, see-saw shape, S P "
     "three D hybridisation. C l F three has three bond pairs and two "
     "lone pairs: T-shaped, again S P three D. X e F four has four bond "
     "pairs and two lone pairs: octahedral electron geometry, square "
     "planar shape, S P three D two. B r F five has five bond pairs and "
     "one lone pair: square pyramidal, S P three D two.",
     "visual": {"style": "shape table", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Ammonia boils at about two hundred forty kelvin, phosphine at about "
     "one eighty five. Nitrogen is small and electronegative, so N H "
     "bonds are polar enough for hydrogen bonding between molecules. "
     "Phosphorus is larger and less electronegative, so P H three has "
     "only weak dipole and dispersion forces. Breaking hydrogen bonds "
     "costs extra energy, so ammonia boils higher.",
     "visual": {"style": "boiling points", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Bond angles in increasing order: water at one hundred four point "
     "five degrees, ammonia at one hundred seven, methane at one hundred "
     "nine point five, and carbon dioxide at one hundred eighty. Water "
     "has two lone pairs squeezing the tetrahedral angle the most, "
     "ammonia one lone pair squeezing it less, methane has no lone pairs "
     "and is a perfect tetrahedron, and carbon dioxide is "
     "sp-hybridised carbon with two double bonds, linear.",
     "visual": {"style": "bond angles", "transition": "fade"},
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
