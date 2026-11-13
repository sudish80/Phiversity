TITLE = "Q25 - CONCENTRATION OF A SUGAR SOLUTION"

QUESTION = {
    "display":
        "What is the concentration of sugar (C12H22O11) in mol/L if 20 g "
        "are dissolved in enough water to make a final volume up to 2 L?",
    "speech":
        "What is the concentration of sugar, C twelve H twenty two O "
        "eleven, in moles per litre, if twenty grams are dissolved in "
        "enough water to make a final volume of two litres? The molar "
        "mass of sucrose is three hundred forty two grams per mole.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 25 - MOLARITY OF SUGAR", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"m=20\,\text{g},\quad V=2\,\text{L},\quad "
            r"M_m(\mathrm{C_{12}H_{22}O_{11}})=342\,\text{g/mol}",
            font_size=29, color=T.constant)
        c_chem = Text("STEP 1", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "moles = 20 / 342 = 0.0585 mol",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("STEP 2", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "M = 0.0585 / 2 = 0.029 mol/L",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("ANSWER", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "about 0.029 M",
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
        self.wait(5.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=0.9)
        self.wait(5.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q25 - MOLES OF SUGAR", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"n=\frac{m}{M_m}=\frac{20\,\text{g}}"
                     r"{342\,\text{g/mol}}", font_size=33,
                     color=T.text_primary)
        r2 = MathTex(r"n=0.0585\ \text{mol}", font_size=36,
                     color=T.result_final)
        rows = VGroup(r1, r2)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        fit_width(rows, 10.6)
        rows.next_to(rule, DOWN, buff=0.8)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.5)
        box2 = SurroundingRectangle(r2, buff=0.18, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q25 - DIVIDE BY THE VOLUME", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"M=\frac{n}{V}=\frac{0.0585}{2}", font_size=33,
                     color=T.text_primary)
        r2 = MathTex(r"M=0.0292\ \text{mol/L}\approx 0.029\ \text{M}",
                     font_size=36, color=T.result_final)
        r3 = Text("about 0.03 molar - a dilute solution", font_size=24,
                  color=T.text_secondary)
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
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.1)
        self.wait(3.6)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "First find the moles of sucrose. Twenty grams divided by the molar "
     "mass, three hundred forty two grams per mole, gives zero point zero "
     "five eight five moles.",
     "visual": {"style": "moles", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Then divide by the final volume of two litres: zero point zero five "
     "eight five over two is zero point zero two nine two moles per "
     "litre. The concentration is about zero point zero two nine molar.",
     "visual": {"style": "molarity", "transition": "fade"},
     "code": SEG1},
]

LECTURE = {
    "title": TITLE,
    "preset": "lab",
    "format": "mixed",
    "question": QUESTION,
    "question_code": QUESTION_CODE,
    "segments": SEGMENTS,
}
