from manim import *
import numpy as np

class CamFollowerDisplacement(Scene):
    """
    Professional cam-follower mechanism with:
    - Horizontal alignment through actual contact point
    - Fixed slider supports on both sides
    - Extended 400° graph
    - Improved roller and follower design
    """
    
    def construct(self):
        # ==================== CONFIGURATION ====================
        self.cam_center = LEFT * 4.5 + DOWN * 1.2
        self.base_radius = 1.0
        self.max_variation = 0.6
        self.roller_radius = 0.25
        self.follower_x = self.cam_center[0]
        
        # ==================== SCENE SETUP ====================
        self.show_title()
        
        # ==================== CREATE COMPONENTS ====================
        cam, center_dot, center_label, vertical_line = self.create_cam_system()
        graph_axes, x_label, y_label, x_ticks, grid = self.create_graph_system()
        slider_supports = self.create_slider_supports()
        
        # Show static elements
        self.play(
            Create(cam),
            Create(center_dot),
            Write(center_label),
            Create(vertical_line),
            *[Create(support) for support in slider_supports],
            run_time=1.2
        )
        
        self.play(
            Create(graph_axes),
            Write(x_label),
            Write(y_label),
            Create(x_ticks),
            Create(grid),
            run_time=1.2
        )
        
        # ==================== CREATE FOLLOWER ====================
        follower_parts = self.create_follower()
        
        # Show follower assembly
        self.play(
            *[Create(part) for part in [
                follower_parts['stem'],
                follower_parts['top_plate'],
                follower_parts['roller'],
                follower_parts['roller_inner'],
                follower_parts['bearing_outer'],
                follower_parts['bearing_inner'],
            ]],
            run_time=1.2
        )
        self.wait(0.3)
        
        # ==================== ANIMATION ====================
        self.animate_cam_rotation(cam, follower_parts, graph_axes, slider_supports)
        
        # ==================== CONCLUSION ====================
        self.show_conclusion()
        
    # ==================== HELPER METHODS ====================
    
    def get_cam_radius(self, theta):
        """Calculate cam radius at given angle with smooth profile"""
        variation = self.max_variation * (
            0.6 + 0.25 * np.sin(2 * theta) + 0.15 * np.sin(3 * theta)
        )
        return self.base_radius + variation
    
    def find_contact_point(self, cam_angle):
        """
        Find vertical contact point between cam and follower
        Returns Y-coordinate where cam surface touches vertical centerline
        """
        theta_contact = PI / 2 - cam_angle
        r = self.get_cam_radius(theta_contact)
        contact_y = self.cam_center[1] + r
        return contact_y
    
    def show_title(self):
        """Display and fade title"""
        title = Text(
            "Cam-Follower Displacement Analysis",
            font_size=38,
            color=TEAL_C,
            weight=BOLD
        ).to_edge(UP, buff=0.3)
        
        self.play(Write(title), run_time=0.8)
        self.wait(0.2)
        self.play(FadeOut(title), run_time=0.4)
    
    def create_cam_system(self):
        """Create cam, center point, and vertical guide line"""
        # Build cam profile
        n_points = 120
        angles = np.linspace(0, 2 * PI, n_points)
        cam_points = [
            [
                self.cam_center[0] + self.get_cam_radius(theta) * np.cos(theta),
                self.cam_center[1] + self.get_cam_radius(theta) * np.sin(theta),
                0
            ]
            for theta in angles
        ]
        
        cam = Polygon(
            *cam_points,
            color=TEAL_D,
            fill_opacity=0.8,
            stroke_color=TEAL_B,
            stroke_width=2.5
        )
        
        center_dot = Dot(self.cam_center, color=WHITE, radius=0.06)
        center_label = Text("O", font_size=20, color=WHITE).next_to(center_dot, DOWN, buff=0.12)
        
        vertical_line = DashedLine(
            self.cam_center + DOWN * 1.8,
            self.cam_center + UP * 3.5,
            color=GRAY,
            stroke_width=1.5,
            stroke_opacity=0.35,
            dash_length=0.08
        )
        
        return cam, center_dot, center_label, vertical_line
    
    def create_slider_supports(self):
        """Create short slider supports at top to show follower constraint"""
        slider_offset = 0.35
        slider_height = 1.2  # Much shorter - just to show constraint
        
        # Calculate position - should be at top of follower path
        slider_top_y = self.cam_center[1] + 3.0
        
        # Left slider support (short guide at top)
        left_slider = Rectangle(
            width=0.15,
            height=slider_height,
            color=BLUE_D,
            fill_opacity=0.6,
            stroke_color=BLUE_C,
            stroke_width=2
        ).move_to([self.follower_x - slider_offset, slider_top_y - slider_height/2, 0])
        
        # Right slider support (short guide at top)
        right_slider = Rectangle(
            width=0.15,
            height=slider_height,
            color=BLUE_D,
            fill_opacity=0.6,
            stroke_color=BLUE_C,
            stroke_width=2
        ).move_to([self.follower_x + slider_offset, slider_top_y - slider_height/2, 0])
        
        # Top connecting plate (shows constraint)
        top_constraint = Rectangle(
            width=0.9,
            height=0.15,
            color=BLUE_E,
            fill_opacity=0.7,
            stroke_color=BLUE_D,
            stroke_width=2
        ).move_to([self.follower_x, slider_top_y, 0])
        
        return [left_slider, right_slider, top_constraint]
    
    def create_graph_system(self):
        """Create graph axes with extended range to 400 degrees"""
        graph_axes = Axes(
            x_range=[0, 400, 100],
            y_range=[0, 2.5, 0.5],
            x_length=6.8,
            y_length=4.0,
            axis_config={
                "color": GRAY_B,
                "stroke_width": 2,
                "include_ticks": True,
                "tick_size": 0.05,
            },
            tips=True
        ).shift(RIGHT * 2.2 + DOWN * 0.15)
        
        x_label = Text("Cam Angle (degrees)", font_size=18).next_to(graph_axes.x_axis, DOWN, buff=0.35)
        y_label = MathTex("s", font_size=30).next_to(graph_axes.y_axis, LEFT, buff=0.25)
        
        x_ticks = VGroup(*[
            Text(str(x), font_size=15).next_to(graph_axes.c2p(x, 0), DOWN, buff=0.12)
            for x in [0, 100, 200, 300, 400]
        ])
        
        grid = VGroup(*[
            DashedLine(
                graph_axes.c2p(x, 0),
                graph_axes.c2p(x, 2.5),
                color=GRAY,
                stroke_width=0.8,
                stroke_opacity=0.12,
                dash_length=0.08
            ) for x in range(0, 401, 100)
        ])
        
        return graph_axes, x_label, y_label, x_ticks, grid
    
    def create_follower(self):
        """Create improved follower mechanism with better roller design"""
        initial_contact_y = self.find_contact_point(0)
        roller_center_y = initial_contact_y + self.roller_radius
        
        # Main roller (outer layer)
        roller = Circle(
            radius=self.roller_radius,
            color=RED_D,
            fill_opacity=0.75,
            stroke_color=RED_C,
            stroke_width=2.8
        ).move_to([self.follower_x, roller_center_y, 0])
        
        # Roller inner ring (darker)
        roller_inner = Circle(
            radius=self.roller_radius * 0.7,
            color=RED_E,
            fill_opacity=0.85,
            stroke_color=RED_D,
            stroke_width=1.5
        ).move_to([self.follower_x, roller_center_y, 0])
        
        # Bearing outer ring
        bearing_outer = Circle(
            radius=self.roller_radius * 0.35,
            color=GRAY_D,
            fill_opacity=0.9,
            stroke_color=GRAY_C,
            stroke_width=1.5
        ).move_to([self.follower_x, roller_center_y, 0])
        
        # Bearing center pin
        bearing_inner = Dot(
            [self.follower_x, roller_center_y, 0],
            color=DARK_GRAY,
            radius=0.05
        )
        
        # Main stem (follower body) - improved design
        stem_width = 0.22
        stem_height = 2.0
        stem = Rectangle(
            width=stem_width,
            height=stem_height,
            color=GREEN_D,
            fill_opacity=0.8,
            stroke_color=GREEN_C,
            stroke_width=2.5
        ).move_to([self.follower_x, roller_center_y + self.roller_radius + stem_height / 2, 0])
        
        # Top plate (follower top)
        top_plate = Rectangle(
            width=0.45,
            height=0.18,
            color=GREEN_E,
            fill_opacity=0.85,
            stroke_color=GREEN_D,
            stroke_width=2
        ).move_to([self.follower_x, roller_center_y + self.roller_radius + stem_height + 0.09, 0])
        
        return {
            'roller': roller,
            'roller_inner': roller_inner,
            'bearing_outer': bearing_outer,
            'bearing_inner': bearing_inner,
            'stem': stem,
            'top_plate': top_plate,
            'stem_height': stem_height,
            'initial_contact_y': initial_contact_y
        }
    
    def animate_cam_rotation(self, cam, follower_parts, graph_axes, slider_supports):
        """Animate with horizontal line through actual contact point"""
        # Unpack follower parts
        roller = follower_parts['roller']
        roller_inner = follower_parts['roller_inner']
        bearing_outer = follower_parts['bearing_outer']
        bearing_inner = follower_parts['bearing_inner']
        stem = follower_parts['stem']
        top_plate = follower_parts['top_plate']
        stem_height = follower_parts['stem_height']
        
        # Graph tracking
        displacement_curve = VMobject(color=YELLOW, stroke_width=3.5)
        graph_dot = Dot(color=YELLOW, radius=0.08)
        
        # Horizontal alignment line (will pass through contact point)
        alignment_line = DashedLine(
            LEFT, RIGHT,
            color=ORANGE,
            stroke_width=1.8,
            stroke_opacity=0.5,
            dash_length=0.12
        )
        
        self.add(graph_dot, alignment_line, displacement_curve)
        
        # Reference height
        base_y = self.cam_center[1] + self.base_radius
        
        # Store curve points
        curve_points = []
        
        # ValueTracker for smooth animation
        angle_tracker = ValueTracker(0)
        
        # Update function
        def update_mechanism(mob):
            current_angle = angle_tracker.get_value()
            # Convert to degrees, but allow beyond 360 for extended graph
            angle_degrees = np.degrees(current_angle)
            
            # Use modulo for cam rotation but keep full angle for graph
            cam_angle_for_contact = current_angle % (2 * PI)
            
            # Calculate contact point (actual contact between cam and roller)
            contact_y = self.find_contact_point(cam_angle_for_contact)
            roller_center_y = contact_y + self.roller_radius
            
            # Update all follower parts
            roller.move_to([self.follower_x, roller_center_y, 0])
            roller_inner.move_to([self.follower_x, roller_center_y, 0])
            bearing_outer.move_to([self.follower_x, roller_center_y, 0])
            bearing_inner.move_to([self.follower_x, roller_center_y, 0])
            stem.move_to([self.follower_x, roller_center_y + self.roller_radius + stem_height / 2, 0])
            top_plate.move_to([self.follower_x, roller_center_y + self.roller_radius + stem_height + 0.09, 0])
            
            # Calculate displacement
            displacement = contact_y - base_y
            s_normalized = np.clip(displacement + 1.0, 0.05, 2.45)
            
            # Update graph (extended to 400 degrees)
            if angle_degrees <= 400:
                graph_point = graph_axes.c2p(angle_degrees, s_normalized)
                
                # Add curve point
                curve_points.append(graph_point)
                if len(curve_points) > 1:
                    displacement_curve.set_points_as_corners(curve_points)
                
                graph_dot.move_to(graph_point)
                
                # IMPORTANT: Horizontal line passes through CONTACT POINT, not roller center
                # Contact point Y-coordinate matches with graph point Y-coordinate
                alignment_line.put_start_and_end_on(
                    [self.follower_x, contact_y, 0],  # Start at actual contact point
                    graph_point  # End at graph point
                )
        
        # Add updaters
        roller.add_updater(update_mechanism)
        
        # Animate rotation - go slightly beyond 360° to reach 400° on graph
        total_rotation = (400 / 360) * 2 * PI  # ~4.19 radians for 400°
        
        self.play(
            angle_tracker.animate.set_value(total_rotation),
            Rotate(cam, angle=total_rotation, about_point=self.cam_center),
            run_time=10,
            rate_func=linear
        )
        
        # Remove updaters
        roller.remove_updater(update_mechanism)
        
        # Highlight curve
        self.play(displacement_curve.animate.set_stroke(width=5, color=YELLOW_C), run_time=0.3)
        self.play(displacement_curve.animate.set_stroke(width=3.5, color=YELLOW), run_time=0.3)
        
        self.wait(1)
    
    def show_conclusion(self):
        """Display conclusion and fade out"""
        conclusion = Text(
            "Contact point alignment • Smooth displacement profile to 400°",
            font_size=17,
            color=GOLD_B
        ).to_edge(DOWN, buff=0.4)
        
        self.play(Write(conclusion), run_time=0.8)
        self.wait(2)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)