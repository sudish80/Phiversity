TITLE = "Q28 - ENERGY TO IONISE THE n=2 STATE OF HYDROGEN"

QUESTION = {
    "display":
        "The ionization enthalpy of the hydrogen atom is 1.312 x 10^6 "
        "J/mol. The energy of the electron in the n=2 state is -3.28 x "
        "10^5 J/mol. Calculate the energy required to remove the "
        "electron from the n=2 state.",
    "speech":
        "The ionization enthalpy of the hydrogen atom is one point three "
        "one two times ten to the six joules per mole. The energy of the "
        "electron in the n equals two state is minus three point two "
        "eight times ten to the five joules per mole. Calculate the "
        "energy required to remove the electron from the n equals two "
        "state. The answer is plus three point two eight times ten to the "
        "five joules per mole.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 28 - IONISATION FROM n=2", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"\mathrm{IE}_1=1.312\times10^{6}\,\text{J/mol},\quad "
            r"E_{2}=-3.28\times10^{5}\,\text{J/mol}", font_size=29,
            color=T.constant)
        c_chem = Text("IDEA", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "removing the electron takes it\n"
            "from E(2) to 0 (free electron)",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("CONSISTENCY CHECK", font_size=20,
                      color=T.highlight_secondary)
        r_math = Text(
            "E(n) = -IE/n^2:\n"
            "-1.312e6 / 4 = -3.28e5 (matches)",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("ANSWER", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "+3.28 x 10^5 J/mol",
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
        self.wait(5.0)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=0.9)
        self.wait(5.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q28 - THE LEVEL DIAGRAM", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        zero = Line(LEFT * 3.0, RIGHT * 3.0, color=T.result_final,
                    stroke_width=2.5)
        zero.move_to(UP * 1.7)
        zl = MathTex(r"E=0\ \text{(free electron)}", font_size=24,
                     color=T.result_final)
        zl.next_to(zero, UP, buff=0.12)
        e1 = Line(LEFT * 3.0, RIGHT * 3.0, color=T.graph_function,
                  stroke_width=2.5)
        e1.move_to(DOWN * 2.4)
        l1 = MathTex(r"n=1:\ -1.312\times10^{6}\,\text{J/mol}",
                     font_size=24, color=T.graph_function)
        l1.next_to(e1, DOWN, buff=0.12)
        e2 = Line(LEFT * 3.0, RIGHT * 3.0, color=T.highlight_primary,
                  stroke_width=2.5)
        e2.move_to(DOWN * 0.6)
        l2 = MathTex(r"n=2:\ -3.28\times10^{5}\,\text{J/mol}",
                     font_size=24, color=T.highlight_primary)
        l2.next_to(e2, UP, buff=0.12)
        arr = DoubleArrow(LEFT * 3.0 + UP * 1.7, LEFT * 3.0 + DOWN * 0.6,
                          color=T.cancel_mark, buff=0.0)
        alab = MathTex(r"\Delta E=?", font_size=27, color=T.cancel_mark)
        alab.next_to(arr, LEFT, buff=0.2)
        self.play(Create(zero), Write(zl), run_time=1.2)
        self.play(Create(e2), Write(l2), run_time=1.2)
        self.wait(2.4)
        self.play(Create(e1), Write(l1), run_time=1.2)
        self.wait(2.4)
        self.play(Create(arr), Write(alab), run_time=1.2)
        self.wait(3.6)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q28 - THE IONISATION ENERGY FROM n=2", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\Delta E=E_{\infty}-E_{2}=0-(-3.28\times10^{5})",
                     font_size=32, color=T.text_primary)
        r2 = MathTex(r"=+3.28\times10^{5}\ \text{J/mol}", font_size=36,
                     color=T.result_final)
        r3 = MathTex(r"E(n)=-\frac{\mathrm{IE}}{n^{2}}:\quad"
                     r"-\frac{1.312\times10^{6}}{4}"
                     r"=-3.28\times10^{5}\ \checkmark", font_size=28,
                     color=T.text_secondary)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.6)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.6)
        box2 = SurroundingRectangle(r2, buff=0.18, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=1.0)
        self.wait(3.0)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.4)
        self.wait(3.6)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "The energy scale starts at zero for a free electron. The n equals "
     "one level sits at minus one point three one two times ten to the "
     "six joules per mole, since removing the ground-state electron "
     "costs exactly that. The n equals two level sits at minus three "
     "point two eight times ten to the five. The gap from n equals two "
     "up to zero is the quantity we want.",
     "visual": {"style": "level diagram", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "The energy to remove the n equals two electron is zero minus minus "
     "three point two eight times ten to the five, which is plus three "
     "point two eight times ten to the five joules per mole. As a "
     "consistency check, the level formula E of n equals minus I E over n "
     "squared gives minus one point three one two times ten to the six "
     "divided by four, which is exactly the given n equals two energy.",
     "visual": {"style": "answer", "transition": "fade"},
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
