"""
Animated gear mesh visualization using Manim
"""

import numpy as np
from manim import *


class GearMeshAnimation(Scene):
    """Animated gear mesh with two meshing gears"""
    
    CONFIG = {
        "camera_config": {"background_color": WHITE},
    }

    def construct(self):
        # ============= GEAR PARAMETERS =============
        num_teeth = 22
        phi = np.radians(20)  # Pressure angle
        rp = 2.64  # Pitch radius (scaled for Manim: 132mm / 50)
        m = 2 * rp / num_teeth  # Module
        rb = rp * np.cos(phi)  # Base radius
        ra = rp + 1 * m  # Addendum radius
        rd = rp - 1.25 * m  # Dedendum radius
        p = 2 * np.pi * rp / num_teeth  # Pitch
        tp = p / 2  # Tooth thickness
        
        # ============= HELPER FUNCTIONS =============
        def involute(alpha_rad):
            return np.tan(alpha_rad) - alpha_rad

        def pressure_angle_at_radius(rb, r):
            return np.where(r < rb, 0, np.arccos(rb / r))

        def tooth_thickness_at_radius(r, tp, rp, phi_rad, rb):
            psi = pressure_angle_at_radius(rb, r)
            return 2 * r * (tp / (2 * rp) + involute(phi_rad) - involute(psi))

        def point_on_circle(center, radius, angle):
            return center + radius * np.array([np.cos(angle), np.sin(angle), 0])

        def generate_gear_profile(center, rb, ra, tp, rp, phi_rad, ptP, ptP1, num_teeth, rd, rotation_angle=0, num_points=35):
            """Generate gear profile points"""
            tooth_angle = 2 * np.pi / num_teeth
            r_end = max(rd, ra) if rb < rd else ra
            
            gear_points = []
            
            for tooth_num in range(num_teeth):
                rotation = tooth_num * tooth_angle + rotation_angle
                rotated_P = np.array([
                    np.cos(rotation) * ptP[0] - np.sin(rotation) * ptP[1],
                    np.sin(rotation) * ptP[0] + np.cos(rotation) * ptP[1]
                ]) + center[:2]
                
                rotated_P1 = np.array([
                    np.cos(rotation) * ptP1[0] - np.sin(rotation) * ptP1[1],
                    np.sin(rotation) * ptP1[0] + np.cos(rotation) * ptP1[1]
                ]) + center[:2]
                
                angle_P1 = np.arctan2(rotated_P1[1] - center[1], rotated_P1[0] - center[0])
                
                half_angle_base = tooth_thickness_at_radius(rb, tp, rp, phi_rad, rb) / (2 * rb)
                angle_left_base = angle_P1 - half_angle_base
                angle_right_base = angle_P1 + half_angle_base
                angle_next_left = angle_P1 + tooth_angle - half_angle_base
                
                # Left involute
                for i in range(num_points + 1):
                    r = rb + (r_end - rb) * i / num_points
                    half_angle = tooth_thickness_at_radius(r, tp, rp, phi_rad, rb) / (2 * r)
                    pt = point_on_circle(center, r, angle_P1 - half_angle)
                    gear_points.append(pt)
                
                # Addendum arc
                half_angle_end = tooth_thickness_at_radius(r_end, tp, rp, phi_rad, rb) / (2 * r_end)
                for i in range(10):
                    angle = angle_P1 - half_angle_end + (2 * half_angle_end) * i / 9
                    pt = point_on_circle(center, r_end, angle)
                    gear_points.append(pt)
                
                # Right involute
                for i in range(num_points, -1, -1):
                    r = rb + (r_end - rb) * i / num_points
                    half_angle = tooth_thickness_at_radius(r, tp, rp, phi_rad, rb) / (2 * r)
                    pt = point_on_circle(center, r, angle_P1 + half_angle)
                    gear_points.append(pt)
                
                # Dedendum arc
                for i in range(10):
                    angle = angle_right_base + (angle_next_left - angle_right_base) * i / 9
                    pt = point_on_circle(center, rd, angle)
                    gear_points.append(pt)
            
            return np.array(gear_points)
        
        # ============= SETUP GEAR POSITIONS =============
        center1 = np.array([0, 0, 0])
        angle_initial = 100 * np.pi / 180
        ptP = np.array([rp * np.cos(angle_initial + (tp / 2) / rp), rp * np.sin(angle_initial + (tp / 2) / rp), 0])
        ptP1 = np.array([rp * np.cos(angle_initial), rp * np.sin(angle_initial), 0])
        
        angle_to_P = np.arctan2(ptP[1], ptP[0])
        center2 = center1 + 2 * rp * np.array([np.cos(angle_to_P), np.sin(angle_to_P), 0])
        angle_P1_gear2 = angle_to_P - (tp / 2) / rp
        ptP1_gear2 = np.array([rp * np.cos(angle_P1_gear2), rp * np.sin(angle_P1_gear2), 0])
        
        # ============= CREATE GEARS AS ANIMATED OBJECTS =============
        
        # Create gear profiles for animation
        def create_gear_group(center, rb, ra, tp, rp, phi_rad, ptP, ptP1, num_teeth, rd, rotation_angle, scale=1):
            """Create a gear as a Manim object"""
            points = generate_gear_profile(center, rb, ra, tp, rp, phi_rad, ptP, ptP1, num_teeth, rd, rotation_angle)
            
            # Create polygon from points
            gear = Polygon(*points, fill_color=GREY, fill_opacity=0.8, stroke_color=BLACK, stroke_width=2)
            return gear
        
        # ============= CREATE CIRCLES AND CENTERS =============
        
        # Pitch circles
        circle1_pitch = Circle(radius=rp, color=BLUE, stroke_width=1, stroke_opacity=0.5)
        circle1_pitch.move_to(center1)
        
        circle2_pitch = Circle(radius=rp, color=BLUE, stroke_width=1, stroke_opacity=0.5)
        circle2_pitch.move_to(center2)
        
        # Center dots
        dot1 = Dot(point=center1, radius=0.1, color=BLACK)
        dot2 = Dot(point=center2, radius=0.1, color=BLACK)
        
        # Line between centers
        center_line = Line(center1, center2, color=BLACK, stroke_width=1, stroke_opacity=0.3)
        
        # Mesh point
        mesh_point = Dot(point=ptP, radius=0.12, color=RED)
        
        # ============= ANIMATION =============
        
        # Title
        title = Text("Gear Mesh Animation", font_size=36)
        title.to_edge(UP)
        
        # Frame counter
        frame_num = Integer(1, font_size=20)
        frame_num.to_corner(DOWN + LEFT)
        
        # Add static elements
        self.add(circle1_pitch, circle2_pitch, dot1, dot2, center_line, title)
        self.add(frame_num)
        
        # Animation: rotate gears in opposite directions
        # Gear 1 rotates counterclockwise, Gear 2 rotates clockwise
        
        # We'll update gears frame by frame
        num_frames = 60
        
        # Create initial gears
        gear1 = create_gear_group(center1, rb, ra, tp, rp, phi, ptP, ptP1, num_teeth, rd, 0)
        gear2 = create_gear_group(center2, rb, ra, tp, rp, phi, ptP, ptP1_gear2, num_teeth, rd, 0)
        
        self.add(gear1, gear2, mesh_point)
        
        def update_gears(scene, t):
            """Update function for animation"""
            # t goes from 0 to 1
            angle_increment = 2 * np.pi * t
            
            # Generate new gear profiles
            new_gear1_points = generate_gear_profile(center1, rb, ra, tp, rp, phi, ptP, ptP1, num_teeth, rd, angle_increment)
            new_gear2_points = generate_gear_profile(center2, rb, ra, tp, rp, phi, ptP, ptP1_gear2, num_teeth, rd, -angle_increment)
            
            # Update gear1
            gear1.set_points_as_corners(new_gear1_points)
            
            # Update gear2
            gear2.set_points_as_corners(new_gear2_points)
            
            # Update frame number
            frame_num.set_value(int(t * num_frames) + 1)
        
        # Use updater for smooth animation
        gear1.add_updater(lambda mob, dt: None)  # Placeholder
        gear2.add_updater(lambda mob, dt: None)  # Placeholder
        
        # Animate for one complete rotation
        self.play(
            AnimationGroup(
                *[
                    Succession(
                        Wait(1/30)  # 30 fps equivalent
                    ) for _ in range(num_frames)
                ]
            ),
            rate_func=linear,
            run_time=4
        )
        
        # Alternative approach: Use ValueTracker for smooth animation
        # This creates a smoother animation
        self.remove(gear1, gear2)
        
        # Reset with ValueTracker approach
        rotation_val = ValueTracker(0)
        
        def gear1_updater(mob):
            angle = rotation_val.get_value()
            new_points = generate_gear_profile(center1, rb, ra, tp, rp, phi, ptP, ptP1, num_teeth, rd, angle)
            mob.set_points_as_corners(new_points)
        
        def gear2_updater(mob):
            angle = rotation_val.get_value()
            new_points = generate_gear_profile(center2, rb, ra, tp, rp, phi, ptP, ptP1_gear2, num_teeth, rd, -angle)
            mob.set_points_as_corners(new_points)
        
        def mesh_point_updater(mob):
            angle = rotation_val.get_value()
            # Mesh point rotates around gear1 center
            mesh_x = ptP[0] * np.cos(angle) - ptP[1] * np.sin(angle)
            mesh_y = ptP[0] * np.sin(angle) + ptP[1] * np.cos(angle)
            mob.move_to(np.array([mesh_x, mesh_y, 0]))
        
        def frame_updater(mob):
            progress = rotation_val.get_value() / (2 * np.pi)
            frame = int(progress * num_frames) + 1
            mob.set_value(min(frame, num_frames))
        
        gear1.add_updater(gear1_updater)
        gear2.add_updater(gear2_updater)
        mesh_point.add_updater(mesh_point_updater)
        frame_num.add_updater(frame_updater)
        
        self.add(gear1, gear2, mesh_point)
        
        # Animate rotation through one complete cycle
        self.play(
            rotation_val.animate.set_value(2 * np.pi),
            rate_func=linear,
            run_time=4
        )
        
        self.wait(1)


class GearMeshSimple(Scene):
    """Simpler version focused on the gear interaction"""
    
    CONFIG = {
        "camera_config": {"background_color": WHITE},
    }

    def construct(self):
        # ============= GEAR PARAMETERS =============
        num_teeth = 20
        phi = np.radians(20)
        rp = 2.0
        m = 2 * rp / num_teeth
        rb = rp * np.cos(phi)
        ra = rp + 1 * m
        rd = rp - 1.25 * m
        
        # ============= HELPER FUNCTIONS =============
        def involute(alpha_rad):
            return np.tan(alpha_rad) - alpha_rad

        def pressure_angle_at_radius(rb, r):
            return np.where(r < rb, 0, np.arccos(rb / r))

        def tooth_thickness_at_radius(r, tp, rp, phi_rad, rb):
            psi = pressure_angle_at_radius(rb, r)
            return 2 * r * (tp / (2 * rp) + involute(phi_rad) - involute(psi))

        def point_on_circle(center, radius, angle):
            return center + radius * np.array([np.cos(angle), np.sin(angle), 0])

        def generate_gear_profile(center, rb, ra, tp, rp, phi_rad, num_teeth, rd, rotation_angle=0, num_points=30):
            """Simplified gear profile generation"""
            tooth_angle = 2 * np.pi / num_teeth
            r_end = max(rd, ra) if rb < rd else ra
            
            gear_points = []
            
            for tooth_num in range(num_teeth):
                base_angle = tooth_num * tooth_angle + rotation_angle
                
                # Left involute
                for i in range(num_points + 1):
                    r = rb + (r_end - rb) * i / num_points
                    half_angle = tp / (2 * r)
                    pt = point_on_circle(center, r, base_angle - half_angle)
                    gear_points.append(pt)
                
                # Addendum arc
                for i in range(10):
                    angle = base_angle - tp / (2 * r_end) + (tp / r_end) * i / 9
                    pt = point_on_circle(center, r_end, angle)
                    gear_points.append(pt)
                
                # Right involute
                for i in range(num_points, -1, -1):
                    r = rb + (r_end - rb) * i / num_points
                    half_angle = tp / (2 * r)
                    pt = point_on_circle(center, r, base_angle + half_angle)
                    gear_points.append(pt)
                
                # Dedendum arc
                for i in range(10):
                    angle = base_angle + tp / (2 * rd) + (tooth_angle - tp / rd) * i / 9
                    pt = point_on_circle(center, rd, angle)
                    gear_points.append(pt)
            
            return np.array(gear_points)
        
        # ============= SETUP =============
        center1 = np.array([0, 0, 0])
        center2 = np.array([4.0, 0, 0])
        
        p = 2 * np.pi * rp / num_teeth
        tp = p / 2
        
        # Create initial gears
        gear1_points = generate_gear_profile(center1, rb, ra, tp, rp, phi, num_teeth, rd, 0)
        gear2_points = generate_gear_profile(center2, rb, ra, tp, rp, phi, num_teeth, rd, 0)
        
        gear1 = Polygon(*gear1_points, fill_color=GREY_A, fill_opacity=0.8, 
                       stroke_color=DARK_GREY, stroke_width=2.5)
        gear2 = Polygon(*gear2_points, fill_color=GREY_A, fill_opacity=0.8, 
                       stroke_color=DARK_GREY, stroke_width=2.5)
        
        # Circles
        circle1_pitch = Circle(radius=rp, color=BLUE, stroke_width=1.5, stroke_opacity=0.4)
        circle1_pitch.move_to(center1)
        
        circle2_pitch = Circle(radius=rp, color=BLUE, stroke_width=1.5, stroke_opacity=0.4)
        circle2_pitch.move_to(center2)
        
        # Centers and mesh point
        dot1 = Dot(center1, radius=0.12, color=BLACK)
        dot2 = Dot(center2, radius=0.12, color=BLACK)
        center_line = Line(center1, center2, color=BLACK, stroke_width=1, stroke_opacity=0.3)
        mesh_point = Dot(center1 + np.array([rp, 0, 0]), radius=0.15, color=RED)
        
        # Add title and labels
        title = Text("Gear Mesh Animation", font_size=40, color=BLACK, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        
        # Add all elements
        self.add(circle1_pitch, circle2_pitch, center_line, dot1, dot2, gear1, gear2, mesh_point, title)
        
        # ============= ANIMATION =============
        
        # Use ValueTracker for smooth rotation
        rotation = ValueTracker(0)
        
        def update_gear1(mob):
            angle = rotation.get_value()
            new_points = generate_gear_profile(center1, rb, ra, tp, rp, phi, num_teeth, rd, angle)
            mob.set_points_as_corners(new_points)
        
        def update_gear2(mob):
            angle = rotation.get_value()
            new_points = generate_gear_profile(center2, rb, ra, tp, rp, phi, num_teeth, rd, -angle)
            mob.set_points_as_corners(new_points)
        
        def update_mesh(mob):
            angle = rotation.get_value()
            mesh_x = center1[0] + rp * np.cos(angle)
            mesh_y = center1[1] + rp * np.sin(angle)
            mob.move_to(np.array([mesh_x, mesh_y, 0]))
        
        gear1.add_updater(update_gear1)
        gear2.add_updater(update_gear2)
        mesh_point.add_updater(update_mesh)
        
        # Animate one complete rotation cycle
        self.play(
            rotation.animate.set_value(2 * np.pi),
            rate_func=linear,
            run_time=6
        )
        
        self.wait(0.5)
