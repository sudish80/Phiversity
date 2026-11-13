TITLE = "Q23 - LOCKED EQUATORIAL BROMIDE: NO E2, NO FLIP"

QUESTION = {
    "display":
        "Draw a bicyclic molecule with a bromine atom in an equatorial "
        "position. Explain why it cannot undergo E2 elimination and why "
        "it cannot flip to an axial position.",
    "speech":
        "Draw a bicyclic molecule with a bromine atom in an equatorial "
        "position, and explain why it cannot undergo E two elimination, "
        "and why it cannot flip to an axial position. The example is "
        "exo two bromo bicyclo two point two point one heptane, where the "
        "rigid cage locks the bromine and removes every anti periplanar "
        "beta hydrogen.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 23 - LOCKED EQUATORIAL Br", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = Text("exo-2-bromobicyclo[2.2.1]heptane", font_size=28,
                    color=T.constant)
        c_chem = Text("WHY NO E2", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "E2 needs anti-periplanar H-C-C-Br;\n"
            "equatorial Br has none available",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("WHY NO FLIP", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "the one-carbon bridge locks the cage;\n"
            "a chair flip would tear it apart",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("RESULT", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "the geometry is frozen; elimination\n"
            "is impossible in this conformation",
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
        self.wait(4.5)
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
        head = Text("Q23 - THE LOCKED CONFORMATION", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        cx = LEFT * 3.2 + DOWN * 0.5
        p1 = cx + UP * 1.2 + LEFT * 1.6
        p2 = cx + DOWN * 0.1 + LEFT * 1.6
        p3 = cx + DOWN * 1.4
        p4 = cx + DOWN * 0.1 + RIGHT * 1.6
        p5 = cx + UP * 1.2 + RIGHT * 1.6
        p6 = cx + UP * 2.2
        ring = VGroup(Line(p1, p2), Line(p2, p3), Line(p3, p4), Line(p4, p5),
                      Line(p5, p6), Line(p6, p1))
        ring.set_stroke(T.graph_function, 3)
        bridge = VGroup(Line(p1, cx + UP * 0.5), Line(cx + UP * 0.5, p4))
        bridge.set_stroke(T.graph_reference, 3)
        blab = MathTex(r"\mathrm{C7}", font_size=24, color=T.graph_reference)
        blab.next_to(cx + UP * 0.5, UP, buff=0.12)
        brdot = Dot(p2 + RIGHT * 1.05 + UP * 0.25, radius=0.13,
                    color=T.cancel_mark)
        brline = Line(p2, brdot.get_center(), color=T.cancel_mark,
                      stroke_width=3)
        brlab = MathTex(r"\mathrm{Br}\ \text{(equatorial/exo)}",
                        font_size=26, color=T.cancel_mark)
        brlab.next_to(brdot, RIGHT, buff=0.12)
        note = Text("cyclohexane chair + C7 bridge = norbornane cage",
                    font_size=22, color=T.text_secondary)
        note.move_to(RIGHT * 3.6 + UP * 1.5)
        fit_width(note, 6.2)
        note2 = Text("Br is locked exo (equatorial-like)", font_size=24,
                     color=T.cancel_mark)
        note2.next_to(note, DOWN, buff=0.5).align_to(note, LEFT)
        note3 = Text("both beta-H bonds (C1-H, C3-H)\nare pinned away: no "
                     "anti-periplanar partner", font_size=23,
                     color=T.text_primary)
        note3.next_to(note2, DOWN, buff=0.5).align_to(note, LEFT)
        fit_width(note3, 6.2)
        note3.align_to(note2, LEFT)
        self.play(Create(ring), run_time=1.8)
        self.play(Create(bridge), Write(blab), run_time=1.2)
        self.play(Create(brline), FadeIn(brdot), Write(brlab), run_time=1.2)
        self.play(FadeIn(note, shift=0.2 * UP), run_time=1.2)
        self.wait(2.4)
        self.play(FadeIn(note2, shift=0.2 * UP), run_time=1.1)
        self.wait(2.4)
        self.play(FadeIn(note3, shift=0.2 * UP), run_time=1.2)
        self.wait(3.4)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q23 - E2 NEEDS ANTI-PERIPLANAR GEOMETRY", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\mathrm{H}\ \text{and}\ \mathrm{Br}\ \text{must be "
                     r"anti}\ \left(180^{\circ}\right)", font_size=30,
                     color=T.text_primary)
        r2 = Text("in a chair, only an AXIAL leaving group has an "
                  "anti-periplanar beta-H.", font_size=24,
                  color=T.text_secondary)
        r3 = Text("here Br is equatorial/exo: the two beta-H bonds are "
                  "held away from 180 degrees by the cage.", font_size=24,
                  color=T.text_primary)
        r4 = MathTex(r"\Rightarrow\ \text{no suitable beta-H}\Rightarrow"
                     r"\ \text{no E2}", font_size=31, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.6)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.3)
        self.wait(2.8)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.4)
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
        head = Text("Q23 - WHY THE RING CANNOT FLIP", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("a cyclohexane chair flip passes through a half-chair "
                  "in which C1 and C4 move far apart.", font_size=24,
                  color=T.text_primary)
        r2 = Text("in norbornane the C7 bridge ties C1 to C4; widening "
                  "that distance would snap the bridge.", font_size=24,
                  color=T.text_primary)
        r3 = MathTex(r"\Rightarrow\ \text{cage is conformationally rigid}"
                     r"\Rightarrow\ \text{flip impossible}",
                     font_size=30, color=T.result_final)
        r4 = Text("so the molecule is stuck: Br stays equatorial for "
                  "good.", font_size=24, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(FadeIn(r1, shift=0.2 * UP), run_time=1.5)
        self.wait(3.0)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.5)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.16, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.1)
        self.wait(3.4)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q23 - SUMMARY", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{E2: no anti-periplanar beta-H}",
                     font_size=30, color=T.text_primary)
        r2 = MathTex(r"\text{flip: C7 bridge forbids the half-chair}",
                     font_size=30, color=T.text_primary)
        r3 = Text("contrast: in plain bromocyclohexane the ring flips "
                  "readily, so axial Br (5%) is always available and E2 "
                  "proceeds.", font_size=23, color=T.text_secondary)
        r4 = MathTex(r"\text{geometry frozen}\ \Rightarrow\ \text{no "
                     r"elimination}", font_size=32, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.6)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.5)
        self.wait(3.2)
        self.play(Write(r4), run_time=1.6)
        box4 = SurroundingRectangle(r4, buff=0.17, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=1.0)
        self.wait(4.0)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Draw norbornane as a cyclohexane chair with a one-carbon bridge, C "
     "seven, tying C one to C four. Put the bromine on C two in the exo "
     "position, which is the equatorial-like position. In this rigid "
     "cage the two beta hydrogens, on C one and C three, are pinned so "
     "that neither can align with the carbon bromine bond.",
     "visual": {"style": "cage diagram", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "E two elimination demands an anti-periplanar arrangement: the "
     "breaking C H and C Br bonds must be coplanar and point in opposite "
     "directions, one hundred eighty degrees apart. In a chair, only an "
     "axial leaving group has such a partner. Here bromine is "
     "equatorial, and the cage holds every beta hydrogen away from the "
     "required geometry. No anti-periplanar beta hydrogen, no E two.",
     "visual": {"style": "E2 requirement", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Could the ring flip and turn bromine axial? A chair flip passes "
     "through a half-chair in which C one and C four spread far apart. "
     "In norbornane the C seven bridge ties exactly those two carbons "
     "together, so widening their distance would tear the molecule "
     "apart. The cage is conformationally rigid, the flip is impossible, "
     "and bromine is stuck equatorial.",
     "visual": {"style": "flip blocked", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "Summary: E two is blocked for want of an anti-periplanar beta "
     "hydrogen, and the flip is blocked by the C seven bridge. The "
     "geometry is frozen, so no elimination is possible. In plain "
     "bromocyclohexane, by contrast, the ring flips freely and a small "
     "axial population is always available for E two.",
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
