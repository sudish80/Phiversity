from manim import *
import numpy as np

# ---------------------------------------------------------------- colours ---
BG   = "#121821"   # chalkboard
BLUE = "#58C4DD"
YELL = "#F4D35E"
GRN  = "#83C167"
RED  = "#FC6255"
TEXT = "#EAF0F6"

config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = 30
config.background_color = BG


class MoonTest(Scene):
    def construct(self):
        # faint blue number-plane grid (the only thing visible on frame 0)
        grid = NumberPlane(
            x_range=[-7, 7, 1],
            y_range=[-4, 4, 1],
            axis_config={"color": BLUE, "stroke_opacity": 0.12, "stroke_width": 1},
            background_line_style={
                "stroke_color": BLUE,
                "stroke_opacity": 0.07,
                "stroke_width": 1,
            },
        )
        self.add(grid)
        self.wait(0.3)  # t = 0.3  (frame 0: chalkboard + grid only)

        # ================= Scene 1 : apple fall + v-t graph (0.3 - 3.7) =====
        apple = Circle(radius=0.22, fill_color=RED, fill_opacity=1, stroke_width=0)
        apple.move_to([-3.6, 3.1, 0])

        axes = Axes(
            x_range=[0, 4, 1],
            y_range=[0, 12, 3],
            x_length=2.6,
            y_length=2.6,
            axis_config={"color": TEXT, "stroke_opacity": 0.6, "stroke_width": 1.5},
            tips=False,
        )
        axes.move_to([3.6, 0.35, 0])
        ax_label = Text("v", font_size=18, color=TEXT).next_to(axes, UP, buff=0.05)
        tx_label = Text("t", font_size=18, color=TEXT).next_to(axes, RIGHT, buff=0.05)

        origin = axes.c2p(0, 0)
        end_pt = axes.c2p(1.0, 9.8)
        vt_line = Line(origin, end_pt, color=BLUE, stroke_width=5)

        label1 = MathTex(
            r"a = g = 9.8\,\mathrm{m/s^2}",
            font_size=30,
            color=YELL,
        ).next_to(axes, DOWN, buff=0.25)

        g = 9.8
        y0 = apple.get_center()[1]
        t_ref = [0.0]

        def fall_update(mob, dt):
            t_ref[0] += dt
            y = y0 - 0.5 * g * (t_ref[0] ** 2)
            mob.move_to([-3.6, min(y, 3.1), 0])

        s1 = VGroup(apple, axes, ax_label, tx_label, vt_line, label1)
        self.play(
            FadeIn(apple, shift=0.2 * UP),
            FadeIn(axes),
            Write(ax_label),
            Write(tx_label),
            run_time=0.6,
        )
        apple.add_updater(fall_update)
        self.play(Create(vt_line), run_time=1.0)
        apple.remove_updater(fall_update)
        self.play(Write(label1), run_time=0.6)
        self.wait(1.2)  # scene 1: 0.6+1.0+0.6+1.2 = 3.4  -> t = 3.7

        # ---------------- Scene 2 : Earth / Moon 60R (3.7 - 9.9) ------------
        self.play(FadeOut(s1), run_time=0.15)

        earth = Circle(radius=0.75, fill_color=BLUE, fill_opacity=0.9, stroke_width=0)
        earth.move_to([-3.4, -0.1, 0])
        moon = Circle(radius=0.28, fill_color="#D8D8D8", fill_opacity=0.95, stroke_width=0)
        moon.move_to([3.0, 0.0, 0])
        moon_label = Text("not to scale", font_size=16, color=TEXT).next_to(moon, UP, buff=0.1)

        arrow_a = Arrow(
            [-3.4, -0.9, 0], [-3.4, -1.55, 0], color=RED, stroke_width=5, buff=0
        )
        lab_a = MathTex("9.8", font_size=24, color=RED).next_to(arrow_a, DOWN, buff=0.05)
        arrow_m = Arrow(
            [3.0, -0.6, 0], [3.0, -0.82, 0], color=RED, stroke_width=2, buff=0
        )
        lab_m = MathTex("0.0027", font_size=20, color=RED).next_to(arrow_m, DOWN, buff=0.05)

        dist_line = Line(
            [-3.4, 0.55, 0], [3.0, 0.55, 0], color=YELL, stroke_width=4
        )
        dist_label = MathTex("60R", font_size=26, color=YELL).move_to([-0.2, 0.85, 0])
        ratio = MathTex(r"\times \tfrac{1}{60^2}", font_size=28, color=TEXT).move_to(
            [0.0, -1.6, 0]
        )
        sq = MathTex("60^2 = 3{,}600", font_size=26, color=YELL).move_to(
            [0.0, -2.5, 0]
        )

        s2 = VGroup(
            earth,
            moon,
            moon_label,
            arrow_a,
            lab_a,
            arrow_m,
            lab_m,
            dist_line,
            dist_label,
            ratio,
            sq,
        )
        self.play(
            FadeIn(earth, shift=0.2 * DOWN),
            FadeIn(moon, shift=0.2 * DOWN),
            Write(moon_label),
            run_time=0.9,
        )
        self.play(
            GrowArrow(arrow_a),
            Write(lab_a),
            GrowArrow(arrow_m),
            Write(lab_m),
            run_time=0.9,
        )
        self.play(
            Create(dist_line),
            Write(dist_label),
            run_time=1.0,
        )
        self.play(Write(ratio), run_time=0.7)
        self.play(Write(sq), run_time=0.7)
        self.wait(2.25)  # scene 2: 0.15+0.9+0.9+1.0+0.7+0.7+2.25 = 7.3 -> t = 10.0

        # ---------------- Scene 3 : prediction (9.9 - 13.4) ----------------
        self.play(FadeOut(s2), run_time=0.15)
        calc1 = MathTex("9.8 \div 3{,}600", font_size=34, color=TEXT)
        calc2 = MathTex(r"\approx 0.0027\,\mathrm{m/s^2}", font_size=36, color=YELL)
        calc1.move_to([0, 0.55, 0])
        calc2.move_to([0, -0.25, 0])
        s3 = VGroup(calc1, calc2)
        self.play(Write(calc1), run_time=1.0)
        self.play(Write(calc2), run_time=1.0)
        self.wait(1.35)  # scene 3: 0.15+1.0+1.0+1.35 = 3.5 -> t = 13.4

        # ---------------- Scene 4 : Moon's own motion (13.4 - 17.0) ---------
        self.play(FadeOut(s3), run_time=0.15)
        earth2 = Circle(radius=0.75, fill_color=BLUE, fill_opacity=0.9, stroke_width=0)
        earth2.move_to([-3.6, 0.0, 0])
        moon2 = Circle(radius=0.26, fill_color="#D8D8D8", fill_opacity=0.95, stroke_width=0)
        moon2.move_to([-3.6 + 2.6, 0.0, 0])

        orbit = Circle(radius=2.6, color=BLUE, stroke_opacity=0.15, stroke_width=2)
        orbit.move_to([-3.6, 0.0, 0])

        # at rightmost point: tangent (velocity) is up, radial (acceleration) is left
        vel_arrow = Arrow(
            moon2.get_center(),
            moon2.get_center() + [0, 0.62, 0],
            color=GRN,
            stroke_width=4,
            buff=0,
        )
        acc_arrow = Arrow(
            moon2.get_center(),
            earth2.get_center(),
            color=RED,
            stroke_width=4,
            buff=0,
        )

        formula = MathTex(
            r"a = \tfrac{4\pi^2 r}{T^2} \approx 0.0027\,\mathrm{m/s^2}",
            font_size=28,
            color=TEXT,
        ).move_to([0.55, 2.2, 0])
        val1 = MathTex("0.0027", font_size=26, color=TEXT).move_to([-1.35, -1.95, 0])
        val2 = MathTex("0.0027", font_size=26, color=YELL).move_to([1.35, -1.95, 0])
        check = MathTex(r"\checkmark", font_size=30, color=GRN).move_to(
            [0.0, -1.95, 0]
        )

        s4 = VGroup(earth2, orbit, moon2, vel_arrow, acc_arrow, formula, val1, val2, check)
        self.play(
            FadeIn(earth2, shift=0.2 * DOWN),
            Create(orbit),
            FadeIn(moon2, shift=0.2 * DOWN),
            Create(vel_arrow),
            Create(acc_arrow),
            run_time=0.7,
        )
        self.add(vel_arrow, acc_arrow)
        group = VGroup(moon2, vel_arrow, acc_arrow)
        self.play(
            Rotate(group, angle=1.8, about_point=earth2.get_center()),
            Write(formula),
            run_time=1.0,
        )
        self.play(Write(val1), Write(val2), Write(check), run_time=0.8)
        self.wait(0.55)  # scene 4: 0.15+0.7+1.0+0.8+0.55 = 3.6 -> t = 17.0

