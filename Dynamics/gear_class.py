from manim import *
import numpy as np

class SimpleGear:
    """Simple gear class with proper interior fill"""
    def __init__(self, num_teeth, module=0.2, pressure_angle=20, color=BLUE, **kwargs):
        self.num_teeth = num_teeth
        self.module = module
        self.pressure_angle = pressure_angle * DEGREES
        
        # Calculate dimensions
        self.pitch_radius = module * num_teeth / 2
        self.base_radius = self.pitch_radius * np.cos(self.pressure_angle)
        self.addendum = module * 1.0
        self.dedendum = module * 1.25
        self.outer_radius = self.pitch_radius + self.addendum
        self.root_radius = max(self.pitch_radius - self.dedendum, self.base_radius * 0.85)
        self.tooth_angle = 2 * PI / num_teeth
        
        # Create the gear shape
        self.mobject = self.create_gear_shape(color=color, **kwargs)
        self.center = ORIGIN.copy()
    
    def involute_point(self, t):
        """Calculate point on involute curve"""
        r = self.base_radius
        x = r * (np.cos(t) + t * np.sin(t))
        y = r * (np.sin(t) - t * np.cos(t))
        return np.array([x, y, 0])
    
    def create_tooth_profile(self):
        """Create one tooth profile using proper involute polar coordinates."""
        rb = self.base_radius
        num_pts = 20
        num_arc = 5
        
        # Involute function: inv(α) = tan(α) - α
        def inv_func(alpha):
            return np.tan(alpha) - alpha
        
        # Pressure angle and involute function at pitch circle
        alpha_p = self.pressure_angle
        inv_p = inv_func(alpha_p)
        
        # Half angular tooth thickness at pitch circle
        half_thick_pitch = PI / (2 * self.num_teeth)
        
        # Half angular tooth thickness at any radius R
        def half_tooth_at(R):
            if R <= rb:
                return half_thick_pitch + inv_p
            alpha_R = np.arccos(rb / R)
            return half_thick_pitch + inv_p - inv_func(alpha_R)
        
        # Involute goes from base circle to outer circle
        involute_radii = np.linspace(rb, self.outer_radius, num_pts)
        
        # Key angles
        theta_base = half_tooth_at(rb)
        theta_tip = half_tooth_at(self.outer_radius)
        
        all_points = []
        
        # --- 1. Right flank: root → base → outer ---
        if self.root_radius < rb:
            all_points.append(np.array([
                self.root_radius * np.cos(-theta_base),
                self.root_radius * np.sin(-theta_base), 0]))
        
        for R in involute_radii:
            theta = -half_tooth_at(R)
            all_points.append(np.array([R * np.cos(theta), R * np.sin(theta), 0]))
        
        # --- 2. Top arc ---
        for i in range(num_arc):
            t = i / (num_arc - 1)
            angle = -theta_tip + t * 2 * theta_tip
            all_points.append(np.array([
                self.outer_radius * np.cos(angle),
                self.outer_radius * np.sin(angle), 0]))
        
        # --- 3. Left flank: outer → base → root ---
        for R in reversed(involute_radii):
            theta = half_tooth_at(R)
            all_points.append(np.array([R * np.cos(theta), R * np.sin(theta), 0]))
        
        if self.root_radius < rb:
            all_points.append(np.array([
                self.root_radius * np.cos(theta_base),
                self.root_radius * np.sin(theta_base), 0]))
        
        # --- 4. Gap arc at root radius ---
        gap_start = theta_base if self.root_radius < rb else half_tooth_at(max(self.root_radius, rb))
        gap_end = self.tooth_angle - gap_start
        
        for i in range(1, num_arc):
            t = i / (num_arc - 1)
            angle = gap_start + t * (gap_end - gap_start)
            all_points.append(np.array([
                self.root_radius * np.cos(angle),
                self.root_radius * np.sin(angle), 0]))
        
        return all_points
    
    def create_gear_shape(self, color=BLUE, **kwargs):
        """Create complete gear as a single closed path"""
        tooth_points = self.create_tooth_profile()
        
        all_points = []
        for i in range(self.num_teeth):
            angle = i * self.tooth_angle
            for point in tooth_points:
                x = point[0] * np.cos(angle) - point[1] * np.sin(angle)
                y = point[0] * np.sin(angle) + point[1] * np.cos(angle)
                all_points.append(np.array([x, y, 0]))
        
        gear = Polygon(*all_points, color=color)
        gear.set_stroke(WHITE, width=2)
        gear.set_fill(color, opacity=0.8)
        
        if 'fill_opacity' in kwargs:
            gear.set_fill(opacity=kwargs['fill_opacity'])
        if 'stroke_width' in kwargs:
            gear.set_stroke(width=kwargs['stroke_width'])
        
        return gear
    
    def get_mobject(self):
        return self.mobject
    
    def get_center(self):
        return self.mobject.get_center()
    
    def shift(self, vector):
        self.mobject.shift(vector)
        self.center += vector
        return self
    
    def rotate(self, angle, about_point=None):
        if about_point is None:
            about_point = self.get_center()
        self.mobject.rotate(angle, about_point=about_point)
        return self


class QuickGearTest(MovingCameraScene):
    """Quick test of properly filled and meshed gears with zoom"""
    def construct(self):
        # Create two meshing gears
        gear1 = SimpleGear(num_teeth=20, module=0.3, color=BLUE, fill_opacity=0.9)
        gear2 = SimpleGear(num_teeth=30, module=0.3, color=RED, fill_opacity=0.9)
        
        # Position for meshing
        separation = gear1.pitch_radius + gear2.pitch_radius
        gear1.shift(LEFT * separation / 2)
        gear2.shift(RIGHT * separation / 2)
        
        # Proper meshing alignment
        gear2.rotate(PI / gear2.num_teeth)
        
        # Get mobjects
        gear1_mob = gear1.get_mobject()
        gear2_mob = gear2.get_mobject()
        
        # Add centers
        center1 = Dot(gear1.get_center(), color=YELLOW, radius=0.08)
        center2 = Dot(gear2.get_center(), color=YELLOW, radius=0.08)
        
        # Add title
        title = Text("Gear Meshing Close-Up", font_size=36)
        title.to_edge(UP)
        
        self.play(Write(title))
        self.play(
            FadeIn(gear1_mob, scale=0.5),
            FadeIn(gear2_mob, scale=0.5),
            Create(center1),
            Create(center2),
            run_time=1.5
        )
        
        # Rotate with proper ratio
        ratio = 20 / 30
        angle1 = 4 * PI
        angle2 = -angle1 * ratio
        
        self.play(
            Rotate(gear1_mob, angle1, about_point=gear1.get_center(), rate_func=linear),
            Rotate(gear2_mob, angle2, about_point=gear2.get_center(), rate_func=linear),
            run_time=4
        )
        
        self.wait()

        # Zoom to the teeth contact point between the two gears
        contact_point = gear1.get_center() + RIGHT * gear1.pitch_radius
        contact_dot = Dot(contact_point, color=YELLOW, radius=0.06)
        contact_label = Text("Contact Point", font_size=20, color=YELLOW)
        contact_label.next_to(contact_dot, DOWN, buff=0.2)
        
        self.play(Create(contact_dot), Write(contact_label), run_time=0.5)
        self.wait(0.5)

        # Save current camera frame, move & scale to focus on contact, then restore
        self.camera.frame.save_state()
        
        # Calculate scale factor to zoom in
        target_width = gear1.pitch_radius * 1.5  # Show area around contact point
        
        self.play(
            self.camera.frame.animate.move_to(contact_point).set(width=target_width),
            FadeOut(title),
            FadeOut(contact_label),
            run_time=2
        )
        
        self.wait(0.5)

        # Small local rotation to emphasize tooth contact
        small_angle1 = PI / gear1.num_teeth
        small_angle2 = -small_angle1 * ratio
        
        self.play(
            Rotate(gear1_mob, small_angle1, about_point=gear1.get_center(), rate_func=there_and_back),
            Rotate(gear2_mob, small_angle2, about_point=gear2.get_center(), rate_func=there_and_back),
            run_time=2
        )

        self.wait(1)
        
        # Restore camera and fade out contact dot
        self.play(
            Restore(self.camera.frame),
            FadeOut(contact_dot),
            FadeIn(title),
            run_time=2
        )
        
        self.wait()
        
        # Final rotation while zoomed out
        self.play(
            Rotate(gear1_mob, 2*PI, about_point=gear1.get_center(), rate_func=linear),
            Rotate(gear2_mob, -2*PI * ratio, about_point=gear2.get_center(), rate_func=linear),
            run_time=3
        )
        
        self.wait()


class DetailedGearMeshing(MovingCameraScene):
    """Show detailed meshing with multiple zoom levels"""
    def construct(self):
        # Create gears
        gear1 = SimpleGear(num_teeth=24, module=0.35, color=BLUE, fill_opacity=0.9)
        gear2 = SimpleGear(num_teeth=24, module=0.35, color=RED, fill_opacity=0.9)
        
        # Position
        separation = gear1.pitch_radius + gear2.pitch_radius
        gear1.shift(LEFT * separation / 2)
        gear2.shift(RIGHT * separation / 2)
        gear2.rotate(PI / gear2.num_teeth)
        
        # Get mobjects
        gear1_mob = gear1.get_mobject()
        gear2_mob = gear2.get_mobject()
        
        # Centers
        center1 = Dot(gear1.get_center(), color=YELLOW, radius=0.08)
        center2 = Dot(gear2.get_center(), color=YELLOW, radius=0.08)
        
        # Pitch circles
        pitch1 = Circle(radius=gear1.pitch_radius, color=GREEN, stroke_width=2, stroke_opacity=0.6)
        pitch1.move_to(gear1.get_center())
        pitch2 = Circle(radius=gear2.pitch_radius, color=GREEN, stroke_width=2, stroke_opacity=0.6)
        pitch2.move_to(gear2.get_center())
        
        # Title
        title = Text("Detailed Gear Meshing Analysis", font_size=40)
        title.to_edge(UP)
        
        # Show everything
        self.play(Write(title))
        self.play(
            FadeIn(gear1_mob, scale=0.5),
            FadeIn(gear2_mob, scale=0.5),
            Create(center1),
            Create(center2),
            Create(pitch1),
            Create(pitch2),
            run_time=2
        )
        self.wait()
        
        # Rotate a bit
        self.play(
            Rotate(gear1_mob, PI, about_point=gear1.get_center(), rate_func=linear),
            Rotate(gear2_mob, -PI, about_point=gear2.get_center(), rate_func=linear),
            run_time=2
        )
        
        # Contact point
        contact_point = gear1.get_center() + RIGHT * gear1.pitch_radius
        contact_dot = Dot(contact_point, color=YELLOW, radius=0.08)
        contact_label = Text("Pitch Point", font_size=24, color=YELLOW)
        contact_label.next_to(contact_dot, UP, buff=0.3)
        
        self.play(Create(contact_dot), Write(contact_label))
        self.wait()
        
        # Zoom in stages
        self.camera.frame.save_state()
        
        # First zoom - moderate
        self.play(
            self.camera.frame.animate.move_to(contact_point).set(width=6),
            FadeOut(title),
            run_time=2
        )
        self.wait()
        
        # Show rotation at this zoom
        self.play(
            Rotate(gear1_mob, PI/2, about_point=gear1.get_center(), rate_func=linear),
            Rotate(gear2_mob, -PI/2, about_point=gear2.get_center(), rate_func=linear),
            run_time=2
        )
        
        # Second zoom - close up
        self.play(
            self.camera.frame.animate.set(width=3),
            FadeOut(contact_label),
            FadeOut(pitch1),
            FadeOut(pitch2),
            run_time=2
        )
        self.wait()
        
        # Very slow rotation to show detail
        self.play(
            Rotate(gear1_mob, PI/4, about_point=gear1.get_center(), rate_func=smooth),
            Rotate(gear2_mob, -PI/4, about_point=gear2.get_center(), rate_func=smooth),
            run_time=3
        )
        
        self.wait()
        
        # Zoom back out
        self.play(
            Restore(self.camera.frame),
            FadeIn(title),
            FadeIn(pitch1),
            FadeIn(pitch2),
            FadeIn(contact_label),
            run_time=2.5
        )
        
        self.wait()
        
        # Final full rotation
        self.play(
            Rotate(gear1_mob, 2*PI, about_point=gear1.get_center(), rate_func=linear),
            Rotate(gear2_mob, -2*PI, about_point=gear2.get_center(), rate_func=linear),
            run_time=4
        )
        
        self.wait(2)