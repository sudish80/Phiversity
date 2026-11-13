"""Bundled lecture: three intersecting charged spheres with cavities and a cube.

A worked electrostatics problem, built as a hand-authored Phiversity lecture
(Manim scenes + voice-over). Every number on screen and in the narration comes
from charged_spheres_data, which holds the output of an independent numerical
solver (Coulomb sums on a 0.05 m voxel grid) and exact inclusion-exclusion
volumes.

Priority rule used throughout: cube > cavities > union of spheres > vacuum.
"""

from __future__ import annotations

from . import charged_spheres_data as D

V = D.VOLUMES
QS = D.Q_ERR[-1][1]


def _f(x, n=2):
    return f"{x:.{n}f}"


def _sci(x):
    m, e = f"{x:.1e}".split("e")
    return f"{m} times ten to the minus {abs(int(e))}"


TITLE = "Three Intersecting Charged Spheres"

QUESTION = {
    "display": "Three uniformly charged spheres of radius $R=3\\,\\mathrm{m}$ "
               "centred at $(0,0,0)$, $(2,0,0)$ and $(0,2,0)$ overlap. The body "
               "has a hollow cavity $a=1\\,\\mathrm{m}$ at the origin, a "
               "hemispherical cavity in $S_2$ ($z<0$) and a charged cube. "
               "Find $Q$, $\\phi$ and $\\mathbf E$, verify Maxwell's equations "
               "and validate with Gauss's law.",
    "speech": "Three uniformly charged spheres, each of radius three metres, "
              "are centred at the origin, at two on the x axis, and at two on "
              "the y axis. The composite body has a hollow spherical cavity of "
              "radius one metre at the origin, a hemispherical cavity in the "
              "second sphere where z is negative, and a charged cube of side "
              "one metre. Find the total charge, the potential and the electric "
              "field, verify Maxwell's equations, and validate the result with "
              "Gauss's law.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION", font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.2)
        line = Underline(badge, buff=0.15)
        r1 = Text("Three uniformly charged spheres, radius 3 m, intersect.",
                  font_size=26, color=T.text_primary)
        r2 = MathTex(r"C_1=(0,0,0),\ C_2=(2,0,0),\ C_3=(0,2,0)",
                     font_size=30, color=T.constant)
        r3 = Text("Hollow cavity a = 1 m at C1, hemispherical cavity (z < 0) in S2,",
                  font_size=24, color=T.text_primary)
        r4 = Text("and a charged cube of side 1 m centred at (2, 0, 1).",
                  font_size=24, color=T.text_primary)
        r5 = Text("Find Q, the potential and E. Verify Maxwell. Validate with Gauss.",
                  font_size=24, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r5).arrange(DOWN, buff=0.26)
        rows.move_to(UP * 1.2)
        c1 = Circle(radius=0.9, color=T.variable, stroke_width=4)
        c2 = c1.copy().set_color(T.constant).shift(RIGHT * 0.9)
        c3 = c1.copy().set_color(T.highlight_secondary).shift(RIGHT * 0.45 + UP * 0.8)
        venn = VGroup(c1, c2, c3).move_to(DOWN * 2.1)
        cube = Square(side_length=0.3, color=T.warning, stroke_width=4)
        cube.move_to(c2.get_center() + UP * 0.2)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(Write(r1), run_time=1.8)
        self.play(Write(r2), run_time=1.6)
        self.play(Write(r3), Write(r4), run_time=2.4)
        self.play(Write(r5), run_time=1.6)
        self.play(Create(c1), Create(c2), Create(c3), run_time=1.6)
        self.play(Create(cube), run_time=0.6)
        self.wait(5.0)
        self.play(FadeOut(VGroup(venn, cube)), run_time=0.7)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.72).to_edge(UP, buff=0.25), run_time=1.0)
        self.wait(1.0)
'''

# ---------------------------------------------------------------------------
# Manim code of the segments (numbers are substituted from the data module)
# ---------------------------------------------------------------------------

SEG0 = r'''from manim import *


class Segment0(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=66 * DEGREES, theta=-58 * DEGREES)
        K = 0.5
        axes = ThreeDAxes(x_range=[-3, 5, 1], y_range=[-3, 5, 1],
                          z_range=[-3, 3, 1], x_length=8 * K, y_length=8 * K,
                          z_length=6 * K,
                          axis_config={"color": T.text_muted, "stroke_width": 1.5,
                                       "include_ticks": False, "include_tip": False})

        def ball(c, r, color, op, v_range=None, res=(9, 16), sw=0.5):
            kw = dict(center=axes.c2p(*c), radius=r * K, resolution=res,
                      fill_opacity=op, stroke_width=sw, stroke_color=color,
                      checkerboard_colors=[color, color])
            if v_range is not None:
                kw["v_range"] = v_range
            return Sphere(**kw)

        s1 = ball((0, 0, 0), 3, T.variable, 0.10)
        s2 = ball((2, 0, 0), 3, T.constant, 0.10)
        s3 = ball((0, 2, 0), 3, T.highlight_secondary, 0.10)
        cav = ball((0, 0, 0), 1, T.text_primary, 0.35, res=(7, 12), sw=0.8)
        hemi = ball((2, 0, 0), 3, T.result_intermediate, 0.30, v_range=[0, PI / 2],
                    res=(7, 14), sw=0.8)
        cube = Cube(side_length=K, fill_color=T.warning, fill_opacity=0.9,
                    stroke_color=T.text_primary, stroke_width=2)
        cube.move_to(axes.c2p(2, 0, 1))
        world = VGroup(axes, s1, s2, s3, cav, hemi, cube)
        world.shift(RIGHT * 2.7)

        head = Text("(a) Geometric model", font_size=30, color=T.text_secondary)
        head.to_corner(UL, buff=0.4)
        eqs = [
            MathTex(r"S_1:\ x^2+y^2+z^2\le 9", font_size=30, color=T.variable),
            MathTex(r"S_2:\ (x-2)^2+y^2+z^2\le 9", font_size=30, color=T.constant),
            MathTex(r"S_3:\ x^2+(y-2)^2+z^2\le 9", font_size=30,
                    color=T.highlight_secondary),
            MathTex(r"A:\ x^2+y^2+z^2<1\quad(\text{hollow})", font_size=30,
                    color=T.text_primary),
            MathTex(r"B:\ (x-2)^2+y^2+z^2\le 9,\ z<0", font_size=30,
                    color=T.result_intermediate),
            MathTex(r"\text{cube}:\ |x-2|,\ |y|,\ |z-1|\le \tfrac12", font_size=30,
                    color=T.warning),
        ]
        stack = VGroup(*eqs).arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        stack.next_to(head, DOWN, buff=0.55).align_to(head, LEFT)
        fit_width(stack, 6.2)
        self.add_fixed_in_frame_mobjects(head, *eqs)
        self.remove(head, *eqs)
        self.play(FadeIn(head), Create(axes), run_time=1.2)
        self.play(DrawBorderThenFill(s1), FadeIn(eqs[0]), run_time=2.0)
        self.wait(1.2)
        self.play(DrawBorderThenFill(s2), DrawBorderThenFill(s3),
                  FadeIn(eqs[1]), FadeIn(eqs[2]), run_time=2.4)
        self.wait(2.0)
        self.play(DrawBorderThenFill(cav), FadeIn(eqs[3]), run_time=1.6)
        self.wait(1.6)
        self.play(DrawBorderThenFill(hemi), FadeIn(eqs[4]), run_time=1.6)
        self.wait(1.6)
        self.play(FadeIn(cube, scale=1.6), FadeIn(eqs[5]), run_time=1.6)
        self.play(Indicate(cube, color=T.warning, scale_factor=1.3), run_time=1.0)
        orbit_start(self, rate=0.10)
        self.wait(5.0)
        orbit_stop(self)
        self.wait(1.0)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("(b) Volume charge density", font_size=30, color=T.text_secondary)
        head.to_corner(UL, buff=0.4)
        self.play(FadeIn(head), run_time=0.6)
        lab = Text("priority rule", font_size=22, color=T.text_muted)
        spec = [(r"\mathbf{1}\ \ \text{cube}\ \Rightarrow\ \rho_c", T.warning),
                (r"\mathbf{2}\ \ \text{cavities } A,B\ \Rightarrow\ 0", T.text_primary),
                (r"\mathbf{3}\ \ S_1\cup S_2\cup S_3\ \Rightarrow\ \rho_0", T.variable),
                (r"\mathbf{4}\ \ \text{everything else}\ \Rightarrow\ 0", T.text_muted)]
        rows = VGroup(*[MathTex(s, font_size=30, color=c) for s, c in spec])
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.26)
        lab.next_to(head, DOWN, buff=0.45).align_to(head, LEFT)
        rows.next_to(lab, DOWN, buff=0.25).align_to(head, LEFT)
        self.play(FadeIn(lab), run_time=0.5)
        for r in rows:
            self.play(Write(r), run_time=1.2)
            self.wait(0.6)
        self.wait(0.6)
        pw = MathTex(r"\rho_v(x,y,z)=\begin{cases}"
                     r"\rho_c & \text{in the cube}\\"
                     r"0 & \text{in } A\cup B\\"
                     r"\rho_0 & \text{in } (S_1\cup S_2\cup S_3)\setminus(A\cup B\cup\text{cube})\\"
                     r"0 & \text{otherwise}\end{cases}", font_size=28)
        fit_width(pw, 7.0)
        pw.next_to(rows, DOWN, buff=0.45).align_to(head, LEFT)
        self.play(Write(pw), run_time=3.0)
        self.wait(1.0)

        k = 0.58

        def P(x, z):
            return np.array([3.9 + (x - 1) * k, 0.2 + z * k, 0])

        xax = Line(P(-3.4, -3.3), P(5.4, -3.3), color=T.text_muted, stroke_width=1.5)
        zax = Line(P(-3.4, -3.3), P(-3.4, 3.3), color=T.text_muted, stroke_width=1.5)
        title = Text("slice  y = 0", font_size=24, color=T.text_secondary)
        title.move_to(P(1, 3.6))
        c1 = Circle(radius=3 * k).move_to(P(0, 0))
        c2 = Circle(radius=3 * k).move_to(P(2, 0))
        body = Union(c1, c2, color=T.variable, fill_opacity=0.5,
                     stroke_color=T.text_primary, stroke_width=2)
        s3c = DashedVMobject(Circle(radius=5 ** 0.5 * k, color=T.highlight_secondary,
                                    stroke_width=2).move_to(P(0, 0)), num_dashes=36)
        cavA = Circle(radius=1 * k, color=T.text_primary, stroke_width=2)
        cavA.move_to(P(0, 0)).set_fill(T.background_primary, 1)
        cavB = Sector(outer_radius=3 * k, start_angle=PI, angle=PI, arc_center=P(2, 0),
                      color=T.result_intermediate, stroke_width=2)
        cavB.set_fill(T.background_primary, 1)
        cube = Square(side_length=k).move_to(P(2, 1))
        cube.set_fill(T.warning, 0.95).set_stroke(T.text_primary, 2)
        l0 = MathTex(r"\rho_0", font_size=34, color=T.text_primary).move_to(P(-1.7, 1.5))
        lc = MathTex(r"\rho_c", font_size=30, color=T.warning).next_to(cube, UR, buff=0.05)
        lA = MathTex(r"A", font_size=26, color=T.text_primary).move_to(P(-0.1, 0.35))
        lB = MathTex(r"B", font_size=30, color=T.result_intermediate).move_to(P(2.3, -1.6))
        self.play(FadeIn(title), Create(xax), Create(zax), Create(body), run_time=1.6)
        self.play(Create(s3c), run_time=0.9)
        self.play(FadeIn(l0), run_time=0.5)
        self.play(FadeIn(cavA), FadeIn(cavB), FadeIn(lA), FadeIn(lB), run_time=1.4)
        self.play(FadeIn(cube, scale=1.5), FadeIn(lc), run_time=1.0)
        self.play(Indicate(cube, color=T.warning), run_time=0.9)
        self.wait(5.0)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("(c) Total charge", font_size=30, color=T.text_secondary)
        head.to_corner(UL, buff=0.4)
        self.play(FadeIn(head), run_time=0.6)
        L = [
            MathTex(r"Q=\rho_0V_0+\rho_cV_{\text{cube}}", font_size=36),
            MathTex(r"V_0=V(S_1\cup S_2\cup S_3)-V(A\cup B)-V_{\text{cube}}", font_size=28),
            MathTex(r"V(\cup)=3V-(V_{12}+V_{13}+V_{23})+V_{123}", font_size=28),
            MathTex(r"V_{ij}(d)=\pi\,(4R+d)(2R-d)^2/12", font_size=28),
            MathTex(r"V(A\cup B)=\tfrac{4\pi}{3}+18\pi-\tfrac{2\pi}{3}=\tfrac{56\pi}{3}", font_size=28),
            MathTex(r"Q=@V0@\,\rho_0+\rho_c", font_size=40, color=T.result_final),
        ]
        stack = VGroup(*L).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        stack.next_to(head, DOWN, buff=0.5).align_to(head, LEFT)
        fit_width(stack, 6.7)
        note = MathTex(r"\rho_c=2\rho_0\ \Rightarrow\ Q=@QEX@\,\rho_0", font_size=30,
                       color=T.text_secondary)
        note.next_to(stack, DOWN, buff=0.35).align_to(stack, LEFT)
        nums = Text("V12 = V13 = @L12@   V23 = @L23@   V123 = @T123@   (m^3)",
                    font_size=20, color=T.text_muted)
        nums.next_to(L[3], DOWN, buff=0.1).align_to(L[3], LEFT)
        nums.shift(DOWN * 0.0)

        base = -3.0
        sc = 0.0155
        xs = [2.6, 3.9, 5.2, 6.5]
        spec = [(0.0, @UNION@, T.variable, "union", "@UNION@"),
                (@UNION@ - @CAV@, @UNION@, T.constant, "cavities", "-@CAV@"),
                (@V0@ - 0.0 + 0.0, @V0@ + 1.0, T.warning, "cube", "-1.00"),
                (0.0, @V0@, T.result_final, "uniform V0", "@V0@")]
        bars, caps = VGroup(), VGroup()
        for x, (lo, hi, col, name, val) in zip(xs, spec):
            r = Rectangle(width=0.9, height=(hi - lo) * sc, stroke_color=col, stroke_width=3)
            r.set_fill(col, 0.45)
            r.move_to(np.array([x, base + (lo + hi) / 2 * sc, 0]))
            t = Text(val, font_size=22, color=T.text_primary).next_to(r, UP, buff=0.12)
            n = Text(name, font_size=20, color=T.text_secondary).next_to(r, DOWN, buff=0.12)
            bars.add(r)
            caps.add(VGroup(t, n))
        axis = Line(np.array([2.0, base, 0]), np.array([7.0, base, 0]), color=T.text_muted)
        unit = Text("volume, m^3", font_size=20, color=T.text_muted).move_to(np.array([4.55, 1.3, 0]))

        self.play(Write(L[0]), run_time=1.6)
        self.wait(1.2)
        self.play(Write(L[1]), run_time=1.8)
        self.wait(1.0)
        self.play(Write(L[2]), Create(axis), FadeIn(unit), run_time=2.0)
        self.play(FadeIn(bars[0], shift=UP * 0.2), FadeIn(caps[0]), run_time=1.0)
        self.wait(1.0)
        self.play(Write(L[3]), run_time=1.6)
        self.play(FadeIn(nums), run_time=0.8)
        self.wait(1.6)
        self.play(Write(L[4]), run_time=1.6)
        self.play(FadeIn(bars[1]), FadeIn(caps[1]), FadeIn(bars[2]), FadeIn(caps[2]), run_time=1.4)
        self.wait(1.0)
        self.play(FadeIn(bars[3]), FadeIn(caps[3]), run_time=1.0)
        self.play(Write(L[5]), run_time=1.4)
        self.play(Indicate(L[5], color=T.result_final), run_time=1.0)
        self.play(Write(note), run_time=1.2)
        self.wait(3.0)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("(d)(e) Potential and field", font_size=30, color=T.text_secondary)
        head.to_corner(UL, buff=0.4)
        self.play(FadeIn(head), run_time=0.6)
        L = [
            MathTex(r"\phi(\mathbf r)=\frac{1}{4\pi\varepsilon_0}\iiint \frac{\rho_v(\mathbf r')}{|\mathbf r-\mathbf r'|}\,dV'", font_size=30),
            MathTex(r"\phi=\frac{1}{4\pi\varepsilon_0}\Big[\rho_0\!\!\iiint_{\Omega_0}\!\frac{dV'}{R}+\rho_c\!\!\iiint_{\text{cube}}\!\frac{dV'}{R}\Big]", font_size=28),
            MathTex(r"\mathbf E=-\nabla\phi,\qquad \nabla\frac1R=-\frac{\mathbf r-\mathbf r'}{R^{3}}", font_size=30),
            MathTex(r"E_x=\frac{1}{4\pi\varepsilon_0}\iiint \rho_v(\mathbf r')\,\frac{x-x'}{R^{3}}\,dV'", font_size=30),
        ]
        stack = VGroup(*L).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        stack.next_to(head, DOWN, buff=0.5).align_to(head, LEFT)
        fit_width(stack, 7.4)
        foot = Text("E_y, E_z: replace x - x' by y - y', z - z'   (R = |r - r'|)", font_size=20,
                    color=T.text_muted)
        foot.next_to(stack, DOWN, buff=0.4).align_to(stack, LEFT)
        num = Text("evaluated numerically: 1,295,379 charge cells of 0.05 m", font_size=22,
                   color=T.text_secondary)
        num.next_to(foot, DOWN, buff=0.35).align_to(stack, LEFT)

        blob = Union(Circle(radius=1.15).move_to(np.array([4.2, 1.2, 0])),
                     Circle(radius=1.15).move_to(np.array([5.1, 1.2, 0])),
                     color=T.variable, fill_opacity=0.30, stroke_color=T.text_primary, stroke_width=2)
        blob_lab = MathTex(r"\rho_v(\mathbf r')", font_size=28, color=T.text_primary).move_to(np.array([4.0, 2.7, 0]))
        src = Dot(np.array([4.7, 1.7, 0]), color=T.constant, radius=0.09)
        obs = Dot(np.array([5.6, -2.0, 0]), color=T.text_primary, radius=0.1)
        dv = Square(side_length=0.22, color=T.constant, stroke_width=3).move_to(src)
        rvec = Arrow(src.get_center(), obs.get_center(), buff=0.12, color=T.displacement,
                     stroke_width=4)
        lr = MathTex(r"\mathbf R", font_size=30, color=T.displacement).move_to(np.array([5.45, -0.1, 0]))
        lp = MathTex(r"\mathbf r'", font_size=28, color=T.constant).next_to(src, LEFT, buff=0.15)
        lo = MathTex(r"\mathbf r", font_size=30, color=T.text_primary).next_to(obs, LEFT, buff=0.15)
        ldv = MathTex(r"dV'", font_size=24, color=T.constant).next_to(dv, UR, buff=0.02)
        extra = VGroup()
        for p in [(3.7, 1.0), (4.3, 0.6), (4.9, 0.7), (5.5, 1.0), (3.9, 1.6), (5.3, 1.7), (4.6, 0.9)]:
            d = Dot(np.array([p[0], p[1], 0]), color=T.constant, radius=0.05)
            ln = Line(d.get_center(), obs.get_center(), color=T.grid, stroke_width=1.5)
            extra.add(VGroup(ln, d))
        Evec = Arrow(obs.get_center(), obs.get_center() + np.array([0.9, -0.2, 0]), buff=0,
                     color=T.vector_force, stroke_width=6)
        lE = MathTex(r"\mathbf E(\mathbf r)", font_size=30, color=T.vector_force).next_to(Evec, DOWN, buff=0.1)

        self.play(Write(L[0]), FadeIn(blob), FadeIn(blob_lab), run_time=2.4)
        self.play(FadeIn(obs), FadeIn(lo), run_time=0.8)
        self.wait(1.2)
        self.play(Write(L[1]), run_time=2.6)
        self.play(FadeIn(src), Create(dv), FadeIn(lp), FadeIn(ldv), run_time=1.0)
        self.play(GrowArrow(rvec), FadeIn(lr), run_time=1.0)
        self.wait(1.2)
        self.play(Write(L[2]), run_time=2.2)
        self.play(FadeIn(extra), run_time=1.4)
        self.wait(1.0)
        self.play(Write(L[3]), run_time=2.2)
        self.play(Write(foot), run_time=1.0)
        self.play(GrowArrow(Evec), FadeIn(lE), run_time=1.2)
        self.play(Indicate(Evec, color=T.vector_force), run_time=0.9)
        self.play(Write(num), run_time=1.4)
        self.wait(3.0)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("(f) Maxwell's equations", font_size=30, color=T.text_secondary)
        head.to_corner(UL, buff=0.4)
        self.play(FadeIn(head), run_time=0.6)
        L = [
            MathTex(r"\nabla^2\frac1R=-4\pi\,\delta(\mathbf r-\mathbf r')", font_size=34),
            MathTex(r"\nabla^2\phi=-\frac{\rho_v}{\varepsilon_0}\ \Rightarrow\ \nabla\cdot\mathbf E=\frac{\rho_v}{\varepsilon_0}", font_size=34, color=T.result_final),
            MathTex(r"\nabla\times\mathbf E=-\nabla\times(\nabla\phi)=\mathbf 0", font_size=34, color=T.result_final),
        ]
        stack = VGroup(*L).arrange(DOWN, aligned_edge=LEFT, buff=0.7)
        stack.next_to(head, DOWN, buff=0.7).align_to(head, LEFT)
        fit_width(stack, 6.4)
        irr = Text("a gradient is irrotational", font_size=22, color=T.text_muted)
        irr.next_to(L[2], DOWN, buff=0.3).align_to(L[2], LEFT)

        rows = @LOCAL@
        names = {"rho0 region": "uniform rho0", "cube": "cube", "hollow cavity": "hollow cavity",
                 "hemispherical cavity": "hemisph. cavity", "vacuum": "vacuum"}
        x0, y0 = 1.0, 1.9
        hd = VGroup(Text("location", font_size=22, color=T.text_muted),
                    MathTex(r"\rho_v/\rho_0", font_size=26, color=T.text_muted),
                    MathTex(r"\varepsilon_0\nabla\!\cdot\!\mathbf E/\rho_0", font_size=26, color=T.text_muted))
        xs = [x0, x0 + 2.6, x0 + 4.3]
        for h, x in zip(hd, xs):
            h.move_to(np.array([x, y0, 0]), aligned_edge=LEFT)
        grid = VGroup(hd)
        for i, rw in enumerate(rows):
            y = y0 - 0.7 - i * 0.62
            a = Text(names[rw["where"]], font_size=22, color=T.text_primary)
            b = Text(f"{rw['rho']:.1f}", font_size=22, color=T.text_secondary)
            ok = abs(rw["div"] - rw["rho"]) < 0.03
            c = Text(f"{rw['div']:+.3f}", font_size=22, color=T.result_final if ok else T.warning)
            for m, x in zip((a, b, c), xs):
                m.move_to(np.array([x, y, 0]), aligned_edge=LEFT)
            grid.add(VGroup(a, b, c))
        rule = Line(np.array([x0, y0 - 0.35, 0]), np.array([x0 + 5.6, y0 - 0.35, 0]), color=T.grid)
        cap = Text("flux / volume through a 0.3 m sphere", font_size=18, color=T.text_muted)
        cap.move_to(np.array([x0, y0 - 0.7 - 5 * 0.62 - 0.1, 0]), aligned_edge=LEFT)

        self.play(Write(L[0]), run_time=2.2)
        self.wait(1.6)
        self.play(Write(L[1]), run_time=2.6)
        self.wait(1.6)
        self.play(Write(L[2]), run_time=2.4)
        self.play(FadeIn(irr), run_time=0.8)
        self.wait(1.6)
        self.play(FadeIn(hd), Create(rule), run_time=1.2)
        for g in grid[1:]:
            self.play(FadeIn(g, shift=LEFT * 0.2), run_time=0.9)
        self.play(FadeIn(cap), run_time=0.6)
        self.play(Indicate(L[1], color=T.result_final), run_time=1.2)
        self.wait(2.0)
'''

SEG5 = r'''from manim import *


class Segment5(Scene):
    def construct(self):
        head = Text("(g) Boundary conditions", font_size=30, color=T.text_secondary)
        head.to_corner(UL, buff=0.4)
        self.play(FadeIn(head), run_time=0.6)
        L = [
            MathTex(r"E_n^{\text{out}}-E_n^{\text{in}}=\sigma/\varepsilon_0=0", font_size=30),
            MathTex(r"E_t^{\text{out}}-E_t^{\text{in}}=0", font_size=30),
            MathTex(r"\mathbf E\ \text{continuous;}\ \nabla\cdot\mathbf E=\rho_v/\varepsilon_0\ \text{jumps}",
                    font_size=28, color=T.result_final),
        ]
        stack = VGroup(*L).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        stack.next_to(head, DOWN, buff=0.6).align_to(head, LEFT)
        fit_width(stack, 6.0)
        t1 = Text("Cavity wall: no shielding.", font_size=24, color=T.text_secondary)
        t2 = Text("An empty cavity is not a conductor,", font_size=22, color=T.text_muted)
        t3 = Text("so field lines pass straight through.", font_size=22, color=T.text_muted)
        notes = VGroup(t1, t2, t3).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        notes.next_to(stack, DOWN, buff=0.7).align_to(head, LEFT)

        xs, em, ex, mt = @SX@, @SEM@, @SEX@, @SMAT@
        axes = Axes(x_range=[-4, 6, 2], y_range=[-0.9, 1.5, 0.5], x_length=6.2, y_length=3.4,
                    axis_config={"color": T.text_muted, "include_tip": False,
                                 "font_size": 20},
                    x_axis_config={"numbers_to_include": [-4, -2, 0, 2, 4, 6]},
                    y_axis_config={"numbers_to_include": [-0.5, 0, 0.5, 1.0, 1.5]})
        axes.move_to(np.array([3.5, 0.7, 0]))
        cols = {1: T.variable, 2: T.text_muted, 3: T.result_intermediate, 4: T.warning}
        bands = VGroup()
        start = 0
        for i in range(1, len(mt) + 1):
            if i == len(mt) or mt[i] != mt[start]:
                if mt[start] in cols:
                    a = axes.c2p(xs[start], -0.9)
                    b = axes.c2p(xs[min(i, len(xs) - 1)] if i < len(xs) else xs[-1], 1.5)
                    r = Rectangle(width=max(b[0] - a[0], 0.02), height=b[1] - a[1], stroke_width=0)
                    r.set_fill(cols[mt[start]], 0.16 if mt[start] == 1 else 0.40)
                    r.move_to((a + b) / 2)
                    bands.add(r)
                start = i
        gE = axes.plot_line_graph(xs, em, line_color=T.text_primary, add_vertex_dots=False, stroke_width=4)
        gX = axes.plot_line_graph(xs, ex, line_color=T.constant, add_vertex_dots=False, stroke_width=3)
        lE = Text("|E|", font_size=22, color=T.text_primary).move_to(axes.c2p(5.3, em[-3] + 0.18))
        lX = Text("Ex", font_size=22, color=T.constant).move_to(axes.c2p(-3.2, ex[2] - 0.2))
        xl = Text("x (m) along y = 0, z = -0.5", font_size=20, color=T.text_muted)
        xl.next_to(axes, DOWN, buff=0.25)
        yl = Text("E in rho0/eps0 * m", font_size=18, color=T.text_muted).next_to(axes, UP, buff=0.15)

        jr = @JUMPS@
        jt = VGroup()
        for i, j in enumerate(jr):
            a = Text(j["where"], font_size=18, color=T.text_secondary)
            b = Text(f"dEn = {j['dEn']:+.3f}", font_size=18, color=T.text_primary)
            c = Text(f"d rho = {j['drho']:+.0f}", font_size=18, color=T.text_muted)
            row = VGroup(a, b, c).arrange(RIGHT, buff=0.35)
            jt.add(row)
        jt.arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(np.array([3.5, -2.85, 0]))
        jcap = Text("differences measured +-0.03 m across each wall (grid-limited)", font_size=16,
                    color=T.text_muted).next_to(jt, DOWN, buff=0.12)

        self.play(Write(L[0]), run_time=2.0)
        self.play(Write(L[1]), run_time=1.6)
        self.wait(1.0)
        self.play(Write(L[2]), run_time=2.2)
        self.wait(1.4)
        self.play(FadeIn(notes), run_time=1.4)
        self.wait(2.0)
        self.play(Create(axes), FadeIn(yl), FadeIn(xl), FadeIn(bands), run_time=1.6)
        self.play(Create(gE), FadeIn(lE), run_time=2.4)
        self.play(Create(gX), FadeIn(lX), run_time=2.0)
        self.wait(1.0)
        self.play(FadeIn(jt), FadeIn(jcap), run_time=1.6)
        self.play(Indicate(gE, color=T.text_primary), run_time=1.2)
        self.wait(3.0)
'''

SEG6 = r'''from manim import *


class Segment6(Scene):
    def construct(self):
        head = Text("(h) Visualization and numerics", font_size=30, color=T.text_secondary)
        head.to_corner(UL, buff=0.4)
        self.play(FadeIn(head), run_time=0.6)
        k = 0.52

        def P(x, z):
            return np.array([-2.5 + (x - 1) * k, -0.15 + z * k, 0])

        c1 = Circle(radius=3 * k).move_to(P(0, 0))
        c2 = Circle(radius=3 * k).move_to(P(2, 0))
        body = Union(c1, c2, color=T.variable, fill_opacity=0.22,
                     stroke_color=T.text_primary, stroke_width=2)
        cavA = Circle(radius=k, color=T.text_primary, stroke_width=2).move_to(P(0, 0))
        cavA.set_fill(T.background_primary, 1)
        cavB = Sector(outer_radius=3 * k, start_angle=PI, angle=PI, arc_center=P(2, 0),
                      color=T.result_intermediate, stroke_width=2)
        cavB.set_fill(T.background_primary, 1)
        cube = Square(side_length=k).move_to(P(2, 1))
        cube.set_fill(T.warning, 0.95).set_stroke(T.text_primary, 2)
        title = Text("E in the plane y = 0 (Coulomb sum, 0.05 m cells)", font_size=22,
                     color=T.text_secondary).move_to(np.array([-2.3, 3.15, 0]))
        gx, gz, ex, ez = @QX@, @QZ@, @QEX@, @QEZ@
        arrows = VGroup()
        mx = 0.0
        for i, x in enumerate(gx):
            for j, z in enumerate(gz):
                mx = max(mx, (ex[i][j] ** 2 + ez[i][j] ** 2) ** 0.5)
        for i, x in enumerate(gx):
            for j, z in enumerate(gz):
                vx, vz = ex[i][j], ez[i][j]
                m = (vx * vx + vz * vz) ** 0.5
                if m < 1e-3:
                    continue
                ln = 0.18 + 0.30 * min(m / 1.2, 1.0)
                a = P(x, z)
                d = np.array([vx / m, vz / m, 0]) * ln
                col = interpolate_color(T.variable, T.warning, min(m / 1.2, 1.0))
                arrows.add(Arrow(a - d / 2, a + d / 2, buff=0, color=col, stroke_width=3,
                                 max_tip_length_to_length_ratio=0.5, max_stroke_width_to_length_ratio=8))
        pts = @POINTS@
        hdr = VGroup(Text("point", font_size=20, color=T.text_muted),
                     Text("|E|", font_size=20, color=T.text_muted),
                     Text("phi", font_size=20, color=T.text_muted))
        xs = [2.0, 5.1, 6.1]
        for h, x in zip(hdr, xs):
            h.move_to(np.array([x, 3.0, 0]), aligned_edge=LEFT)
        rows = VGroup()
        for i, p in enumerate(pts):
            y = 2.45 - i * 0.62
            a = Text(p["name"], font_size=18, color=T.text_primary)
            b = Text(str(tuple(p["r"])).replace(".0", ""), font_size=15, color=T.text_muted)
            va = VGroup(a, b).arrange(DOWN, aligned_edge=LEFT, buff=0.04)
            va.move_to(np.array([xs[0], y, 0]), aligned_edge=LEFT)
            m = Text(f"{p['Emag']:.3f}", font_size=20, color=T.text_primary).move_to(np.array([xs[1], y, 0]), aligned_edge=LEFT)
            f = Text(f"{p['phi']:.2f}", font_size=20, color=T.text_primary).move_to(np.array([xs[2], y, 0]), aligned_edge=LEFT)
            rows.add(VGroup(va, m, f))
        unit = Text("E: rho0/eps0 * m    phi: rho0/eps0 * m^2", font_size=15, color=T.text_muted)
        unit.move_to(np.array([2.0, -3.3, 0]), aligned_edge=LEFT)

        self.play(Create(body), FadeIn(title), run_time=1.6)
        self.play(FadeIn(cavA), FadeIn(cavB), FadeIn(cube, scale=1.4), run_time=1.4)
        self.wait(1.0)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.02), run_time=5.0)
        self.wait(2.0)
        self.play(FadeIn(hdr), run_time=0.6)
        for r in rows:
            self.play(FadeIn(r, shift=LEFT * 0.2), run_time=0.8)
        self.play(FadeIn(unit), run_time=0.6)
        self.play(Indicate(cube, color=T.warning), run_time=1.0)
        self.wait(3.0)
'''

SEG7 = r'''from manim import *


class Segment7(Scene):
    def construct(self):
        head = Text("(i) Validation", font_size=30, color=T.text_secondary)
        head.to_corner(UL, buff=0.4)
        self.play(FadeIn(head), run_time=0.6)
        ax = Axes(x_range=[0, 8, 2], y_range=[0, 1.1, 0.25], x_length=5.6, y_length=2.7,
                  axis_config={"color": T.text_muted, "include_tip": False, "font_size": 18},
                  x_axis_config={"numbers_to_include": [0, 2, 4, 6, 8]},
                  y_axis_config={"numbers_to_include": [0, 0.5, 1.0]})
        ax.move_to(np.array([-3.5, 1.1, 0]))
        f = lambda r: r / 3.0 if r < 3.0 else 9.0 / (r * r)
        curve = ax.plot(f, x_range=[0.01, 8], color=T.graph_function, stroke_width=4)
        rr, en = @RADII@, @ENUM@
        dots = VGroup(*[Dot(ax.c2p(r, e), color=T.warning, radius=0.07) for r, e in zip(rr, en)])
        t_a = Text("single sphere: E(r)", font_size=20, color=T.text_secondary).next_to(ax, UP, buff=0.15)
        l_an = Text("analytic", font_size=18, color=T.graph_function).move_to(ax.c2p(5.4, 0.55))
        l_nu = Text("numerical (h = 1/16)", font_size=18, color=T.warning).move_to(ax.c2p(2.2, 0.95))
        eqs = MathTex(r"E=\frac{\rho r}{3\varepsilon_0}\ (r<R),\qquad E=\frac{Q}{4\pi\varepsilon_0r^2}\ (r>R)",
                      font_size=24)
        fit_width(eqs, 5.6)
        eqs.next_to(ax, DOWN, buff=0.55)

        bx = Axes(x_range=[-1.4, -0.2, 0.4], y_range=[-5.2, -0.4, 1], x_length=5.0, y_length=2.7,
                  axis_config={"color": T.text_muted, "include_tip": False})
        bx.move_to(np.array([3.6, 1.1, 0]))
        se = @SERR@
        qe = @QERR@
        sp = [bx.c2p(np.log10(h), np.log10(e)) for h, e in se]
        qp = [bx.c2p(np.log10(h), np.log10(e)) for h, e in qe]
        sl = VMobject(color=T.warning, stroke_width=4).set_points_as_corners(sp)
        ql = VMobject(color=T.result_final, stroke_width=4).set_points_as_corners(qp)
        sd = VGroup(*[Dot(p, color=T.warning, radius=0.06) for p in sp])
        qd = VGroup(*[Dot(p, color=T.result_final, radius=0.06) for p in qp])
        ticks = VGroup()
        for h, lab in ((0.0625, "1/16"), (0.125, "1/8"), (0.25, "1/4"), (0.5, "1/2")):
            ticks.add(Text(lab, font_size=16, color=T.text_muted).next_to(bx.c2p(np.log10(h), -5.2), DOWN, buff=0.1))
        for e, lab in ((-1, "1e-1"), (-2, "1e-2"), (-3, "1e-3"), (-4, "1e-4"), (-5, "1e-5")):
            ticks.add(Text(lab, font_size=16, color=T.text_muted).next_to(bx.c2p(-1.4, e), LEFT, buff=0.1))
        t_b = Text("error vs cell size h", font_size=20, color=T.text_secondary).next_to(bx, UP, buff=0.15)
        l_s = Text("single sphere, max |dE|/E_peak", font_size=16, color=T.warning).move_to(bx.c2p(-0.75, -1.1))
        l_q = Text("composite body, total charge", font_size=16, color=T.result_final).move_to(bx.c2p(-0.75, -4.6))

        g = @GAUSS@
        gt = VGroup()
        hdr = VGroup(Text("Gauss surface", font_size=18, color=T.text_muted),
                     Text("flux", font_size=18, color=T.text_muted),
                     Text("Q enclosed", font_size=18, color=T.text_muted),
                     Text("rel. diff", font_size=18, color=T.text_muted))
        cx = [-6.6, -1.2, 0.8, 2.8]
        for h, x in zip(hdr, cx):
            h.move_to(np.array([x, -1.7, 0]), aligned_edge=LEFT)
        gt.add(hdr)
        for i, r in enumerate(g):
            y = -2.15 - i * 0.4
            vals = [Text(r["surface"], font_size=18, color=T.text_primary),
                    Text(f"{r['flux']:.3f}", font_size=18, color=T.text_primary),
                    Text(f"{r['q']:.3f}", font_size=18, color=T.text_primary),
                    Text(f"{r['rel']:.1e}", font_size=18, color=T.result_final)]
            for v, x in zip(vals, cx):
                v.move_to(np.array([x, y, 0]), aligned_edge=LEFT)
            gt.add(VGroup(*vals))
        far = Text("far field, 300 m from the charge centroid: differs from a point charge by @FAR@",
                   font_size=16, color=T.text_muted).move_to(np.array([-6.6, -3.45, 0]), aligned_edge=LEFT)

        self.play(Create(ax), FadeIn(t_a), run_time=1.2)
        self.play(Create(curve), FadeIn(l_an), Write(eqs), run_time=3.0)
        self.play(FadeIn(dots, lag_ratio=0.1), FadeIn(l_nu), run_time=2.4)
        self.wait(1.0)
        self.play(Create(bx), FadeIn(ticks), FadeIn(t_b), run_time=1.4)
        self.play(Create(sl), FadeIn(sd), FadeIn(l_s), run_time=2.0)
        self.wait(0.8)
        self.play(Create(ql), FadeIn(qd), FadeIn(l_q), run_time=2.0)
        self.wait(1.0)
        self.play(FadeIn(gt[0]), run_time=0.6)
        for row in gt[1:]:
            self.play(FadeIn(row, shift=LEFT * 0.2), run_time=0.8)
        self.play(Indicate(gt[1], color=T.result_final), run_time=1.0)
        self.play(FadeIn(far), run_time=0.8)
        self.wait(3.0)
'''

SEG8 = r'''from manim import *


class Segment8(Scene):
    def construct(self):
        head = Text("Summary", font_size=34, color=T.text_secondary)
        head.to_corner(UL, buff=0.4)
        self.play(FadeIn(head), run_time=0.6)
        items = [
            ("Geometry", r"\text{inequalities, one priority rule: cube}>\text{cavities}>\text{spheres}"),
            ("Charge", r"Q=@V0@\,\rho_0+\rho_c\ \ (\text{exact, inclusion--exclusion})"),
            ("Field", r"\phi=\frac{1}{4\pi\varepsilon_0}\iiint\frac{\rho_v}{R}dV',\quad \mathbf E=-\nabla\phi"),
            ("Maxwell", r"\nabla\cdot\mathbf E=\rho_v/\varepsilon_0,\quad \nabla\times\mathbf E=\mathbf 0"),
            ("Boundaries", r"\mathbf E,\ \phi\ \text{continuous: no surface charge}"),
            ("Validation", r"\text{Gauss's law to }6\times10^{-5};\ \text{single sphere}\ @SPH@\%\text{ of peak}"),
        ]
        rows = VGroup()
        for name, tex in items:
            tick = VMobject(color=T.result_final, stroke_width=6)
            tick.set_points_as_corners([np.array([-0.18, 0.0, 0]), np.array([-0.05, -0.14, 0]),
                                        np.array([0.2, 0.2, 0])])
            n = Text(name, font_size=28, color=T.text_primary)
            e = MathTex(tex, font_size=28, color=T.text_secondary)
            fit_width(e, 8.2)
            line = VGroup(tick, n, e).arrange(RIGHT, buff=0.4)
            rows.add(line)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to(DOWN * 0.1)
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT * 0.3), run_time=1.1)
            self.wait(1.2)
        box = SurroundingRectangle(rows[1], color=T.result_final, buff=0.15)
        self.play(Create(box), Indicate(rows[1], color=T.result_final), run_time=1.4)
        self.wait(3.0)
'''


def _fill(code: str, **tokens) -> str:
    for key, value in tokens.items():
        code = code.replace(f"@{key}@", value if isinstance(value, str) else repr(value))
    return code


_L = _f(V["lens_12"])
SEGMENTS = [
    {
        "narration": "Start with the geometry. Each sphere is a ball of radius three "
                     "metres. Sphere one is centred at the origin: x squared plus y "
                     "squared plus z squared is at most nine. Sphere two moves the "
                     "centre to x equals two, and sphere three moves it to y equals "
                     "two. The hollow cavity is the open unit ball at the origin: x "
                     "squared plus y squared plus z squared is less than one. The "
                     "hemispherical cavity is the half of sphere two where z is "
                     "negative. And the cube has side one metre, centred at two, zero, "
                     "one, so each coordinate stays within one half of its centre.",
        "visual": {"objective": "define every region as a Cartesian inequality, "
                                "building the 3D body piece by piece",
                   "transition": "slide-up",
                   "visual_elements": ["three spheres", "hollow cavity",
                                       "hemispherical cavity", "cube", "inequalities"],
                   "diagram": "none", "camera_movement": "orbit",
                   "three_d": True,
                   "highlight": ["each region as its inequality appears"],
                   "color_roles": {"S1": "variable", "S2": "constant",
                                   "S3": "highlight_secondary",
                                   "cube": "warning", "hemisphere": "result_intermediate"},
                   "animation_beats": ["sphere one", "spheres two and three",
                                       "hollow cavity", "hemispherical cavity", "cube"],
                   "outcome": "all regions are defined by inequalities"},
        "code": SEG0,
    },
    {
        "narration": "Where regions overlap, every point must belong to exactly one "
                     "material, so we fix a priority rule. The cube comes first, with "
                     "density rho c. The cavities come second, and they are carved out "
                     "of the spheres, so they hold no charge. The union of the three "
                     "spheres comes third, with density rho zero. Everything else is "
                     "vacuum. As a piecewise function, rho v equals rho c inside the "
                     "cube, zero inside either cavity, rho zero in the rest of the "
                     "union, and zero outside. This slice through the plane y equals "
                     "zero shows the result: the cube in red, the two cavities in "
                     "black, and the uniform body around them.",
        "visual": {"objective": "state the priority rule, the piecewise density, "
                                "and show it on a slice",
                   "transition": "carry-over",
                   "visual_elements": ["priority list", "piecewise function",
                                       "cross-section"],
                   "diagram": "geometry",
                   "highlight": ["the cube"],
                   "color_roles": {"cube": "warning", "uniform": "variable",
                                   "cavity B": "result_intermediate"},
                   "animation_beats": ["priority rule", "piecewise rho_v",
                                       "build the y = 0 slice"],
                   "outcome": "every point has exactly one material"},
        "code": SEG1,
    },
    {
        "narration": "The total charge is rho zero times the volume of the uniform "
                     "material, plus rho c times the volume of the cube. The uniform "
                     "volume is the union of the spheres, minus the cavities, minus the "
                     "cube, so no charge is counted twice. By inclusion and exclusion, "
                     "the union is three ball volumes, minus the three pairwise "
                     "overlaps, plus the triple overlap. Each ball has volume thirty "
                     f"six pi, or {_f(V['v_ball'])} cubic metres. Two balls at distance "
                     "d overlap in a lens of volume pi times four R plus d, times two R "
                     f"minus d, squared, over twelve. That gives {_L} for the first two "
                     f"pairs, and {_f(V['lens_23'])} for the pair at distance two root "
                     "two. The triple overlap, found by integrating the cross sectional "
                     f"area, is {_f(V['triple'])}. The union is {_f(V['union'])}. The "
                     f"cavities total {_f(V['cavities'])}: the unit ball, plus the "
                     "hemisphere, minus the half ball they share. So the uniform volume "
                     f"is {_f(V['rho0_volume'])} cubic metres, and Q equals "
                     f"{_f(V['rho0_volume'])} rho zero, plus one times rho c. With rho c "
                     f"equal to two rho zero, that is {_f(D.Q_EXACT)} rho zero.",
        "visual": {"objective": "derive Q by inclusion-exclusion without "
                                "double counting",
                   "transition": "carry-over",
                   "visual_elements": ["formulas", "volume bars"],
                   "diagram": "none", "integration": False,
                   "highlight": ["the final charge"],
                   "color_roles": {"union": "variable", "cavities": "constant",
                                   "cube": "warning", "result": "result_final"},
                   "animation_beats": ["Q formula", "uniform volume",
                                       "inclusion-exclusion", "lens volume",
                                       "cavities", "result"],
                   "outcome": f"Q = {_f(V['rho0_volume'])} rho0 + rho_c"},
        "code": _fill(SEG2, V0=_f(V["rho0_volume"]), QEX=_f(D.Q_EXACT), L12=_L,
                      L23=_f(V["lens_23"]), T123=_f(V["triple"]), UNION=_f(V["union"]),
                      CAV=_f(V["cavities"])),
    },
    {
        "narration": "The potential is the Coulomb integral of the charge density over "
                     "the whole body, taken to be zero at infinity. Splitting by "
                     "material, phi at r equals one over four pi epsilon zero, times "
                     "rho zero times the integral over the uniform region, plus rho c "
                     "times the integral over the cube, each divided by the distance R. "
                     "The electric field is minus the gradient of phi. Because the "
                     "gradient of one over R is minus R hat over R squared, the three "
                     "components follow directly. E x equals one over four pi epsilon "
                     "zero times the integral of rho v of r prime, times x minus x "
                     "prime, over R cubed. The y and z components are identical in "
                     "form. No closed form exists for this geometry, so we evaluate "
                     "these integrals numerically, by summing over small charge cells.",
        "visual": {"objective": "write the Coulomb integrals for phi and E and "
                                "show the geometry of one source cell",
                   "transition": "carry-over",
                   "visual_elements": ["integrals", "source cell", "vector R"],
                   "diagram": "geometry",
                   "highlight": ["the field vector"],
                   "color_roles": {"R": "vector_displacement", "E": "vector_force"},
                   "animation_beats": ["phi integral", "split by material",
                                       "E = -grad phi", "components", "numerics"],
                   "outcome": "phi and E are Coulomb integrals"},
        "code": SEG3,
    },
    {
        "narration": "Now we check the electrostatic equations. The Laplacian of one "
                     "over R equals minus four pi times a delta function. Applying it "
                     "to the potential gives Poisson's equation, so the divergence of E "
                     "equals rho over epsilon zero. And because E is a gradient, its "
                     "curl is the curl of a gradient, which is identically zero. "
                     "Numerically, the flux through a small sphere divided by its "
                     "volume recovers the density: one in the uniform region, two in "
                     "the cube, and zero in both cavities and in vacuum, all within "
                     "two hundredths.",
        "visual": {"objective": "derive div E and curl E and confirm div E "
                                "numerically at five points",
                   "transition": "carry-over",
                   "visual_elements": ["equations", "check table"],
                   "diagram": "none",
                   "highlight": ["Poisson's equation"],
                   "color_roles": {"results": "result_final"},
                   "animation_beats": ["Laplacian of 1/R", "div E", "curl E",
                                       "numerical table"],
                   "outcome": "Maxwell's electrostatic equations hold"},
        "code": _fill(SEG4, LOCAL=D.LOCAL),
    },
    {
        "narration": "There is no surface charge, so the boundary conditions are "
                     "simple. The normal component of E jumps by sigma over epsilon "
                     "zero, and sigma is zero, so it is continuous. The tangential "
                     "component is always continuous. The field is therefore "
                     "continuous across every interface. Only its slope changes, "
                     "because rho jumps, and so does the divergence. At a cavity wall "
                     "the field does not vanish. The cavity is empty, not a "
                     "conductor, and the surrounding charge is not symmetric, so field "
                     "lines pass straight through. This scan along the x axis at z "
                     "equals minus one half crosses every region without a jump. "
                     "Measured differences across the walls are all below "
                     f"{max(abs(j['dEn']) for j in D.JUMPS):.2f}, and shrink with the "
                     "grid spacing.",
        "visual": {"objective": "show that E is continuous at every interface",
                   "transition": "carry-over",
                   "visual_elements": ["boundary conditions", "line scan plot",
                                       "jump table"],
                   "diagram": "graph",
                   "highlight": ["continuity of E"],
                   "color_roles": {"|E|": "text_primary", "Ex": "constant"},
                   "animation_beats": ["normal and tangential conditions",
                                       "cavity walls", "line scan"],
                   "outcome": "E is continuous across every interface"},
        "code": _fill(SEG5, SX=D.SCAN_X, SEM=D.SCAN_EMAG, SEX=D.SCAN_EX,
                      SMAT=D.SCAN_MAT, JUMPS=D.JUMPS),
    },
    {
        "narration": "Here is the numerical model in the plane y equals zero: the "
                     "spheres, the two cavities and the cube. The field arrows, "
                     "computed from the Coulomb sum over one point three million "
                     "charge cells, point away from the positive charge and weaken "
                     "with distance. At selected points, the numerical field and "
                     "potential are tabulated in units of rho zero over epsilon zero.",
        "visual": {"objective": "visualise the field and tabulate E and phi at "
                                "selected points",
                   "transition": "carry-over",
                   "visual_elements": ["slice", "field arrows", "table"],
                   "diagram": "geometry",
                   "highlight": ["field arrows"],
                   "color_roles": {"arrows": "variable", "cube": "warning"},
                   "animation_beats": ["draw the slice", "field arrows",
                                       "table of points"],
                   "outcome": "E points away from the charge and decays"},
        "code": _fill(SEG6, QX=D.QUIVER_X, QZ=D.QUIVER_Z, QEX=D.QUIVER_EX,
                      QEZ=D.QUIVER_EZ, POINTS=D.POINTS),
    },
    {
        "narration": "To validate the method, we first solve a single uniformly "
                     "charged sphere, where the exact answer is known: E equals rho r "
                     "over three epsilon zero inside, and Q over four pi epsilon zero "
                     "r squared outside. The numerical points land on the analytic "
                     "curve, and the error falls steadily as the cell size is halved, "
                     f"to {100 * D.SPHERE_ERR[-1][1]:.1f} percent of the peak field at "
                     "the finest grid. For the composite body, the total charge "
                     f"converges to within {_sci(QS)} of the exact value. Gauss's law "
                     f"holds too. The flux through a sphere of radius seven is "
                     f"{D.GAUSS[0]['flux']:.2f}, against an enclosed charge of "
                     f"{D.GAUSS[0]['q']:.2f}, a relative difference of "
                     f"{_sci(D.GAUSS[0]['rel'])}. Far from the body, the field matches "
                     "a point charge at the charge centroid to "
                     f"{_sci(D.FAR_FIELD[-1][1])}, at three hundred metres.",
        "visual": {"objective": "validate against the single-sphere solution, "
                                "grid convergence and Gauss's law",
                   "transition": "carry-over",
                   "visual_elements": ["E(r) curve", "convergence plot",
                                       "Gauss table"],
                   "diagram": "graph",
                   "highlight": ["agreement of numerical and analytic results"],
                   "color_roles": {"analytic": "graph_function",
                                   "numerical": "warning", "result": "result_final"},
                   "animation_beats": ["analytic curve", "numerical points",
                                       "convergence", "Gauss's law"],
                   "outcome": "the numerics agree with Gauss and with the sphere"},
        "code": _fill(SEG7, RADII=D.SPHERE_RADII, ENUM=D.SPHERE_E_NUM, SERR=D.SPHERE_ERR,
                      QERR=D.Q_ERR, GAUSS=D.GAUSS,
                      FAR=f"{D.FAR_FIELD[-1][1]:.1e}"),
    },
    {
        "narration": "To summarise: the body is defined by inequalities with a clear "
                     f"priority rule. Its total charge is {_f(V['rho0_volume'])} rho "
                     "zero plus rho c. The potential and field are Coulomb integrals "
                     "that satisfy Maxwell's equations, and the field is continuous at "
                     "every interface. Numerical results agree with Gauss's law and "
                     "with the analytic solution for a single sphere.",
        "visual": {"objective": "summarise the results",
                   "transition": "answer-reveal",
                   "visual_elements": ["checklist"],
                   "diagram": "none",
                   "highlight": ["the total charge"],
                   "color_roles": {"checks": "result_final"},
                   "animation_beats": ["geometry", "charge", "field", "Maxwell",
                                       "boundaries", "validation"],
                   "outcome": "all parts of the problem are solved and verified"},
        "code": _fill(SEG8, V0=_f(V["rho0_volume"]),
                      SPH=f"{100 * D.SPHERE_ERR[-1][1]:.1f}"),
    },
]

LECTURE = {
    "title": TITLE,
    "preset": "spatial",
    "format": "derivation",
    "question": QUESTION,
    "question_code": QUESTION_CODE,
    "segments": SEGMENTS,
}
