TITLE = "Q36 - THIRTY FORMULAS AND THEOREMS FROM FIRST PRINCIPLES"

QUESTION = {
    "display":
        "Instruction: Derive each formula from first principles. Show "
        "all intermediate mathematical steps, explain the assumptions, "
        "use appropriate mathematical notation, and include labelled "
        "diagrams wherever necessary. 30 items: 1 Quadratic Formula; "
        "2 Binomial Theorem; 3 Sum of an Arithmetic Progression; "
        "4 Sum of a Geometric Progression; 5 Exponential and "
        "Logarithmic Laws; 6 Sine Rule; 7 Cosine Rule; 8 Area of a "
        "Triangle; 9 Double-Angle Formula; 10 Product-to-Sum "
        "Identities; 11 Distance Formula; 12 Section Formula; 13 "
        "Equation of a Circle; 14 Equation of a Parabola; 15 Equation "
        "of an Ellipse; 16 Derivative of a Power Function; 17 Product "
        "Rule; 18 Quotient Rule; 19 Chain Rule; 20 Derivatives of "
        "Trigonometric Functions; 21 Integration by Parts; 22 "
        "Integration of a Power Function; 23 Fundamental Theorem of "
        "Calculus; 24 Volume of a Solid of Revolution; 25 Dot Product "
        "Formula; 26 Cross Product Magnitude; 27 Equation of a Plane; "
        "28 Bayes' Theorem; 29 Euler's Formula for Polyhedra; 30 "
        "Heron's Formula.",
    "speech":
        "Instruction: derive each formula from first principles, show "
        "all intermediate steps, explain the assumptions, use proper "
        "notation, and include labelled diagrams wherever necessary. "
        "Thirty items across algebra, trigonometry, coordinate "
        "geometry, calculus, vectors, probability, and geometry: the "
        "quadratic formula, binomial theorem, arithmetic and geometric "
        "series, logarithm laws, sine and cosine rules, triangle area, "
        "double-angle and product-to-sum identities, distance and "
        "section formulas, circle, parabola and ellipse equations, "
        "power, product, quotient, chain and trigonometric "
        "derivatives, integration by parts, power integrals, the "
        "fundamental theorem, volumes of revolution, dot and cross "
        "products, plane equations, Bayes' theorem, Euler's polyhedron "
        "formula, and Heron's formula.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 36 - THIRTY FORMULAS, FIRST PRINCIPLES",
                     font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        inst = Text("Instruction: derive each formula from first "
                    "principles. Show all intermediate mathematical "
                    "steps, explain the assumptions, use appropriate "
                    "mathematical notation, and include labelled "
                    "diagrams wherever necessary.", font_size=19,
                    color=T.text_primary)
        fit_width(inst, 12.7)
        cols = []
        groups = [
            ["1  Quadratic Formula", "2  Binomial Theorem",
             "3  Sum of an AP", "4  Sum of a GP",
             "5  Exponential & Log Laws", "6  Sine Rule",
             "7  Cosine Rule", "8  Area of a Triangle",
             "9  Double-Angle Formula", "10 Product-to-Sum Identities"],
            ["11 Distance Formula", "12 Section Formula",
             "13 Equation of a Circle", "14 Equation of a Parabola",
             "15 Equation of an Ellipse", "16 Derivative of x^n",
             "17 Product Rule", "18 Quotient Rule", "19 Chain Rule",
             "20 Derivatives of sin x, cos x"],
            ["21 Integration by Parts", "22 Integration of x^n",
             "23 Fundamental Theorem of Calculus",
             "24 Volume of a Solid of Revolution", "25 Dot Product",
             "26 Cross Product Magnitude", "27 Equation of a Plane",
             "28 Bayes' Theorem", "29 Euler's Formula for Polyhedra",
             "30 Heron's Formula"],
        ]
        for g in groups:
            col = VGroup(*[Text(s, font_size=15, color=T.text_secondary)
                           for s in g]).arrange(DOWN, aligned_edge=LEFT,
                                                 buff=0.13)
            cols.append(col)
        catalog = VGroup(*cols).arrange(RIGHT, buff=0.7)
        fit_width(catalog, 12.7)
        if catalog.height > 5.4:
            catalog.scale_to_fit_height(5.4)
        block = VGroup(inst, catalog).arrange(DOWN, aligned_edge=LEFT,
                                              buff=0.3)
        block.move_to(DOWN * 0.25)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(FadeIn(inst, shift=0.2 * UP), run_time=1.2)
        self.wait(4.5)
        self.play(FadeIn(catalog, shift=0.2 * UP), run_time=1.6)
        self.wait(9.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(block.animate.scale(0.72).to_edge(UP, buff=0.2), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q36 - ALGEBRA 1-2: QUADRATIC + BINOMIAL",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"ax^{2}+bx+c=0\ \Rightarrow\ "
                     r"x^{2}+\frac{b}{a}x=-\frac{c}{a}", font_size=29,
                     color=T.text_primary)
        r2 = MathTex(r"x^{2}+\frac{b}{a}x+\left(\frac{b}{2a}\right)^{2}"
                     r"=-\frac{c}{a}+\frac{b^{2}}{4a^{2}}", font_size=27,
                     color=T.text_primary)
        r3 = MathTex(r"\left(x+\frac{b}{2a}\right)^{2}="
                     r"\frac{b^{2}-4ac}{4a^{2}}", font_size=29,
                     color=T.result_intermediate)
        r4 = MathTex(r"x+\frac{b}{2a}=\pm\sqrt{\frac{b^{2}-4ac}{4a^{2}}}"
                     r"\ \Rightarrow\ x=\frac{-b\pm\sqrt{b^{2}-4ac}}{2a}",
                     font_size=28, color=T.result_final)
        r5 = MathTex(r"(a+b)^{n}=\sum_{r=0}^{n}\binom{n}{r}"
                     r"a^{n-r}b^{r}", font_size=33,
                     color=T.result_final)
        r6 = Text("binomial: coefficient of a^{n-r} b^r counts "
                  "ways to choose the r b-factors of n.", font_size=22,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.34)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        self.wait(3.0)
        self.play(Write(r2), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r4), run_time=2.0)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r5), run_time=2.0)
        box5 = SurroundingRectangle(r5, buff=0.12, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        self.wait(2.8)
        self.play(FadeIn(r6, shift=0.2 * UP), run_time=1.3)
        self.wait(3.4)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q36 - ALGEBRA 3-4: AP AND GP SUMS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"S_n=a+(a+d)+\cdots+(a+(n-1)d)", font_size=28,
                     color=T.text_primary)
        r2 = MathTex(r"\text{reverse: }S_n=(a+(n-1)d)+\cdots+a",
                     font_size=28, color=T.text_primary)
        r3 = MathTex(r"2S_n=n(2a+(n-1)d)\ \Rightarrow\ "
                     r"S_n=\frac{n}{2}[2a+(n-1)d]", font_size=29,
                     color=T.result_final)
        r4 = MathTex(r"S_n=a+ar+\cdots+ar^{n-1},\quad "
                     r"rS_n=ar+\cdots+ar^{n}", font_size=28,
                     color=T.text_primary)
        r5 = MathTex(r"(1-r)S_n=a(1-r^{n})\ \Rightarrow\ "
                     r"S_n=\frac{a(1-r^{n})}{1-r}", font_size=29,
                     color=T.result_intermediate)
        r6 = MathTex(r"|r|<1:\quad S_{\infty}=\lim_{n\to\infty}"
                     r"S_n=\frac{a}{1-r}", font_size=29,
                     color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.34)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.8)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.9)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r5), run_time=1.9)
        self.wait(3.0)
        self.play(Write(r6), run_time=1.9)
        box6 = SurroundingRectangle(r6, buff=0.12, color=T.result_final)
        self.play(Create(box6), run_time=0.7)
        emphasize(self, r6, color=T.result_final, run_time=0.9)
        self.wait(3.4)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q36 - ALGEBRA 5: LOGARITHMIC LAWS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{definition: }y=\log_a x\iff x=a^{y}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"\text{let }x=a^{p},\ y=a^{q}:\ "
                     r"\log_a x=p,\ \log_a y=q", font_size=28,
                     color=T.text_primary)
        r3 = MathTex(r"xy=a^{p}a^{q}=a^{p+q}\ \Rightarrow\ "
                     r"\log_a(xy)=p+q=\log_a x+\log_a y", font_size=29,
                     color=T.result_final)
        r4 = MathTex(r"\frac{x}{y}=\frac{a^{p}}{a^{q}}=a^{p-q}\ "
                     r"\Rightarrow\ \log_a\left(\frac{x}{y}\right)"
                     r"=\log_a x-\log_a y", font_size=29,
                     color=T.result_final)
        r5 = MathTex(r"\text{assumptions: }a>0,\ a\neq1,\ x,y>0",
                     font_size=27, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 12.4)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r3), run_time=2.0)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(3.0)
        self.play(Write(r4), run_time=2.1)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.2)
        self.wait(3.0)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q36 - TRIG 6-8: SINE, COSINE, AREA", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        t = Triangle(color=T.graph_function, stroke_width=3)
        t.scale(1.25).move_to(DOWN * 1.0 + LEFT * 3.2)
        A, B, C = t.get_vertices()
        labA = MathTex(r"A", font_size=28, color=T.text_primary).next_to(A, UL, buff=0.15)
        labB = MathTex(r"B", font_size=28, color=T.text_primary).next_to(B, DOWN, buff=0.12)
        labC = MathTex(r"C", font_size=28, color=T.text_primary).next_to(C, RIGHT, buff=0.15)
        sideA = MathTex(r"a", font_size=26, color=T.result_final)
        sideA.move_to((B + C) / 2 + DOWN * 0.22)
        sideB = MathTex(r"b", font_size=26, color=T.result_final)
        sideB.move_to((A + C) / 2 + RIGHT * 0.22)
        sideC = MathTex(r"c", font_size=26, color=T.result_final)
        sideC.move_to((A + B) / 2 + UP * 0.30)
        alt = DashedLine(C, (C[0], A[1], 0), color=T.cancel_mark,
                         stroke_width=2)
        hlab = MathTex(r"h", font_size=24, color=T.cancel_mark)
        hlab.move_to(((C[0] + A[0]) / 2, (C[1] + A[1]) / 2, 0) + RIGHT * 0.18)
        tri = VGroup(t, labA, labB, labC, sideA, sideB, sideC, alt, hlab)
        r1 = MathTex(r"\text{area: }K=\frac{1}{2}ch=\frac{1}{2}cb\sin A",
                     font_size=28, color=T.result_intermediate)
        r2 = MathTex(r"K=\frac{1}{2}bc\sin A=\frac{1}{2}ca\sin B"
                     r"=\frac{1}{2}ab\sin C", font_size=28,
                     color=T.text_primary)
        r3 = MathTex(r"\text{divide by }\frac{1}{2}abc:\ "
                     r"\frac{\sin A}{a}=\frac{\sin B}{b}"
                     r"=\frac{\sin C}{c}", font_size=28,
                     color=T.result_final)
        r4 = MathTex(r"\text{cosine: }a^{2}=b^{2}+c^{2}-2bc\cos A",
                     font_size=29, color=T.result_final)
        r5 = Text("proof of cosine rule: drop altitude from C onto AB: "
                  "a^2 = (c - b cos A)^2 + (b sin A)^2.", font_size=21,
                  color=T.text_secondary)
        r6 = MathTex(r"=c^{2}-2bc\cos A+b^{2}(\cos^{2}A+\sin^{2}A)"
                     r"=b^{2}+c^{2}-2bc\cos A", font_size=27,
                     color=T.text_primary)
        right = VGroup(r1, r2, r3, r4, r5, r6).arrange(DOWN,
                                                        aligned_edge=LEFT,
                                                        buff=0.26)
        fit_width(right, 7.1)
        right.next_to(t, RIGHT, buff=0.45).align_to(t, UP)
        if right.height > 5.6:
            right.scale_to_fit_height(5.6)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        self.play(Create(t), run_time=1.4)
        self.play(FadeIn(labA), FadeIn(labB), FadeIn(labC), run_time=0.9)
        self.play(FadeIn(sideA), FadeIn(sideB), FadeIn(sideC),
                  Create(alt), run_time=1.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.9)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.8)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        self.wait(2.6)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.3)
        self.wait(2.8)
        self.play(Write(r6), run_time=2.0)
        self.wait(3.4)
        self.wait(6)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q36 - TRIG 9-10: DOUBLE ANGLE + PRODUCT-TO-SUM",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{compound: }\sin(A+B)=\sin A\cos B"
                     r"+\cos A\sin B", font_size=29,
                     color=T.text_primary)
        r2 = MathTex(r"\text{take }A=B=\theta:\ \sin 2\theta=2\sin\theta"
                     r"\cos\theta", font_size=29, color=T.result_final)
        r3 = MathTex(r"\cos(A+B)=\cos A\cos B-\sin A\sin B\ "
                     r"\Rightarrow\ \cos 2\theta=\cos^{2}\theta"
                     r"-\sin^{2}\theta", font_size=27,
                     color=T.result_final)
        r4 = MathTex(r"\sin(A+B)+\sin(A-B)=2\sin A\cos B", font_size=30,
                     color=T.result_intermediate)
        r5 = MathTex(r"\text{so }2\sin A\cos B=\sin(A+B)+\sin(A-B)",
                     font_size=30, color=T.result_final)
        r6 = Text("step: expand both sum formulas and cancel the "
                  "opposite-sign terms.", font_size=22,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.34)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.7)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=2.0)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(3.0)
        self.play(Write(r4), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r5), run_time=1.8)
        box5 = SurroundingRectangle(r5, buff=0.12, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(FadeIn(r6, shift=0.2 * UP), run_time=1.2)
        self.wait(3.0)
        self.wait(6)
'''

SEG5 = r'''from manim import *


class Segment5(Scene):
    def construct(self):
        head = Text("Q36 - COORD 11-13: DISTANCE, SECTION, CIRCLE",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        axes = Axes(x_range=[-1, 6, 1], y_range=[-1, 4, 1],
                    x_length=5.2, y_length=3.6,
                    axis_config={"color": T.grid, "stroke_width": 2})
        axes.move_to(DOWN * 0.7 + LEFT * 3.6)
        P = axes.c2p(1, 1)
        Q = axes.c2p(5, 3)
        pdot = Dot(P, radius=0.06, color=T.result_final)
        qdot = Dot(Q, radius=0.06, color=T.result_final)
        pL = MathTex(r"P(x_1,y_1)", font_size=22, color=T.result_final).next_to(P, DL, buff=0.1)
        qL = MathTex(r"Q(x_2,y_2)", font_size=22, color=T.result_final).next_to(Q, UR, buff=0.1)
        dy = DashedLine(P, (P[0], Q[1], 0), color=T.cancel_mark, stroke_width=2)
        dx = DashedLine((P[0], Q[1], 0), Q, color=T.cancel_mark, stroke_width=2)
        hyp = Line(P, Q, color=T.highlight_primary, stroke_width=3)
        dL = MathTex(r"d", font_size=26, color=T.highlight_primary).move_to((P + Q) / 2 + UP * 0.25)
        r1 = MathTex(r"d^{2}=(x_2-x_1)^{2}+(y_2-y_1)^{2}", font_size=27,
                     color=T.result_intermediate)
        r2 = MathTex(r"\Rightarrow d=\sqrt{(x_2-x_1)^{2}+(y_2-y_1)^{2}}",
                     font_size=28, color=T.result_final)
        r3 = MathTex(r"P=\left(\frac{mx_2+nx_1}{m+n},"
                     r"\frac{my_2+ny_1}{m+n}\right)", font_size=28,
                     color=T.result_final)
        r4 = Text("section: x-coordinate is the weighted mean of the "
                  "endpoints with weights n and m.", font_size=21,
                  color=T.text_secondary)
        r5 = MathTex(r"(x-h)^{2}+(y-k)^{2}=r^{2}", font_size=31,
                     color=T.result_final)
        r6 = MathTex(r"\text{circle = points at distance }r\ \text{from }"
                     r"(h,k)", font_size=26, color=T.text_secondary)
        right = VGroup(r1, r2, r3, r4, r5, r6).arrange(DOWN,
                                                        aligned_edge=LEFT,
                                                        buff=0.26)
        fit_width(right, 6.6)
        right.next_to(axes, RIGHT, buff=0.45).align_to(axes, UP)
        if right.height > 5.6:
            right.scale_to_fit_height(5.6)
        self.play(Create(axes), run_time=1.2)
        self.play(FadeIn(pdot), FadeIn(qdot), run_time=0.8)
        self.play(FadeIn(pL), FadeIn(qL), run_time=0.8)
        self.play(Create(dx), Create(dy), Create(hyp), run_time=1.1)
        self.play(Write(dL), run_time=0.6)
        self.play(Write(r1), run_time=1.6)
        self.play(Write(r2), run_time=1.7)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.9)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.6)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.2)
        self.wait(2.4)
        self.play(Write(r5), run_time=1.7)
        box5 = SurroundingRectangle(r5, buff=0.12, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        self.wait(2.4)
        self.play(FadeIn(r6, shift=0.2 * UP), run_time=1.1)
        self.wait(2.8)
        self.wait(6)
'''

SEG6 = r'''from manim import *


class Segment6(Scene):
    def construct(self):
        head = Text("Q36 - COORD 14-15: PARABOLA + ELLIPSE", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        # parabola diagram
        ax1 = Axes(x_range=[-2, 5, 1], y_range=[-3.4, 3.4, 1],
                   x_length=4.6, y_length=4.4,
                   axis_config={"color": T.grid, "stroke_width": 2})
        ax1.move_to(DOWN * 0.9 + LEFT * 4.4)
        para = ParametricFunction(
            lambda t: ax1.c2p(t * t / 4.0, t), t_range=[-3.2, 3.2],
            color=T.result_final, stroke_width=3)
        fx = Dot(ax1.c2p(1.0, 0.0), radius=0.06, color=T.cancel_mark)
        fL = MathTex(r"\text{focus }(a,0)", font_size=20,
                     color=T.cancel_mark).next_to(fx, DOWN, buff=0.1)
        dirx = DashedLine(ax1.c2p(-1, -3.2), ax1.c2p(-1, 3.2),
                          color=T.cancel_mark, stroke_width=2)
        dL = MathTex(r"x=-a", font_size=20, color=T.cancel_mark).next_to(dirx, UP, buff=0.08)
        o1 = Dot(ax1.c2p(0, 0), radius=0.05, color=T.text_primary)
        o1L = MathTex(r"O", font_size=20, color=T.text_primary).next_to(o1, DL, buff=0.08)
        p1 = para.point_from_proportion(0.72)
        pdot1 = Dot(p1, radius=0.06, color=T.highlight_primary)
        segF = Line(fx.get_center(), p1, color=T.highlight_secondary, stroke_width=2)
        segD = Line(p1, (ax1.c2p(-1, 0)[0], p1[1], 0), color=T.highlight_secondary,
                    stroke_width=2)
        pL1 = MathTex(r"P(x,y)", font_size=20, color=T.highlight_primary).next_to(p1, UR, buff=0.1)
        r1 = MathTex(r"PF=PD:\quad\sqrt{(x-a)^{2}+y^{2}}=|x+a|",
                     font_size=25, color=T.text_primary)
        r2 = MathTex(r"(x-a)^{2}+y^{2}=(x+a)^{2}\ \Rightarrow\ "
                     r"y^{2}=4ax", font_size=26, color=T.result_final)
        # ellipse diagram
        ax2 = Axes(x_range=[-3, 3, 1], y_range=[-2, 2, 1],
                   x_length=4.4, y_length=3.0,
                   axis_config={"color": T.grid, "stroke_width": 2})
        ax2.move_to(DOWN * 0.9 + RIGHT * 4.4)
        ell = Ellipse(width=4.2, height=2.5, color=T.result_final,
                      stroke_width=3).move_to(ax2.c2p(0, 0))
        c = 1.687
        f1 = Dot(ax2.c2p(-c, 0), radius=0.06, color=T.cancel_mark)
        f2 = Dot(ax2.c2p(c, 0), radius=0.06, color=T.cancel_mark)
        fL1 = MathTex(r"F_1(-c,0)", font_size=20, color=T.cancel_mark).next_to(f1, DOWN, buff=0.1)
        fL2 = MathTex(r"F_2(c,0)", font_size=20, color=T.cancel_mark).next_to(f2, DOWN, buff=0.1)
        p2 = ell.point_at_angle(PI / 3)
        pdot2 = Dot(p2, radius=0.06, color=T.highlight_primary)
        s1 = Line(f1.get_center(), p2, color=T.highlight_secondary, stroke_width=2)
        s2 = Line(f2.get_center(), p2, color=T.highlight_secondary, stroke_width=2)
        pL2 = MathTex(r"P", font_size=22, color=T.highlight_primary).next_to(p2, UR, buff=0.1)
        r3 = MathTex(r"PF_1+PF_2=2a", font_size=27,
                     color=T.text_primary)
        r4 = MathTex(r"\frac{x^{2}}{a^{2}}+\frac{y^{2}}{b^{2}}=1,\quad "
                     r"b^{2}=a^{2}-c^{2}", font_size=26,
                     color=T.result_final)
        labL = MathTex(r"b", font_size=22, color=T.text_secondary).move_to(ax2.c2p(0.25, 1.25))
        labL2 = MathTex(r"a", font_size=22, color=T.text_secondary).move_to(ax2.c2p(1.25, 0.25))
        r5 = Text("ellipse: sum of distances to the two foci is constant "
                  "2a (string construction).", font_size=20,
                  color=T.text_secondary)
        bot = VGroup(r3, r4, r5).arrange(DOWN, aligned_edge=LEFT, buff=0.20)
        fit_width(bot, 4.0)
        bot.next_to(ax2, DOWN, buff=0.18).align_to(ax2, LEFT)
        self.play(Create(ax1), run_time=1.0)
        self.play(Create(para), run_time=1.4)
        self.play(FadeIn(fx), Write(fL), Create(dirx), Write(dL), run_time=1.0)
        self.play(FadeIn(o1), Write(o1L), run_time=0.7)
        self.play(FadeIn(pdot1), Create(segF), Create(segD), Write(pL1), run_time=1.0)
        self.play(Write(r1), run_time=1.8)
        self.play(Write(r2), run_time=1.7)
        box2 = SurroundingRectangle(r2, buff=0.10, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(3.0)
        self.play(Create(ax2), run_time=1.0)
        self.play(Create(ell), run_time=1.3)
        self.play(FadeIn(f1), FadeIn(f2), Write(fL1), Write(fL2), Write(labL),
                  Write(labL2), run_time=1.0)
        self.play(FadeIn(pdot2), Create(s1), Create(s2), Write(pL2), run_time=1.0)
        self.play(Write(r3), run_time=1.6)
        self.play(Write(r4), run_time=1.7)
        box4 = SurroundingRectangle(r4, buff=0.10, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        self.play(FadeIn(r5, shift=0.1 * UP), run_time=1.1)
        self.wait(3.4)
        self.wait(6)
'''

SEG7 = r'''from manim import *


class Segment7(Scene):
    def construct(self):
        head = Text("Q36 - CALC 16-19: DERIVATIVE RULES", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\frac{d}{dx}x^{n}=\lim_{h\to0}\frac{(x+h)^{n}-x^{n}}{h}",
                     font_size=27, color=T.text_primary)
        r2 = MathTex(r"=\lim_{h\to0}\frac{nx^{n-1}h+\binom{n}{2}"
                     r"x^{n-2}h^{2}+\cdots+h^{n}}{h}=nx^{n-1}", font_size=25,
                     color=T.result_final)
        r3 = MathTex(r"\text{product: }(uv)'=\lim_{h\to0}\frac{u(x+h)"
                     r"v(x+h)-u(x)v(x)}{h}", font_size=25,
                     color=T.text_primary)
        r4 = MathTex(r"=u'v+uv'", font_size=30, color=T.result_final)
        r5 = MathTex(r"\text{quotient: }\left(\frac{u}{v}\right)'="
                     r"\frac{u'v-uv'}{v^{2}}", font_size=27,
                     color=T.result_final)
        r6 = MathTex(r"\text{chain: }\frac{dy}{dx}=\frac{dy}{du}"
                     r"\frac{du}{dx}", font_size=31, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.26)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.32)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r2), run_time=2.1)
        box2 = SurroundingRectangle(r2, buff=0.10, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(3.0)
        self.play(Write(r3), run_time=2.0)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.4)
        box4 = SurroundingRectangle(r4, buff=0.10, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        self.wait(2.4)
        self.play(Write(r5), run_time=1.8)
        box5 = SurroundingRectangle(r5, buff=0.10, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r6), run_time=1.6)
        box6 = SurroundingRectangle(r6, buff=0.10, color=T.result_final)
        self.play(Create(box6), run_time=0.7)
        emphasize(self, r6, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.wait(6)
'''

SEG8 = r'''from manim import *


class Segment8(Scene):
    def construct(self):
        head = Text("Q36 - CALC 20: DERIVATIVES OF sin AND cos",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\frac{d}{dx}\sin x=\lim_{h\to0}\frac{\sin(x+h)-\sin x}{h}",
                     font_size=27, color=T.text_primary)
        r2 = MathTex(r"=\sin x\lim\frac{\cos h-1}{h}+\cos x\lim\frac{\sin h}{h}",
                     font_size=27, color=T.text_primary)
        r3 = MathTex(r"\lim_{h\to0}\frac{\sin h}{h}=1,\qquad "
                     r"\lim_{h\to0}\frac{\cos h-1}{h}=0", font_size=28,
                     color=T.result_intermediate)
        r4 = MathTex(r"\frac{d}{dx}\sin x=\cos x", font_size=32,
                     color=T.result_final)
        r5 = MathTex(r"\frac{d}{dx}\cos x=\lim_{h\to0}\frac{\cos(x+h)-\cos x}{h}"
                     r"=-\sin x", font_size=27, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.38)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r2), run_time=2.1)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.8)
        self.wait(2.8)
        self.play(Write(r4), run_time=1.7)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r5), run_time=2.0)
        box5 = SurroundingRectangle(r5, buff=0.12, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        self.wait(3.6)
        self.wait(6)
'''

SEG9 = r'''from manim import *


class Segment9(Scene):
    def construct(self):
        head = Text("Q36 - CALC 21-23: PARTS, POWER INTEGRAL, FTC",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"(uv)'=u'v+uv'\ \Rightarrow\ uv=\int u\,dv+\int v\,du",
                     font_size=28, color=T.text_primary)
        r2 = MathTex(r"\int u\,dv=uv-\int v\,du", font_size=32,
                     color=T.result_final)
        r3 = MathTex(r"\int x^{n}\,dx=\frac{x^{n+1}}{n+1}+C\ \ (n\neq-1)",
                     font_size=31, color=T.result_final)
        r4 = MathTex(r"\text{check: }\frac{d}{dx}\frac{x^{n+1}}{n+1}=x^{n}",
                     font_size=28, color=T.text_primary)
        r5 = MathTex(r"\text{FTC: }\int_a^{b}f(x)\,dx=F(b)-F(a),\quad F'=f",
                     font_size=29, color=T.result_final)
        r6 = Text("FTC: the signed area under f from a to b equals the "
                  "net change of any antiderivative F.", font_size=21,
                  color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.34)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.7)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.8)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.6)
        self.wait(2.4)
        self.play(Write(r5), run_time=1.9)
        box5 = SurroundingRectangle(r5, buff=0.12, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=0.9)
        self.wait(3.0)
        self.play(FadeIn(r6, shift=0.2 * UP), run_time=1.2)
        self.wait(3.2)
        self.wait(6)
'''

SEG10 = r'''from manim import *


class Segment10(Scene):
    def construct(self):
        head = Text("Q36 - CALC 24: VOLUME OF REVOLUTION (DISKS)",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        ax = Axes(x_range=[0, 4, 1], y_range=[0, 3, 1],
                  x_length=6.2, y_length=3.4,
                  axis_config={"color": T.grid, "stroke_width": 2})
        ax.move_to(DOWN * 0.9 + LEFT * 3.3)
        fx = ax.plot(lambda x: 1.0 + 0.5 * x, color=T.result_final,
                     stroke_width=3)
        x0 = 2.0
        disc = Ellipse(width=0.7, height=0.35, color=T.result_intermediate,
                       stroke_width=3)
        disc.move_to(ax.c2p(x0, 0))
        up = Line(ax.c2p(x0, 0), ax.c2p(x0, 2.0), color=T.highlight_secondary,
                  stroke_width=2.5)
        upL = MathTex(r"f(x)", font_size=24, color=T.highlight_secondary).next_to(up, RIGHT, buff=0.12)
        xL = MathTex(r"x", font_size=22, color=T.text_secondary).next_to(ax.c2p(x0, 0), DOWN, buff=0.1)
        dxL = MathTex(r"dx", font_size=22, color=T.text_secondary).move_to(ax.c2p(2.45, -0.35))
        r1 = MathTex(r"dV=\pi f(x)^{2}\,dx", font_size=29,
                     color=T.result_intermediate)
        r2 = MathTex(r"V=\pi\int_a^{b}[f(x)]^{2}\,dx", font_size=32,
                     color=T.result_final)
        r3 = Text("disk method: a slice at x is a disk of radius f(x) "
                  "and thickness dx, so its volume is the area of a "
                  "circle times dx.", font_size=20, color=T.text_secondary)
        right = VGroup(r1, r2, r3).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        fit_width(right, 5.4)
        right.next_to(ax, RIGHT, buff=0.4).align_to(ax, UP)
        if right.height > 4.6:
            right.scale_to_fit_height(4.6)
        self.play(Create(ax), run_time=1.2)
        self.play(Create(fx), run_time=1.5)
        self.play(Create(up), FadeIn(disc), Write(upL), Write(xL), Write(dxL),
                  run_time=1.2)
        self.play(Write(r1), run_time=1.6)
        self.wait(2.6)
        self.play(Write(r2), run_time=1.8)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        emphasize(self, r2, color=T.result_final, run_time=0.9)
        self.wait(3.0)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.3)
        self.wait(3.4)
        self.wait(6)
'''

SEG11 = r'''from manim import *


class Segment11(Scene):
    def construct(self):
        head = Text("Q36 - VECTORS 25-27: DOT, CROSS, PLANE", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        O = DOWN * 1.2 + LEFT * 4.6
        a_end = O + UP * 2.4 + RIGHT * 1.2
        b_end = O + RIGHT * 3.0
        a_vec = Arrow(O, a_end, buff=0, color=T.result_final, stroke_width=4)
        b_vec = Arrow(O, b_end, buff=0, color=T.highlight_primary, stroke_width=4)
        aL = MathTex(r"\vec a", font_size=27, color=T.result_final).next_to(a_end, UP, buff=0.1)
        bL = MathTex(r"\vec b", font_size=27, color=T.highlight_primary).next_to(b_end, DOWN, buff=0.1)
        th = MathTex(r"\theta", font_size=26, color=T.text_primary).move_to(O + RIGHT * 0.75 + UP * 0.5)
        r1 = MathTex(r"|\vec a-\vec b|^{2}=|\vec a|^{2}+|\vec b|^{2}"
                     r"-2|\vec a||\vec b|\cos\theta", font_size=25,
                     color=T.text_primary)
        r2 = MathTex(r"\text{also }|\vec a-\vec b|^{2}=|\vec a|^{2}"
                     r"+|\vec b|^{2}-2\vec a\cdot\vec b", font_size=25,
                     color=T.text_primary)
        r3 = MathTex(r"\vec a\cdot\vec b=|\vec a||\vec b|\cos\theta",
                     font_size=29, color=T.result_final)
        r4 = MathTex(r"|\vec a\times\vec b|=|\vec a||\vec b|\sin\theta",
                     font_size=29, color=T.result_final)
        r5 = MathTex(r"\text{plane: }ax+by+cz+d=0", font_size=31,
                     color=T.result_final)
        r6 = MathTex(r"\vec n=(a,b,c)\ \text{normal};\quad "
                     r"\vec n\cdot(\vec r-\vec r_0)=0", font_size=28,
                     color=T.text_primary)
        right = VGroup(r1, r2, r3, r4, r5, r6).arrange(DOWN,
                                                        aligned_edge=LEFT,
                                                        buff=0.24)
        fit_width(right, 7.2)
        right.next_to(O, RIGHT, buff=1.1).align_to(O, UP)
        if right.height > 5.6:
            right.scale_to_fit_height(5.6)
        self.play(Create(a_vec), Create(b_vec), run_time=1.2)
        self.play(Write(aL), Write(bL), Write(th), run_time=0.9)
        self.play(Write(r1), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r2), run_time=1.9)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.7)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.7)
        box4 = SurroundingRectangle(r4, buff=0.12, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        self.wait(2.6)
        self.play(Write(r5), run_time=1.7)
        box5 = SurroundingRectangle(r5, buff=0.12, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        self.wait(2.6)
        self.play(Write(r6), run_time=1.8)
        self.wait(3.2)
        self.wait(6)
'''

SEG12 = r'''from manim import *


class Segment12(Scene):
    def construct(self):
        head = Text("Q36 - PROB/GEOM 28-30: BAYES, EULER, HERON",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"P(A|B)=\frac{P(A\cap B)}{P(B)},\quad "
                     r"P(B|A)=\frac{P(A\cap B)}{P(A)}", font_size=27,
                     color=T.text_primary)
        r2 = MathTex(r"\Rightarrow P(A\cap B)=P(B|A)P(A)", font_size=29,
                     color=T.result_intermediate)
        r3 = MathTex(r"P(A|B)=\frac{P(B|A)P(A)}{P(B)}", font_size=32,
                     color=T.result_final)
        r4 = MathTex(r"\text{cube: }V-E+F=8-12+6=2", font_size=28,
                     color=T.text_primary)
        r5 = MathTex(r"\text{tetrahedron: }V-E+F=4-6+4=2", font_size=28,
                     color=T.text_primary)
        r6 = MathTex(r"\text{Heron: }A=\sqrt{s(s-a)(s-b)(s-c)},\ "
                     r"s=\frac{a+b+c}{2}", font_size=28,
                     color=T.result_final)
        r7 = Text("Heron: from A = (1/2)bc sin A and cos A = "
                  "(b^2+c^2-a^2)/2bc; the sine squared factor becomes "
                  "the four s-terms.", font_size=20, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5, r6, r7)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.32)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=2.0)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.6)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.7)
        box3 = SurroundingRectangle(r3, buff=0.12, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r4), run_time=1.6)
        self.wait(2.4)
        self.play(Write(r5), run_time=1.6)
        self.wait(2.4)
        self.play(Write(r6), run_time=1.9)
        box6 = SurroundingRectangle(r6, buff=0.12, color=T.result_final)
        self.play(Create(box6), run_time=0.7)
        self.wait(3.0)
        self.play(FadeIn(r7, shift=0.2 * UP), run_time=1.2)
        self.wait(3.2)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Algebra one: completing the square. Divide by a, add b over 2a "
     "squared to both sides, the left is a perfect square, the right "
     "becomes b squared minus 4ac over 4a squared. Square rooting gives "
     "the quadratic formula. Algebra two: the binomial theorem. "
     "Expanding (a plus b) to the n, the coefficient of a to the n "
     "minus r, b to the r, is the number of ways to choose r b-factors "
     "from n, which is n choose r. That is the whole theorem.",
     "visual": {"style": "algebra 1-2", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Algebra three: arithmetic progression. Add the sum to itself "
     "written backwards; each column adds to 2a plus (n minus 1)d, "
     "there are n columns, so twice S n equals n times that, giving S "
     "n equals n over 2, bracket 2a plus n minus 1 d. Algebra four: "
     "geometric progression. Multiply the sum by r, subtract, the "
     "middle terms cancel, leaving 1 minus r, S n equals a, 1 minus r "
     "to the n. For r less than 1 in magnitude, as n grows r to the n "
     "dies, so the infinite sum is a over 1 minus r.",
     "visual": {"style": "algebra 3-4", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Algebra five: logarithmic laws. A logarithm answers: what power "
     "of a gives x. So x equals a to the p means log base a of x is p. "
     "If y equals a to the q, then x y equals a to the p plus q, so "
     "its logarithm is p plus q: the log of a product is the sum of "
     "logs. Division works the same way: x over y equals a to the p "
     "minus q, so the log of a quotient is the difference. Assumptions: "
     "a positive, not 1, and x, y positive.",
     "visual": {"style": "algebra 5", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "Trigonometry. In triangle A B C with side a opposite angle A and "
     "so on, the area K is half the base c times the height h, and "
     "the height is b sine A, so K is half b c sine A. Using each side "
     "as base gives three expressions for the same area; dividing by "
     "half a b c yields the sine rule, sine A over a equals sine B "
     "over b equals sine C over c. For the cosine rule, drop the "
     "altitude from C to A B: the horizontal piece from A to the foot "
     "is b cos A, and the remaining piece is c minus b cos A, so a "
     "squared equals c minus b cos A squared plus b sin A squared, "
     "which expands to b squared plus c squared minus 2 b c cos A.",
     "visual": {"style": "trig triangle", "transition": "slide-up"},
     "code": SEG3},
    {"narration":
     "Compound-angle formulas give the double-angle identities by "
     "setting A equals B equals theta: sine 2 theta is 2 sine theta "
     "cos theta, and cosine 2 theta is cosine squared theta minus sine "
     "squared theta. Product-to-sum comes from adding the sine sum "
     "formulas: sine of A plus B plus sine of A minus B, the crossed "
     "terms cancel pairwise and leave twice sine A cos B.",
     "visual": {"style": "trig identities", "transition": "fade"},
     "code": SEG4},
    {"narration":
     "Coordinate geometry. The distance formula is Pythagoras in "
     "coordinates: the horizontal gap is x2 minus x1, the vertical gap "
     "y2 minus y1, and the distance is the square root of the sum of "
     "their squares. The section formula gives the point dividing a "
     "segment in ratio m to n as the weighted mean of the endpoints, "
     "with weights n and m. The circle equation restates the distance "
     "formula: every point at distance r from the centre h, k "
     "satisfies x minus h squared plus y minus k squared equals r "
     "squared.",
     "visual": {"style": "coordinate diagrams", "transition": "carry-over"},
     "code": SEG5},
    {"narration":
     "The parabola. By definition, a point P lies on the parabola when "
     "its distance to the focus a, 0 equals its distance to the "
     "directrix x equals minus a. Squaring both sides and expanding, "
     "the x squared terms cancel, leaving y squared equals 4 a x. The "
     "ellipse. A point P lies on the ellipse when the sum of distances "
     "to the two foci is the constant 2a. In coordinates this "
     "simplifies to x squared over a squared plus y squared over b "
     "squared equals 1, with b squared equal to a squared minus c "
     "squared.",
     "visual": {"style": "conics", "transition": "slide-up"},
     "code": SEG6},
    {"narration":
     "Differential calculus. Power rule from first principles: expand "
     "x plus h to the n with the binomial theorem, subtract x to the "
     "n, divide by h, and the limit leaves n x to the n minus 1. "
     "Product rule: write the difference quotient with u and v, add "
     "and subtract u of x plus h times v of x, split into two limits, "
     "and get u prime v plus u v prime. Quotient rule follows by "
     "applying the product rule to u times 1 over v. Chain rule: the "
     "differential of y with respect to x factors through u, the "
     "derivative of y with respect to u times the derivative of u with "
     "respect to x.",
     "visual": {"style": "rules", "transition": "carry-over"},
     "code": SEG7},
    {"narration":
     "Derivatives of sine and cosine. Write the difference quotient for "
     "sine of x plus h; split it using the compound-angle formula into "
     "sine x times the limit of cos h minus 1 over h, plus cos x times "
     "the limit of sine h over h. The first limit is 0, the second is "
     "1, so the derivative of sine is cosine. The same treatment gives "
     "the derivative of cosine as minus sine.",
     "visual": {"style": "trig limits", "transition": "fade"},
     "code": SEG8},
    {"narration":
     "Integration by parts is the product rule read backwards: "
     "integrate u v prime equals u v minus v u prime, which is the "
     "familiar u d v equals u v minus v d u. The power rule for "
     "integrals follows because differentiating x to the n plus 1 over "
     "n plus 1 returns x to the n. The fundamental theorem of calculus "
     "says the signed area under f from a to b equals the net change "
     "of any antiderivative, F of b minus F of a, which is why "
     "antiderivatives compute areas.",
     "visual": {"style": "integral calculus", "transition": "slide-up"},
     "code": SEG9},
    {"narration":
     "Volume of revolution by the disk method. Rotate the curve y "
     "equals f of x about the x-axis. A thin slice at x is a disk of "
     "radius f of x and thickness d x, so its volume is pi f of x "
     "squared d x. Adding the slices from a to b gives the integral V "
     "equals pi times the integral from a to b of f of x squared d x.",
     "visual": {"style": "revolution", "transition": "carry-over"},
     "code": SEG10},
    {"narration":
     "Vectors. The dot product emerges from the cosine rule applied to "
     "the triangle made by vectors a and b: the length of a minus b "
     "squared is a squared plus b squared minus 2 a b cos theta, but "
     "also a squared plus b squared minus 2 a dot b, so a dot b "
     "equals the product of the lengths times cos theta. The magnitude "
     "of the cross product is the area of the parallelogram spanned by "
     "the vectors, a b sin theta. A plane with normal vector n equals "
     "a, b, c has equation n dot r minus r zero equals zero, which "
     "expands to a x plus b y plus c z plus d equals zero.",
     "visual": {"style": "vectors", "transition": "fade"},
     "code": SEG11},
    {"narration":
     "Bayes' theorem: the definition of conditional probability gives "
     "P of A intersect B in two ways; equating them and solving for P "
     "of A given B gives P of B given A times P of A over P of B. "
     "Euler's polyhedron formula: for a cube, vertices minus edges "
     "plus faces is 8 minus 12 plus 6, which is 2; for a tetrahedron, "
     "4 minus 6 plus 4 is also 2. The formula holds for every convex "
     "polyhedron. Heron's formula: substitute the cosine rule into the "
     "area formula half b c sine A, square it, factor the difference of "
     "squares, and the expression collapses into s times s minus a "
     "times s minus b times s minus c, where s is the semiperimeter.",
     "visual": {"style": "probability-geometry", "transition": "slide-up"},
     "code": SEG12},
]

LECTURE = {
    "title": TITLE,
    "preset": "lab",
    "format": "mixed",
    "question": QUESTION,
    "question_code": QUESTION_CODE,
    "segments": SEGMENTS,
}
