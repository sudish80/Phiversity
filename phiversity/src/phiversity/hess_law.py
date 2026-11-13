TITLE = "Q30 - HESS'S LAW AND THE FORMATION ENTHALPY OF METHANE"

QUESTION = {
    "display":
        "(i) State Hess's law of constant heat summation. (ii) Calculate "
        "the enthalpy change for C(graphite) + 2H2(g) -> CH4(g), given "
        "the combustion enthalpies of C, H2 and CH4 (-393.5, -285.8, "
        "-890.3 kJ/mol).",
    "speech":
        "State Hess's law of constant heat summation, and calculate the "
        "enthalpy change for the reaction of graphite with two moles of "
        "hydrogen gas to give methane. We are given the enthalpies of "
        "combustion: graphite plus oxygen gives carbon dioxide with "
        "minus three ninety three point five kilojoules per mole; "
        "hydrogen plus half oxygen gives liquid water with minus two "
        "eighty five point eight; and methane plus two oxygen gives "
        "carbon dioxide plus two water with minus eight hundred ninety "
        "point three.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 30 - HESS'S LAW", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"\Delta H=-393.5,\ -285.8,\ -890.3\ \mathrm{kJ/mol}"
            r"\ (\mathrm{C},\ \mathrm{H_2},\ \mathrm{CH_4}\ \text{combustion})", font_size=26, color=T.constant)
        c_chem = Text("LAW", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "total enthalpy change is the same\n"
            "whether the reaction occurs in one\n"
            "step or several",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("COMBINE", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "target = eq1 + 2 x eq2 - eq3",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("ANSWER", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "delta H = -74.8 kJ/mol",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, chem, maths, econ).arrange(DOWN, aligned_edge=LEFT,
                                                       buff=0.32)
        rows.move_to(UP * 0.15)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=2.0)
        self.wait(4.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
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
        head = Text("Q30 - HESS'S LAW", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("Hess's law: the total enthalpy change of a reaction is "
                  "the same,", font_size=25, color=T.text_primary)
        r2 = Text("whether it takes place in one step or in several "
                  "steps.", font_size=25, color=T.text_primary)
        r3 = MathTex(r"\Delta H_\text{overall}=\sum\Delta H_\text{steps}",
                     font_size=33, color=T.result_final)
        r4 = Text("because enthalpy is a state function: it depends only "
                  "on initial and final states.", font_size=23,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 11.8)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(FadeIn(r1, shift=0.2 * UP), run_time=1.3)
        self.wait(2.4)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.3)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.5)
        box3 = SurroundingRectangle(r3, buff=0.16, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.4)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.4)
        self.wait(3.4)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q30 - COMBINE THE THREE EQUATIONS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        t = MathTex(r"\text{target: }"
                    r"\mathrm{C}+2\mathrm{H_2}\rightarrow\mathrm{CH_4}",
                    font_size=31, color=T.highlight_primary)
        e1 = MathTex(r"\mathrm{C}+\mathrm{O_2}\rightarrow\mathrm{CO_2}"
                     r"\qquad \Delta H_1=-393.5", font_size=27,
                     color=T.text_primary)
        e2 = MathTex(r"\mathrm{H_2}+\frac{1}{2}\mathrm{O_2}\rightarrow"
                     r"\mathrm{H_2O}\qquad \Delta H_2=-285.8",
                     font_size=27, color=T.text_primary)
        e3 = MathTex(r"\mathrm{CH_4}+2\mathrm{O_2}\rightarrow\mathrm{CO_2}"
                     r"+2\mathrm{H_2O}\qquad \Delta H_3=-890.3",
                     font_size=27, color=T.text_primary)
        comb = MathTex(r"\text{target}=(1)+2\times(2)-(3)",
                       font_size=31, color=T.result_intermediate)
        rows = VGroup(t, e1, e2, e3, comb)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.38)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(t), run_time=1.6)
        self.wait(2.4)
        self.play(Write(e1), run_time=1.6)
        self.wait(2.4)
        self.play(Write(e2), run_time=1.6)
        self.wait(2.4)
        self.play(Write(e3), run_time=1.6)
        self.wait(2.4)
        self.play(Write(comb), run_time=1.6)
        box5 = SurroundingRectangle(comb, buff=0.15,
                                    color=T.result_intermediate)
        self.play(Create(box5), run_time=0.7)
        self.wait(3.4)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q30 - COMPUTE delta H", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\Delta H=-393.5+2(-285.8)-(-890.3)", font_size=32,
                     color=T.text_primary)
        r2 = MathTex(r"=-393.5-571.6+890.3", font_size=32,
                     color=T.text_primary)
        r3 = MathTex(r"=-74.8\ \text{kJ/mol}", font_size=38,
                     color=T.result_final)
        r4 = Text("exothermic: methane lies lower in enthalpy than its "
                  "elements.", font_size=23, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        fit_width(rows, 11.4)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.5)
        box3 = SurroundingRectangle(r3, buff=0.18, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=1.0)
        self.wait(3.0)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.2)
        self.wait(3.4)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Hess's law states that the total enthalpy change of a reaction is "
     "the same whether it occurs in one step or in several steps. This "
     "works because enthalpy is a state function: it depends only on the "
     "initial and final states, not on the path.",
     "visual": {"style": "law", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "We want carbon plus two hydrogen giving methane. Reverse-engineer it "
     "from the three combustion equations. Equation one burns carbon to "
     "carbon dioxide. Equation two, used twice, burns the two hydrogens. "
     "Equation three burns methane, so we reverse it, which flips the "
     "sign of its enthalpy. The target equals equation one, plus two "
     "times equation two, minus equation three.",
     "visual": {"style": "combination", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Compute: minus three ninety three point five, plus two times minus "
     "two eighty five point eight, minus minus eight hundred ninety "
     "point three. That is minus three ninety three point five, minus "
     "five seventy one point six, plus eight hundred ninety point three, "
     "which gives minus seventy four point eight kilojoules per mole. "
     "The formation of methane is exothermic.",
     "visual": {"style": "computation", "transition": "fade"},
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
