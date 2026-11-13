TITLE = "Q3 - 2D HEAT EQUATION ON A RECTANGULAR PLATE"

QUESTION = {
    "display":
        "A thin rectangular plate 0 ≤ x ≤ a, 0 ≤ y ≤ b obeys "
        "$\\partial T/\\partial t=\\alpha^2(\\partial^2 T/\\partial x^2+"
        "\\partial^2 T/\\partial y^2)$ with "
        "$T(x,y,0)=T_0\\sin(\\pi x/a)\\sin(2\\pi y/b)$ and zero "
        "boundary temperatures on all four edges. (a) derive the equation, "
        "(b-c) separate variables and find eigenvalues/eigenfunctions, "
        "(d) general solution, (e-f) apply the initial condition, "
        "(g) temperature at the centre at time τ, (h) long-term behaviour, "
        "(i) physical meaning of eigenvalues/eigenfunctions.",
    "speech":
        "A thin rectangular plate with sides a and b obeys the two "
        "dimensional heat equation with thermal diffusivity alpha squared. "
        "It starts with temperature T zero sine pi x over a sine two pi y "
        "over b, and all four edges are held at zero. Part a, derive the "
        "equation. Parts b and c, separate variables and find the "
        "eigenvalues and eigenfunctions. Part d, obtain the general "
        "solution. Parts e and f, apply the initial condition and give the "
        "final expression. Part g, find the temperature at the centre at "
        "time tau. Part h, investigate the long term behaviour. Part i, "
        "explain the physical significance of the eigenvalues and "
        "eigenfunctions.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 3 - PARTIAL DIFFERENTIAL EQUATIONS", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(r"T_t=\alpha^2(T_{xx}+T_{yy}),\quad "
                       r"T(x,y,0)=T_0\sin\frac{\pi x}{a}\sin\frac{2\pi y}{b}",
                       font_size=27, color=T.constant)
        c_chem = Text("SETUP", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "plate: 0 <= x <= a, 0 <= y <= b\n"
            "edges held at T = 0 (Dirichlet)",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("METHOD", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "a  derive: energy conservation + Fourier's law\n"
            "b-d  separate T = X Y G; general double sum\n"
            "e-f  match initial condition -> final T(x,y,t)\n"
            "g-h  centre value; t -> infinity behaviour\n"
            "i  meaning of eigenvalues / eigenfunctions",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("ANSWER", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "T = T0 sin(pi x/a) sin(2 pi y/b) *\n"
            "    exp(-alpha^2 [(pi/a)^2 + (2 pi/b)^2] t)\n"
            "centre always 0; T -> 0 as t -> infinity",
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
        self.wait(9.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q3 (a) - DERIVING THE HEAT EQUATION", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{conservation of thermal energy: }"
                     r"\frac{d}{dt}\int_V \rho c T\,dV"
                     r" = -\int_S \mathbf{q}\cdot\mathbf{n}\,dS",
                     font_size=28, color=T.text_primary)
        r2 = MathTex(r"\text{Fourier's law: }\mathbf{q}=-k\,\nabla T",
                     font_size=29, color=T.variable)
        r3 = MathTex(r"\text{divergence theorem: }\rho c"
                     r"\ \frac{\partial T}{\partial t}"
                     r" = k\,\nabla^2 T",
                     font_size=29, color=T.text_primary)
        r4 = MathTex(r"\frac{\partial T}{\partial t}"
                     r" = \alpha^2\nabla^2 T,\qquad"
                     r"\alpha^2=\frac{k}{\rho c}",
                     font_size=32, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 11.5)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.0)
        self.wait(5.0)
        self.play(Write(r2), run_time=1.4)
        self.wait(3.5)
        self.play(Write(r3), run_time=1.8)
        self.wait(4.5)
        self.play(Write(r4), run_time=1.6)
        box4 = SurroundingRectangle(r4, buff=0.15, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q3 (b)-(c) - SEPARATION OF VARIABLES", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"T(x,y,t)=X(x)\,Y(y)\,G(t)",
                     font_size=32, color=T.variable)
        r2 = MathTex(r"\frac{G'}{\alpha^2 G}=\frac{X''}{X}+\frac{Y''}{Y}"
                     r"=-\lambda",
                     font_size=31, color=T.text_primary)
        r3 = MathTex(r"G'+\alpha^2\lambda G=0\ \Rightarrow\ "
                     r"G\propto e^{-\alpha^2\lambda t}",
                     font_size=29, color=T.text_primary)
        r4 = MathTex(r"X''+\mu X=0,\ X(0)=X(a)=0:\quad"
                     r"\mu_n=\left(\frac{n\pi}{a}\right)^2,\ "
                     r"X_n=\sin\frac{n\pi x}{a}",
                     font_size=28, color=T.result_intermediate)
        r5 = MathTex(r"Y''+\nu Y=0,\ Y(0)=Y(b)=0:\quad"
                     r"\nu_m=\left(\frac{m\pi}{b}\right)^2,\ "
                     r"Y_m=\sin\frac{m\pi y}{b}",
                     font_size=28, color=T.result_intermediate)
        r6 = MathTex(r"\lambda_{nm}=\mu_n+\nu_m,\qquad n,m=1,2,3,\dots",
                     font_size=29, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 11.7)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.4)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.8)
        self.wait(4.5)
        self.play(Write(r3), run_time=1.6)
        self.wait(3.5)
        self.play(Write(r4), run_time=1.8)
        self.wait(4.5)
        self.play(Write(r5), run_time=1.8)
        self.wait(4.5)
        self.play(Write(r6), run_time=1.4)
        box6 = SurroundingRectangle(r6, buff=0.13, color=T.result_final)
        self.play(Create(box6), run_time=0.7)
        emphasize(self, r6, color=T.result_final, run_time=0.9)
        self.wait(3.5)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q3 (d) - GENERAL SOLUTION", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{superposition of all modes:}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(
            r"T(x,y,t)=\sum_{n=1}^{\infty}\sum_{m=1}^{\infty} A_{nm}"
            r"\sin\frac{n\pi x}{a}\sin\frac{m\pi y}{b}"
            r"\,e^{-\alpha^2\left[\left(\frac{n\pi}{a}\right)^2"
            r"+\left(\frac{m\pi}{b}\right)^2\right]t}",
            font_size=27, color=T.result_intermediate)
        r3 = MathTex(r"\text{every term satisfies the heat equation and all}"
                     r"\ \text{four zero boundary conditions}",
                     font_size=28, color=T.text_secondary)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 11.8)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.2)
        self.wait(3.0)
        self.play(Write(r2), run_time=2.4)
        self.wait(5.5)
        self.play(Write(r3), run_time=1.4)
        self.wait(4.0)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q3 (e)-(f) - APPLY THE INITIAL CONDITION", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{at }t=0:\ "
                     r"T(x,y,0)=T_0\sin\frac{\pi x}{a}\sin\frac{2\pi y}{b}",
                     font_size=30, color=T.text_primary)
        r2 = MathTex(r"\text{this is exactly one mode: }n=1,\ m=2",
                     font_size=29, color=T.result_intermediate)
        r3 = MathTex(r"A_{12}=T_0,\qquad A_{nm}=0\ \text{otherwise}",
                     font_size=29, color=T.result_intermediate)
        r4 = MathTex(
            r"T(x,y,t)=T_0\sin\frac{\pi x}{a}\sin\frac{2\pi y}{b}"
            r"\,e^{-\alpha^2\left[\left(\frac{\pi}{a}\right)^2"
            r"+\left(\frac{2\pi}{b}\right)^2\right]t}",
            font_size=29, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 11.5)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(4.0)
        self.play(Write(r2), run_time=1.2)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.4)
        self.wait(3.5)
        self.play(Write(r4), run_time=2.0)
        box4 = SurroundingRectangle(r4, buff=0.15, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(4.5)
        self.wait(6)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q3 (g)-(h) - CENTRE VALUE AND LONG-TERM BEHAVIOUR",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{centre: }x=\frac{a}{2},\ y=\frac{b}{2}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"\sin\frac{\pi}{2}=1,\qquad \sin\pi=0",
                     font_size=29, color=T.text_primary)
        r3 = MathTex(r"T\!\left(\frac{a}{2},\frac{b}{2},\tau\right)=0\ "
                     r"\text{for every }\tau",
                     font_size=31, color=T.result_final)
        r4 = MathTex(r"\text{the centre lies on the nodal line }y=\frac{b}{2}",
                     font_size=28, color=T.text_secondary)
        r5 = MathTex(r"\text{as }t\to\infty:\ "
                     r"e^{-\alpha^2\lambda t}\to 0\ \Rightarrow\ "
                     r"T\to 0\ \text{everywhere (uniform)}",
                     font_size=30, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 11.7)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.2)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.4)
        self.wait(3.5)
        self.play(Write(r3), run_time=1.6)
        box3 = SurroundingRectangle(r3, buff=0.13, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.5)
        self.play(Write(r4), run_time=1.4)
        self.wait(3.5)
        self.play(Write(r5), run_time=2.0)
        box5 = SurroundingRectangle(r5, buff=0.13, color=T.result_intermediate)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_intermediate, run_time=0.9)
        self.wait(4.0)
        self.wait(6)
'''

SEG5 = r'''from manim import *


class Segment5(Scene):
    def construct(self):
        head = Text("Q3 (i) - PHYSICAL SIGNIFICANCE", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{eigenvalues } \lambda_{nm}\ \text{set the decay}"
                     r"\ \text{rate of each mode: }e^{-\alpha^2\lambda t}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"\text{larger eigenvalues = shorter wavelengths =}"
                     r"\ \text{faster cooling}",
                     font_size=29, color=T.result_intermediate)
        r3 = MathTex(r"\text{eigenfunctions are the spatial modes that}"
                     r"\ \text{satisfy the boundary conditions}",
                     font_size=29, color=T.text_primary)
        r4 = MathTex(r"\text{general solution = superposition of independent}"
                     r"\ \text{modes, each decaying on its own}",
                     font_size=29, color=T.result_final)
        r5 = MathTex(r"\text{that is why small-scale detail disappears first in}"
                     r"\ \text{real heat conduction}",
                     font_size=28, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 11.8)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(4.0)
        self.play(Write(r2), run_time=1.6)
        self.wait(3.5)
        self.play(Write(r3), run_time=1.6)
        self.wait(3.5)
        self.play(Write(r4), run_time=1.8)
        box4 = SurroundingRectangle(r4, buff=0.13, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.5)
        self.play(Write(r5), run_time=1.4)
        self.wait(3.5)
        self.wait(6)
'''

SEGMENTS = [
    {"narration": "We derive the heat equation from two physical laws. "
     "First, conservation of thermal energy: the rate of change of stored "
     "thermal energy inside any volume equals the net heat flow into it "
     "across its surface. Second, Fourier's law: heat flux is proportional "
     "to the negative temperature gradient, with conductivity k. Applying "
     "the divergence theorem turns the surface integral into a volume "
     "integral, giving rho c partial T partial t equals k nabla squared T. "
     "Dividing by rho c yields the heat equation with thermal diffusivity "
     "alpha squared equal to k over rho c.",
     "visual": {"style": "derivation", "transition": "slide-up"},
     "code": SEG0},
    {"narration": "Separation of variables assumes T equals X of x times Y "
     "of y times G of t. Substituting into the heat equation and dividing "
     "by X Y G separates time from space, so both sides equal a constant, "
     "minus lambda. The space part splits into two one-dimensional "
     "problems: X double prime plus mu X equals zero, and Y double prime "
     "plus nu Y equals zero, with mu plus nu equal to lambda. The zero "
     "boundary conditions give eigenvalues mu n equals n pi over a squared "
     "and nu m equals m pi over b squared, with sine eigenfunctions. The "
     "time equation gives G proportional to e to the minus alpha squared "
     "lambda t.",
     "visual": {"style": "separation", "transition": "fade"},
     "code": SEG1},
    {"narration": "By superposition, the general solution is a double sum "
     "over all modes: T equals the sum over n and m of A n m times sine n "
     "pi x over a, times sine m pi y over b, times e to the minus alpha "
     "squared times the sum of n pi over a squared and m pi over b "
     "squared, times t. Every term satisfies the heat equation and all "
     "four zero boundary conditions.",
     "visual": {"style": "general solution", "transition": "fade"},
     "code": SEG2},
    {"narration": "At t equals zero, the series must equal the initial "
     "temperature, T zero sine pi x over a sine two pi y over b. This is "
     "exactly one mode: n equals one and m equals two. Hence all "
     "coefficients vanish except A one two equals T zero. The final "
     "analytical solution is therefore T of x y t equals T zero sine pi x "
     "over a sine two pi y over b, times e to the minus alpha squared "
     "times the sum of pi over a squared and two pi over b squared, times "
     "t.",
     "visual": {"style": "final solution", "transition": "fade"},
     "code": SEG3},
    {"narration": "At the centre, x equals a over two and y equals b over "
     "two. Sine of pi over two is one, but sine of pi is zero, so the "
     "temperature at the centre is zero for every time, including t equals "
     "tau. The centre lies on the nodal line y equals b over two. For "
     "long times, the exponential factor decays to zero, so the "
     "temperature tends uniformly to zero everywhere, which matches the "
     "physical expectation that the plate cools to the zero-temperature "
     "edges.",
     "visual": {"style": "centre + limit", "transition": "carry-over"},
     "code": SEG4},
    {"narration": "Physical significance. The eigenvalues control the "
     "decay rate of each mode, through e to the minus alpha squared lambda "
     "t. Larger eigenvalues mean shorter wavelengths and faster cooling, "
     "because temperature gradients are steeper. The eigenfunctions are "
     "the spatial shapes, or modes, that satisfy the boundary conditions, "
     "like standing waves. The complete solution is a superposition of "
     "independent modes, each decaying at its own rate, which is why "
     "high-frequency detail disappears first in real heat conduction.",
     "visual": {"style": "summary", "transition": "fade"},
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
