from manim import *
import numpy as np

class CircularBodyForcesScene(Scene):
    def construct(self):
        # Title
        title = Text("Finite Element Analysis: Body Under Load", font_size=36)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # Create slightly irregular circular shape
        np.random.seed(15)
        num_points = 12
        angles = np.linspace(0, 2*np.pi, num_points + 1)[:-1]
        control_points = []
        
        base_radius = 2.2
        for angle in angles:
            r = base_radius + np.random.uniform(-0.15, 0.15)
            x = r * np.cos(angle)
            y = r * np.sin(angle)
            control_points.append(np.array([x, y, 0]))
        
        # Create smooth closed circular shape
        circular_body = VMobject(color=BLUE, stroke_width=4)
        circular_body.set_points_smoothly(control_points + [control_points[0]])
        circular_body.set_fill(BLUE, opacity=0.3)
        circular_body.shift(LEFT * 0.5)
        
        body_label = Text("Circular Body", font_size=24)
        body_label.next_to(circular_body, DOWN, buff=0.5)
        
        self.play(
            FadeOut(title, shift=UP),
            Create(circular_body),
            Write(body_label)
        )
        self.wait(1)
        
        # Add system of forces acting on the body
        forces = VGroup()
        force_labels = VGroup()
        
        # Top force (compression)
        f_top = Arrow(
            circular_body.get_top() + UP * 1.2,
            circular_body.get_top() + UP * 0.1,
            color=RED, buff=0, stroke_width=8, max_tip_length_to_length_ratio=0.15
        )
        f_top_label = MathTex("F_1", color=RED, font_size=28).next_to(f_top, UP, buff=0.1)
        
        # Bottom force (tension)
        f_bottom = Arrow(
            circular_body.get_bottom() + DOWN * 0.1,
            circular_body.get_bottom() + DOWN * 1.2,
            color=RED, buff=0, stroke_width=8, max_tip_length_to_length_ratio=0.15
        )
        f_bottom_label = MathTex("F_2", color=RED, font_size=28).next_to(f_bottom, DOWN, buff=0.1)
        
        # Side forces
        f_left = Arrow(
            circular_body.get_left() + LEFT * 1.0,
            circular_body.get_left() + LEFT * 0.1,
            color=GREEN, buff=0, stroke_width=7, max_tip_length_to_length_ratio=0.15
        )
        f_left_label = MathTex("F_3", color=GREEN, font_size=28).next_to(f_left, LEFT, buff=0.1)
        
        f_right = Arrow(
            circular_body.get_right() + RIGHT * 0.1,
            circular_body.get_right() + RIGHT * 1.0,
            color=GREEN, buff=0, stroke_width=7, max_tip_length_to_length_ratio=0.15
        )
        f_right_label = MathTex("F_4", color=GREEN, font_size=28).next_to(f_right, RIGHT, buff=0.1)
        
        forces.add(f_top, f_bottom, f_left, f_right)
        force_labels.add(f_top_label, f_bottom_label, f_left_label, f_right_label)
        
        self.play(
            FadeOut(body_label),
            *[Create(f) for f in forces],
            *[Write(label) for label in force_labels]
        )
        self.wait(1.5)
        
        # Create finite element mesh
        cube_size = 0.22
        cubes = VGroup()
        
        all_points = circular_body.get_all_points()
        x_min = np.min(all_points[:, 0]) - 0.5
        x_max = np.max(all_points[:, 0]) + 0.5
        y_min = np.min(all_points[:, 1]) - 0.5
        y_max = np.max(all_points[:, 1]) + 0.5
        
        for x in np.arange(x_min, x_max, cube_size):
            for y in np.arange(y_min, y_max, cube_size):
                cube_center = np.array([x, y, 0])
                
                sample_points = [
                    cube_center,
                    cube_center + np.array([cube_size/3, cube_size/3, 0]),
                    cube_center + np.array([-cube_size/3, cube_size/3, 0]),
                    cube_center + np.array([cube_size/3, -cube_size/3, 0]),
                    cube_center + np.array([-cube_size/3, -cube_size/3, 0]),
                ]
                
                if all(self.point_inside_curve(pt, circular_body) for pt in sample_points):
                    cube = Square(side_length=cube_size, stroke_width=0.8)
                    cube.set_fill(BLUE, opacity=0.6)
                    cube.set_stroke(WHITE, width=0.6)
                    cube.move_to(cube_center)
                    cubes.add(cube)
        
        mesh_label = Text("Discretized Mesh", font_size=24)
        mesh_label.next_to(circular_body, DOWN, buff=0.5)
        
        self.play(
            circular_body.animate.set_fill(opacity=0.1).set_stroke(width=2),
            Create(cubes, lag_ratio=0.003),
            Write(mesh_label)
        )
        self.wait(1.5)
        
        # Select and highlight one element from the middle
        target_index = len(cubes) // 2 + 15
        target_element = cubes[target_index]
        highlight = target_element.copy().set_stroke(YELLOW, width=5).set_fill(YELLOW, opacity=0.3)
        
        self.play(Create(highlight))
        self.wait(0.5)
        
        # Extract animation - zoom and move the element
        extraction_label = Text("Element Extraction", font_size=28)
        extraction_label.to_edge(UP)
        
        extracted_element = target_element.copy()
        
        self.play(
            FadeOut(circular_body),
            FadeOut(forces),
            FadeOut(force_labels),
            FadeOut(mesh_label),
            Write(extraction_label)
        )
        
        # Animate extraction: fade other elements and move target
        other_cubes = VGroup(*[c for i, c in enumerate(cubes) if i != target_index])
        
        self.play(
            other_cubes.animate.set_opacity(0.15),
            highlight.animate.scale(2).shift(RIGHT * 2.5),
            run_time=1.5
        )
        
        self.play(FadeOut(highlight))
        
        # Create enlarged single element for analysis
        single_element = Square(side_length=3, stroke_width=4, color=ORANGE)
        single_element.set_fill(ORANGE, opacity=0.5)
        single_element.shift(RIGHT * 2.5)
        
        self.play(
            other_cubes.animate.shift(LEFT * 2).scale(0.7),
            Create(single_element)
        )
        self.wait(1)
        
        # Add stress components on the extracted element
        stress_label = Text("Stress Analysis on Element", font_size=24)
        stress_label.next_to(single_element, UP, buff=0.5)
        self.play(Write(stress_label))
        
        # Normal stresses
        sigma_x = Arrow(
            single_element.get_right(),
            single_element.get_right() + RIGHT * 0.9,
            color=RED, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.2
        )
        sigma_x_label = MathTex(r"\sigma_{xx}", color=RED, font_size=26).next_to(sigma_x, RIGHT)
        
        sigma_y = Arrow(
            single_element.get_top(),
            single_element.get_top() + UP * 0.9,
            color=GREEN, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.2
        )
        sigma_y_label = MathTex(r"\sigma_{yy}", color=GREEN, font_size=26).next_to(sigma_y, UP)
        
        # Shear stress
        tau = Arrow(
            single_element.get_top() + LEFT * 0.8,
            single_element.get_top() + LEFT * 0.8 + RIGHT * 0.8,
            color=PURPLE, buff=0, stroke_width=5, max_tip_length_to_length_ratio=0.25
        )
        tau_label = MathTex(r"\tau_{xy}", color=PURPLE, font_size=26).next_to(tau, UP, buff=0.1)
        
        self.play(
            Create(sigma_x), Write(sigma_x_label),
        )
        self.wait(0.3)
        self.play(
            Create(sigma_y), Write(sigma_y_label),
        )
        self.wait(0.3)
        self.play(
            Create(tau), Write(tau_label),
        )
        self.wait(1)
        
        # Dimensions
        dx = MathTex(r"\Delta x", font_size=28).next_to(single_element, DOWN, buff=0.3)
        dy = MathTex(r"\Delta y", font_size=28).next_to(single_element, LEFT, buff=0.3)
        
        self.play(Write(dx), Write(dy))
        self.wait(2)
        
        # Final emphasis
        self.play(
            single_element.animate.set_fill(opacity=0.7),
            rate_func=there_and_back,
            run_time=1
        )
        self.wait(2)
    
    def point_inside_curve(self, point, curve):
        """Ray casting algorithm for point in polygon"""
        x, y = point[0], point[1]
        curve_points = curve.get_all_points()
        n = len(curve_points)
        
        if n < 3:
            return False
        
        inside = False
        p1x, p1y = curve_points[0][0], curve_points[0][1]
        
        for i in range(1, n):
            p2x, p2y = curve_points[i][0], curve_points[i][1]
            
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        p2x, p2y = curve_points[0][0], curve_points[0][1]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        
        return inside