TITLE = "Q34 - THE GRAND MECHANICS MARATHON"

QUESTION = {
    "display":
        "A particle (m) released from rest on a rough incline (angle "
        "theta, length L) sits atop a movable wedge (M) on a frictionless "
        "floor. It slides down, crosses a rough horizontal track, hits a "
        "rotating uniform disc tied to a spring, then enters a vertical "
        "circular track and is finally launched as a projectile. The "
        "whole system feels the gravity of a spherical planet. Develop "
        "the complete mathematical analysis: dimensional analysis, "
        "equations of motion, friction, work-energy, momentum, impulse, "
        "restitution, rotation, rolling, gravitation, oscillations, "
        "elasticity, fluids -- deriving every governing equation from "
        "first principles, with free-body and energy diagrams, and "
        "dimensional checks.",
    "speech":
        "A particle of mass m is released from rest on a rough inclined "
        "plane of angle theta and length L, sitting on a movable wedge of "
        "mass M on a frictionless floor. The particle slides down, "
        "crosses a rough horizontal track, collides with a rotating "
        "uniform disc connected to a spring, then moves along a vertical "
        "circular track and is finally launched as a projectile, all "
        "under the gravity of a spherical planet. Develop the complete "
        "mathematical analysis of this interconnected system, deriving "
        "every governing equation from first principles.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 34 - THE GRAND MECHANICS MARATHON",
                     font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = Text("incline + wedge -> rough track -> disc+spring -> "
                    "vertical loop -> projectile -> planet gravity",
                    font_size=24, color=T.constant)
        c_chem = Text("TASKS", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "derive EOM from first principles; FBD + energy\n"
            "diagrams; state when each conservation law holds",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("TOOLKIT", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "dimensional analysis, vectors, relative motion,\n"
            "Newton + friction, work-energy, momentum, impulse,\n"
            "restitution, rotation, rolling, gravitation, SHM,\n"
            "coupled/damped/forced, elasticity, fluids",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("OUTPUT", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "a, v, x, t, F, E, omega, torque, collision outcomes,\n"
            "frequencies, orbital elements -- all dimensionally checked",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, chem, maths, econ).arrange(DOWN, aligned_edge=LEFT,
                                                       buff=0.30)
        rows.move_to(UP * 0.15)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=2.0)
        self.wait(4.5)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(5.5)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(8.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(7.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q34 - THE STAGE: ONE PARTICLE, EVERY LAW",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        # floor
        floor = Line(LEFT * 6.6 + DOWN * 2.4, RIGHT * 6.6 + DOWN * 2.4,
                     color=T.graph_function, stroke_width=3)
        # wedge: right triangle, apex up-right, slope down to the left
        wpts = [LEFT * 4.6 + DOWN * 2.4, LEFT * 1.8 + DOWN * 2.4,
                LEFT * 1.8 + DOWN * 0.2]
        wedge = Polygon(*wpts, stroke_color=T.graph_reference,
                        stroke_width=3)
        wedge.set_fill(T.graph_reference, opacity=0.10)
        # incline surface = hypotenuse p0->p2
        inclab = MathTex(r"\theta", font_size=30, color=T.text_primary)
        inclab.move_to(LEFT * 3.0 + DOWN * 2.05)
        linelab = MathTex(r"L", font_size=30, color=T.text_primary)
        linelab.move_to((wpts[0] + wpts[2]) / 2 + LEFT * 0.35)
        # block on slope midpoint
        mid = ((wpts[0][0] + wpts[2][0]) / 2,
               (wpts[0][1] + wpts[2][1]) / 2, 0.0)
        blk = Square(side_length=0.5, stroke_color=T.result_final,
                     stroke_width=3).set_fill(T.result_final, opacity=0.25)
        blk.move_to(LEFT * 3.2 + DOWN * 1.55)
        blklab = MathTex(r"m", font_size=30, color=T.result_final)
        blklab.next_to(blk, RIGHT, buff=0.15)
        # wedge mass label
        wlab = MathTex(r"M", font_size=30, color=T.graph_reference)
        wlab.move_to(LEFT * 2.4 + DOWN * 2.05)
        # rough horizontal track
        track = Line(LEFT * 1.8 + DOWN * 2.4, RIGHT * 1.4 + DOWN * 2.4,
                     color=T.cancel_mark, stroke_width=7)
        trklab = Text("rough track, mu_k", font_size=20,
                      color=T.cancel_mark).next_to(track, DOWN, buff=0.15)
        # disc on axle with spring to wall
        disc = Circle(radius=0.55, stroke_color=T.result_intermediate,
                      stroke_width=3).move_to(RIGHT * 2.4 + DOWN * 1.85)
        disc.set_fill(T.result_intermediate, opacity=0.15)
        axle = Dot(disc.get_center(), radius=0.07, color=T.text_primary)
        dl = MathTex(r"I", font_size=28, color=T.result_intermediate)
        dl.next_to(disc, UP, buff=0.12)
        wall = Line(RIGHT * 5.2 + DOWN * 1.35, RIGHT * 5.2 + DOWN * 2.4,
                    color=T.text_secondary, stroke_width=3)
        spring = VGroup(Line(RIGHT * 2.95 + DOWN * 1.85,
                             RIGHT * 5.2 + DOWN * 1.85,
                             color=T.highlight_primary, stroke_width=2.5))
        for i in range(6):
            x0 = RIGHT * (3.0 + 0.36 * i) + DOWN * 1.85
            spring.add(Line(x0, x0 + UP * 0.14,
                            color=T.highlight_primary, stroke_width=2.5))
        spring.add(Line(RIGHT * 5.2 + DOWN * 1.85,
                        RIGHT * 4.35 + DOWN * 1.85,
                        color=T.highlight_primary, stroke_width=2.5))
        klab = MathTex(r"k", font_size=28, color=T.highlight_primary)
        klab.move_to(RIGHT * 4.1 + UP * 1.75)
        # vertical loop
        loop = Circle(radius=0.7, stroke_color=T.highlight_secondary,
                      stroke_width=3).move_to(RIGHT * 5.9 + UP * 0.4)
        loop.set_fill(opacity=0)
        llab = MathTex(r"R_\ell", font_size=26, color=T.highlight_secondary)
        llab.next_to(loop, UP, buff=0.1)
        # projectile arc
        arc = Arc(start_angle=-PI / 2, angle=PI / 2, radius=1.3,
                  arc_center=RIGHT * 5.9 + UP * 1.1,
                  stroke_color=T.text_secondary, stroke_width=2.5)
        arclab = Text("projectile", font_size=20,
                      color=T.text_secondary).next_to(arc, UR, buff=0.1)
        # planet
        pl = Circle(radius=0.9, stroke_color=T.graph_function,
                    stroke_width=2).move_to(RIGHT * 2.4 + UP * 3.1)
        pl.set_fill(T.graph_function, opacity=0.10)
        pll = MathTex(r"M_p,\ R_p", font_size=26, color=T.graph_function)
        pll.next_to(pl, UP, buff=0.1)
        stage = VGroup(floor, wedge, inclab, linelab, blk, blklab, wlab,
                       track, trklab, disc, axle, dl, wall, spring, klab,
                       loop, llab, arc, arclab, pl, pll)
        stage.move_to(DOWN * 0.7)
        if stage.height > 5.6:
            stage.scale_to_fit_height(5.6)
        # caption
        cap = Text("particle m on wedge M -> rough track -> disc I on "
                   "spring k -> loop R -> projectile; planet sets g",
                   font_size=22, color=T.text_secondary)
        fit_width(cap, 12.4)
        cap.to_edge(DOWN, buff=0.35)
        self.play(Create(floor), Create(wedge), run_time=1.6)
        self.play(FadeIn(blk), Write(blklab), Write(wlab), Write(inclab),
                  Write(linelab), run_time=1.4)
        self.wait(2.6)
        self.play(Create(track), FadeIn(trklab), run_time=1.1)
        self.play(Create(disc), FadeIn(axle), Write(dl), run_time=1.1)
        self.play(Create(wall), Create(spring), Write(klab), run_time=1.1)
        self.play(Create(loop), Write(llab), run_time=1.0)
        self.play(Create(arc), FadeIn(arclab), run_time=1.0)
        self.play(Create(pl), Write(pll), run_time=1.1)
        self.play(FadeIn(cap, shift=0.15 * UP), run_time=1.1)
        self.wait(4.0)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q34 - STEP 1: DIMENSIONAL ANALYSIS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"[g]=LT^{-2},\ [k]=MT^{-2},\ [I]=ML^{2},\ "
                     r"[\mu]=1", font_size=29, color=T.text_primary)
        r2 = MathTex(r"[v_\text{base}]=\sqrt{gL}\ \Rightarrow\ "
                     r"\sqrt{\frac{m}{M+m}}\sqrt{2gL\,f(\theta,\mu_1)}",
                     font_size=28, color=T.result_intermediate)
        r3 = MathTex(r"\omega_{\text{spring}}=\sqrt{\frac{k}{m+I/R^{2}}}"
                     r"\ \Rightarrow\ T^{-1}", font_size=28,
                     color=T.text_primary)
        r4 = MathTex(r"v_\text{orb}=\sqrt{\frac{GM_p}{r}}\ \Rightarrow\ "
                     r"\sqrt{L^{3}T^{-2}/L}=LT^{-1}\ \checkmark",
                     font_size=28, color=T.result_final)
        r5 = Text("every answer must be a combination of g, L, k, m, M, "
                  "I, R that closes dimensionally.", font_size=23,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.9)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.9)
        box4 = SurroundingRectangle(r4, buff=0.14, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        self.wait(2.8)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.2)
        self.wait(3.4)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q34 - STEP 2: VECTORS AND RELATIVE MOTION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\vec a_{P/\text{ground}}=\vec a_{P/W}"
                     r"+\vec a_{W}", font_size=31, color=T.text_primary)
        r2 = Text("the particle slides along the slope at angle theta "
                  "relative to the wedge, while the wedge itself "
                  "accelerates.", font_size=23, color=T.text_secondary)
        r3 = MathTex(r"\hat n\cdot\vec a_{P/\text{ground}}=0\ "
                     r"\text{(stays on slope plane)}", font_size=28,
                     color=T.text_primary)
        r4 = MathTex(r"\Rightarrow a_{P,W}\cos\theta"
                     r"=a_W\sin\theta\ \Rightarrow\ "
                     r"a_{P,W}=a_W\tan\theta", font_size=28,
                     color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.8)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.4)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.9)
        box4 = SurroundingRectangle(r4, buff=0.15,
                                    color=T.result_intermediate)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_intermediate, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q34 - STEP 3: FBD AND EQUATIONS OF MOTION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"m:\ \ mg\sin\theta-\mu_1 N\ \mp\ "
                     r"N\text{-components} = m(a_{P,W}\hat{t}+a_W)",
                     font_size=27, color=T.text_primary)
        r2 = MathTex(r"M:\ -N\sin\theta+\mu_1 N\cos\theta = -M a_W",
                     font_size=28, color=T.text_primary)
        r3 = MathTex(r"\Rightarrow\ a_W=\frac{m\sin\theta\cos\theta"
                     r"(1-\mu_1\tan\theta)\,g}{M+m\sin^{2}\theta}",
                     font_size=29, color=T.result_intermediate)
        r4 = MathTex(r"a_{P,W}=\frac{(M+m)\sin\theta"
                     r"(1-\mu_1\tan\theta)\,g}{M+m\sin^{2}\theta}",
                     font_size=29, color=T.result_final)
        r5 = Text("pseudo-force -m a_W acts on the particle in the "
                  "wedge frame; the constraint N couples both FBDs.",
                  font_size=23, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=2.0)
        box3 = SurroundingRectangle(r3, buff=0.13,
                                    color=T.result_intermediate)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.6)
        self.play(Write(r4), run_time=2.0)
        box4 = SurroundingRectangle(r4, buff=0.13, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(2.8)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.2)
        self.wait(3.4)
        self.wait(6)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q34 - STEP 4: WORK-ENERGY DOWN THE INCLINE",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{wedge frictionless: }"
                     r"\Sigma W=\Delta K\ \text{for the system}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"mgL\sin\theta-\mu_1 mg\cos\theta\,L = "
                     r"\tfrac12 m v_{rel}^{2}+\tfrac12 M v_{W}^{2}",
                     font_size=27, color=T.text_primary)
        r3 = MathTex(r"v_{rel}=\sin\theta\sqrt{\frac{2gL\,(M+m)"
                     r"(1-\mu_1\cot\theta)}{M+m\sin^{2}\theta}}",
                     font_size=28, color=T.result_intermediate)
        r4 = MathTex(r"v_W=\frac{m v_{rel}\cos\theta}{M+m}\ \ \text{("
                     r"horizontal momentum conserved mid-slide)}",
                     font_size=28, color=T.result_final)
        r5 = MathTex(r"\checkmark\ \text{conservation holds: no external "
                     r"horizontal force on (block+wedge)}", font_size=26,
                     color=T.highlight_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.36)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r2), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r3), run_time=2.0)
        box3 = SurroundingRectangle(r3, buff=0.13,
                                    color=T.result_intermediate)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.6)
        self.play(Write(r4), run_time=2.0)
        box4 = SurroundingRectangle(r4, buff=0.13, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        self.wait(2.6)
        self.play(Write(r5), run_time=1.7)
        emphasize(self, r5, color=T.highlight_secondary, run_time=0.9)
        self.wait(3.6)
        self.wait(6)
'''

SEG5 = r'''from manim import *


class Segment5(Scene):
    def construct(self):
        head = Text("Q34 - STEP 5: ROUGH TRACK AND APPROACH SPEED",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("on the rough horizontal track, friction is kinetic: "
                  "f = mu2 m g, opposite velocity.", font_size=23,
                  color=T.text_primary)
        r2 = MathTex(r"\tfrac12 m v^{2}=\tfrac12 m v_{x}^{2}"
                     r"-\mu_2 m g\,d\ \Rightarrow\ "
                     r"v=\sqrt{v_{x}^{2}-2\mu_2 g\,d}", font_size=29,
                     color=T.result_intermediate)
        r3 = Text("stopping condition: if v_x^2 < 2 mu2 g d the particle "
                  "never reaches the disc.", font_size=23,
                  color=T.cancel_mark)
        r4 = MathTex(r"\text{time on track }t=\frac{v_x-v}{\mu_2 g},"
                     r"\qquad d=\frac{v_x^{2}-v^{2}}{2\mu_2 g}",
                     font_size=28, color=T.text_primary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(FadeIn(r1, shift=0.2 * UP), run_time=1.5)
        self.wait(2.8)
        self.play(Write(r2), run_time=2.0)
        box2 = SurroundingRectangle(r2, buff=0.15,
                                    color=T.result_intermediate)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_intermediate, run_time=0.9)
        self.wait(3.2)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.4)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.8)
        self.wait(3.6)
        self.wait(6)
'''

SEG6 = r'''from manim import *


class Segment6(Scene):
    def construct(self):
        head = Text("Q34 - STEP 6: COLLISION WITH THE DISC-SPRING",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{impulse }J=\int F\,dt,\quad "
                     r"\Delta p=m(v'-v),\quad "
                     r"e=\frac{v'_{\text{disc}}-v'}{v}", font_size=27,
                     color=T.text_primary)
        r2 = MathTex(r"\text{angular impulse on disc: }Jh=I\omega", 
                     font_size=29, color=T.text_primary)
        r3 = MathTex(r"\Rightarrow\ v'=\frac{m-e m_{\text{eff}}}{m+m_"
                     r"{\text{eff}}}v,\ \ \omega=\frac{h m(1+e)v}"
                     r"{(I+m_{\text{eff}}h^{2})}", font_size=27,
                     color=T.result_intermediate)
        r4 = MathTex(r"\text{after impact: }\tfrac12 (m+I/R^{2})"
                     r"V^{2}=\tfrac12 kA^{2}\ \Rightarrow\ "
                     r"A=V\sqrt{\frac{m_{\text{eff}}}{k}}", font_size=27,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=2.1)
        box3 = SurroundingRectangle(r3, buff=0.13,
                                    color=T.result_intermediate)
        self.play(Create(box3), run_time=0.7)
        self.wait(3.0)
        self.play(Write(r4), run_time=2.1)
        box4 = SurroundingRectangle(r4, buff=0.13, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG7 = r'''from manim import *


class Segment7(Scene):
    def construct(self):
        head = Text("Q34 - STEP 7: ROTATION OF THE DISC", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"I_c=\frac{1}{2}MR_d^{2}\ \text{(uniform disc)}",
                     font_size=30, color=T.text_primary)
        r2 = MathTex(r"\text{parallel axis: }I=I_c+md^{2},\quad"
                     r"\text{perpendicular: }I_z=I_x+I_y", font_size=28,
                     color=T.text_primary)
        r3 = MathTex(r"\tau=I\alpha,\qquad "
                     r"\frac{dL}{dt}=\tau\ \text{(about fixed axis)}",
                     font_size=29, color=T.result_intermediate)
        r4 = MathTex(r"\text{rolling: }v_{cm}=R_d\omega,\quad "
                     r"K_{\text{rot}}=\tfrac12 I\omega^{2}", font_size=29,
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
        self.play(Write(r2), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.8)
        box3 = SurroundingRectangle(r3, buff=0.14,
                                    color=T.result_intermediate)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.8)
        box4 = SurroundingRectangle(r4, buff=0.14, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG8 = r'''from manim import *


class Segment8(Scene):
    def construct(self):
        head = Text("Q34 - STEP 8: THE VERTICAL CIRCULAR TRACK",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"N+mg=\frac{mv_{top}^{2}}{R_\ell}\ \Rightarrow\ "
                     r"N\geq0\ \text{needs } v_{top}\geq\sqrt{gR_\ell}",
                     font_size=27, color=T.text_primary)
        r2 = MathTex(r"\text{energy: }\tfrac12 mv_{bot}^{2}="
                     r"\tfrac12 mv_{top}^{2}+mg(2R_\ell)", font_size=28,
                     color=T.text_primary)
        r3 = MathTex(r"\Rightarrow\ v_{bot}\geq\sqrt{5gR_\ell}"
                     r"\ \text{(loop-the-loop condition)}", font_size=29,
                     color=T.result_final)
        r4 = MathTex(r"N(\phi)=\frac{m v^{2}(\phi)}{R_\ell}"
                     r"+mg\cos\phi", font_size=28,
                     color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.9)
        box3 = SurroundingRectangle(r3, buff=0.15, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.8)
        self.wait(3.6)
        self.wait(6)
'''

SEG9 = r'''from manim import *


class Segment9(Scene):
    def construct(self):
        head = Text("Q34 - STEP 9: PROJECTILE LAUNCH", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\ddot{x}=0,\quad \ddot{y}=-g_p\ \Rightarrow\ "
                     r"x=v_0\cos\alpha\,t,\ \ y=v_0\sin\alpha\,t"
                     r"-\tfrac12 g_p t^{2}", font_size=27,
                     color=T.text_primary)
        r2 = MathTex(r"T=\frac{2v_0\sin\alpha}{g_p},\qquad "
                     r"H=\frac{v_0^{2}\sin^{2}\alpha}{2g_p}", font_size=29,
                     color=T.result_intermediate)
        r3 = MathTex(r"\text{range }=\frac{v_0^{2}\sin 2\alpha}{g_p}"
                     r"\ \ \text{(flat ground)}", font_size=29,
                     color=T.result_final)
        r4 = MathTex(r"y=x\tan\alpha-\frac{g_p x^{2}}"
                     r"{2v_0^{2}\cos^{2}\alpha}", font_size=28,
                     color=T.text_primary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.1)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.9)
        box3 = SurroundingRectangle(r3, buff=0.15, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.8)
        self.wait(3.4)
        self.wait(6)
'''

SEG10 = r'''from manim import *


class Segment10(Scene):
    def construct(self):
        head = Text("Q34 - STEP 10: GRAVITATION OF THE PLANET",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"g_p(r)=\frac{GM_p}{r^{2}},\qquad "
                     r"V(r)=-\frac{GM_p}{r}", font_size=30,
                     color=T.text_primary)
        r2 = MathTex(r"v_{\text{esc}}=\sqrt{\frac{2GM_p}{R_p}},\qquad "
                     r"v_{\text{orb}}=\sqrt{\frac{GM_p}{r}}", font_size=29,
                     color=T.result_intermediate)
        r3 = MathTex(r"\frac{mv_{orb}^{2}}{r}=\frac{GM_p m}{r^{2}}"
                     r"\Rightarrow\ v_{orb}^{2}r=\text{const}",
                     font_size=28, color=T.text_primary)
        r4 = MathTex(r"T^{2}=\frac{4\pi^{2}}{GM_p}a^{3}\ \ "
                     r"\text{(Kepler III, derived)}", font_size=30,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.9)
        self.wait(2.6)
        self.play(Write(r4), run_time=2.0)
        box4 = SurroundingRectangle(r4, buff=0.15, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG11 = r'''from manim import *


class Segment11(Scene):
    def construct(self):
        head = Text("Q34 - STEP 11: OSCILLATIONS OF THE SYSTEM",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{spring+disc: }m_{\text{eff}}\ddot{x}+kx=0"
                     r",\quad \omega_0=\sqrt{k/m_{\text{eff}}}",
                     font_size=27, color=T.text_primary)
        r2 = MathTex(r"\text{pendulum: }T=2\pi\sqrt{I_p/(mgd)}"
                     r"\ \text{(physical)}", font_size=28,
                     color=T.text_primary)
        r3 = MathTex(r"\text{coupled: }\omega_{\pm}^{2}="
                     r"\frac{k}{\mu}\big(1\pm\kappa\big)", font_size=28,
                     color=T.result_intermediate)
        r4 = MathTex(r"\text{damped+forced: }A(\omega)=\frac{F_0/m}"
                     r"{\sqrt{(\omega_0^{2}-\omega^{2})^{2}+"
                     r"(2\beta\omega)^{2}}}", font_size=28,
                     color=T.result_final)
        r5 = Text("resonance: amplitude peaks when the drive frequency "
                  "meets the damped natural frequency.", font_size=23,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.36)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.9)
        self.wait(2.6)
        self.play(Write(r4), run_time=2.2)
        box4 = SurroundingRectangle(r4, buff=0.14, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.0)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.2)
        self.wait(3.4)
        self.wait(6)
'''

SEG12 = r'''from manim import *


class Segment12(Scene):
    def construct(self):
        head = Text("Q34 - STEP 12: ELASTICITY AND FLUIDS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\sigma=\frac{F}{A},\ \ \epsilon=\frac{\Delta L}"
                     r"{L},\ \ Y=\frac{\sigma}{\epsilon}", font_size=28,
                     color=T.text_primary)
        r2 = MathTex(r"\text{buoyancy: }F_b=\rho_f V g_p\ \text{("
                     r"Archimedes)}", font_size=28,
                     color=T.result_intermediate)
        r3 = MathTex(r"\nabla\cdot\vec v=0\ \text{(continuity)},\quad "
                     r"p+\tfrac12\rho v^{2}+\rho g h=\text{const}",
                     font_size=28, color=T.text_primary)
        r4 = MathTex(r"\text{Stokes: }F=6\pi\eta r v\ \Rightarrow\ "
                     r"v_t=\frac{2r^{2}(\rho-\sigma)g_p}{9\eta}",
                     font_size=28, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.8)
        box2 = SurroundingRectangle(r2, buff=0.14,
                                    color=T.result_intermediate)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.6)
        self.play(Write(r3), run_time=2.0)
        self.wait(2.8)
        self.play(Write(r4), run_time=2.0)
        box4 = SurroundingRectangle(r4, buff=0.14, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG13 = r'''from manim import *


class Segment13(Scene):
    def construct(self):
        head = Text("Q34 - SYNTHESIS: THE MASTER RESULTS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        items = [
            (r"a_W,\ a_{P,W}", "wedge-frame dynamics"),
            (r"v_{rel},\ v", "incline and rough-track speeds"),
            (r"v',\ \omega", "collision outcomes (e, J)"),
            (r"A=V\sqrt{m_{\text{eff}}/k}", "spring oscillation amplitude"),
            (r"v_{bot}\geq\sqrt{5gR_\ell}", "loop survival"),
            (r"\text{range}=v_0^{2}\sin 2\alpha/g_p", "projectile"),
            (r"T^{2}\propto a^{3}", "orbits"),
        ]
        rows = []
        for sym, txt in items:
            a = MathTex(sym, font_size=27, color=T.result_final)
            b = Text(txt, font_size=22, color=T.text_secondary)
            rows.append(VGroup(a, b).arrange(RIGHT, buff=0.5))
        grp = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        fit_width(grp, 12.2)
        grp.next_to(rule, DOWN, buff=0.4)
        grp.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if grp.height > 6.0:
            grp.scale_to_fit_height(6.0)
        for row in rows:
            self.play(FadeIn(row, shift=0.15 * UP), run_time=0.8)
            self.wait(1.0)
        cap = Text("all quantities closed in g, L, k, m, M, I, R: "
                   "dimensionally consistent end to end.",
                   font_size=23, color=T.highlight_secondary)
        fit_width(cap, 12.0)
        cap.next_to(grp, DOWN, buff=0.35)
        if cap.height + grp.height > 7.0:
            grp.scale_to_fit_height(5.6)
            cap.next_to(grp, DOWN, buff=0.35)
        self.play(FadeIn(cap, shift=0.15 * UP), run_time=1.2)
        emphasize(self, cap, color=T.highlight_secondary, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "The stage: a particle of mass m rests on a rough incline of angle "
     "theta and length L, built into a wedge of mass M free to slide on "
     "a frictionless floor. From the bottom, a rough horizontal track "
     "leads to a uniform disc on a fixed axle, coupled to a spring of "
     "constant k. Past the disc, a vertical circular track of radius R "
     "ends in a launch ramp that throws the particle as a projectile. "
     "The planet below, mass M p and radius R p, supplies gravity g. "
     "Every law of mechanics will be used exactly once on this stage.",
     "visual": {"style": "system sketch", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "First, dimensional analysis. Gravity g has dimensions L T minus "
     "two, the spring constant k is M T minus two, the disc inertia I "
     "is M L squared, and friction coefficients are dimensionless. Any "
     "speed the system can produce must look like root g L, times a "
     "dimensionless function of theta, mu, and mass ratios. The spring "
     "frequency must look like root k over m, and the orbital speed "
     "like root G M p over r. We will build each result so it closes "
     "dimensionally.",
     "visual": {"style": "dimensions", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Vectors and relative motion. The ground-frame acceleration of the "
     "particle equals its acceleration relative to the wedge plus the "
     "wedge's own acceleration. The constraint that the particle stays "
     "on the slope plane, expressed in the normal direction, links the "
     "relative acceleration to the wedge acceleration: a relative "
     "equals a wedge times tan theta. This kinematic lock is what "
     "couples the two free-body diagrams.",
     "visual": {"style": "relative motion", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "Free-body diagrams. On the particle: weight, normal reaction N, "
     "and friction mu one N along the slope; in the wedge frame a "
     "pseudo-force minus m a wedge also acts. On the wedge: minus N sin "
     "theta plus the friction component drive it. Solving the pair "
     "gives the wedge acceleration m sin theta cos theta times one "
     "minus mu one tan theta, times g, over M plus m sin squared theta; "
     "and the relative acceleration down the slope with the factor M "
     "plus m in the numerator. If one minus mu tan theta is negative, "
     "the particle never slides: static friction holds.",
     "visual": {"style": "fbd equations", "transition": "slide-up"},
     "code": SEG3},
    {"narration":
     "Work-energy down the incline. Because the floor is frictionless, "
     "the only non-conservative work inside the system is friction on "
     "the slope, and normal reactions do no work. Gravity supplies m g "
     "L sin theta, friction removes mu one m g cos theta L, and the "
     "sum becomes the kinetic energy of the relative motion plus the "
     "wedge's kinetic energy. Conservation of horizontal momentum "
     "during the slide fixes the wedge speed as m times the relative "
     "speed times cos theta, over M plus m. These are speeds at the "
     "bottom of the incline.",
     "visual": {"style": "energy", "transition": "carry-over"},
     "code": SEG4},
    {"narration":
     "The rough horizontal track. Kinetic friction mu two m g decelerates "
     "the particle uniformly. Energy conservation with friction gives "
     "the arrival speed: v equals root of v x squared minus two mu two g "
     "d. If v x squared is less than two mu two g d, the particle stops "
     "before reaching the disc and the rest of the ride never happens; "
     "that is the boundary condition. The time spent on the track is v "
     "x minus v over mu two g.",
     "visual": {"style": "rough track", "transition": "fade"},
     "code": SEG5},
    {"narration":
     "The collision. During the impact, the horizontal impulse J changes "
     "the particle's momentum, and the same impulse applied at height h "
     "above the axle gives the disc an angular impulse J h, setting it "
     "spinning. The coefficient of restitution e relates the separation "
     "speed to the approach speed. Solving the impulse equations gives "
     "the rebound speed and the disc's angular velocity. After impact, "
     "the combined translating-rotating system compresses the spring, "
     "and energy shared with the spring fixes the maximum compression: "
     "A equals V root m effective over k.",
     "visual": {"style": "collision", "transition": "slide-up"},
     "code": SEG6},
    {"narration":
     "Rotational machinery of the disc. A uniform disc has inertia one "
     "half M d R d squared about its axle. The parallel axis theorem "
     "moves inertia to any offset axis; the perpendicular axis theorem "
     "relates the three principal axes of a flat lamina. Torque equals "
     "inertia times angular acceleration, and angular impulse changes "
     "angular momentum. For rolling contact, v equals omega R, and the "
     "rotational kinetic energy is one half I omega squared, which is "
     "exactly the reservoir the collision tapped.",
     "visual": {"style": "rotation", "transition": "carry-over"},
     "code": SEG7},
    {"narration":
     "The vertical circular track. At the top, the inward equation is N "
     "plus m g equals m v top squared over R; the track can only push, "
     "so contact holds only if v top is at least root g R. Energy from "
     "bottom to top then demands v bottom at least root five g R, the "
     "classic loop-the-loop condition. At a general angle phi, the "
     "normal force is m v squared over R plus m g cos phi, giving the "
     "full force profile around the loop.",
     "visual": {"style": "loop", "transition": "fade"},
     "code": SEG8},
    {"narration":
     "Projectile launch. With launch speed v zero at angle alpha and "
     "planet gravity g p, the equations of motion are x double dot zero "
     "and y double dot minus g p. Integration gives the parabola, with "
     "time of flight two v zero sin alpha over g p, maximum height v "
     "zero squared sin squared alpha over two g p, and range v zero "
     "squared sin two alpha over g p on flat ground. The trajectory "
     "equation is y equals x tan alpha minus g p x squared over two v "
     "zero squared cos squared alpha.",
     "visual": {"style": "projectile", "transition": "slide-up"},
     "code": SEG9},
    {"narration":
     "Gravitation of the planet. Outside a spherical planet, Newton's "
     "shell theorem makes it act as a point mass: g p of r is G M p "
     "over r squared and the potential is minus G M p over r. Escape "
     "speed is root two G M p over R p, and circular orbit speed is "
     "root G M p over r. Balancing m v squared over r against G M p m "
     "over r squared gives v squared r equals constant, and combining "
     "with the orbit circumference derives Kepler's third law, T "
     "squared equals four pi squared a cubed over G M p.",
     "visual": {"style": "gravitation", "transition": "carry-over"},
     "code": SEG10},
    {"narration":
     "Oscillations everywhere. The disc-spring system is a mass-spring "
     "with effective mass m plus I over R squared, omega zero root k "
     "over m effective. The wedge, if pivoted, is a physical pendulum "
     "with period two pi root I p over m g d. Two coupled masses give "
     "normal-mode frequencies omega plus and omega minus. With damping "
     "beta and a driving force F zero, the steady amplitude is F zero "
     "over m, over root of omega zero squared minus omega squared "
     "squared plus two beta omega squared, which peaks at resonance "
     "near the damped natural frequency.",
     "visual": {"style": "oscillations", "transition": "fade"},
     "code": SEG11},
    {"narration":
     "Elasticity and fluids. Stress is force per area, strain is "
     "extension per length, and Young's modulus is their ratio in the "
     "linear regime. If the particle ever lands in a fluid, buoyancy is "
     "rho f V g p by Archimedes. Fluid flow obeys continuity, "
     "divergence of v equals zero for incompressible flow, and "
     "Bernoulli's theorem, p plus half rho v squared plus rho g h "
     "constant along a streamline. A sphere falling in a viscous fluid "
     "feels Stokes drag six pi eta r v, giving terminal speed two r "
     "squared, rho minus sigma, g p, over nine eta.",
     "visual": {"style": "fluids", "transition": "slide-up"},
     "code": SEG12},
    {"narration":
     "Synthesis. The full analysis closes: wedge-frame dynamics gives "
     "the two accelerations; work-energy gives the speeds at the bottom "
     "and on the rough track; impulse and restitution give the "
     "collision outcome and the disc's spin; the spring converts the "
     "post-impact energy into oscillation amplitude V root m effective "
     "over k; the loop demands five g R at the bottom; the projectile "
     "range is v zero squared sin two alpha over g p; and the same g p "
     "keeps satellites on Kepler's T squared proportional to a cubed. "
     "Every result is dimensionally closed in g, L, k, m, M, I, and R.",
     "visual": {"style": "synthesis", "transition": "fade"},
     "code": SEG13},
]

LECTURE = {
    "title": TITLE,
    "preset": "lab",
    "format": "mixed",
    "question": QUESTION,
    "question_code": QUESTION_CODE,
    "segments": SEGMENTS,
}
