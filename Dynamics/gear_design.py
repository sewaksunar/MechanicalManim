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


from manim import *
import numpy as np


class InvoluteFromFundamentals(Scene):
    """
    Build involute curve from first principles - unwrapping a string from a circle
    """
    
    def construct(self):
        # Title
        title = Text("Involute Curve: From First Principles", font_size=40)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait()
        
        # Base circle
        base_radius = 1.5
        base_circle = Circle(radius=base_radius, color=BLUE)
        base_label = Text("Base Circle", font_size=24, color=BLUE)
        base_label.next_to(base_circle, DOWN, buff=0.3)
        
        self.play(Create(base_circle), Write(base_label))
        self.wait()
        
        # Explanation text
        explanation = Text(
            "Imagine unwrapping a string from a circle...",
            font_size=28,
            color=YELLOW
        )
        explanation.to_edge(DOWN)
        self.play(Write(explanation))
        self.wait()
        
        # Create the involute by unwrapping
        def involute_point(t, r):
            """Generate involute curve point at parameter t"""
            x = r * (np.cos(t) + t * np.sin(t))
            y = r * (np.sin(t) - t * np.cos(t))
            return np.array([x, y, 0])
        
        # Animate the unwrapping process
        t_max = 2 * PI
        num_steps = 60
        
        # Create the string and endpoint
        string = Line(start=ORIGIN, end=ORIGIN, color=YELLOW, stroke_width=3)
        endpoint = Dot(color=RED, radius=0.08)
        endpoint.move_to(base_circle.point_from_proportion(0))
        
        # Path that the endpoint traces
        involute_path = VMobject(color=RED, stroke_width=4)
        involute_path.set_points_as_corners([involute_point(0, base_radius)])
        
        self.play(FadeIn(endpoint), FadeIn(string))
        
        def update_string(mob, alpha):
            t = alpha * t_max
            # Point on circle where string is still wrapped
            circle_point = np.array([
                base_radius * np.cos(t),
                base_radius * np.sin(t),
                0
            ])
            # Point at end of unwrapped string
            end_point = involute_point(t, base_radius)
            
            mob.put_start_and_end_on(circle_point, end_point)
            endpoint.move_to(end_point)
            
            # Add point to involute path
            involute_path.add_points_as_corners([end_point])
        
        self.play(
            UpdateFromAlphaFunc(string, update_string),
            Create(involute_path),
            rate_func=linear,
            run_time=4
        )
        
        self.wait()
        
        # Show the mathematical formula
        formula = MathTex(
            r"\vec{r}(t) = R\begin{bmatrix} \cos t + t\sin t \\ \sin t - t\cos t \end{bmatrix}",
            font_size=36,
            color=GREEN
        )
        formula.to_edge(DOWN)
        
        self.play(
            FadeOut(explanation),
            Write(formula)
        )
        self.wait(2)
        
        # Clear for next scene
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class InvoluteGearConstruction(Scene):
    """
    Build a gear tooth from involute curves
    """
    
    def construct(self):
        # Title
        title = Text("Constructing a Gear Tooth", font_size=40)
        title.to_edge(UP)
        self.play(Write(title))
        
        # Parameters
        num_teeth = 20
        module = 0.25
        pressure_angle = 20 * DEGREES
        
        # Calculate key dimensions
        pitch_radius = module * num_teeth / 2
        base_radius = pitch_radius * np.cos(pressure_angle)
        addendum = module
        dedendum = 1.25 * module
        outer_radius = pitch_radius + addendum
        root_radius = pitch_radius - dedendum
        
        # Show the circles
        base_circle = Circle(radius=base_radius, color=BLUE, stroke_width=2)
        pitch_circle = Circle(radius=pitch_radius, color=GREEN, stroke_width=2)
        outer_circle = Circle(radius=outer_radius, color=YELLOW, stroke_width=2)
        root_circle = Circle(radius=root_radius, color=RED, stroke_width=2)
        
        # Labels
        labels = VGroup(
            Text("Base", font_size=16, color=BLUE).move_to(LEFT * (base_radius + 0.5)),
            Text("Pitch", font_size=16, color=GREEN).move_to(LEFT * (pitch_radius + 0.5)),
            Text("Outer", font_size=16, color=YELLOW).move_to(LEFT * (outer_radius + 0.5)),
            Text("Root", font_size=16, color=RED).move_to(LEFT * (root_radius + 0.5))
        )
        
        self.play(
            Create(base_circle),
            Create(pitch_circle),
            Create(outer_circle),
            Create(root_circle),
            Write(labels),
            run_time=2
        )
        self.wait()
        
        # Generate involute curve
        def involute_curve(r_base, r_start, r_end, num_points=50):
            """Generate involute from r_start to r_end"""
            points = []
            
            # Find t values for start and end radii
            def radius_at_t(t):
                return r_base * np.sqrt(1 + t**2)
            
            # Solve for t_start and t_end
            t_start = 0 if r_start <= r_base else np.sqrt((r_start/r_base)**2 - 1)
            t_end = np.sqrt((r_end/r_base)**2 - 1)
            
            t_values = np.linspace(t_start, t_end, num_points)
            
            for t in t_values:
                x = r_base * (np.cos(t) + t * np.sin(t))
                y = r_base * (np.sin(t) - t * np.cos(t))
                points.append([x, y, 0])
            
            return points
        
        # Create one side of tooth (involute curve)
        involute_points = involute_curve(base_radius, base_radius, outer_radius)
        involute_side1 = VMobject(color=WHITE, stroke_width=4)
        involute_side1.set_points_as_corners(involute_points)
        
        # Calculate tooth angle
        tooth_angle = 2 * PI / num_teeth
        
        # Rotate to position (half tooth width at pitch circle)
        tooth_thickness_angle = PI / num_teeth  # Half the pitch angle
        involute_side1.rotate(tooth_thickness_angle / 2, about_point=ORIGIN)
        
        # Mirror for other side
        involute_side2 = involute_side1.copy()
        involute_side2.flip(RIGHT, about_point=ORIGIN)
        
        # Explanation
        explanation = Text(
            "Two involute curves form the tooth profile",
            font_size=24,
            color=YELLOW
        )
        explanation.to_edge(DOWN)
        self.play(Write(explanation))
        
        # Draw the involutes
        self.play(
            Create(involute_side1),
            Create(involute_side2),
            run_time=2
        )
        self.wait()
        
        # Connect with arcs at top and bottom
        top_arc = Arc(
            radius=outer_radius,
            start_angle=involute_side2.points[-1],
            angle=angle_of_vector(involute_side1.points[-1]) - angle_of_vector(involute_side2.points[-1]),
            color=WHITE,
            stroke_width=4
        )
        
        # Create bottom connection (arc at root)
        root_arc = Arc(
            radius=root_radius,
            start_angle=angle_of_vector(involute_side2.points[0]),
            angle=angle_of_vector(involute_side1.points[0]) - angle_of_vector(involute_side2.points[0]),
            color=WHITE,
            stroke_width=4
        )
        
        self.play(Create(top_arc), Create(root_arc))
        self.wait(2)
        
        # Fade out construction circles and show complete tooth
        tooth_group = VGroup(involute_side1, involute_side2, top_arc, root_arc)
        
        self.play(
            FadeOut(base_circle),
            FadeOut(pitch_circle),
            FadeOut(outer_circle),
            FadeOut(root_circle),
            FadeOut(labels),
            FadeOut(explanation),
            tooth_group.animate.set_color(BLUE).set_stroke(width=3)
        )
        self.wait()
        
        # Build complete gear
        explanation2 = Text(
            "Repeat around the circle to create a complete gear",
            font_size=24,
            color=YELLOW
        )
        explanation2.to_edge(DOWN)
        self.play(Write(explanation2))
        
        # Create remaining teeth
        all_teeth = VGroup(tooth_group)
        for i in range(1, num_teeth):
            tooth_copy = tooth_group.copy()
            tooth_copy.rotate(i * tooth_angle, about_point=ORIGIN)
            all_teeth.add(tooth_copy)
        
        self.play(
            Create(all_teeth[1:]),
            run_time=3
        )
        self.wait()
        
        # Add fill
        self.play(
            all_teeth.animate.set_fill(BLUE, opacity=0.5),
            FadeOut(explanation2)
        )
        self.wait(2)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class SimpleGearClass:
    """Simple gear class built from fundamentals"""
    
    def __init__(self, num_teeth, module=0.2, pressure_angle=20, **kwargs):
        self.num_teeth = num_teeth
        self.module = module
        self.pressure_angle = pressure_angle * DEGREES
        
        # Calculate dimensions
        self.pitch_radius = module * num_teeth / 2
        self.base_radius = self.pitch_radius * np.cos(self.pressure_angle)
        self.addendum = module
        self.dedendum = 1.25 * module
        self.outer_radius = self.pitch_radius + self.addendum
        self.root_radius = max(self.pitch_radius - self.dedendum, self.base_radius * 0.9)
        self.tooth_angle = 2 * PI / num_teeth
        
        # Create the gear shape
        self.mobject = self.create_gear_shape(**kwargs)
        
    def involute_point(self, t):
        """Calculate point on involute curve"""
        r = self.base_radius
        x = r * (np.cos(t) + t * np.sin(t))
        y = r * (np.sin(t) - t * np.cos(t))
        return np.array([x, y, 0])
    
    def create_tooth_profile(self):
        """Create one tooth profile"""
        # Generate involute curve from base to outer radius
        def radius_at_t(t):
            return self.base_radius * np.sqrt(1 + t**2)
        
        # Solve for t at outer radius
        if self.outer_radius > self.base_radius:
            t_max = np.sqrt((self.outer_radius / self.base_radius)**2 - 1)
        else:
            t_max = 0
        
        t_values = np.linspace(0, t_max, 30)
        
        # Right side of tooth
        right_points = [self.involute_point(t) for t in t_values]
        
        # Rotate for tooth thickness
        tooth_thickness_angle = PI / self.num_teeth
        
        tooth_path = VMobject()
        tooth_path.set_points_as_corners(right_points)
        tooth_path.rotate(tooth_thickness_angle / 2, about_point=ORIGIN)
        
        # Left side (mirrored)
        left_path = tooth_path.copy().flip(RIGHT, about_point=ORIGIN)
        
        # Combine into single path
        all_points = []
        
        # Start at root on one side
        start_angle = angle_of_vector(left_path.points[0])
        root_start = self.root_radius * np.array([np.cos(start_angle), np.sin(start_angle), 0])
        all_points.append(root_start)
        
        # Add left involute
        all_points.extend(left_path.points)
        
        # Top arc
        top_angle = angle_of_vector(tooth_path.points[-1]) - angle_of_vector(left_path.points[-1])
        for i in range(10):
            angle = angle_of_vector(left_path.points[-1]) + top_angle * i / 9
            point = self.outer_radius * np.array([np.cos(angle), np.sin(angle), 0])
            all_points.append(point)
        
        # Add right involute (reversed)
        all_points.extend(reversed(tooth_path.points))
        
        # Bottom arc back to start
        end_angle = angle_of_vector(tooth_path.points[0])
        root_end = self.root_radius * np.array([np.cos(end_angle), np.sin(end_angle), 0])
        
        bottom_angle = start_angle - end_angle
        for i in range(10):
            angle = end_angle + bottom_angle * i / 9
            point = self.root_radius * np.array([np.cos(angle), np.sin(angle), 0])
            all_points.append(point)
        
        tooth = VMobject()
        tooth.set_points_as_corners(all_points)
        return tooth
    
    def create_gear_shape(self, **kwargs):
        """Create complete gear"""
        tooth = self.create_tooth_profile()
        
        gear = VGroup()
        for i in range(self.num_teeth):
            tooth_copy = tooth.copy()
            tooth_copy.rotate(i * self.tooth_angle, about_point=ORIGIN)
            gear.add(tooth_copy)
        
        # Set default styling
        gear.set_stroke(WHITE, width=2)
        gear.set_fill(BLUE, opacity=0.7)
        
        # Apply any custom styling
        if 'color' in kwargs:
            gear.set_color(kwargs['color'])
        if 'fill_opacity' in kwargs:
            gear.set_fill(opacity=kwargs['fill_opacity'])
        
        return gear
    
    def get_mobject(self):
        return self.mobject


class GearMeshingFromFundamentals(Scene):
    """
    Demonstrate gear meshing with gears built from scratch
    """
    
    def construct(self):
        # Title
        title = Text("Gear Meshing: The Mathematics", font_size=40)
        title.to_edge(UP)
        self.play(Write(title))
        
        # Create two gears
        gear1 = SimpleGearClass(num_teeth=15, module=0.3, color=BLUE)
        gear2 = SimpleGearClass(num_teeth=25, module=0.3, color=RED)
        
        # Position gears
        gear1_mob = gear1.get_mobject()
        gear2_mob = gear2.get_mobject()
        
        # Position them so they mesh
        separation = gear1.pitch_radius + gear2.pitch_radius
        gear1_mob.shift(LEFT * separation / 2)
        gear2_mob.shift(RIGHT * separation / 2)
        
        # Show pitch circles
        pitch1 = Circle(radius=gear1.pitch_radius, color=GREEN, stroke_width=2)
        pitch1.move_to(gear1_mob.get_center())
        pitch2 = Circle(radius=gear2.pitch_radius, color=GREEN, stroke_width=2)
        pitch2.move_to(gear2_mob.get_center())
        
        # Center dots
        dot1 = Dot(gear1_mob.get_center(), color=YELLOW)
        dot2 = Dot(gear2_mob.get_center(), color=YELLOW)
        
        # Show the gears
        self.play(
            FadeIn(gear1_mob, scale=0.5),
            FadeIn(gear2_mob, scale=0.5),
            Create(pitch1),
            Create(pitch2),
            Create(dot1),
            Create(dot2),
            run_time=2
        )
        
        # Mathematical relationship
        ratio_text = MathTex(
            r"\omega_1 \cdot r_1 = \omega_2 \cdot r_2",
            font_size=32,
            color=YELLOW
        )
        ratio_text.next_to(title, DOWN, buff=0.3)
        
        ratio_calc = MathTex(
            r"\frac{\omega_1}{\omega_2} = \frac{r_2}{r_1} = \frac{25}{15} = \frac{5}{3}",
            font_size=28,
            color=GREEN
        )
        ratio_calc.next_to(ratio_text, DOWN, buff=0.2)
        
        self.play(Write(ratio_text))
        self.wait()
        self.play(Write(ratio_calc))
        self.wait()
        
        # Mark the pitch point
        pitch_point = gear1_mob.get_center() + RIGHT * gear1.pitch_radius
        pitch_dot = Dot(pitch_point, color=YELLOW, radius=0.1)
        pitch_label = Text("Pitch Point", font_size=20, color=YELLOW)
        pitch_label.next_to(pitch_dot, UP, buff=0.2)
        
        self.play(
            FadeIn(pitch_dot),
            Write(pitch_label)
        )
        self.wait()
        
        # Rotate the gears
        angle1 = 3 * gear1.tooth_angle
        angle2 = -(15/25) * angle1  # Inverse ratio
        
        self.play(
            Rotate(gear1_mob, angle1, about_point=gear1_mob.get_center()),
            Rotate(gear2_mob, angle2, about_point=gear2_mob.get_center()),
            rate_func=linear,
            run_time=4
        )
        
        self.wait()
        
        # Continue rotation
        self.play(
            Rotate(gear1_mob, 2*PI, about_point=gear1_mob.get_center()),
            Rotate(gear2_mob, -(15/25) * 2*PI, about_point=gear2_mob.get_center()),
            rate_func=linear,
            run_time=5
        )
        
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class InvoluteProperties(Scene):
    """
    Demonstrate why involute curves are special for gears
    """
    
    def construct(self):
        # Title
        title = Text("Why Involute Curves?", font_size=40)
        title.to_edge(UP)
        self.play(Write(title))
        
        # Property 1: Constant pressure angle
        prop1 = Text(
            "Property 1: Constant Pressure Angle",
            font_size=32,
            color=YELLOW
        )
        prop1.next_to(title, DOWN, buff=0.5)
        self.play(Write(prop1))
        
        # Draw involute with tangent lines
        base_radius = 1.5
        base_circle = Circle(radius=base_radius, color=BLUE, stroke_width=2)
        
        def involute_point(t, r):
            x = r * (np.cos(t) + t * np.sin(t))
            y = r * (np.sin(t) - t * np.cos(t))
            return np.array([x, y, 0])
        
        # Create involute
        t_values = np.linspace(0, 1.5, 50)
        involute_points = [involute_point(t, base_radius) for t in t_values]
        involute = VMobject(color=RED, stroke_width=3)
        involute.set_points_as_corners(involute_points)
        
        self.play(Create(base_circle), Create(involute))
        
        # Show tangent lines at different points
        tangent_lines = VGroup()
        normal_lines = VGroup()
        
        for t in [0.3, 0.7, 1.1]:
            point = involute_point(t, base_radius)
            
            # Tangent direction (perpendicular to radius from base circle)
            circle_point = np.array([base_radius * np.cos(t), base_radius * np.sin(t), 0])
            tangent_dir = point - circle_point
            tangent_dir = tangent_dir / np.linalg.norm(tangent_dir)
            
            tangent = Line(
                point - tangent_dir * 0.5,
                point + tangent_dir * 0.5,
                color=GREEN,
                stroke_width=2
            )
            
            # Normal (points to base circle center along the string)
            normal_dir = circle_point - point
            normal_dir = normal_dir / np.linalg.norm(normal_dir)
            
            normal = Line(
                point,
                point + normal_dir * 1.0,
                color=YELLOW,
                stroke_width=2
            )
            
            tangent_lines.add(tangent)
            normal_lines.add(normal)
        
        self.play(Create(tangent_lines), Create(normal_lines))
        
        explanation = Text(
            "All normals pass through a fixed line of action",
            font_size=24,
            color=YELLOW
        )
        explanation.to_edge(DOWN)
        self.play(Write(explanation))
        
        self.wait(3)
        
        # Clear
        self.play(*[FadeOut(mob) for mob in [
            base_circle, involute, tangent_lines, normal_lines, prop1, explanation
        ]])
        
        # Property 2: Center distance variation
        prop2 = Text(
            "Property 2: Tolerant to Center Distance Changes",
            font_size=32,
            color=YELLOW
        )
        prop2.next_to(title, DOWN, buff=0.5)
        self.play(Write(prop2))
        
        # Create two small gears
        gear1 = SimpleGearClass(num_teeth=12, module=0.25, color=BLUE)
        gear2 = SimpleGearClass(num_teeth=12, module=0.25, color=RED)
        
        gear1_mob = gear1.get_mobject()
        gear2_mob = gear2.get_mobject()
        
        # Start with correct distance
        correct_distance = gear1.pitch_radius + gear2.pitch_radius
        gear1_mob.shift(LEFT * correct_distance / 2)
        gear2_mob.shift(RIGHT * correct_distance / 2)
        
        self.play(FadeIn(gear1_mob), FadeIn(gear2_mob))
        
        # Show they still mesh with different distances
        explanation2 = Text(
            "Gears still mesh correctly even with spacing variations",
            font_size=24,
            color=GREEN
        )
        explanation2.to_edge(DOWN)
        self.play(Write(explanation2))
        
        # Vary the distance
        self.play(
            gear2_mob.animate.shift(RIGHT * 0.3),
            run_time=1.5
        )
        
        # Rotate to show they still work
        self.play(
            Rotate(gear1_mob, PI, about_point=gear1_mob.get_center()),
            Rotate(gear2_mob, -PI, about_point=gear2_mob.get_center()),
            rate_func=linear,
            run_time=3
        )
        
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects])


# Main comprehensive scene
class ComprehensiveGearDemo(Scene):
    """Complete demonstration from fundamentals"""
    
    def construct(self):
        # Final title
        title = Text("Involute Gears", font_size=60, weight=BOLD)
        subtitle = Text("Built from Mathematical Fundamentals", font_size=32)
        subtitle.next_to(title, DOWN)
        
        title_group = VGroup(title, subtitle)
        
        self.play(Write(title), Write(subtitle))
        self.wait()
        
        self.play(title_group.animate.scale(0.5).to_corner(UL))
        
        # Create multiple gears of different sizes
        gear1 = SimpleGearClass(num_teeth=10, module=0.2, color=RED)
        gear2 = SimpleGearClass(num_teeth=15, module=0.2, color=ORANGE)
        gear3 = SimpleGearClass(num_teeth=20, module=0.2, color=YELLOW)
        gear4 = SimpleGearClass(num_teeth=25, module=0.2, color=GREEN)
        
        gears = [gear1, gear2, gear3, gear4]
        gear_mobs = [g.get_mobject() for g in gears]
        
        # Arrange in a gear train
        gear_mobs[0].shift(LEFT * 4)
        
        for i in range(1, len(gears)):
            prev_gear = gears[i-1]
            curr_gear = gears[i]
            separation = prev_gear.pitch_radius + curr_gear.pitch_radius
            gear_mobs[i].move_to(gear_mobs[i-1].get_center() + RIGHT * separation)
        
        # Show gears appearing
        self.play(
            LaggedStart(*[FadeIn(g, scale=0.3) for g in gear_mobs], lag_ratio=0.3),
            run_time=2
        )
        
        # Rotate the gear train
        angles = [2*PI, -2*PI * 10/15, 2*PI * 10/20, -2*PI * 10/25]
        
        self.play(
            *[Rotate(gear_mobs[i], angles[i], about_point=gear_mobs[i].get_center(), rate_func=linear)
              for i in range(len(gears))],
            run_time=6
        )
        
        self.wait(2)


# Quick test scene
class QuickTest(Scene):
    """Quick test of gear from fundamentals"""
    
    def construct(self):
        gear = SimpleGearClass(num_teeth=20, module=0.3, color=BLUE)
        gear_mob = gear.get_mobject()
        
        self.add(gear_mob)
        self.play(
            Rotate(gear_mob, 2*PI, rate_func=linear),
            run_time=4
        )
        self.wait()