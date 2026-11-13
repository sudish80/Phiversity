TITLE = "Q32 - REDOX: KMnO4, OXIDATION NUMBERS AND Fe3O4"

QUESTION = {
    "display":
        "(i) Write the balanced equation for KMnO4 with oxalic acid in "
        "acidic medium. (ii) Assign oxidation numbers in Cr2O7^2-, "
        "MnO4^- and H2O2. (iii) Calculate the oxidation state of Fe in "
        "Fe3O4 and explain why it is fractional.",
    "speech":
        "Part one, write the balanced equation for potassium "
        "permanganate with oxalic acid in acidic medium. Part two, "
        "assign oxidation numbers to all atoms in dichromate ion, "
        "permanganate ion, and hydrogen peroxide. Part three, calculate "
        "the oxidation state of iron in F e three O four and explain why "
        "it is fractional.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 32 - REDOX CHEMISTRY", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = Text("KMnO4 + H2C2O4 / oxidation numbers / Fe3O4",
                    font_size=27, color=T.constant)
        c_chem = Text("BALANCED EQUATION", font_size=20,
                      color=T.highlight_secondary)
        r_chem = Text(
            "2 KMnO4 + 3 H2SO4 + 5 H2C2O4\n"
            "-> K2SO4 + 2 MnSO4 + 10 CO2 + 8 H2O",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("OXIDATION NUMBERS", font_size=20,
                      color=T.highlight_secondary)
        r_math = Text(
            "Cr2O7^2-: Cr +6; MnO4^-: Mn +7;\nH2O2: O -1",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("Fe3O4", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "FeO . Fe2O3 mixed valence;\naverage +8/3",
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
        self.wait(6.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(5.5)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q32 - PERMANGANATE + OXALIC ACID", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\mathrm{MnO_4^-}\rightarrow\mathrm{Mn^{2+}}"
                     r"\ \ (5e^{-}\ \text{gain}),\qquad"
                     r"\mathrm{C_2O_4^{2-}}\rightarrow2\mathrm{CO_2}"
                     r"\ \ (2e^{-}\ \text{loss})", font_size=26,
                     color=T.text_primary)
        r2 = Text("LCM of 5 and 2 is 10: multiply Mn by 2 and oxalate by 5.",
                  font_size=24, color=T.text_secondary)
        r3 = MathTex(r"2\,\mathrm{KMnO_4}+3\,\mathrm{H_2SO_4}"
                     r"+5\,\mathrm{H_2C_2O_4}", font_size=29,
                     color=T.result_intermediate)
        r4 = MathTex(r"\rightarrow\mathrm{K_2SO_4}+2\,\mathrm{MnSO_4}"
                     r"+10\,\mathrm{CO_2}+8\,\mathrm{H_2O}", font_size=29,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.0)
        self.wait(3.0)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.4)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.8)
        self.wait(2.4)
        self.play(Write(r4), run_time=1.8)
        box4 = SurroundingRectangle(r4, buff=0.15, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q32 - OXIDATION NUMBERS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\mathrm{Cr_2O_7^{2-}}:\ 2x+7(-2)=-2"
                     r"\Rightarrow x=+6", font_size=30,
                     color=T.text_primary)
        r2 = MathTex(r"\mathrm{MnO_4^-}:\ x+4(-2)=-1"
                     r"\Rightarrow x=+7", font_size=30,
                     color=T.text_primary)
        r3 = MathTex(r"\mathrm{H_2O_2}:\ 2(+1)+2x=0"
                     r"\Rightarrow x=-1\ \text{(peroxide!)}",
                     font_size=30, color=T.text_primary)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.6)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.9)
        box3 = SurroundingRectangle(r3, buff=0.16, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q32 - Fe IN Fe3O4: A FRACTIONAL AVERAGE", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"3x+4(-2)=0\Rightarrow 3x=8\Rightarrow x=+\frac{8}{3}",
                     font_size=32, color=T.text_primary)
        r2 = MathTex(r"\mathrm{Fe_3O_4}=\mathrm{FeO}\cdot\mathrm{Fe_2O_3}",
                     font_size=31, color=T.result_intermediate)
        r3 = Text("one Fe is +2 and two Fe are +3: a mixed-valence "
                  "oxide.", font_size=24, color=T.text_primary)
        r4 = MathTex(r"\text{average}=\frac{2+3+3}{3}=+\frac{8}{3}",
                     font_size=31, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.6)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.4)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.7)
        box4 = SurroundingRectangle(r4, buff=0.16, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "In acidic medium permanganate takes five electrons, going from "
     "manganese plus seven to manganese plus two. Each oxalate ion loses "
     "two electrons, going to two carbon dioxides. The lowest common "
     "multiple is ten, so use two permanganates and five oxalates. Adding "
     "the potassium, sulphate and hydrogen balances to give: two K M n O "
     "four, plus three H two S O four, plus five H two C two O four, "
     "giving K two S O four, plus two M n S O four, plus ten C O two, "
     "plus eight H two O.",
     "visual": {"style": "balancing", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Oxidation numbers. In dichromate, let chromium be x: two x plus "
     "seven times minus two equals minus two, so chromium is plus six. In "
     "permanganate, x plus four times minus two equals minus one, so "
     "manganese is plus seven. In hydrogen peroxide the oxygens are at "
     "minus one each, the peroxide exception, because the O O bond "
     "shares electrons equally.",
     "visual": {"style": "oxidation numbers", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "For F e three O four, three x plus four times minus two equals zero "
     "gives x equal to plus eight thirds, a fractional value. The reason: "
     "magnetite is a mixed valence oxide, F e O dot F e two O three. One "
     "iron is plus two and two irons are plus three, so the average is "
     "two plus three plus three over three, which is eight thirds. "
     "Oxidation numbers can be fractional when atoms in the same "
     "compound sit in different environments.",
     "visual": {"style": "fractional oxidation", "transition": "fade"},
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
