TITLE = "Q29 - THREE PERIODIC TRENDS EXPLAINED"

QUESTION = {
    "display":
        "Explain: (i) the first ionization enthalpy of nitrogen is "
        "greater than that of oxygen; (ii) the electron gain enthalpy of "
        "fluorine is less negative than that of chlorine; (iii) the "
        "atomic radius of Ga is smaller than that of Al.",
    "speech":
        "Explain three trends. One: the first ionization enthalpy of "
        "nitrogen is greater than that of oxygen. Two: the electron gain "
        "enthalpy of fluorine is less negative than that of chlorine. "
        "Three: the atomic radius of gallium is smaller than that of "
        "aluminium.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 29 - PERIODIC TRENDS", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = Text("(i) N > O (IE1)   (ii) F vs Cl (egH)   "
                    "(iii) Ga < Al (radius)", font_size=27,
                    color=T.constant)
        c_chem = Text("(i) HALF-FILLED 2p3", font_size=20,
                      color=T.highlight_secondary)
        r_chem = Text(
            "N: 2p3 is exchange-stabilised;\n"
            "O: 2p4 has paired-electron repulsion",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("(ii) COMPACTNESS OF F", font_size=20,
                      color=T.highlight_secondary)
        r_math = Text(
            "2p shell of F is tiny: strong\n"
            "inter-electronic repulsion for e- gain",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("(iii) d-BLOCK CONTRACTION", font_size=20,
                      color=T.highlight_secondary)
        r_econ = Text(
            "Ga's 3d electrons shield poorly,\n"
            "raising the effective nuclear charge",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, chem, maths, econ).arrange(DOWN, aligned_edge=LEFT,
                                                       buff=0.34)
        rows.move_to(UP * 0.2)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=1.8)
        self.wait(4.5)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
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
        head = Text("Q29 - (i) WHY N LOSES AN ELECTRON LESS EASILY THAN O",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\mathrm{N}:\ 2p^{3}\ (\text{half-filled}),\qquad"
                     r"\mathrm{O}:\ 2p^{4}", font_size=31,
                     color=T.text_primary)
        r2 = Text("half-filled 2p3 has maximum exchange energy: all three "
                  "electrons in separate orbitals with parallel spins.",
                  font_size=23, color=T.text_secondary)
        r3 = Text("in O the fourth electron must pair up in one orbital; "
                  "the extra repulsion makes it easier to remove.",
                  font_size=23, color=T.text_primary)
        r4 = MathTex(r"\Rightarrow\ \mathrm{IE}_1(\mathrm{N})"
                     r">\mathrm{IE}_1(\mathrm{O})", font_size=32,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.8)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.5)
        self.wait(3.0)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.5)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.5)
        box4 = SurroundingRectangle(r4, buff=0.16, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q29 - (ii) WHY F GAINS AN ELECTRON LESS WILLINGLY",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\mathrm{F}:\ 2p^{5}\ \text{(tiny }n=2\text{ shell)},"
                     r"\qquad \mathrm{Cl}:\ 3p^{5}", font_size=29,
                     color=T.text_primary)
        r2 = Text("F's 2p orbitals are very compact, so the incoming "
                  "electron feels strong repulsion from the electrons "
                  "already there.", font_size=23, color=T.text_secondary)
        r3 = Text("Cl is larger: the added electron spreads out, "
                  "repulsion is smaller, so Cl's electron gain enthalpy "
                  "is more negative.", font_size=23, color=T.text_primary)
        r4 = MathTex(r"\Rightarrow\ \Delta_\text{eg}H(\mathrm{F})"
                     r"\ \text{less negative than}\ \mathrm{Cl}",
                     font_size=29, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.5)
        self.wait(3.0)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.5)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.6)
        box4 = SurroundingRectangle(r4, buff=0.16, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q29 - (iii) WHY Ga IS SMALLER THAN Al", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\mathrm{Al}:\ [\mathrm{Ne}]\,3s^{2}3p^{1},\qquad "
                     r"\mathrm{Ga}:\ [\mathrm{Ar}]\,3d^{10}4s^{2}4p^{1}",
                     font_size=27, color=T.text_primary)
        r2 = Text("Ga carries ten extra protons, but its ten 3d electrons "
                  "shield the outer 4p electron very poorly.",
                  font_size=23, color=T.text_secondary)
        r3 = Text("poor shielding raises the effective nuclear charge, "
                  "pulling the 4p electron in: the d-block contraction.",
                  font_size=23, color=T.text_primary)
        r4 = MathTex(r"\Rightarrow\ r(\mathrm{Ga})<r(\mathrm{Al})",
                     font_size=32, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.0)
        self.wait(2.8)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.5)
        self.wait(3.0)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.5)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.5)
        box4 = SurroundingRectangle(r4, buff=0.16, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Nitrogen's configuration is two p cubed, exactly half-filled: three "
     "electrons in three separate orbitals with parallel spins, giving "
     "maximum exchange energy. Oxygen is two p to the four, so the fourth "
     "electron must pair up, and the extra interelectronic repulsion "
     "makes it easier to remove. Hence the first ionization enthalpy of "
     "nitrogen is higher than that of oxygen, despite the trend.",
     "visual": {"style": "trend one", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Fluorine gains an electron into its tiny two p shell, where the "
     "incoming electron feels strong repulsion from the electrons already "
     "present. Chlorine receives the electron into a larger three p "
     "shell, where there is room to spread out, so the repulsion is "
     "smaller and the electron gain enthalpy is more negative. That is "
     "why fluorine's electron gain enthalpy is less negative than "
     "chlorine's.",
     "visual": {"style": "trend two", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Gallium has ten more protons than aluminium, but those ten three d "
     "electrons shield the outer four p electron very poorly, because d "
     "electrons are poor at screening. The higher effective nuclear "
     "charge pulls gallium's outer electrons in. This d-block "
     "contraction makes gallium slightly smaller than aluminium.",
     "visual": {"style": "trend three", "transition": "fade"},
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
