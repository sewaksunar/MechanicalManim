from manim import *


# Three-link mechanism with left joint as a slider
class ThreeLinkSliderMechanism(Scene):
    def construct(self):
        # Parameters (unchanged lengths)
        r1 = 1.5
        r2 = 2.0
        r3 = 2.5

        # ValueTracker for slider position (as a fraction along the lower link)
        t = ValueTracker(0.0)  # t in [0, 1]

        # Fixed triangle base
        A = LEFT * 2
        B = A + np.array([r1 + r2, 0, 0])

        # Helper to get current slider position (on AB)
        def get_slider():
            return A + (B - A) * t.get_value()

        # C is determined by intersection of two circles (from slider, r3; from B, r2)
        def get_C():
            S = get_slider()
            # Find intersection of two circles: center S, radius r3; center B, radius r2
            # See: https://math.stackexchange.com/questions/256100/how-can-i-find-the-points-at-which-two-circles-intersect
            d = np.linalg.norm(B - S)
            if d > r2 + r3 or d < abs(r2 - r3) or d == 0:
                # No solution, return a default
                return S + np.array([0, r3, 0])
            a = (r3**2 - r2**2 + d**2) / (2 * d)
            h = np.sqrt(max(r3**2 - a**2, 0))
            P2 = S + a * (B - S) / d
            # Intersection points
            offset = h * np.array([-(B - S)[1], (B - S)[0], 0]) / d
            C1 = P2 + offset
            C2 = P2 - offset
            # Choose the upper intersection (higher y)
            return C1 if C1[1] > C2[1] else C2

        # Dynamic parts using always_redraw
        link1 = always_redraw(lambda: Line(A, B, color=YELLOW, stroke_width=5))
        link2 = always_redraw(lambda: Line(get_slider(), get_C(), color=GREEN, stroke_width=5))
        link3 = always_redraw(lambda: Line(get_C(), get_slider(), color=BLUE, stroke_width=5))
        slider_joint = always_redraw(lambda: Rectangle(width=0.3, height=0.6, color=RED, fill_opacity=0.8).move_to(get_slider()))
        joint_b = always_redraw(lambda: Dot(B, color=RED))
        joint_c = always_redraw(lambda: Dot(get_C(), color=RED))

        self.add(link1, link2, link3, slider_joint, joint_b, joint_c)

        # Animate the slider moving along the lower link
        self.play(t.animate.set_value(1.0), run_time=5, rate_func=there_and_back)
        self.wait(2)

class DefaultTemplate(Scene):
    def construct(self):
        circle = Circle()  # create a circle
        circle.set_fill(PINK, opacity=0.5)  # set color and transparency

        square = Square()  # create a square
        square.flip(RIGHT)  # flip horizontally
        square.rotate(-3 * TAU / 8)  # rotate a certain amount

        self.play(Create(square))  # animate the creation of the square
        self.play(Transform(square, circle))  # interpolate the square into the circle
        self.play(FadeOut(square))  # fade out animation

class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()  # create a circle
        circle.set_fill(PINK, opacity=0.5)  # set color and transparency

        square = Square()  # create a square
        square.rotate(PI / 4)  # rotate a certain amount

        self.play(Create(square))  # animate the creation of the square
        self.play(Transform(square, circle))  # interpolate the square into the circle
        self.play(FadeOut(square))  # fade out animation

class Graph(Scene):
    def construct(self):
        axes = Axes()
        self.add(axes)
        self.play(Create(axes))

class SliderCrankMechanism(Scene):
    def construct(self):
        # Parameters
        r = 1.5  # Crank length
        l = 4.0  # Connecting rod length
        
        # ValueTracker for the crank angle
        theta = ValueTracker(0)
        
        # Center of rotation for the crank
        center = LEFT * 2
        
        # Helper functions to calculate positions
        def get_point_b():
            angle = theta.get_value()
            return center + np.array([r * np.cos(angle), r * np.sin(angle), 0])
            
        def get_point_c():
            angle = theta.get_value()
            y_b = r * np.sin(angle)
            x_b = r * np.cos(angle)
            
            # Calculate slider x position using geometry
            # (x_c - x_b)^2 + (0 - y_b)^2 = l^2
            term = l**2 - y_b**2
            if term < 0: term = 0 # Safety
            x_c = x_b + np.sqrt(term)
            
            return center + np.array([x_c, 0, 0])

        # Static parts
        pivot = Dot(center, color=WHITE)
        path = Circle(radius=r, color=WHITE, stroke_opacity=0.2).move_to(center)
        
        # Ground/Track
        ground = Line(center + RIGHT * (r - l - 2) + DOWN * 0.3, center + RIGHT * (r + l + 2) + DOWN * 0.3, color=GREY)
        
        # Dynamic parts using always_redraw
        crank = always_redraw(lambda: Line(center, get_point_b(), color=YELLOW, stroke_width=5))
        joint = always_redraw(lambda: Dot(get_point_b(), color=RED))
        rod = always_redraw(lambda: Line(get_point_b(), get_point_c(), color=GREEN, stroke_width=5))
        slider = always_redraw(lambda: Rectangle(width=1.0, height=0.6, color=BLUE, fill_opacity=0.8).move_to(get_point_c()))
        
        # Add everything to scene
        self.add(pivot, path, ground, crank, joint, rod, slider)
        
        # Animate
        self.play(theta.animate.set_value(4 * PI), run_time=6, rate_func=linear)

class Pendulum(Scene):
    def construct(self):
        # Parameters
        length = 3.0
        bob_radius = 0.2
        
        # ValueTracker for angle
        angle = ValueTracker(PI / 4)  # Start at 45 degrees
        
        # Pivot point
        pivot = UP * 2
        
        # Helper functions to get bob position
        def get_bob_position():
            a = angle.get_value()
            return pivot + np.array([length * np.sin(a), -length * np.cos(a), 0])
        
        # Static parts
        pivot_dot = Dot(pivot, color=WHITE)
        
        # Dynamic parts using always_redraw
        rod = always_redraw(lambda: Line(pivot, get_bob_position(), color=YELLOW, stroke_width=5))
        bob = always_redraw(lambda: Circle(radius=bob_radius, color=RED, fill_opacity=0.8).move_to(get_bob_position()))
        
        # Add everything to scene
        self.add(pivot_dot, rod, bob)
        
        # Animate swinging
        self.play(angle.animate.set_value(-PI / 4), run_time=2, rate_func=there_and_back)

class BouncingBall(Scene):
    def construct(self):
        # Parameters
        floor_y = -3
        ball_radius = 0.3
        
        # Ball initial position
        ball = Circle(radius=ball_radius, color=BLUE, fill_opacity=0.8).move_to(UP * 3)
        
        # Floor
        floor = Line(LEFT * 7 + DOWN * 3, RIGHT * 7 + DOWN * 3, color=GREY)
        
        # Add floor and ball to scene
        self.add(floor, ball)
        
        # Animation: Bouncing effect
        for _ in range(3):
            self.play(ball.animate.move_to(DOWN * 3 + UP * ball_radius), run_time=0.5, rate_func=there_and_back)
            self.play(ball.animate.move_to(UP * 3), run_time=0.5, rate_func=smooth)


class planerMechanism(Scene):
    def construct(self):
        # Parameters
        r = 1.5  # Crank length
        l = 4.0  # Connecting rod length
        
        # ValueTracker for the crank angle
        theta = ValueTracker(0)
        
        # Center of rotation for the crank
        center = LEFT * 2
        
        # Helper functions to calculate positions
        def get_point_b():
            angle = theta.get_value()
            return center + np.array([r * np.cos(angle), r * np.sin(angle), 0])
            
        def get_point_c():
            angle = theta.get_value()
            y_b = r * np.sin(angle)
            x_b = r * np.cos(angle)
            
            # Calculate slider x position using geometry
            # (x_c - x_b)^2 + (0 - y_b)^2 = l^2
            term = l**2 - y_b**2
            if term < 0: term = 0 # Safety
            x_c = x_b + np.sqrt(term)
            
            return center + np.array([x_c, 0, 0])

        # Static parts
        pivot = Dot(center, color=WHITE)
        path = Circle(radius=r, color=WHITE, stroke_opacity=0.2).move_to(center)
        
        # Ground/Track
        ground = Line(center + RIGHT * (r - l - 2) + DOWN * 0.3, center + RIGHT * (r + l + 2) + DOWN * 0.3, color=GREY)
        
        # Dynamic parts using always_redraw
        crank = always_redraw(lambda: Line(center, get_point_b(), color=YELLOW, stroke_width=5))
        joint = always_redraw(lambda: Dot(get_point_b(), color=RED))
        rod = always_redraw(lambda: Line(get_point_b(), get_point_c(), color=GREEN, stroke_width=5))
        slider = always_redraw(lambda: Rectangle(width=1.0, height=0.6, color=BLUE, fill_opacity=0.8).move_to(get_point_c()))
        
        # Add everything to scene
        self.add(pivot, path, ground, crank, joint, rod, slider)
        
        # Animate
        self.play(theta.animate.set_value(4 * PI), run_time=6, rate_func=linear)

class ZeroMobilityStrucutre(Scene):
    def construct(self):
        # Parameters
        r = 1.5  # Crank length
        l = 4.0  # Connecting rod length
        
        # ValueTracker for the crank angle
        theta = ValueTracker(0)
        
        # Center of rotation for the crank
        center = LEFT * 2
        
        # Helper functions to calculate positions
        def get_point_b():
            angle = theta.get_value()
            return center + np.array([r * np.cos(angle), r * np.sin(angle), 0])
            
        def get_point_c():
            angle = theta.get_value()
            y_b = r * np.sin(angle)
            x_b = r * np.cos(angle)
            
            # Calculate slider x position using geometry
            # (x_c - x_b)^2 + (0 - y_b)^2 = l^2
            term = l**2 - y_b**2
            if term < 0: term = 0 # Safety
            x_c = x_b + np.sqrt(term)
            
            return center + np.array([x_c, 0, 0])

        # Static parts
        pivot = Dot(center, color=WHITE)
        path = Circle(radius=r, color=WHITE, stroke_opacity=0.2).move_to(center)
        
        # Ground/Track
        ground = Line(center + RIGHT * (r - l - 2) + DOWN * 0.3, center + RIGHT * (r + l + 2) + DOWN * 0.3, color=GREY)
        
        # Dynamic parts using always_redraw
        crank = always_redraw(lambda: Line(center, get_point_b(), color=YELLOW, stroke_width=5))
        joint = always_redraw(lambda: Dot(get_point_b(), color=RED))
        rod = always_redraw(lambda: Line(get_point_b(), get_point_c(), color=GREEN, stroke_width=5))
        slider = always_redraw(lambda: Rectangle(width=1.0, height=0.6, color=BLUE, fill_opacity=0.8).move_to(get_point_c()))
        
        # Add everything to scene
        self.add(pivot, path, ground, crank, joint, rod, slider)
        
        # Animate
        self.play(theta.animate.set_value(4 * PI), run_time=6, rate_func=linear)

# creating a scene that respresnt a three link planar mechanism with n = 3, j1 = 3, j2 = 0, j3 = 0, m = 1
class ThreeLinkPlanarMechanism(Scene):
    def construct(self):
        # Parameters (unchanged lengths)
        r1 = 1.5
        r2 = 2.0
        r3 = 2.5

        # Triangle vertices (closed loop, m=0)
        A = LEFT * 2
        B = A + np.array([r1, 0, 0])
        # C is determined by intersection of two circles (from B, r2; from A, r3)
        # Place C above AB for illustration
        # Law of cosines to get angle at A
        a = r2
        b = r3
        c = r1
        cos_angle = (b**2 + c**2 - a**2) / (2 * b * c)
        angle = np.arccos(np.clip(cos_angle, -1, 1))
        # C is at distance r3 from A, at angle above AB
        C = A + np.array([
            r3 * np.cos(angle),
            r3 * np.sin(angle),
            0
        ])

        # Draw links
        link1 = Line(A, B, color=YELLOW, stroke_width=5)
        link2 = Line(B, C, color=GREEN, stroke_width=5)
        link3 = Line(C, A, color=BLUE, stroke_width=5)

        # Draw joints
        joint_a = Dot(A, color=RED)
        joint_b = Dot(B, color=RED)
        joint_c = Dot(C, color=RED)

        self.add(link1, link2, link3, joint_a, joint_b, joint_c)
        self.wait(4)

from manim import *

class ThreeLinkOneSliderMechanism(Scene):
    def construct(self):
        # Link lengths (fixed)
        r_AS = 3.0  # Length from A to Slider (along horizontal track)
        r_SC = 2.5  # Length from Slider to C (constant)
        r_CA = 2.0  # Length from C to A (constant)
        
        # Fixed points
        A = LEFT * 1.5 + DOWN * 0.5  # Fixed pivot point A
        
        # Slider track (horizontal line through A)
        track_length = 5
        track = Line(
            A + LEFT * 1.5, 
            A + RIGHT * track_length, 
            color=GRAY, 
            stroke_width=3
        )
        track_base = Rectangle(
            width=track_length + 1.5,
            height=0.15,
            color=DARK_GRAY,
            fill_opacity=1
        ).move_to(track.get_center())
        
        # ValueTracker for slider position along track
        slider_pos = ValueTracker(0.5)  # Position in [0, 1] along valid range
        
        # Calculate valid slider range where mechanism can exist
        # Slider must satisfy: |r_SC - r_CA| <= distance_to_A <= r_SC + r_CA
        min_dist = abs(r_SC - r_CA)
        max_dist = r_SC + r_CA
        
        def get_slider_point():
            # Slider moves along horizontal line through A
            t = slider_pos.get_value()
            dist = min_dist + t * (max_dist - min_dist)
            return A + RIGHT * dist
        
        def get_C_point():
            S = get_slider_point()
            # C is at intersection of:
            # - Circle centered at S with radius r_SC
            # - Circle centered at A with radius r_CA
            
            d = np.linalg.norm(S - A)
            
            # Check if circles intersect
            if d > r_SC + r_CA or d < abs(r_SC - r_CA) or d < 0.001:
                # Return default position above
                return S + UP * r_SC
            
            # Find intersection using circle intersection formula
            a = (r_SC**2 - r_CA**2 + d**2) / (2 * d)
            h = np.sqrt(max(r_SC**2 - a**2, 0))
            
            # Point along AS line
            P = S + a * (A - S) / d
            
            # Perpendicular offset (choose upper point)
            direction = (A - S) / d
            perpendicular = np.array([-direction[1], direction[0], 0])
            
            C1 = P + h * perpendicular
            C2 = P - h * perpendicular
            
            # Choose upper intersection
            return C1 if C1[1] > C2[1] else C2
        
        # Create dynamic elements with always_redraw
        link_AS = always_redraw(lambda: Line(
            A, get_slider_point(),
            color=YELLOW,
            stroke_width=6
        ))
        
        link_SC = always_redraw(lambda: Line(
            get_slider_point(), get_C_point(),
            color=GREEN,
            stroke_width=6
        ))
        
        link_CA = always_redraw(lambda: Line(
            get_C_point(), A,
            color=BLUE,
            stroke_width=6
        ))
        
        # Slider block (rectangular)
        slider_block = always_redraw(lambda: VGroup(
            Rectangle(
                width=0.5,
                height=0.4,
                color=RED,
                fill_opacity=1,
                stroke_width=2,
                stroke_color=WHITE
            ).move_to(get_slider_point() + UP * 0.05),
            # Slider groove
            Line(
                get_slider_point() + DOWN * 0.15 + LEFT * 0.2,
                get_slider_point() + DOWN * 0.15 + RIGHT * 0.2,
                color=DARK_GRAY,
                stroke_width=8
            )
        ))
        
        # Joints (circular pivots)
        joint_A = always_redraw(lambda: Dot(
            A, 
            color=RED_E, 
            radius=0.12,
            stroke_width=2,
            stroke_color=WHITE
        ))
        
        joint_C = always_redraw(lambda: Dot(
            get_C_point(), 
            color=RED_E, 
            radius=0.12,
            stroke_width=2,
            stroke_color=WHITE
        ))
        
        # Labels with better positioning
        label_A = always_redraw(lambda: MathTex(
            "A", 
            font_size=40,
            color=YELLOW
        ).next_to(A, DOWN + LEFT, buff=0.2))
        
        label_S = always_redraw(lambda: MathTex(
            "S", 
            font_size=40,
            color=RED
        ).next_to(get_slider_point(), DOWN, buff=0.4))
        
        label_C = always_redraw(lambda: MathTex(
            "C", 
            font_size=40,
            color=GREEN
        ).next_to(get_C_point(), UP + RIGHT, buff=0.2))
        
        # Length annotations
        length_AS = always_redraw(lambda: MathTex(
            f"\\ell_{{AS}}",
            font_size=28,
            color=YELLOW
        ).next_to(link_AS.get_center(), DOWN, buff=0.1))
        
        length_SC = always_redraw(lambda: MathTex(
            f"\\ell_{{SC}} = {r_SC:.1f}",
            font_size=28,
            color=GREEN
        ).next_to(link_SC.get_center(), LEFT, buff=0.15))
        
        length_CA = always_redraw(lambda: MathTex(
            f"\\ell_{{CA}} = {r_CA:.1f}",
            font_size=28,
            color=BLUE
        ).next_to(link_CA.get_center(), RIGHT, buff=0.15))
        
        # Title
        title = Text(
            "Three-Link Slider-Crank Mechanism",
            font_size=36
        ).to_edge(UP)
        
        # Add all elements to scene
        self.add(track_base, track)
        self.add(link_AS, link_SC, link_CA)
        self.add(slider_block, joint_A, joint_C)
        self.add(label_A, label_S, label_C)
        self.add(length_SC, length_CA)
        self.add(title)
        
        # Animate slider movement
        self.play(
            slider_pos.animate.set_value(0.95),
            run_time=4,
            rate_func=smooth
        )
        self.play(
            slider_pos.animate.set_value(0.05),
            run_time=4,
            rate_func=smooth
        )
        self.play(
            slider_pos.animate.set_value(0.5),
            run_time=3,
            rate_func=smooth
        )
        self.wait(2)

class Test(Scene):
    def construct(self):
        # text = Text("Test Scene")
        # self.add(text)
        # A = LEFT * 2
        # B = A + np.array([3, 0, 0])
        # circle = Circle(radius=1.0).move_to(B)
        # self.add(circle)
        # mattex = MathTex(r"\int_a^b f(x) \, dx = F(b) - F(a)").to_edge(DOWN)
        # self.add(mattex)
        title = Text("Kutzbach Criterion Example").to_edge(UP)
        self.add(title)
        cfig = -2
        ab = 5
        p1 = [-ab/2, cfig, 0]
        p2 = p1 + np.array([ab, 0, 0])
        A = Dot(p1, color=RED)
        B = Dot(p2, color=BLUE)
        self.add(A, B)
        line = Line(p1, p2)
        self.add(line)

        ac = 5
        theta = PI/6  # 30 degrees
        dx = ac * np.cos(theta)
        dy = ac * np.sin(theta)
        p3 = p1 + np.array([dx, dy, 0])        
        C = Dot(p3, color=GREEN)
        self.add(C)

        line2 = Line(p1, p3)
        self.add(line2)
        self.play(Create(line2))
        line3 = Line(p2, p3)
        self.add(line3)
        self.play(Create(line3))

from manim import *

class Test2(Scene):
    def construct(self):
        # Title
        title = Text("Kutzbach Criterion Illustration", font_size=42).to_edge(UP)
        self.add(title)
        
        # Define link lengths (FIXED - these never change)
        self.L_AB = 4.0
        self.L_BC = 3.0
        self.L_CD = 3.5
        self.L_DA = 2.0
        
        # Initial positions for mechanism at CENTER
        y_base = -0.5
        x_offset = 0
        
        self.p_A = np.array([x_offset - self.L_AB/2, y_base, 0])
        self.p_B = np.array([x_offset + self.L_AB/2, y_base, 0])
        
        # Initial angle for link DA
        self.initial_angle = 2*PI/3
        
        # Calculate initial positions
        p_D_init = self.get_point_D(self.initial_angle)
        p_C_init = self.get_point_C(p_D_init)
        
        # Fixed supports at A and B
        support_A = self.create_fixed_support(self.p_A)
        support_B = self.create_fixed_support(self.p_B)
        
        # Links
        self.link1 = Line(self.p_A, self.p_B, color=WHITE, stroke_width=6)
        self.link2 = Line(self.p_B, p_C_init, color=WHITE, stroke_width=6)
        self.link3 = Line(p_C_init, p_D_init, color=WHITE, stroke_width=6)
        self.link4 = Line(p_D_init, self.p_A, color=WHITE, stroke_width=6)
        
        # Pin joints (hollow circles)
        self.joint_A = self.create_pin_joint(self.p_A, BLUE)
        self.joint_B = self.create_pin_joint(self.p_B, BLUE)
        self.joint_C = self.create_pin_joint(p_C_init, RED)
        self.joint_D = self.create_pin_joint(p_D_init, RED)
        
        # Labels
        self.label_A = MathTex("A", font_size=36, color=BLUE).next_to(self.p_A, DOWN, buff=0.5)
        self.label_B = MathTex("B", font_size=36, color=BLUE).next_to(self.p_B, DOWN, buff=0.5)
        self.label_C = MathTex("C", font_size=36, color=RED).next_to(p_C_init, UP+RIGHT, buff=0.2)
        self.label_D = MathTex("D", font_size=36, color=RED).next_to(p_D_init, UP+LEFT, buff=0.2)
        
        # Link labels showing fixed lengths
        self.label_link1 = MathTex(f"L_{{AB}}={self.L_AB:.1f}", font_size=24).next_to(self.link1.get_center(), DOWN, buff=0.1)
        self.label_link2 = MathTex(f"L_{{BC}}={self.L_BC:.1f}", font_size=24).next_to(self.link2.get_center(), RIGHT, buff=0.1)
        self.label_link3 = MathTex(f"L_{{CD}}={self.L_CD:.1f}", font_size=24).next_to(self.link3.get_center(), UP, buff=0.1)
        self.label_link4 = MathTex(f"L_{{DA}}={self.L_DA:.1f}", font_size=24).next_to(self.link4.get_center(), LEFT, buff=0.1)
        
        # Animation sequence - Build mechanism
        self.play(FadeIn(support_A), FadeIn(support_B), run_time=0.8)
        self.wait(0.3)
        
        self.play(
            Create(self.link1),
            FadeIn(self.joint_A),
            FadeIn(self.joint_B),
            run_time=1
        )
        self.play(FadeIn(self.label_A), FadeIn(self.label_B), FadeIn(self.label_link1), run_time=0.6)
        self.wait(0.4)
        
        self.play(Create(self.link2), FadeIn(self.joint_C), run_time=1)
        self.play(FadeIn(self.label_C), FadeIn(self.label_link2), run_time=0.6)
        self.wait(0.4)
        
        self.play(Create(self.link3), FadeIn(self.joint_D), run_time=1)
        self.play(FadeIn(self.label_D), FadeIn(self.label_link3), run_time=0.6)
        self.wait(0.4)
        
        self.play(Create(self.link4), FadeIn(self.label_link4), run_time=1)
        self.wait(1)
        
        # Group all mechanism elements
        mechanism_group = VGroup(
            support_A, support_B,
            self.link1, self.link2, self.link3, self.link4,
            self.joint_A, self.joint_B, self.joint_C, self.joint_D,
            self.label_A, self.label_B, self.label_C, self.label_D,
            self.label_link1, self.label_link2, self.label_link3, self.label_link4
        )
        
        # Store the scale factor for later updates
        self.scale_factor = 0.65
        target_x = -3.2
        
        # Move mechanism to left and scale down
        self.play(
            mechanism_group.animate.scale(self.scale_factor).move_to(np.array([target_x, -0.8, 0])),
            run_time=1.2
        )
        
        # Update the base points after scaling and moving
        center_before = (self.p_A + self.p_B) / 2
        center_after = np.array([target_x, -0.8, 0])
        
        self.p_A = center_after + self.scale_factor * (self.p_A - center_before)
        self.p_B = center_after + self.scale_factor * (self.p_B - center_before)
        self.L_AB *= self.scale_factor
        self.L_BC *= self.scale_factor
        self.L_CD *= self.scale_factor
        self.L_DA *= self.scale_factor
        
        # Show Kutzbach formula on RIGHT side
        formula_box = Rectangle(width=5.5, height=5.5, color=BLUE_D, fill_opacity=0.1).shift(RIGHT * 3.3 + DOWN * 0.3)
        
        formula_title = Text("Kutzbach Criterion:", font_size=28).move_to(RIGHT * 3.3 + UP * 1.7)
        formula = MathTex(
            "DOF = 3(n-1) - 2j_1 - j_2",
            font_size=32
        ).next_to(formula_title, DOWN, buff=0.4)
        
        # Parameter values
        params = VGroup(
            MathTex("n = 4 \\text{ (links)}", font_size=26, color=YELLOW),
            MathTex("j_1 = 4 \\text{ (revolute)}", font_size=26, color=YELLOW),
            MathTex("j_2 = 0", font_size=26, color=YELLOW),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT).next_to(formula, DOWN, buff=0.4).set_x(3.3)
        
        # Calculation
        calculation = MathTex(
            "DOF = 3(4-1) - 2(4) - 0",
            font_size=27
        ).next_to(params, DOWN, buff=0.35).set_x(3.3)
        
        calculation2 = MathTex(
            "= 9 - 8",
            font_size=27
        ).next_to(calculation, DOWN, buff=0.2).set_x(3.3)
        
        result = MathTex(
            "\\boxed{DOF = 1}",
            font_size=34,
            color=GREEN
        ).next_to(calculation2, DOWN, buff=0.4).set_x(3.3)
        
        self.play(Create(formula_box), run_time=0.5)
        self.play(Write(formula_title), run_time=0.8)
        self.play(Write(formula), run_time=1)
        self.wait(0.5)
        self.play(FadeIn(params), run_time=1)
        self.wait(0.5)
        self.play(Write(calculation), run_time=1)
        self.play(Write(calculation2), run_time=0.8)
        self.wait(0.5)
        self.play(Write(result), run_time=1)
        self.wait(1)
        
        # Add mobility demonstration text
        mobility_text = Text(
            "Demonstrating motion:",
            font_size=26,
            color=YELLOW
        ).next_to(result, DOWN, buff=0.5).set_x(3.3)
        
        self.play(FadeIn(mobility_text), run_time=0.8)
        self.wait(0.5)
        
        # Demonstrate motion with RIGID links
        self.demonstrate_motion()
        
        self.wait(2)
    
    def get_point_D(self, angle):
        """Calculate position of D based on angle from A"""
        return self.p_A + self.L_DA * np.array([np.cos(angle), np.sin(angle), 0])
    
    def get_point_C(self, p_D):
        """Calculate position of C using circle intersection (RIGID GEOMETRY)"""
        # C is at intersection of:
        # Circle 1: center B, radius L_BC
        # Circle 2: center D, radius L_CD
        
        d = np.linalg.norm(self.p_B - p_D)
        
        # Check if solution exists
        if d < 0.01 or d > self.L_BC + self.L_CD or d < abs(self.L_BC - self.L_CD):
            # Return approximate position
            return self.p_B + self.L_BC * np.array([np.cos(PI/3), np.sin(PI/3), 0])
        
        # Use circle intersection formula
        a = (self.L_BC**2 - self.L_CD**2 + d**2) / (2 * d)
        h_sq = self.L_BC**2 - a**2
        
        if h_sq < 0:
            h_sq = 0
        
        h = np.sqrt(h_sq)
        
        # Point on line BD
        P = self.p_B + a * (p_D - self.p_B) / d
        
        # Perpendicular direction
        direction = (p_D - self.p_B) / d
        perpendicular = np.array([-direction[1], direction[0], 0])
        
        # Two possible positions
        C1 = P + h * perpendicular
        C2 = P - h * perpendicular
        
        # Choose upper position
        return C1 if C1[1] > C2[1] else C2
    
    def demonstrate_motion(self):
        """Animate mechanism with RIGID links"""
        # ValueTracker for angle
        angle_tracker = ValueTracker(self.initial_angle)
        
        def update_mechanism(mob):
            angle = angle_tracker.get_value()
            
            # Calculate new positions using RIGID geometry
            new_D = self.get_point_D(angle)
            new_C = self.get_point_C(new_D)
            
            # Get current positions of A and B (they should be fixed)
            current_A = self.joint_A.get_center()
            current_B = self.joint_B.get_center()
            
            # Update links - make sure they connect to CURRENT A and B positions
            self.link1.become(Line(current_A, current_B, color=WHITE, stroke_width=6))
            self.link2.become(Line(current_B, new_C, color=WHITE, stroke_width=6))
            self.link3.become(Line(new_C, new_D, color=WHITE, stroke_width=6))
            self.link4.become(Line(new_D, current_A, color=WHITE, stroke_width=6))
            
            # Update joints
            self.joint_C.move_to(new_C)
            self.joint_D.move_to(new_D)
            
            # Update labels
            self.label_C.next_to(new_C, UP+RIGHT, buff=0.15)
            self.label_D.next_to(new_D, UP+LEFT, buff=0.15)
            self.label_link2.next_to(self.link2.get_center(), RIGHT, buff=0.1)
            self.label_link3.next_to(self.link3.get_center(), UP, buff=0.1)
            self.label_link4.next_to(self.link4.get_center(), LEFT, buff=0.1)
        
        # Add updater
        self.link2.add_updater(update_mechanism)
        
        # Animate - smooth rotation
        self.play(
            angle_tracker.animate.set_value(self.initial_angle + PI/2.5),
            run_time=3,
            rate_func=smooth
        )
        self.play(
            angle_tracker.animate.set_value(self.initial_angle - PI/4),
            run_time=3,
            rate_func=smooth
        )
        self.play(
            angle_tracker.animate.set_value(self.initial_angle),
            run_time=2,
            rate_func=smooth
        )
        
        # Remove updater
        self.link2.remove_updater(update_mechanism)
    
    def create_pin_joint(self, position, color):
        """Create a simple pin joint (single hollow circle)"""
        return Circle(
            radius=0.12,
            color=color,
            stroke_width=3,
            fill_opacity=0
        ).move_to(position)
    
    def create_fixed_support(self, position):
        """Create a simple fixed support with triangle, hatching, and hollow dot"""
        # Triangle
        triangle = Polygon(
            position + np.array([-0.3, -0.2, 0]),
            position + np.array([0.3, -0.2, 0]),
            position,
            color=DARK_GRAY,
            fill_opacity=1,
            stroke_width=0
        )
        
        # Ground base line
        ground_line = Line(
            position + np.array([-0.4, -0.2, 0]),
            position + np.array([0.4, -0.2, 0]),
            color=DARK_GRAY,
            stroke_width=4
        )
        
        # Hash lines
        hash_lines = VGroup(*[
            Line(
                position + np.array([-0.4 + i*0.1, -0.2, 0]),
                position + np.array([-0.5 + i*0.1, -0.35, 0]),
                color=DARK_GRAY,
                stroke_width=2
            )
            for i in range(9)
        ])
        
        # Hollow dot at top corner (joint)
        hollow_dot = Circle(
            radius=0.12,
            color=WHITE,
            stroke_width=3,
            fill_opacity=0
        ).move_to(position)
        
        return VGroup(triangle, ground_line, hash_lines, hollow_dot)