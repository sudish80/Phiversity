TITLE = "Q21 - A COMPOUND THAT PREFERS ITS ENOL FORM"

QUESTION = {
    "display":
        "Draw the keto form of a compound that exists primarily in the "
        "enol form. Explain why the enol is favored.",
    "speech":
        "Draw the keto form of a compound that exists primarily in the "
        "enol form, and explain why the enol is favoured. The classic "
        "example is pentane two four dione, also called acetylacetone, "
        "which is roughly eighty percent enol at equilibrium.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 21 - KETO-ENOL EQUILIBRIUM", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"\mathrm{CH_3COCH_2COCH_3}\ \rightleftharpoons\ "
            r"\mathrm{CH_3C(OH){=}CHCOCH_3}",
            font_size=30, color=T.constant)
        c_chem = Text("COMPOUND", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "pentane-2,4-dione (acetylacetone)\n"
            "about 80% enol in the pure liquid",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("WHY ENOL WINS", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "intramolecular H-bond (six-membered ring)\n"
            "plus C=C conjugation with C=O",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("ALSO", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "the central CH2 is doubly activated,\n"
            "so the enolic H is easy to place",
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
        head = Text("Q21 - KETO AND ENOL FORMS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        cx = DOWN * 0.5
        x1 = cx + LEFT * 4.4
        x2 = cx + LEFT * 2.7
        x3 = cx + LEFT * 1.0
        x4 = cx + RIGHT * 0.7
        x5 = cx + RIGHT * 2.4
        o1 = x2 + UP * 1.5
        o4 = x4 + UP * 1.5
        seg_keto = VGroup(
            Line(x1, x2), Line(x2, x3), Line(x3, x4), Line(x4, x5),
            DoubleArrow(x2, o1, buff=0.05), DoubleArrow(x4, o4, buff=0.05))
        seg_keto.set_stroke(T.graph_function, 3.5)
        l1 = MathTex(r"\mathrm{CH_3}", font_size=27, color=T.text_primary)
        l1.next_to(x1, DOWN, buff=0.12)
        l2 = MathTex(r"\mathrm{C}", font_size=27, color=T.text_primary)
        l2.next_to(x2, DOWN, buff=0.12)
        l3 = MathTex(r"\mathrm{CH_2}", font_size=27, color=T.text_primary)
        l3.next_to(x3, DOWN, buff=0.12)
        l4 = MathTex(r"\mathrm{C}", font_size=27, color=T.text_primary)
        l4.next_to(x4, DOWN, buff=0.12)
        l5 = MathTex(r"\mathrm{CH_3}", font_size=27, color=T.text_primary)
        l5.next_to(x5, DOWN, buff=0.12)
        o1l = MathTex(r"\mathrm{O}", font_size=27, color=T.cancel_mark)
        o1l.next_to(o1, UP, buff=0.1)
        o4l = MathTex(r"\mathrm{O}", font_size=27, color=T.cancel_mark)
        o4l.next_to(o4, UP, buff=0.1)
        klab = Text("keto form", font_size=24, color=T.graph_function)
        klab.next_to(l3, DOWN, buff=0.35)
        arrow = MathTex(r"\rightleftharpoons", font_size=46,
                        color=T.highlight_primary)
        arrow.move_to(RIGHT * 0.1 + UP * 0.1)
        enol = MathTex(
            r"\mathrm{CH_3C(OH){=}CH{-}C(=O)CH_3}", font_size=30,
            color=T.result_final)
        enol.move_to(RIGHT * 3.4 + DOWN * 1.4)
        elab = Text("enol form (about 80%)", font_size=24,
                    color=T.result_final)
        elab.next_to(enol, DOWN, buff=0.3)
        self.play(Create(seg_keto), run_time=1.8)
        self.play(Write(l1), Write(l2), Write(l3), Write(l4), Write(l5),
                  Write(o1l), Write(o4l), run_time=1.6)
        self.play(FadeIn(klab, shift=0.2 * UP), run_time=1.0)
        self.wait(2.6)
        self.play(Write(arrow), run_time=1.0)
        self.play(Write(enol), run_time=1.6)
        self.play(FadeIn(elab, shift=0.2 * UP), run_time=1.0)
        self.wait(3.4)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q21 - WHY THE ENOL IS FAVOURED", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{1. six-membered H-bond ring: }"
                     r"\mathrm{O{-}H\cdots O{=}C}", font_size=29,
                     color=T.text_primary)
        r2 = Text("the enol OH hydrogen bonds to the other carbonyl "
                  "oxygen, closing a stable six-membered pseudo-ring.",
                  font_size=23, color=T.text_secondary)
        r3 = MathTex(r"\text{2. conjugation: }"
                     r"\mathrm{C{=}C{-}C{=}O}\ \text{delocalised}",
                     font_size=29, color=T.text_primary)
        r4 = Text("the enol double bond is conjugated with the remaining "
                  "carbonyl, giving extra resonance stabilisation.",
                  font_size=23, color=T.text_secondary)
        r5 = MathTex(r"\text{3. two carbonyls make the CH}_2"
                     r"\ \text{strongly acidic}", font_size=29,
                     color=T.text_primary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.4)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.4)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.6)
        self.wait(2.4)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.4)
        self.wait(2.6)
        self.play(Write(r5), run_time=1.6)
        box5 = SurroundingRectangle(r5, buff=0.14, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        self.wait(3.4)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q21 - SUMMARY", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("ordinary ketones: enol is a trace species (< 1%).",
                  font_size=25, color=T.text_primary)
        r2 = Text("acetylacetone: H-bond ring + conjugation + double "
                  "activation stack up,", font_size=25, color=T.text_primary)
        r3 = MathTex(r"\approx 80\%\ \text{enol at equilibrium}",
                     font_size=34, color=T.result_final)
        r4 = Text("similar behaviour: 1,3-cyclohexanedione, dimedone.",
                  font_size=23, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(FadeIn(r1, shift=0.2 * UP), run_time=1.3)
        self.wait(2.8)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.3)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.5)
        box3 = SurroundingRectangle(r3, buff=0.18, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=1.0)
        self.wait(3.4)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.1)
        self.wait(3.4)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "The keto form of the classic example, pentane two four dione, is "
     "methyl C O, C H two, C O methyl: a one three diketone. In solution "
     "and in the pure liquid it equilibrates with its enol, methyl C, "
     "O H, double bond C H, C O methyl. Unusually, the equilibrium lies "
     "about eighty percent on the enol side.",
     "visual": {"style": "structures", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Why does the enol win here when it loses for almost every other "
     "ketone? Three reasons stack up. First, the O H of the enol hydrogen "
     "bonds intramolecularly to the other carbonyl oxygen, closing a "
     "stable six-membered pseudo ring. Second, the enol C double bond C "
     "is conjugated with the remaining C double bond O, which gives extra "
     "resonance stabilisation. Third, the central C H two is flanked by "
     "two carbonyls, so it is strongly acidic and the proton transfers "
     "easily.",
     "visual": {"style": "reasons", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "To put the number in perspective: for an ordinary ketone the enol "
     "is a trace species, well under one percent. In acetylacetone the "
     "hydrogen bond, the conjugation and the double activation push the "
     "equilibrium to about eighty percent enol. One three cyclohexane "
     "dione and dimedone behave the same way.",
     "visual": {"style": "summary", "transition": "fade"},
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
