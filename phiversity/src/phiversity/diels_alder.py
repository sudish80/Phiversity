TITLE = "Q1 - DIELS-ALDER: BUTADIENE + MALEIC ANHYDRIDE"

QUESTION = {
    "display":
        "1,3-butadiene + maleic anhydride, $\\Delta$, "
        "gives a [4+2] cycloaddition product. "
        "1. draw the final product; 2. curved-arrow mechanism; "
        "3. molecular orbital overlap; "
        "4. why [4+2]? 5. importance of s-cis; "
        "6. stereochemistry; 7. endo rule and major product; "
        "8. why concerted.",
    "speech":
        "Question one. Diels Alder reaction between one three butadiene and "
        "maleic anhydride under heating. Number one, draw the complete "
        "molecular structure of the final product. Number two, explain the "
        "reaction mechanism using curved arrows. Number three, draw the "
        "molecular orbital overlap diagram. Number four, explain why this is "
        "a four plus two cycloaddition. Number five, explain the importance "
        "of the s-cis conformation. Number six, determine the stereochemistry "
        "of the product. Number seven, explain the endo rule and predict the "
        "major product. Number eight, explain why the reaction is concerted.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 1 - DIELS-ALDER CYCLOADDITION", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"\text{1,3-butadiene + maleic anhydride, }\Delta \ "
            r"\Rightarrow\ \text{[4+2], concerted, endo}",
            font_size=27, color=T.constant)
        c_chem = Text("STRUCTURE", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "1  final product: cis-1,2-cyclohex-4-ene-\n"
            "   dicarboxylic anhydride (tetrahydrophthalic)\n"
            "6  stereochemistry: cis, meso",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("MECHANISM", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "2  three curved arrows, cyclic electron flow\n"
            "8  concerted - one transition state, no intermediates",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("WHY / HOW", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "3  HOMO (diene) + LUMO (dienophile) overlap\n"
            "4  [4+2]: 6 pi electrons = 4n+2, thermal\n"
            "5  s-cis conformation required\n"
            "7  endo rule: carbonyls under diene pi cloud",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, chem, maths, econ).arrange(DOWN, aligned_edge=LEFT,
                                                       buff=0.34)
        rows.move_to(UP * 0.2)
        fit_width(rows, 12.9)
        ring = RegularPolygon(6, start_angle=PI / 2, stroke_width=4,
                              color=T.graph_function)
        ring.scale(1.4)
        ring.move_to(DOWN * 2.6 + LEFT * 2.3)
        dbl = Line(ring.get_vertices()[0], ring.get_vertices()[1],
                   stroke_width=5, color=T.result_final)
        dbl.shift(RIGHT * 0.12)
        c1 = Dot(ring.get_vertices()[2], radius=0.06, color=T.variable)
        c2 = Dot(ring.get_vertices()[3], radius=0.06, color=T.variable)
        o = Dot(ring.get_vertices()[4], radius=0.06, color=T.warning)
        sketch = VGroup(ring, dbl, c1, c2, o)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=2.2)
        self.wait(6.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(9.0)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(10.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(10.0)
        self.play(Create(sketch), run_time=2.0)
        self.wait(8.0)
        self.play(FadeOut(sketch), run_time=0.6)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q1 (1) - THE PRODUCT STRUCTURE", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{product = }"
                     r"\mathrm{cis}\text{-1,2-cyclohex-4-ene-}"
                     r"\text{dicarboxylic anhydride}",
                     font_size=28, color=T.result_final)
        r2 = MathTex(r"\text{the diene gives carbons 1-4 of the new ring;}"
                     r"\ \text{the dienophile gives carbons 5-6}",
                     font_size=27, color=T.text_primary)
        r3 = MathTex(r"\text{two new }\sigma\text{-bonds: }"
                     r"\text{C1-C5 and C4-C6}",
                     font_size=27, color=T.text_primary)
        r4 = MathTex(r"\text{the C2=C3 double bond of the diene} "
                     r"\text{survives in the ring}",
                     font_size=27, color=T.text_primary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 8.2)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        cx, cy = 3.3, -1.0
        R = 1.7
        pts = []
        for k in range(6):
            ang = PI / 6 + k * PI / 3
            pts.append(np.array([cx + R * np.cos(ang), cy + R * np.sin(ang), 0]))
        ring = Polygon(*pts, color=T.text_primary, stroke_width=4)
        v0, v1 = pts[0], pts[1]
        perp = (v1 - v0) / np.linalg.norm(v1 - v0)
        perp = np.array([-perp[1], perp[0], 0]) * 0.22
        dbl1 = Line(v0, v1, color=T.result_final, stroke_width=5)
        dbl2 = Line(v0 + perp, v1 + perp, color=T.result_final, stroke_width=5)
        c1 = v0 + np.array([0.85, 0.55, 0])
        c2 = v1 + np.array([0.85, -0.55, 0])
        br1 = Line(v0, c1, color=T.text_primary, stroke_width=4)
        br2 = Line(v1, c2, color=T.text_primary, stroke_width=4)
        o = np.array([cx + 2.55, cy, 0])
        o1 = Line(c1, o, color=T.text_primary, stroke_width=4)
        o2 = Line(c2, o, color=T.text_primary, stroke_width=4)
        odbl = Line(c1 + np.array([0.12, 0.62, 0]),
                    c1 + np.array([0.12, 1.05, 0]),
                    color=T.warning, stroke_width=5)
        odbl2 = Line(c1 + np.array([0.22, 0.62, 0]),
                     c1 + np.array([0.22, 1.05, 0]),
                     color=T.warning, stroke_width=5)
        odbl3 = Line(c2 + np.array([0.12, -0.62, 0]),
                     c2 + np.array([0.12, -1.05, 0]),
                     color=T.warning, stroke_width=5)
        odbl4 = Line(c2 + np.array([0.22, -0.62, 0]),
                     c2 + np.array([0.22, -1.05, 0]),
                     color=T.warning, stroke_width=5)
        olab = Text("O", font_size=26, color=T.warning)
        olab.move_to(o + RIGHT * 0.55)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.82)
        self.play(Write(r2), run_time=1.4)
        self.wait(3.82)
        self.play(Write(r3), run_time=1.4)
        self.wait(3.82)
        self.play(Create(ring), run_time=1.2)
        self.play(Create(dbl1), Create(dbl2), run_time=0.8)
        self.play(Create(br1), Create(br2), Create(o1), Create(o2),
                  run_time=1.0)
        self.play(Create(odbl), Create(odbl2), Create(odbl3), Create(odbl4),
                  Write(olab), run_time=1.0)
        self.wait(2.97)
        self.play(Write(r4), run_time=1.4)
        self.wait(2.97)
        box = SurroundingRectangle(VGroup(r1), buff=0.13, color=T.result_final)
        self.play(Create(box), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(5.1)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q1 (2) - MECHANISM: CURVED ARROWS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{concerted: three curved arrows push }"
                     r"\text{simultaneously - one cyclic transition state}",
                     font_size=27, color=T.text_primary)
        r2 = MathTex(r"\text{no zwitterion, no diradical, no intermediates}",
                     font_size=27, color=T.text_secondary)
        rows = VGroup(r1, r2)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 9.0)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        A = np.array([0.0, 1.35, 0])
        B = np.array([1.35, 0.45, 0])
        C = np.array([0.95, -1.1, 0])
        D = np.array([-0.95, -1.1, 0])
        E = np.array([-1.35, 0.45, 0])
        F = np.array([0.0, 1.35, 0])
        P = np.array([0.55, 0.28, 0])
        d1 = Dot(A, radius=0.07, color=T.graph_point)
        d2 = Dot(B, radius=0.07, color=T.graph_point)
        d3 = Dot(C, radius=0.07, color=T.graph_point)
        d4 = Dot(D, radius=0.07, color=T.graph_point)
        d5 = Dot(E, radius=0.07, color=T.graph_point)
        l1 = Line(A, B, color=T.text_primary, stroke_width=4)
        l2 = Line(B, C, color=T.text_primary, stroke_width=4)
        l3 = Line(C, D, color=T.text_primary, stroke_width=4)
        l4 = Line(D, E, color=T.text_primary, stroke_width=4)
        l5 = Line(E, F, color=T.text_primary, stroke_width=4)
        a1 = CurvedArrow(B, E, angle=-2.2, color=T.warning, stroke_width=5)
        a2 = CurvedArrow(E, C, angle=-2.2, color=T.warning, stroke_width=5)
        a3 = CurvedArrow(C, B, angle=-2.2, color=T.warning, stroke_width=5)
        la = Text("C1", font_size=20, color=T.graph_point)
        la.move_to(A + UP * 0.35)
        lb = Text("C2", font_size=20, color=T.graph_point)
        lb.move_to(B + UP * 0.35 + RIGHT * 0.2)
        lc = Text("C3", font_size=20, color=T.graph_point)
        lc.move_to(C + DOWN * 0.35)
        ld = Text("C4", font_size=20, color=T.graph_point)
        ld.move_to(D + DOWN * 0.35)
        le = Text("Ca", font_size=20, color=T.graph_tangent)
        le.move_to(E + UP * 0.35 + LEFT * 0.2)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.99)
        self.play(Create(l1), Create(l2), Create(l3), Create(l4), Create(l5),
                  Create(d1), Create(d2), Create(d3), Create(d4), Create(d5),
                  run_time=1.6)
        self.wait(2.61)
        self.play(Create(a1), run_time=1.2)
        self.wait(2.24)
        self.play(Create(a2), run_time=1.2)
        self.wait(2.24)
        self.play(Create(a3), run_time=1.2)
        self.wait(2.24)
        self.play(Write(la), Write(lb), Write(lc), Write(ld), Write(le),
                  run_time=1.0)
        self.wait(2.24)
        self.play(Write(r2), run_time=1.2)
        self.wait(2.99)
        self.wait(4.48)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q1 (3) - MOLECULAR ORBITAL OVERLAP", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{normal demand: diene HOMO }\psi_2"
                     r"\ \text{+ dienophile LUMO }\pi^{*}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"\text{in-phase overlap at both termini: }"
                     r"\text{C1 leftrightarrow Ca and C4 leftrightarrow Cb}",
                     font_size=27, color=T.result_intermediate)
        rows = VGroup(r1, r2)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 10.2)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        yL = 0.4
        xs = [-4.1, -2.7, -1.3, 0.1]
        lobes = VGroup()
        for x in xs:
            up = Ellipse(width=0.5, height=0.95, color=T.graph_function,
                         fill_color=T.graph_function, fill_opacity=0.55)
            up.move_to([x, yL + 0.48, 0])
            dn = Ellipse(width=0.5, height=0.95, color=T.graph_function,
                         stroke_width=2)
            dn.move_to([x, yL - 0.48, 0])
            lobes.add(up, dn)
        lineL = Line([xs[0] - 0.9, yL, 0], [xs[-1] + 0.9, yL, 0],
                     color=T.text_muted, stroke_width=2)
        plus = VGroup(*[MathTex(r"+", font_size=24, color=T.graph_function)
                        for _ in range(2)])
        minus = VGroup(*[MathTex(r"-", font_size=24, color=T.graph_function)
                        for _ in range(2)])
        plus.arrange(RIGHT, buff=0.9).move_to([-3.4, yL + 1.15, 0])
        minus.arrange(RIGHT, buff=0.9).move_to([-0.6, yL + 1.15, 0])
        labH = Text("HOMO psi2 (diene)", font_size=22, color=T.graph_function)
        labH.move_to([-2.0, yL - 1.55, 0])
        xR = 2.9
        upR = Ellipse(width=0.5, height=0.95, color=T.graph_tangent,
                      fill_color=T.graph_tangent, fill_opacity=0.55)
        upR.move_to([xR, yL + 0.48, 0])
        dnR = Ellipse(width=0.5, height=0.95, color=T.graph_tangent,
                      stroke_width=2)
        dnR.move_to([xR, yL - 0.48, 0])
        upR2 = Ellipse(width=0.5, height=0.95, color=T.graph_tangent,
                       stroke_width=2)
        upR2.move_to([xR + 1.4, yL + 0.48, 0])
        dnR2 = Ellipse(width=0.5, height=0.95, color=T.graph_tangent,
                       fill_color=T.graph_tangent, fill_opacity=0.55)
        dnR2.move_to([xR + 1.4, yL - 0.48, 0])
        lineR = Line([xR - 0.9, yL, 0], [xR + 2.3, yL, 0],
                     color=T.text_muted, stroke_width=2)
        labL = Text("LUMO pi* (dienophile)", font_size=22,
                    color=T.graph_tangent)
        labL.move_to([xR + 0.7, yL - 1.55, 0])
        dash1 = DashedLine([xs[0], yL + 0.48, 0], [xR, yL + 0.48, 0],
                           color=T.result_final, stroke_width=3)
        dash2 = DashedLine([xs[-1], yL - 0.48, 0],
                           [xR + 1.4, yL - 0.48, 0],
                           color=T.result_final, stroke_width=3)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.83)
        self.play(Create(lineL), FadeIn(lobes), run_time=1.6)
        self.wait(2.2)
        self.play(Write(plus), Write(minus), Write(labH), run_time=1.2)
        self.wait(2.2)
        self.play(Create(lineR), FadeIn(upR), FadeIn(dnR), FadeIn(upR2),
                  FadeIn(dnR2), Write(labL), run_time=1.6)
        self.wait(2.2)
        self.play(Create(dash1), Create(dash2), run_time=1.2)
        self.wait(2.2)
        self.play(Write(r2), run_time=1.4)
        self.wait(2.2)
        self.wait(3.77)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q1 (4) - WHY [4+2] CYCLOADDITION", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{diene supplies }4\pi\ \text{electrons}"
                     r"\ (2\ \text{double bonds})",
                     font_size=29, color=T.variable)
        r2 = MathTex(r"\text{dienophile supplies }2\pi\ \text{electrons}"
                     r"\ (1\ \text{double bond})",
                     font_size=29, color=T.variable)
        r3 = MathTex(r"\text{total: }6\ \text{electrons} = 4n+2,"
                     r"\ n=1\ \text{(aromatic transition state)}",
                     font_size=29, color=T.result_intermediate)
        r4 = MathTex(r"\text{Woodward-Hoffmann: thermally allowed,}"
                     r"\ \text{suprafacial / suprafacial}",
                     font_size=29, color=T.result_final)
        r5 = MathTex(r"[2+2]\ \text{would need light (photochemical)}",
                     font_size=27, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 10.5)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.78)
        self.play(Write(r2), run_time=1.4)
        self.wait(2.78)
        self.play(Write(r3), run_time=1.8)
        self.wait(2.78)
        self.play(Write(r4), run_time=1.8)
        box4 = SurroundingRectangle(r4, buff=0.13, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        emphasize(self, r4, color=T.result_final, run_time=0.9)
        self.wait(2.78)
        self.play(Write(r5), run_time=1.2)
        self.wait(2.44)
        self.wait(4.18)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q1 (5) - THE s-CIS CONFORMATION", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{only s-cis puts both termini close enough"
                     r"\ \text{to bond simultaneously}",
                     font_size=28, color=T.result_final)
        r2 = MathTex(r"\text{s-trans: termini point away - no reaction}",
                     font_size=27, color=T.text_secondary)
        r3 = MathTex(r"\text{rotation about C2-C3 needs small energy;}"
                     r"\ \text{heating supplies it}",
                     font_size=27, color=T.text_primary)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 9.5)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        A = np.array([-1.7, 0.55, 0])
        B = np.array([-0.75, -0.05, 0])
        C = np.array([0.75, -0.05, 0])
        D = np.array([1.7, 0.55, 0])
        perp = np.array([0, -0.22, 0])
        l1 = Line(A, B, color=T.text_primary, stroke_width=4)
        l1b = Line(A + perp, B + perp, color=T.text_primary, stroke_width=4)
        l2 = Line(B, C, color=T.text_primary, stroke_width=3)
        l3 = Line(C, D, color=T.text_primary, stroke_width=4)
        l3b = Line(C + perp, D + perp, color=T.text_primary, stroke_width=4)
        cis = VGroup(l1, l1b, l2, l3, l3b)
        cis.move_to(LEFT * 4.6 + DOWN * 1.35)
        lab_cis = Text("s-cis (reactive)", font_size=22, color=T.result_final)
        lab_cis.next_to(cis, DOWN, buff=0.35)
        A2 = np.array([-1.7, 0.7, 0])
        B2 = np.array([-0.75, 0.1, 0])
        C2 = np.array([0.75, -0.1, 0])
        D2 = np.array([1.7, -0.7, 0])
        l4 = Line(A2, B2, color=T.text_primary, stroke_width=4)
        l4b = Line(A2 + perp * 0.6, B2 + perp * 0.6,
                   color=T.text_primary, stroke_width=4)
        l5 = Line(B2, C2, color=T.text_primary, stroke_width=3)
        l6 = Line(C2, D2, color=T.text_primary, stroke_width=4)
        l6b = Line(C2 + perp * 0.6, D2 + perp * 0.6,
                   color=T.text_primary, stroke_width=4)
        trans = VGroup(l4, l4b, l5, l6, l6b)
        trans.move_to(RIGHT * 4.6 + DOWN * 1.35)
        lab_trans = Text("s-trans (unreactive)", font_size=22,
                         color=T.text_secondary)
        lab_trans.next_to(trans, DOWN, buff=0.35)
        rot = CurvedArrow(LEFT * 1.4 + UP * 1.35, RIGHT * 1.4 + UP * 1.35,
                          angle=-1.6, color=T.warning, stroke_width=5)
        rotlab = Text("rotate about C2-C3", font_size=20, color=T.warning)
        rotlab.next_to(rot, UP, buff=0.2)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.14)
        self.play(Create(l1), Create(l1b), Create(l2), Create(l3), Create(l3b),
                  Write(lab_cis), run_time=1.6)
        self.wait(2.79)
        self.play(Create(l4), Create(l4b), Create(l5), Create(l6), Create(l6b),
                  Write(lab_trans), run_time=1.6)
        self.wait(2.79)
        self.play(Create(rot), Write(rotlab), run_time=1.2)
        self.wait(2.44)
        self.play(Write(r2), run_time=1.2)
        self.wait(2.44)
        self.play(Write(r3), run_time=1.4)
        self.wait(2.44)
        self.wait(4.19)
'''

SEG5 = r'''from manim import *


class Segment5(Scene):
    def construct(self):
        head = Text("Q1 (6) - STEREOCHEMISTRY OF THE PRODUCT", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{stereospecific: cis dienophile }"
                     r"\Rightarrow\ \text{both bonds on the same face}",
                     font_size=28, color=T.text_primary)
        r2 = MathTex(r"\text{anhydride is cis on the ring}",
                     font_size=27, color=T.result_intermediate)
        r3 = MathTex(r"\text{product is meso: internal mirror plane,}"
                     r"\ \text{two equivalent stereocenters}",
                     font_size=27, color=T.result_final)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 10.0)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        cx, cy = 3.2, -1.3
        R = 1.6
        pts = []
        for k in range(6):
            ang = PI / 6 + k * PI / 3
            pts.append(np.array([cx + R * np.cos(ang), cy + R * np.sin(ang), 0]))
        ring = Polygon(*pts, color=T.text_primary, stroke_width=4)
        v0, v1 = pts[0], pts[1]
        perp = (v1 - v0) / np.linalg.norm(v1 - v0)
        perp = np.array([-perp[1], perp[0], 0]) * 0.22
        dbl1 = Line(v0, v1, color=T.result_final, stroke_width=5)
        dbl2 = Line(v0 + perp, v1 + perp, color=T.result_final, stroke_width=5)
        w1 = Polygon(v0, v0 + np.array([-0.3, 0.55, 0]),
                     v0 + np.array([0.3, 0.55, 0]),
                     fill_color=T.variable, fill_opacity=0.55,
                     stroke_width=2)
        w2 = Polygon(v1, v1 + np.array([-0.3, -0.55, 0]),
                     v1 + np.array([0.3, -0.55, 0]),
                     fill_color=T.variable, fill_opacity=0.55,
                     stroke_width=2)
        wlab = Text("wedges: same face (cis)", font_size=20,
                    color=T.variable)
        wlab.move_to(v0 + np.array([0.0, 1.25, 0]))
        mirr = DashedLine(pts[2], pts[5], color=T.graph_reference,
                          stroke_width=3)
        mlab = Text("mirror plane -> meso", font_size=20,
                    color=T.graph_reference)
        mlab.next_to(mirr, UP, buff=0.45)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.94)
        self.play(Create(ring), run_time=1.2)
        self.play(Create(dbl1), Create(dbl2), run_time=0.8)
        self.wait(2.29)
        self.play(FadeIn(w1), FadeIn(w2), Write(wlab), run_time=1.2)
        self.wait(2.29)
        self.play(Write(r2), run_time=1.2)
        self.wait(2.29)
        self.play(Create(mirr), Write(mlab), run_time=1.2)
        self.wait(2.29)
        self.play(Write(r3), run_time=1.4)
        self.wait(2.29)
        self.wait(3.92)
'''

SEG6 = r'''from manim import *


class Segment6(Scene):
    def construct(self):
        head = Text("Q1 (7) - THE ENDO RULE - PREDICTING MAJOR PRODUCT",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{endo rule: electron-withdrawing carbonyls"
                     r"\ \text{stack under the diene pi cloud}",
                     font_size=28, color=T.text_primary)
        r2 = MathTex(r"\text{secondary orbital overlap lowers the}"
                     r"\ \text{endo transition state}",
                     font_size=27, color=T.result_intermediate)
        r3 = MathTex(r"\text{therefore: endo is the major product}",
                     font_size=28, color=T.result_final)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(rows, 10.2)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        A = np.array([-1.6, 0.55, 0])
        B = np.array([-0.7, -0.05, 0])
        C = np.array([0.7, -0.05, 0])
        D = np.array([1.6, 0.55, 0])
        perp = np.array([0, -0.2, 0])
        l1 = Line(A, B, color=T.text_primary, stroke_width=4)
        l1b = Line(A + perp, B + perp, color=T.text_primary, stroke_width=4)
        l2 = Line(B, C, color=T.text_primary, stroke_width=3)
        l3 = Line(C, D, color=T.text_primary, stroke_width=4)
        l3b = Line(C + perp, D + perp, color=T.text_primary, stroke_width=4)
        en = VGroup(l1, l1b, l2, l3, l3b)
        en.move_to(LEFT * 4.4 + UP * 0.7)
        c1 = np.array([0.0, 0.75, 0]) + en.get_center()
        c2 = np.array([0.0, 0.12, 0]) + en.get_center()
        o = np.array([0.0, -0.25, 0]) + en.get_center()
        d1 = Line(c1 + np.array([-0.35, 0.15, 0]),
                  c1 + np.array([-0.1, -0.28, 0]),
                  color=T.warning, stroke_width=4)
        d2 = Line(c1 + np.array([0.35, 0.15, 0]),
                  c1 + np.array([0.1, -0.28, 0]),
                  color=T.warning, stroke_width=4)
        link1 = Line(c1, c2, color=T.text_primary, stroke_width=4)
        link2 = Line(c2, o, color=T.text_primary, stroke_width=4)
        endo_lab = Text("endo (major)", font_size=22, color=T.result_final)
        endo_lab.next_to(en, DOWN, buff=0.5)
        self.play(Write(r1), run_time=1.8)
        self.wait(2.84)
        self.play(Create(l1), Create(l1b), Create(l2), Create(l3), Create(l3b),
                  run_time=1.5)
        self.wait(2.21)
        self.play(Create(link1), Create(link2), Create(d1), Create(d2),
                  run_time=1.2)
        self.wait(2.21)
        self.play(Write(endo_lab), run_time=0.8)
        self.wait(2.21)
        self.play(Write(r2), run_time=1.4)
        self.wait(2.21)
        self.play(Write(r3), run_time=1.4)
        box3 = SurroundingRectangle(r3, buff=0.13, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(2.21)
        self.wait(3.78)
'''

SEG7 = r'''from manim import *


class Segment7(Scene):
    def construct(self):
        head = Text("Q1 (8) - WHY THE REACTION IS CONCERTED", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{stereospecific: E/Z geometry is fully preserved}",
                     font_size=28, color=T.text_primary)
        r2 = MathTex(r"\text{no solvent effect - no charge separation}",
                     font_size=28, color=T.text_primary)
        r3 = MathTex(r"\text{radical initiators do not change the rate}",
                     font_size=28, color=T.text_primary)
        r4 = MathTex(r"\text{strongly negative activation entropy -}"
                     r"\ \text{one ordered transition state}",
                     font_size=28, color=T.result_intermediate)
        r5 = MathTex(r"\text{one step, one cyclic TS, }6\ \text{electrons flowing}",
                     font_size=30, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 11.0)
        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.6)
        self.wait(3.19)
        self.play(Write(r2), run_time=1.4)
        self.wait(3.19)
        self.play(Write(r3), run_time=1.4)
        self.wait(3.19)
        self.play(Write(r4), run_time=1.6)
        self.wait(3.19)
        self.play(Write(r5), run_time=1.6)
        box5 = SurroundingRectangle(r5, buff=0.13, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=0.9)
        self.wait(3.19)
        self.wait(5.46)
'''

SEGMENTS = [
    {"narration": "The product is cis-1,2-cyclohex-4-ene-dicarboxylic "
     "anhydride. The diene contributes carbons one through four of the new "
     "six-membered ring, and the dienophile contributes carbons five and six. "
     "Two new sigma bonds form between carbon one and carbon five, and between "
     "carbon four and carbon six. The double bond of the original diene "
     "survives between the two central ring carbons, and the anhydride group "
     "bridges the two adjacent stereocenters on the same face.",
     "visual": {"style": "product drawing", "transition": "slide-up"},
     "code": SEG0},
    {"narration": "The mechanism is concerted: three curved arrows push "
     "simultaneously. The first arrow moves the pi bond between carbon one "
     "and carbon two onto the dienophile carbon alpha. The second arrow moves "
     "the dienophile pi bond onto carbon four. The third arrow shifts the pi "
     "bond between carbon three and carbon four inward to complete the cyclic "
     "electron flow. There is no zwitterion, no diradical, and no "
     "intermediate.",
     "visual": {"style": "curved arrows cartoon", "transition": "carry-over"},
     "code": SEG1},
    {"narration": "Under normal electron demand, the diene HOMO, psi two, "
     "interacts with the dienophile LUMO, the pi star of the double bond. "
     "The terminal lobes of the HOMO have matching signs, and the LUMO has "
     "opposite lobes. In-phase overlap at both termini gives the two bonding "
     "interactions that form the new sigma bonds, which is why the reaction "
     "is symmetry-allowed.",
     "visual": {"style": "orbital diagram", "transition": "fade"},
     "code": SEG2},
    {"narration": "The diene supplies four pi electrons from its two double "
     "bonds, and the dienophile supplies two pi electrons. Six electrons "
     "move in a cyclic array, giving an aromatic transition state with four "
     "n plus two electrons. By the Woodward-Hoffmann rules, this "
     "suprafacial-suprafacial cycloaddition is thermally allowed, whereas a "
     "two plus two addition would require light.",
     "visual": {"style": "equations", "transition": "fade"},
     "code": SEG3},
    {"narration": "Only the s-cis conformation of butadiene puts both "
     "terminal carbons close enough to bond to the dienophile at the same "
     "time. In s-trans, the termini point away, and the required topology is "
     "impossible. The diene rotates about its central single bond, and "
     "heating supplies the small amount of energy this costs. Cyclic dienes "
     "locked in s-cis react exceptionally fast for exactly this reason.",
     "visual": {"style": "conformation comparison", "transition": "carry-over"},
     "code": SEG4},
    {"narration": "The cycloaddition is stereospecific. Because maleic "
     "anhydride is a cis-disubstituted alkene, both new bonds form on the "
     "same face of the developing ring, so the anhydride is cis. The product "
     "has a mirror plane and is meso, because the two stereocenters are "
     "equivalent. The E-Z configuration of any substituted diene would "
     "likewise be preserved.",
     "visual": {"style": "ring + wedges", "transition": "fade"},
     "code": SEG5},
    {"narration": "According to the endo rule, the major product places the "
     "anhydride carbonyls beneath the diene pi system. Secondary orbital "
     "interactions between the carbonyl pi-star orbitals and the interior p "
     "orbitals of the diene lower the energy of this transition state. We "
     "therefore predict the endo product: the anhydride lies on the same "
     "face of the ring as the remaining double bond.",
     "visual": {"style": "endo TS sketch", "transition": "fade"},
     "code": SEG6},
    {"narration": "The evidence for a concerted reaction: it is "
     "stereospecific, so no intermediate scrambles geometry. It shows no "
     "solvent effect, ruling out charge separation. Radical initiators do "
     "not change the rate, ruling out radical chains. And the activation "
     "entropy is strongly negative, consistent with one highly ordered "
     "transition state. One step, one cyclic transition state, six electrons "
     "flowing.",
     "visual": {"style": "evidence list", "transition": "fade"},
     "code": SEG7},
]

LECTURE = {
    "title": TITLE,
    "preset": "lab",
    "format": "mixed",
    "question": QUESTION,
    "question_code": QUESTION_CODE,
    "segments": SEGMENTS,
}
