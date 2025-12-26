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
        # Get direction vector of the normal line
        normal_direction = normal_at_N.direction
        # Normalize it
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

        # Lines - Now Line refers to Manim's Line
        AB_line = Line(A_coords, B_coords, color=YELLOW)
        BC_line_manim = Line(B_coords, C_coords, color=WHITE)
        ND_line = Line(N_coords, D_coords, color=PINK)
        
        # Slider axis visualization
        slider_line = DashedLine(
            to_coords(slider_axis.p1),
            to_coords(slider_axis.p2),
            color=GRAY
        )

        # add everything
        self.add(slider_line)
        self.add(AB_line, BC_line_manim, ND_line)
        self.add(A_dot, B_dot, C_dot, N_dot, D_dot)
        self.add(A_label, B_label, C_label, N_label, D_label)

        # Polygon joining B, C, D
        BCD_polygon = Polygon(
        B_coords,  # only x,y
        C_coords,
        D_coords,
        color=TEAL,
        fill_opacity=0.2  # semi-transparent fill
        )

        self.add(BCD_polygon)
        dim_AB = self.get_dimension_label(A_coords, B_coords, f"r_{{BA}} = {r_BA}")
        dim_BC = self.get_dimension_label(B_coords, C_coords, f"r_{{CB}} = {r_CB}")
        dim_NB = self.get_dimension_label(B_coords, N_coords, f"r_{{NB}} = {r_NB}", offset_val=-0.1)
        dim_DN = self.get_dimension_label(N_coords, D_coords, f"r_{{DN}} = {r_DN}")
        # self.add(dim_AB, dim_BC, dim_NB, dim_DN)

        self.add(self.angle_with_x_axis_label(A_coords, B_coords))

        self.add(self.pin_joint_ground(A_coords))

        slider = self.slider_joint(C_coords)
        self.add(slider)
        self.play(Succession(Create(dim_AB, run_time=2), Create(dim_BC, run_time=2), Create(dim_NB, run_time=2), Create(dim_DN, run_time=2)))

    def get_dimension_label(self, start, end, label_text, offset_val=0.1, scale=0.7, label_buff=0.15):
            direction = end - start
            dist = np.linalg.norm(direction)
            if dist == 0: return VGroup() 
            
            unit_dir = direction / dist
            perp_vec = np.array([-unit_dir[1], unit_dir[0], 0]) 
            
            side_multiplier = 1 if offset_val >= 0 else -1
            brace_dir = perp_vec * side_multiplier
            
            brace = BraceBetweenPoints(start, end, direction=brace_dir)
            brace.shift(perp_vec * offset_val) 
            
            label = brace.get_tex(label_text).scale(scale)
            
            # Calculate angle to rotate text parallel to the line
            angle = np.arctan2(direction[1], direction[0])
            
            # Logic to keep text upright (readable)
            if PI/2 < angle <= PI or -PI <= angle < -PI/2:
                angle += PI
                
            label.rotate(angle)
            label.move_to(brace.get_tip() + brace_dir * label_buff)
            
            return VGroup(brace, label)


    
    def angle_with_x_axis_label(self, A, B):
        # 1. Define lines to measure the angle
        line1 = Line(A, A + RIGHT)
        line2 = Line(A, B)
        
        # 2. Create the Angle arc
        angle_arc = Angle(line1, line2, radius=0.4)

        # 3. FIX: Extract the numerical float value from the Angle object
        # .get_value(degrees=True) converts the radian arc to a degree number
        angle_value = angle_arc.get_value(degrees=True)

        # 4. Create the label using the extracted number
        value_label = DecimalNumber(
            angle_value, 
            unit=r"^{\circ}", 
            num_decimal_places=1
        ).scale(0.7)

        # 5. Position the label near the arc
        value_label.next_to(angle_arc, RIGHT, buff=0.1)

        # 6 horizontal refernce line
        x_line = DashedLine(A+LEFT, A + RIGHT, color=GRAY)

        return VGroup(angle_arc, value_label, x_line)

    def pin_joint_ground(self, point_coords, size=0.25):
        # 1. The Pin (The pivot point)
        pin = Dot(point_coords, radius=size*0.2, color=WHITE, z_index=10)
        
        # 2. The Triangle Base
        # Points: Top(point), Bottom-Left, Bottom-Right
        base = Triangle(color=GRAY).set_height(size).move_to(point_coords + DOWN*size/2)
        
        # 3. The Ground Line
        ground_line = Line(
            base.get_corner(DL) + LEFT*0.1, 
            base.get_corner(DR) + RIGHT*0.1, 
            color=GRAY
        )
        
        # 4. Grounding Hashes (The diagonal lines)
        hashes = VGroup(*[
            Line(ORIGIN, DOWN*0.1 + LEFT*0.05, color=GRAY, stroke_width=2)
            for _ in range(5)
        ]).arrange(RIGHT, buff=0.1).next_to(ground_line, DOWN, buff=0)

        # Combine everything
        joint = VGroup(base, ground_line, hashes, pin)
        
        return joint

    # --- Usage in construct ---
    # self.add(self.pin_joint_ground(A_coords))
    
    def slider_joint(self, point_coords, width=0.7, height=0.4):
        # 1. The Slider Block
        block = Rectangle(width=width, height=height, color=BLUE_B, stroke_width=0.1)
        block.set_fill(BLUE_E, opacity=1)
        block.move_to(point_coords)
        
        # 2. The Connecting Pin
        pin = Dot(point_coords, radius=0.06, color=WHITE, z_index=10)
        
        # 3. The Guide Rails
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
        
        # 4. Grounding Hashes
        hashes = VGroup(*[
            Line(ORIGIN, UP*0.1 + RIGHT*0.05, color=GRAY_D, stroke_width=2)
            for _ in range(8)
        ]).arrange(RIGHT, buff=0.15)
        
        # FIX: Use .copy() instead of .clone()
        hashes_top = hashes.copy().next_to(rail_top, UP, buff=0)
        hashes_bottom = hashes.copy().next_to(rail_bottom, DOWN, buff=0)

        # Group components
        moving_part = VGroup(block, pin)
        static_part = VGroup(rail_top, rail_bottom, hashes_top, hashes_bottom)
        
        return VGroup(static_part, moving_part)
