TITLE = "Q6 - CAR ON A CIRCULAR ROAD"

QUESTION = {
    "display":
        "A car of mass 1000 kg moves along a circular road of radius 50 m "
        "at a constant speed of 20 m/s. (a) Draw a neat diagram of the car "
        "on the circular path. (b) Calculate the centripetal acceleration. "
        "(c) Calculate the centripetal force. (d) Find the minimum "
        "coefficient of friction to prevent skidding. (e) What happens to "
        "the centripetal force if the speed is doubled? (f) Derive the "
        "maximum safe speed on a level circular road.",
    "speech":
        "A car of mass one thousand kilograms moves along a circular road "
        "of radius fifty metres at a constant speed of twenty metres per "
        "second. Part a, draw a neat diagram of the car on the circular "
        "path. Part b, calculate the centripetal acceleration. Part c, "
        "calculate the centripetal force. Part d, find the minimum "
        "coefficient of friction needed to prevent skidding. Part e, what "
        "happens to the centripetal force if the speed is doubled? Part f, "
        "derive the expression for the maximum safe speed on a level "
        "circular road.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 6 - CIRCULAR MOTION", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(r"m=1000\ \text{kg},\quad r=50\ \text{m},\quad "
                       r"v=20\ \text{m/s}", font_size=29, color=T.constant)
        c_chem = Text("GIVEN", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "uniform circular motion\n"
            "speed constant, direction changing",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("PLAN", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "a  diagram: circle, car, v, a_c\n"
            "b  a_c = v^2 / r\n"
            "c  F_c = m a_c\n"
            "d  friction: mu m g = m v^2 / r\n"
            "e-f  speed doubling; derive v_max",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("RESULTS", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "a_c = 8 m/s^2,   F_c = 8000 N\n"
            "mu_min ~ 0.82,   doubled speed -> 32000 N\n"
            "v_max = sqrt(mu r g)",
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
        self.wait(5.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(8.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q6 (a) - THE CIRCULAR PATH: FREE-BODY VIEW",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        C = DOWN * 0.5
        R = 1.85
        ang = np.radians(38)
        P = C + R * np.array([np.cos(ang), np.sin(ang), 0])
        circle = Circle(radius=R, color=T.graph_reference, stroke_width=3)
        circle.move_to(C)
        cen = Dot(C, radius=0.08, color=T.graph_point)
        olab = Text("O", font_size=24, color=T.graph_point)
        olab.next_to(cen, DOWN, buff=0.1)
        radial = DashedLine(C, P, color=T.text_secondary, stroke_width=2)
        rlab = MathTex(r"r=50\,\text{m}", font_size=24, color=T.text_secondary)
        rlab.next_to(radial.get_center(), DOWN, buff=0.12)
        tangent = np.array([-np.sin(ang), np.cos(ang), 0])
        car = Rectangle(width=0.56, height=0.28, color=T.text_primary,
                        stroke_width=3)
        car.set_fill(T.background_primary, opacity=1.0)
        car.rotate(ang + np.pi / 2)
        car.move_to(P)
        varr = Arrow(P, P + 1.25 * tangent, buff=0, color=T.graph_function,
                     stroke_width=5)
        vlab = MathTex(r"v=20\,\text{m/s}", font_size=24,
                       color=T.graph_function)
        vlab.next_to(varr.get_end(), tangent, buff=0.12)
        inward = (C - P) / np.linalg.norm(C - P)
        aarr = Arrow(P, P + 1.15 * inward, buff=0, color=T.cancel_mark,
                     stroke_width=5)
        alab = MathTex(r"a_c=\frac{v^2}{r}", font_size=24,
                       color=T.cancel_mark)
        alab.next_to(aarr.get_center(), inward * -1, buff=0.1)
        flab = Text("static friction supplies the centripetal force",
                    font_size=22, color=T.text_secondary)
        flab.next_to(circle, DOWN, buff=0.35)
        self.play(Create(circle), FadeIn(cen), Write(olab), run_time=1.4)
        self.play(Create(radial), Write(rlab), run_time=0.9)
        self.play(FadeIn(car), run_time=0.8)
        self.play(Create(varr), Write(vlab), run_time=1.0)
        self.play(Create(aarr), Write(alab), run_time=1.0)
        self.play(FadeIn(flab, shift=0.2 * UP), run_time=1.0)
        self.wait(4.0)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q6 (b) - CENTRIPETAL ACCELERATION", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"a_c=\frac{v^{2}}{r}", font_size=36,
                     color=T.result_intermediate)
        r2 = MathTex(r"=\frac{(20)^{2}}{50}", font_size=34,
                     color=T.text_primary)
        r3 = MathTex(r"=\frac{400}{50}=8\ \text{m/s}^{2}", font_size=34,
                     color=T.result_final)
        r4 = Text("directed towards the centre of the circle", font_size=25,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        fit_width(rows, 10.5)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(1.74)
        self.play(Write(r2), run_time=1.4)
        self.wait(1.53)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.16, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(2.05)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.0)
        self.wait(1.53)
        self.wait(3.07)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q6 (c) - CENTRIPETAL FORCE", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"F_c=m a_c=\frac{m v^{2}}{r}", font_size=36,
                     color=T.result_intermediate)
        r2 = MathTex(r"=1000\times 8", font_size=34, color=T.text_primary)
        r3 = MathTex(r"=8000\ \text{N}=8\ \text{kN}", font_size=34,
                     color=T.result_final)
        r4 = Text("on a level road this force is provided entirely by "
                  "static friction", font_size=24, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        fit_width(rows, 11.0)
        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.48)
        self.play(Write(r2), run_time=1.2)
        self.wait(1.93)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.16, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(2.75)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.0)
        self.wait(2.34)
        self.wait(4.13)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q6 (d) - MINIMUM COEFFICIENT OF FRICTION", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"f_{s,\max}=\mu_s N=\mu_s m g", font_size=32,
                     color=T.text_primary)
        r2 = MathTex(r"\text{prevent skidding: }f_{s,\max}\ge "
                     r"\frac{m v^{2}}{r}", font_size=30, color=T.text_primary)
        r3 = MathTex(r"\mu_s\ge\frac{v^{2}}{r g}"
                     r"=\frac{400}{50\times 9.8}", font_size=32,
                     color=T.result_intermediate)
        r4 = MathTex(r"\mu_s\ge 0.816\approx 0.82", font_size=34,
                     color=T.result_final)
        r5 = Text("with g = 10, mu ~ 0.8; ordinary tyres cannot exceed "
                  "about 0.8 on a dry road", font_size=22,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 11.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.6)
        self.wait(3.4)
        self.play(Write(r3), run_time=1.8)
        self.wait(3.6)
        self.play(Write(r4), run_time=1.4)
        box4 = SurroundingRectangle(r4, buff=0.16, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.8)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.0)
        self.wait(3.4)
        self.wait(6)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q6 (e) - SPEED DOUBLED", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"F_c=\frac{m v^{2}}{r}\ \Rightarrow\ F_c\propto v^{2}",
                     font_size=33, color=T.text_primary)
        r2 = MathTex(r"v\to 2v:\quad F_c\to 4F_c", font_size=34,
                     color=T.result_intermediate)
        r3 = MathTex(r"F_c'=4\times 8000=32000\ \text{N}=32\ \text{kN}",
                     font_size=32, color=T.result_final)
        r4 = MathTex(r"\text{required }\mu=4\times 0.816\approx 3.27",
                     font_size=30, color=T.text_primary)
        r5 = Text("far beyond tyre grip, so the car skids unless the road "
                  "is banked", font_size=23, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 11.2)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.07)
        self.play(Write(r2), run_time=1.4)
        self.wait(1.95)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.15, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(2.32)
        self.play(Write(r4), run_time=1.4)
        self.wait(1.83)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.0)
        self.wait(2.07)
        self.wait(3.66)
'''

SEG5 = r'''from manim import *


class Segment5(Scene):
    def construct(self):
        head = Text("Q6 (f) - MAXIMUM SAFE SPEED ON A LEVEL ROAD",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"f_{s,\max}=m a_c", font_size=32, color=T.text_primary)
        r2 = MathTex(r"\mu_s m g=\frac{m v_{\max}^{2}}{r}", font_size=33,
                     color=T.text_primary)
        r3 = MathTex(r"\Rightarrow\ v_{\max}=\sqrt{\mu_s r g}", font_size=36,
                     color=T.result_final)
        r4 = MathTex(r"=\sqrt{0.816\times 50\times 9.8}\approx 20\ "
                     r"\text{m/s}", font_size=32, color=T.result_intermediate)
        r5 = Text("independent of the mass of the car; only mu, r and g "
                  "matter", font_size=23, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 11.2)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.4)
        self.wait(2.52)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.85)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.16, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.36)
        self.play(Write(r4), run_time=1.6)
        self.wait(2.69)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.0)
        self.wait(2.85)
        self.wait(5.04)
'''

SEGMENTS = [
    {"narration":
     "Part a. Here is the car seen from above, moving on a circle of "
     "radius fifty metres about the centre O. Its velocity is always "
     "tangent to the circle, and because the direction of motion changes "
     "continuously, there is a centripetal acceleration pointing towards "
     "the centre. On a level road the only horizontal force available is "
     "static friction between the tyres and the road, and it points "
     "towards the centre.",
     "visual": {"style": "circle diagram", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Part b. The centripetal acceleration is v squared over r. "
     "Substituting v equals twenty metres per second and r equals fifty "
     "metres gives four hundred over fifty, which is eight metres per "
     "second squared, directed towards the centre of the circular path.",
     "visual": {"style": "calculation", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Part c. The centripetal force is mass times centripetal "
     "acceleration, which is also m v squared over r. That is one "
     "thousand times eight, giving eight thousand newtons, or eight "
     "kilonewtons, directed towards the centre. On a level road this "
     "force is provided entirely by static friction.",
     "visual": {"style": "calculation", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "Part d. Static friction has a maximum value mu times the normal "
     "force, which equals mu m g. To prevent skidding this maximum must "
     "be at least m v squared over r. The mass cancels, leaving mu "
     "greater than or equal to v squared over r g. Substituting gives "
     "four hundred over fifty times nine point eight, so mu must be at "
     "least zero point eight one six. Ordinary tyres on a dry road "
     "cannot exceed about zero point eight, so twenty metres per second "
     "is close to the limit.",
     "visual": {"style": "friction limit", "transition": "fade"},
     "code": SEG3},
    {"narration":
     "Part e. Since the centripetal force is proportional to the square "
     "of the speed, doubling the speed multiplies the force by four. The "
     "force rises from eight thousand to thirty two thousand newtons. "
     "The coefficient of friction needed would be about three point "
     "three, far beyond what tyres can provide, so the car would skid "
     "unless the road is banked.",
     "visual": {"style": "scaling", "transition": "fade"},
     "code": SEG4},
    {"narration":
     "Part f. For the maximum safe speed, friction is just sufficient to "
     "supply the centripetal force, so mu m g equals m v max squared over "
     "r. Cancelling the mass and taking the square root gives v max "
     "equals the square root of mu r g. With mu zero point eight one six, "
     "r fifty metres and g nine point eight, this is about twenty metres "
     "per second. Notice that the answer is independent of the mass of "
     "the car.",
     "visual": {"style": "derivation", "transition": "fade"},
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
