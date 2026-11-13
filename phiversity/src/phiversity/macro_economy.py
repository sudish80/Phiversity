TITLE = "Q7 - INFLATION, UNEMPLOYMENT AND MACRO POLICY"

QUESTION = {
    "display":
        "A country faces rising inflation, increasing unemployment, "
        "declining GDP growth and a widening balance-of-payments deficit. "
        "(a) Define inflation, unemployment, GDP and balance of payments. "
        "(b) Explain the major causes of inflation in a developing "
        "economy. (c) Differentiate demand-pull and cost-push inflation "
        "with examples. (d) With a diagram, explain the relationship "
        "between aggregate demand and aggregate supply. (e) Analyse the "
        "effects of inflation and unemployment on growth and living "
        "standards. (f) Explain the monetary and fiscal policies to "
        "control inflation and unemployment. (g) Evaluate expansionary and "
        "contractionary policies for macroeconomic stability. (h) Suggest "
        "policies for a developing country like Nepal.",
    "speech":
        "A country's economy is experiencing rising inflation, increasing "
        "unemployment, declining GDP growth and a widening balance of "
        "payments deficit. Part a, define inflation, unemployment, GDP and "
        "the balance of payments. Part b, explain the major causes of "
        "inflation in a developing economy. Part c, differentiate between "
        "demand pull and cost push inflation with suitable examples. Part "
        "d, using an appropriate diagram, explain the relationship between "
        "aggregate demand and aggregate supply. Part e, analyse the "
        "effects of inflation and unemployment on economic growth and "
        "living standards. Part f, explain the monetary and fiscal "
        "policies that a central bank and government can adopt to control "
        "inflation and unemployment. Part g, evaluate the effectiveness of "
        "expansionary and contractionary policies in achieving "
        "macroeconomic stability. Part h, suggest appropriate policies for "
        "a developing country like Nepal to achieve sustainable economic "
        "growth.",
}

QUESTION_CODE = r'''from manim import *


class QuestionScene(Scene):
    def construct(self):
        badge = Text("QUESTION 7 - MACROECONOMIC POLICY", font_size=26,
                     color=T.highlight_secondary)
        badge.move_to(UP * 3.3)
        line = Underline(badge, buff=0.15)
        data = Text("inflation up + unemployment up + GDP growth down + "
                    "BoP deficit widening", font_size=25, color=T.constant)
        c_chem = Text("SYMPTOMS", font_size=20, color=T.highlight_secondary)
        r_chem = Text(
            "stagflation-like mix\n"
            "demand, supply and structural pressures together",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_math = Text("TASKS", font_size=20, color=T.highlight_secondary)
        r_math = Text(
            "a  define the four key terms\n"
            "b-c  causes; demand-pull vs cost-push\n"
            "d  AD-AS diagram and equilibrium\n"
            "e-g  effects; policy tools; evaluation\n"
            "h  Nepal-specific policy package",
            font_size=23, color=T.text_primary, line_spacing=0.8)
        c_econ = Text("TOOLS", font_size=20, color=T.highlight_secondary)
        r_econ = Text(
            "monetary: policy rate, CRR, open market\n"
            "fiscal: spending, taxes, deficit, subsidies\n"
            "supply-side: productivity, infrastructure",
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
        self.wait(10.51)
        self.play(FadeIn(chem, shift=0.2 * UP), run_time=1.0)
        self.wait(12.61)
        self.play(FadeIn(maths, shift=0.2 * UP), run_time=1.0)
        self.wait(16.81)
        self.play(FadeIn(econ, shift=0.2 * UP), run_time=1.0)
        self.wait(12.61)
        self.play(FadeOut(VGroup(badge, line)), run_time=0.5)
        self.play(rows.animate.scale(0.62).to_edge(UP, buff=0.22), run_time=1.0)
        self.wait(4.2)
'''

SEG0 = r'''from manim import *


class Segment0(Scene):
    def construct(self):
        head = Text("Q7 (a) - DEFINITIONS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("Inflation: sustained rise in the general price level; "
                  "money buys less", font_size=25, color=T.text_primary)
        r2 = Text("Unemployment: share of the labour force able and willing "
                  "to work but jobless", font_size=25, color=T.text_primary)
        r3 = Text("GDP: market value of final goods and services produced "
                  "within a country in a year", font_size=25,
                  color=T.text_primary)
        r4 = Text("Balance of payments: record of all transactions with the "
                  "rest of the world", font_size=25, color=T.text_primary)
        r4b = Text("(current account + capital and financial account)",
                   font_size=22, color=T.text_secondary)
        rows = VGroup(r1, r2, r3, r4, r4b)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 11.6)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(FadeIn(r1, shift=0.2 * UP), run_time=1.3)
        self.wait(4.0)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.3)
        self.wait(4.0)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.3)
        self.wait(4.0)
        self.play(FadeIn(VGroup(r4, r4b), shift=0.2 * UP), run_time=1.3)
        self.wait(4.5)
        self.wait(6)
'''

SEG1 = r'''from manim import *


class Segment1(Scene):
    def construct(self):
        head = Text("Q7 (b) - CAUSES OF INFLATION IN A DEVELOPING ECONOMY",
                    font_size=24, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        demand = VGroup(
            Text("DEMAND-SIDE", font_size=21, color=T.highlight_secondary),
            Text("- rapid money-supply growth", font_size=22,
                 color=T.text_primary),
            Text("- deficit financing by the state", font_size=22,
                 color=T.text_primary),
            Text("- credit expansion by banks", font_size=22,
                 color=T.text_primary),
            Text("- rising remittances and demand", font_size=22,
                 color=T.text_primary),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        cost = VGroup(
            Text("COST / SUPPLY-SIDE", font_size=21,
                 color=T.highlight_secondary),
            Text("- imported fuel and input prices", font_size=22,
                 color=T.text_primary),
            Text("- currency depreciation", font_size=22,
                 color=T.text_primary),
            Text("- wage and administered-price hikes", font_size=22,
                 color=T.text_primary),
            Text("- supply shocks and shortages", font_size=22,
                 color=T.text_primary),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        struct = VGroup(
            Text("STRUCTURAL", font_size=21, color=T.highlight_secondary),
            Text("- weak infrastructure and bottlenecks", font_size=22,
                 color=T.text_primary),
            Text("- food scarcity and hoarding", font_size=22,
                 color=T.text_primary),
            Text("- low productivity, import dependence", font_size=22,
                 color=T.text_primary),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        left = VGroup(demand, cost).arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        panels = VGroup(left, struct).arrange(RIGHT, aligned_edge=UP, buff=0.9)
        panels.move_to(DOWN * 0.5)
        fit_width(panels, 12.0)
        self.play(FadeIn(demand, shift=0.2 * UP), run_time=1.4)
        self.wait(5.0)
        self.play(FadeIn(cost, shift=0.2 * UP), run_time=1.4)
        self.wait(5.0)
        self.play(FadeIn(struct, shift=0.2 * UP), run_time=1.4)
        self.wait(5.0)
        self.wait(6)
'''

SEG2 = r'''from manim import *


class Segment2(Scene):
    def construct(self):
        head = Text("Q7 (c) - DEMAND-PULL vs COST-PUSH INFLATION",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        left = VGroup(
            Text("DEMAND-PULL", font_size=22, color=T.graph_function),
            Text("AD rises faster than AS", font_size=22,
                 color=T.text_primary),
            Text("'too much money chasing", font_size=21, color=T.text_primary),
            Text(" too few goods'", font_size=21, color=T.text_primary),
            Text("Example: stimulus spending,", font_size=21,
                 color=T.text_secondary),
            Text("cheap credit, remittance boom", font_size=21,
                 color=T.text_secondary),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        right = VGroup(
            Text("COST-PUSH", font_size=22, color=T.result_intermediate),
            Text("AS falls as costs rise", font_size=22,
                 color=T.text_primary),
            Text("higher input and wage costs", font_size=21,
                 color=T.text_primary),
            Text("squeeze firms' margins", font_size=21,
                 color=T.text_primary),
            Text("Example: oil-price shock,", font_size=21,
                 color=T.text_secondary),
            Text("imported inflation, wage push", font_size=21,
                 color=T.text_secondary),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        div = Line(DOWN * 2.4, UP * 2.0, color=T.grid, stroke_width=2)
        panels = VGroup(left, div, right).arrange(RIGHT, buff=0.7)
        panels.move_to(DOWN * 0.4)
        fit_width(panels, 12.0)
        self.play(FadeIn(left, shift=0.2 * UP), run_time=1.4)
        self.wait(5.0)
        self.play(Create(div), run_time=0.6)
        self.play(FadeIn(right, shift=0.2 * UP), run_time=1.4)
        self.wait(6.0)
        self.wait(6)
'''

SEG3 = r'''from manim import *


class Segment3(Scene):
    def construct(self):
        head = Text("Q7 (d) - AGGREGATE DEMAND AND AGGREGATE SUPPLY",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("AD: total planned spending", font_size=23,
                  color=T.text_primary)
        r2 = Text("at each price level", font_size=23, color=T.text_primary)
        r3 = Text("AS: total output firms", font_size=23, color=T.text_primary)
        r4 = Text("supply at each price level", font_size=23,
                  color=T.text_primary)
        r5 = Text("Equilibrium: AD = AS gives", font_size=23,
                  color=T.text_primary)
        r6 = Text("price level P* and output Y*", font_size=23,
                  color=T.text_primary)
        r7 = Text("AD shifts right -> P rises", font_size=22,
                  color=T.graph_function)
        r8 = Text("(demand-pull inflation)", font_size=22,
                  color=T.graph_function)
        r9 = Text("AS shifts left -> P rises, Y falls", font_size=22,
                  color=T.result_intermediate)
        r10 = Text("(cost-push, stagflation)", font_size=22,
                  color=T.result_intermediate)
        left = VGroup(r1, r2, r3, r4, r5, r6, r7, r8, r9, r10)
        left.arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        fit_width(left, 6.6)
        left.next_to(rule, DOWN, buff=0.4)
        left.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if left.height > 6.2:
            left.scale_to_fit_height(6.2)
        axes = Axes(x_range=[0, 10, 1], y_range=[0, 10, 1],
                    x_length=4.6, y_length=3.4,
                    axis_config={"color": T.text_muted, "stroke_width": 1.5,
                                 "include_tip": False})
        axes.move_to(RIGHT * 3.85 + DOWN * 0.7)
        ad = axes.plot(lambda x: 9 - 0.7 * x, x_range=[0.5, 9.2],
                       color=T.graph_function, stroke_width=4)
        asup = axes.plot(lambda x: 2 + 0.7 * x, x_range=[0.5, 9.2],
                         color=T.result_intermediate, stroke_width=4)
        ad2 = axes.plot(lambda x: 11 - 0.7 * x, x_range=[0.5, 9.2],
                        color=T.graph_function, stroke_width=3)
        e1 = Dot(axes.c2p(5, 5.5), radius=0.08, color=T.graph_point)
        e2 = Dot(axes.c2p(6.43, 6.5), radius=0.08, color=T.graph_point)
        d1 = DashedLine(axes.c2p(0, 5.5), axes.c2p(5, 5.5),
                        color=T.text_secondary, stroke_width=2)
        d2 = DashedLine(axes.c2p(0, 6.5), axes.c2p(6.43, 6.5),
                        color=T.text_secondary, stroke_width=2)
        p_lab = MathTex(r"P", font_size=24, color=T.text_secondary)
        p_lab.next_to(axes, LEFT, buff=0.15).shift(UP * 1.3)
        y_lab = MathTex(r"Y", font_size=24, color=T.text_secondary)
        y_lab.next_to(axes, DOWN, buff=0.15).shift(RIGHT * 1.9)
        ad_lab = MathTex(r"AD", font_size=23, color=T.graph_function)
        ad_lab.next_to(ad.get_end(), RIGHT, buff=0.1)
        as_lab = MathTex(r"AS", font_size=23, color=T.result_intermediate)
        as_lab.next_to(asup.get_end(), RIGHT, buff=0.1)
        ad2_lab = MathTex(r"AD'", font_size=23, color=T.graph_function)
        ad2_lab.next_to(ad2.get_end(), RIGHT, buff=0.1)
        e_lab = MathTex(r"E", font_size=22, color=T.graph_point)
        e_lab.next_to(e1, LEFT, buff=0.1)
        e2_lab = MathTex(r"E'", font_size=22, color=T.graph_point)
        e2_lab.next_to(e2, RIGHT, buff=0.1)
        self.play(Write(r1), Write(r2), run_time=1.2)
        self.wait(2.4)
        self.play(Write(r3), Write(r4), run_time=1.2)
        self.wait(2.4)
        self.play(Write(r5), Write(r6), Create(axes), Create(ad),
                  Create(asup), run_time=2.0)
        self.play(FadeIn(e1), Write(e_lab), Write(p_lab), Write(y_lab),
                  run_time=1.2)
        self.play(Create(d1), run_time=0.8)
        self.wait(2.8)
        self.play(Write(r7), Write(r8), Create(ad2), run_time=1.6)
        self.play(FadeIn(e2), Write(e2_lab), Create(d2), run_time=1.2)
        self.wait(2.8)
        self.play(Write(r9), Write(r10), run_time=1.6)
        self.wait(4.01)
        self.wait(4.81)
'''

SEG4 = r'''from manim import *


class Segment4(Scene):
    def construct(self):
        head = Text("Q7 (e) - EFFECTS ON GROWTH AND LIVING STANDARDS",
                    font_size=25, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        left = VGroup(
            Text("INFLATION", font_size=22, color=T.cancel_mark),
            Text("- erodes real incomes and", font_size=21,
                 color=T.text_primary),
            Text("  savings of fixed earners", font_size=21,
                 color=T.text_primary),
            Text("- hurts the poor and pensioners", font_size=21,
                 color=T.text_primary),
            Text("- uncertainty cuts investment", font_size=21,
                 color=T.text_primary),
            Text("- exports dearer, BoP worsens", font_size=21,
                 color=T.text_primary),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        right = VGroup(
            Text("UNEMPLOYMENT", font_size=22, color=T.result_intermediate),
            Text("- wastes labour and skills", font_size=21,
                 color=T.text_primary),
            Text("- output below potential (Okun)", font_size=21,
                 color=T.text_primary),
            Text("- poverty, inequality, unrest", font_size=21,
                 color=T.text_primary),
            Text("- lower tax revenue, weaker", font_size=21,
                 color=T.text_primary),
            Text("  demand and growth", font_size=21, color=T.text_primary),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        div = Line(DOWN * 2.4, UP * 2.0, color=T.grid, stroke_width=2)
        panels = VGroup(left, div, right).arrange(RIGHT, buff=0.7)
        panels.move_to(DOWN * 0.3)
        fit_width(panels, 12.0)
        self.play(FadeIn(left, shift=0.2 * UP), run_time=1.4)
        self.wait(5.0)
        self.play(Create(div), run_time=0.6)
        self.play(FadeIn(right, shift=0.2 * UP), run_time=1.4)
        self.wait(6.0)
        self.wait(6)
'''

SEG5 = r'''from manim import *


class Segment5(Scene):
    def construct(self):
        head = Text("Q7 (f) - MONETARY AND FISCAL POLICY TOOLS", font_size=25,
                    color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        left = VGroup(
            Text("MONETARY (central bank)", font_size=21,
                 color=T.graph_function),
            Text("raise policy / repo rate", font_size=21,
                 color=T.text_primary),
            Text("raise CRR and SLR", font_size=21, color=T.text_primary),
            Text("sell securities (open market)", font_size=21,
                 color=T.text_primary),
            Text("credit controls, moral suasion", font_size=21,
                 color=T.text_primary),
            Text("-> less money, lower demand", font_size=20,
                 color=T.text_secondary),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        right = VGroup(
            Text("FISCAL (government)", font_size=21,
                 color=T.result_intermediate),
            Text("cut public spending", font_size=21, color=T.text_primary),
            Text("raise taxes, broaden the base", font_size=21,
                 color=T.text_primary),
            Text("reduce deficit, target subsidies", font_size=21,
                 color=T.text_primary),
            Text("supply-side: skills, infrastructure", font_size=21,
                 color=T.text_primary),
            Text("-> cool demand, raise capacity", font_size=20,
                 color=T.text_secondary),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        div = Line(DOWN * 2.4, UP * 2.0, color=T.grid, stroke_width=2)
        panels = VGroup(left, div, right).arrange(RIGHT, buff=0.7)
        panels.move_to(DOWN * 0.3)
        fit_width(panels, 12.2)
        self.play(FadeIn(left, shift=0.2 * UP), run_time=1.4)
        self.wait(5.0)
        self.play(Create(div), run_time=0.6)
        self.play(FadeIn(right, shift=0.2 * UP), run_time=1.4)
        self.wait(6.0)
        self.wait(6)
'''

SEG6 = r'''from manim import *


class Segment6(Scene):
    def construct(self):
        head = Text("Q7 (g-h) - EVALUATION AND A POLICY PACKAGE FOR NEPAL",
                    font_size=24, color=T.text_secondary)
        head.to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.9, RIGHT * 6.9, color=T.grid, stroke_width=1)
        rule.next_to(head, DOWN, buff=0.12)
        rule.set_x(0.0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(rule), run_time=0.8)
        r1 = Text("Contractionary policy cools inflation but may raise "
                  "unemployment", font_size=24, color=T.text_primary)
        r2 = Text("Expansionary policy cuts unemployment but risks more "
                  "inflation", font_size=24, color=T.text_primary)
        r3 = Text("Limits: time lags, crowding out, expectations, supply "
                  "shocks, politics", font_size=24, color=T.text_primary)
        r4 = Text("Nepal: monetary discipline and fiscal consolidation",
                  font_size=24, color=T.result_final)
        r5 = Text("Raise farm and energy productivity; prune imports; "
                  "diversify tourism and exports", font_size=23,
                  color=T.text_primary)
        r6 = Text("Targeted social protection, skills, financial inclusion, "
                  "and FDI", font_size=23, color=T.text_primary)
        rows = VGroup(r1, r2, r3, r4, r5, r6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        fit_width(rows, 12.0)
        rows.next_to(rule, DOWN, buff=0.45)
        rows.align_to(rule, LEFT).shift(RIGHT * 0.4)
        if rows.height > 6.0:
            rows.scale_to_fit_height(6.0)
        self.play(FadeIn(r1, shift=0.2 * UP), run_time=1.3)
        self.wait(4.0)
        self.play(FadeIn(r2, shift=0.2 * UP), run_time=1.3)
        self.wait(4.0)
        self.play(FadeIn(r3, shift=0.2 * UP), run_time=1.3)
        self.wait(4.0)
        self.play(FadeIn(r4, shift=0.2 * UP), run_time=1.3)
        box4 = SurroundingRectangle(r4, buff=0.13, color=T.result_final)
        self.play(Create(box4), run_time=0.7)
        self.wait(3.5)
        self.play(FadeIn(r5, shift=0.2 * UP), run_time=1.3)
        self.wait(4.0)
        self.play(FadeIn(r6, shift=0.2 * UP), run_time=1.3)
        self.wait(4.5)
        self.wait(6)
'''

SEGMENTS = [
    {"narration":
     "Part a. Definitions. Inflation is a sustained rise in the general "
     "price level, so money buys less over time. Unemployment is the "
     "share of the labour force that is able and willing to work but "
     "cannot find a job. GDP is the market value of all final goods and "
     "services produced within a country in a year. The balance of "
     "payments records all economic transactions between a country's "
     "residents and the rest of the world, in the current account and the "
     "capital and financial accounts.",
     "visual": {"style": "definitions", "transition": "slide-up"},
     "code": SEG0},
    {"narration":
     "Part b. In a developing economy inflation usually has several "
     "sources at once. On the demand side, rapid money-supply growth, "
     "deficit financing, bank credit expansion and large remittance "
     "inflows raise spending. On the cost side, imported fuel and input "
     "prices, currency depreciation, wage settlements and administered "
     "price increases push costs up. Structurally, weak infrastructure, "
     "food scarcity, hoarding and import dependence create bottlenecks "
     "that keep prices rising.",
     "visual": {"style": "causes", "transition": "carry-over"},
     "code": SEG1},
    {"narration":
     "Part c. Demand-pull inflation occurs when aggregate demand rises "
     "faster than aggregate supply, the familiar case of too much money "
     "chasing too few goods. Examples are stimulus spending, cheap "
     "credit and a remittance boom. Cost-push inflation occurs when "
     "aggregate supply falls because production costs rise, squeezing "
     "firms' margins. Examples are an oil-price shock, imported "
     "inflation and a strong wage push.",
     "visual": {"style": "comparison", "transition": "fade"},
     "code": SEG2},
    {"narration":
     "Part d. The diagram plots the price level P against real output Y. "
     "Aggregate demand slopes downward and aggregate supply slopes "
     "upward. Their intersection gives the equilibrium price level P "
     "star and output Y star. If aggregate demand shifts right, the "
     "price level rises: that is demand-pull inflation. If aggregate "
     "supply shifts left, the price level rises while output falls, the "
     "cost-push case known as stagflation.",
     "visual": {"style": "AD-AS diagram", "transition": "fade"},
     "code": SEG3},
    {"narration":
     "Part e. Inflation erodes real incomes and savings, hits fixed "
     "earners and pensioners hardest, creates uncertainty that reduces "
     "investment, and makes exports dearer so the external deficit "
     "widens. Unemployment wastes labour and skills, holds output below "
     "its potential, and raises poverty, inequality and social unrest. "
     "Together they lower both growth and living standards.",
     "visual": {"style": "effects", "transition": "fade"},
     "code": SEG4},
    {"narration":
     "Part f. To control inflation a central bank uses contractionary "
     "monetary policy: it raises the policy rate, raises the cash and "
     "statutory liquidity ratios, sells securities in the open market, "
     "and uses credit controls and moral suasion. The government uses "
     "contractionary fiscal policy: cut spending, raise taxes, trim the "
     "deficit and target subsidies. To fight unemployment the same tools "
     "run in reverse, supported by supply-side spending on skills and "
     "infrastructure.",
     "visual": {"style": "policy tools", "transition": "fade"},
     "code": SEG5},
    {"narration":
     "Part g. Contractionary policy cools inflation but can raise "
     "unemployment, while expansionary policy cuts unemployment but "
     "risks more inflation, the classic policy trade-off. Effectiveness "
     "is limited by time lags, crowding out, shifting expectations, "
     "supply shocks and political constraints, so policies must be "
     "coordinated and credible. Part h, for Nepal the package is "
     "monetary discipline with fiscal consolidation, higher farm and "
     "energy productivity, fewer essential imports, diversified tourism "
     "and exports, targeted social protection, skills, financial "
     "inclusion and foreign direct investment.",
     "visual": {"style": "evaluation", "transition": "fade"},
     "code": SEG6},
]

LECTURE = {
    "title": TITLE,
    "preset": "lab",
    "format": "mixed",
    "question": QUESTION,
    "question_code": QUESTION_CODE,
    "segments": SEGMENTS,
}
