TITLE = "Q38 - WORK-ENERGY THEOREM: STATEMENT, DERIVATION, APPLICATIONS"

QUESTION = {
    "display":
        "Work-Energy Theorem. Statement: the net work done by all the "
        "forces acting on a body is equal to the change in its kinetic "
        "energy. To prove: W = K_f - K_i, where W is net work done, "
        "K_f final kinetic energy, K_i initial kinetic energy. "
        "Diagram: a body of mass m moving along a straight horizontal "
        "surface under an applied force F, with initial velocity u, "
        "final velocity v, and displacement s. Mathematical "
        "derivation: write it step by step. Hence proved: W_net = "
        "ΔK.",
    "speech":
        "The work-energy theorem. Statement: the net work done by all "
        "the forces acting on a body equals the change in its kinetic "
        "energy. To prove: W equals K f minus K i, where W is the net "
        "work done, K f the final kinetic energy, and K i the initial "
        "kinetic energy. The diagram shows a body of mass m moving "
        "along a straight horizontal surface under an applied force F, "
        "with initial velocity u, final velocity v, and displacement s. "
        "We write the mathematical derivation step by step, and "
        "conclude: W net equals delta K. Hence the theorem is proved.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 38 - WORK-ENERGY THEOREM",
                     font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        r1 = MathTex(r"W_{\text{net}}=K_f-K_i=\Delta K", font_size=36,
                     color=T.result_final)
        r2 = Text("net work done by all forces = change in kinetic energy",
                  font_size=24, color=T.text_primary)
        r3 = MathTex(r"K=\frac{1}{2}mv^{2}", font_size=33,
                     color=T.result_intermediate)
        r4 = MathTex(r"K_f=\frac{1}{2}mv^{2},\qquad "
                     r"K_i=\frac{1}{2}mu^{2}", font_size=31,
                     color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.9)
        rows.move_to(UP * 0.3)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(r1), run_time=1.8)
        box1 = SurroundingRectangle(r1, buff=0.16, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        self.wait(4.0)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.2)
        self.wait(4.5)
        self.play(Write(r3), run_time=1.6)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.7)
        self.wait(4.0)
        self.play(FadeOut(VGroup(badge, line, box1)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q38 - STATEMENT AND THE STANDARD DIAGRAM",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        # diagram: block on horizontal surface
        floor = Line(LEFT * 5.4 + DOWN * 1.55, RIGHT * 5.4 + DOWN * 1.55,
                     color=T.grid, stroke_width=3)
        blk = Square(side_length=1.0, stroke_color=T.result_final,
                     stroke_width=3).set_fill(T.result_final, opacity=0.18)
        blk.move_to(DOWN * 1.05)
        mLab = MathTex(r"m", font_size=30, color=T.result_final)
        mLab.move_to(blk.get_center())
        F = Arrow(blk.get_center() + RIGHT * 2.2, blk.get_center() + RIGHT * 0.55,
                  buff=0, color=T.highlight_primary, stroke_width=5)
        FLab = MathTex(r"\vec F", font_size=32, color=T.highlight_primary)
        FLab.next_to(F, UP, buff=0.12)
        fk = Arrow(blk.get_center() + LEFT * 2.0, blk.get_center() + LEFT * 0.55,
                   buff=0, color=T.cancel_mark, stroke_width=4)
        fkLab = MathTex(r"\vec f_k", font_size=30, color=T.cancel_mark)
        fkLab.next_to(fk, UP, buff=0.12)
        uL = MathTex(r"u", font_size=30, color=T.text_secondary)
        uL.next_to(blk.get_center() + DOWN * 0.2, DOWN, buff=0.25)
        vL = MathTex(r"v", font_size=30, color=T.result_intermediate)
        vL.next_to(blk.get_center() + UP * 0.2, UP, buff=0.25)
        s = DoubleArrow(blk.get_center() + LEFT * 3.6 + DOWN * 0.45,
                        blk.get_center() + RIGHT * 3.6 + DOWN * 0.45,
                        buff=0, color=T.text_secondary, stroke_width=3)
        sLab = MathTex(r"s", font_size=32, color=T.text_secondary)
        sLab.next_to(s, DOWN, buff=0.12)
        dg = VGroup(floor, blk, mLab, F, FLab, fk, fkLab, uL, vL, s, sLab)
        dg.move_to(UP * 0.2)
        r1 = Text("A body of mass m moves on a straight horizontal surface "
                  "under an applied force F.", font_size=22,
                  color=T.text_primary)
        r2 = Text("Work is done by every force; the theorem uses the "
                  "NET work.", font_size=22, color=T.result_final)
        r3 = MathTex(r"W_{\text{net}}=K_f-K_i", font_size=32,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        fit_width(rows, 12.0)
        rows.move_to(DOWN * 2.6)
        self.play(Create(floor), Create(blk), Write(mLab), run_time=1.4)
        self.play(Create(F), Write(FLab), run_time=1.0)
        self.play(Create(fk), Write(fkLab), run_time=1.0)
        self.play(Write(uL), Write(vL), run_time=0.8)
        self.play(Create(s), Write(sLab), run_time=1.0)
        self.play(FadeIn(r1, shift=0.2 * UP), run_time=1.2)
        self.wait(3.0)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.2)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.14, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.6)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q38 - DERIVATION FROM FIRST PRINCIPLES",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"W_{\text{net}}=\int \vec F_{\text{net}}\cdot d\vec r",
                     font_size=31, color=T.text_primary)
        r2 = MathTex(r"\vec F_{\text{net}}=m\vec a\ \Rightarrow\ "
                     r"W_{\text{net}}=m\int a\,ds", font_size=30,
                     color=T.text_primary)
        r3 = MathTex(r"a=\frac{dv}{dt}=\frac{dv}{ds}\frac{ds}{dt}=v\frac{dv}{ds}",
                     font_size=30, color=T.result_intermediate)
        r4 = MathTex(r"W_{\text{net}}=m\int_u^{v}v\,dv=m\left[\frac{v^{2}}{2}\right]_u^{v}",
                     font_size=30, color=T.result_intermediate)
        r5 = MathTex(r"W_{\text{net}}=\frac{1}{2}mv^{2}-\frac{1}{2}mu^{2}",
                     font_size=33, color=T.result_final)
        r6 = MathTex(r"W_{\text{net}}=K_f-K_i=\Delta K\ \ \blacksquare",
                     font_size=33, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.34)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r5), run_time=1.8)
        box5 = SurroundingRectangle(r5, buff=0.12, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r6), run_time=1.8)
        box6 = SurroundingRectangle(r6, buff=0.12, color=T.result_final)
        self.play(Create(box6), run_time=0.7)
        self.wait(3.6)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q38 - KINETIC ENERGY, SIGNS ( POSITIVE AND NEGATIVE WORK",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"K=\frac{1}{2}mv^{2}\ \text{(scalar, always }\geq0\text{)}",
                     font_size=31, color=T.result_final)
        r2 = MathTex(r"W>0:\ \text{force aids motion - kinetic energy grows}",
                     font_size=28, color=T.text_primary)
        r3 = MathTex(r"W<0:\ \text{force opposes motion - kinetic energy shrinks}",
                     font_size=28, color=T.text_primary)
        r4 = MathTex(r"W=0:\ \text{force } \perp \text{ displacement (e.g. normal, }"
                     r"\text{centripetal)}", font_size=28, color=T.text_primary)
        r5 = MathTex(r"\text{assumptions: inertial frame, }m=\text{const}",
                     font_size=27, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.38)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r5), run_time=1.4)
        self.wait(2.8)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q38 - GENERALIZATION: MANY FORCES, 3D, VARIABLE FORCE",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"W_{\text{net}}=\sum_i W_i=\int\left(\sum_i\vec F_i\right)\cdot d\vec r",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"W_{\text{net}}=\Delta K\ \text{holds no matter the path}",
                     font_size=29, color=T.result_final)
        r3 = MathTex(r"\text{variable force: }W=\int_{x_1}^{x_2}F(x)\,dx",
                     font_size=30, color=T.result_intermediate)
        r4 = MathTex(r"\text{example: spring }F=-kx\ \Rightarrow\ W_s=-\frac{1}{2}k(x_2^{2}-x_1^{2})",
                     font_size=28, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.7)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.9)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_intermediate)
        self.play(Create(box4), run_time=0.7)
        self.wait(3.2)
        self.wait(6)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q38 - WORKED EXAMPLE 1: PULLING A BLOCK (NO FRICTION)",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"m=10\ \text{kg},\ F=40\ \text{N},\ s=5\ \text{m},\ u=0",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"W_{\text{net}}=Fs=40\times5=200\ \text{J}",
                     font_size=31, color=T.result_intermediate)
        r3 = MathTex(r"200=\frac{1}{2}(10)v^{2}-0", font_size=31,
                     color=T.text_primary)
        r4 = MathTex(r"v^{2}=40\ \Rightarrow\ v=2\sqrt{10}\approx6.32\ \text{m/s}",
                     font_size=31, color=T.result_final)
        r5 = MathTex(r"\text{check with kinematics: }v^{2}=u^{2}+2as,\ a=4\ \text{m/s}^{2}",
                     font_size=28, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.36)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.8)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_intermediate)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.8)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.3)
        self.wait(3.0)
        self.wait(6)
'''

SEG5 = r'''from manim import *


class Segment5(Scene):
    def construct(self):
        head = Text("Q38 - WORKED EXAMPLE 2: WITH KINETIC FRICTION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\mu_k=0.3,\ m=10\ \text{kg},\ F=40\ \text{N},\ s=5\ \text{m}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"f_k=\mu_k mg=0.3\times10\times9.8=29.4\ \text{N}",
                     font_size=29, color=T.text_primary)
        r3 = MathTex(r"W_{\text{net}}=Fs-f_k s=40\times5-29.4\times5=53\ \text{J}",
                     font_size=28, color=T.result_intermediate)
        r4 = MathTex(r"53=\frac{1}{2}(10)v^{2}\ \Rightarrow\ v=\sqrt{10.6}\approx3.26\ \text{m/s}",
                     font_size=28, color=T.result_final)
        r5 = MathTex(r"\text{net work minus  = kinetic energy gained}",
                     font_size=27, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.34)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.8)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.9)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.2)
        self.wait(3.0)
        self.wait(6)
'''

SEG6 = r'''from manim import *


class Segment6(Scene):
    def construct(self):
        head = Text("Q38 - APPLICATION: STOPPING DISTANCE VIA WORK-ENERGY",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"W_{\text{net}}=-f_k s=-\mu_k mg\,s", font_size=31,
                     color=T.text_primary)
        r2 = MathTex(r"-\mu_k mg\,s=0-\frac{1}{2}mu^{2}", font_size=31,
                     color=T.text_primary)
        r3 = MathTex(r"s=\frac{u^{2}}{2\mu_k g}", font_size=35,
                     color=T.result_final)
        r4 = MathTex(r"\text{matches kinematics: }u^{2}=2\mu_k g\,s\ \checkmark",
                     font_size=29, color=T.result_intermediate)
        r5 = MathTex(r"\text{doubling }u\ \text{quadruples }s", font_size=29,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.38)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.7)
        box3 = SurroundingRectangle(r3, buff=0.14, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r4), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r5), run_time=1.6)
        box5 = SurroundingRectangle(r5, buff=0.12, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        self.wait(3.2)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Statement: the net work done by all the forces acting on a body "
     "equals the change in its kinetic energy. Look at the standard "
     "diagram: a body of mass m slides on a straight horizontal "
     "surface, pushed by an applied force F, resisted by kinetic "
     "friction f k; its initial velocity is u, its final velocity v, "
     "and the displacement is s. Every force on the body does work; "
     "the theorem speaks about their sum, the net work. Sketch the "
     "diagram, label every force, and the theorem reads W net equals "
     "K f minus K i.",
     "visual": {"style": "statement diagram", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Derivation, step by step. The net work is the integral of the "
     "net force along the displacement. By Newton's second law the "
     "net force is m a, so W net is m times the integral of a d s. "
     "Now use the chain rule: a equals d v d t equals v d v d s. "
     "Substitute: W net equals m times the integral of v d v from u "
     "to v, which is m times the bracket of v squared over two "
     "between the limits. That evaluates to half m v squared minus "
     "half m u squared. These two terms are exactly the final and "
     "initial kinetic energies, so W net equals K f minus K i, "
     "which is delta K. Proved.",
     "visual": {"style": "derivation", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Kinetic energy is half m v squared, a scalar, never negative. "
     "Work carries a sign: a force aiding motion does positive work "
     "and grows kinetic energy; a force opposing motion does negative "
     "work and shrinks it; a force perpendicular to the displacement, "
     "like the normal force or a centripetal force, does zero work. "
     "The theorem is a scalar statement: it does not care about "
     "direction, only about the total energy bookkeeping. We also "
     "assume an inertial frame and constant mass.",
     "visual": {"style": "signs", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "Generalization. With several forces, the net work is the sum of "
     "the works of every force, and the theorem still holds along any "
     "path and in three dimensions. For variable forces, work is the "
     "integral of F of x d x. The standard example is a spring with "
     "F equals minus k x, whose work over a stretch is minus half k "
     "times the change of x squared, exactly the spring potential "
     "energy entering the kinetic-energy budget.",
     "visual": {"style": "general", "transition": "slide-up"},
     "code": SEG3},
    {"narration":
     "Worked example one: pull a ten kilogram block with a constant "
     "forty newton force over five metres on a frictionless floor, "
     "starting from rest. The net work is F times s, two hundred "
     "joules. By the theorem that equals the final kinetic energy, "
     "half m v squared. Solve: v squared is forty, so v is two root "
     "ten, about six point three two metres per second. The answer "
     "matches the kinematic solution with acceleration four metres "
     "per second squared.",
     "visual": {"style": "example 1", "transition": "carry-over"},
     "code": SEG4},
    {"narration":
     "Worked example two: repeat with kinetic friction of coefficient "
     "zero point three. First compute friction: f k equals mu k m g, "
     "twenty-nine point four newtons. The net work is F s minus f k "
     "s, fifty-three joules. Half m v squared equals fifty-three, so "
     "v is about three point two six metres per second. Friction "
     "stole the rest of the input energy; only the net work became "
     "kinetic energy. This is why the net work, not the applied work, "
     "drives the speed.",
     "visual": {"style": "example 2", "transition": "fade"},
     "code": SEG5},
    {"narration":
     "Application: stopping distance. A car brakes on a rough road; "
     "the only horizontal force is friction, opposite to motion, so "
     "the net work is minus f k s, which is minus mu k m g s. The "
     "theorem equates it to the change in kinetic energy, zero minus "
     "half m u squared. Cancel m and solve: s equals u squared over "
     "two mu k g, exactly the kinematic answer. Doubling the speed "
     "quadruples the stopping distance. The work-energy theorem is "
     "not a new law: it is Newton's second law integrated, and it "
     "turns dynamics problems into energy bookkeeping.",
     "visual": {"style": "stopping", "transition": "slide-up"},
     "code": SEG6},
]

LECTURE = {
    "title": TITLE,
    "preset": "lab",
    "format": "mixed",
    "question": QUESTION,
    "question_code": QUESTION_CODE,
    "segments": SEGMENTS,
}
