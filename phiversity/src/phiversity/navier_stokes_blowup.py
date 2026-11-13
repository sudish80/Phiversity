TITLE = "Q35 - NAVIER-STOKES AND THE AI BLOWUP PROOF"

QUESTION = {
    "display":
        "What are the Navier-Stokes equations? State the Clay "
        "Millennium Prize existence and smoothness problem. Explain "
        "what finite-time blowup means and how it can happen, describe "
        "the September 2026 OpenAI agent result (smooth initial data "
        "whose 3D incompressible Navier-Stokes solution develops a "
        "singularity, verified in Lean), place it in the history of "
        "the problem from Leray onward, and explain what it means for "
        "the continuum model of a fluid.",
    "speech":
        "What are the Navier-Stokes equations? State the Clay "
        "Millennium Prize existence and smoothness problem. Explain "
        "what finite-time blowup means and how it can happen, "
        "describe the September twenty twenty-six OpenAI agent result "
        "in which smooth initial data lead to a singularity of the "
        "three-dimensional incompressible Navier-Stokes equations, "
        "verified in Lean, place it in the history of the problem from "
        "Leray onward, and explain what it means for the continuum "
        "model of a fluid.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 35 - NAVIER-STOKES, AI-PROVEN BLOWUP",
                     font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(r"\partial_t u+(u\cdot\nabla)u=-\frac{1}{\rho}"
                       r"\nabla p+\nu\nabla^{2}u,\qquad\nabla\cdot u=0",
                       font_size=28, color=T.constant)
        c_chem = Text("THE PROBLEM", font_size=20,
                      color=T.highlight_secondary)
        r_chem = Text(
            "Clay Millennium Prize: do smooth solutions of 3D\n"
            "incompressible NS stay smooth forever, or blow up?",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("THE RESULT", font_size=20,
                      color=T.highlight_secondary)
        r_math = Text(
            "Sept 2026, OpenAI agents: finite-time singularity\n"
            "from smooth data; paper + Lean proof public",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("THE MEANING", font_size=20,
                      color=T.highlight_secondary)
        r_econ = Text(
            "the continuum approximation of a fluid can fail;\n"
            "regularity is decided in the blowup direction",
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
        self.wait(4.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(6.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q35 - THE EQUATIONS AND THE PRIZE", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\partial_t u+(u\cdot\nabla)u=-\frac{1}{\rho}"
                     r"\nabla p+\nu\nabla^{2}u", font_size=32,
                     color=T.text_primary)
        r2 = MathTex(r"\nabla\cdot u=0\ \text{(incompressibility)}",
                     font_size=30, color=T.text_primary)
        r3 = Text("F = ma for a fluid: inertia, pressure, viscosity; the "
                  "convective term (u.grad)u is nonlinear.", font_size=23,
                  color=T.text_secondary)
        r4 = MathTex(r"\text{Clay 2000: smooth 3D data}\ \Rightarrow\ "
                     r"\text{smooth solution for all }t\ ?\ ", font_size=28,
                     color=T.result_final)
        r5 = Text("or is there smooth initial data whose solution "
                  "develops a finite-time singularity?", font_size=23,
                  color=T.text_primary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.36)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.6)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.4)
        self.wait(3.0)
        self.play(Write(r4), run_time=2.0)
        box4 = SurroundingRectangle(r4, buff=0.15, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        self.wait(2.6)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.3)
        self.wait(3.4)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q35 - WHAT BLOWUP WOULD MEAN", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"u(0)\ \text{smooth}\ \Rightarrow\ u(t)\ "
                     r"\text{smooth for }t<T^{*},\qquad "
                     r"\lim_{t\to T^{*}}\|\nabla u\|_{L^{\infty}}=\infty",
                     font_size=27, color=T.result_final)
        r2 = MathTex(r"\omega=\nabla\times u\ \text{(vorticity)},\qquad "
                     r"\text{vortex stretching: }\omega\cdot\nabla u",
                     font_size=27, color=T.text_primary)
        r3 = MathTex(r"\frac{d}{dt}\int|\omega|^{2}\ \text{can exceed "
                     r"viscous damping: energy piles onto smaller scales}",
                     font_size=26, color=T.result_intermediate)
        r4 = MathTex(r"\text{BKM criterion: blowup iff }\int_0^{T^{*}}"
                     r"\|\omega\|_{L^{\infty}}\,dt=\infty", font_size=28,
                     color=T.text_primary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.2)
        box1 = SurroundingRectangle(r1, buff=0.14, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(3.4)
        self.play(Write(r2), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r3), run_time=2.2)
        self.wait(3.0)
        self.play(Write(r4), run_time=2.0)
        self.wait(3.6)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q35 - HISTORY: LERAY TO HOU-LUO", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"1934:\ \text{Leray - weak solutions exist for "
                     r"all }t\geq0", font_size=28, color=T.text_primary)
        r2 = MathTex(r"2\text{D: global smoothness holds "
                     r"(Ladyzhenskaya)}", font_size=28,
                     color=T.result_intermediate)
        r3 = MathTex(r"3\text{D: only partial results - conditional "
                     r"regularity, small-data theory}", font_size=28,
                     color=T.text_primary)
        r4 = MathTex(r"2013:\ \text{Hou-Luo - numerics + analysis "
                     r"point to Euler singularity}", font_size=28,
                     color=T.text_primary)
        r5 = MathTex(r"90\ \text{years of no answer: the prize stood "
                     r"open}", font_size=28, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.38)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.8)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.8)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.9)
        self.wait(2.6)
        self.play(Write(r5), run_time=1.8)
        self.wait(3.4)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q35 - THE SEPTEMBER 2026 RESULT", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\exists\ \text{smooth }u_0:\ \text{NS solution "
                     r"singular at }T^{*}<\infty", font_size=30,
                     color=T.result_final)
        r2 = Text("announced Sept 8, 2026: the blowup direction of the "
                  "Clay problem, for 3D incompressible NS.", font_size=23,
                  color=T.text_primary)
        r3 = MathTex(r"\sim10^{4}\ \text{agents},\ 88\,\text{h},\ "
                     r"4.9\times10^{6}\ \text{messages},\ \sim300\,"
                     r"\text{B tokens}", font_size=27,
                     color=T.result_intermediate)
        r4 = MathTex(r"\text{Lean formalization: }+\,17\,\text{h}\ "
                     r"\text{- machine-checked steps}", font_size=27,
                     color=T.text_primary)
        r5 = Text("an Euler regularity result came the same week; "
                  "forced-Euler priority goes to Buckmaster and "
                  "Alpoge.", font_size=23, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.36)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.2)
        box1 = SurroundingRectangle(r1, buff=0.15, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=1.0)
        self.wait(3.4)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.4)
        self.wait(3.0)
        self.play(Write(r3), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.9)
        self.wait(2.8)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.3)
        self.wait(3.4)
        self.wait(6)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q35 - WHAT IT MEANS FOR FLUIDS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("the continuum picture - fluid as a smooth medium - "
                  "can break down in finite time.", font_size=24,
                  color=T.text_primary)
        r2 = Text("near a singularity, gradients diverge: the model "
                  "itself predicts where it stops applying.",
                  font_size=24, color=T.text_primary)
        r3 = MathTex(r"\text{at }t\to T^{*}:\quad "
                     r"\|\nabla u\|,\ \|\omega\|,\ \frac{\partial u_i}"
                     r"{\partial x_j}\ \to\ \infty", font_size=29,
                     color=T.result_intermediate)
        r4 = Text("practical codes (aircraft, weather, blood flow) stay "
                  "valid away from such states; the theorem maps the "
                  "boundary.", font_size=23, color=T.text_secondary)
        r5 = MathTex(r"\text{status: proof public + Lean-checked; "
                     r"community scrutiny ongoing}", font_size=27,
                     color=T.text_primary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 12.2)
        rows.next_to(rule, DOWN, buff=0.38)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(FadeIn(r1, shift=0.2 * UP), run_time=1.5)
        self.wait(3.0)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.5)
        self.wait(3.0)
        self.play(Write(r3), run_time=2.0)
        self.wait(3.0)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.4)
        self.wait(3.0)
        self.play(Write(r5), run_time=1.9)
        box5 = SurroundingRectangle(r5, buff=0.14, color=T.text_primary)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.text_primary, run_time=0.9)
        self.wait(3.6)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "The Navier-Stokes equations are Newton's second law written for a "
     "fluid: acceleration equals pressure force plus viscous force, "
     "with incompressibility as the side condition. Written out, partial "
     "u by partial t plus u dot grad u equals minus one over rho grad p, "
     "plus nu times laplacian of u. The villain is the convective term u "
     "dot grad u: it is nonlinear, and it lets fast fluid drag itself "
     "into tighter and tighter swirls. In two thousand the Clay "
     "Institute posed the question: does every smooth initial flow stay "
     "smooth forever in three dimensions, or can a solution blow up?",
     "visual": {"style": "equations", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Blowup means this: take perfectly smooth initial data, run the "
     "equation, and at some finite time T star the velocity gradients "
     "diverge, so the solution ceases to be a function. The mechanism "
     "people suspect is vortex stretching. Vorticity omega, the curl of "
     "velocity, gets amplified when fluid stretches along vortex lines; "
     "energy cascades to ever smaller scales faster than viscosity can "
     "dissipate it. The Beale Kato Majda criterion says blowup happens "
     "exactly when the time integral of the sup norm of vorticity "
     "diverges.",
     "visual": {"style": "blowup", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "The history. In nineteen thirty-four Leray proved weak solutions "
     "exist for all time, possibly non-smooth. In two dimensions, "
     "Ladyzhenskaya's estimates give global smoothness, so the question "
     "is genuinely three-dimensional. In 3D we had only conditional "
     "results: regularity under smallness assumptions, mild solutions, "
     "local existence. In twenty thirteen, Hou and Luo's numerics and "
     "analysis pointed at a singularity for the Euler equations, the "
     "inviscid limit. For ninety years nobody could answer the prize "
     "question either way.",
     "visual": {"style": "timeline", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "In September twenty twenty-six, OpenAI announced the blowup "
     "direction: there exists smooth initial data whose three-"
     "dimensional incompressible Navier-Stokes solution develops a "
     "finite-time singularity. The work was produced by roughly ten "
     "thousand autonomous agents running eighty-eight hours, exchanging "
     "about four point nine million messages and three hundred billion "
     "output tokens, on an internal model; the proof was then "
     "formalized in Lean in another seventeen hours, so every step is "
     "machine-checked. A related Euler regularity result appeared the "
     "same week; OpenAI grants priority on forced Euler to Buckmaster "
     "and Alpoge. The prize claim is waived, and community scrutiny of "
     "the proof is ongoing.",
     "visual": {"style": "result", "transition": "slide-up"},
     "code": SEG3},
    {"narration":
     "What it means. The continuum model - fluid as a smooth medium - "
     "can fail in finite time: velocity gradients and vorticity grow "
     "without bound as t approaches T star. That is not a flaw of "
     "engineering; it is the equation telling us where its own "
     "assumptions expire. Practical simulations for aircraft, weather "
     "and blood flow operate far from such states, and the theorem "
     "maps the boundary of validity. Navier and Stokes gave us the "
     "equations in the nineteenth century; in twenty twenty-six we "
     "finally know they can, in principle, tear their own smoothness "
     "apart.",
     "visual": {"style": "meaning", "transition": "fade"},
     "code": SEG4},
]

LECTURE = {
    "title": TITLE,
    "preset": "lab",
    "format": "mixed",
    "question": QUESTION,
    "question_code": QUESTION_CODE,
    "segments": SEGMENTS,
}
