TITLE = "Q37 - COMPLETE KINEMATICS CHAPTER COURSE (1 HOUR)"

QUESTION = {
    "display":
        "COMPLETE KINEMATICS - MASTER COURSE. Fundamentals (mechanics, "
        "reference frames, coordinate systems, scalars/vectors, "
        "position, distance, displacement, speed, velocity, "
        "acceleration, dimensions). Linear motion (1D/rectilinear, "
        "uniform/non-uniform/accelerated, average vs instantaneous, "
        "equations of motion derived, stopping/braking/reaction, "
        "catch-up/overtaking). Graphical kinematics (x-t, v-t, a-t, "
        "slope, area, piecewise, differentiation/integration). Motion "
        "under gravity (free fall, vertical projection, tower/moving "
        "platform, two-body, variable g). Projectile motion (horizontal/"
        "oblique, trajectory, range, max height, T, complementary "
        "angles, elevated/inclined, moving target, envelope). Relative "
        "motion (relative vectors, river-boat, rain-man, wind-aircraft, "
        "swimmer crossing, pursuit). 2D/3D motion (vector calculus, "
        "parametric, polar, tangential/normal, Frenet-Serret). "
        "Circular motion (angular quantities, linear-angular, "
        "centripetal derivation, non-uniform, period/frequency, "
        "rolling). Constrained motion (string/pulley/wedge/rod/gears). "
        "Calculus kinematics (derivatives/integrals, a(t), a(x), a(v), "
        "jerk). Advanced (translating/rotating frames, Coriolis, rigid "
        "body, instantaneous centre, robots, SHM). Experimental "
        "(dimensional analysis, significant figures, free-fall/range "
        "experiments, numerical modelling, graph fitting).",
    "speech":
        "Complete kinematics master course. We will teach the whole "
        "chapter, slowly and in detail: fundamentals, linear motion, "
        "graphs, gravity, projectiles, relative motion, motion in two "
        "and three dimensions, circular motion, constrained motion, "
        "calculus-based kinematics, advanced applications, and "
        "experimental analysis. Every formula will be derived from "
        "first principles with diagrams and worked reasoning.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 37 - COMPLETE KINEMATICS CHAPTER",
                     font_size=26, color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        inst = Text("Master course: teach the chapter slowly, in detail. "
                    "Derive every formula from first principles; use "
                    "diagrams, figures and graphs throughout.",
                    font_size=19, color=T.text_primary)
        fit_width(inst, 12.7)
        sections = [
            "1  Fundamentals (1-20)",
            "2  Linear Motion (21-45)",
            "3  Graphical Kinematics (46-59)",
            "4  Motion Under Gravity (60-75)",
            "5  Projectile Motion (76-100)",
            "6  Relative Motion (101-120)",
            "7  2D/3D Motion (121-140)",
            "8  Circular Motion (141-162)",
            "9  Constrained Motion (163-180)",
            "10 Calculus-Based Kinematics (181-200)",
            "11 Advanced Applications (201-225)",
            "12 Experimental & Mathematical Analysis (226-240)",
        ]
        col = VGroup(*[Text(s, font_size=17, color=T.text_secondary)
                       for s in sections]).arrange(DOWN, aligned_edge=LEFT,
                                                   buff=0.14)
        fit_width(col, 12.7)
        block = VGroup(inst, col).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        block.move_to(DOWN * 0.3)
        self.play(FadeIn(badge, shift=0.3 * DOWN), Create(line), run_time=0.7)
        self.play(FadeIn(inst, shift=0.2 * UP), run_time=1.2)
        self.wait(4.0)
        self.play(FadeIn(col, shift=0.2 * UP), run_time=1.8)
        self.wait(8.0)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(block.animate.scale(0.72).to_edge(UP, buff=0.2), run_time=1.0)
        self.wait(2.0)
'''

from .kin_parts.part01 import PART as _P1
from .kin_parts.part02 import PART as _P2
from .kin_parts.part03 import PART as _P3
from .kin_parts.part04 import PART as _P4
from .kin_parts.part05 import PART as _P5
from .kin_parts.part06 import PART as _P6
from .kin_parts.part07 import PART as _P7
from .kin_parts.part08 import PART as _P8
from .kin_parts.part09 import PART as _P9
from .kin_parts.part10 import PART as _P10
from .kin_parts.part11 import PART as _P11
from .kin_parts.part12 import PART as _P12

SEGMENTS = _P1 + _P2 + _P3 + _P4 + _P5 + _P6 + _P7 + _P8 + _P9 + _P10 + _P11 + _P12

LECTURE = {
    "title": TITLE,
    "preset": "lab",
    "format": "mixed",
    "question": QUESTION,
    "question_code": QUESTION_CODE,
    "segments": SEGMENTS,
}
