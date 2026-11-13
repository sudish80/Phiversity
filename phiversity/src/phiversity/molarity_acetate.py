TITLE = "Q24 - MASS OF SODIUM ACETATE FOR 500 mL OF 0.375 M"

QUESTION = {
    "display":
        "Calculate the mass of sodium acetate (CH3COONa) required to "
        "make 500 mL of 0.375 molar aqueous solution. Molar mass of "
        "sodium acetate is 82.0245 g/mol.",
    "speech":
        "Calculate the mass of sodium acetate required to make five "
        "hundred millilitres of a zero point three seven five molar "
        "aqueous solution. The molar mass of sodium acetate is eighty "
        "two point zero two four five grams per mole.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 24 - MOLARITY CALCULATION", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"V=500\,\text{mL}=0.500\,\text{L},\quad M=0.375\,\text{mol/L},"
            r"\quad M_m=82.0245\,\text{g/mol}", font_size=29,
            color=T.constant)
        c_chem = Text("STEP 1", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "moles = M x V\n= 0.375 x 0.500 = 0.1875 mol",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("STEP 2", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "mass = moles x molar mass\n= 0.1875 x 82.0245 = 15.38 g",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("ANSWER", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "about 15.38 g of sodium acetate",
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
        self.wait(5.5)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=0.9)
        self.wait(5.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q24 - WHAT MOLARITY MEANS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"M=\frac{\text{moles of solute}}{\text{volume of "
                     r"solution in litres}}", font_size=32,
                     color=T.text_primary)
        r2 = MathTex(r"\Rightarrow\ n=M\times V", font_size=34,
                     color=T.result_intermediate)
        r3 = MathTex(r"V=500\,\text{mL}=0.500\,\text{L}", font_size=31,
                     color=T.text_primary)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        fit_width(rows, 11.4)
        rows.next_to(rule, DOWN, buff=0.6)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.5)
        box2 = SurroundingRectangle(r2, buff=0.15, color=T.result_intermediate)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.5)
        self.wait(3.4)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q24 - MOLES NEEDED", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"n=M\times V=0.375\times 0.500", font_size=33,
                     color=T.text_primary)
        r2 = MathTex(r"n=0.1875\ \text{mol}", font_size=36,
                     color=T.result_final)
        rows = VGroup(r1, r2)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        fit_width(rows, 10.6)
        rows.next_to(rule, DOWN, buff=0.8)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.5)
        box2 = SurroundingRectangle(r2, buff=0.18, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q24 - CONVERT MOLES TO MASS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"m=n\times M_m=0.1875\times 82.0245", font_size=32,
                     color=T.text_primary)
        r2 = MathTex(r"m=15.3796\ \text{g}\approx 15.38\ \text{g}",
                     font_size=36, color=T.result_final)
        r3 = Text("dissolve 15.38 g of CH3COONa and make up to 500 mL.",
                  font_size=24, color=T.text_secondary)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        fit_width(rows, 11.4)
        rows.next_to(rule, DOWN, buff=0.6)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.6)
        box2 = SurroundingRectangle(r2, buff=0.18, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=1.0)
        self.wait(3.2)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.2)
        self.wait(3.6)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Molarity is moles of solute per litre of solution. So the number of "
     "moles needed is molarity times volume in litres. The volume here is "
     "five hundred millilitres, which is zero point five litres.",
     "visual": {"style": "definition", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "The moles required are zero point three seven five times zero point "
     "five, which is zero point one eight seven five moles.",
     "visual": {"style": "moles", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Mass equals moles times molar mass: zero point one eight seven five "
     "times eighty two point zero two four five, which is fifteen point "
     "three seven nine six grams, about fifteen point three eight grams. "
     "Dissolve that and make the volume up to five hundred millilitres.",
     "visual": {"style": "mass", "transition": "fade"},
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
