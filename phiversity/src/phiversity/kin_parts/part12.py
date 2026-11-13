PART = [
{
 "narration":
  "Dimensional analysis verifies any kinematic formula: each side "
  "must close in M, L and T. Significant figures record the "
  "precision of measurement: a result cannot be more precise than "
  "its least precise input. Uncertainties propagate through "
  "formulas: for a product, relative errors add; for a sum, "
  "absolute errors add. These checks turn a calculation into a "
  "trustworthy prediction.",
 "visual": {"style": "dimensional analysis", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment64(Scene):
    def construct(self):
        head = Text("LESSON 65 - DIMENSIONAL ANALYSIS, SIGNIFICANT FIGURES",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"[v^{2}]=[2as]=L^{2}T^{-2}\ \checkmark", font_size=31,
                     color=T.result_final)
        r2 = MathTex(r"\text{product: }\frac{\delta q}{q}=\frac{\delta a}{a}+\frac{\delta b}{b}",
                     font_size=29, color=T.result_intermediate)
        r3 = MathTex(r"\text{sum: }\delta(a+b)=\delta a+\delta b",
                     font_size=29, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.46)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.7)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(3.0)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "Experiments confirm the assumptions. The classic free-fall "
  "experiment drops a ball from known heights and records the fall "
  "times; plotting height against time squared gives a straight "
  "line whose slope is g over two, so g is twice the slope. The "
  "projectile range experiment launches balls at fixed speed and "
  "records the range at several angles; the maximum at forty-five "
  "degrees and the sine-two-theta curve confirm the range formula. "
  "Photogates and motion sensors digitize the same measurements.",
 "visual": {"style": "experiments", "transition": "fade"},
 "code": r'''
from manim import *


class Segment65(Scene):
    def construct(self):
        head = Text("LESSON 66 - EXPERIMENTS: FREE FALL AND RANGE",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"h=\frac{1}{2}gt^{2}\ \Rightarrow\ \text{slope of }h\text{-}t^{2}\ "
                     r"\text{graph}=\frac{g}{2}", font_size=29,
                     color=T.result_final)
        r2 = MathTex(r"R=\frac{u^{2}\sin2\theta}{g}\ \Rightarrow\ "
                     r"\text{maximum at }45^{\circ}", font_size=29,
                     color=T.result_final)
        r3 = MathTex(r"\text{photogate: }v=\frac{\Delta x}{\Delta t}",
                     font_size=29, color=T.result_intermediate)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.46)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.9)
        box2 = SurroundingRectangle(r2, buff=0.12, color=T.result_final)
        self.play(Create(box2), run_time=0.7)
        self.wait(3.0)
        self.play(Write(r3), run_time=1.6)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "Video analysis tracks a point frame by frame and fits the "
  "coordinates. Numerical modelling, such as Euler's method, "
  "approximates the integrals of kinematics: stepping time by small "
  "increments, updating velocity by a times delta t and position by "
  "v times delta t. The approximation improves as the step shrinks "
  "and remains stable when the step is small enough. This is how "
  "complex kinematics is computed in practice.",
 "visual": {"style": "numerical", "transition": "slide-up"},
 "code": r'''
from manim import *


class Segment66(Scene):
    def construct(self):
        head = Text("LESSON 67 - VIDEO ANALYSIS AND NUMERICAL MODELLING",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"v_{n+1}=v_n+a_n\Delta t,\qquad x_{n+1}=x_n+v_n\Delta t",
                     font_size=29, color=T.result_final)
        r2 = MathTex(r"\text{Euler: error }\sim\Delta t;\ \text{smaller step, better}",
                     font_size=28, color=T.result_intermediate)
        r3 = MathTex(r"\text{video: track }(x,y)\ \text{per frame, fit kinematics}",
                     font_size=28, color=T.text_secondary)
        rows = VGroup(r1, r2, r3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.44)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.8)
        self.play(Write(r3), run_time=1.6)
        self.wait(2.8)
        self.wait(6)
''',
},
{
 "narration":
  "Finally, graph fitting extracts the laws from data. If a scatter "
  "plot is curved, choose new variables that make the relation "
  "linear, then fit a straight line. For free fall, plotting v "
  "squared against h linearizes v squared equals two g h, and the "
  "slope is two g. Linearization converts every power law into a "
  "line, and the fitted slope and intercept give the constants. "
  "This closes the chapter: from definitions to equations, to "
  "graphs, to experiments, and back to the same laws.",
 "visual": {"style": "graph fitting", "transition": "fade"},
 "code": r'''
from manim import *


class Segment67(Scene):
    def construct(self):
        head = Text("LESSON 68 - GRAPH FITTING AND LINEARIZATION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = MathTex(r"v^{2}=2gh:\ \text{plot }v^{2}\ \text{vs }h\ \Rightarrow\ "
                     r"\text{slope}=2g", font_size=29, color=T.result_final)
        r2 = MathTex(r"\text{power law }y=kx^{n}:\ \text{plot }\log y\ \text{vs }\log x",
                     font_size=29, color=T.result_intermediate)
        r3 = MathTex(r"\text{slope}=n,\ \text{intercept}=\log k", font_size=29,
                     color=T.result_intermediate)
        r4 = MathTex(r"\text{all kinematics laws verified by linear fits}",
                     font_size=27, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        fit_width(rows, 12.6)
        rows.next_to(rule, DOWN, buff=0.4)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(Write(r1), run_time=1.9)
        box1 = SurroundingRectangle(r1, buff=0.12, color=T.result_final)
        self.play(Create(box1), run_time=0.7)
        emphasize(self, r1, color=T.result_final, run_time=0.9)
        self.wait(3.2)
        self.play(Write(r2), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r3), run_time=1.7)
        self.wait(2.6)
        self.play(Write(r4), run_time=1.5)
        self.wait(3.0)
        self.wait(6)
''',
},
]
