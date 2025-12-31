from manim import *
import numpy as np
from sympy import cos, sin, pi, sqrt
from sympy.geometry import Point, Line as SympyLine, Circle as SympyCircle

class OffsetSliderCrank(Scene):
    def construct(self):
        # dimensions
        r_BA = 50   # crank length
        r_CB = 140  # connecting rod length
        r_NB = 80   # point N on connecting rod
        r_DN = 50   # projection length from N normal to BC
        offset = 20 # slider offset
        
        # Angular velocity of crank (rad/s)
        omega2 = 2 * PI  # 1 revolution per second

        # scale factor to fit on screen
        scale = 0.05

        # origin shifted to (-3, -1)
        A_fixed = Point(-4, 0)
        
        # Create the static scene first
        self.setup_static_elements(A_fixed, scale, offset)
        
        # Show initial mechanism with dimensions
        self.show_initial_dimensions(A_fixed, r_BA, r_CB, r_NB, r_DN, offset, scale)
        
        # Now animate the mechanism
        self.animate_mechanism(A_fixed, r_BA, r_CB, r_NB, r_DN, offset, scale, omega2)
    
    def setup_static_elements(self, A, scale, offset):
        """Setup ground and slider axis"""
        A_coords = np.array([float(A.x), float(A.y), 0])
        
        # Add ground joint at A
        self.ground_joint = self.pin_joint_ground(A_coords, size=0.4)
        self.add(self.ground_joint)
        
        # Slider axis (convert SymPy Float to Python float)
        slider_y = float(A.y - offset*scale)
        self.slider_line = DashedLine(
            np.array([float(A.x) - 1, slider_y, 0]),
            np.array([float(A.x) + 10, slider_y, 0]),
            color=GRAY
        )
        self.add(self.slider_line)
        
        # Store A_coords for later use
        self.A_coords = A_coords
        self.A_fixed = A
        self.offset = offset
        self.scale_factor = scale
    
    def show_initial_dimensions(self, A, r_BA, r_CB, r_NB, r_DN, offset, scale):
        """Show the mechanism with dimension annotations before animation"""
        # Initial angle
        theta2_initial = pi/4
        
        # Calculate initial positions
        result = self.calculate_positions(A, r_BA, r_CB, r_NB, r_DN, offset, scale, theta2_initial)
        if not result:
            return
        
        B, C, N, D = result
        
        def to_coords(P):
            return np.array([float(P.x), float(P.y), 0])
        
        A_coords, B_coords, C_coords, N_coords, D_coords = map(to_coords, [A, B, C, N, D])
        
        # Create initial objects
        A_dot = Dot(A_coords, color=BLUE, radius=0.08)
        B_dot = Dot(B_coords, color=RED, radius=0.08)
        C_dot = Dot(C_coords, color=GREEN, radius=0.08)
        N_dot = Dot(N_coords, color=ORANGE, radius=0.08)
        D_dot = Dot(D_coords, color=PURPLE, radius=0.08)
        
        # Labels
        A_label = Text("A", font_size=20).next_to(A_dot, DOWN+LEFT, buff=0.1)
        B_label = Text("B", font_size=20).next_to(B_dot, UP, buff=0.1)
        C_label = Text("C", font_size=20).next_to(C_dot, RIGHT, buff=0.1)
        N_label = Text("N", font_size=20).next_to(N_dot, UP+RIGHT, buff=0.1)
        D_label = Text("D", font_size=20).next_to(D_dot, DOWN, buff=0.1)
        
        # Create realistic links
        AB_link = self.create_realistic_link(A_coords, B_coords, width=0.15, color=YELLOW)
        BC_link = self.create_realistic_link(B_coords, C_coords, width=0.18, color=WHITE)
        # ND link is welded at N (no pin joint at N), only pin at D
        ND_link = self.create_realistic_link(N_coords, D_coords, width=0.12, color=PINK, 
                                             end_joints=(False, True))
        
        # Slider (will be in middle layer)
        self.min_x_position = C_coords[0]
        self.max_x_position = C_coords[0]
        slider = self.create_dynamic_slider(C_coords, self.min_x_position, self.max_x_position)
        
        # Polygon (coupler body visualization)
        BCD_polygon = Polygon(B_coords, C_coords, D_coords, color=TEAL, fill_opacity=0.2, stroke_width=1)
        
        # Create dimensions
        dim_AB = self.get_dimension_label(A_coords, B_coords, f"{r_BA}", offset_val=0.4, scale=0.6)
        dim_BC = self.get_dimension_label(B_coords, C_coords, f"{r_CB}", offset_val=-0.4, scale=0.6)
        dim_BN = self.get_dimension_label(B_coords, N_coords, f"{r_NB}", offset_val=0.3, scale=0.6)
        dim_ND = self.get_dimension_label(N_coords, D_coords, f"{r_DN}", offset_val=-0.3, scale=0.6)
        
        # Offset dimension (vertical)
        slider_y = A_coords[1] - offset*scale
        offset_start = np.array([A_coords[0] - 1.5, A_coords[1], 0])
        offset_end = np.array([A_coords[0] - 1.5, slider_y, 0])
        dim_offset = self.get_dimension_label(offset_start, offset_end, f"{offset}", offset_val=-0.3, scale=0.6)
        
        # Animate creation with proper layering
        # Layer 1 (back): Slider support/rails
        # Layer 2 (middle): Polygon fill, slider block
        # Layer 3 (front): Links and joints
        # Layer 4 (top): Dots and labels
        
        self.play(
            Create(slider),  # Slider rails in back
            run_time=1.0
        )
        
        self.play(
            Create(BCD_polygon),  # Polygon behind links
            run_time=0.8
        )
        
        self.play(
            Create(AB_link),
            Create(BC_link),
            Create(ND_link),
            run_time=1.2
        )
        
        self.play(
            *[GrowFromCenter(dot) for dot in [A_dot, B_dot, C_dot, N_dot, D_dot]],
            *[Write(label) for label in [A_label, B_label, C_label, N_label, D_label]],
            run_time=1.0
        )
        
        # Show dimensions one by one
        self.play(Create(dim_AB), run_time=0.8)
        self.play(Create(dim_BC), run_time=0.8)
        self.play(Create(dim_BN), run_time=0.8)
        self.play(Create(dim_ND), run_time=0.8)
        self.play(Create(dim_offset), run_time=0.8)
        
        # Wait to appreciate dimensions
        self.wait(1)
        
        # Fade out dimensions
        self.play(
            FadeOut(dim_AB),
            FadeOut(dim_BC),
            FadeOut(dim_BN),
            FadeOut(dim_ND),
            FadeOut(dim_offset),
            run_time=0.5
        )
        
        # Store objects for animation
        self.initial_objects = {
            'AB_link': AB_link,
            'BC_link': BC_link,
            'ND_link': ND_link,
            'BCD_polygon': BCD_polygon,
            'slider': slider,
            'A_dot': A_dot,
            'B_dot': B_dot,
            'C_dot': C_dot,
            'N_dot': N_dot,
            'D_dot': D_dot,
            'A_label': A_label,
            'B_label': B_label,
            'C_label': C_label,
            'N_label': N_label,
            'D_label': D_label
        }
    
    def calculate_positions(self, A, r_BA, r_CB, r_NB, r_DN, offset, scale, theta2):
        """Calculate all positions for a given crank angle theta2"""
        # Crank end B
        B = Point(A.x + r_BA*scale*cos(theta2), A.y + r_BA*scale*sin(theta2))
        
        # Slider axis
        slider_y = A.y - offset*scale
        slider_axis = SympyLine(Point(A.x - 1, slider_y), Point(A.x + 10, slider_y))
        
        # Connecting rod circle centered at B
        circle_CB = SympyCircle(B, r_CB*scale)
        
        # Intersection gives slider C
        C_candidates = circle_CB.intersection(slider_axis)
        if not C_candidates:
            return None
        
        C = C_candidates[0] if C_candidates[0].x > C_candidates[1].x else C_candidates[1]
        
        # Point N on BC
        ratio = r_NB / r_CB
        N = Point(B.x + ratio*(C.x - B.x), B.y + ratio*(C.y - B.y))
        
        # Normal to BC through N
        BC_line = SympyLine(B, C)
        normal_at_N = BC_line.perpendicular_line(N)
        
        # Point D
        normal_direction = normal_at_N.direction
        dir_length = sqrt(normal_direction.x**2 + normal_direction.y**2)
        dir_x = normal_direction.x / dir_length
        dir_y = normal_direction.y / dir_length
        
        D = Point(N.x - r_DN*scale*dir_x, N.y - r_DN*scale*dir_y)
        
        return B, C, N, D
    
    def animate_mechanism(self, A, r_BA, r_CB, r_NB, r_DN, offset, scale, omega2):
        """Animate the mechanism with given angular velocity"""
        
        def to_coords(P):
            return np.array([float(P.x), float(P.y), 0])
        
        # Initial angle
        theta2_initial = pi/4
        
        # Get existing objects
        A_coords = self.A_coords
        AB_link = self.initial_objects['AB_link']
        BC_link = self.initial_objects['BC_link']
        ND_link = self.initial_objects['ND_link']
        BCD_polygon = self.initial_objects['BCD_polygon']
        slider = self.initial_objects['slider']
        B_dot = self.initial_objects['B_dot']
        C_dot = self.initial_objects['C_dot']
        N_dot = self.initial_objects['N_dot']
        D_dot = self.initial_objects['D_dot']
        B_label = self.initial_objects['B_label']
        C_label = self.initial_objects['C_label']
        N_label = self.initial_objects['N_label']
        D_label = self.initial_objects['D_label']
        
        # Angle dimension
        result = self.calculate_positions(A, r_BA, r_CB, r_NB, r_DN, offset, scale, theta2_initial)
        B_init, _, _, _ = result
        B_init_coords = to_coords(B_init)
        
        angle_dim = self.angle_dimension(A_coords, B_init_coords, reference='horizontal', 
                                        radius=0.6, show_ref_line=True)
        self.add(angle_dim)
        
        # Animation updater
        theta2 = ValueTracker(theta2_initial)
        
        def update_mechanism(mob):
            current_theta = theta2.get_value()
            result = self.calculate_positions(A, r_BA, r_CB, r_NB, r_DN, offset, scale, current_theta)
            
            if not result:
                return
            
            B_new, C_new, N_new, D_new = result
            B_c, C_c, N_c, D_c = map(to_coords, [B_new, C_new, N_new, D_new])
            
            # Update min/max positions for rail extension
            self.min_x_position = min(self.min_x_position, C_c[0])
            self.max_x_position = max(self.max_x_position, C_c[0])
            
            # Update positions
            B_dot.move_to(B_c)
            C_dot.move_to(C_c)
            N_dot.move_to(N_c)
            D_dot.move_to(D_c)
            
            # Update realistic links
            new_AB_link = self.create_realistic_link(A_coords, B_c, width=0.15, color=YELLOW)
            new_BC_link = self.create_realistic_link(B_c, C_c, width=0.18, color=WHITE)
            # ND link is welded at N (no pin joint at N), only pin at D
            new_ND_link = self.create_realistic_link(N_c, D_c, width=0.12, color=PINK,
                                                     end_joints=(False, True))
            
            AB_link.become(new_AB_link)
            BC_link.become(new_BC_link)
            ND_link.become(new_ND_link)
            
            # Update polygon
            BCD_polygon.become(Polygon(B_c, C_c, D_c, color=TEAL, fill_opacity=0.2, stroke_width=1))
            
            # Update slider with extended rails
            new_slider = self.create_dynamic_slider(C_c, self.min_x_position, self.max_x_position)
            slider.become(new_slider)
            
            # Update labels
            B_label.next_to(B_dot, UP, buff=0.1)
            C_label.next_to(C_dot, RIGHT, buff=0.1)
            N_label.next_to(N_dot, UP+RIGHT, buff=0.1)
            D_label.next_to(D_dot, DOWN, buff=0.1)
            
            # Update angle dimension
            new_angle_dim = self.angle_dimension(A_coords, B_c, reference='horizontal',
                                                radius=0.6, show_ref_line=True)
            angle_dim.become(new_angle_dim)
        
        # Add updaters
        AB_link.add_updater(update_mechanism)
        
        # Animate: 2 full rotations at given angular velocity
        rotation_time = 2 * (2*PI) / omega2  # Time for 2 rotations
        
        self.play(
            theta2.animate.increment_value(4*PI),
            rate_func=linear,
            run_time=rotation_time
        )
        
        AB_link.remove_updater(update_mechanism)
    
    def create_dynamic_slider(self, slider_pos, min_x, max_x, width=0.6, height=0.3, buffer=0.5):
        """Creates a slider with rails that extend based on the slider's travel range."""
        # Slider block
        block = Rectangle(width=width, height=height, color=BLUE_B, fill_opacity=0.9, stroke_width=2)
        block.move_to(slider_pos)
        
        # Connecting pin
        pin = Circle(radius=0.08, color=WHITE, fill_opacity=1, stroke_width=1).move_to(slider_pos)
        pin_hole = Circle(radius=0.04, color=DARK_GRAY, fill_opacity=1, stroke_width=1).move_to(slider_pos)
        
        # Calculate rail endpoints with buffer
        rail_left_x = min_x - buffer
        rail_right_x = max_x + buffer
        rail_y = slider_pos[1]
        
        # Guide rails
        rail_top = Line(
            np.array([rail_left_x, rail_y + height/2, 0]),
            np.array([rail_right_x, rail_y + height/2, 0]),
            color=GRAY_D, 
            stroke_width=2
        )
        rail_bottom = Line(
            np.array([rail_left_x, rail_y - height/2, 0]),
            np.array([rail_right_x, rail_y - height/2, 0]),
            color=GRAY_D, 
            stroke_width=2
        )
        
        # Grounding hashes on rails - density stays constant
        hash_spacing = 0.3  # Fixed spacing between hashes
        rail_length = rail_right_x - rail_left_x
        num_hashes = max(5, int(rail_length / hash_spacing))  # Adjust number based on rail length
        actual_spacing = rail_length / (num_hashes + 1)
        
        # Top rail hashes
        hashes_top = VGroup(*[
            Line(ORIGIN, UP*0.1 + RIGHT*0.05, color=GRAY_D, stroke_width=2)
            for _ in range(num_hashes)
        ])
        for i, hash_line in enumerate(hashes_top):
            x_pos = rail_left_x + (i + 1) * actual_spacing
            hash_line.move_to(np.array([x_pos, rail_y + height/2, 0]))
            hash_line.shift(UP * 0.05)
        
        # Bottom rail hashes
        hashes_bottom = VGroup(*[
            Line(ORIGIN, DOWN*0.1 + RIGHT*0.05, color=GRAY_D, stroke_width=2)
            for _ in range(num_hashes)
        ])
        for i, hash_line in enumerate(hashes_bottom):
            x_pos = rail_left_x + (i + 1) * actual_spacing
            hash_line.move_to(np.array([x_pos, rail_y - height/2, 0]))
            hash_line.shift(DOWN * 0.05)
        
        return VGroup(rail_top, rail_bottom, hashes_top, hashes_bottom, block, pin, pin_hole)

    def get_dimension_label(self, start, end, label_text, offset_val=0.5, scale=0.7, 
                            arrow_size=0.15, ext_line_extension=0.1):
        """Creates a CAD-style dimension with extension lines, arrows, and text."""
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
        
        # Calculate angle
        angle = np.arctan2(direction[1], direction[0])
        
        # Keep text upright
        if PI/2 < angle <= PI or -PI <= angle < -PI/2:
            angle += PI
        
        label.rotate(angle)
        
        # Position text
        midpoint = (dim_start + dim_end) / 2
        label.move_to(midpoint + offset_dir * 0.2)
        
        return VGroup(ext_line_1, ext_line_2, dim_line, arrow_1, arrow_2, label)

    def angle_dimension(self, vertex, point, reference='horizontal', radius=0.5, 
                       label_scale=0.5, show_ref_line=True, ref_line_length=1.0,
                       arc_color=BLUE_C, ref_line_color=GRAY):
        """Creates a CAD-style angle dimension - ALWAYS counterclockwise from reference."""
        # Calculate direction from vertex to point
        direction = point - vertex
        angle_to_point = np.arctan2(direction[1], direction[0])
        
        # Define reference angle
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
        
        # Calculate angle from reference to point (ALWAYS counterclockwise)
        angle_rad = angle_to_point - ref_angle
        
        # Normalize to [0, 2π) for counterclockwise measurement
        while angle_rad < 0:
            angle_rad += 2*PI
        while angle_rad >= 2*PI:
            angle_rad -= 2*PI
        
        # Create arc ALWAYS counterclockwise
        arc = Arc(
            radius=radius,
            start_angle=ref_angle,
            angle=angle_rad,  # Always positive = counterclockwise
            color=arc_color,
            stroke_width=2
        ).shift(vertex)
        
        # Calculate angle in degrees
        angle_deg = np.degrees(angle_rad)
        
        # Create label
        value_label = MathTex(
            f"\\theta = {angle_deg:.1f}^{{\\circ}}"
        ).scale(label_scale)
        
        # Position label
        if angle_deg < 30 or angle_deg > 330:
            label_distance = radius + 0.5
        else:
            label_distance = radius + 0.35
        
        # Bisector angle
        bisector_angle = ref_angle + angle_rad / 2
        
        label_pos = vertex + np.array([
            np.cos(bisector_angle) * label_distance,
            np.sin(bisector_angle) * label_distance,
            0
        ])
        
        value_label.move_to(label_pos)
        
        # Adjust for edge cases
        if angle_deg < 15 or angle_deg > 345:
            if reference == 'horizontal':
                value_label.shift(UP * 0.2)
            else:
                value_label.shift(RIGHT * 0.2)
        
        # Create reference line
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

    def create_realistic_link(self, start, end, width=0.15, color=YELLOW, 
                             joint_radius=0.12, show_holes=True, end_joints=(True, True)):
        """
        Creates a realistic mechanical link with proper depth and joint holes.
        
        Args:
            start: Starting point coordinates
            end: Ending point coordinates
            width: Width of the link body
            color: Color of the link
            joint_radius: Radius of the joint circles at ends
            show_holes: Whether to show holes at joints
            end_joints: Tuple (start_joint, end_joint) - True for pin joint, False for welded/rigid
        """
        direction = end - start
        length = np.linalg.norm(direction)
        
        if length == 0:
            return VGroup()
        
        unit_dir = direction / length
        perp_dir = np.array([-unit_dir[1], unit_dir[0], 0])
        
        # Link body as a rectangle
        link_body = Rectangle(
            width=length,
            height=width,
            color=color,
            fill_opacity=0.9,
            stroke_width=2
        )
        
        # Position and rotate the link
        angle = np.arctan2(direction[1], direction[0])
        link_body.rotate(angle)
        link_body.move_to((start + end) / 2)
        
        elements = [link_body]
        
        # Add circles at joints for realistic appearance (only for pin joints)
        if end_joints[0]:  # Start joint is a pin
            joint_start = Circle(
                radius=joint_radius,
                color=color,
                fill_opacity=0.9,
                stroke_width=2
            ).move_to(start)
            elements.append(joint_start)
            
            if show_holes:
                hole_start = Circle(
                    radius=joint_radius * 0.4,
                    color=DARK_GRAY,
                    fill_opacity=1,
                    stroke_width=1
                ).move_to(start)
                elements.append(hole_start)
        
        if end_joints[1]:  # End joint is a pin
            joint_end = Circle(
                radius=joint_radius,
                color=color,
                fill_opacity=0.9,
                stroke_width=2
            ).move_to(end)
            elements.append(joint_end)
            
            if show_holes:
                hole_end = Circle(
                    radius=joint_radius * 0.4,
                    color=DARK_GRAY,
                    fill_opacity=1,
                    stroke_width=1
                ).move_to(end)
                elements.append(hole_end)
        
        return VGroup(*elements)
    
    def create_coupler_link(self, B_coords, C_coords, D_coords, width=0.15):
        """
        Creates a realistic coupler link (BC with extension to D).
        This is a more complex link with three connection points.
        """
        # Main body BC
        BC_link = self.create_realistic_link(
            B_coords, C_coords, 
            width=width, 
            color=WHITE
        )
        
        # Extension ND is part of the same rigid body
        # We'll create a connecting piece from the BC line to D
        
        # Find point N on BC
        BC_vec = C_coords - B_coords
        BC_length = np.linalg.norm(BC_vec)
        
        if BC_length > 0:
            # Point N is at r_NB/r_CB along BC
            # This will be calculated in the position calculation
            # For now, we'll just return the BC link
            pass
        
        return BC_link

    def pin_joint_ground(self, point_coords, size=0.25):
        """Creates a grounded pin joint symbol."""
        # Pin
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
        """Creates a grounded pin joint symbol."""
        # Pin
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