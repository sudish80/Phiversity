TITLE = "Q33 - LAW OF MASS ACTION AND THE AMMONIA EQUILIBRIUM"

QUESTION = {
    "display":
        "(i) State the law of mass action and derive Kc for "
        "N2(g) + 3H2(g) <=> 2NH3(g). (ii) At 500 K, Kc = 0.061. If the "
        "equilibrium concentrations are [N2] = 0.5 M and [H2] = 0.3 M, "
        "calculate [NH3].",
    "speech":
        "State the law of mass action and derive the equilibrium constant "
        "expression for N two plus three H two in equilibrium with two N H "
        "three. Then, at five hundred kelvin the equilibrium constant is "
        "zero point zero six one. If the equilibrium concentrations of N "
        "two and H two are zero point five and zero point three molar, "
        "calculate the concentration of ammonia.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 33 - LAW OF MASS ACTION", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"\mathrm{N_2}+3\mathrm{H_2}\rightleftharpoons2\mathrm{NH_3},"
            r"\qquad K_c=0.061\ \text{at}\ 500\,\text{K}", font_size=29,
            color=T.constant)
        c_chem = Text("LAW", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "rate is proportional to the product\n"
            "of the concentrations, each raised\n"
            "to its stoichiometric power",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("EXPRESSION", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "Kc = [NH3]^2 / ([N2] [H2]^3)",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("ANSWER", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "[NH3] = about 0.029 M",
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
        self.wait(6.5)
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
        head = Text("Q33 - LAW OF MASS ACTION", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("the rate of a reaction is proportional to the product "
                  "of the molar concentrations", font_size=24,
                  color=T.text_primary)
        r2 = Text("of the reactants, each raised to the power of its "
                  "stoichiometric coefficient.", font_size=24,
                  color=T.text_primary)
        r3 = MathTex(r"r_f=k_f[\mathrm{N_2}][\mathrm{H_2}]^{3},\qquad "
                     r"r_b=k_b[\mathrm{NH_3}]^{2}", font_size=30,
                     color=T.text_secondary)
        r4 = MathTex(r"\text{at equilibrium }r_f=r_b\Rightarrow "
                     r"\frac{k_f}{k_b}=\frac{[\mathrm{NH_3}]^{2}}"
                     r"{[\mathrm{N_2}][\mathrm{H_2}]^{3}}",
                     font_size=28, color=T.text_primary)
        r5 = MathTex(r"K_c=\frac{[\mathrm{NH_3}]^{2}}"
                     r"{[\mathrm{N_2}][\mathrm{H_2}]^{3}}", font_size=34,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 12.4)
        rows.next_to(rule, DOWN, buff=0.36)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(FadeIn(r1, shift=0.2 * UP), run_time=1.4)
        self.wait(2.6)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.4)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.8)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.9)
        self.wait(2.6)
        self.play(Write(r5), run_time=1.7)
        box5 = SurroundingRectangle(r5, buff=0.16, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q33 - SOLVE FOR [NH3]", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"[\mathrm{NH_3}]^{2}=K_c[\mathrm{N_2}][\mathrm{H_2}]^{3}",
                     font_size=32, color=T.text_primary)
        r2 = MathTex(r"=0.061\times0.5\times(0.3)^{3}", font_size=31,
                     color=T.text_primary)
        r3 = MathTex(r"=0.061\times0.5\times0.027"
                     r"=8.235\times10^{-4}", font_size=31,
                     color=T.text_primary)
        r4 = MathTex(r"[\mathrm{NH_3}]=\sqrt{8.235\times10^{-4}}"
                     r"\approx 0.029\,\text{M}", font_size=33,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.7)
        box4 = SurroundingRectangle(r4, buff=0.17, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "The law of mass action says the rate of a reaction is proportional "
     "to the product of the molar concentrations of the reactants, each "
     "raised to the power of its stoichiometric coefficient. For the "
     "ammonia synthesis, the forward rate is k f times N two times H two "
     "cubed, and the reverse rate is k b times N H three squared. At "
     "equilibrium the rates match, so K c equals k f over k b, which is "
     "N H three squared over N two times H two cubed.",
     "visual": {"style": "law and derivation", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Now insert the numbers. N H three squared equals zero point zero "
     "six one, times zero point five, times zero point three cubed. Zero "
     "point three cubed is zero point zero two seven. Multiplying gives "
     "eight point two three five times ten to the minus four. The square "
     "root is about zero point zero two nine molar. So the equilibrium "
     "concentration of ammonia is about zero point zero two nine molar.",
     "visual": {"style": "computation", "transition": "fade"},
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
