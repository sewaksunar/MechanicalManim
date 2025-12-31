from manim import *
import numpy as np
from sympy import cos, sin, pi, sqrt
from sympy.geometry import Point, Line as SympyLine, Circle

class OffsetSliderCrank(Scene):
    def construct(self):
        # dimensions
        r_BA = 50   # crank length
        r_CB = 140  # connecting rod length
        r_NB = 80   # point N on connecting rod
        r_DN = 50   # projection length from N normal to BC
        offset = 20 # slider offset
        theta2 = pi/4  # crank angle

        # scale factor to fit on screen
        scale = 0.05

        # origin shifted to (-3, -1)
        A = Point(-4, 0)

        # crank end B
        B = Point(A.x + r_BA*scale*cos(theta2), A.y + r_BA*scale*sin(theta2))
        # slider axis: horizontal line with offset
        slider_y = A.y - offset*scale
        slider_axis = SympyLine(Point(A.x - 1, slider_y), Point(A.x + 10, slider_y))

        # connecting rod circle centered at B with radius r_CB
        circle_CB = Circle(B, r_CB*scale)

        # intersection of connecting rod circle and slider axis gives slider C
        C_candidates = circle_CB.intersection(slider_axis)
        if not C_candidates:
            raise ValueError("No intersection found between connecting rod circle and slider axis")
        
        # Pick the intersection point that's to the right of B (forward position)
        C = C_candidates[0] if C_candidates[0].x > C_candidates[1].x else C_candidates[1]

        # point N on BC (ratio r_NB : r_CB from B towards C)
        ratio = r_NB / r_CB
        N = Point(B.x + ratio*(C.x - B.x), B.y + ratio*(C.y - B.y))

        # normal to BC through N
        BC_line = SympyLine(B, C)
        normal_at_N = BC_line.perpendicular_line(N)

        # point D at distance r_DN along the normal
        normal_direction = normal_at_N.direction
        dir_length = sqrt(normal_direction.x**2 + normal_direction.y**2)
        dir_x = normal_direction.x / dir_length
        dir_y = normal_direction.y / dir_length
        
        D = Point(N.x - r_DN*scale*dir_x, N.y - r_DN*scale*dir_y)

        # helper to convert Sympy Point to NumPy coords for Manim
        def to_coords(P):
            return np.array([float(P.x), float(P.y), 0])

        A_coords, B_coords, C_coords, N_coords, D_coords = map(to_coords, [A, B, C, N, D])

        # Manim objects
        A_dot = Dot(A_coords, color=BLUE)
        B_dot = Dot(B_coords, color=RED)
        C_dot = Dot(C_coords, color=GREEN)
        N_dot = Dot(N_coords, color=ORANGE)
        D_dot = Dot(D_coords, color=PURPLE)

        # Labels
        A_label = Text("A", font_size=24).next_to(A_dot, UP+LEFT)
        B_label = Text("B", font_size=24).next_to(B_dot, UP)
        C_label = Text("C", font_size=24).next_to(C_dot, RIGHT)
        N_label = Text("N", font_size=24).next_to(N_dot, UP+RIGHT)
        D_label = Text("D", font_size=24).next_to(D_dot, DOWN)

        # Lines
        AB_line = Line(A_coords, B_coords, color=YELLOW)
        BC_line_manim = Line(B_coords, C_coords, color=WHITE)
        ND_line = Line(N_coords, D_coords, color=PINK)
        
        # Slider axis visualization
        slider_line = DashedLine(
            to_coords(slider_axis.p1),
            to_coords(slider_axis.p2),
            color=GRAY
        )

        # Polygon joining B, C, D
        BCD_polygon = Polygon(
            B_coords,
            C_coords,
            D_coords,
            color=TEAL,
            fill_opacity=0.2
        )

        # Add base elements
        self.add(slider_line)
        self.add(AB_line, BC_line_manim, ND_line)
        self.add(A_dot, B_dot, C_dot, N_dot, D_dot)
        self.add(A_label, B_label, C_label, N_label, D_label)
        self.add(BCD_polygon)

        # Create dimensions
        dim_AB = self.get_dimension_label(A_coords, B_coords, f"r_{{BA}} = {r_BA}")
        dim_BC = self.get_dimension_label(B_coords, C_coords, f"r_{{CB}} = {r_CB}")
        dim_NB = self.get_dimension_label(B_coords, N_coords, f"r_{{NB}} = {r_NB}", offset_val=-0.1)
        dim_DN = self.get_dimension_label(N_coords, D_coords, f"r_{{DN}} = {r_DN}")

        # Add angle dimension
        self.add(self.angle_with_x_axis_label(A_coords, B_coords))

        # Add joints
        self.add(self.pin_joint_ground(A_coords))
        slider = self.slider_joint(C_coords)
        self.add(slider)

        # Animate dimensions
        self.play(
            Succession(
                Create(dim_AB, run_time=2), 
                Create(dim_BC, run_time=2), 
                Create(dim_NB, run_time=2), 
                Create(dim_DN, run_time=2)
            )
        )

    def get_dimension_label(self, start, end, label_text, offset_val=0.5, scale=0.7, 
                            arrow_size=0.15, ext_line_extension=0.1):
        """
        Creates a CAD-style dimension with extension lines, arrows, and text.
        """
        direction = end - start
        dist = np.linalg.norm(direction)
        if dist == 0: 
            return VGroup()
        
        unit_dir = direction / dist
        perp_vec = np.array([-unit_dir[1], unit_dir[0], 0])
        
        # Determine offset direction
        side_multiplier = 1 if offset_val >= 0 else -1
        offset_dir = perp_vec * side_multiplier
        offset_distance = abs(offset_val)
        
        # Calculate dimension line endpoints
        dim_start = start + offset_dir * offset_distance
        dim_end = end + offset_dir * offset_distance
        
        # Extension Lines
        ext_line_1 = Line(
            start - offset_dir * 0.05,
            dim_start + offset_dir * ext_line_extension,
            color=GRAY, 
            stroke_width=1
        )
        ext_line_2 = Line(
            end - offset_dir * 0.05,
            dim_end + offset_dir * ext_line_extension,
            color=GRAY,
            stroke_width=1
        )
        
        # Dimension Line
        dim_line = Line(dim_start, dim_end, color=GRAY, stroke_width=2)
        
        # Arrows
        arrow_1 = Arrow(
            dim_start + unit_dir * arrow_size,
            dim_start,
            buff=0,
            color=GRAY,
            stroke_width=2,
            max_tip_length_to_length_ratio=1,
            tip_length=arrow_size
        )
        arrow_2 = Arrow(
            dim_end - unit_dir * arrow_size,
            dim_end,
            buff=0,
            color=GRAY,
            stroke_width=2,
            max_tip_length_to_length_ratio=1,
            tip_length=arrow_size
        )
        
        # Dimension Text
        label = MathTex(label_text).scale(scale)
        
        # Calculate angle to keep text parallel to dimension line
        angle = np.arctan2(direction[1], direction[0])
        
        # Keep text upright
        if PI/2 < angle <= PI or -PI <= angle < -PI/2:
            angle += PI
        
        label.rotate(angle)
        
        # Position text at midpoint
        midpoint = (dim_start + dim_end) / 2
        label.move_to(midpoint + offset_dir * 0.2)
        
        return VGroup(ext_line_1, ext_line_2, dim_line, arrow_1, arrow_2, label)

    def angle_dimension(self, vertex, point, reference='horizontal', radius=0.5, 
                       label_scale=0.5, show_ref_line=True, ref_line_length=1.0,
                       arc_color=BLUE_C, ref_line_color=GRAY):
        """
        Creates a clean CAD-style angle dimension from horizontal or vertical reference.
        
        Args:
            vertex: Origin point (vertex of angle)
            point: Second point defining the angle
            reference: 'horizontal' or 'vertical' - reference axis
            radius: Radius of the arc
            label_scale: Scale of the angle text
            show_ref_line: Whether to show the reference line
            ref_line_length: Length of reference line
            arc_color: Color of the arc
            ref_line_color: Color of the reference line
        """
        # Calculate direction from vertex to point
        direction = point - vertex
        angle_to_point = np.arctan2(direction[1], direction[0])
        
        # Define reference angle and direction
        if reference == 'horizontal':
            ref_angle = 0  # Horizontal (positive X-axis)
            ref_start = vertex + LEFT * ref_line_length * 0.3
            ref_end = vertex + RIGHT * ref_line_length
        elif reference == 'vertical':
            ref_angle = PI/2  # Vertical (positive Y-axis)
            ref_start = vertex + DOWN * ref_line_length * 0.3
            ref_end = vertex + UP * ref_line_length
        else:
            raise ValueError("reference must be 'horizontal' or 'vertical'")
        
        # Calculate angle from reference to point
        angle_rad = angle_to_point - ref_angle
        
        # Normalize angle to [-π, π]
        while angle_rad > PI:
            angle_rad -= 2*PI
        while angle_rad < -PI:
            angle_rad += 2*PI
        
        # Create clean arc
        arc = Arc(
            radius=radius,
            start_angle=ref_angle,
            angle=angle_rad,
            color=arc_color,
            stroke_width=2
        ).shift(vertex)
        
        # Calculate angle in degrees
        angle_deg = abs(np.degrees(angle_rad))
        
        # Create label with theta symbol
        value_label = MathTex(
            f"\\theta = {angle_deg:.1f}^{{\\circ}}"
        ).scale(label_scale)
        
        # Position label intelligently
        # For small angles, place label further out to avoid overlap
        if abs(angle_deg) < 30:
            label_distance = radius + 0.5
        else:
            label_distance = radius + 0.35
        
        # Calculate bisector angle (middle of the arc)
        bisector_angle = ref_angle + angle_rad / 2
        
        # Position at bisector
        label_pos = vertex + np.array([
            np.cos(bisector_angle) * label_distance,
            np.sin(bisector_angle) * label_distance,
            0
        ])
        
        # Move label to calculated position
        value_label.move_to(label_pos)
        
        # Adjust label to avoid overlapping with arc for edge cases
        # If angle is very small or very large, shift label slightly
        if abs(angle_deg) < 15:
            # For very small angles, shift label away from vertex more
            if reference == 'horizontal':
                value_label.shift(UP * 0.2)
            else:
                value_label.shift(RIGHT * 0.2)
        elif abs(angle_deg) > 165:
            # For angles close to 180, shift label outward
            value_label.shift((label_pos - vertex) * 0.2)
        
        # Create reference line (dashed)
        if show_ref_line:
            ref_line = DashedLine(
                ref_start,
                ref_end,
                color=ref_line_color,
                stroke_width=1.5,
                dash_length=0.08
            )
            return VGroup(ref_line, arc, value_label)
        
        return VGroup(arc, value_label)
    
    def angle_with_x_axis_label(self, A, B, radius=0.5, label_scale=0.5, 
                                show_ref_line=True):
        """
        Legacy function - creates angle dimension from horizontal axis.
        For new code, use angle_dimension() instead.
        """
        return self.angle_dimension(A, B, reference='horizontal', radius=radius,
                                   label_scale=label_scale, show_ref_line=show_ref_line)

    def pin_joint_ground(self, point_coords, size=0.25):
        """
        Creates a grounded pin joint symbol.
        """
        # Pin (pivot point)
        pin = Dot(point_coords, radius=size*0.2, color=WHITE, z_index=10)
        
        # Triangle base
        base = Triangle(color=GRAY).set_height(size).move_to(point_coords + DOWN*size/2)
        
        # Ground line
        ground_line = Line(
            base.get_corner(DL) + LEFT*0.2, 
            base.get_corner(DR) + RIGHT*0.2, 
            color=GRAY
        )
        
        # Grounding hashes
        hashes = VGroup(*[
            Line(ORIGIN, DOWN*0.1 + LEFT*0.05, color=GRAY, stroke_width=2)
            for _ in range(5)
        ]).arrange(RIGHT, buff=0.1).next_to(ground_line, DOWN, buff=0)

        joint = VGroup(base, ground_line, hashes, pin)
        
        return joint

    def slider_joint(self, point_coords, width=0.7, height=0.4):
        """
        Creates a slider joint symbol.
        """
        # Slider block
        block = Rectangle(width=width, height=height, color=BLUE_B, stroke_width=0.1)
        block.set_fill(BLUE_E, opacity=1)
        block.move_to(point_coords)
        
        # Connecting pin
        pin = Dot(point_coords, radius=0.06, color=WHITE, z_index=10)
        
        # Guide rails
        rail_top = Line(
            point_coords + LEFT*width + UP*(height/2), 
            point_coords + RIGHT*width + UP*(height/2), 
            color=GRAY_D, stroke_width=2
        )
        rail_bottom = Line(
            point_coords + LEFT*width + DOWN*(height/2), 
            point_coords + RIGHT*width + DOWN*(height/2), 
            color=GRAY_D, stroke_width=2
        )
        
        # Grounding hashes
        hashes = VGroup(*[
            Line(ORIGIN, UP*0.1 + RIGHT*0.05, color=GRAY_D, stroke_width=2)
            for _ in range(8)
        ]).arrange(RIGHT, buff=0.15)
        
        hashes_top = hashes.copy().next_to(rail_top, UP, buff=0)
        hashes_bottom = hashes.copy().next_to(rail_bottom, DOWN, buff=0)

        # Group components
        moving_part = VGroup(block, pin)
        static_part = VGroup(rail_top, rail_bottom, hashes_top, hashes_bottom)
        
        joint = VGroup(static_part, moving_part)
        
        return joint