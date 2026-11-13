TITLE = "Q20 - WHY 1-BROMOBICYCLO[2.2.1]HEPTANE IS INERT"

QUESTION = {
    "display":
        "Draw 1-bromobicyclo[2.2.1]heptane. Explain why it is extremely "
        "unreactive in both SN1 and SN2 reactions.",
    "speech":
        "Draw one bromo bicyclo two point two point one heptane. Explain "
        "why it is extremely unreactive in both S N one and S N two "
        "reactions. The key facts: the bromine sits on a bridgehead carbon "
        "of a rigid, small bicyclic cage.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 20 - BRIDGED HALIDE", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = Text("1-bromobicyclo[2.2.1]heptane", font_size=28,
                    color=T.constant)
        c_chem = Text("SN1", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "bridgehead carbocation cannot\n"
            "planarise (Bredt's rule)",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("SN2", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "backside attack blocked by\n"
            "the rigid cage; inversion impossible",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("RESULT", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "unreactive in both pathways",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, chem, maths, econ).arrange(DOWN, aligned_edge=LEFT,
                                                       buff=0.34)
        rows.move_to(UP * 0.2)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=1.6)
        self.wait(4.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
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
        head = Text("Q20 - THE CAGE: 1-BROMONORBORNANE", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        cx = LEFT * 3.2 + DOWN * 0.4
        p1 = cx + UP * 1.35 + LEFT * 1.5
        p4 = cx + UP * 1.35 + RIGHT * 1.5
        p2 = cx + DOWN * 0.1 + LEFT * 1.9
        p3 = cx + DOWN * 0.1 + RIGHT * 1.9
        p5 = cx + DOWN * 1.7 + LEFT * 1.9
        p6 = cx + DOWN * 1.7 + RIGHT * 1.9
        p7 = cx + UP * 2.5
        cage = VGroup(
            Line(p1, p2), Line(p2, p3), Line(p3, p4),
            Line(p4, p6), Line(p6, p5), Line(p5, p2),
            Line(p3, p6), Line(p1, p7), Line(p7, p4))
        cage.set_stroke(T.graph_function, 3)
        br = Dot(p1 + UP * 0.75 + LEFT * 0.15, radius=0.14,
                 color=T.cancel_mark)
        brline = Line(p1, br.get_center(), color=T.cancel_mark, stroke_width=3)
        brlab = MathTex(r"\mathrm{Br}", font_size=30, color=T.cancel_mark)
        brlab.next_to(br, UP, buff=0.1)
        c1 = MathTex(r"\mathrm{C1}", font_size=26, color=T.highlight_primary)
        c1.next_to(p1, LEFT, buff=0.2)
        c7 = MathTex(r"\mathrm{C7}", font_size=24, color=T.text_secondary)
        c7.next_to(p7, UP, buff=0.12)
        c4 = MathTex(r"\mathrm{C4}", font_size=26, color=T.text_secondary)
        c4.next_to(p4, RIGHT, buff=0.2)
        blab = Text("bridgeheads C1 and C4;\nthree bridges: 2, 2 and 1 "
                    "carbons", font_size=22, color=T.text_secondary)
        blab.move_to(RIGHT * 3.4 + UP * 0.6)
        fit_width(blab, 6.0)
        note = Text("Br sits on bridgehead C1", font_size=24,
                    color=T.cancel_mark)
        note.next_to(blab, DOWN, buff=0.4).align_to(blab, LEFT)
        note2 = Text("the cage is rigid: no ring flipping", font_size=24,
                     color=T.text_primary)
        note2.next_to(note, DOWN, buff=0.35).align_to(blab, LEFT)
        self.play(Create(cage), run_time=2.0)
        self.play(Write(c1), Write(c4), Write(c7), run_time=1.2)
        self.play(Create(brline), FadeIn(br), Write(brlab), run_time=1.2)
        self.play(FadeIn(blab, shift=0.2 * UP), run_time=1.2)
        self.wait(2.4)
        self.play(FadeIn(note, shift=0.2 * UP), run_time=1.1)
        self.wait(2.4)
        self.play(FadeIn(note2, shift=0.2 * UP), run_time=1.1)
        self.wait(3.4)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q20 - WHY NO SN1", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\mathrm{R-Br}\rightarrow \mathrm{R}^{+}+\mathrm{Br}^{-}",
                     font_size=32, color=T.text_primary)
        r2 = Text("SN1 needs a planar sp2 carbocation:", font_size=24,
                  color=T.text_secondary)
        r3 = MathTex(r"\mathrm{C}^{+}\text{ must be }sp^{2}\text{ with a "
                     r"free }p\text{ orbital}", font_size=29,
                     color=T.text_primary)
        r4 = Text("at a bridgehead of a small cage the bonds are locked; "
                  "the carbon cannot flatten, so the empty p orbital "
                  "cannot align with the framework.", font_size=24,
                  color=T.text_primary)
        r5 = MathTex(r"\Rightarrow\ \text{Bredt's rule: no bridgehead "
                     r"cation}\ \Rightarrow\ \text{no SN1}", font_size=29,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.5)
        self.wait(2.8)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.0)
        self.play(Write(r3), run_time=1.5)
        self.wait(2.6)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.6)
        self.wait(3.2)
        self.play(Write(r5), run_time=1.7)
        box5 = SurroundingRectangle(r5, buff=0.15, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q20 - WHY NO SN2", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("SN2 needs backside attack along the C-Br axis:", font_size=24,
                  color=T.text_secondary)
        r2 = MathTex(r"\mathrm{Nu}^{-}\to \mathrm{C}\leftarrow \mathrm{Br}",
                     font_size=31, color=T.text_primary)
        r3 = Text("on a bridgehead the backside is inside the cage: the "
                  "three bridges block the trajectory completely.",
                  font_size=24, color=T.text_primary)
        r4 = Text("SN2 also requires inversion at carbon; a bridgehead "
                  "cannot invert inside a small rigid cage.", font_size=24,
                  color=T.text_primary)
        r5 = MathTex(r"\Rightarrow\ \text{no backside access and no "
                     r"inversion}\ \Rightarrow\ \text{no SN2}",
                     font_size=29, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(FadeIn(r1, shift=0.2 * UP), run_time=1.1)
        self.play(Write(r2), run_time=1.5)
        self.wait(2.8)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.5)
        self.wait(3.0)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.5)
        self.wait(3.0)
        self.play(Write(r5), run_time=1.7)
        box5 = SurroundingRectangle(r5, buff=0.15, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q20 - SUMMARY", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{SN1: cation cannot planarise (Bredt)}",
                     font_size=30, color=T.text_primary)
        r2 = MathTex(r"\text{SN2: backside blocked, inversion impossible}",
                     font_size=30, color=T.text_primary)
        r3 = Text("both ionisation and displacement are shut off, so the "
                  "halide is stable even in boiling ethanolic silver "
                  "nitrate.", font_size=24, color=T.text_secondary)
        r4 = MathTex(r"\text{unreactive in both SN1 and SN2}", font_size=34,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.6)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.4)
        self.wait(3.2)
        self.play(Write(r4), run_time=1.5)
        box4 = SurroundingRectangle(r4, buff=0.18, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Bicyclo two point two point one heptane, also called norbornane, has "
     "two bridgehead carbons, C one and C four, joined by three bridges of "
     "two, two and one carbons. In the one bromo compound the bromine sits "
     "on bridgehead C one. The cage is completely rigid, so the geometry "
     "at C one is fixed and cannot relax.",
     "visual": {"style": "cage diagram", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "For S N one, ionisation would give a carbocation at C one. A "
     "carbocation must be planar, with an empty p orbital standing "
     "perpendicular to three coplanar bonds. At a bridgehead of a small "
     "bicyclic cage the three bonds are pinned together and the carbon "
     "cannot flatten, so the cation cannot form. This is Bredt's rule "
     "applied to cations. No cation, no S N one.",
     "visual": {"style": "SN1", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "For S N two, the nucleophile must attack from directly behind the "
     "carbon along the carbon bromine bond axis. On a bridgehead that "
     "backside region is inside the cage, completely blocked by the three "
     "bridges. On top of that, S N two requires Walden inversion, and a "
     "bridgehead carbon cannot invert inside a rigid cage. No backside "
     "access and no inversion, so no S N two.",
     "visual": {"style": "SN2", "transition": "carry-over"},
     "code": SEG2},
    {"narration":
     "In summary, S N one is blocked because the bridgehead cation cannot "
     "planarise, and S N two is blocked because backside attack is "
     "impossible and inversion cannot occur. Both substitution pathways "
     "are shut off at once, which is why one bromo bicyclo two point two "
     "point one heptane is extremely unreactive.",
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
