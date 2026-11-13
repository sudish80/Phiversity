TITLE = "Q4 - BIOT-SAVART LAW: MAGNETIC FIELD DERIVATIONS"

QUESTION = {
    "display":
        "State and explain Biot-Savart's law. Derive the magnetic field "
        "due to: (1) a current-carrying straight conductor at a nearby "
        "point, (2) a circular loop at a point on its axis, (3) a circular "
        "coil of N turns at its centre, (4) a circular arc subtending "
        "angle θ at its centre. Draw labelled diagrams, explain the "
        "direction with the right-hand thumb rule, and discuss "
        "applications.",
    "speech":
        "State and explain Biot Savart's law. Derive the magnetic field "
        "due to, one, a current carrying straight conductor at a point "
        "near it. Two, a circular current carrying loop at a point along "
        "its axis. Three, a circular coil having N turns at its centre. "
        "Four, a circular arc of a conductor subtending an angle theta at "
        "its centre. Draw neat, properly labelled diagrams for each case. "
        "Explain the direction of the magnetic field using the right hand "
        "thumb rule. Also discuss the practical applications of Biot "
        "Savart's law.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 4 - BIOT-SAVART LAW", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(r"d\mathbf{B}=\frac{\mu_0}{4\pi}"
                       r"\frac{I\,d\mathbf{l}\times\hat{\mathbf{r}}}{r^2}",
                       font_size=30, color=T.constant)
        c_chem = Text("STATEMENT", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "field of a current element: dB = (mu0/4pi) I dl x rhat / r^2\n"
            "direction: cross product; integrate over the circuit",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("CASES", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "1  straight wire: B = (mu0 I / 4 pi d)(sin t2 - sin t1)\n"
            "2  loop axis: B = mu0 I R^2 / 2 (R^2 + x^2)^(3/2)\n"
            "3  N-turn centre: B = N mu0 I / 2 R\n"
            "4  arc: B = mu0 I theta / 4 pi R",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("APPS", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "solenoids, electromagnets, MRI, transformers,\n"
            "particle accelerators, power lines, CRTs",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, chem, maths, econ).arrange(DOWN, aligned_edge=LEFT,
                                                       buff=0.34)
        rows.move_to(UP * 0.2)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=2.2)
        self.wait(6.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(8.0)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(10.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(8.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q4 - THE LAW AND THE RIGHT-HAND RULE", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"d\mathbf{B}=\frac{\mu_0}{4\pi}"
                     r"\frac{I\,d\mathbf{l}\times\hat{\mathbf{r}}}{r^2}",
                     font_size=36, color=T.result_final)
        r2 = MathTex(r"I:\ \text{current},\ d\mathbf{l}:\ \text{element},"
                     r"\ r:\ \text{distance},\ \hat{\mathbf{r}}:\ \text{unit} "
                     r"\text{vector from element to point}",
                     font_size=26, color=T.text_primary)
        r3 = MathTex(r"\text{total field: }\mathbf{B}=\int d\mathbf{B}"
                     r"\ \text{(superposition)}",
                     font_size=30, color=T.text_primary)
        r4 = MathTex(r"\text{right-hand thumb rule: thumb along current,}"
                     r"\ \text{fingers curl along B}",
                     font_size=29, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 11.5)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.2)
        box1 = SurroundingRectangle(r1, buff=0.16, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(5.0)
        self.play(Write(r2), run_time=1.8)
        self.wait(4.0)
        self.play(Write(r3), run_time=1.6)
        self.wait(3.5)
        self.play(Write(r4), run_time=1.6)
        self.wait(4.0)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q4 (1) - STRAIGHT CONDUCTOR", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"B=\frac{\mu_0 I}{4\pi d}"
                     r"(\sin\theta_2-\sin\theta_1)",
                     font_size=32, color=T.result_intermediate)
        r2 = MathTex(r"\text{infinite wire: }\theta_1\to-\frac{\pi}{2},"
                     r"\ \theta_2\to+\frac{\pi}{2}",
                     font_size=29, color=T.text_primary)
        r3 = MathTex(r"B=\frac{\mu_0 I}{2\pi d}",
                     font_size=34, color=T.result_final)
        r4 = MathTex(r"\text{field lines: concentric circles around the wire,}"
                     r"\ \text{direction by right-hand rule}",
                     font_size=28, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 8.2)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        wire = Line(LEFT * 2.6 + DOWN * 2.5, LEFT * 2.6 + UP * 2.5,
                    color=T.graph_function, stroke_width=5)
        tip = Arrow(LEFT * 2.6 + DOWN * 2.5, LEFT * 2.6 + UP * 2.5,
                    color=T.graph_function, stroke_width=5)
        wirelab = Text("I", font_size=24, color=T.graph_function)
        wirelab.next_to(wire, LEFT, buff=0.12).shift(UP * 0.6)
        P = Dot(RIGHT * 2.9 + UP * 0.8, radius=0.09, color=T.graph_point)
        Plab = Text("P", font_size=24, color=T.graph_point)
        Plab.next_to(P, RIGHT, buff=0.12)
        dline = DashedLine(LEFT * 2.6 + UP * 0.8, RIGHT * 2.9 + UP * 0.8,
                           color=T.text_secondary, stroke_width=3)
        dlab = MathTex(r"d", font_size=24, color=T.text_secondary)
        dlab.next_to(dline, DOWN, buff=0.1)
        th1 = MathTex(r"\theta_1", font_size=24, color=T.text_secondary)
        th1.move_to(LEFT * 1.9 + UP * 0.15)
        th2 = MathTex(r"\theta_2", font_size=24, color=T.text_secondary)
        th2.move_to(LEFT * 1.9 + UP * 1.15)
        self.play(Write(r1), run_time=1.8)
        self.wait(4.5)
        self.play(Create(wire), Create(tip), Write(wirelab), run_time=1.4)
        self.play(FadeIn(P), Write(Plab), run_time=0.8)
        self.play(Create(dline), Write(dlab), run_time=1.0)
        self.play(Write(th1), Write(th2), run_time=0.8)
        self.wait(3.5)
        self.play(Write(r2), run_time=1.6)
        self.wait(3.5)
        self.play(Write(r3), run_time=1.4)
        box3 = SurroundingRectangle(r3, buff=0.15, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.5)
        self.play(Write(r4), run_time=1.6)
        self.wait(3.5)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q4 (2) - CIRCULAR LOOP, FIELD ON ITS AXIS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"B=\frac{\mu_0 I R^2}{2(R^2+x^2)^{3/2}}",
                     font_size=32, color=T.result_intermediate)
        r2 = MathTex(r"\text{perpendicular components cancel by symmetry;}",
                     r"\ \text{only the axial component survives}",
                     font_size=28, color=T.text_primary)
        r3 = MathTex(r"\text{centre, }x=0:\ B=\frac{\mu_0 I}{2R}",
                     font_size=31, color=T.result_final)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 8.4)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        loop = Ellipse(width=2.8, height=1.0, color=T.graph_function,
                       stroke_width=5)
        loop.move_to(RIGHT * 3.2 + DOWN * 0.6)
        axis = Line(RIGHT * 1.2 + DOWN * 0.6, RIGHT * 6.2 + DOWN * 0.6,
                    color=T.text_muted, stroke_width=2)
        P = Dot(RIGHT * 5.6 + DOWN * 0.6, radius=0.09, color=T.graph_point)
        Plab = Text("P", font_size=24, color=T.graph_point)
        Plab.next_to(P, UP, buff=0.12)
        xline = DashedLine(RIGHT * 4.6 + DOWN * 0.6, RIGHT * 5.6 + DOWN * 0.6,
                           color=T.text_secondary, stroke_width=3)
        xlab = MathTex(r"x", font_size=24, color=T.text_secondary)
        xlab.next_to(xline, DOWN, buff=0.08)
        rlab = MathTex(r"R", font_size=24, color=T.text_secondary)
        rlab.move_to(RIGHT * 3.2 + DOWN * 0.05 + LEFT * 0.4)
        self.play(Write(r1), run_time=1.8)
        self.wait(4.5)
        self.play(Create(axis), Create(loop), run_time=1.6)
        self.play(FadeIn(P), Write(Plab), run_time=0.8)
        self.play(Create(xline), Write(xlab), Write(rlab), run_time=1.0)
        self.wait(3.5)
        self.play(Write(r2), run_time=1.8)
        self.wait(4.0)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.15, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.5)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q4 (3) - COIL OF N TURNS AT ITS CENTRE", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{each turn contributes }B_1=\frac{\mu_0 I}{2R}",
                     font_size=30, color=T.text_primary)
        r2 = MathTex(r"\text{fields of N turns add:}",
                     font_size=30, color=T.text_primary)
        r3 = MathTex(r"B=\frac{N\mu_0 I}{2R}",
                     font_size=36, color=T.result_final)
        r4 = MathTex(r"\text{direction: along the axis, by the right-hand}"
                     r"\ \text{thumb rule}",
                     font_size=28, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 8.6)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        coil = Circle(radius=1.8, color=T.graph_function, stroke_width=5)
        coil.move_to(RIGHT * 4.0 + DOWN * 0.6)
        cen = Dot(RIGHT * 4.0 + DOWN * 0.6, radius=0.1, color=T.graph_point)
        ring = Circle(radius=0.26, color=T.graph_point, stroke_width=3)
        ring.move_to(RIGHT * 4.0 + DOWN * 0.6)
        nlab = Text("N turns", font_size=24, color=T.graph_function)
        nlab.next_to(coil, UP, buff=0.15)
        self.play(Write(r1), run_time=1.6)
        self.wait(4.0)
        self.play(Create(coil), FadeIn(cen), Create(ring), Write(nlab),
                  run_time=1.6)
        self.wait(3.5)
        self.play(Write(r2), run_time=1.2)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.4)
        box3 = SurroundingRectangle(r3, buff=0.16, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.5)
        self.play(Write(r4), run_time=1.4)
        self.wait(3.5)
        self.wait(6)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q4 (4) - CIRCULAR ARC SUBTENDING ANGLE THETA",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"B=\frac{\mu_0 I\theta}{4\pi R},\quad "
                     r"\theta\ \text{in radians}",
                     font_size=34, color=T.result_intermediate)
        r2 = MathTex(r"\text{semicircle: }\theta=\pi\ \Rightarrow\ "
                     r"B=\frac{\mu_0 I}{4R}",
                     font_size=29, color=T.text_primary)
        r3 = MathTex(r"\text{full circle: }\theta=2\pi\ \Rightarrow\ "
                     r"B=\frac{\mu_0 I}{2R}\ \text{(check against loop)}",
                     font_size=29, color=T.result_final)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 9.6)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        O = RIGHT * 4.0 + DOWN * 0.6
        arc = Arc(radius=1.8, start_angle=-1.15, angle=2.3,
                  color=T.graph_function, stroke_width=5)
        arc.move_to(O)
        cen = Dot(O, radius=0.1, color=T.graph_point)
        r1l = Line(O, O + 1.8 * np.array([np.cos(-1.15), np.sin(-1.15), 0]),
                   color=T.text_secondary, stroke_width=2)
        r2l = Line(O, O + 1.8 * np.array([np.cos(1.15), np.sin(1.15), 0]),
                   color=T.text_secondary, stroke_width=2)
        thlab = MathTex(r"\theta", font_size=28, color=T.text_secondary)
        thlab.move_to(O + np.array([0.55, 0.25, 0]))
        Rlab = MathTex(r"R", font_size=24, color=T.text_secondary)
        Rlab.next_to(r1l, LEFT, buff=0.08)
        iarrow = Arrow(O + 1.8 * np.array([np.cos(1.15), np.sin(1.15), 0]),
                       arc.point_from_proportion(0.5),
                       color=T.graph_function, stroke_width=4)
        self.play(Write(r1), run_time=1.8)
        self.wait(4.5)
        self.play(Create(arc), FadeIn(cen), run_time=1.4)
        self.play(Create(r1l), Create(r2l), Write(thlab), Write(Rlab),
                  run_time=1.2)
        self.wait(3.5)
        self.play(Write(r2), run_time=1.4)
        self.wait(3.5)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.13, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.5)
        self.wait(6)
'''

SEG5 = r'''from manim import *


class Segment5(Scene):
    def construct(self):
        head = Text("Q4 - APPLICATIONS OF BIOT-SAVART'S LAW", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{design of solenoids and electromagnets - MRI}"
                     r"\ \text{scanners}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"\text{fields of power transmission lines and busbars}",
                     font_size=29, color=T.text_primary)
        r3 = MathTex(r"\text{deflection systems of cathode-ray tubes and}"
                     r"\ \text{electron beams}",
                     font_size=29, color=T.text_primary)
        r4 = MathTex(r"\text{inductors, transformers, and induction heating}"
                     r"\ \text{coils}",
                     font_size=29, color=T.text_primary)
        r5 = MathTex(r"\text{particle accelerators and plasma physics fields}",
                     font_size=29, color=T.text_primary)
        r6 = MathTex(r"\text{the law is the starting point for computing}"
                     r"\ \text{magnetic fields from any current distribution}",
                     font_size=29, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 11.6)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.4)
        self.wait(3.5)
        self.play(Write(r2), run_time=1.2)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.2)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.2)
        self.wait(3.0)
        self.play(Write(r5), run_time=1.2)
        self.wait(3.0)
        self.play(Write(r6), run_time=1.6)
        box6 = SurroundingRectangle(r6, buff=0.13, color=T.result_final)
        self.play(Create(box6), run_time=0.7)
        emphasize(self, r6, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEGMENTS = [
    {"narration": "Biot Savart's law gives the magnetic field produced by "
     "a small current element. The contribution dB is proportional to the "
     "current I, to the length dl of the element, and inversely "
     "proportional to the square of the distance r. The direction is the "
     "cross product of dl with the unit vector toward the point. In SI "
     "units the constant is mu zero over four pi. Integrating over the "
     "whole circuit gives the total field, and the right hand thumb rule "
     "gives the direction: thumb along the current, curled fingers show "
     "the field loops.",
     "visual": {"style": "statement", "transition": "slide-up"},
     "code": SEG0},
    {"narration": "Consider a long straight conductor carrying current I, "
     "and a point P at perpendicular distance d. For a finite segment "
     "subtending angles theta one and theta two from the perpendicular, "
     "integration of the Biot Savart law gives B equals mu zero I over "
     "four pi d, times sine theta two minus sine theta one. For an "
     "infinitely long wire, theta one tends to minus ninety degrees and "
     "theta two to plus ninety degrees, so B equals mu zero I over two pi "
     "d. The field lines are concentric circles around the wire, matching "
     "the right hand thumb rule.",
     "visual": {"style": "wire diagram", "transition": "carry-over"},
     "code": SEG1},
    {"narration": "For a circular loop of radius R carrying current I, "
     "take point P on the axis at distance x from the centre. Symmetry "
     "cancels the perpendicular components: each element contributes a "
     "field tilted toward the axis, and only the axial part survives. "
     "Adding all contributions gives B equals mu zero I R squared over "
     "two, times the quantity R squared plus x squared to the power three "
     "halves. At the centre, x equals zero, so B equals mu zero I over "
     "two R, directed along the axis.",
     "visual": {"style": "loop diagram", "transition": "fade"},
     "code": SEG2},
    {"narration": "A coil of N closely wound turns carries the same "
     "current in every turn, and since the fields add, the field at the "
     "centre becomes B equals N mu zero I over two R. This is why "
     "increasing the number of turns strengthens an electromagnet "
     "directly.",
     "visual": {"style": "coil diagram", "transition": "fade"},
     "code": SEG3},
    {"narration": "For a circular arc of radius R subtending angle theta "
     "at the centre, every element is at the same distance R and "
     "perpendicular to the radius, so the integration reduces to the arc "
     "length divided by R squared. This gives B equals mu zero I theta "
     "over four pi R, with theta in radians. As a check, a full circle "
     "with theta equals two pi recovers the loop result mu zero I over two "
     "R, and a semicircle with theta equals pi gives mu zero I over four "
     "R.",
     "visual": {"style": "arc diagram", "transition": "fade"},
     "code": SEG4},
    {"narration": "Practical applications. Designing solenoids and "
     "electromagnets for MRI machines and particle accelerators. "
     "Computing the fields of power transmission lines and busbars. "
     "Deflection systems of cathode ray tubes and electron beams. "
     "Inductors, transformers, and induction heating coils. And in "
     "plasma physics and geophysics, where moving charges produce the "
     "Earth's magnetic field. The law is the starting point for computing "
     "the field of any current distribution.",
     "visual": {"style": "applications", "transition": "fade"},
     "code": SEG5},
]

LECTURE = {
    "title": TITLE,
    "preset": "lab",
    "format": "mixed",
    "question": QUESTION,
    "question_code": QUESTION_CODE,
    "segments": SEGMENTS,
}
