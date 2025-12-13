from manim import *

class KutzbachCriterion(Scene):
    def construct(self):
        # -----------------------------
        # Title
        # -----------------------------
        title = Text(
            "Kutzbach Criterion for Planar Mechanisms",
            font_size=42
        )
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

        # -----------------------------
        # Formula (split for indexing)
        # -----------------------------
        formula = MathTex(
            "M", "=", 
            "3", "(", "N", "-", "1", ")", 
            "-", "2", "J", 
            "-", "H",
            font_size=48
        )

        self.play(Write(formula))
        self.wait(2)

        # -----------------------------
        # Explanation of terms
        # -----------------------------
        terms = VGroup(
            MathTex("M", ":", r"\text{Degrees of Freedom}", font_size=32),
            MathTex("N", ":", r"\text{Number of Links (including ground)}", font_size=32),
            MathTex("J", ":", r"\text{Number of Lower Pair Joints}", font_size=32),
            MathTex("H", ":", r"\text{Number of Higher Pair Joints}", font_size=32),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)

        # Move formula up
        self.play(formula.animate.to_edge(UP))

        # CORRECT staggered FadeIn (no LaggedStartMap bug)
        self.play(
            LaggedStart(
                *[FadeIn(term, shift=DOWN) for term in terms],
                lag_ratio=0.2
            )
        )
        self.wait(2)

        # -----------------------------
        # Highlight matching symbols
        # -----------------------------
        highlights = [
            (0, 0),   # M
            (4, 1),   # N
            (10, 2),  # J
            (12, 3),  # H
        ]

        for formula_index, term_index in highlights:
            self.play(
                Indicate(formula[formula_index], scale_factor=1.3),
                Indicate(terms[term_index][0], scale_factor=1.3),
            )
            self.wait(1)

        # -----------------------------
        # Cleanup
        # -----------------------------
        self.wait(2)
        self.play(FadeOut(VGroup(formula, terms)))
from manim import *
from manim import *

class KutzbachCriterionDerivation(Scene):
    def construct(self):
        # -----------------------------
        # Title
        # -----------------------------
        title = Text(
            "Derivation of Kutzbach Criterion",
            font_size=42
        )
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

        # -----------------------------
        # Initial Explanation
        # -----------------------------
        explanation = Text(
            "Consider a planar mechanism with N links and J lower pair joints.",
            font_size=32
        )
        self.play(Write(explanation))
        self.wait(3)
        self.play(FadeOut(explanation))

        # -----------------------------
        # Step 1: Total DOF without constraints
        # -----------------------------
        step1_title = Text(
            "Step 1: Total DOF without constraints",
            font_size=32,
            color=BLUE
        ).to_edge(UP)
        
        # Visual representation of links as lines with pin joints (hollow circles with black stroke)
        step1_visual = VGroup()
        
        # Link 1 (line with endpoints)
        link1_line = Line(LEFT*2.5, LEFT*1, color=YELLOW, stroke_width=6)
        link1_dot1 = Circle(radius=0.12, color=BLACK, fill_opacity=1, stroke_width=3, stroke_color=WHITE).move_to(link1_line.get_start())
        link1_dot2 = Circle(radius=0.12, color=BLACK, fill_opacity=1, stroke_width=3, stroke_color=WHITE).move_to(link1_line.get_end())
        link1_label = Text("Link 1", font_size=20).next_to(link1_line, DOWN, buff=0.3)
        
        # Link 2
        link2_line = Line(LEFT*0.5, RIGHT*1, color=YELLOW, stroke_width=6)
        link2_dot1 = Circle(radius=0.12, color=BLACK, fill_opacity=1, stroke_width=3, stroke_color=WHITE).move_to(link2_line.get_start())
        link2_dot2 = Circle(radius=0.12, color=BLACK, fill_opacity=1, stroke_width=3, stroke_color=WHITE).move_to(link2_line.get_end())
        link2_label = Text("Link 2", font_size=20).next_to(link2_line, DOWN, buff=0.3)
        
        # Link 3
        link3_line = Line(RIGHT*1.5, RIGHT*3, color=YELLOW, stroke_width=6)
        link3_dot1 = Circle(radius=0.12, color=BLACK, fill_opacity=1, stroke_width=3, stroke_color=WHITE).move_to(link3_line.get_start())
        link3_dot2 = Circle(radius=0.12, color=BLACK, fill_opacity=1, stroke_width=3, stroke_color=WHITE).move_to(link3_line.get_end())
        link3_label = Text("Link 3", font_size=20).next_to(link3_line, DOWN, buff=0.3)
        
        step1_visual.add(
            link1_line, link1_dot1, link1_dot2, link1_label,
            link2_line, link2_dot1, link2_dot2, link2_label,
            link3_line, link3_dot1, link3_dot2, link3_label
        )
        step1_visual.shift(UP*0.5)
        
        step1_explanation = Text(
            "Each link has 3 DOF in 2D plane (x, y, θ)",
            font_size=24,
            color=GREEN
        ).next_to(step1_visual, DOWN, buff=0.8)
        
        step1_math = MathTex(
            r"\text{Total DOF}", "=", "3", "(", "N", "-", "1", ")",
            font_size=40
        ).next_to(step1_explanation, DOWN, buff=0.5)
        
        step1_note = Text(
            "(N-1) because one link is fixed as ground",
            font_size=20,
            color=GRAY
        ).next_to(step1_math, DOWN, buff=0.3)

        self.play(Write(step1_title))
        self.play(Create(step1_visual))
        self.wait(1)
        self.play(Write(step1_explanation))
        self.wait(1)
        
        # Animate the 3 DOF - translation in x, y and rotation
        # X-direction movement
        x_arrow = Arrow(link2_line.get_center(), link2_line.get_center() + RIGHT*0.8, color=RED, buff=0)
        x_label = Text("x", font_size=18, color=RED).next_to(x_arrow, UP, buff=0.1)
        self.play(Create(x_arrow), Write(x_label))
        self.play(link2_line.animate.shift(RIGHT*0.4), 
                  link2_dot1.animate.shift(RIGHT*0.4),
                  link2_dot2.animate.shift(RIGHT*0.4),
                  link2_label.animate.shift(RIGHT*0.4))
        self.play(link2_line.animate.shift(LEFT*0.4), 
                  link2_dot1.animate.shift(LEFT*0.4),
                  link2_dot2.animate.shift(LEFT*0.4),
                  link2_label.animate.shift(LEFT*0.4))
        
        # Y-direction movement
        y_arrow = Arrow(link2_line.get_center(), link2_line.get_center() + UP*0.8, color=GREEN, buff=0)
        y_label = Text("y", font_size=18, color=GREEN).next_to(y_arrow, RIGHT, buff=0.1)
        self.play(ReplacementTransform(x_arrow, y_arrow), ReplacementTransform(x_label, y_label))
        self.play(link2_line.animate.shift(UP*0.4), 
                  link2_dot1.animate.shift(UP*0.4),
                  link2_dot2.animate.shift(UP*0.4),
                  link2_label.animate.shift(UP*0.4))
        self.play(link2_line.animate.shift(DOWN*0.4), 
                  link2_dot1.animate.shift(DOWN*0.4),
                  link2_dot2.animate.shift(DOWN*0.4),
                  link2_label.animate.shift(DOWN*0.4))
        
        # Rotation
        theta_arc = Arc(radius=0.5, start_angle=0, angle=PI/3, color=BLUE, arc_center=link2_line.get_center())
        theta_label = MathTex(r"\theta", font_size=24, color=BLUE).next_to(theta_arc, RIGHT, buff=0.1)
        self.play(ReplacementTransform(y_arrow, theta_arc), ReplacementTransform(y_label, theta_label))
        
        link2_group = VGroup(link2_line, link2_dot1, link2_dot2, link2_label)
        self.play(Rotate(link2_group, angle=PI/6, about_point=link2_line.get_center()))
        self.play(Rotate(link2_group, angle=-PI/6, about_point=link2_line.get_center()))
        
        self.play(FadeOut(theta_arc, theta_label))
        self.wait(1)
        
        self.play(Write(step1_math))
        self.play(Write(step1_note))
        self.wait(3)
        self.play(FadeOut(step1_title, step1_visual, step1_explanation, step1_math, step1_note))

        # -----------------------------
        # Step 2: Constraints from joints
        # -----------------------------
        step2_title = Text(
            "Step 2: Constraints from joints",
            font_size=32,
            color=BLUE
        ).to_edge(UP)
        
        # Visual representation of joints with links as lines
        step2_visual = VGroup()
        
        # Lower pair joint (revolute) - removes 2 DOF
        joint_link1_line = Line(LEFT*3, LEFT*1.5, color=YELLOW, stroke_width=6)
        joint_link1_dot1 = Circle(radius=0.12, color=BLACK, fill_opacity=1, stroke_width=3, stroke_color=WHITE).move_to(joint_link1_line.get_start())
        joint_link1_dot2 = Circle(radius=0.12, color=BLACK, fill_opacity=1, stroke_width=3, stroke_color=WHITE).move_to(joint_link1_line.get_end())
        
        joint_link2_line = Line(LEFT*1.5, LEFT*0, color=YELLOW, stroke_width=6)
        joint_link2_dot1 = Circle(radius=0.12, color=BLACK, fill_opacity=1, stroke_width=3, stroke_color=WHITE).move_to(joint_link2_line.get_start())
        joint_link2_dot2 = Circle(radius=0.12, color=BLACK, fill_opacity=1, stroke_width=3, stroke_color=WHITE).move_to(joint_link2_line.get_end())
        
        revolute_joint = Circle(radius=0.2, color=RED, fill_opacity=0.3, stroke_width=4).move_to(LEFT*1.5)
        revolute_label = Text("Revolute (J)", font_size=18, color=RED).next_to(revolute_joint, DOWN, buff=0.5)
        
        # Higher pair joint - removes 1 DOF
        higher_link1_line = Line(RIGHT*0.5, RIGHT*1.8, color=YELLOW, stroke_width=6)
        higher_link1_dot1 = Circle(radius=0.12, color=BLACK, fill_opacity=1, stroke_width=3, stroke_color=WHITE).move_to(higher_link1_line.get_start())
        higher_link1_dot2 = Circle(radius=0.12, color=BLACK, fill_opacity=1, stroke_width=3, stroke_color=WHITE).move_to(higher_link1_line.get_end())
        
        higher_link2_line = Arc(radius=0.8, start_angle=-PI/4, angle=PI/2, color=YELLOW, stroke_width=6).shift(RIGHT*2.5)
        higher_link2_dot1 = Circle(radius=0.12, color=BLACK, fill_opacity=1, stroke_width=3, stroke_color=WHITE).move_to(higher_link2_line.get_start())
        higher_link2_dot2 = Circle(radius=0.12, color=BLACK, fill_opacity=1, stroke_width=3, stroke_color=WHITE).move_to(higher_link2_line.get_end())
        
        higher_joint = Dot(color=ORANGE, radius=0.12).move_to(RIGHT*1.8)
        higher_label = Text("Cam (H)", font_size=18, color=ORANGE).next_to(higher_joint, DOWN, buff=0.5)
        
        step2_visual.add(
            joint_link1_line, joint_link1_dot1, joint_link1_dot2,
            joint_link2_line, joint_link2_dot1, joint_link2_dot2,
            revolute_joint, revolute_label,
            higher_link1_line, higher_link1_dot1, higher_link1_dot2,
            higher_link2_line, higher_link2_dot1, higher_link2_dot2,
            higher_joint, higher_label
        )
        step2_visual.shift(UP*0.5)
        
        step2_explanation = VGroup(
            Text("Lower pair (J): removes 2 DOF (only rotation allowed)", font_size=22, color=RED),
            Text("Higher pair (H): removes 1 DOF (point/line contact)", font_size=22, color=ORANGE)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(step2_visual, DOWN, buff=0.8)
        
        step2_math = MathTex(
            r"\text{Total Constraints}", "=", "2", "J", "+", "H",
            font_size=40
        ).next_to(step2_explanation, DOWN, buff=0.5)

        self.play(Write(step2_title))
        self.play(Create(step2_visual))
        
        # Demonstrate revolute joint constraint - can only rotate
        joint2_group = VGroup(joint_link2_line, joint_link2_dot1, joint_link2_dot2)
        self.play(Rotate(joint2_group, angle=PI/4, about_point=LEFT*1.5))
        self.play(Rotate(joint2_group, angle=-PI/2, about_point=LEFT*1.5))
        self.play(Rotate(joint2_group, angle=PI/4, about_point=LEFT*1.5))
        
        self.wait(1)
        self.play(Write(step2_explanation))
        self.wait(1)
        self.play(Write(step2_math))
        self.wait(3)
        self.play(FadeOut(step2_title, step2_visual, step2_explanation, step2_math))

        # -----------------------------
        # Step 3: Final Formula Derivation
        # -----------------------------
        step3_title = Text(
            "Step 3: Mobility (Degrees of Freedom)",
            font_size=32,
            color=BLUE
        ).to_edge(UP)
        
        derivation_steps = VGroup(
            MathTex(r"M", "=", r"\text{Total DOF}", "-", r"\text{Constraints}", font_size=36),
            MathTex(r"M", "=", "3", "(", "N", "-", "1", ")", "-", "(", "2", "J", "+", "H", ")", font_size=36),
            MathTex(r"M", "=", "3", "(", "N", "-", "1", ")", "-", "2", "J", "-", "H", font_size=36)
        ).arrange(DOWN, buff=0.5)
        
        self.play(Write(step3_title))
        
        for step in derivation_steps:
            self.play(Write(step))
            self.wait(2)
        
        self.wait(2)
        
        # Highlight final formula
        box = SurroundingRectangle(derivation_steps[-1], color=GREEN, buff=0.2)
        final_label = Text(
            "Kutzbach Criterion (Mobility Equation)",
            font_size=28,
            color=GREEN
        ).next_to(box, DOWN, buff=0.3)
        
        self.play(Create(box))
        self.play(Write(final_label))
        self.wait(3)

        # -----------------------------
        # Resources and References
        # -----------------------------
        self.play(FadeOut(step3_title, derivation_steps, box, final_label))
        
        resources_title = Text(
            "Additional Resources",
            font_size=36,
            color=YELLOW
        ).to_edge(UP)
        
        resources = VGroup(
            Text("📚 Theory of Machines textbooks", font_size=24),
            Text("🔗 Wikipedia: Chebychev–Grübler–Kutzbach criterion", font_size=24),
            Text("🎓 Mechanism kinematics courses", font_size=24),
            Text("🔧 Practice: Apply to four-bar linkage, slider-crank", font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4).next_to(resources_title, DOWN, buff=0.5)
        
        self.play(Write(resources_title))
        for resource in resources:
            self.play(Write(resource))
            self.wait(0.5)
        
        self.wait(3)
        
        # -----------------------------
        # Cleanup
        # -----------------------------
        self.play(FadeOut(resources_title, resources))