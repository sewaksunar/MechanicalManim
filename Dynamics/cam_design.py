from manim import *
import numpy as np

class CamFollowerDisplacement(Scene):
    """
    Cam-follower with follower ABOVE cam on VERTICAL CENTERLINE
    Follower moves UP/DOWN along the vertical axis through cam center
    Contact point and graph displacement are horizontally aligned
    """
    
    def construct(self):
        # Title
        title = Text(
            "Cam-Follower Displacement",
            font_size=40,
            color=TEAL_C
        ).to_edge(UP, buff=0.3)
        
        self.play(Write(title), run_time=1)
        self.wait(0.3)
        self.play(FadeOut(title), run_time=0.5)
        
        # Vertical divider
        divider = Line(UP*3.5, DOWN*3.5, color=GRAY_B, stroke_width=2)
        self.play(Create(divider))
        
        # === CAM MECHANISM (LEFT SIDE) ===
        cam_center = LEFT * 3.5 + DOWN * 1.5
        base_radius = 1.0
        max_variation = 0.6
        
        # Define cam profile
        def get_cam_radius(theta):
            """Returns radius of cam at angle theta"""
            # Smooth varying profile
            variation = max_variation * (0.6 + 0.25*np.sin(2*theta) + 0.15*np.sin(3*theta))
            return base_radius + variation
        
        # Build cam shape
        n_points = 200
        angles = np.linspace(0, 2*PI, n_points)
        cam_points = []
        
        for theta in angles:
            r = get_cam_radius(theta)
            x = cam_center[0] + r * np.cos(theta)
            y = cam_center[1] + r * np.sin(theta)
            cam_points.append([x, y, 0])
        
        cam = Polygon(
            *cam_points,
            color=TEAL_D,
            fill_opacity=0.7,
            stroke_color=TEAL_B,
            stroke_width=3
        )
        
        # Center point
        center_dot = Dot(cam_center, color=WHITE, radius=0.08)
        center_label = Text("O", font_size=20, color=WHITE).next_to(center_dot, DOWN, buff=0.15)
        
        # VERTICAL CENTERLINE (follower moves along this line)
        vertical_line = DashedLine(
            cam_center + DOWN * 1.5,
            cam_center + UP * 3,
            color=GRAY,
            stroke_width=2,
            stroke_opacity=0.5
        )
        
        # === FOLLOWER (ON VERTICAL CENTERLINE ABOVE CAM) ===
        # Follower X position = cam center X (always on vertical line)
        follower_x = cam_center[0]
        
        # Roller (red circle at contact point)
        roller_radius = 0.22
        roller = Circle(
            radius=roller_radius,
            color=RED_C,
            fill_opacity=0.6,
            stroke_color=RED_D,
            stroke_width=3
        )
        
        # Roller center pin/shaft (black dot showing rotation center)
        roller_center_pin = Dot(color=BLACK, radius=0.05)
        
        # Roller rolling indicator (arc showing rotation)
        roller_arc = Arc(
            radius=roller_radius*0.6,
            angle=PI/3,
            color=YELLOW,
            stroke_width=1.5,
            stroke_opacity=0.6
        )
        
        # Vertical stem (green rectangle - main body)
        stem_width = 0.14
        stem_height = 2.0
        stem = Rectangle(
            width=stem_width,
            height=stem_height,
            color=GREEN_D,
            fill_opacity=0.7,
            stroke_color=GREEN_B,
            stroke_width=2
        )
        
        # Pin support connection (thin line from roller to stem)
        pin_support = Line(
            start=ORIGIN,
            end=ORIGIN,
            color=BLUE_D,
            stroke_width=2
        )
        
        # Support base (wider rectangle at bottom)
        support_base = Rectangle(
            width=0.5,
            height=0.15,
            color=BLUE_C,
            fill_opacity=0.6,
            stroke_color=BLUE_D,
            stroke_width=2
        )
        
        # Guide rails (two thin vertical lines)
        left_guide = Line(
            start=ORIGIN + LEFT*0.08,
            end=ORIGIN + UP*2.5,
            color=GRAY_B,
            stroke_width=1,
            stroke_opacity=0.5
        )
        right_guide = Line(
            start=ORIGIN + RIGHT*0.08,
            end=ORIGIN + UP*2.5,
            color=GRAY_B,
            stroke_width=1,
            stroke_opacity=0.5
        )
        
        # Contact point marker
        contact_dot = Dot(color=YELLOW, radius=0.08)
        
        # Horizontal alignment line (dashed line from contact to graph)
        alignment_line = DashedLine(
            LEFT, RIGHT,
            color=YELLOW,
            stroke_width=1.5,
            stroke_opacity=0.4
        )
        
        # === GRAPH (RIGHT SIDE) ===
        graph_axes = Axes(
            x_range=[0, 360, 90],
            y_range=[0, 2.5, 0.5],
            x_length=7.5,
            y_length=4,
            axis_config={
                "color": GRAY_B,
                "stroke_width": 2,
                "include_ticks": True,
            },
            tips=True
        ).shift(RIGHT*3.5 + DOWN*0.2)
        
        # Labels
        x_label = Text("Angle (°)", font_size=20).next_to(graph_axes.x_axis, DOWN, buff=0.3)
        y_label = MathTex("s", font_size=28).next_to(graph_axes.y_axis, LEFT, buff=0.3)
        
        # Tick labels
        x_ticks = VGroup(*[
            Text(str(x), font_size=16).next_to(graph_axes.c2p(x, 0), DOWN, buff=0.15)
            for x in [0, 90, 180, 270, 360]
        ])
        
        # Grid
        grid = VGroup(*[
            DashedLine(
                graph_axes.c2p(x, 0),
                graph_axes.c2p(x, 2.5),
                color=GRAY,
                stroke_width=1,
                stroke_opacity=0.2
            ) for x in range(0, 361, 90)
        ])
        
        # Show initial setup
        self.play(
            Create(cam),
            Create(center_dot),
            Write(center_label),
            Create(vertical_line),
            Create(graph_axes),
            Write(x_label),
            Write(y_label),
            Create(x_ticks),
            Create(grid),
            run_time=1.5
        )
        self.wait(0.3)
        
        # Function to find contact point on cam along vertical centerline
        def find_top_contact(cam_angle):
            """
            Find where the cam surface touches the vertical line above cam center
            Returns the Y coordinate of contact (topmost point on vertical line)
            The follower roller should just touch the cam outer surface
            """
            # The vertical line is at angle PI/2 in world coordinates (straight up)
            # With cam rotation, we need to find which part of cam profile faces up
            theta_contact = PI/2 - cam_angle  # Angle in cam's local coordinates
            
            # Get radius at this angle
            r = get_cam_radius(theta_contact)
            
            # Contact point Y coordinate (cam surface at the top)
            # The roller CENTER should be at distance (r + roller_radius) from cam center
            # So the contact point (bottom of roller) is at distance r from cam center
            contact_y = cam_center[1] + r
            
            return contact_y
        
        # Initialize follower position
        initial_contact_y = find_top_contact(0)
        
        # Position roller so its BOTTOM edge touches the cam
        roller_center_y = initial_contact_y + roller_radius
        roller.move_to([follower_x, roller_center_y, 0])
        
        # Position roller center pin
        roller_center_pin.move_to([follower_x, roller_center_y, 0])
        
        # Position roller arc
        roller_arc.move_to([follower_x, roller_center_y, 0])
        
        # Position pin support
        pin_support.put_start_and_end_on(
            [follower_x, roller_center_y, 0],
            [follower_x, roller_center_y + roller_radius + stem_height/2, 0]
        )
        
        # Position support base
        support_base.move_to([follower_x, roller_center_y + roller_radius + stem_height + 0.1, 0])
        
        # Position guide rails
        left_guide.put_start_and_end_on(
            [follower_x - 0.08, roller_center_y, 0],
            [follower_x - 0.08, roller_center_y + stem_height, 0]
        )
        right_guide.put_start_and_end_on(
            [follower_x + 0.08, roller_center_y, 0],
            [follower_x + 0.08, roller_center_y + stem_height, 0]
        )
        
        # Position stem above roller
        stem.move_to([follower_x, roller_center_y + roller_radius + stem_height/2, 0])
        
        # Contact point is at the bottom of the roller (touching cam surface)
        contact_dot.move_to([follower_x, initial_contact_y, 0])
        
        # Show follower with all details
        self.play(
            Create(left_guide),
            Create(right_guide),
            Create(support_base),
            Create(stem),
            Create(roller),
            Create(roller_center_pin),
            Create(roller_arc),
            Create(pin_support),
            Create(contact_dot),
            run_time=1.5
        )
        self.wait(0.3)
        
        # === ANIMATION ===
        # Displacement curve
        curve_points = []
        displacement_curve = VMobject(color=YELLOW, stroke_width=4)
        
        # Tracking dot on graph
        graph_dot = Dot(color=YELLOW, radius=0.08)
        self.add(graph_dot)
        self.add(alignment_line)
        
        # Reference height (base displacement at theta=90deg when cam_angle=0)
        base_y = cam_center[1] + base_radius
        
        # Animate rotation
        num_steps = 120  # Optimized for smooth fast compilation
        total_angle = 2 * PI
        rotation_step = total_angle / num_steps
        
        for i in range(num_steps + 1):
            # Current rotation angle of cam
            current_angle = i * rotation_step
            angle_degrees = np.degrees(current_angle)
            
            # Find contact point at current cam angle
            contact_y = find_top_contact(current_angle)
            
            # Position roller center (roller radius above contact point)
            roller_center_y = contact_y + roller_radius
            roller.move_to([follower_x, roller_center_y, 0])
            
            # Update roller center pin
            roller_center_pin.move_to([follower_x, roller_center_y, 0])
            
            # Update roller arc (rotation indicator)
            roller_arc.move_to([follower_x, roller_center_y, 0])
            roller_arc.rotate(current_angle, about_point=[follower_x, roller_center_y, 0])
            
            # Update pin support connection
            pin_support.put_start_and_end_on(
                [follower_x, roller_center_y, 0],
                [follower_x, roller_center_y + roller_radius + stem_height/2 - stem_height/2, 0]
            )
            
            # Update support base position
            support_base.move_to([follower_x, roller_center_y + roller_radius + stem_height + 0.1, 0])
            
            # Update guide rails
            left_guide.put_start_and_end_on(
                [follower_x - 0.08, roller_center_y, 0],
                [follower_x - 0.08, roller_center_y + stem_height, 0]
            )
            right_guide.put_start_and_end_on(
                [follower_x + 0.08, roller_center_y, 0],
                [follower_x + 0.08, roller_center_y + stem_height, 0]
            )
            
            # Update stem position (above roller)
            stem.move_to([follower_x, roller_center_y + roller_radius + stem_height/2, 0])
            
            # Update contact dot (at bottom of roller, touching cam)
            contact_dot.move_to([follower_x, contact_y, 0])
            
            # Calculate displacement (vertical distance from base)
            displacement = contact_y - base_y
            # Normalize for graph (shift to positive range 0-2.5)
            s_normalized = np.clip(displacement + 1.0, 0.1, 2.4)
            
            # Add point to curve
            graph_point = graph_axes.c2p(angle_degrees, s_normalized)
            curve_points.append(graph_point)
            
            # Update displacement curve
            if len(curve_points) > 1:
                displacement_curve.set_points_as_corners(curve_points)
                if i == 1:
                    self.add(displacement_curve)
            
            # Update graph dot
            graph_dot.move_to(graph_point)
            
            # Update horizontal alignment line (sync with graph point Y-coordinate)
            alignment_line.put_start_and_end_on(
                [follower_x, graph_point[1], 0],
                graph_point
            )
            
            # Rotate cam
            cam.rotate(rotation_step, about_point=cam_center)
            
            # Consistent smooth timing
            self.wait(0.04)
        
        # Highlight the complete curve
        self.play(
            displacement_curve.animate.set_stroke(width=6),
            run_time=0.3
        )
        self.play(
            displacement_curve.animate.set_stroke(width=4),
            run_time=0.3
        )
        
        self.wait(1.5)
        
        # Conclusion
        conclusion = Text(
            "Follower moves vertically along centerline • Contact & graph aligned horizontally",
            font_size=18,
            color=GOLD
        ).to_edge(DOWN, buff=0.5)
        
        self.play(Write(conclusion))
        self.wait(2)
        
        # Fade out
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)