"""Hand-authored lecture: the hard problem set (problems only).

Seven problems across chemistry (precipitation control, a complex-ion
cell), maths (a log integral, a factorial limit, a monic quartic,
unit-circle complex numbers) and economics (entry deterrence). Same
structure as charged_spheres: a QUESTION card plus SEGMENTS, each with
narration, a visual plan for the director, and Manim code.
"""

TITLE = "Hard Problem Set: Chemistry, Maths and Economics"

QUESTION = {
    "display":
        "DATA (298 K): $K_b(\\mathrm{NH_3})=1.8\\times10^{-5}$, "
        "$K_{sp}[\\mathrm{Mg(OH)_2}]=1.2\\times10^{-11}$, "
        "$E^{\\circ}(\\mathrm{Cu}^{2+}/\\mathrm{Cu})=+0.34\\ \\mathrm{V}$, "
        "$K_f[\\mathrm{Cu(NH_3)_4}^{2+}]=1.0\\times10^{13}$, "
        "$2.303RT/F=0.0591\\ \\mathrm{V}$. "
        "1A: a solution of $0.10\\ \\mathrm{M}\\ \\mathrm{MgCl_2}$ and "
        "$0.050\\ \\mathrm{M}\\ \\mathrm{NH_3}$ - show that "
        "$\\mathrm{Mg(OH)_2}$ precipitates, find the minimum $\\mathrm{NH_4Cl}$ "
        "that prevents it and the final pH, and explain the common-ion effect. "
        "1B: the cell "
        "$\\mathrm{Cu}\\,|\\,\\mathrm{Cu}^{2+}(0.10\\ \\mathrm{M})\\,||\\,"
        "[\\mathrm{Cu(NH_3)_4}]^{2+}(0.10\\ \\mathrm{M}),\\ \\mathrm{NH_3}(1.0\\ \\mathrm{M})\\,|\\,\\mathrm{Cu}$ "
        "- free $[\\mathrm{Cu}^{2+}]$, half-cell potentials, anode/cathode and "
        "$E_{cell}$, $\\Delta G$ and $K$, and the effect of doubling $\\mathrm{NH_3}$. "
        "2A: evaluate $\\int_0^1 \\ln(1+x)/(1+x^2)\\,dx$. "
        "2B: evaluate $\\lim_{n\\to\\infty}\\frac{1}{n}\\left[\\frac{(2n)!}{n!}\\right]^{1/n}$. "
        "2C: $P$ monic of degree 4 with $P(1)=10, P(2)=20, P(3)=30$ - find "
        "$P(10)+P(-6)$. "
        "2D: $|z_1|=|z_2|=|z_3|=1$ and $z_1+z_2+z_3=0$ - prove the points form "
        "an equilateral triangle on the unit circle and find "
        "$\\sum|z_i-z_j|^2$. "
        "3: $P=100-Q$, $MC=10$ for both firms, entrant fixed cost $F=225$ - "
        "best response, limit quantity, deterrence versus accommodation, the "
        "range of $F$ where deterrence is optimal, welfare, and Cournot.",
    "speech":
        "Here is the hard problem set, problems only. The data at two hundred "
        "ninety-eight kelvin: K B of ammonia one point eight times ten to the "
        "minus five, K S P of magnesium hydroxide one point two times ten to "
        "the minus eleven, copper's standard potential plus zero point three "
        "four volts, and the ammine formation constant ten to the thirteen. "
        "Chemistry: show that magnesium hydroxide precipitates from ammonia, "
        "find the ammonium chloride that just prevents it, then solve the "
        "complex-ion copper cell - potentials, cell voltage, delta G and K. "
        "Maths: a logarithmic integral, a factorial limit, a monic quartic "
        "through ten, twenty and thirty, and three unit complex numbers that "
        "sum to zero. Economics: entry deterrence - the limit quantity, "
        "deterrence versus accommodation, the range of F, welfare, and "
        "Cournot. Seven problems. Let us solve them all.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("HARD PROBLEM SET - PROBLEMS ONLY", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = MathTex(
            r"K_b=1.8\times10^{-5},\quad K_{sp}=1.2\times10^{-11},\quad "
            r"E^{\circ}=+0.34\ \mathrm{V},\quad K_f=10^{13}",
            font_size=27, color=T.constant)
        c_chem = Text("CHEMISTRY", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "1A  Mg(OH)2 from MgCl2/NH3 - precipitate? least NH4Cl? pH?\n"
            "1B  Cu | Cu2+ || [Cu(NH3)4]2+, NH3 | Cu - potentials, Ecell, dG, K",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("MATHS", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "2A  integral of ln(1+x)/(1+x2)   2B  lim (1/n)[(2n)!/n!]^(1/n)\n"
            "2C  monic quartic through 10, 20, 30   2D  |zi| = 1, sum zero",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("ECONOMICS", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "3  entry deterrence: limit quantity, deter or accommodate,\n"
            "range of F, welfare, and Cournot entry",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        chem = VGroup(c_chem, r_chem).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        maths = VGroup(c_math, r_math).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        econ = VGroup(c_econ, r_econ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rows = VGroup(data, chem, maths, econ).arrange(DOWN, aligned_edge=LEFT,
                                                       buff=0.34)
        rows.move_to(UP * 0.2)
        fit_width(rows, 12.9)
        beak = VGroup(
            Line(LEFT * 0.55, DOWN * 0.75 + LEFT * 0.55),
            Line(DOWN * 0.75 + LEFT * 0.55, DOWN * 0.75 + RIGHT * 0.55),
            Line(DOWN * 0.75 + RIGHT * 0.55, RIGHT * 0.55))
        beak.set_stroke(T.auxiliary_geometry, 2.5)
        pi_s = MathTex(r"\pi", font_size=34, color=T.graph_tangent)
        bars = VGroup(Rectangle(width=0.22, height=0.55),
                      Rectangle(width=0.22, height=0.85),
                      Rectangle(width=0.22, height=0.35))
        bars.arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
        bars.set_fill(T.result_final, 0.7).set_stroke(width=0)
        sketch = VGroup(beak, pi_s, bars).arrange(RIGHT, buff=1.6)
        sketch.move_to(DOWN * 2.9)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(data), run_time=2.2)
        self.wait(6.0)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(9.0)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(10.0)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(10.0)
        self.play(Create(beak), run_time=0.8)
        self.play(Write(pi_s), run_time=0.7)
        self.play(FadeIn(bars, shift=0.2 * UP), run_time=0.8)
        self.wait(9.0)
        self.play(FadeOut(sketch), run_time=0.6)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(2.0)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("PROBLEM 1A - DOES Mg(OH)2 PRECIPITATE?", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"[\mathrm{Mg}^{2+}]=0.10\ \mathrm{M},\qquad "
                     r"[\mathrm{NH_3}]=0.050\ \mathrm{M}",
                     font_size=29, color=T.constant)
        r2 = MathTex(r"K_b=1.8\times10^{-5},\qquad K_{sp}=1.2\times10^{-11}",
                     font_size=29, color=T.constant)
        r3 = MathTex(r"\mathrm{NH_3}+\mathrm{H_2O}\ \rightleftharpoons\ "
                     r"\mathrm{NH_4^+}+\mathrm{OH^-}",
                     font_size=31, color=T.variable)
        r4 = MathTex(r"x=[\mathrm{OH^-}]=\sqrt{K_b\,C}"
                     r"=\sqrt{1.8\times10^{-5}\times0.050}",
                     font_size=29, color=T.text_primary)
        r5 = MathTex(r"[\mathrm{OH^-}]=9.5\times10^{-4}\ \mathrm{M}",
                     font_size=29, color=T.result_intermediate)
        r6 = MathTex(r"Q=[\mathrm{Mg}^{2+}][\mathrm{OH^-}]^2"
                     r"=0.10\times(9.5\times10^{-4})^2=9.0\times10^{-8}",
                     font_size=29, color=T.text_primary)
        lab_q = MathTex(r"Q", font_size=28, color=T.warning)
        bar_q = Rectangle(width=4.5, height=0.24, fill_color=T.warning,
                          fill_opacity=0.85, stroke_width=0)
        val_q = MathTex(r"9.0\times10^{-8}", font_size=25,
                        color=T.text_secondary)
        row_q = VGroup(lab_q, bar_q, val_q).arrange(RIGHT, buff=0.2)
        lab_k = MathTex(r"K_{sp}", font_size=28, color=T.constant)
        bar_k = Rectangle(width=0.30, height=0.24, fill_color=T.constant,
                          fill_opacity=0.85, stroke_width=0)
        val_k = MathTex(r"1.2\times10^{-11}", font_size=25,
                        color=T.text_secondary)
        row_k = VGroup(lab_k, bar_k, val_k).arrange(RIGHT, buff=0.2)
        r7 = MathTex(r"Q\gg K_{sp}\ \Rightarrow\ "
                     r"\mathrm{Mg(OH)_2\ precipitates}",
                     font_size=29, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5, r6, row_q, row_k)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        fit_width(rows, 6.7)

        if rows.height > 6.0:

            rows.scale_to_fit_height(6.0)

        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        r7.move_to(rows.get_bottom() + DOWN * 0.55)
        r7.align_to(rows, LEFT)
        fit_width(r7, 6.7)
        bx = RIGHT * 3.85 + UP * 0.35
        rim = Line(UP * 1.55 + LEFT * 1.15, UP * 1.55 + RIGHT * 1.15)
        wl = Line(UP * 1.55 + LEFT * 1.15, DOWN * 1.35 + LEFT * 1.15)
        base = Line(DOWN * 1.35 + LEFT * 1.15, DOWN * 1.35 + RIGHT * 1.15)
        wr = Line(UP * 1.55 + RIGHT * 1.15, DOWN * 1.35 + RIGHT * 1.15)
        glass = VGroup(rim, wl, base, wr)
        glass.set_stroke(T.auxiliary_geometry, 3)
        liquid = Rectangle(width=2.3, height=2.4, stroke_width=0,
                           fill_color=T.variable, fill_opacity=0.10)
        liquid.move_to(bx + DOWN * 0.15)
        glass.move_to(bx)
        drops = VGroup(*[Dot(radius=0.055, color=T.text_primary,
                             fill_opacity=0.9)
                         for _ in range(7)])
        drops.arrange_in_grid(rows=2, cols=4, buff=0.22)
        drops.move_to(bx + DOWN * 0.95)
        tag = MathTex(r"\mathrm{Mg(OH)_2(s)}", font_size=26,
                      color=T.result_final)
        tag.next_to(glass, DOWN, buff=0.35)
        solute = Text("Mg2+ + NH3(aq)", font_size=22, color=T.text_muted)
        solute.next_to(rim, UP, buff=0.2)
        self.play(Write(r1), run_time=1.6)
        self.wait(4.06)
        self.play(Write(r2), run_time=1.4)
        self.wait(4.73)
        self.play(Write(r3), Create(liquid), run_time=1.6)
        self.wait(5.41)
        self.play(Write(r4), run_time=1.8)
        self.wait(4.06)
        self.play(Write(r5), run_time=1.0)
        self.wait(4.73)
        self.play(Write(r6), run_time=2.0)
        self.wait(4.06)
        self.play(FadeIn(row_q, shift=0.2 * RIGHT), run_time=0.8)
        self.play(FadeIn(row_k, shift=0.2 * RIGHT), run_time=0.8)
        self.wait(7.44)
        self.play(Write(r7), run_time=1.2)
        box = SurroundingRectangle(r7, buff=0.16, color=T.result_final)
        self.play(Create(box), run_time=0.7)
        emphasize(self, r7, color=T.result_final, run_time=0.9)
        self.play(FadeIn(drops, shift=0.4 * DOWN), Write(solute),
                  Write(tag), run_time=1.4)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("1A (b)-(d) - NH4Cl HOLDS THE PRECIPITATE BACK",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"Q=K_{sp}\ \Rightarrow\ [\mathrm{OH^-}]_{\max}"
                     r"=\sqrt{\frac{K_{sp}}{[\mathrm{Mg}^{2+}]}}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"=\sqrt{\frac{1.2\times10^{-11}}{0.10}}"
                     r"=1.10\times10^{-5}\ \mathrm{M}",
                     font_size=29, color=T.result_intermediate)
        r3 = MathTex(r"K_b=\frac{[\mathrm{NH_4^+}][\mathrm{OH^-}]}{[\mathrm{NH_3}]}"
                     r"\ \Rightarrow\ [\mathrm{NH_4^+}]"
                     r"=\frac{K_b[\mathrm{NH_3}]}{[\mathrm{OH^-}]}",
                     font_size=29, color=T.text_primary)
        r4 = MathTex(r"=\frac{1.8\times10^{-5}\times0.050}"
                     r"{1.10\times10^{-5}}=0.082\ \mathrm{M}",
                     font_size=29, color=T.result_intermediate)
        r5 = MathTex(r"\mathrm{pH}=14-\mathrm{pOH}"
                     r"=14-4.96=9.04\approx9.0",
                     font_size=29, color=T.result_intermediate)
        r6 = MathTex(r"\mathrm{NH_3}+\mathrm{H_2O}\ \rightleftharpoons\ "
                     r"\mathrm{NH_4^+}+\mathrm{OH^-}",
                     font_size=31, color=T.variable)
        r7 = MathTex(r"\text{add }\mathrm{NH_4^+}\ \text{(common ion)}"
                     r"\ \Rightarrow\ \text{equilibrium shifts left}",
                     font_size=27, color=T.text_primary)
        r8 = MathTex(r"[\mathrm{OH^-}]\downarrow\ \text{below threshold}"
                     r"\ \Rightarrow\ \text{no precipitate}",
                     font_size=27, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5, r6, r7, r8)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        fit_width(rows, 6.9)

        if rows.height > 6.0:

            rows.scale_to_fit_height(6.0)

        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        box_a = SurroundingRectangle(VGroup(r4), buff=0.13,
                                     color=T.result_final)
        box_p = SurroundingRectangle(VGroup(r5), buff=0.13,
                                     color=T.result_final)
        tracker = ValueTracker(1.0)
        bar_c = RIGHT * 3.7 + DOWN * 0.4
        thr = DashedLine(bar_c + LEFT * 2.3, bar_c + RIGHT * 2.3,
                         color=T.cancel_mark, stroke_width=3)
        thr_lab = MathTex(r"[\mathrm{OH^-}]_{\max}", font_size=25,
                          color=T.cancel_mark)
        thr_lab.next_to(thr, UP, buff=0.15)
        bar = always_redraw(lambda: Rectangle(
            width=max(0.3, 4.4 * tracker.get_value()), height=0.34,
            fill_color=T.vector_gravity, fill_opacity=0.85,
            stroke_width=0).move_to(bar_c + LEFT * (2.3 - 0.5 *
                                                   tracker.get_value()),
                                    aligned_edge=LEFT))
        bar_lab = MathTex(r"[\mathrm{OH^-}]", font_size=25,
                          color=T.vector_gravity)
        bar_lab.next_to(bar_c, DOWN, buff=0.4)
        nh4 = Text("adding NH4Cl", font_size=22, color=T.constant)
        nh4.next_to(thr_lab, UP, buff=0.35)
        arrow = Arrow(bar_c + UP * 1.3, bar_c + DOWN * 0.4,
                      color=T.constant, stroke_width=4)
        arrow.next_to(thr.get_right(), RIGHT, buff=0.3)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.32)
        self.play(Write(r2), run_time=1.2)
        self.wait(3.79)
        self.play(Write(r3), run_time=2.0)
        self.wait(4.26)
        self.play(Write(r4), FadeIn(bar), run_time=1.4)
        self.play(Create(box_a), run_time=0.7)
        self.wait(4.26)
        self.play(Write(r5), run_time=1.2)
        self.play(Create(box_p), run_time=0.7)
        self.wait(3.79)
        self.play(Write(r6), run_time=1.2)
        self.wait(2.84)
        self.play(Write(r7), Create(thr), Write(thr_lab), FadeIn(nh4),
                  run_time=1.6)
        self.wait(3.32)
        self.play(tracker.animate.set_value(0.07), run_time=3.2)
        self.wait(2.84)
        self.play(Write(r8), run_time=1.2)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("PROBLEM 1B - THE COMPLEX-ION CELL", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"K_f=\frac{[\mathrm{Cu(NH_3)_4}^{2+}]}"
                     r"{[\mathrm{Cu}^{2+}][\mathrm{NH_3}]^4}"
                     r"=1.0\times10^{13}",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"[\mathrm{Cu}^{2+}]_{\mathrm{free}}"
                     r"=\frac{0.10}{1.0\times10^{13}\times(1.0)^4}"
                     r"=1.0\times10^{-14}\ \mathrm{M}",
                     font_size=29, color=T.result_final)
        r3 = MathTex(r"E=E^{\circ}+\frac{0.0591}{2}\log[\mathrm{Cu}^{2+}],"
                     r"\qquad E^{\circ}=+0.34\ \mathrm{V}",
                     font_size=29, color=T.text_primary)
        r4 = MathTex(r"E_R=0.34+0.0296\times(-14)=-0.074\ \mathrm{V}",
                     font_size=29, color=T.result_intermediate)
        r5 = MathTex(r"E_L=0.34+0.0296\times(-1)=+0.310\ \mathrm{V}",
                     font_size=29, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3, r4, r5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 5.9)

        if rows.height > 6.0:

            rows.scale_to_fit_height(6.0)

        rows.next_to(rule, DOWN, buff=0.5)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        box_f = SurroundingRectangle(r2, buff=0.13, color=T.result_final)
        bl = RIGHT * 1.3 + DOWN * 0.55
        br = RIGHT * 5.0 + DOWN * 0.55
        wl = Line(UP * 1.3 + LEFT * 1.05, DOWN * 1.15 + LEFT * 1.05)
        bl_b = Line(DOWN * 1.15 + LEFT * 1.05, DOWN * 1.15 + RIGHT * 1.05)
        wrr = Line(DOWN * 1.15 + RIGHT * 1.05, UP * 1.3 + RIGHT * 1.05)
        glass_l = VGroup(wl, bl_b, wrr).set_stroke(T.auxiliary_geometry, 3)
        glass_l.move_to(bl)
        wr2 = Line(UP * 1.3 + LEFT * 1.05, DOWN * 1.15 + LEFT * 1.05)
        br_b = Line(DOWN * 1.15 + LEFT * 1.05, DOWN * 1.15 + RIGHT * 1.05)
        wr3 = Line(DOWN * 1.15 + RIGHT * 1.05, UP * 1.3 + RIGHT * 1.05)
        glass_r = VGroup(wr2, br_b, wr3).set_stroke(T.auxiliary_geometry, 3)
        glass_r.move_to(br)
        liq_l = Rectangle(width=2.1, height=1.9, stroke_width=0,
                          fill_color=T.graph_point, fill_opacity=0.10)
        liq_l.move_to(bl + DOWN * 0.12)
        liq_r = Rectangle(width=2.1, height=1.9, stroke_width=0,
                          fill_color=T.variable, fill_opacity=0.16)
        liq_r.move_to(br + DOWN * 0.12)
        el_l = Rectangle(width=0.18, height=2.3, fill_color=T.vector_acceleration,
                         fill_opacity=0.9, stroke_width=1,
                         stroke_color=T.text_primary)
        el_r = el_l.copy()
        el_l.move_to(bl + UP * 0.75)
        el_r.move_to(br + UP * 0.75)
        bridge = VGroup(
            Line(bl + UP * 1.35, bl + UP * 1.95),
            Line(bl + UP * 1.95, br + UP * 1.95),
            Line(br + UP * 1.95, br + UP * 1.35))
        bridge.set_stroke(T.auxiliary_geometry, 3)
        lab_l = MathTex(r"\mathrm{Cu}^{2+}\ 0.10\ \mathrm{M}", font_size=25,
                        color=T.graph_point)
        lab_l.next_to(glass_l, DOWN, buff=0.3)
        lab_r = MathTex(r"[\mathrm{Cu(NH_3)_4}]^{2+}\ 0.10\ \mathrm{M}",
                        font_size=25, color=T.variable)
        lab_r.next_to(glass_r, DOWN, buff=0.3).shift(LEFT * 0.35)
        lab_nh = MathTex(r"\mathrm{NH_3}\ 1.0\ \mathrm{M}", font_size=25,
                         color=T.atom_nitrogen)
        lab_nh.next_to(lab_r, DOWN, buff=0.18)
        tag = MathTex(r"[\mathrm{Cu}^{2+}]_{\mathrm{free}}=10^{-14}",
                      font_size=24, color=T.result_final)
        e_r = MathTex(r"E_R=-0.074\ \mathrm{V}", font_size=25,
                      color=T.result_intermediate)
        e_r.next_to(el_r, UP, buff=0.25)
        tag.next_to(e_r, UP, buff=0.18).shift(RIGHT * 0.35)
        e_l = MathTex(r"E_L=+0.310\ \mathrm{V}", font_size=25,
                      color=T.result_intermediate)
        e_l.next_to(el_l, UP, buff=0.25)
        cu = Text("Cu", font_size=20, color=T.vector_acceleration)
        cu.next_to(el_l, LEFT, buff=0.15)
        cu2 = Text("Cu", font_size=20, color=T.vector_acceleration)
        cu2.next_to(el_r, RIGHT, buff=0.15)
        self.play(Write(r1), run_time=2.2)
        self.wait(6.3)
        self.play(Write(r2), Create(glass_l), Create(glass_r), Create(liq_l),
                  Create(liq_r), run_time=2.0)
        self.play(Create(box_f), Create(el_l), Create(el_r), Create(bridge),
                  run_time=1.2)
        self.wait(5.6)
        self.play(Write(r3), run_time=2.0)
        self.wait(6.3)
        self.play(Write(r4), Write(e_r), run_time=1.6)
        self.wait(6.3)
        self.play(Write(r5), Write(e_l), Write(lab_l), Write(lab_r),
                  Write(lab_nh), Write(cu), Write(cu2), run_time=1.8)
        self.wait(4.2)
        self.play(Write(tag), run_time=1.0)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("1B (c)-(e) - ANODE, CATHODE, dG, K", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        bl = RIGHT * 1.3 + DOWN * 0.95
        br = RIGHT * 5.0 + DOWN * 0.95
        wl = Line(UP * 1.3 + LEFT * 1.05, DOWN * 1.15 + LEFT * 1.05)
        bl_b = Line(DOWN * 1.15 + LEFT * 1.05, DOWN * 1.15 + RIGHT * 1.05)
        wrr = Line(DOWN * 1.15 + RIGHT * 1.05, UP * 1.3 + RIGHT * 1.05)
        glass_l = VGroup(wl, bl_b, wrr).set_stroke(T.auxiliary_geometry, 3)
        glass_l.move_to(bl)
        wr2 = Line(UP * 1.3 + LEFT * 1.05, DOWN * 1.15 + LEFT * 1.05)
        br_b = Line(DOWN * 1.15 + LEFT * 1.05, DOWN * 1.15 + RIGHT * 1.05)
        wr3 = Line(DOWN * 1.15 + RIGHT * 1.05, UP * 1.3 + RIGHT * 1.05)
        glass_r = VGroup(wr2, br_b, wr3).set_stroke(T.auxiliary_geometry, 3)
        glass_r.move_to(br)
        liq_l = Rectangle(width=2.1, height=1.9, stroke_width=0,
                          fill_color=T.graph_point, fill_opacity=0.10)
        liq_l.move_to(bl + DOWN * 0.12)
        liq_r = Rectangle(width=2.1, height=1.9, stroke_width=0,
                          fill_color=T.variable, fill_opacity=0.16)
        liq_r.move_to(br + DOWN * 0.12)
        el_l = Rectangle(width=0.18, height=2.3, fill_color=T.vector_acceleration,
                         fill_opacity=0.9, stroke_width=1,
                         stroke_color=T.text_primary)
        el_r = el_l.copy()
        el_l.move_to(bl + UP * 0.75)
        el_r.move_to(br + UP * 0.75)
        bridge = VGroup(
            Line(bl + UP * 1.35, bl + UP * 1.95),
            Line(bl + UP * 1.95, br + UP * 1.95),
            Line(br + UP * 1.95, br + UP * 1.35))
        bridge.set_stroke(T.auxiliary_geometry, 3)
        anode = Text("ANODE", font_size=22, color=T.warning)
        anode.next_to(el_r, UP, buff=0.25)
        cath = Text("CATHODE", font_size=22, color=T.stable_state)
        cath.next_to(el_l, UP, buff=0.25)
        eflow = Arrow(br + UP * 2.75, bl + UP * 2.75, color=T.constant,
                      stroke_width=4)
        elab = MathTex(r"e^{-}", font_size=26, color=T.constant)
        elab.next_to(eflow, UP, buff=0.12)
        r1 = MathTex(r"\text{anode (right): }\mathrm{Cu}+4\mathrm{NH_3}"
                     r"\rightarrow[\mathrm{Cu(NH_3)_4}]^{2+}+2e^{-}",
                     font_size=27, color=T.warning)
        r2 = MathTex(r"\text{cathode (left): }\mathrm{Cu}^{2+}+2e^{-}"
                     r"\rightarrow\mathrm{Cu}",
                     font_size=27, color=T.stable_state)
        r3 = MathTex(r"E_{\mathrm{cell}}=E_{\mathrm{cathode}}"
                     r"-E_{\mathrm{anode}}=0.310-(-0.074)=0.384\ \mathrm{V}",
                     font_size=29, color=T.result_final)
        r4 = MathTex(r"\text{overall: }\mathrm{Cu}^{2+}+4\mathrm{NH_3}"
                     r"\rightleftharpoons[\mathrm{Cu(NH_3)_4}]^{2+},"
                     r"\qquad K=K_f=10^{13}",
                     font_size=27, color=T.result_final)
        r5 = MathTex(r"\Delta G=-nFE_{\mathrm{cell}}"
                     r"=-2\times96485\times0.384=-74.1\ \mathrm{kJ/mol}",
                     font_size=29, color=T.result_final)
        r6 = MathTex(r"[\mathrm{NH_3}]=2.0:\ "
                     r"[\mathrm{Cu}^{2+}]=\frac{0.10}{10^{13}\times16}"
                     r"=6.3\times10^{-16}\ \mathrm{M}",
                     font_size=27, color=T.text_primary)
        r7 = MathTex(r"E_{\mathrm{cell}}=0.0296\log\frac{0.10}{6.3\times10^{-16}}"
                     r"=0.420\ \mathrm{V}",
                     font_size=27, color=T.result_intermediate)
        r8 = MathTex(r"\Delta E=+0.036\ \mathrm{V}=+36\ \mathrm{mV}",
                     font_size=27, color=T.result_final)
        rows = VGroup(r1, r2, r3, r4, r5, r6, r7, r8)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        fit_width(rows, 6.2)

        if rows.height > 6.0:

            rows.scale_to_fit_height(6.0)

        rows.next_to(rule, DOWN, buff=0.42)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        self.play(Create(glass_l), Create(glass_r), Create(liq_l), Create(liq_r),
                  Create(el_l), Create(el_r), Create(bridge), run_time=1.6)
        self.play(Write(anode), Write(cath), Create(eflow), Write(elab),
                  run_time=1.2)
        self.wait(4.62)
        self.play(Write(r1), run_time=1.8)
        self.wait(4.62)
        self.play(Write(r2), run_time=1.2)
        self.wait(3.96)
        self.play(Write(r3), run_time=1.8)
        box3 = SurroundingRectangle(r3, buff=0.13, color=T.result_final)
        self.play(Create(box3), run_time=0.7)
        emphasize(self, r3, color=T.result_final, run_time=0.9)
        self.wait(4.62)
        self.play(Write(r4), run_time=1.8)
        box4 = SurroundingRectangle(r4, buff=0.13, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        self.wait(4.62)
        self.play(Write(r5), run_time=1.8)
        box5 = SurroundingRectangle(r5, buff=0.13, color=T.result_final)
        self.play(Create(box5), run_time=0.7)
        self.wait(5.28)
        self.play(Write(r6), run_time=1.6)
        self.wait(5.28)
        self.play(Write(r7), run_time=1.6)
        self.wait(4.62)
        self.play(Write(r8), run_time=1.0)
        box8 = SurroundingRectangle(r8, buff=0.13, color=T.result_final)
        self.play(Create(box8), run_time=0.7)
        self.wait(6)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("PROBLEM 2A - A LOGARITHMIC INTEGRAL", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"I=\int_{0}^{1}\frac{\ln(1+x)}{1+x^{2}}\,dx",
                     font_size=31, color=T.variable)
        r2 = MathTex(r"x=\tan\theta:\quad dx=\sec^{2}\theta\,d\theta,"
                     r"\qquad \theta:0\to\frac{\pi}{4}",
                     font_size=29, color=T.text_primary)
        r3 = MathTex(r"I=\int_{0}^{\pi/4}\ln(1+\tan\theta)\,d\theta",
                     font_size=31, color=T.text_primary)
        r4 = MathTex(r"1+\tan\theta=\frac{\cos\theta+\sin\theta}{\cos\theta}"
                     r"=\frac{\sqrt{2}\,\cos(\theta-\frac{\pi}{4})}{\cos\theta}",
                     font_size=29, color=T.text_primary)
        r5a = MathTex(
            r"I=\frac{\pi}{4}\cdot\frac{\ln 2}{2}",
            r"+",
            r"\ \int_{0}^{\pi/4}\ln\cos(\theta-\tfrac{\pi}{4})\,d\theta",
            r"-",
            r"\ \int_{0}^{\pi/4}\ln\cos\theta\,d\theta",
            font_size=29, color=T.text_primary)
        r6 = MathTex(r"u=\frac{\pi}{4}-\theta:\ "
                     r"\int_{0}^{\pi/4}\ln\cos(\theta-\tfrac{\pi}{4})\,d\theta"
                     r"=\int_{0}^{\pi/4}\ln\cos u\,du",
                     font_size=27, color=T.result_intermediate)
        r7 = MathTex(r"I=\frac{\pi\,\ln 2}{8}\approx0.272",
                     font_size=33, color=T.result_final)
        left = VGroup(r1, r2, r3, r4, r6, r7)
        left.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        fit_width(left, 7.2)

        if left.height > 6.0:

            left.scale_to_fit_height(6.0)

        left.next_to(rule, DOWN, buff=0.4)
        left.align_to(rule, LEFT).shift(RIGHT * 0.4)
        r5a.move_to(left.get_bottom() + DOWN * 0.62)
        r5a.align_to(left, LEFT)
        fit_width(r5a, 7.4)
        axes = Axes(x_range=[0, 1, 0.5], y_range=[0, 0.8, 0.2],
                    x_length=4.6, y_length=3.0,
                    axis_config={"color": T.text_muted, "stroke_width": 1.5,
                                 "include_tip": False})
        axes.move_to(RIGHT * 3.9 + DOWN * 1.05)
        f = lambda x: np.log(1 + x) / (1 + x * x)
        curve = axes.plot(f, x_range=[0, 1], color=T.graph_function,
                          stroke_width=4)
        curve_lab = MathTex(r"y=\frac{\ln(1+x)}{1+x^2}", font_size=25,
                            color=T.graph_function)
        curve_lab.next_to(axes, UP, buff=0.25)
        area_lab = MathTex(r"\text{area}=0.272", font_size=25,
                           color=T.result_final)
        area_lab.next_to(axes, DOWN, buff=0.25)
        rects = riemann_rectangles(axes, f, 0.0, 1.0, 4)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.68)
        self.play(Write(r2), run_time=1.8)
        self.wait(3.68)
        self.play(Write(r3), run_time=1.2)
        self.wait(2.76)
        self.play(Write(r4), run_time=2.0)
        self.wait(3.68)
        self.play(Write(r5a), Create(axes), Create(curve), run_time=2.2)
        self.play(Create(curve_lab), run_time=0.8)
        self.wait(5.52)
        self.play(Write(r6), run_time=1.6)
        self.wait(4.6)
        slash_a = strike_through(self, r5a[2], run_time=0.6)
        slash_b = strike_through(self, r5a[4], run_time=0.6)
        self.wait(3.22)
        self.play(FadeOut(VGroup(r5a, slash_a, slash_b)), run_time=0.6)
        self.play(TransformMatchingTex(r6.copy(), r7), run_time=1.4)
        box = SurroundingRectangle(r7, buff=0.16, color=T.result_final)
        self.play(Create(box), run_time=0.7)
        emphasize(self, r7, color=T.result_final, run_time=0.9)
        self.play(FadeIn(rects), run_time=1.6)
        rects2 = riemann_rectangles(axes, f, 0.0, 1.0, 16)
        self.play(Transform(rects, rects2), run_time=2.2)
        self.play(Write(area_lab), run_time=0.9)
        self.wait(6)
'''

SEG5 = r'''from manim import *


class Segment5(Scene):
    def construct(self):
        head = Text("PROBLEM 2B - A FACTORIAL LIMIT", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"L=\lim_{n\to\infty}\frac{1}{n}"
                     r"\left[\frac{(2n)!}{n!}\right]^{1/n}",
                     font_size=31, color=T.variable)
        r2 = MathTex(r"\ln\frac{(2n)!}{n!}=\sum_{k=n+1}^{2n}\ln k",
                     font_size=29, color=T.text_primary)
        r3 = MathTex(r"\frac{1}{n}\sum_{k=n+1}^{2n}\ln k"
                     r"=\ln n+\frac{1}{n}\sum_{k=n+1}^{2n}\ln\frac{k}{n}",
                     font_size=29, color=T.text_primary)
        r4 = MathTex(r"\to\ \ln n+\int_{1}^{2}\ln t\,dt"
                     r"=\ln n+2\ln 2-1",
                     font_size=29, color=T.result_intermediate)
        r5 = MathTex(r"\left[\frac{(2n)!}{n!}\right]^{1/n}\to"
                     r"\ e^{2\ln 2-1}\cdot n=\frac{4}{e}\,n",
                     font_size=29, color=T.text_primary)
        r6 = MathTex(r"L=\frac{4}{e}\approx1.47", font_size=33,
                     color=T.result_final)
        r7 = MathTex(r"\text{Stirling: }\frac{(2n)!}{n!}\approx"
                     r"\sqrt{2}\,4^{n}n^{n}e^{-n}",
                     font_size=27, color=T.text_secondary)
        left = VGroup(r1, r2, r3, r4, r5, r6, r7)
        left.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        fit_width(left, 7.2)

        if left.height > 6.0:

            left.scale_to_fit_height(6.0)

        left.next_to(rule, DOWN, buff=0.42)
        left.align_to(rule, LEFT).shift(RIGHT * 0.4)
        axes = Axes(x_range=[1, 2, 0.25], y_range=[0, 0.8, 0.2],
                    x_length=4.4, y_length=3.0,
                    axis_config={"color": T.text_muted, "stroke_width": 1.5,
                                 "include_tip": False})
        axes.move_to(RIGHT * 4.0 + DOWN * 1.0)
        g = lambda t: np.log(t)
        curve = axes.plot(g, x_range=[1, 2], color=T.graph_function,
                          stroke_width=4)
        curve_lab = MathTex(r"y=\ln t", font_size=25, color=T.graph_function)
        curve_lab.next_to(axes, UP, buff=0.25)
        area_lab = MathTex(r"\int_1^2\ln t\,dt=2\ln2-1\approx0.386",
                           font_size=25, color=T.result_final)
        area_lab.next_to(axes, DOWN, buff=0.25)
        rects = riemann_rectangles(axes, g, 1.0, 2.0, 4)
        self.play(Write(r1), run_time=1.8)
        self.wait(3.84)
        self.play(Write(r2), run_time=1.4)
        self.wait(3.36)
        self.play(Write(r3), run_time=2.0)
        self.wait(4.32)
        self.play(Write(r4), Create(axes), Create(curve), Write(curve_lab),
                  run_time=2.0)
        self.wait(4.32)
        self.play(Write(r5), run_time=1.8)
        self.wait(3.36)
        self.play(Write(r6), FadeIn(rects), run_time=1.4)
        box = SurroundingRectangle(r6, buff=0.16, color=T.result_final)
        self.play(Create(box), run_time=0.7)
        emphasize(self, r6, color=T.result_final, run_time=0.9)
        rects2 = riemann_rectangles(axes, g, 1.0, 2.0, 24)
        self.play(Transform(rects, rects2), run_time=2.0)
        self.play(Write(area_lab), run_time=1.0)
        self.wait(2.4)
        self.play(Write(r7), run_time=1.4)
        self.wait(6)
'''

SEG6 = r'''from manim import *


class Segment6(Scene):
    def construct(self):
        head = Text("PROBLEM 2C - THE MONIC QUARTIC", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"P(1)=10,\quad P(2)=20,\quad P(3)=30",
                     font_size=29, color=T.constant)
        r2 = MathTex(r"Q(x)=P(x)-10x:\ \text{monic, and }"
                     r"Q(1)=Q(2)=Q(3)=0",
                     font_size=29, color=T.text_primary)
        r3 = MathTex(r"Q(x)=(x-1)(x-2)(x-3)(x-r)",
                     font_size=31, color=T.variable)
        r4 = MathTex(r"P(10)=9\cdot8\cdot7\,(10-r)+100"
                     r"=504(10-r)+100",
                     font_size=29, color=T.text_primary)
        r5 = MathTex(r"P(-6)=(-504)(-6-r)-60=504(6+r)-60",
                     font_size=29, color=T.text_primary)
        r6 = MathTex(r"P(10)+P(-6)=504(10-r)", r"+", r"504(6+r)", r"+40",
                     font_size=29, color=T.text_primary)
        r7 = MathTex(r"=504\times16+40=\mathbf{8104}",
                     font_size=33, color=T.result_final)
        r8 = Text("the free root r cancels - the answer is unique",
                  font_size=24, color=T.text_secondary)
        left = VGroup(r1, r2, r3, r4, r5, r8)
        left.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        fit_width(left, 7.6)

        if left.height > 6.0:

            left.scale_to_fit_height(6.0)

        left.next_to(rule, DOWN, buff=0.42)
        left.align_to(rule, LEFT).shift(RIGHT * 0.4)
        r6.move_to(left.get_bottom() + DOWN * 0.55)
        r6.align_to(left, LEFT)
        r7.move_to(r6.get_bottom() + DOWN * 0.6)
        r7.align_to(left, LEFT)
        fit_width(r7, 7.6)
        numline = NumberLine(x_range=[-1, 11, 1], length=5.2,
                             color=T.text_muted, stroke_width=2,
                             include_tip=True, tip_width=0.16, tip_height=0.16,
                             font_size=22)
        numline.move_to(RIGHT * 3.9 + UP * 1.5)
        d1 = Dot(numline.number_to_point(1), color=T.variable, radius=0.09)
        d2 = Dot(numline.number_to_point(2), color=T.variable, radius=0.09)
        d3 = Dot(numline.number_to_point(3), color=T.variable, radius=0.09)
        dr = Dot(numline.number_to_point(7.5), color=T.warning, radius=0.09)
        dr.set_fill(opacity=0.5)
        lab_r = MathTex(r"r=?", font_size=26, color=T.warning)
        lab_r.next_to(dr, UP, buff=0.2)
        roots = Text("roots of Q: 1, 2, 3 and a free r",
                     font_size=22, color=T.text_secondary)
        roots.next_to(numline, DOWN, buff=0.5)
        self.play(Write(r1), run_time=1.4)
        self.wait(4.51)
        self.play(Write(r2), run_time=2.0)
        self.wait(5.16)
        self.play(Write(r3), Create(numline), FadeIn(d1), FadeIn(d2),
                  FadeIn(d3), run_time=1.8)
        self.play(FadeIn(dr, scale=0.5), Write(lab_r), Write(roots),
                  run_time=1.0)
        self.wait(5.8)
        self.play(Write(r4), run_time=1.8)
        self.wait(5.16)
        self.play(Write(r5), run_time=1.6)
        self.wait(5.16)
        self.play(Write(r6), run_time=1.4)
        self.wait(4.51)
        slash_c = strike_through(self, r6[0], run_time=0.6)
        slash_d = strike_through(self, r6[2], run_time=0.6)
        self.wait(3.87)
        self.play(FadeOut(VGroup(r6, slash_c, slash_d)), run_time=0.5)
        self.play(Write(r7), run_time=1.2)
        box = SurroundingRectangle(r7, buff=0.16, color=T.result_final)
        self.play(Create(box), run_time=0.7)
        emphasize(self, r7, color=T.result_final, run_time=0.9)
        self.play(Write(r8), run_time=1.2)
        self.wait(6)
'''

SEG7 = r'''from manim import *


class Segment7(Scene):
    def construct(self):
        head = Text("PROBLEM 2D - THREE UNIT COMPLEX NUMBERS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"z_1+z_2+z_3=0,\qquad |z_1|=|z_2|=|z_3|=1",
                     font_size=29, color=T.text_primary)
        r2 = MathTex(r"|z_1+z_2|=|-z_3|=1\ \Rightarrow\ |z_1+z_2|^2=1",
                     font_size=29, color=T.text_primary)
        r3 = MathTex(r"2+2\,\mathrm{Re}(z_1\bar{z}_2)=1"
                     r"\ \Rightarrow\ \mathrm{Re}(z_1\bar{z}_2)=-\tfrac{1}{2}",
                     font_size=29, color=T.result_intermediate)
        r4 = MathTex(r"|z_1-z_2|^2=2-2\,\mathrm{Re}(z_1\bar{z}_2)=3"
                     r"\ \Rightarrow\ |z_i-z_j|=\sqrt{3}",
                     font_size=29, color=T.text_primary)
        r5 = MathTex(r"|z_1-z_2|^2+|z_2-z_3|^2+|z_3-z_1|^2"
                     r"=3+3+3=\mathbf{9}",
                     font_size=31, color=T.result_final)
        left = VGroup(r1, r2, r3, r4, r5)
        left.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(left, 7.6)

        if left.height > 6.0:

            left.scale_to_fit_height(6.0)

        left.next_to(rule, DOWN, buff=0.45)
        left.align_to(rule, LEFT).shift(RIGHT * 0.4)
        tracker = ValueTracker(0.35)
        R = 1.9
        cc = Circle(radius=R, color=T.auxiliary_geometry, stroke_width=2)
        cc.move_to(RIGHT * 4.1 + DOWN * 0.6)
        angles = [0.0, 2 * PI / 3, 4 * PI / 3]
        colors = [T.graph_point, T.graph_tangent, T.graph_secant]
        names = ["z1", "z2", "z3"]

        def pos(i):
            a = tracker.get_value() + angles[i]
            return cc.get_center() + R * np.array([np.cos(a), np.sin(a), 0])

        dots = []
        labels = []
        for i in range(3):
            d = Dot(color=colors[i], radius=0.1)
            d.add_updater(lambda m, i=i: m.move_to(pos(i)))
            t = Text(names[i], font_size=24, color=colors[i])
            t.add_updater(lambda m, i=i: m.next_to(dots[i], UP, buff=0.14))
            dots.append(d)
            labels.append(t)
        tri = always_redraw(lambda: Polygon(pos(0), pos(1), pos(2),
                                            color=T.graph_function,
                                            stroke_width=4))
        side_lab = MathTex(r"\text{each side}=\sqrt{3}", font_size=25,
                           color=T.graph_function)
        side_lab.next_to(cc, DOWN, buff=0.4)
        self.play(Write(r1), run_time=1.6)
        self.wait(4.6)
        self.play(Write(r2), Create(cc), run_time=1.4)
        self.wait(4.6)
        self.play(Write(r3), FadeIn(tri), FadeIn(dots[0]), FadeIn(dots[1]),
                  FadeIn(dots[2]), FadeIn(labels[0]), FadeIn(labels[1]),
                  FadeIn(labels[2]), run_time=1.8)
        self.wait(5.25)
        self.play(tracker.animate.set_value(0.35 + 2 * PI / 3), run_time=2.6)
        self.wait(3.94)
        self.play(Write(r4), Write(side_lab), run_time=1.6)
        self.wait(5.25)
        self.play(tracker.animate.set_value(0.35 + 4 * PI / 3), run_time=2.4)
        self.wait(3.28)
        self.play(Write(r5), run_time=1.2)
        box = SurroundingRectangle(r5, buff=0.16, color=T.result_final)
        self.play(Create(box), run_time=0.7)
        emphasize(self, r5, color=T.result_final, run_time=0.9)
        self.wait(6)
'''

SEG8 = r'''from manim import *


class Segment8(Scene):
    def construct(self):
        head = Text("PROBLEM 3 - ENTRY DETERRENCE (a)-(b)", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"P=100-Q,\quad MC_1=MC_2=10,\quad F=225",
                     font_size=29, color=T.constant)
        r2 = MathTex(r"\pi_2=(90-q_1-q_2)\,q_2-F",
                     font_size=29, color=T.text_primary)
        r3 = MathTex(r"\frac{\partial\pi_2}{\partial q_2}=0:\quad "
                     r"q_2(q_1)=\frac{90-q_1}{2}",
                     font_size=29, color=T.variable)
        r4 = MathTex(r"\pi_2^{\mathrm{entry}}=\frac{(90-q_1)^2}{4}-225",
                     font_size=29, color=T.text_primary)
        r5 = MathTex(r"\pi_2\le0\ \Leftrightarrow\ (90-q_1)^2\le900"
                     r"\ \Leftrightarrow\ q_1\ge60",
                     font_size=29, color=T.result_intermediate)
        r6 = MathTex(r"q_1^{\mathrm{lim}}=60", font_size=33,
                     color=T.result_final)
        left = VGroup(r1, r2, r3, r4, r5, r6)
        left.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(left, 7.6)

        if left.height > 6.0:

            left.scale_to_fit_height(6.0)

        left.next_to(rule, DOWN, buff=0.42)
        left.align_to(rule, LEFT).shift(RIGHT * 0.4)
        axes = Axes(x_range=[0, 90, 15], y_range=[0, 50, 10],
                    x_length=5.4, y_length=3.6,
                    axis_config={"color": T.text_muted, "stroke_width": 1.5,
                                 "include_tip": False})
        axes.move_to(RIGHT * 3.8 + DOWN * 0.9)
        x_lab = axes.get_x_axis_label(MathTex(r"q_1", font_size=26,
                                             color=T.text_secondary))
        y_lab = axes.get_y_axis_label(MathTex(r"q_2", font_size=26,
                                             color=T.text_secondary))
        br_line = Line(axes.c2p(0, 45), axes.c2p(90, 0),
                       color=T.graph_function, stroke_width=4)
        br_lab = MathTex(r"q_2=\frac{90-q_1}{2}", font_size=25,
                         color=T.graph_function)
        br_lab.next_to(axes.c2p(30, 30), UP, buff=0.35)
        zone = Polygon(axes.c2p(60, 0), axes.c2p(90, 0), axes.c2p(90, 50),
                       axes.c2p(60, 50), stroke_width=0,
                       fill_color=T.warning, fill_opacity=0.10)
        zone_lab = Text("entry blocked", font_size=22, color=T.warning)
        zone_lab.move_to(axes.c2p(75, 26))
        dot = Dot(axes.c2p(60, 15), color=T.graph_point, radius=0.1)
        dot_lab = MathTex(r"(60,\ 15):\ \pi_2=0", font_size=25,
                          color=T.graph_point)
        dot_lab.next_to(dot, DOWN, buff=0.3)
        self.play(Write(r1), run_time=1.6)
        self.wait(5.81)
        self.play(Write(r2), run_time=1.4)
        self.wait(5.08)
        self.play(Write(r3), Create(axes), Write(x_lab), Write(y_lab),
                  run_time=1.8)
        self.play(Create(br_line), Write(br_lab), run_time=1.4)
        self.wait(5.81)
        self.play(Write(r4), run_time=1.4)
        self.wait(5.81)
        self.play(Write(r5), FadeIn(zone), Write(zone_lab), run_time=1.6)
        self.wait(5.81)
        self.play(FadeIn(dot, scale=0.6), Write(dot_lab), run_time=0.9)
        self.play(Write(r6), run_time=1.0)
        box = SurroundingRectangle(r6, buff=0.16, color=T.result_final)
        self.play(Create(box), run_time=0.7)
        emphasize(self, r6, color=T.result_final, run_time=0.9)
        self.wait(6)
'''

SEG9 = r'''from manim import *


class Segment9(Scene):
    def construct(self):
        head = Text("3 (c)-(d) - DETER OR ACCOMMODATE?", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"\text{(c) accommodate: }q_1=45,\ q_2=22.5,"
                     r"\ P=32.5,\ \pi_1=1012.5",
                     font_size=27, color=T.text_primary)
        r2 = MathTex(r"\text{(c) deter: }q_1=60,\ P=40,"
                     r"\ \pi_1=(40-10)\times60=1800>1012.5",
                     font_size=27, color=T.result_final)
        r3 = MathTex(r"\text{(d) }q_1^{L}=90-2\sqrt{F},\qquad"
                     r"\ \pi_1^{\mathrm{det}}=180\sqrt{F}-4F",
                     font_size=27, color=T.variable)
        r4 = MathTex(r"180\sqrt{F}-4F>1012.5\ \Leftrightarrow\ F>43.4",
                     font_size=27, color=T.text_primary)
        r5 = MathTex(r"F\ge506.25:\ \text{blockaded monopoly},"
                     r"\ \pi_1=2025",
                     font_size=27, color=T.text_primary)
        r6 = MathTex(r"\text{deterrence optimal: }43.4\le F\le506.25",
                     font_size=29, color=T.result_final)
        left = VGroup(r1, r2, r3, r4, r5, r6)
        left.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit_width(left, 7.6)

        if left.height > 6.0:

            left.scale_to_fit_height(6.0)

        left.next_to(rule, DOWN, buff=0.42)
        left.align_to(rule, LEFT).shift(RIGHT * 0.4)
        axes = Axes(x_range=[0, 800, 200], y_range=[0, 2200, 500],
                    x_length=5.4, y_length=3.7,
                    axis_config={"color": T.text_muted, "stroke_width": 1.5,
                                 "include_tip": False})
        axes.move_to(RIGHT * 3.8 + DOWN * 0.85)
        x_lab = axes.get_x_axis_label(Text("F", font_size=24,
                                           color=T.text_secondary))
        y_lab = MathTex(r"\pi_1", font_size=26, color=T.text_secondary)
        y_lab.next_to(axes.y_axis.get_top(), LEFT, buff=0.2)
        curve = axes.plot(lambda F: 180 * np.sqrt(F) - 4 * F,
                          x_range=[0, 800], color=T.graph_function,
                          stroke_width=4)
        ref1 = DashedLine(axes.c2p(0, 1012.5), axes.c2p(800, 1012.5),
                          color=T.graph_reference, stroke_width=2)
        ref1_lab = MathTex(r"1012.5", font_size=22, color=T.graph_reference)
        ref1_lab.next_to(ref1, LEFT, buff=0.15).shift(DOWN * 0.25)
        band = Polygon(axes.c2p(43.4, 0), axes.c2p(506.25, 0),
                       axes.c2p(506.25, 2200), axes.c2p(43.4, 2200),
                       stroke_width=0, fill_color=T.stable_state,
                       fill_opacity=0.10)
        band_lab = Text("deterrence wins", font_size=20,
                        color=T.stable_state)
        band_lab.move_to(axes.c2p(230, 2060))
        dot = Dot(axes.c2p(225, 1800), color=T.graph_point, radius=0.1)
        dot_lab = MathTex(r"F=225:\ \pi_1=1800", font_size=23,
                          color=T.graph_point)
        dot_lab.next_to(dot, DOWN, buff=0.25).shift(LEFT * 0.5)
        self.play(Write(r1), run_time=1.8)
        self.wait(7.7)
        self.play(Write(r2), run_time=1.6)
        self.wait(7.7)
        self.play(Write(r3), Create(axes), Write(x_lab), Write(y_lab),
                  Create(curve), run_time=2.2)
        self.wait(6.84)
        self.play(Write(r4), Create(ref1), Write(ref1_lab), run_time=1.6)
        self.wait(6.84)
        self.play(Write(r5), FadeIn(band), Write(band_lab), run_time=1.6)
        self.wait(7.7)
        self.play(FadeIn(dot, scale=0.6), Write(dot_lab), run_time=0.9)
        self.play(Write(r6), run_time=1.2)
        box = SurroundingRectangle(r6, buff=0.16, color=T.result_final)
        self.play(Create(box), run_time=0.7)
        emphasize(self, r6, color=T.result_final, run_time=0.9)
        self.wait(6)
'''

SEG10 = r'''from manim import *


class Segment10(Scene):
    def construct(self):
        head = Text("3 (e)-(f) - WELFARE AND COURNOT", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        h_det = Text("deterrence", font_size=22, color=T.stable_state)
        t_det = MathTex(r"Q=60,\ P=40\ \Rightarrow\ CS=1800,"
                        r"\ \pi_1=1800,\ W=3600",
                        font_size=27, color=T.text_primary)
        h_acc = Text("accommodation", font_size=22, color=T.graph_function)
        t_acc = MathTex(r"Q=67.5,\ P=32.5\ \Rightarrow\ CS=2278,"
                        r"\ \pi_1+\pi_2=1294,\ W=3572",
                        font_size=27, color=T.text_primary)
        cmp_row = MathTex(r"CS:\ -478,\qquad W:\ +28\ \text{(entry cost saved)}",
                          font_size=27, color=T.result_intermediate)
        concl = Text("consumers lose, total welfare gains slightly - "
                     "not harmful in total",
                     font_size=24, color=T.text_secondary)
        rf = MathTex(r"\text{(f) Cournot: }q_1=q_2=30,\ P=40,"
                     r"\ \pi_2=900-225=675>0\ \Rightarrow\ \text{enters}",
                     font_size=27, color=T.result_final)
        left = VGroup(h_det, t_det, h_acc, t_acc, cmp_row, concl, rf)
        left.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        fit_width(left, 8.2)

        if left.height > 6.0:

            left.scale_to_fit_height(6.0)

        left.next_to(rule, DOWN, buff=0.42)
        left.align_to(rule, LEFT).shift(RIGHT * 0.4)
        box = SurroundingRectangle(rf, buff=0.13, color=T.result_final)
        axes = Axes(x_range=[0, 60, 15], y_range=[0, 45, 15],
                    x_length=3.6, y_length=3.2,
                    axis_config={"color": T.text_muted, "stroke_width": 1.5,
                                 "include_tip": False})
        axes.move_to(RIGHT * 4.0 + DOWN * 0.9)
        l1 = Line(axes.c2p(0, 45), axes.c2p(60, 15),
                  color=T.graph_function, stroke_width=3.5)
        l2 = Line(axes.c2p(22.5, 45), axes.c2p(45, 0),
                  color=T.graph_tangent, stroke_width=3.5)
        dot = Dot(axes.c2p(30, 30), color=T.graph_point, radius=0.1)
        dot_lab = MathTex(r"(30,\ 30)", font_size=24, color=T.graph_point)
        dot_lab.next_to(dot, DOWN, buff=0.2)
        lab1 = Text("firm 2 BR", font_size=18, color=T.graph_function)
        lab1.move_to(axes.c2p(9, 35))
        lab2 = Text("firm 1 BR", font_size=18, color=T.graph_tangent)
        lab2.move_to(axes.c2p(36, 40))
        self.play(FadeIn(h_det, shift=0.2 * UP), Write(t_det), run_time=1.8)
        self.wait(11.45)
        self.play(FadeIn(h_acc, shift=0.2 * UP), Write(t_acc), run_time=1.8)
        self.wait(11.45)
        self.play(Write(cmp_row), run_time=1.6)
        self.wait(10.41)
        self.play(Write(concl), run_time=1.4)
        self.wait(8.33)
        self.play(Write(rf), Create(axes), Create(l1), Create(l2),
                  FadeIn(dot), Write(dot_lab), Write(lab1), Write(lab2),
                  run_time=2.4)
        self.play(Create(box), run_time=0.7)
        emphasize(self, rf, color=T.result_final, run_time=0.9)
        self.wait(6)
'''

SEG11 = r'''from manim import *


class Segment11(Scene):
    def construct(self):
        head = Text("THE HARD PROBLEM SET - ALL ANSWERS", font_size=26,
                    color=T.highlight_secondary)
        head.to_edge(UP, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        a1 = MathTex(r"\mathbf{1A}:\ Q=9.0\times10^{-8}\gg K_{sp}"
                     r"\Rightarrow\text{ ppt};\ [\mathrm{NH_4Cl}]=0.082"
                     r"\ \mathrm{M};\ \mathrm{pH}=9.0",
                     font_size=27, color=T.text_primary)
        a2 = MathTex(r"\mathbf{1B}:\ [\mathrm{Cu}^{2+}]=10^{-14};"
                     r"\ E_R=-0.074;\ E_{\mathrm{cell}}=0.384\ \mathrm{V};"
                     r"\ \Delta G=-74\ \mathrm{kJ};\ K=10^{13};"
                     r"\ +36\ \mathrm{mV}",
                     font_size=27, color=T.text_primary)
        a3 = MathTex(r"\mathbf{2A}:\ \dfrac{\pi\ln 2}{8}\approx0.272",
                     font_size=27, color=T.text_primary)
        a4 = MathTex(r"\mathbf{2B}:\ \dfrac{4}{e}\approx1.47",
                     font_size=27, color=T.text_primary)
        a5 = MathTex(r"\mathbf{2C}:\ 8104", font_size=27,
                     color=T.text_primary)
        a6 = MathTex(r"\mathbf{2D}:\ \text{equilateral};\ \Sigma|z_i-z_j|^2=9",
                     font_size=27, color=T.text_primary)
        a7 = MathTex(r"\mathbf{3}:\ q_1^{\mathrm{lim}}=60;"
                     r"\ \pi_1=1800\ \text{vs}\ 1012.5;"
                     r"\ 43.4\le F\le506.25;"
                     r"\ W:\ 3600\ \text{vs}\ 3572;"
                     r"\ \text{Cournot enters}",
                     font_size=27, color=T.text_primary)
        rows = VGroup(a1, a2, a3, a4, a5, a6, a7)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        rows.move_to(DOWN * 0.4)
        fit_width(rows, 12.9)
        thanks = Text("thanks for watching", font_size=24, color=T.text_muted)
        thanks.to_edge(DOWN, buff=0.35)
        b1 = SurroundingRectangle(a1, buff=0.12, color=T.result_final)
        b2 = SurroundingRectangle(a2, buff=0.12, color=T.result_final)
        b3 = SurroundingRectangle(a3, buff=0.12, color=T.result_final)
        b4 = SurroundingRectangle(a4, buff=0.12, color=T.result_final)
        b5 = SurroundingRectangle(a5, buff=0.12, color=T.result_final)
        b6 = SurroundingRectangle(a6, buff=0.12, color=T.result_final)
        b7 = SurroundingRectangle(a7, buff=0.12, color=T.result_final)
        self.play(FadeIn(head, shift=0.3 * DOWN), Create(rule), run_time=0.9)
        self.wait(2.38)
        self.play(FadeIn(a1, shift=0.25 * RIGHT), Create(b1), run_time=1.2)
        self.wait(5.48)
        self.play(FadeIn(a2, shift=0.25 * RIGHT), Create(b2), run_time=1.2)
        self.wait(5.48)
        self.play(FadeIn(a3, shift=0.25 * RIGHT), Create(b3), run_time=1.2)
        self.wait(5.48)
        self.play(FadeIn(a4, shift=0.25 * RIGHT), Create(b4), run_time=1.2)
        self.wait(5.48)
        self.play(FadeIn(a5, shift=0.25 * RIGHT), Create(b5), run_time=1.2)
        self.wait(5.48)
        self.play(FadeIn(a6, shift=0.25 * RIGHT), Create(b6), run_time=1.2)
        self.wait(5.48)
        self.play(FadeIn(a7, shift=0.25 * RIGHT), Create(b7), run_time=1.2)
        self.wait(5.48)
        self.wait(2.86)
        self.play(FadeIn(thanks, shift=0.3 * UP), run_time=0.9)
        self.wait(6)
'''

SEGMENTS = [
    {
        "narration":
            "Problem 1 A. A solution holds zero point one zero molar magnesium "
            "chloride and zero point zero five zero molar ammonia. Does "
            "magnesium hydroxide precipitate? Ammonia is a weak base. It "
            "ionises: N H three plus water gives N H four plus and O H minus, "
            "with K B equal to one point eight times ten to the minus five. "
            "Since the base is weak, the hydroxide concentration is the square "
            "root of K B times the concentration: about nine point five times "
            "ten to the minus four molar. Now compare. The ion product Q is "
            "magnesium times hydroxide squared: zero point one zero times that "
            "square, nine point zero times ten to the minus eight. K S P is "
            "only one point two times ten to the minus eleven. Q is thousands "
            "of times larger, so magnesium hydroxide precipitates.",
        "visual": {
            "objective": "show the ammonia ionisation, the hydroxide level, "
                         "and the Q versus Ksp verdict",
            "transition": "slide-up",
            "visual_elements": ["data", "NH3 equilibrium", "hydroxide calc",
                                "Q vs Ksp bars", "beaker with precipitate"],
            "diagram": "apparatus",
            "highlight": ["the ion product Q", "Ksp", "the verdict"],
            "color_roles": {"Q": "warning", "Ksp": "constant",
                            "verdict": "result_final",
                            "precipitate": "text_primary"},
            "animation_beats": ["write the data", "write the equilibrium",
                                "solve for hydroxide", "compute Q",
                                "compare bars", "box the verdict",
                                "precipitate falls"],
            "layout": "working left, beaker right",
            "outcome": "Q = 9.0e-8 far exceeds Ksp, so Mg(OH)2 precipitates",
        },
        "code": SEG0,
    },
    {
        "narration":
            "How much ammonium chloride just prevents the precipitate? On the "
            "verge, the ion product equals K S P, so hydroxide must fall to "
            "the square root of K S P over zero point one zero: one point one "
            "times ten to the minus five molar. The ammonia equilibrium still "
            "holds, and K B ties hydroxide to ammonium: ammonium must rise to "
            "K B times zero point zero five zero, divided by that hydroxide, "
            "about zero point zero eight two molar. That is the minimum "
            "ammonium chloride. At the threshold the p O H is four point nine "
            "six, so the final p H is nine point zero. Why does ammonium work? "
            "It is the common ion: it floods the ammonia equilibrium, pushes "
            "it backwards, suppresses the ionisation, and hydroxide drops "
            "below the precipitation threshold.",
        "visual": {
            "objective": "derive the buffer condition, the minimum NH4Cl, "
                         "the final pH, and the common-ion effect",
            "transition": "carry-over",
            "visual_elements": ["threshold hydroxide", "buffer equation",
                                "minimum NH4Cl", "pH", "shrinking OH bar"],
            "diagram": "none",
            "highlight": ["the minimum NH4Cl", "the pH",
                          "the common-ion shift"],
            "dynamic": ["the hydroxide bar shrinks below the threshold as "
                        "NH4+ is added"],
            "color_roles": {"threshold": "cancel_mark", "NH4": "constant",
                            "OH": "vector_gravity", "verdict": "result_final"},
            "animation_beats": ["threshold hydroxide", "buffer relation",
                                "solve for NH4+", "box the minimum",
                                "compute pH", "shift the equilibrium",
                                "shrink the bar"],
            "layout": "working left, live bar right",
            "outcome": "0.082 M NH4Cl is the minimum; pH 9.0; common-ion "
                       "effect suppresses OH-",
        },
        "code": SEG1,
    },
    {
        "narration":
            "Problem one B: a copper concentration cell with complexation on "
            "the right. The right half-cell holds zero point one zero molar "
            "tetra-ammine copper two plus in one molar ammonia, and the "
            "formation constant is ten to the thirteen. Free copper two plus "
            "equals the complex concentration divided by K F times ammonia to "
            "the fourth: one times ten to the minus fourteen molar. Now the "
            "Nernst equation for the copper couple: E equals zero point three "
            "four plus zero point zero two nine six, times log of copper two "
            "plus. On the right, that is zero point three four minus zero "
            "point four one four: minus zero point zero seven four volts. On "
            "the left, plain zero point one molar copper two plus: plus zero "
            "point three one volts.",
        "visual": {
            "objective": "find the free Cu2+ from Kf and both electrode "
                         "potentials from the Nernst equation",
            "transition": "fade",
            "visual_elements": ["formation constant", "free Cu2+",
                                "Nernst equation", "two half-cells"],
            "diagram": "apparatus",
            "highlight": ["the free Cu2+", "both electrode potentials"],
            "color_roles": {"complex": "variable", "freeCu": "result_final",
                            "electrode": "vector_acceleration"},
            "animation_beats": ["write Kf", "solve free Cu2+",
                                "draw the cell", "Nernst right",
                                "Nernst left"],
            "layout": "working left, cell diagram right",
            "outcome": "free Cu2+ is 1.0e-14 M; ER = -0.074 V, EL = +0.310 V",
        },
        "code": SEG2,
    },
    {
        "narration":
            "Which electrode is which? The right side sits at the lower "
            "potential, so it is the anode: copper dissolves into the ammonia "
            "as the ammine complex and releases electrons. The left electrode "
            "is the cathode: copper two plus plates onto it. The cell "
            "potential is cathode minus anode: zero point three one zero minus "
            "minus zero point zero seven four, which is zero point three "
            "eight four volts. Free energy: delta G equals minus n F E, that "
            "is minus two times ninety six four eight five times zero point "
            "three eight four, about minus seventy four point one kilojoules "
            "per mole. The two electrode reactions add to pure complexation: "
            "copper two plus plus four ammonia gives the complex, so the "
            "overall equilibrium constant is just K F, ten to the thirteen. "
            "If ammonia is doubled, free copper two plus falls sixteen-fold to "
            "six point three times ten to the minus sixteen, and E cell rises "
            "by thirty six millivolts, to zero point four two zero volts.",
        "visual": {
            "objective": "identify anode and cathode, compute Ecell, dG and "
                         "K, and the effect of doubling NH3",
            "transition": "carry-over",
            "visual_elements": ["anode and cathode labels",
                                "electron flow arrow", "half-reactions",
                                "Ecell", "dG", "K = Kf", "NH3 doubling"],
            "diagram": "apparatus",
            "highlight": ["Ecell = 0.384 V", "K = Kf", "the +36 mV shift"],
            "color_roles": {"anode": "warning", "cathode": "stable_state",
                            "electrons": "constant",
                            "results": "result_final"},
            "animation_beats": ["redraw the cell", "label anode and cathode",
                                "electron arrow", "half-reactions",
                                "Ecell", "dG", "K = Kf", "double NH3"],
            "layout": "working left, cell diagram right",
            "outcome": "Ecell = 0.384 V, dG = -74.1 kJ, K = Kf = 1e13, "
                       "doubling NH3 adds 36 mV",
        },
        "code": SEG3,
    },
    {
        "narration":
            "Problem two A: the integral from zero to one of l n of one plus "
            "x, over one plus x squared. Substitute x equals tan theta. Then "
            "d x is secant squared theta, the denominator eats the secant "
            "squared, and theta runs from zero to pi over four: the integral "
            "becomes l n of one plus tan theta. The key step: one plus tan "
            "theta is sine plus cosine over cosine, which is root two cosine "
            "of theta minus pi over four, over cosine theta. So the integral "
            "splits: half of l n two times pi over four, plus the integral of "
            "l n cosine at theta minus pi over four, minus the integral of l n "
            "cosine at theta. Shift the first by pi over four and the two "
            "cosine integrals are identical. They cancel, and what survives "
            "is pi over eight times l n two, about zero point two seven two.",
        "visual": {
            "objective": "derive the tangent substitution, split the "
                         "integral, cancel the cosine terms, and show the "
                         "area under the curve",
            "transition": "fade",
            "visual_elements": ["substitution", "trig identity",
                                "three-part split", "cancellation",
                                "Riemann rectangles"],
            "diagram": "graph",
            "highlight": ["the two cosine integrals", "the final area"],
            "cancellation": True,
            "integration": True,
            "color_roles": {"integral": "variable", "curve": "graph_function",
                             "area": "result_final"},
            "animation_beats": ["write the integral", "substitute tan",
                                "split the log", "Riemann rectangles",
                                "shift and cancel", "box the answer"],
            "layout": "derivation left, graph right",
            "outcome": "I = pi ln 2 over 8, about 0.272",
        },
        "code": SEG4,
    },
    {
        "narration":
            "Problem two B: one over n, times the n-th root of two n "
            "factorial over n factorial. Take the logarithm: one over n times "
            "the sum from k equals n plus one to two n of l n k, which is a "
            "Riemann sum. Write k as n times t: the sum becomes l n n, plus "
            "one over n times the sum of l n t, and that tends to l n n plus "
            "the integral from one to two of l n t. The integral is two l n "
            "two minus one. Exponentiate: the n-th root grows like n times e "
            "to the two l n two minus one, which is n times four over e. "
            "Stirling's formula agrees exactly. Divide by n and the answer is "
            "four over e, about one point four seven.",
        "visual": {
            "objective": "turn the factorial into a Riemann sum for ln t, "
                         "evaluate the integral, and read off 4/e",
            "transition": "carry-over",
            "visual_elements": ["log of factorial", "Riemann sum",
                                "integral of ln t", "Stirling check",
                                "Riemann rectangles"],
            "diagram": "graph",
            "highlight": ["the integral 2 ln 2 - 1", "the final 4/e"],
            "integration": True,
            "color_roles": {"limit": "variable", "curve": "graph_function",
                             "area": "result_final"},
            "animation_beats": ["write the limit", "log the factorial",
                                "Riemann sum", "evaluate the integral",
                                "exponentiate", "box 4/e", "Stirling"],
            "layout": "derivation left, graph right",
            "outcome": "L = 4/e, about 1.47",
        },
        "code": SEG5,
    },
    {
        "narration":
            "Problem two C: P is monic of degree four, with P of one equal "
            "ten, P of two equal twenty, P of three equal thirty. Find P of "
            "ten plus P of minus six. Subtract the known part: Q of x equals "
            "P of x minus ten x is still monic, and it vanishes at one, two "
            "and three, so Q factors as x minus one, x minus two, x minus "
            "three, times x minus r, with one root r still free. At ten, "
            "nine eight seven give five oh four, so P of ten is five oh four "
            "times ten minus r, plus one hundred. At minus six, minus seven "
            "minus eight minus nine give minus five oh four, so P of minus "
            "six is five oh four times six plus r, minus sixty. Add them: the "
            "r terms cancel exactly, leaving five oh four times sixteen, plus "
            "forty: eight thousand, one hundred and four. Unique, whatever r "
            "is.",
        "visual": {
            "objective": "factor Q = P - 10x with a free root r and show "
                         "the r-terms cancel in P(10) + P(-6)",
            "transition": "fade",
            "visual_elements": ["Q = P - 10x", "factorisation",
                                "evaluation at 10 and -6", "cancellation",
                                "number line of roots"],
            "diagram": "geometry",
            "highlight": ["the free root r", "the cancellation", "8104"],
            "cancellation": True,
            "color_roles": {"roots": "variable", "r": "warning",
                             "answer": "result_final"},
            "animation_beats": ["write the values", "form Q", "factor Q",
                                "draw the roots", "evaluate at 10",
                                "evaluate at -6", "cancel r", "box 8104"],
            "layout": "derivation left, number line right",
            "outcome": "P(10) + P(-6) = 8104, independent of r",
        },
        "code": SEG6,
    },
    {
        "narration":
            "Problem two D: three complex numbers, each of modulus one, "
            "adding to zero. Then z one plus z two equals minus z three, "
            "which also has modulus one. Square the magnitude: two plus two "
            "times the real part of z one z two bar equals one, so that real "
            "part is minus one half, for every pair. Now the distance: the "
            "squared distance between z one and z two is two minus two times "
            "minus one half, which is three. Every side is root three. Three "
            "points on the unit circle with all sides root three form an "
            "equilateral triangle: the central angles are all one hundred "
            "and twenty degrees. The sum of the three squared sides is three "
            "plus three plus three, nine. Watch the triangle stay "
            "equilateral as it rotates.",
        "visual": {
            "objective": "prove Re(z1 conj z2) = -1/2, hence all sides "
                         "sqrt 3, and show the live equilateral triangle",
            "transition": "fade",
            "visual_elements": ["modulus equation", "real-part identity",
                                "side length", "rotating unit-circle "
                                "triangle"],
            "diagram": "geometry",
            "highlight": ["Re(z1 z2bar) = -1/2", "each side = sqrt 3",
                          "the sum 9"],
            "dynamic": ["the triangle stays equilateral while the tracker "
                        "rotates it around the unit circle"],
            "color_roles": {"points": "graph_point", "triangle":
                            "graph_function", "answer": "result_final"},
            "animation_beats": ["write the conditions", "modulus argument",
                                "real part", "side length",
                                "rotate the triangle", "box the sum 9"],
            "layout": "derivation left, live triangle right",
            "outcome": "equilateral triangle; sum of squared sides = 9",
        },
        "code": SEG7,
    },
    {
        "narration":
            "Problem three: entry deterrence. Demand is P equals one hundred "
            "minus Q; both firms have marginal cost ten; the entrant pays a "
            "fixed cost of two twenty five, sunk on entry. Firm two observes "
            "q one, then chooses q two. Its profit is ninety minus q one "
            "minus q two, times q two, minus the fixed cost. Maximising, the "
            "best response is q two equals ninety minus q one, over two, and "
            "entry profit is ninety minus q one, squared over four, minus "
            "two twenty five. Entry is just deterred when that profit is "
            "zero: ninety minus q one squared at most nine hundred, so q one "
            "at least sixty. The limit quantity is sixty: produce sixty, and "
            "the entrant stays out.",
        "visual": {
            "objective": "derive the follower best response and the limit "
                         "quantity on the best-response graph",
            "transition": "fade",
            "visual_elements": ["profit function", "best response",
                                "entry profit", "best-response graph"],
            "diagram": "graph",
            "highlight": ["the best-response line", "the (60, 15) point",
                          "the blocked region"],
            "color_roles": {"demand": "constant", "BR": "graph_function",
                             "limit": "result_final"},
            "animation_beats": ["write the data", "write profit",
                                "best response", "draw the BR line",
                                "entry profit", "shade the blocked region",
                                "mark (60, 15)", "box q1 = 60"],
            "layout": "derivation left, graph right",
            "outcome": "q2 = (90 - q1)/2; smallest deterring q1 is 60",
        },
        "code": SEG8,
    },
    {
        "narration":
            "Now compare the incumbent's options. Accommodate: firm one "
            "leads, firm two follows. The Stackelberg leader takes "
            "forty five, the follower twenty two and a half, price thirty "
            "two point five, and firm one earns one thousand and twelve "
            "point five. Deter with sixty: price forty, profit thirty times "
            "sixty, one thousand eight hundred. Deterrence wins by nearly "
            "eight hundred. For a general fixed cost F, the limit quantity "
            "is ninety minus two root F, and deterrence profit becomes one "
            "eighty root F minus four F. That beats accommodation once F "
            "passes about forty three. But past F equals five hundred and "
            "six, entry is blockaded anyway: plain monopoly earns two "
            "thousand and twenty five, and chasing entrants only wastes "
            "output. So the deterrence regime is forty three up to five "
            "hundred and six, and at two twenty five, deterrence is the "
            "answer.",
        "visual": {
            "objective": "compare Stackelberg accommodation with "
                         "deterrence, then locate the F-range where "
                         "deterrence is optimal",
            "transition": "carry-over",
            "visual_elements": ["Stackelberg quantities", "deterrence "
                                "profit", "pi1 as a function of F",
                                "profit-versus-F graph"],
            "diagram": "graph",
            "highlight": ["1012.5 versus 1800", "the crossing at F = 43.4",
                          "the deterrence band"],
            "color_roles": {"accommodate": "text_primary",
                             "deter": "result_final",
                             "curve": "graph_function",
                             "band": "stable_state"},
            "animation_beats": ["accommodation profit", "deterrence profit",
                                "plot pi1(F)", "reference line 1012.5",
                                "blockade threshold", "mark F = 225",
                                "box the F-range"],
            "layout": "derivation left, graph right",
            "outcome": "deterrence beats accommodation; optimal for "
                       "43.4 <= F <= 506.25",
        },
        "code": SEG9,
    },
    {
        "narration":
            "Was deterrence socially harmful? Under deterrence the market "
            "makes sixty units at price forty: consumer surplus is half of "
            "sixty times sixty, one thousand eight hundred; profit is also "
            "one thousand eight hundred; total welfare three thousand six "
            "hundred. Under accommodation output rises to sixty seven and a "
            "half at thirty two point five: consumer surplus two thousand "
            "two hundred seventy eight, and profits one thousand two "
            "hundred ninety four net of the entry cost, giving welfare three "
            "thousand five hundred seventy two. So deterrence actually "
            "raises total welfare slightly, because it saves the two twenty "
            "five entry cost and sacrifices only a little output; but "
            "consumers lose almost five hundred, and surplus shifts to the "
            "incumbent. Finally, without commitment, simultaneous Cournot: "
            "each firm makes thirty, price forty, and the entrant's profit "
            "is nine hundred minus two twenty five, six hundred seventy "
            "five, still positive, so firm two enters.",
        "visual": {
            "objective": "compare consumer surplus and total welfare under "
                         "deterrence versus accommodation, then solve the "
                         "Cournot case",
            "transition": "carry-over",
            "visual_elements": ["welfare table", "CS comparison",
                                "Cournot crossing", "entrant profit"],
            "diagram": "graph",
            "highlight": ["W = 3600 versus 3572",
                          "the entrant's positive profit"],
            "color_roles": {"deterrence": "stable_state",
                             "accommodation": "graph_function",
                             "cournot": "result_final"},
            "animation_beats": ["deterrence table", "accommodation table",
                                "CS and welfare comparison",
                                "Cournot best responses", "mark (30, 30)",
                                "box the entry verdict"],
            "layout": "tables left, Cournot graph right",
            "outcome": "welfare 3600 vs 3572; Cournot with F = 225 still "
                       "entering",
        },
        "code": SEG10,
    },
    {
        "narration":
            "The whole set, answered. One A: Q equals nine times ten to the "
            "minus eight beats K S P, so magnesium hydroxide precipitates; "
            "zero point zero eight two molar ammonium chloride just holds it "
            "back; the solution settles at p H nine. One B: free copper two "
            "plus ten to the minus fourteen; the complex side is the anode at "
            "minus zero point zero seven volts; E cell zero point three "
            "eight four volts, delta G minus seventy four kilojoules, K "
            "equals K F, and doubling ammonia adds thirty six millivolts. "
            "Two A: pi l n two over eight. Two B: four over e. Two C: eight "
            "thousand one hundred and four. Two D: equilateral, squared "
            "sides summing to nine. Three: deter with sixty and earn one "
            "thousand eight hundred; optimal from forty three to five "
            "hundred and six; welfare slightly favours deterrence; and "
            "Cournot still enters. Thanks for watching.",
        "visual": {
            "objective": "recap every final answer of the problem set",
            "transition": "answer-reveal",
            "visual_elements": ["answer checklist"],
            "diagram": "none",
            "highlight": ["each boxed answer"],
            "color_roles": {"answers": "result_final"},
            "animation_beats": ["1A", "1B", "2A", "2B", "2C", "2D", "3",
                                "thanks"],
            "layout": "single checklist, no overlaps",
            "outcome": "all seven problems answered and boxed",
        },
        "code": SEG11,
    },
]

LECTURE = {
    "title": TITLE,
    "preset": "lab",
    "format": "mixed",
    "question": QUESTION,
    "question_code": QUESTION_CODE,
    "segments": SEGMENTS,
}
