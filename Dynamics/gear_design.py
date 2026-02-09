from manim import *
import numpy as np

class InvoluteGearMechanism(Scene):
    """
    Mathematically accurate involute gear mechanism
    - True involute curves using parametric equations
    - Zoomed to contact area for detail
    - Perfect meshing visualization
    """
    
    def construct(self):
        # ==================== CONFIGURATION ====================
        self.gear1_center = np.array([-2.5, 0, 0])
        self.gear1_teeth = 18
        self.module = 0.35  # Larger for better visibility when zoomed
        
        self.gear2_teeth = 27
        
        # Calculate parameters
        self.gear1_pitch_radius = (self.gear1_teeth * self.module) / 2
        self.gear2_pitch_radius = (self.gear2_teeth * self.module) / 2
        
        # Position for perfect meshing
        center_distance = self.gear1_pitch_radius + self.gear2_pitch_radius
        self.gear2_center = self.gear1_center + np.array([center_distance, 0, 0])
        
        # Standard involute parameters
        self.pressure_angle = 20 * DEGREES
        self.addendum = 1.0 * self.module
        self.dedendum = 1.25 * self.module
        
        # ==================== SCENE FLOW ====================
        self.show_title()
        self.show_involute_construction()
        self.show_gear_measurements()
        self.show_meshing_zoomed()
        self.show_conclusion()
        
    # ==================== INVOLUTE CONSTRUCTION ====================
    
    def show_involute_construction(self):
        """Demonstrate involute curve generation"""
        title = Text(
            "Part 1: Involute Tooth Profile Construction",
            font_size=28,
            color=BLUE_C
        ).to_edge(UP, buff=0.3)
        
        self.play(Write(title), run_time=0.8)
        self.wait(0.3)
        
        construction_center = np.array([-3.5, -0.3, 0])
        base_radius = 1.3
        
        base_circle = Circle(
            radius=base_radius,
            color=BLUE_D,
            stroke_width=2.5
        ).move_to(construction_center)
        
        base_label = Text("Base Circle", font_size=18, color=BLUE_D).next_to(
            base_circle, DOWN, buff=0.3
        )
        
        self.play(Create(base_circle), Write(base_label), run_time=0.8)
        self.wait(0.3)
        
        involute_points = []
        involute_curve = VMobject(color=RED_C, stroke_width=3.5)
        
        initial_point = construction_center + np.array([0, base_radius, 0])
        
        contact_indicator = Dot(initial_point, color=YELLOW, radius=0.06)
        trace_dot = Dot(initial_point, color=RED, radius=0.08)
        string_line = Line(initial_point, initial_point, color=YELLOW, stroke_width=2.5)
        
        explanation = Text(
            "String unwrapping creates true involute curve: x = r(cos(t) + t·sin(t))",
            font_size=16,
            color=GRAY_A
        ).to_edge(DOWN, buff=0.5)
        
        self.add(contact_indicator, string_line, trace_dot)
        self.play(Write(explanation), run_time=0.6)
        self.wait(0.2)
        
        angle_tracker = ValueTracker(0)
        
        def update_involute(mob):
            theta = angle_tracker.get_value()
            if theta < 0.01:
                return
            
            contact_angle = PI/2 - theta
            contact_point = construction_center + base_radius * np.array([
                np.cos(contact_angle), np.sin(contact_angle), 0
            ])
            
            string_length = base_radius * theta
            tangent_angle = contact_angle - PI/2
            
            end_point = contact_point + string_length * np.array([
                np.cos(tangent_angle), np.sin(tangent_angle), 0
            ])
            
            contact_indicator.move_to(contact_point)
            trace_dot.move_to(end_point)
            string_line.put_start_and_end_on(contact_point, end_point)
            
            involute_points.append(end_point.copy())
            if len(involute_points) > 1:
                involute_curve.set_points_as_corners(involute_points)
        
        involute_curve.add_updater(update_involute)
        self.add(involute_curve)
        
        self.play(
            angle_tracker.animate.set_value(PI * 0.85),
            run_time=4,
            rate_func=smooth
        )
        
        involute_curve.remove_updater(update_involute)
        self.wait(0.3)
        
        self.play(involute_curve.animate.set_stroke(width=5, color=RED_B), run_time=0.3)
        
        involute_label = Text("Involute Profile", font_size=18, color=RED_B).next_to(
            involute_curve, RIGHT, buff=0.4
        )
        self.play(Write(involute_label), run_time=0.5)
        self.wait(1)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)
    
    # ==================== GEAR MEASUREMENTS ====================
    
    def show_gear_measurements(self):
        """Display gear measurements"""
        title = Text(
            "Part 2: Gear Measurements & Circles",
            font_size=28,
            color=TEAL_C
        ).to_edge(UP, buff=0.3)
        
        self.play(Write(title), run_time=0.7)
        self.wait(0.3)
        
        measure_center = np.array([0, -0.3, 0])
        measure_teeth = 20
        
        pitch_radius = (measure_teeth * self.module) / 2
        base_radius = pitch_radius * np.cos(self.pressure_angle)
        outer_radius = pitch_radius + self.addendum
        root_radius = pitch_radius - self.dedendum
        
        gear = self.create_accurate_involute_gear(
            center=measure_center,
            num_teeth=measure_teeth,
            pitch_radius=pitch_radius,
            color=BLUE_D
        )
        
        self.play(Create(gear), run_time=1)
        self.wait(0.3)
        
        circles_data = [
            (outer_radius, "Addendum Circle", RED_C),
            (pitch_radius, "Pitch Circle", GREEN_C),
            (base_radius, "Base Circle", BLUE_C),
            (root_radius, "Root Circle", ORANGE),
        ]
        
        label_x = measure_center[0] + outer_radius + 1.5
        
        for i, (radius, name, color) in enumerate(circles_data):
            circle = Circle(
                radius=radius,
                color=color,
                stroke_width=2.2,
                stroke_opacity=0.7
            ).move_to(measure_center)
            
            label_y = measure_center[1] + 1.8 - i * 0.5
            label = Text(name, font_size=14, color=color).move_to(
                np.array([label_x, label_y, 0])
            )
            
            line_start = measure_center + np.array([radius, 0, 0])
            line_end = np.array([label_x - 0.3, label_y, 0])
            connector = DashedLine(
                line_start, line_end,
                color=color, stroke_width=1, stroke_opacity=0.4, dash_length=0.06
            )
            
            self.play(Create(circle), Create(connector), Write(label), run_time=0.5)
            self.wait(0.15)
        
        center_dot = Dot(measure_center, color=WHITE, radius=0.06)
        self.play(Create(center_dot))
        
        # Dimensions
        add_start = measure_center + np.array([0, pitch_radius, 0])
        add_end = measure_center + np.array([0, outer_radius, 0])
        addendum_line = Line(add_start, add_end, color=YELLOW, stroke_width=3)
        addendum_brace = Brace(addendum_line, direction=LEFT, buff=0.1)
        addendum_label = Text("a", font_size=14, color=YELLOW).next_to(addendum_brace, LEFT, buff=0.1)
        
        ded_start = measure_center + np.array([0, root_radius, 0])
        ded_end = measure_center + np.array([0, pitch_radius, 0])
        dedendum_line = Line(ded_start, ded_end, color=PURPLE, stroke_width=3)
        dedendum_brace = Brace(dedendum_line, direction=RIGHT, buff=0.1)
        dedendum_label = Text("d", font_size=14, color=PURPLE).next_to(dedendum_brace, RIGHT, buff=0.1)
        
        self.play(
            Create(addendum_line), Create(addendum_brace), Write(addendum_label),
            run_time=0.6
        )
        self.play(
            Create(dedendum_line), Create(dedendum_brace), Write(dedendum_label),
            run_time=0.6
        )
        
        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)
    
    # ==================== ZOOMED MESHING ====================
    
    def show_meshing_zoomed(self):
        """Show zoomed view of contact area with accurate meshing"""
        title = Text(
            "Part 3: Tooth Contact Area (Zoomed)",
            font_size=28,
            color=GOLD_C
        ).to_edge(UP, buff=0.3)
        
        self.play(Write(title), run_time=0.7)
        self.wait(0.3)
        
        # Create partial gears (only show 3-4 teeth around contact area)
        # This is more efficient and focuses on the contact region
        
        # Gear 1 - show teeth around right side (contact area)
        gear1_partial = self.create_partial_gear(
            center=self.gear1_center,
            num_teeth=self.gear1_teeth,
            pitch_radius=self.gear1_pitch_radius,
            color=BLUE_D,
            show_teeth_range=(-2, 3)  # Show 5 teeth around 0 degrees
        )
        
        # Gear 2 - show teeth around left side (contact area)
        offset_angle = PI / self.gear2_teeth
        gear2_partial = self.create_partial_gear(
            center=self.gear2_center,
            num_teeth=self.gear2_teeth,
            pitch_radius=self.gear2_pitch_radius,
            color=GREEN_D,
            rotation_offset=offset_angle,
            show_teeth_range=(-2, 3)  # Show 5 teeth around 180 degrees (PI)
        )
        
        # Pitch circles (partial)
        pitch1 = Arc(
            radius=self.gear1_pitch_radius,
            start_angle=-30*DEGREES,
            angle=60*DEGREES,
            color=GREEN_C,
            stroke_width=2,
            stroke_opacity=0.6
        ).move_arc_center_to(self.gear1_center)
        
        pitch2 = Arc(
            radius=self.gear2_pitch_radius,
            start_angle=150*DEGREES,
            angle=60*DEGREES,
            color=GREEN_C,
            stroke_width=2,
            stroke_opacity=0.6
        ).move_arc_center_to(self.gear2_center)
        
        # Contact point marker
        contact_x = self.gear1_center[0] + self.gear1_pitch_radius
        contact_point = Dot(
            np.array([contact_x, self.gear1_center[1], 0]),
            color=RED,
            radius=0.12
        )
        
        contact_label = Text("Contact Point", font_size=14, color=RED).next_to(
            contact_point, UP, buff=0.3
        )
        
        # Pressure angle line
        pressure_line = DashedLine(
            self.gear1_center + np.array([self.gear1_pitch_radius - 0.8, 0, 0]),
            self.gear1_center + np.array([self.gear1_pitch_radius - 0.8, 0, 0]) + 
            1.6 * np.array([np.cos(self.pressure_angle), np.sin(self.pressure_angle), 0]),
            color=YELLOW,
            stroke_width=2,
            dash_length=0.08
        )
        
        pressure_label = MathTex("20°", font_size=16, color=YELLOW).next_to(
            pressure_line, RIGHT, buff=0.2
        )
        
        # Show setup
        self.play(
            Create(gear1_partial),
            Create(gear2_partial),
            Create(pitch1),
            Create(pitch2),
            run_time=1.2
        )
        
        self.play(
            Create(contact_point),
            Write(contact_label),
            run_time=0.6
        )
        
        self.play(
            Create(pressure_line),
            Write(pressure_label),
            run_time=0.6
        )
        
        self.wait(0.5)
        
        # Gear info
        info = VGroup(
            Text(f"Gear 1: {self.gear1_teeth} teeth", font_size=12, color=BLUE_B),
            Text(f"Gear 2: {self.gear2_teeth} teeth", font_size=12, color=GREEN_B),
            Text(f"Module: {self.module}", font_size=12, color=GRAY_A),
            Text(f"Pressure angle: 20°", font_size=12, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UL, buff=0.8)
        
        self.play(Write(info), run_time=0.8)
        
        # Contact pressure bar
        pressure_label_text = Text("Contact\nPressure", font_size=12, color=RED_C).to_corner(
            UR, buff=0.6
        )
        
        pressure_container = Rectangle(
            width=0.35, height=2.0,
            color=GRAY_C, stroke_width=2, fill_opacity=0
        ).next_to(pressure_label_text, DOWN, buff=0.2)
        
        pressure_bar = Rectangle(
            width=0.3, height=0.01,
            color=RED_C, fill_opacity=0.8, stroke_width=0
        ).align_to(pressure_container, DOWN).shift(UP * 0.025)
        
        self.play(Write(pressure_label_text), Create(pressure_container))
        self.add(pressure_bar)
        
        # Animation
        angle_tracker = ValueTracker(0)
        
        def update_contact(mob):
            angle = angle_tracker.get_value()
            
            # Contact point moves along pressure line
            contact_variation = 0.15 * np.sin(angle * self.gear1_teeth)
            contact_y = self.gear1_center[1] + contact_variation
            
            contact_point.move_to(np.array([contact_x, contact_y, 0]))
            
            # Pressure variation
            pressure = abs(np.sin(angle * self.gear1_teeth)) * 0.85 + 0.15
            bar_height = pressure * 1.8
            
            new_bar = Rectangle(
                width=0.3, height=bar_height,
                color=RED_C, fill_opacity=0.8, stroke_width=0
            ).align_to(pressure_container, DOWN).shift(UP * 0.025)
            
            pressure_bar.become(new_bar)
        
        contact_point.add_updater(update_contact)
        
        # Rotation
        ratio = self.gear2_teeth / self.gear1_teeth
        
        self.play(
            Rotate(gear1_partial, angle=2*PI, about_point=self.gear1_center),
            Rotate(gear2_partial, angle=-2*PI/ratio, about_point=self.gear2_center),
            Rotate(pitch1, angle=2*PI, about_point=self.gear1_center),
            Rotate(pitch2, angle=-2*PI/ratio, about_point=self.gear2_center),
            angle_tracker.animate.set_value(2*PI),
            run_time=10,
            rate_func=linear
        )
        
        contact_point.remove_updater(update_contact)
        self.wait(1)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.7)
    
    # ==================== ACCURATE INVOLUTE GEAR ====================
    
    def involute(self, base_radius, t):
        """
        True involute curve using parametric equations
        x = r(cos(t) + t*sin(t))
        y = r(sin(t) - t*cos(t))
        """
        x = base_radius * (np.cos(t) + t * np.sin(t))
        y = base_radius * (np.sin(t) - t * np.cos(t))
        return np.array([x, y, 0])
    
    def create_accurate_involute_gear(self, center, num_teeth, pitch_radius, color, rotation_offset=0):
        """Create gear with mathematically accurate involute profiles"""
        
        base_radius = pitch_radius * np.cos(self.pressure_angle)
        outer_radius = pitch_radius + self.addendum
        root_radius = pitch_radius - self.dedendum
        
        tooth_angle = 2 * PI / num_teeth
        
        # Calculate involute parameter range
        # At pitch circle: t_pitch
        t_pitch = np.sqrt((pitch_radius / base_radius) ** 2 - 1)
        # At outer circle: t_outer
        t_outer = np.sqrt((outer_radius / base_radius) ** 2 - 1)
        
        # Tooth thickness at pitch circle (half of circular pitch)
        tooth_thickness_pitch = PI * self.module / 2
        tooth_half_angle_pitch = tooth_thickness_pitch / (2 * pitch_radius)
        
        all_points = []
        
        for i in range(num_teeth):
            base_angle = i * tooth_angle + rotation_offset
            
            # Generate right involute flank
            num_involute_points = 15
            t_values = np.linspace(0, t_outer, num_involute_points)
            
            for t in t_values:
                inv_point = self.involute(base_radius, t)
                
                # Rotate to position
                angle = base_angle + tooth_half_angle_pitch + t
                cos_a, sin_a = np.cos(angle), np.sin(angle)
                rotated = np.array([
                    inv_point[0] * cos_a - inv_point[1] * sin_a,
                    inv_point[0] * sin_a + inv_point[1] * cos_a,
                    0
                ])
                all_points.append(center + rotated)
            
            # Tip arc
            tip_angles = np.linspace(
                base_angle + tooth_half_angle_pitch * 0.7,
                base_angle - tooth_half_angle_pitch * 0.7,
                5
            )
            for tip_angle in tip_angles:
                all_points.append(center + outer_radius * np.array([
                    np.cos(tip_angle), np.sin(tip_angle), 0
                ]))
            
            # Left involute flank (mirrored)
            for t in reversed(t_values):
                inv_point = self.involute(base_radius, t)
                
                angle = base_angle - tooth_half_angle_pitch - t
                cos_a, sin_a = np.cos(angle), np.sin(angle)
                rotated = np.array([
                    inv_point[0] * cos_a - inv_point[1] * sin_a,
                    inv_point[0] * sin_a + inv_point[1] * cos_a,
                    0
                ])
                all_points.append(center + rotated)
            
            # Root fillet
            next_angle = (i + 1) * tooth_angle + rotation_offset
            root_angles = np.linspace(
                base_angle - tooth_half_angle_pitch,
                next_angle + tooth_half_angle_pitch,
                10
            )
            for root_angle in root_angles:
                all_points.append(center + root_radius * np.array([
                    np.cos(root_angle), np.sin(root_angle), 0
                ]))
        
        gear = Polygon(
            *all_points,
            color=color,
            fill_opacity=0.85,
            stroke_color=color,
            stroke_width=2.5
        )
        
        return gear
    
    def create_partial_gear(self, center, num_teeth, pitch_radius, color, 
                           show_teeth_range, rotation_offset=0):
        """Create partial gear showing only specific teeth"""
        
        base_radius = pitch_radius * np.cos(self.pressure_angle)
        outer_radius = pitch_radius + self.addendum
        root_radius = pitch_radius - self.dedendum
        
        tooth_angle = 2 * PI / num_teeth
        t_outer = np.sqrt((outer_radius / base_radius) ** 2 - 1)
        
        tooth_thickness_pitch = PI * self.module / 2
        tooth_half_angle_pitch = tooth_thickness_pitch / (2 * pitch_radius)
        
        all_points = []
        
        start_tooth, end_tooth = show_teeth_range
        
        for i in range(start_tooth, end_tooth + 1):
            base_angle = i * tooth_angle + rotation_offset
            
            # Right involute
            num_involute_points = 15
            t_values = np.linspace(0, t_outer, num_involute_points)
            
            for t in t_values:
                inv_point = self.involute(base_radius, t)
                angle = base_angle + tooth_half_angle_pitch + t
                cos_a, sin_a = np.cos(angle), np.sin(angle)
                rotated = np.array([
                    inv_point[0] * cos_a - inv_point[1] * sin_a,
                    inv_point[0] * sin_a + inv_point[1] * cos_a,
                    0
                ])
                all_points.append(center + rotated)
            
            # Tip
            tip_angles = np.linspace(
                base_angle + tooth_half_angle_pitch * 0.7,
                base_angle - tooth_half_angle_pitch * 0.7,
                5
            )
            for tip_angle in tip_angles:
                all_points.append(center + outer_radius * np.array([
                    np.cos(tip_angle), np.sin(tip_angle), 0
                ]))
            
            # Left involute
            for t in reversed(t_values):
                inv_point = self.involute(base_radius, t)
                angle = base_angle - tooth_half_angle_pitch - t
                cos_a, sin_a = np.cos(angle), np.sin(angle)
                rotated = np.array([
                    inv_point[0] * cos_a - inv_point[1] * sin_a,
                    inv_point[0] * sin_a + inv_point[1] * cos_a,
                    0
                ])
                all_points.append(center + rotated)
            
            # Root
            if i < end_tooth:
                next_angle = (i + 1) * tooth_angle + rotation_offset
                root_angles = np.linspace(
                    base_angle - tooth_half_angle_pitch,
                    next_angle + tooth_half_angle_pitch,
                    10
                )
                for root_angle in root_angles:
                    all_points.append(center + root_radius * np.array([
                        np.cos(root_angle), np.sin(root_angle), 0
                    ]))
        
        gear = Polygon(
            *all_points,
            color=color,
            fill_opacity=0.85,
            stroke_color=color,
            stroke_width=2.5
        )
        
        return gear
    
    # ==================== TITLE & CONCLUSION ====================
    
    def show_title(self):
        """Main title"""
        title = Text(
            "Involute Gear Mechanism",
            font_size=42,
            color=TEAL_C,
            weight=BOLD
        ).to_edge(UP, buff=0.3)
        
        subtitle = Text(
            "Mathematical Involute • Zoomed Contact Area • Accurate Meshing",
            font_size=20,
            color=GRAY_A
        ).next_to(title, DOWN, buff=0.2)
        
        self.play(Write(title), Write(subtitle), run_time=1)
        self.wait(0.6)
        self.play(FadeOut(title), FadeOut(subtitle), run_time=0.5)
    
    def show_conclusion(self):
        """Summary"""
        summary = VGroup(
            Text("✓ True Involute: x = r(cos(t) + t·sin(t)), y = r(sin(t) - t·cos(t))", font_size=14, color=BLUE_B),
            Text("✓ Contact Zone: Teeth mesh along 20° pressure angle line", font_size=14, color=GREEN_B),
            Text("✓ Smooth Transmission: Constant velocity ratio throughout mesh", font_size=14, color=RED_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_edge(DOWN, buff=0.6)
        
        self.play(Write(summary), run_time=1.5)
        self.wait(2.5)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


class InvoluteCircle(Scene):
    """Show involute curve on a circle"""
    
    def construct(self):
        center = np.array([0, 0, 0])
        base_radius = 1.5
        
        base_circle = Circle(
            radius=base_radius,
            color=BLUE_D,
            stroke_width=2.5
        ).move_to(center)
        
        self.play(Create(base_circle), run_time=0.8)
        
        involute_points = []
        involute_curve = VMobject(color=RED_C, stroke_width=3.5)
        
        initial_point = center + np.array([0, base_radius, 0])
        
        contact_indicator = Dot(initial_point, color=YELLOW, radius=0.06)
        trace_dot = Dot(initial_point, color=RED, radius=0.08)
        string_line = Line(initial_point, initial_point, color=YELLOW, stroke_width=2.5)
        
        explanation = Text(
            "String unwrapping creates true involute curve: x = r(cos(t) + t·sin(t))",
            font_size=16,
            color=GRAY_A
        ).to_edge(DOWN, buff=0.5)
        
        self.add(contact_indicator, string_line, trace_dot)
        self.play(Write(explanation), run_time=0.6)
        
        angle_tracker = ValueTracker(0)
        
        def update_involute(mob):
            theta = angle_tracker.get_value()
            if theta < 0.01:
                return
            
            contact_angle = PI/2 - theta
            contact_point = center + base_radius * np.array([
                np.cos(contact_angle), np.sin(contact_angle), 0
            ])
            
            string_length = base_radius * theta
            tangent_angle = contact_angle - PI/2
            
            end_point = contact_point + string_length * np.array([
                np.cos(tangent_angle), np.sin(tangent_angle), 0
            ])
            
            contact_indicator.move_to(contact_point)
            trace_dot.move_to(end_point)
            string_line.put_start_and_end_on(contact_point, end_point)
            
            involute_points.append(end_point.copy())
            if len(involute_points) > 1:
                involute_curve.set_points_as_corners(involute_points)
        
        involute_curve.add_updater(update_involute)
        self.add(involute_curve)
        
        # --- Ribbon-style rope: wrapped arc + growing rope along involute ---
        # Rope body (thick ribbon following involute points)
        rope = VMobject()
        rope.set_stroke(color="#8B4513", width=12)
        # initialize with a very short segment to avoid empty-point issues
        rope.set_points_as_corners([initial_point, initial_point + np.array([1e-6, 0, 0])])

        def update_rope(r):
            if len(involute_points) > 1:
                try:
                    r.set_points_as_corners(involute_points)
                except Exception:
                    r.set_points_as_corners(r.points)
            return r

        rope.add_updater(update_rope)

        # Thin highlight along the rope center for texture
        rope_center = VMobject()
        rope_center.set_stroke(color=YELLOW, width=2)
        rope_center.set_points_as_corners([initial_point, initial_point + np.array([1e-6, 0, 0])])
        def update_rope_center(rc):
            if len(involute_points) > 1:
                try:
                    rc.set_points_as_corners(involute_points)
                except Exception:
                    rc.set_points_as_corners(rc.points)
            return rc
        rope_center.add_updater(update_rope_center)

        # Wrapped portion on base circle (arc) representing rope still wrapped
        wrapped_arc = always_redraw(lambda: Arc(
            start_angle=PI/2 - angle_tracker.get_value(),
            angle=angle_tracker.get_value() if angle_tracker.get_value() != 0 else 0.0001,
            radius=base_radius,
            color="#8B4513",
            stroke_width=12
        ))

        # Rope end marker
        rope_tip = always_redraw(lambda: Dot(trace_dot.get_center(), color="#6B3E26", radius=0.09))

        # Add rope visuals behind the involute curve so they appear connected smoothly
        self.add(wrapped_arc)
        self.add(rope, rope_center, rope_tip)
        self.bring_to_front(rope_tip)

        # Reuse the step-by-step animation while showing continuous rope growth
        steps = 12
        for k in range(1, steps + 1):
            target = PI * 0.85 * (k / steps)
            self.play(angle_tracker.animate.set_value(target), run_time=0.35, rate_func=linear)
            # Small pulse on rope tip for visual emphasis
            self.play(rope_tip.animate.scale(1.05), run_time=0.07)
            self.play(rope_tip.animate.scale(1/1.05), run_time=0.07)

        # Final smooth finish
        self.play(angle_tracker.animate.set_value(PI * 0.85), run_time=0.9, rate_func=smooth)

        # Clean up updaters so curve remains
        rope.remove_updater(update_rope)
        rope_center.clear_updaters()
        wrapped_arc.clear_updaters()
        self.wait(0.3)

        involute_label = Text("Involute Profile", font_size=18, color=RED_B).next_to(
            involute_curve, RIGHT, buff=0.4
        )
        self.play(Write(involute_label), run_time=0.5)
        self.wait(1)