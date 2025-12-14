from manim import *
import numpy as np

class StressTransformation2D(Scene):
    def construct(self):
        # Parameters
        sigma_x = 10
        sigma_y = 2
        tau_xy = 4
        theta_final = PI / 6  # 30 degrees

        # Title
        title = Text("2D Stress Transformation", font_size=32).to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.5)

        # Create stress element (square) - positioned on the left
        side = 2
        element_center = LEFT * 4
        element = Square(side_length=side, color=YELLOW, fill_opacity=0.3)
        element.move_to(element_center)
        self.play(Create(element))

        # Original stress arrows
        arrow_len = 1.0
        
        # sigma_x arrows (horizontal, on left and right faces)
        sigma_x_right = Arrow(
            start=element.get_right(),
            end=element.get_right() + RIGHT * arrow_len,
            color=RED, buff=0
        )
        sigma_x_left = Arrow(
            start=element.get_left(),
            end=element.get_left() + LEFT * arrow_len,
            color=RED, buff=0
        )
        sigma_x_label = MathTex(r"\sigma_x", color=RED, font_size=28).next_to(sigma_x_right, RIGHT, buff=0.1)

        # sigma_y arrows (vertical, on top and bottom faces)
        sigma_y_top = Arrow(
            start=element.get_top(),
            end=element.get_top() + UP * arrow_len,
            color=BLUE, buff=0
        )
        sigma_y_bottom = Arrow(
            start=element.get_bottom(),
            end=element.get_bottom() + DOWN * arrow_len,
            color=BLUE, buff=0
        )
        sigma_y_label = MathTex(r"\sigma_y", color=BLUE, font_size=28).next_to(sigma_y_top, UP, buff=0.1)

        # tau_xy arrows (shear - tangent to faces)
        # Right face: shear arrow pointing up along the face
        tau_right_start = element.get_right() + DOWN * 0.4
        tau_right_end = element.get_right() + UP * 0.4
        tau_xy_right = Arrow(
            start=tau_right_start,
            end=tau_right_end,
            color=ORANGE, buff=0
        )
        
        # Top face: shear arrow pointing right along the face
        tau_top_start = element.get_top() + LEFT * 0.4
        tau_top_end = element.get_top() + RIGHT * 0.4
        tau_xy_top = Arrow(
            start=tau_top_start,
            end=tau_top_end,
            color=ORANGE, buff=0
        )
        
        tau_xy_label = MathTex(r"\tau_{xy}", color=ORANGE, font_size=28).next_to(tau_xy_right, RIGHT, buff=0.15)

        # Play original stress arrows
        self.play(
            Create(sigma_x_right), Create(sigma_x_left),
            Create(sigma_y_top), Create(sigma_y_bottom),
        )
        self.play(
            Create(tau_xy_right), Create(tau_xy_top),
        )
        self.play(
            Write(sigma_x_label), Write(sigma_y_label), Write(tau_xy_label)
        )
        self.wait(0.5)

        # Show original stress values - positioned in bottom left
        stress_values = VGroup(
            MathTex(r"\sigma_x = " + str(sigma_x), color=RED, font_size=24),
            MathTex(r"\sigma_y = " + str(sigma_y), color=BLUE, font_size=24),
            MathTex(r"\tau_{xy} = " + str(tau_xy), color=ORANGE, font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(DL, buff=0.5)
        self.play(Write(stress_values))
        self.wait(0.5)

        # Transformation equations - positioned on the right side
        eq_title = Text("Transformation Equations:", font_size=18, color=WHITE).to_edge(RIGHT, buff=0.3).shift(UP * 2.5)
        eq1 = MathTex(
            r"\sigma_{x'} = \frac{\sigma_x + \sigma_y}{2} + \frac{\sigma_x - \sigma_y}{2}\cos 2\theta",
            font_size=18
        ).next_to(eq_title, DOWN, buff=0.2, aligned_edge=LEFT)
        eq1b = MathTex(
            r"+ \tau_{xy}\sin 2\theta",
            font_size=18
        ).next_to(eq1, DOWN, buff=0.1, aligned_edge=LEFT).shift(RIGHT * 0.5)
        
        eq2 = MathTex(
            r"\sigma_{y'} = \frac{\sigma_x + \sigma_y}{2} - \frac{\sigma_x - \sigma_y}{2}\cos 2\theta",
            font_size=18
        ).next_to(eq1b, DOWN, buff=0.2, aligned_edge=LEFT).shift(LEFT * 0.5)
        eq2b = MathTex(
            r"- \tau_{xy}\sin 2\theta",
            font_size=18
        ).next_to(eq2, DOWN, buff=0.1, aligned_edge=LEFT).shift(RIGHT * 0.5)
        
        eq3 = MathTex(
            r"\tau_{x'y'} = -\frac{\sigma_x - \sigma_y}{2}\sin 2\theta + \tau_{xy}\cos 2\theta",
            font_size=18
        ).next_to(eq2b, DOWN, buff=0.2, aligned_edge=LEFT).shift(LEFT * 0.5)

        equations = VGroup(eq_title, eq1, eq1b, eq2, eq2b, eq3)
        equations.scale(0.9).to_edge(RIGHT, buff=0.2).shift(UP * 0.5)

        self.play(Write(eq_title))
        self.play(Write(eq1), Write(eq1b))
        self.play(Write(eq2), Write(eq2b))
        self.play(Write(eq3))
        self.wait(1)

        # Compute transformed stresses
        theta = theta_final
        sigma_x_prime = (sigma_x + sigma_y) / 2 + (sigma_x - sigma_y) / 2 * np.cos(2 * theta) + tau_xy * np.sin(2 * theta)
        sigma_y_prime = (sigma_x + sigma_y) / 2 - (sigma_x - sigma_y) / 2 * np.cos(2 * theta) - tau_xy * np.sin(2 * theta)
        tau_xy_prime = -(sigma_x - sigma_y) / 2 * np.sin(2 * theta) + tau_xy * np.cos(2 * theta)

        # Rotation matrix
        R = np.array([
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1]
        ])

        # Create rotated element
        element_rotated = Square(side_length=side, color=GREEN, fill_opacity=0.3)
        element_rotated.rotate(theta)
        element_rotated.move_to(element_center)

        # Get rotated directions
        dir_x = R @ np.array([1, 0, 0])
        dir_y = R @ np.array([0, 1, 0])

        # Rotated stress arrows
        center = element_rotated.get_center()
        
        sigma_xp_right = Arrow(
            start=center + dir_x * side / 2,
            end=center + dir_x * (side / 2 + arrow_len),
            color=RED, buff=0
        )
        sigma_xp_left = Arrow(
            start=center - dir_x * side / 2,
            end=center - dir_x * (side / 2 + arrow_len),
            color=RED, buff=0
        )
        sigma_xp_label = MathTex(r"\sigma_{x'}", color=RED, font_size=28).next_to(sigma_xp_right.get_end(), RIGHT, buff=0.1)

        sigma_yp_top = Arrow(
            start=center + dir_y * side / 2,
            end=center + dir_y * (side / 2 + arrow_len),
            color=BLUE, buff=0
        )
        sigma_yp_bottom = Arrow(
            start=center - dir_y * side / 2,
            end=center - dir_y * (side / 2 + arrow_len),
            color=BLUE, buff=0
        )
        sigma_yp_label = MathTex(r"\sigma_{y'}", color=BLUE, font_size=28).next_to(sigma_yp_top.get_end(), UP, buff=0.1)

        # Shear on rotated element - tangent to faces
        # Right face: shear arrow along the face (in dir_y direction)
        tau_xyp_right = Arrow(
            start=center + dir_x * side / 2 - dir_y * 0.4,
            end=center + dir_x * side / 2 + dir_y * 0.4,
            color=ORANGE, buff=0
        )
        # Top face: shear arrow along the face (in dir_x direction)
        tau_xyp_top = Arrow(
            start=center + dir_y * side / 2 - dir_x * 0.4,
            end=center + dir_y * side / 2 + dir_x * 0.4,
            color=ORANGE, buff=0
        )
        tau_xyp_label = MathTex(r"\tau_{x'y'}", color=ORANGE, font_size=28).next_to(tau_xyp_right.get_end(), RIGHT, buff=0.15)

        # Angle arc
        angle_arc = Arc(radius=0.6, start_angle=0, angle=theta, color=WHITE).move_to(element_center, aligned_edge=ORIGIN)
        theta_label_arc = MathTex(r"\theta", font_size=24).next_to(angle_arc, UR, buff=0.05)

        # Animate transformation
        self.play(
            ReplacementTransform(element, element_rotated),
            ReplacementTransform(sigma_x_right, sigma_xp_right),
            ReplacementTransform(sigma_x_left, sigma_xp_left),
            ReplacementTransform(sigma_y_top, sigma_yp_top),
            ReplacementTransform(sigma_y_bottom, sigma_yp_bottom),
            ReplacementTransform(tau_xy_right, tau_xyp_right),
            ReplacementTransform(tau_xy_top, tau_xyp_top),
            ReplacementTransform(sigma_x_label, sigma_xp_label),
            ReplacementTransform(sigma_y_label, sigma_yp_label),
            ReplacementTransform(tau_xy_label, tau_xyp_label),
            Create(angle_arc),
            Write(theta_label_arc),
            run_time=2
        )
        self.wait(1)

        # Show transformed stress values - replace original values
        transformed_values = VGroup(
            MathTex(r"\sigma_{x'} = " + f"{sigma_x_prime:.2f}", color=RED, font_size=24),
            MathTex(r"\sigma_{y'} = " + f"{sigma_y_prime:.2f}", color=BLUE, font_size=24),
            MathTex(r"\tau_{x'y'} = " + f"{tau_xy_prime:.2f}", color=ORANGE, font_size=24),
            MathTex(r"\theta = 30°", color=WHITE, font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(DL, buff=0.5)

        self.play(ReplacementTransform(stress_values, transformed_values))
        self.wait(2)
