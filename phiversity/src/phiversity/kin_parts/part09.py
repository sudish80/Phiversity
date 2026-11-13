PART = [
{
 "narration":
  "Constraints are geometric conditions that link the motions of "
  "connected bodies. For an inextensible string, the length is "
  "constant, so the displacements of the two ends are equal in "
  "magnitude along the string; that gives the constraint equation. "
  "For a block on a wedge, the block must stay on the surface, so "
  "its motion normal to the wedge is zero. Writing these relations "
  "is the first step in every connected-body problem.",
 "visual": {"style": "constraints", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment49(Scene):
    def construct(self):
        head = Text("LESSON 50 - CONSTRAINT EQUATIONS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{inextensible string: }L=\text{const}",
                     font_size=30, color=T.result_final)
        r2 = MathTex(r"\text{ends: }x_A+x_B=\text{const}\ \Rightarrow\ "
                     r"\dot x_A+\dot x_B=0", font_size=29,
                     color=T.result_final)
        r3 = MathTex(r"\text{wedge: }a_{\text{normal}}=0\ \text{(stay on surface)}",
                     font_size=29, color=T.result_intermediate)
        r4 = MathTex(r"\text{count unknowns; write one constraint per contact}",
                     font_size=27, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.8)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.5)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "A fixed pulley redirects a string but does not change lengths, so "
  "the two hanging ends move with equal and opposite accelerations "
  "if one end goes down. A movable pulley changes the geometry: the "
  "pulley's displacement is the average of the two string ends, so "
  "the block attached to the pulley moves half as far as the pulled "
  "end. These ratios are the heart of pulley kinematics.",
 "visual": {"style": "pulleys", "transition": "fade"},
 "code": r'''
from manim import *


class Segment50(Scene):
    def construct(self):
        head = Text("LESSON 51 - FIXED AND MOVABLE PULLEYS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{fixed: }a_1=-a_2", font_size=31,
                     color=T.result_final)
        r2 = MathTex(r"\text{movable: }x_p=\frac{x_1+x_2}{2}\ "
                     r"\Rightarrow\ a_p=\frac{a_1+a_2}{2}", font_size=29,
                     color=T.result_final)
        r3 = MathTex(r"\text{pulled end moves }2x_p", font_size=29,
                     color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.46)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.9)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r3), run_time=1.6)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "Multiple-pulley systems are solved by drawing the string path and "
  "writing one constraint per string segment. Each movable pulley "
  "halves the relation between the pulled end and the load. For a "
  "string wound around several pulleys, the displacement of the load "
  "is the pulled displacement divided by the number of supporting "
  "string segments. Counting the supporting segments gives the "
  "mechanical advantage and the kinematic ratio at once.",
 "visual": {"style": "multiple pulleys", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment51(Scene):
    def construct(self):
        head = Text("LESSON 52 - MULTIPLE PULLEY SYSTEMS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{one constraint per string segment}", font_size=30,
                     color=T.text_primary)
        r2 = MathTex(r"x_{\text{load}}=\frac{x_{\text{pulled}}}{n}",
                     font_size=31, color=T.result_final)
        r3 = MathTex(r"n=\text{number of supporting string segments}",
                     font_size=28, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.46)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.8)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "A block on a wedge is constrained to slide along the surface, so "
  "its acceleration component normal to the wedge matches the "
  "wedge's own normal motion. If the wedge is fixed, the block "
  "simply slides down the incline. If the wedge is free on a smooth "
  "floor, the wedge accelerates, and the constraint couples the two "
  "accelerations. Writing the normal constraint gives the relation "
  "between the block's acceleration relative to the wedge and the "
  "wedge's acceleration.",
 "visual": {"style": "wedge constraint", "transition": "fade"},
 "code": r'''
from manim import *


class Segment52(Scene):
    def construct(self):
        head = Text("LESSON 53 - BLOCK-WEDGE KINEMATICS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"a_{P/W}=\text{along slope};\qquad "
                     r"a_W=\text{horizontal}", font_size=29,
                     color=T.text_primary)
        r2 = MathTex(r"\text{normal constraint: }a_{P/W}\cos\theta=a_W\sin\theta",
                     font_size=29, color=T.result_final)
        r3 = MathTex(r"\text{fixed wedge: }a_W=0\ \Rightarrow\ a_{P/W}=a\sin\theta",
                     font_size=29, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.8)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "A rigid rod keeps the distance between its ends fixed, which "
  "constrains their velocity components along the rod to be equal. "
  "Belts and gears transfer rotation: two gears in mesh have equal "
  "linear speed at the contact point, so omega one R one equals "
  "omega two R two, meaning the angular speeds are inversely "
  "proportional to the radii. A belt connecting pulleys imposes the "
  "same condition through the belt speed.",
 "visual": {"style": "rod belt gears", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment53(Scene):
    def construct(self):
        head = Text("LESSON 54 - ROD CONSTRAINT, BELTS, GEARS",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{rod: }v_A\cos\alpha=v_B\cos\beta",
                     font_size=30, color=T.result_final)
        r2 = MathTex(r"\text{gears: }\omega_1R_1=\omega_2R_2",
                     font_size=31, color=T.result_final)
        r3 = MathTex(r"\omega\propto\frac{1}{R}\ \text{(inverse)}",
                     font_size=30, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.46)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.8)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r3), run_time=1.6)
        self.wait(2.8)
        self.wait(6)
''',
},
]
