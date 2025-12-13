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
        
        # Define link lengths (FIXED)
        self.L_AB = 4.0
        self.L_BC = 3.0
        self.L_CD = 3.5
        self.L_DA = 2.0
        
        # Initial positions at CENTER
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
        
        # Create links with their own pin joints at both ends
        self.link1 = Line(self.p_A, self.p_B, color=WHITE, stroke_width=6)
        self.joint1_A = self.create_pin_joint(self.p_A, BLUE)
        self.joint1_B = self.create_pin_joint(self.p_B, BLUE)
        
        self.link2 = Line(self.p_B, p_C_init, color=WHITE, stroke_width=6)
        self.joint2_B = self.create_pin_joint(self.p_B, BLUE)
        self.joint2_C = self.create_pin_joint(p_C_init, RED)
        
        self.link3 = Line(p_C_init, p_D_init, color=WHITE, stroke_width=6)
        self.joint3_C = self.create_pin_joint(p_C_init, RED)
        self.joint3_D = self.create_pin_joint(p_D_init, RED)
        
        self.link4 = Line(p_D_init, self.p_A, color=WHITE, stroke_width=6)
        self.joint4_D = self.create_pin_joint(p_D_init, RED)
        self.joint4_A = self.create_pin_joint(self.p_A, BLUE)
        
        # Labels
        self.label_A = MathTex("A", font_size=36, color=BLUE).next_to(self.p_A, DOWN, buff=0.5)
        self.label_B = MathTex("B", font_size=36, color=BLUE).next_to(self.p_B, DOWN, buff=0.5)
        self.label_C = MathTex("C", font_size=36, color=RED).next_to(p_C_init, UP+RIGHT, buff=0.2)
        self.label_D = MathTex("D", font_size=36, color=RED).next_to(p_D_init, UP+LEFT, buff=0.2)
        
        # Animation sequence - Each link arrives as complete unit
        self.play(FadeIn(support_A), FadeIn(support_B), run_time=0.8)
        self.wait(0.3)
        
        # Link 1 with both joints
        link1_assembly = VGroup(self.link1, self.joint1_A, self.joint1_B)
        self.play(FadeIn(link1_assembly, shift=UP*0.5), run_time=0.8)
        self.play(FadeIn(self.label_A), FadeIn(self.label_B), run_time=0.4)
        self.wait(0.3)
        
        # Link 2 with both joints
        link2_assembly = VGroup(self.link2, self.joint2_B, self.joint2_C)
        self.play(FadeIn(link2_assembly, shift=DOWN*0.5+RIGHT*0.3), run_time=0.8)
        self.play(FadeIn(self.label_C), run_time=0.4)
        self.wait(0.3)
        
        # Link 3 with both joints
        link3_assembly = VGroup(self.link3, self.joint3_C, self.joint3_D)
        self.play(FadeIn(link3_assembly, shift=LEFT*0.5), run_time=0.8)
        self.play(FadeIn(self.label_D), run_time=0.4)
        self.wait(0.3)
        
        # Link 4 with both joints
        link4_assembly = VGroup(self.link4, self.joint4_D, self.joint4_A)
        self.play(FadeIn(link4_assembly, shift=DOWN*0.3), run_time=0.8)
        self.wait(0.5)
        
        # Group all mechanism elements
        mechanism_group = VGroup(
            support_A, support_B,
            self.link1, self.link2, self.link3, self.link4,
            self.joint1_A, self.joint1_B, self.joint2_B, self.joint2_C,
            self.joint3_C, self.joint3_D, self.joint4_D, self.joint4_A,
            self.label_A, self.label_B, self.label_C, self.label_D
        )
        
        # Scale and move to left
        self.scale_factor = 0.65
        target_x = -3.2
        
        self.play(
            mechanism_group.animate.scale(self.scale_factor).move_to(np.array([target_x, -0.8, 0])),
            run_time=1.2
        )
        
        # Update base points after scaling
        center_before = (self.p_A + self.p_B) / 2
        center_after = np.array([target_x, -0.8, 0])
        
        self.p_A = center_after + self.scale_factor * (self.p_A - center_before)
        self.p_B = center_after + self.scale_factor * (self.p_B - center_before)
        self.L_AB *= self.scale_factor
        self.L_BC *= self.scale_factor
        self.L_CD *= self.scale_factor
        self.L_DA *= self.scale_factor
        
        # Show Kutzbach formula on RIGHT
        formula_box = Rectangle(width=5.5, height=5.5, color=BLUE_D, fill_opacity=0.1).shift(RIGHT * 3.3 + DOWN * 0.3)
        
        formula_title = Text("Kutzbach Criterion:", font_size=28).move_to(RIGHT * 3.3 + UP * 1.7)
        formula = MathTex(
            "DOF = 3(n-1) - 2j_1 - j_2",
            font_size=32
        ).next_to(formula_title, DOWN, buff=0.4)
        
        params = VGroup(
            MathTex("n = 4 \\text{ (links)}", font_size=26, color=YELLOW),
            MathTex("j_1 = 4 \\text{ (revolute)}", font_size=26, color=YELLOW),
            MathTex("j_2 = 0", font_size=26, color=YELLOW),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT).next_to(formula, DOWN, buff=0.4).set_x(3.3)
        
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
        
        # n = 4 (highlight links with yellow glow)
        param_n = MathTex("n = 4 \\text{ (links)}", font_size=26, color=YELLOW)
        param_n.move_to(params[0].get_center())
        self.play(Write(param_n), run_time=0.8)
        
        # Create temporary thick yellow lines behind
        highlight_links = VGroup(
            Line(self.link1.get_start(), self.link1.get_end(), color=YELLOW, stroke_width=12),
            Line(self.link2.get_start(), self.link2.get_end(), color=YELLOW, stroke_width=12),
            Line(self.link3.get_start(), self.link3.get_end(), color=YELLOW, stroke_width=12),
            Line(self.link4.get_start(), self.link4.get_end(), color=YELLOW, stroke_width=12)
        )
        self.play(FadeIn(highlight_links), run_time=0.4)
        self.wait(0.5)
        self.play(FadeOut(highlight_links), run_time=0.4)
        self.wait(0.3)
        
        # j1 = 4 (highlight joints - one from each position)
        param_j1 = MathTex("j_1 = 4 \\text{ (revolute)}", font_size=26, color=YELLOW)
        param_j1.move_to(params[1].get_center())
        self.play(Write(param_j1), run_time=0.8)
        self.play(
            self.joint1_A.animate.set_stroke(width=5, color=YELLOW),
            self.joint1_B.animate.set_stroke(width=5, color=YELLOW),
            self.joint2_C.animate.set_stroke(width=5, color=YELLOW),
            self.joint3_D.animate.set_stroke(width=5, color=YELLOW),
            run_time=0.6
        )
        self.play(
            self.joint1_A.animate.set_stroke(width=3, color=BLUE),
            self.joint1_B.animate.set_stroke(width=3, color=BLUE),
            self.joint2_C.animate.set_stroke(width=3, color=RED),
            self.joint3_D.animate.set_stroke(width=3, color=RED),
            run_time=0.4
        )
        self.wait(0.3)
        
        # j2 = 0
        param_j2 = MathTex("j_2 = 0", font_size=26, color=YELLOW)
        param_j2.move_to(params[2].get_center())
        self.play(Write(param_j2), run_time=0.8)
        self.wait(0.5)
        
        # Show calculation
        self.play(Write(calculation), run_time=1)
        self.play(Write(calculation2), run_time=0.8)
        self.wait(0.5)
        self.play(Write(result), run_time=1)
        
        # Emphasize result
        self.play(result.animate.scale(1.15), run_time=0.5)
        self.play(result.animate.scale(1/1.15), run_time=0.5)
        self.wait(0.5)
        
        # Mobility demonstration text
        mobility_text = Text(
            "Demonstrating motion:",
            font_size=26,
            color=YELLOW
        ).next_to(result, DOWN, buff=0.5).set_x(3.3)
        
        self.play(FadeIn(mobility_text), run_time=0.8)
        self.wait(0.5)
        
        # Demonstrate motion
        self.demonstrate_motion()
        
        self.wait(2)
    
    def get_point_D(self, angle):
        """Calculate position of D based on angle from A"""
        return self.p_A + self.L_DA * np.array([np.cos(angle), np.sin(angle), 0])
    
    def get_point_C(self, p_D):
        """Calculate position of C using circle intersection"""
        d = np.linalg.norm(self.p_B - p_D)
        
        if d < 0.01 or d > self.L_BC + self.L_CD or d < abs(self.L_BC - self.L_CD):
            return self.p_B + self.L_BC * np.array([np.cos(PI/3), np.sin(PI/3), 0])
        
        a = (self.L_BC**2 - self.L_CD**2 + d**2) / (2 * d)
        h_sq = self.L_BC**2 - a**2
        h = np.sqrt(max(h_sq, 0))
        
        P = self.p_B + a * (p_D - self.p_B) / d
        direction = (p_D - self.p_B) / d
        perpendicular = np.array([-direction[1], direction[0], 0])
        
        C1 = P + h * perpendicular
        C2 = P - h * perpendicular
        
        return C1 if C1[1] > C2[1] else C2
    
    def demonstrate_motion(self):
        """Animate mechanism with RIGID links"""
        angle_tracker = ValueTracker(self.initial_angle)
        
        # Store fixed positions
        fixed_A = self.joint1_A.get_center().copy()
        fixed_B = self.joint1_B.get_center().copy()
        
        def update_mechanism(mob):
            angle = angle_tracker.get_value()
            
            # Calculate new positions
            new_D = fixed_A + self.L_DA * np.array([np.cos(angle), np.sin(angle), 0])
            
            d = np.linalg.norm(fixed_B - new_D)
            
            if d < 0.01 or d > self.L_BC + self.L_CD or d < abs(self.L_BC - self.L_CD):
                new_C = fixed_B + self.L_BC * np.array([np.cos(PI/3), np.sin(PI/3), 0])
            else:
                a = (self.L_BC**2 - self.L_CD**2 + d**2) / (2 * d)
                h_sq = self.L_BC**2 - a**2
                h = np.sqrt(max(h_sq, 0))
                
                P = fixed_B + a * (new_D - fixed_B) / d
                direction = (new_D - fixed_B) / d
                perpendicular = np.array([-direction[1], direction[0], 0])
                
                C1 = P + h * perpendicular
                C2 = P - h * perpendicular
                new_C = C1 if C1[1] > C2[1] else C2
            
            # Update all links
            self.link1.become(Line(fixed_A, fixed_B, color=WHITE, stroke_width=6))
            self.link2.become(Line(fixed_B, new_C, color=WHITE, stroke_width=6))
            self.link3.become(Line(new_C, new_D, color=WHITE, stroke_width=6))
            self.link4.become(Line(new_D, fixed_A, color=WHITE, stroke_width=6))
            
            # Update all joints
            self.joint2_B.move_to(fixed_B)
            self.joint2_C.move_to(new_C)
            self.joint3_C.move_to(new_C)
            self.joint3_D.move_to(new_D)
            self.joint4_D.move_to(new_D)
            self.joint4_A.move_to(fixed_A)
            
            # Update labels
            self.label_C.next_to(new_C, UP+RIGHT, buff=0.15)
            self.label_D.next_to(new_D, UP+LEFT, buff=0.15)
        
        self.link2.add_updater(update_mechanism)
        
        # Animate
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
        
        self.link2.remove_updater(update_mechanism)
    
    def create_pin_joint(self, position, color):
        """Create a pin joint with solid black fill"""
        return Circle(
            radius=0.12,
            color=color,
            stroke_width=3,
            fill_color=BLACK,
            fill_opacity=1
        ).move_to(position)
    
    def create_fixed_support(self, position):
        """Create a fixed support"""
        triangle = Polygon(
            position + np.array([-0.3, -0.2, 0]),
            position + np.array([0.3, -0.2, 0]),
            position,
            color=DARK_GRAY,
            fill_opacity=1,
            stroke_width=0
        )
        
        ground_line = Line(
            position + np.array([-0.4, -0.2, 0]),
            position + np.array([0.4, -0.2, 0]),
            color=DARK_GRAY,
            stroke_width=4
        )
        
        hash_lines = VGroup(*[
            Line(
                position + np.array([-0.4 + i*0.1, -0.2, 0]),
                position + np.array([-0.5 + i*0.1, -0.35, 0]),
                color=DARK_GRAY,
                stroke_width=2
            )
            for i in range(9)
        ])
        
        hollow_dot = Circle(
            radius=0.12,
            color=WHITE,
            stroke_width=3,
            fill_opacity=0
        ).move_to(position)
        
        return VGroup(triangle, ground_line, hash_lines, hollow_dot)

from manim import *

class GrueblerDerivation(Scene):
    def construct(self):
        # Title
        title = Text("Derivation of Gruebler's Equation", font_size=42).to_edge(UP)
        self.add(title)
        self.wait(0.5)
        
        # Step 1: Start with rigid body in plane
        step1_title = Text("Step 1: Rigid Body in Plane", font_size=32, color=YELLOW).shift(UP*2.5)
        
        # Create a rigid link (line with joints at ends)
        link = Line(LEFT*1.5, RIGHT*1.5, color=WHITE, stroke_width=8)
        joint1 = Circle(radius=0.12, color=BLUE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(LEFT*1.5)
        joint2 = Circle(radius=0.12, color=BLUE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(RIGHT*1.5)
        body = VGroup(link, joint1, joint2)
        
        # Show DOF arrows
        arrow_x = Arrow(ORIGIN, RIGHT*0.8, color=RED, buff=0)
        arrow_y = Arrow(ORIGIN, UP*0.8, color=RED, buff=0)
        arrow_rot = Arc(radius=0.6, start_angle=0, angle=PI/2, color=RED, stroke_width=3)
        arrow_rot.add_tip(tip_length=0.15)
        
        dof_group = VGroup(arrow_x, arrow_y, arrow_rot).next_to(body, DOWN, buff=0.8)
        
        dof_label = MathTex(r"DOF = 3", font_size=36, color=GREEN).next_to(dof_group, DOWN, buff=0.3)
        explanation1 = MathTex(r"(x, y, \\theta)", font_size=24).next_to(dof_label, DOWN, buff=0.2)
        
        self.play(FadeIn(step1_title), run_time=0.6)
        self.play(Create(body), run_time=0.8)
        self.play(Create(dof_group), run_time=1)
        self.play(Write(dof_label), FadeIn(explanation1), run_time=0.8)
        self.wait(1.5)
        
        # Clear for step 2
        self.play(
            FadeOut(step1_title), FadeOut(body), FadeOut(dof_group), 
            FadeOut(dof_label), FadeOut(explanation1),
            run_time=0.8
        )
        
        # Step 2: Multiple bodies
        step2_title = Text("Step 2: Multiple Bodies", font_size=32, color=YELLOW).shift(UP*2.5)
        
        # Create 3 rigid links
        link1 = Line(LEFT*1.2, RIGHT*1.2, color=WHITE, stroke_width=8).shift(LEFT*3 + UP*0.5)
        j1a = Circle(radius=0.1, color=BLUE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(link1.get_start())
        j1b = Circle(radius=0.1, color=BLUE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(link1.get_end())
        body1 = VGroup(link1, j1a, j1b)
        
        link2 = Line(LEFT*1.2, RIGHT*1.2, color=WHITE, stroke_width=8).shift(UP*0.5)
        j2a = Circle(radius=0.1, color=BLUE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(link2.get_start())
        j2b = Circle(radius=0.1, color=BLUE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(link2.get_end())
        body2 = VGroup(link2, j2a, j2b)
        
        link3 = Line(LEFT*1.2, RIGHT*1.2, color=WHITE, stroke_width=8).shift(RIGHT*3 + UP*0.5)
        j3a = Circle(radius=0.1, color=BLUE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(link3.get_start())
        j3b = Circle(radius=0.1, color=BLUE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(link3.get_end())
        body3 = VGroup(link3, j3a, j3b)
        
        label1 = MathTex("1", font_size=24).next_to(body1, DOWN, buff=0.2)
        label2 = MathTex("2", font_size=24).next_to(body2, DOWN, buff=0.2)
        label3 = MathTex("3", font_size=24).next_to(body3, DOWN, buff=0.2)
        
        bodies = VGroup(body1, body2, body3, label1, label2, label3)
        
        formula1 = Text("For n bodies:", font_size=32).shift(DOWN*1.2)
        
        formula2 = MathTex(
            r"\\text{Total DOF} = 3n",
            font_size=36,
            color=GREEN
        ).next_to(formula1, DOWN, buff=0.3)
        
        explanation2 = Text("(before any constraints)", font_size=24, color=GRAY).next_to(formula2, DOWN, buff=0.2)
        
        self.play(FadeIn(step2_title), run_time=0.6)
        self.play(FadeIn(bodies), run_time=1)
        self.wait(0.5)
        self.play(Write(formula1), run_time=0.8)
        self.play(Write(formula2), run_time=0.8)
        self.play(FadeIn(explanation2), run_time=0.6)
        self.wait(1.5)
        
        # Clear for step 3
        self.play(
            FadeOut(step2_title), FadeOut(bodies), 
            FadeOut(formula1), FadeOut(formula2), FadeOut(explanation2),
            run_time=0.8
        )
        
        # Step 3: Ground constraint
        step3_title = Text("Step 3: Fix One Body (Ground)", font_size=32, color=YELLOW).shift(UP*2.5)
        
        # Ground link
        ground_link = Line(LEFT*2.5, RIGHT*2.5, color=DARK_GRAY, stroke_width=10).shift(DOWN*1.5)
        ground_j1 = Circle(radius=0.12, color=WHITE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(ground_link.get_start())
        ground_j2 = Circle(radius=0.12, color=WHITE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(ground_link.get_end())
        ground = VGroup(ground_link, ground_j1, ground_j2)
        ground_label = Text("Ground", font_size=24, color=WHITE).next_to(ground, DOWN, buff=0.3)
        
        # Hatching below ground
        hatches = VGroup(*[
            Line(
                ground.get_bottom() + LEFT*2.5 + RIGHT*i*0.3,
                ground.get_bottom() + LEFT*2.5 + RIGHT*i*0.3 + DOWN*0.2 + LEFT*0.2,
                color=DARK_GRAY,
                stroke_width=2
            )
            for i in range(18)
        ])
        
        # Moving links
        ml1 = Line(LEFT*1, RIGHT*1, color=WHITE, stroke_width=8).shift(UP*0.5 + LEFT*2)
        mj1a = Circle(radius=0.1, color=BLUE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(ml1.get_start())
        mj1b = Circle(radius=0.1, color=BLUE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(ml1.get_end())
        moving1 = VGroup(ml1, mj1a, mj1b)
        
        ml2 = Line(LEFT*1, RIGHT*1, color=WHITE, stroke_width=8).shift(UP*0.5 + RIGHT*2)
        mj2a = Circle(radius=0.1, color=BLUE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(ml2.get_start())
        mj2b = Circle(radius=0.1, color=BLUE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(ml2.get_end())
        moving2 = VGroup(ml2, mj2a, mj2b)
        
        formula3 = MathTex(
            r"DOF = 3(n-1)",
            font_size=36,
            color=GREEN
        ).shift(UP*1.8 + RIGHT*3.5)
        
        explanation3 = Text("(One body fixed)", font_size=24, color=GRAY).next_to(formula3, DOWN, buff=0.2)
        
        self.play(FadeIn(step3_title), run_time=0.6)
        self.play(FadeIn(ground), FadeIn(ground_label), Create(hatches), run_time=1)
        self.play(FadeIn(moving1), FadeIn(moving2), run_time=0.8)
        self.wait(0.5)
        self.play(Write(formula3), FadeIn(explanation3), run_time=1)
        self.wait(1.5)
        
        # Clear for step 4
        self.play(
            FadeOut(step3_title), FadeOut(ground), FadeOut(ground_label), 
            FadeOut(hatches), FadeOut(moving1), FadeOut(moving2),
            FadeOut(formula3), FadeOut(explanation3),
            run_time=0.8
        )
        
        # Step 4: Joints remove DOF
        step4_title = Text("Step 4: Joints Remove DOF", font_size=32, color=YELLOW).shift(UP*2.8)
        
        # Two links connected by joint
        left_link = Line(LEFT*1.5, ORIGIN, color=WHITE, stroke_width=8).shift(LEFT*0.5)
        lj1 = Circle(radius=0.1, color=BLUE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(left_link.get_start())
        lj2 = Circle(radius=0.1, color=BLUE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(left_link.get_end())
        left_body = VGroup(left_link, lj1, lj2)
        
        right_link = Line(ORIGIN, RIGHT*1.5, color=WHITE, stroke_width=8).shift(RIGHT*0.5)
        rj1 = Circle(radius=0.1, color=BLUE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(right_link.get_start())
        rj2 = Circle(radius=0.1, color=BLUE, fill_color=BLACK, fill_opacity=1, stroke_width=3).move_to(right_link.get_end())
        right_body = VGroup(right_link, rj1, rj2)
        
        # Revolute joint
        joint = Circle(radius=0.15, color=RED, fill_color=BLACK, fill_opacity=1, stroke_width=4)
        joint_label = Text("Revolute Joint", font_size=24, color=RED).next_to(joint, DOWN, buff=0.5)
        
        constraint_text = VGroup(
            Text(r"Constraints:", font_size=28, color=YELLOW),
            MathTex(r"\Delta x = 0", font_size=24),
            MathTex(r"\Delta y = 0", font_size=24),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT).shift(DOWN*1.8 + LEFT*3)
        
        removed_dof = Text("Removes 2 DOF", font_size=32, color=RED).shift(DOWN*1.8 + RIGHT*2.5)
        
        self.play(FadeIn(step4_title), run_time=0.6)
        self.play(FadeIn(left_body), FadeIn(right_body), run_time=0.8)
        self.play(Create(joint), FadeIn(joint_label), run_time=0.8)
        self.wait(0.5)
        self.play(Write(constraint_text), run_time=1)
        self.play(Write(removed_dof), run_time=0.8)
        self.wait(1.5)
        
        # Clear for step 5
        self.play(
            FadeOut(step4_title), FadeOut(left_body), FadeOut(right_body),
            FadeOut(joint), FadeOut(joint_label), FadeOut(constraint_text),
            FadeOut(removed_dof),
            run_time=0.8
        )
        
        # Step 5: Final formula derivation
        step5_title = Text("Step 5: Complete Formula", font_size=32, color=YELLOW).to_edge(UP, buff=1)
        
        self.play(FadeIn(step5_title), run_time=0.6)
        
        # Build formula step by step
        line1 = MathTex(
            r"DOF = 3(n-1)",
            font_size=36
        ).shift(UP*1.5)
        
        line2 = MathTex(
            r"DOF = 3(n-1) - 2j_1",
            font_size=36
        ).shift(UP*0.5)
        
        line2_exp = MathTex(r"j_1 = \text{revolute joints}", font_size=24, color=GRAY).next_to(line2, DOWN, buff=0.2)
        
        line3 = MathTex(
            r"DOF = 3(n-1) - 2j_1 - j_2",
            font_size=36
        ).shift(DOWN*0.8)
        
        line3_exp = MathTex(r"j_2 = \text{prismatic joints}", font_size=24, color=GRAY).next_to(line3, DOWN, buff=0.2)
        
        # Final boxed formula
        final_formula = MathTex(
            r"\\boxed{DOF = 3(n-1) - 2j_1 - j_2}",
            font_size=42,
            color=GREEN
        ).shift(DOWN*2.2)
        
        final_label = Text("Gruebler's Equation", font_size=28, color=YELLOW).next_to(final_formula, DOWN, buff=0.4)
        
        self.play(Write(line1), run_time=1)
        self.wait(0.8)
        self.play(
            FadeOut(line1),
            Write(line2),
            FadeIn(line2_exp),
            run_time=1
        )
        self.wait(1)
        self.play(
            FadeOut(line2), FadeOut(line2_exp),
            Write(line3),
            FadeIn(line3_exp),
            run_time=1
        )
        self.wait(1)
        self.play(
            FadeOut(line3), FadeOut(line3_exp),
            Write(final_formula),
            run_time=1.2
        )
        self.play(FadeIn(final_label), run_time=0.8)
        
        # Emphasize final formula
        self.play(final_formula.animate.scale(1.15), run_time=0.5)
        self.play(final_formula.animate.scale(1/1.15), run_time=0.5)
        
        self.wait(2)
        
        # Show what each term means
        self.play(
            FadeOut(step5_title),
            final_formula.animate.shift(UP*2),
            final_label.animate.shift(UP*2),
            run_time=0.8
        )
        
        terms_title = Text("Where:", font_size=32, color=YELLOW).shift(UP*0.5)
        
        term1 = MathTex(r"n = \text{number of links}", font_size=28).shift(UP*0)
        term2 = MathTex(r"j_1 = \text{1-DOF joints}", font_size=28).shift(DOWN*0.5)
        term3 = MathTex(r"j_2 = \text{2-DOF joints}", font_size=28).shift(DOWN*1)
        term4 = MathTex(r"DOF = \text{mobility}", font_size=28, color=GREEN).shift(DOWN*1.5)
        
        terms = VGroup(term1, term2, term3, term4)
        
        self.play(Write(terms_title), run_time=0.6)
        for term in terms:
            self.play(FadeIn(term), run_time=0.7)
            self.wait(0.3)
        
        self.wait(3)