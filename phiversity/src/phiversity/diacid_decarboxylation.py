TITLE = "Q22 - WHY 1,3-DIACIDS DECARBOXYLATE BUT 1,4-DIACIDS DO NOT"

QUESTION = {
    "display":
        "Draw the structures of a 1,3-dicarboxylic acid and a "
        "1,4-dicarboxylic acid. Explain why the 1,3-diacid undergoes "
        "decarboxylation relatively easily but the 1,4-diacid does not.",
    "speech":
        "Draw the structures of a one three dicarboxylic acid and a one "
        "four dicarboxylic acid. Explain why the one three diacid "
        "undergoes decarboxylation relatively easily, but the one four "
        "diacid does not. The answer lies in the geometry of the cyclic "
        "transition state: only the one three acid can close a "
        "six-membered ring.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 22 - DECARBOXYLATION", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"\mathrm{HOOC{-}CH_2{-}COOH}\qquad\qquad"
            r"\mathrm{HOOC{-}CH_2{-}CH_2{-}COOH}",
            font_size=28, color=T.constant)
        c_chem = Text("1,3-DIACID", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "malonic acid: six-membered cyclic TS\n"
            "CH3COOH + CO2 at about 140 C",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("1,4-DIACID", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "succinic acid: TS would be eight-membered\n"
            "so it dehydrates to an anhydride instead",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("RULE", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "decarboxylation needs a beta-H held\n"
            "by a six-membered cyclic TS",
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
        self.wait(5.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(5.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q22 - THE TWO DIACIDS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        a1 = MathTex(r"\mathrm{HOOC{-}CH_2{-}COOH}", font_size=32,
                     color=T.text_primary)
        a2 = Text("malonic acid (1,3-diacid)", font_size=23,
                  color=T.graph_function)
        b1 = MathTex(r"\mathrm{HOOC{-}CH_2{-}CH_2{-}COOH}", font_size=32,
                     color=T.text_primary)
        b2 = Text("succinic acid (1,4-diacid)", font_size=23,
                  color=T.graph_reference)
        left = VGroup(a1, a2).arrange(DOWN, buff=0.25)
        right = VGroup(b1, b2).arrange(DOWN, buff=0.25)
        left.move_to(LEFT * 3.0 + UP * 0.4)
        right.move_to(RIGHT * 3.0 + UP * 0.4)
        self.play(Write(a1), run_time=1.5)
        self.play(FadeIn(a2, shift=0.2 * UP), run_time=1.0)
        self.wait(2.6)
        self.play(Write(b1), run_time=1.7)
        self.play(FadeIn(b2, shift=0.2 * UP), run_time=1.0)
        self.wait(2.6)
        note = Text("malonic: carboxyls separated by ONE carbon;"
                    "\nsuccinic: separated by TWO carbons", font_size=24,
                    color=T.text_secondary)
        note.move_to(DOWN * 2.3)
        fit_width(note, 12.0)
        self.play(FadeIn(note, shift=0.2 * UP), run_time=1.2)
        self.wait(3.6)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q22 - MALONIC ACID: SIX-MEMBERED CYCLIC TS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        cx = LEFT * 3.2 + DOWN * 0.5
        ring = Polygon(
            cx + UP * 1.6, cx + RIGHT * 1.15 + UP * 0.85,
            cx + RIGHT * 1.15 + DOWN * 0.85, cx + DOWN * 1.6,
            cx + LEFT * 1.15 + DOWN * 0.85, cx + LEFT * 1.15 + UP * 0.85)
        ring.set_stroke(T.graph_function, 3)
        ring.set_fill(T.graph_function, 0.12)
        tlab = Text("cyclic transition state", font_size=21,
                    color=T.graph_function)
        tlab.move_to(cx)
        hb = MathTex(r"\mathrm{O{-}H\cdots O{=}C}", font_size=25,
                     color=T.cancel_mark)
        hb.next_to(ring, UP, buff=0.2)
        r1 = MathTex(r"\mathrm{HOOC{-}CH_2{-}COOH}\ \rightarrow\ "
                     r"\mathrm{CH_3COOH}+\mathrm{CO_2}", font_size=30,
                     color=T.result_final)
        r1.move_to(RIGHT * 3.4 + UP * 1.4)
        fit_width(r1, 6.4)
        r2 = Text("a beta-H is carried to a carboxyl oxygen\nthrough a "
                  "six-membered cyclic TS", font_size=23,
                  color=T.text_secondary)
        r2.move_to(RIGHT * 3.4 + UP * 0.1)
        r3 = Text("concerted C-C cleavage and CO2 loss;\nproducts: acetic "
                  "acid + CO2", font_size=23, color=T.text_primary)
        r3.move_to(RIGHT * 3.4 + DOWN * 1.0)
        self.play(DrawBorderThenFill(ring), run_time=1.8)
        self.play(Write(tlab), Write(hb), run_time=1.3)
        self.wait(2.6)
        self.play(Write(r1), run_time=1.7)
        box1 = SurroundingRectangle(r1, buff=0.15, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.2)
        self.wait(2.6)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.2)
        self.wait(3.4)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q22 - SUCCINIC ACID: THE TS WOULD NEED 8 MEMBERS",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("succinic acid has no beta-H at the right distance:", font_size=24,
                  color=T.text_secondary)
        r2 = MathTex(r"\mathrm{HOOC{-}CH_2{-}CH_2{-}COOH}", font_size=31,
                     color=T.text_primary)
        r3 = Text("decarboxylation would need an eight-membered cyclic "
                  "TS: entropically and geometrically unfavourable.",
                  font_size=24, color=T.text_primary)
        r4 = MathTex(r"\mathrm{2\,HOOC{-}CH_2{-}CH_2{-}COOH}\ \rightarrow\ "
                     r"\text{succinic anhydride}+\mathrm{H_2O}",
                     font_size=28, color=T.result_intermediate)
        r5 = Text("on heating it dehydrates to the anhydride instead of "
                  "losing CO2.", font_size=23, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(FadeIn(r1, shift=0.2 * UP), run_time=1.2)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.6)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.5)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.7)
        box4 = SurroundingRectangle(r4, buff=0.15, color=T.result_intermediate)
        self.play(Create(box4), run_time=0.7)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.2)
        self.wait(3.4)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q22 - SUMMARY", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("decarboxylation of beta-keto acids and malonic acids "
                  "is a six-membered-ring process.", font_size=24,
                  color=T.text_primary)
        r2 = MathTex(r"\text{1,3:}\ 6\text{-membered TS}\Rightarrow"
                     r"\text{easy}\qquad"
                     r"\text{1,4:}\ 8\text{-membered TS}\Rightarrow"
                     r"\text{no}", font_size=29, color=T.result_final)
        r3 = Text("same reason acetoacetic acid decarboxylates to acetone.",
                  font_size=23, color=T.text_secondary)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.6)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(FadeIn(r1, shift=0.2 * UP), run_time=1.4)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.8)
        box2 = SurroundingRectangle(r2, buff=0.16, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=1.0)
        self.wait(3.2)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.1)
        self.wait(3.6)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "The one three diacid is malonic acid, H O O C, C H two, C O O H: two "
     "carboxyl groups separated by a single carbon. The one four diacid "
     "is succinic acid, H O O C, C H two, C H two, C O O H: the carboxyls "
     "are separated by two carbons. That one-carbon difference decides "
     "everything.",
     "visual": {"style": "structures", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Malonic acid decarboxylates easily, at about one hundred forty "
     "degrees, giving acetic acid and carbon dioxide. The mechanism is "
     "concerted: a beta hydrogen is transferred onto a carboxyl oxygen "
     "while the carbon carbon bond breaks, all through a six-membered "
     "cyclic transition state. Six-membered rings are close to "
     "strain-free, so the barrier is low.",
     "visual": {"style": "cyclic TS", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Succinic acid cannot use that pathway. Its hydrogen sits one carbon "
     "too far from the carboxyl, so the cyclic transition state would "
     "have to be eight-membered, which is geometrically and entropically "
     "unfavourable. On heating, succinic acid therefore loses water "
     "instead, forming succinic anhydride, a five-membered ring.",
     "visual": {"style": "no decarboxylation", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "In summary: decarboxylation needs a beta hydrogen carried through a "
     "six-membered cyclic transition state. The one three diacid can "
     "close that ring, so it decarboxylates easily; the one four diacid "
     "cannot, so it does not. The same rule explains why acetoacetic "
     "acid decarboxylates to acetone.",
     "visual": {"style": "summary", "transition": "fade"},
     "code": SEG3},
]

LECTURE = {
    "title": TITLE,
    "preset": "lab",
    "format": "mixed",
    "question": QUESTION,
    "question_code": QUESTION_CODE,
    "segments": SEGMENTS,
}
