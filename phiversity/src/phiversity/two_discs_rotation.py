TITLE = "Q9 - ROTATIONAL MOTION: TWO DISCS COUPLED BY FRICTION"

QUESTION = {
    "display":
        "Two uniform discs A and B, of masses M and 2M and radii R and 2R, "
        "are mounted on separate frictionless coaxial shafts. A rotates at "
        "omega0 while B is at rest. Their rough circular faces are brought "
        "into contact and friction makes them rotate together. Find (1) "
        "the moment of inertia of each disc, (2) the final common angular "
        "velocity, (3) the angular impulse on A, (4) the total loss in "
        "rotational kinetic energy, (5) the ratio of final to initial "
        "kinetic energy, and (6) the fraction of kinetic energy lost. "
        "Assume no external torque.",
    "speech":
        "Two uniform circular discs A and B, having masses M and two M and "
        "radii R and two R respectively, are mounted on separate "
        "frictionless coaxial shafts. Initially disc A rotates with "
        "angular velocity omega zero, while disc B is at rest. The two "
        "discs are brought into contact through their rough circular "
        "faces, and friction eventually makes them rotate together without "
        "slipping. Find, one, the moment of inertia of each disc. Two, the "
        "final common angular velocity after slipping stops. Three, the "
        "angular impulse exerted on disc A. Four, the total loss in "
        "rotational kinetic energy. Five, the ratio of final kinetic "
        "energy to initial kinetic energy. Six, the fraction of initial "
        "kinetic energy lost during the process. Assume no external torque "
        "acts on the system, and apply conservation of angular momentum.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 9 - ROTATIONAL MOTION (JEE ADVANCED)",
                     font_size=25, color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(r"A:\ M,\ R,\ \omega_0\qquad "
                       r"B:\ 2M,\ 2R,\ \omega=0", font_size=30,
                       color=T.constant)
        c_chem = Text("SETUP", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "coaxial shafts, no external torque\n"
            "rough faces in contact -> common omega",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("FIND", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "1  I_A, I_B\n"
            "2  final common omega\n"
            "3  angular impulse on A\n"
            "4  loss in rotational kinetic energy\n"
            "5-6  ratio and fraction of energy lost",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("PRINCIPLE", font_size=20,
                      color=T.highlight_secondary)
        r_econ = Text(
            "L = I omega is conserved\n"
            "friction is internal; only energy is lost",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, chem, maths, econ).arrange(DOWN, aligned_edge=LEFT,
                                                       buff=0.32)
        rows.move_to(UP * 0.2)
        fit_width(rows, 12.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=2.0)
        self.wait(9.1)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(10.92)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(14.55)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(10.92)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(3.64)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q9 - THE SETUP: TWO COAXIAL DISCS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        Ca = LEFT * 1.45 + DOWN * 0.6
        Cb = RIGHT * 1.05 + DOWN * 0.6
        discA = Circle(radius=1.0, color=T.graph_function, stroke_width=4)
        discA.move_to(Ca)
        discB = Circle(radius=1.5, color=T.result_intermediate, stroke_width=4)
        discB.move_to(Cb)
        fillA = Circle(radius=1.0, color=T.graph_function, stroke_width=0)
        fillA.set_fill(T.graph_function, opacity=0.12).move_to(Ca)
        fillB = Circle(radius=1.5, color=T.result_intermediate, stroke_width=0)
        fillB.set_fill(T.result_intermediate, opacity=0.12).move_to(Cb)
        shaft = Line(RIGHT * 3.4 + DOWN * 0.6, LEFT * 3.0 + DOWN * 0.6,
                     color=T.text_muted, stroke_width=2)
        labA = Text("A", font_size=30, color=T.graph_function)
        labA.move_to(Ca)
        labB = Text("B", font_size=30, color=T.result_intermediate)
        labB.move_to(Cb)
        infoA = Text("M, R", font_size=23, color=T.text_primary)
        infoA.next_to(discA, UP, buff=0.18)
        infoB = Text("2M, 2R", font_size=23, color=T.text_primary)
        infoB.next_to(discB, UP, buff=0.18)
        arrow0 = CurvedArrow(
            Ca + 1.25 * np.array([np.cos(np.radians(120)),
                                  np.sin(np.radians(120)), 0]),
            Ca + 1.25 * np.array([np.cos(np.radians(55)),
                                  np.sin(np.radians(55)), 0]),
            angle=-np.pi / 2, color=T.graph_function, stroke_width=4)
        w0 = MathTex(r"\omega_0", font_size=24, color=T.graph_function)
        w0.next_to(arrow0, RIGHT, buff=0.05)
        rest = MathTex(r"\omega=0", font_size=24, color=T.result_intermediate)
        rest.next_to(discB, DOWN, buff=0.3)
        contact = Dot(LEFT * 0.45 + DOWN * 0.6, radius=0.07,
                      color=T.graph_point)
        clab = Text("rough faces in contact", font_size=22,
                    color=T.text_secondary)
        clab.next_to(discB, RIGHT, buff=0.25).shift(UP * 0.9)
        note = Text("friction is an internal torque; angular momentum about "
                    "the axis is conserved", font_size=21,
                    color=T.text_secondary)
        note.to_edge(DOWN, buff=0.35)
        self.play(Create(shaft), run_time=0.8)
        self.play(Create(discA), FadeIn(fillA), Create(discB),
                  FadeIn(fillB), run_time=1.6)
        self.play(Write(labA), Write(labB), Write(infoA), Write(infoB),
                  run_time=1.2)
        self.play(Create(arrow0), Write(w0), Write(rest), FadeIn(contact),
                  run_time=1.2)
        self.play(FadeIn(clab), FadeIn(note), run_time=1.2)
        self.wait(4.5)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q9 (1) - MOMENT OF INERTIA OF EACH DISC", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{uniform disc: }I=\tfrac{1}{2}M R^{2}",
                     font_size=32, color=T.text_primary)
        r2 = MathTex(r"I_A=\tfrac{1}{2}M R^{2}", font_size=34,
                     color=T.result_intermediate)
        r3 = MathTex(r"I_B=\tfrac{1}{2}(2M)(2R)^{2}", font_size=34,
                     color=T.text_primary)
        r4 = MathTex(r"=\tfrac{1}{2}\cdot2M\cdot4R^{2}=4MR^{2}",
                     font_size=34, color=T.result_final)
        r5 = Text("disc B has eight times the inertia of A: twice the mass "
                  "and twice the radius", font_size=23,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 11.4)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.58)
        self.play(Write(r2), run_time=1.4)
        box2 = SurroundingRectangle(r2, buff=0.14, color=T.result_intermediate)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_intermediate, run_time=0.9)
        self.wait(2.91)
        self.play(Write(r3), run_time=1.4)
        self.wait(2.26)
        self.play(Write(r4), run_time=1.6)
        box4 = SurroundingRectangle(r4, buff=0.14, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(2.91)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.0)
        self.wait(2.75)
        self.wait(4.85)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q9 (2) - FINAL COMMON ANGULAR VELOCITY", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"L_i=I_A\omega_0=\tfrac{1}{2}MR^{2}\omega_0",
                     font_size=32, color=T.text_primary)
        r2 = MathTex(r"L_f=(I_A+I_B)\omega=\left(\tfrac{1}{2}MR^{2}"
                     r"+4MR^{2}\right)\omega", font_size=30,
                     color=T.text_primary)
        r3 = MathTex(r"L_f=\tfrac{9}{2}MR^{2}\omega", font_size=32,
                     color=T.text_primary)
        r4 = MathTex(r"\tfrac{1}{2}MR^{2}\omega_0=\tfrac{9}{2}MR^{2}\omega",
                     font_size=32, color=T.result_intermediate)
        r5 = MathTex(r"\omega=\frac{\omega_0}{9}", font_size=38,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 11.0)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.67)
        self.play(Write(r2), run_time=1.8)
        self.wait(2.84)
        self.play(Write(r3), run_time=1.4)
        self.wait(2.51)
        self.play(Write(r4), run_time=1.6)
        self.wait(2.67)
        self.play(Write(r5), run_time=1.6)
        box5 = SurroundingRectangle(r5, buff=0.18, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=1.0)
        self.wait(3.34)
        self.wait(5.01)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q9 (3) - ANGULAR IMPULSE ON DISC A", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"J_A=\Delta L_A=I_A(\omega-\omega_0)",
                     font_size=32, color=T.text_primary)
        r2 = MathTex(r"=\tfrac{1}{2}MR^{2}"
                     r"\left(\frac{\omega_0}{9}-\omega_0\right)",
                     font_size=31, color=T.text_primary)
        r3 = MathTex(r"=\tfrac{1}{2}MR^{2}\left(-\frac{8\omega_0}{9}\right)",
                     font_size=31, color=T.text_primary)
        r4 = MathTex(r"J_A=-\tfrac{4}{9}MR^{2}\omega_0", font_size=35,
                     color=T.result_final)
        r5 = MathTex(r"J_B=+\tfrac{4}{9}MR^{2}\omega_0", font_size=30,
                     color=T.text_primary)
        r6 = Text("equal and opposite impulses: the friction couple slows A "
                  "and spins up B", font_size=22, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 11.2)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.55)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.39)
        self.play(Write(r3), run_time=1.4)
        self.wait(2.23)
        self.play(Write(r4), run_time=1.4)
        box4 = SurroundingRectangle(r4, buff=0.15, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(2.87)
        self.play(Write(r5), run_time=1.2)
        self.wait(2.39)
        self.play(FadeIn(r6, shift=0.2 * UP), run_time=1.0)
        self.wait(2.71)
        self.wait(4.79)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q9 (4) - LOSS IN ROTATIONAL KINETIC ENERGY", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"KE_i=\tfrac{1}{2}I_A\omega_0^{2}"
                     r"=\tfrac{1}{4}MR^{2}\omega_0^{2}", font_size=31,
                     color=T.text_primary)
        r2 = MathTex(r"KE_f=\tfrac{1}{2}(I_A+I_B)\omega^{2}"
                     r"=\tfrac{1}{2}\cdot\tfrac{9}{2}MR^{2}"
                     r"\left(\tfrac{\omega_0}{9}\right)^{2}", font_size=29,
                     color=T.text_primary)
        r3 = MathTex(r"KE_f=\tfrac{1}{36}MR^{2}\omega_0^{2}", font_size=32,
                     color=T.text_primary)
        r4 = MathTex(r"\Delta KE=KE_i-KE_f"
                     r"=\left(\tfrac{1}{4}-\tfrac{1}{36}\right)"
                     r"MR^{2}\omega_0^{2}", font_size=30,
                     color=T.result_intermediate)
        r5 = MathTex(r"\Delta KE=\tfrac{2}{9}MR^{2}\omega_0^{2}",
                     font_size=34, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 11.4)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.41)
        self.play(Write(r2), run_time=1.8)
        self.wait(2.56)
        self.play(Write(r3), run_time=1.4)
        self.wait(2.26)
        self.play(Write(r4), run_time=1.8)
        self.wait(2.41)
        self.play(Write(r5), run_time=1.6)
        box5 = SurroundingRectangle(r5, buff=0.16, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=0.9)
        self.wait(3.01)
        self.wait(4.52)
'''

SEG5 = r'''from manim import *


class Segment5(Scene):
    def construct(self):
        head = Text("Q9 (5-6) - ENERGY RATIO AND FRACTION LOST", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\frac{KE_f}{KE_i}"
                     r"=\frac{\tfrac{1}{36}}{\tfrac{1}{4}}"
                     r"=\frac{4}{36}=\frac{1}{9}", font_size=32,
                     color=T.result_intermediate)
        r2 = MathTex(r"KE_f:KE_i=1:9", font_size=33, color=T.text_primary)
        r3 = MathTex(r"\text{fraction lost}=1-\frac{1}{9}=\frac{8}{9}",
                     font_size=33, color=T.result_final)
        r4 = MathTex(r"\approx0.889=88.9\%", font_size=33,
                     color=T.result_final)
        r5 = MathTex(r"\text{general: }\frac{KE_f}{KE_i}"
                     r"=\frac{I_A}{I_A+I_B},\quad "
                     r"\text{lost}=\frac{I_B}{I_A+I_B}", font_size=29,
                     color=T.text_primary)
        r6 = Text("independent of omega0; friction dissipates energy while "
                  "angular momentum is conserved", font_size=22,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 11.4)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        box1 = SurroundingRectangle(r1, buff=0.13, color=T.result_intermediate)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_intermediate, run_time=0.9)
        self.wait(3.12)
        self.play(Write(r2), run_time=1.2)
        self.wait(2.43)
        self.play(Write(r3), run_time=1.4)
        self.wait(2.43)
        self.play(Write(r4), run_time=1.2)
        box4 = SurroundingRectangle(r4, buff=0.13, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(2.95)
        self.play(Write(r5), run_time=1.6)
        self.wait(2.95)
        self.play(FadeIn(r6, shift=0.2 * UP), run_time=1.0)
        self.wait(3.12)
        self.wait(5.2)
'''

SEGMENTS = [
    {"narration":
     "Here is the setup. Disc A, of mass M and radius R, spins at angular "
     "velocity omega zero. Disc B, of mass two M and radius two R, is at "
     "rest. They share a frictionless axis and no external torque acts. "
     "When the rough faces touch, friction transfers angular momentum "
     "from A to B until they rotate together at a common angular "
     "velocity. Because friction is internal to the pair, the total "
     "angular momentum is conserved, even though energy is lost.",
     "visual": {"style": "disc diagram", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Part one. For a uniform disc about its central axis, the moment of "
     "inertia is one half M R squared. So I A is one half M R squared. "
     "For disc B, substitute mass two M and radius two R: I B equals one "
     "half times two M times the square of two R, which is one half times "
     "two M times four R squared, giving four M R squared. Disc B has "
     "eight times the inertia of disc A.",
     "visual": {"style": "moments", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Part two. The initial angular momentum is I A omega zero, one half "
     "M R squared omega zero. The final angular momentum is the total "
     "inertia, I A plus I B, times the common omega, which is one half "
     "plus four, that is nine halves M R squared omega. Equating the two "
     "and cancelling M R squared gives omega equal to omega zero over "
     "nine. So the pair settles at one ninth of the original spin.",
     "visual": {"style": "conservation", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "Part three. The angular impulse on A equals its change in angular "
     "momentum, I A times omega minus omega zero. Substituting omega "
     "equals omega zero over nine gives one half M R squared times minus "
     "eight omega zero over nine, which is minus four ninths M R squared "
     "omega zero. The minus sign means it opposes the original spin. The "
     "impulse on B is plus four ninths M R squared omega zero, equal and "
     "opposite.",
     "visual": {"style": "impulse", "transition": "fade"},
     "code": SEG3},
    {"narration":
     "Part four. The initial kinetic energy is one half I A omega zero "
     "squared, that is one quarter M R squared omega zero squared. The "
     "final kinetic energy is one half the total inertia times omega "
     "squared, which reduces to one thirty sixth M R squared omega zero "
     "squared. The loss is the difference, one quarter minus one thirty "
     "sixth, giving two ninths M R squared omega zero squared.",
     "visual": {"style": "energy loss", "transition": "fade"},
     "code": SEG4},
    {"narration":
     "Parts five and six. The ratio of final to initial kinetic energy is "
     "one thirty sixth divided by one quarter, which is four over thirty "
     "six, or one ninth. So the energies are in the ratio one to nine. "
     "The fraction lost is one minus one ninth, that is eight ninths, "
     "about eighty eight point nine percent. In general the ratio is I A "
     "over I A plus I B and the fraction lost is I B over that sum, "
     "independent of omega zero. Friction dissipates energy while angular "
     "momentum is conserved.",
     "visual": {"style": "ratio", "transition": "fade"},
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
