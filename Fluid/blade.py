from manim import *
import numpy as np


class Blade(VGroup):
    """Blade-shaped airfoil VGroup used by the scene."""
    def __init__(self, width=0.5, height=2, **kwargs):
        super().__init__(**kwargs)
        
        # CONVEX (curves outward - right side)
        convex_curve = CubicBezier(
            [-2, 3, 0],
            [1, 1, 0],
            [1, -1, 0],
            [-1, -3, 0],
            color=BLUE
        )

        # CONCAVE (curves inward - left side)
        p0 = np.array([-2, 3, 0])
        p1 = np.array([.5, 1, 0])
        p2 = np.array([.5, -1, 0])
        p3 = np.array([-1, -3, 0])
        concave_curve = CubicBezier(p0, p1, p2, p3, color=RED)
        # keep control points available for geometric queries (tangent, normals, etc.)
        self.concave_ctrl_pts = (p0, p1, p2, p3)
        self.concave_curve = concave_curve
        
        # Create blade using boolean difference
        blade_shape = Difference(convex_curve, concave_curve)
        blade_shape.set_fill(BLUE, opacity=0.6)
        blade_shape.set_stroke(BLUE, width=2)
        
        # Get exact inlet and outlet positions from the curves
        inlet_pos = convex_curve.get_start()  # Top point
        outlet_pos = convex_curve.get_end()   # Bottom point
        
        # Create inlet and outlet dots
        inlet = Dot(radius=0.1, color=YELLOW, fill_opacity=0.8)
        inlet.move_to(inlet_pos)
        
        outlet = Dot(radius=0.1, color=RED, fill_opacity=0.8)
        outlet.move_to(outlet_pos)
        
        # Add everything to the VGroup so they move together
        self.add(blade_shape, inlet, outlet)
        self.blade = blade_shape
        self.inlet = inlet
        self.outlet = outlet


class BladeInlet(MovingCameraScene):
    """Scene that visualizes inlet velocity triangle on the blade."""
    def construct(self):
        blade = Blade()
        blade.move_to(ORIGIN)
        
        # Show the blade
        self.play(FadeIn(blade.blade), run_time=2)
        self.wait(0.5)
        
        # Show inlet
        self.play(FadeIn(blade.inlet), run_time=1)
        
        # Add label for inlet
        inlet_label = Text("Inlet", font_size=28, color=YELLOW).next_to(
            blade.inlet, UP + RIGHT, buff=0.2
        )
        self.play(Write(inlet_label))
        self.wait(0.5)
        self.play(FadeOut(inlet_label))
        self.wait(0.5)
        
        # Zoom into the inlet
        self.play(
            self.camera.frame.animate.scale(0.3).move_to(blade.inlet),
            run_time=2
        )
        self.wait(1)
        inlet_center = blade.inlet.get_center()
        # draw tangent to the concave Bezier at the inlet (t=0)
        # analytic derivative for cubic Bezier at t=0 is 3*(P1 - P0)
        p0, p1, p2, p3 = blade.concave_ctrl_pts
        tangent = 3 * (p1 - p0)
        if np.linalg.norm(tangent) != 0:
            unit_tan = tangent / np.linalg.norm(tangent)
            L = 1.0  # half-length of displayed tangent line
            tangent_line = Line(
                inlet_center - unit_tan * L,
                inlet_center + unit_tan * L,
                color=GRAY,
                stroke_width=2,
            )
            self.play(Create(tangent_line))
            # optional small dot at inlet to emphasize location
            self.play(FadeIn(Dot(inlet_center, radius=0.03, color=WHITE)))

        # ============= VELOCITY PARAMETERS & DISPLAY =============

        # Parameters
        alpha1 = np.radians(20)
        V1_mag, u_mag = 1.5, 1.0

        # Vectors (keeping the original arithmetic to preserve the visual)
        V1_vector = V1_mag * np.array([-np.cos(alpha1), np.sin(alpha1), 0])
        u_vector = u_mag * np.array([1.0, 0.0, 0.0])
        neg_u_vector = -u_vector
        Vr1_vector = V1_vector - u_vector
        beta1 = np.arctan2(Vr1_vector[1], Vr1_vector[0])

        # Useful points (named for clarity)
        V1_tip = inlet_center + V1_vector
        center = inlet_center

        # Common arrow kwargs - consistent styling
        ARROW_KWARGS = dict(
            buff=0, 
            stroke_width=6, 
            tip_length=0.25,
            max_stroke_width_to_length_ratio=999
        )
        
        COMPONENT_ARROW_KWARGS = dict(
            buff=0,
            stroke_width=4,
            tip_length=0.2,
            max_stroke_width_to_length_ratio=999
        )

        # ============= V1 (Absolute Velocity) =============
        V1_arrow = Arrow(V1_tip, center, color=GREEN, **ARROW_KWARGS)
        V1_label = MathTex(r"V_{1}", font_size=34, color=GREEN).next_to(
            V1_arrow, UP + LEFT, buff=0.15
        )
        
        self.play(GrowArrow(V1_arrow), Write(V1_label))
        self.wait(1)

        # ============= Components: V1x (tangential) and V1y (radial) =============
        V1x_vec = np.array([V1_vector[0], 0, 0])
        V1y_vec = np.array([0, V1_vector[1], 0])

        V1x_arrow = Arrow(
            center + V1x_vec, center, 
            color=YELLOW, 
            **COMPONENT_ARROW_KWARGS
        )
        V1x_label = MathTex(r"V_{1x}", font_size=28, color=YELLOW).next_to(
            V1x_arrow, DOWN, buff=0.15
        )

        V1y_arrow = Arrow(
            center + V1_vector, center + V1x_vec, 
            color=ORANGE, 
            **COMPONENT_ARROW_KWARGS
        )
        V1y_label = MathTex(r"V_{1y}", font_size=28, color=ORANGE).next_to(
            V1y_arrow, LEFT, buff=0.12
        )

        # Construction lines
        dash1 = DashedLine(center, center + V1x_vec, color=GRAY, dash_length=0.05)
        dash2 = DashedLine(center + V1x_vec, center + V1_vector, color=GRAY, dash_length=0.05)
        
        self.play(Create(dash1), Create(dash2))
        self.play(GrowArrow(V1x_arrow), Write(V1x_label))
        self.play(GrowArrow(V1y_arrow), Write(V1y_label))
        self.wait(1.5)

        # Remove components and show -u
        self.play(FadeOut(dash1, dash2, V1x_arrow, V1y_arrow, V1x_label, V1y_label))
        self.wait(0.5)

        # ============= -u Vector (placed at V1 tip - KEEP EXACT ORIGINAL) =============
        # Place -u so its head is at V1_tip (preserve exact existing expression)
        neg_u_arrow = Arrow(
            V1_arrow.get_start() - neg_u_vector, 
            V1_arrow.get_start(), 
            color=RED, 
            **ARROW_KWARGS
        )
        neg_u_label = MathTex(r"-u", font_size=34, color=RED).next_to(
            neg_u_arrow, DOWN + RIGHT, buff=0.15
        )

        construction = DashedLine(
            V1_arrow.get_start(), 
            V1_arrow.get_start() + neg_u_vector, 
            color=GRAY, 
            dash_length=0.05
        )
        
        self.play(Create(construction))
        self.play(GrowArrow(neg_u_arrow), Write(neg_u_label))
        self.wait(1)

        # ============= Vr1 (Relative Velocity - KEEP EXACT ORIGINAL) =============
        Vr1_arrow = Arrow(
            neg_u_arrow.get_start(), 
            V1_arrow.get_end(), 
            color=PURPLE, 
            **ARROW_KWARGS
        )
        Vr1_label = MathTex(r"V_{r1}", font_size=34, color=PURPLE).next_to(
            Vr1_arrow, RIGHT, buff=0.15
        )
        
        self.play(GrowArrow(Vr1_arrow), Write(Vr1_label))
        self.wait(1.5)
        
        # ============= Angle Annotations =============
        
        # Alpha1: angle between -u arrow and V1 arrow (KEEP EXACT ORIGINAL LOGIC)
        alpha1_arc = Angle(
            V1_arrow, 
            Arrow(
                V1_arrow.get_start(), 
                V1_arrow.get_start() - neg_u_vector, 
                color=RED, 
                **ARROW_KWARGS
            ), 
            radius=0.4, 
            color=WHITE,
            other_angle=False
        )
        alpha1_label = MathTex(r"\alpha_1", font_size=30, color=WHITE).next_to(
            alpha1_arc, UP + LEFT, buff=0.12
        )
        
        # Beta1: angle between -u and Vr1 (KEEP EXACT ORIGINAL LOGIC)
        beta1_arc = Angle(
            neg_u_arrow, 
            Vr1_arrow, 
            radius=0.55, 
            color=PURPLE_B,
            other_angle=False
        )
        beta1_label = MathTex(r"\beta_1", font_size=30, color=PURPLE_B).next_to(
            beta1_arc, LEFT, buff=0.12
        )
        
        self.play(Create(alpha1_arc), Write(alpha1_label))
        self.wait(0.5)
        self.play(Create(beta1_arc), Write(beta1_label))
        self.wait(1.5)
        
        # Add title
        title = Text("Inlet Velocity Triangle", font_size=36, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(2)
        
        # Zoom back out
        self.play(
            self.camera.frame.animate.scale(3.5).move_to(ORIGIN),
            FadeOut(title),
            run_time=2
        )
        self.wait(2)