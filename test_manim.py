from manim import *


# ─────────────────────────────────────────────
#  SCENE 1 — Title Card
# ─────────────────────────────────────────────
class TitleScene(Scene):
    def construct(self):
        self.camera.background_color = "#1a1a2e"

        title = Text("MathSolver", font_size=60, color="#00d4aa")
        subtitle = Text("Step by Step Math", font_size=36, color="#ffd60a")
        subtitle.next_to(title, DOWN, buff=0.4)

        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle), run_time=1.0)
        self.wait(2)


# ─────────────────────────────────────────────
#  SCENE 2 — Problem Statement
# ─────────────────────────────────────────────
class ProblemScene(Scene):
    def construct(self):
        self.camera.background_color = "#1a1a2e"

        label = Text("TODAY'S PROBLEM", font_size=28,
                     color="#00d4aa", weight=BOLD)
        label.to_edge(UP, buff=0.5)

        box = RoundedRectangle(
            corner_radius=0.3, width=10, height=2,
            color="#4cc9f0", fill_color="#0f3460", fill_opacity=1
        )
        box.move_to(ORIGIN + UP * 0.3)

        problem = Text("Solve:  2x + 5 = 13",
                       font_size=48, color="#ffd60a", weight=BOLD)
        problem.move_to(box.get_center())

        statement = Text("Let us break this down step by step!",
                         font_size=26, color="#ffffff")
        statement.next_to(box, DOWN, buff=0.5)

        self.play(FadeIn(label), run_time=0.5)
        self.play(Create(box), run_time=0.6)
        self.play(Write(problem), run_time=1.2)
        self.play(FadeIn(statement, shift=UP * 0.2), run_time=0.8)
        self.wait(2.5)


# ─────────────────────────────────────────────
#  SCENE 3 — Math Step
# ─────────────────────────────────────────────
class StepScene(Scene):
    def construct(self):
        self.camera.background_color = "#1a1a2e"

        # Step badge
        circle = Circle(radius=0.4, color="#00d4aa",
                        fill_color="#00d4aa", fill_opacity=1)
        num = Text("1", font_size=28, color="#1a1a2e", weight=BOLD)
        badge = VGroup(circle, num)
        badge.to_corner(UL, buff=0.5)

        # Step title
        title = Text("Subtract 5 from both sides",
                     font_size=32, color="#ffffff", weight=BOLD)
        title.next_to(badge, RIGHT, buff=0.3)

        # Divider
        divider = Line(LEFT * 6, RIGHT * 6,
                       color="#00d4aa", stroke_width=1.5)
        divider.next_to(VGroup(badge, title), DOWN, buff=0.3)

        # Math expressions
        math1 = MathTex("2x + 5 = 13", font_size=56, color="#ffffff")
        math2 = MathTex("2x = 13 - 5", font_size=56, color="#ffffff")
        math3 = MathTex("2x = 8", font_size=56, color="#ffd60a")

        for m in [math1, math2, math3]:
            m.move_to(ORIGIN + UP * 0.3)

        # Rule banner
        banner = Rectangle(
            width=12, height=0.9,
            fill_color="#534AB7", fill_opacity=1
        )
        banner.to_edge(DOWN, buff=0.8)

        rule = Text(
            "Rule: Subtraction Property of Equality",
            font_size=22, color="#ffffff", weight=BOLD
        )
        rule.move_to(banner.get_center())

        explanation = Text(
            "What we do to one side, we do to the other side!",
            font_size=20, color="#a8b2d8"
        )
        explanation.next_to(banner, DOWN, buff=0.15)

        # Animate
        self.play(FadeIn(badge), Write(title), run_time=0.8)
        self.play(Create(divider), run_time=0.4)
        self.play(Write(math1), run_time=1.2)
        self.wait(0.8)
        self.play(TransformMatchingTex(math1, math2), run_time=1.0)
        self.wait(0.8)
        self.play(TransformMatchingTex(math2, math3), run_time=1.0)
        self.play(
            math3.animate.scale(1.2),
            run_time=0.4
        )
        self.play(
            math3.animate.scale(1/1.2),
            run_time=0.3
        )
        self.play(
            FadeIn(banner, shift=UP * 0.2),
            Write(rule),
            run_time=0.7
        )
        self.play(FadeIn(explanation), run_time=0.5)
        self.wait(2.5)


# ─────────────────────────────────────────────
#  SCENE 4 — Summary
# ─────────────────────────────────────────────
class SummaryScene(Scene):
    def construct(self):
        self.camera.background_color = "#1a1a2e"

        title = Text("SOLUTION", font_size=36,
                     color="#00d4aa", weight=BOLD)
        title.to_edge(UP, buff=0.5)

        # Answer box
        ans_box = RoundedRectangle(
            corner_radius=0.3, width=8, height=2,
            color="#00d4aa", fill_color="#0f3460",
            fill_opacity=1, stroke_width=3
        )
        ans_box.next_to(title, DOWN, buff=0.5)

        answer = Text("x = 4", font_size=52,
                      color="#ffd60a", weight=BOLD)
        answer.move_to(ans_box.get_center())

        # Rules used
        rules_title = Text("Rules used:", font_size=24,
                           color="#4cc9f0", weight=BOLD)
        rules_title.next_to(ans_box, DOWN, buff=0.4)

        rule1 = Text("• Subtraction Property of Equality",
                     font_size=22, color="#a8b2d8")
        rule1.next_to(rules_title, DOWN, buff=0.2)
        rule1.align_to(rules_title, LEFT)

        rule2 = Text("• Division Property of Equality",
                     font_size=22, color="#a8b2d8")
        rule2.next_to(rule1, DOWN, buff=0.1)
        rule2.align_to(rule1, LEFT)

        subscribe = Text(
            "Subscribe for more daily math solutions!",
            font_size=22, color="#ffd60a"
        )
        subscribe.to_edge(DOWN, buff=0.5)

        # Animate
        self.play(Write(title), run_time=0.8)
        self.play(Create(ans_box), run_time=0.6)
        self.play(Write(answer), run_time=1.0)
        self.play(FadeIn(rules_title), run_time=0.5)
        self.play(FadeIn(rule1, shift=RIGHT * 0.3), run_time=0.4)
        self.play(FadeIn(rule2, shift=RIGHT * 0.3), run_time=0.4)
        self.play(FadeIn(subscribe, shift=UP * 0.2), run_time=0.6)
        self.wait(3)