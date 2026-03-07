from manim import *
import numpy as np

class CurveLinkageFigure(Scene):
    def construct(self):
        # Set background color
        self.background_color = WHITE
        
        # Define points (scaled for better visualization)
        z0 = np.array([0, 0, 0])
        z1 = np.array([1, 2, 0])
        z2 = np.array([2, 1, 0])
        
        # Create smooth curve through points
        t_vals = np.linspace(0, 1, 100)
        
        def quadratic_bezier(t, p0, p1, p2):
            return (1-t)**2 * p0 + 2*(1-t)*t * p1 + t**2 * p2
        
        curve_points = np.array([quadratic_bezier(t, z0, z1, z2) for t in t_vals])
        curve = VMobject()
        curve.set_points_as_corners(curve_points)
        curve.set_color(BLUE)
        curve.set_stroke(width=2)
        
        # Line k: z0 to z1
        line_k = Line(z0, z1, color=BLACK, stroke_width=2)
        
        # Line k+1: z1 to z2 (dashed appearance)
        line_k_plus_1 = Line(z1, z2, color=BLACK, stroke_width=2)
        line_k_plus_1.set_stroke(opacity=0.6)
        
        # Extension line (dashed-like, going further)
        extension_dir = (z1 - z0) / np.linalg.norm(z1 - z0)
        extension_point = z0 + 1.8 * (z1 - z0)
        extension = Line(z0, extension_point, color=GRAY_C, stroke_width=1.5)
        extension.set_stroke(opacity=0.5)
        
        # Tangent/normal direction at z1
        tangent_dir = (z2 - z1) / np.linalg.norm(z2 - z1)
        tangent_length = 0.6
        tangent_line = Line(
            z1 - tangent_length * tangent_dir,
            z1 + tangent_length * tangent_dir,
            color=BLUE,
            stroke_width=1.5
        )
        tangent_line.set_stroke(opacity=0.6)
        
        # Calculate angles for arcs
        incoming_angle = np.degrees(np.arctan2(z1[1] - z0[1], z1[0] - z0[0]))
        outgoing_angle = np.degrees(np.arctan2(z2[1] - z1[1], z2[0] - z1[0]))
        
        arc_radius = 0.35
        
        # Arc for angle theta_k (between incoming direction and tangent)
        arc_theta = Arc(
            radius=arc_radius,
            angle=45 * DEGREES,
            start_angle=incoming_angle * DEGREES,
            arc_center=z1,
            color=BLUE,
            stroke_width=2
        )
        
        # Arc for angle phi_k (between tangent and outgoing direction)
        arc_phi = Arc(
            radius=arc_radius,
            angle=50 * DEGREES,
            start_angle=(incoming_angle - 50) * DEGREES,
            arc_center=z1,
            color=BLUE,
            stroke_width=2
        )
        
        # Labels for line segments
        label_k = MathTex(r"\ell_k", color=BLACK, font_size=32)
        midpoint_k = (z0 + z1) / 2
        label_k.move_to(midpoint_k + np.array([-0.35, -0.25, 0]))
        
        label_k_plus_1 = MathTex(r"\ell_{k+1}", color=BLACK, font_size=32)
        midpoint_k1 = (z1 + z2) / 2
        label_k_plus_1.move_to(midpoint_k1 + np.array([0.35, -0.25, 0]))
        
        # Angle labels
        label_theta = MathTex(r"\theta_k", color=BLUE, font_size=28)
        label_theta.move_to(z1 + np.array([0.5, -0.35, 0]))
        
        label_phi = MathTex(r"\phi_k", color=BLUE, font_size=28)
        label_phi.move_to(z1 + np.array([-0.5, -0.5, 0]))
        
        # Points and labels
        dot_z0 = Dot(z0, color=RED, radius=0.08)
        label_z0 = MathTex(r"z_{k-1}", color=RED, font_size=28)
        label_z0.next_to(dot_z0, DOWN + LEFT, buff=0.15)
        
        dot_z1 = Dot(z1, color=RED, radius=0.08)
        label_z1 = MathTex(r"z_k", color=RED, font_size=28)
        label_z1.next_to(dot_z1, UP + LEFT, buff=0.15)
        
        dot_z2 = Dot(z2, color=RED, radius=0.08)
        label_z2 = MathTex(r"z_{k+1}", color=RED, font_size=28)
        label_z2.next_to(dot_z2, UP + RIGHT, buff=0.15)
        
        # Assemble all elements
        self.add(
            extension,
            line_k,
            line_k_plus_1,
            curve,
            tangent_line,
            arc_theta,
            arc_phi,
            dot_z0,
            dot_z1,
            dot_z2,
            label_k,
            label_k_plus_1,
            label_theta,
            label_phi,
            label_z0,
            label_z1,
            label_z2
        )