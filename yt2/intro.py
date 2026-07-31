"""
Rectilinear Motion — Manim animation
Covers: displacement, average vs instantaneous velocity, and acceleration.
"""

from manim import *


class RectilinearMotion(Scene):
    """Narrative intro for 1D motion equations before graph-based interpretation."""

    def construct(self):
        """Render diagram first, then velocity and acceleration derivations."""
        self._build_diagram()
        self._show_velocity_equations()
        self._show_acceleration_equations()

    # ------------------------------------------------------------------ #
    # Section 1 – Diagram                                                #
    # ------------------------------------------------------------------ #

    def _build_diagram(self) -> None:
        """Draw the number line, label the origin, and animate the particle."""
        # --- Number Line Base ---
        number_line = Line(LEFT * 3, RIGHT * 3, color=WHITE)

        # --- Origin Markers ---
        origin_dot = Dot(ORIGIN, color=RED)
        origin_label = MathTex("O", font_size=24).next_to(origin_dot, UP)

        # --- Axis Boundaries ---
        left_extent_label = MathTex("-s", font_size=24).next_to(number_line.get_start(), LEFT)
        right_extent_label = MathTex("s", font_size=24).next_to(number_line.get_end(), RIGHT)

        self.add(origin_dot, origin_label)
        self.play(FadeIn(number_line))
        self.add(left_extent_label, right_extent_label)
        self.wait()

        # --- Initial Position P at t = t ---
        init_pos_marker = Dot(RIGHT * 1.5, color=BLUE)
        init_pos_label = MathTex("P", font_size=24).next_to(init_pos_marker, UP)
        init_time_label = MathTex(r"\text{at }t = t", font_size=24).next_to(init_pos_label, UP)

        self.play(
            FadeIn(init_pos_marker),
            FadeIn(init_pos_label),
            FadeIn(init_time_label),
        )

        # --- Displacement Arrow (O to P) ---
        origin_to_init_arrow = Arrow(ORIGIN, init_pos_marker.get_center(), buff=0, color=YELLOW)
        origin_to_init_label = MathTex("s", font_size=24).next_to(origin_to_init_arrow, DOWN)
        self.play(GrowArrow(origin_to_init_arrow), FadeIn(origin_to_init_label))
        self.wait()

        # --- Particle Motion to P' ---
        animated_particle = init_pos_marker.copy().set_color(BLUE)
        self.add(animated_particle)
        self.play(
            animated_particle.animate.move_to(init_pos_marker.get_center() + RIGHT * 0.5),
            run_time=2,
            rate_func=smooth,
        )

        final_pos_marker = animated_particle.copy()
        final_pos_label = MathTex("P'", font_size=24).next_to(final_pos_marker, UP)
        self.play(FadeIn(final_pos_marker), FadeIn(final_pos_label))

        # --- Delta s Displacement Arrow ---
        delta_s_arrow = Arrow(
            init_pos_marker.get_center(), final_pos_marker.get_center(), buff=0, color=GREEN
        )
        self.play(GrowArrow(delta_s_arrow))
        self.wait()

        delta_s_label = MathTex(r"\Delta s", font_size=24).next_to(delta_s_arrow, DOWN)
        delta_t_label = MathTex(r"\text{in } \Delta t", font_size=24).next_to(delta_s_label, DOWN)
        self.play(FadeIn(delta_s_label), FadeIn(delta_t_label))

        # --- Cleanup & Reposition Group to Top ---
        self.remove(animated_particle)
        self.diagram_group = VGroup(
            number_line, origin_dot, origin_label, left_extent_label, right_extent_label,
            init_pos_marker, init_pos_label, init_time_label,
            origin_to_init_arrow, origin_to_init_label,
            final_pos_marker, final_pos_label,
            delta_s_arrow, delta_s_label, delta_t_label,
        )
        self.play(self.diagram_group.animate.to_edge(UP), run_time=2)

    # ------------------------------------------------------------------ #
    # Section 2 – Velocity Equations                                     #
    # ------------------------------------------------------------------ #

    def _show_velocity_equations(self) -> None:
        """Animate the step-by-step derivation of instantaneous velocity."""
        # Step 1: Average Velocity
        vel_avg_eq = MathTex(r"v", r"=", r"\frac{\Delta s}{\Delta t}", font_size=36)
        self.play(Write(vel_avg_eq))

        vel_avg_note = Tex("This is average velocity", font_size=30).next_to(vel_avg_eq, DOWN*1.5)
        self.play(FadeIn(vel_avg_note))
        self.wait(1.5)
        self.play(FadeOut(vel_avg_note))

        # Step 2: Calculus Limit Form
        vel_lim_eq = MathTex(r"v", r"=", r"\lim_{\Delta t \to 0}", r"\frac{\Delta s}{\Delta t}", font_size=36)
        self.play(TransformMatchingTex(vel_avg_eq, vel_lim_eq))
        self.wait(1.5)

        # Step 3: Leibniz Derivative Notation
        vel_deriv_eq = MathTex(r"v", r"=", r"\frac{ds}{dt}", font_size=36)
        self.play(TransformMatchingTex(vel_lim_eq, vel_deriv_eq))
        self.wait(1.5)

        # Step 4: Dot Notation Variant
        vel_dot_eq = MathTex(r"v", r"=", r"\frac{ds}{dt}", r"=", r"\dot{s}", font_size=36)
        self.play(TransformMatchingTex(vel_deriv_eq, vel_dot_eq))
        self.wait(2)

        # Box and Group Expression
        vel_box = SurroundingRectangle(vel_dot_eq, color=YELLOW, buff=0.2)
        self.play(Create(vel_box))
        self.velocity_eq_group = VGroup(vel_dot_eq, vel_box)
        self.wait()

    # ------------------------------------------------------------------ #
    # Section 3 – Acceleration Equations                                 #
    # ------------------------------------------------------------------ #

    def _show_acceleration_equations(self) -> None:
        """Animate the step-by-step derivation of instantaneous acceleration."""
        # Step 1: Average Acceleration
        acc_avg_eq = MathTex(r"a", r"=", r"\frac{\Delta v}{\Delta t}", font_size=36).next_to(self.velocity_eq_group, DOWN, buff=1)
        self.play(Write(acc_avg_eq))

        acc_avg_note = Tex("This is average acceleration", font_size=30).next_to(acc_avg_eq, DOWN*1.5)
        self.play(FadeIn(acc_avg_note))
        self.wait(1.5)
        self.play(FadeOut(acc_avg_note))

        # Step 2: Calculus Limit Form
        acc_lim_eq = MathTex(r"a", r"=", r"\lim_{\Delta t \to 0}", r"\frac{\Delta v}{\Delta t}", font_size=36).next_to(self.velocity_eq_group, DOWN, buff=1)
        self.play(TransformMatchingTex(acc_avg_eq, acc_lim_eq))
        self.wait(1.5)

        # Step 3: Leibniz Derivative Notation
        acc_deriv_eq = MathTex(r"a", r"=", r"\frac{dv}{dt}", font_size=36).next_to(self.velocity_eq_group, DOWN, buff=1)
        self.play(TransformMatchingTex(acc_lim_eq, acc_deriv_eq))
        self.wait(1.5)

        # Step 4: Higher-order Dot Notation
        acc_dot_eq = MathTex(r"a", r"=", r"\frac{dv}{dt}", r"=", r"\dot{v}", r"=", r"\frac{d^2s}{dt^2}", r"=", r"\ddot{s}", font_size=36).next_to(self.velocity_eq_group, DOWN, buff=1)
        self.play(TransformMatchingTex(acc_deriv_eq, acc_dot_eq))
        self.wait(2)

        acc_box = SurroundingRectangle(acc_dot_eq, color=YELLOW, buff=0.2)
        self.play(Create(acc_box))
        self.wait(2)


class GraphicalInterpretations(Scene):
    """Visual interpretation of derivatives and integrals on kinematic curves."""

    def construct(self):
        """Render the graphical interpretation sequence cleanly."""
        # Initialize instance tracking properties safely
        self.displacement_graph_group = None
        self.velocity_graph_group = None

        self._s_vs_t_graph()
        self._v_vs_t_graph()
        self._a_vs_t_graph()

    # ------------------------------------------------------------------ #
    # Math Kinematic Functions                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _position_function(t: float) -> float:
        return 43 * t**5 / 38400 - 9 * t**4 / 320 + 469 * t**3 / 1920 - 13 * t**2 / 16 + 211 * t / 200 + 6 / 5

    @staticmethod
    def _velocity_function(t: float) -> float:
        return 215 * t**4 / 38400 - 9 * t**3 / 80 + 1407 * t**2 / 1920 - 13 * t / 8 + 211 / 200

    @staticmethod
    def _acceleration_function(t: float) -> float:
        return 43 * t**3 / 1920 - 27 * t**2 / 80 + 1407 * t / 960 - 13 / 8

    # ------------------------------------------------------------------ #
    # Layout Utility Helpers                                             #
    # ------------------------------------------------------------------ #

    def _build_projection_guides(
        self,
        axes: Axes,
        y_function,
        t1: float,
        t2: float,
        y1_label_tex: str,
        y2_label_tex: str,
        time_label_direction=DOWN,
    ):
        """Create reference coordinates and projection lines at specific time frames."""
        v_line_t1 = DashedLine(start=axes.c2p(t1, 0, 0), end=axes.c2p(t1, y_function(t1), 0), color=GREEN)
        v_line_t2 = DashedLine(start=axes.c2p(t2, 0, 0), end=axes.c2p(t2, y_function(t2), 0), color=GREEN)
        label_t1 = MathTex(r"t_1", font_size=24).next_to(axes.c2p(t1, 0, 0), time_label_direction)
        label_t2 = MathTex(r"t_2", font_size=24).next_to(axes.c2p(t2, 0, 0), time_label_direction)

        self.play(
            Succession(
                Write(label_t1),
                Create(v_line_t1),
                Write(label_t2),
                Create(v_line_t2),
            )
        )

        h_line_y1 = DashedLine(start=axes.c2p(0, y_function(t1), 0), end=axes.c2p(t1, y_function(t1), 0), color=GREEN)
        h_line_y2 = DashedLine(start=axes.c2p(0, y_function(t2), 0), end=axes.c2p(t2, y_function(t2), 0), color=GREEN)
        y1_label = MathTex(y1_label_tex, font_size=24).next_to(axes.c2p(0, y_function(t1), 0), LEFT)
        y2_label = MathTex(y2_label_tex, font_size=24).next_to(axes.c2p(0, y_function(t2), 0), LEFT)

        self.play(
            Succession(
                Create(h_line_y1),
                Create(h_line_y2),
                Write(y1_label),
                Write(y2_label),
            )
        )

        return (v_line_t1, v_line_t2, label_t1, label_t2, h_line_y1, h_line_y2, y1_label, y2_label)

    def _create_styled_axes(self, x_range, y_range, y_length=4):
        """Create a consistent styled axes object for the kinematic graphs."""
        return Axes(
            x_range=x_range,
            y_range=y_range,
            x_length=6,
            y_length=y_length,
            axis_config={"color": WHITE, "include_tip": True, "tip_length": 0.1},
        )

    # ------------------------------------------------------------------ #
    # Section 4 – Position Curve Interpretation                          #
    # ------------------------------------------------------------------ #

    def _s_vs_t_graph(self) -> None:
        """Animate position vs time graph: transitioning from a secant line to a tangent."""
        axes_st = Axes(
            x_range=[0, 10, 2],
            y_range=[0, 6, 2],
            x_length=6,
            y_length=4,
            axis_config={"color": WHITE, "include_tip": True, "tip_length": 0.1},
        )
        labels_st = axes_st.get_axis_labels(x_label="t", y_label="s")
        self.play(Create(axes_st), Write(labels_st))

        curve_st = axes_st.plot(self._position_function, x_range=[0, 10], color=BLUE)
        curve_st_label = MathTex("s(t)", font_size=24).next_to(curve_st.get_end(), UP)
        self.play(Create(curve_st), FadeIn(curve_st_label))
        self.wait()

        # Show displacement between two times on s(t) before the slope interpretation.
        t1, t2 = 0.5, 5.8
        (
            left_v_line,
            right_v_line,
            label_t1,
            label_t2,
            left_h_line,
            right_h_line,
            label_s1,
            label_s2,
        ) = self._build_projection_guides(
            axes=axes_st,
            y_function=self._position_function,
            t1=t1,
            t2=t2,
            y1_label_tex=r"s(t_1)",
            y2_label_tex=r"s(t_2)",
            time_label_direction=DOWN,
        )

        s1_point = axes_st.c2p(0, self._position_function(t1), 0)
        s2_point = axes_st.c2p(0, self._position_function(t2), 0)
        delta_s_axis = DashedLine(start=s1_point, end=s2_point, color=YELLOW)
        delta_s_brace = Brace(delta_s_axis, direction=RIGHT, color=YELLOW)
        delta_s_label = MathTex(r"\Delta s", font_size=24).next_to(delta_s_brace, RIGHT, buff=0.1)

        self.play(Create(delta_s_axis), Create(delta_s_brace), Write(delta_s_label))

        delta_s_eq_display = MathTex(r"\Delta s", r"=", r"s(t_2)", r"-", r"s(t_1)" , font_size=30).next_to(axes_st, RIGHT, buff=1)
        self.play(Write(delta_s_eq_display))
        self.wait()
        box_delta_s_eq = SurroundingRectangle(delta_s_eq_display, color=YELLOW, buff=0.2)
        self.play(Create(box_delta_s_eq))

        combined_delta_s_display = VGroup(delta_s_eq_display, box_delta_s_eq)
        self.play(combined_delta_s_display.animate.next_to(axes_st, DOWN, buff=0.5))
        
        self.remove(left_v_line, right_v_line, label_t1, label_t2, left_h_line, right_h_line, label_s1, label_s2, delta_s_axis, delta_s_brace, delta_s_label)


        #----------------
        # slope interpetaion setup
        #-----------------
        # Dynamic Point Trackers
        alpha_tracker = ValueTracker(0.15)
        dt_tracker = ValueTracker(0.25)

        get_p1 = lambda: curve_st.point_from_proportion(alpha_tracker.get_value())
        get_p2 = lambda: curve_st.point_from_proportion(min(0.999, alpha_tracker.get_value() + dt_tracker.get_value()))

        # Live Geometric Components
        marker_p1 = always_redraw(lambda: Dot(get_p1(), color=RED))
        label_p1 = always_redraw(lambda: MathTex("P", font_size=24).next_to(marker_p1, UP))
        marker_p2 = always_redraw(lambda: Dot(get_p2(), color=YELLOW))
        label_p2 = always_redraw(lambda: MathTex("P'", font_size=24, color=YELLOW).next_to(marker_p2, UP))

        secant_line = always_redraw(lambda: Line(get_p1(), get_p2(), color=YELLOW, stroke_width=4))

        # Projected Changes (Delta t / Delta s)
        line_dt = always_redraw(lambda: DashedLine(start=get_p1(), end=[get_p2()[0], get_p1()[1], 0], color=YELLOW))
        line_ds = always_redraw(lambda: DashedLine(start=[get_p2()[0], get_p1()[1], 0], end=get_p2(), color=YELLOW))

        brace_dt = always_redraw(lambda: Brace(line_dt, direction=DOWN, color=YELLOW))
        label_dt = always_redraw(lambda: MathTex(r"\Delta t", font_size=24).next_to(brace_dt, DOWN, buff=0.1))

        brace_ds = always_redraw(lambda: Brace(line_ds, direction=RIGHT, color=YELLOW))
        label_ds = always_redraw(lambda: MathTex(r"\Delta s", font_size=24).next_to(brace_ds, RIGHT, buff=0.1))

        self.play(Create(marker_p1), Write(label_p1))
        self.play(Create(marker_p2), Write(label_p2))
        self.play(Create(secant_line))
        self.wait()

        self.play(
            Create(line_dt), FadeIn(brace_dt), Write(label_dt),
            Create(line_ds), FadeIn(brace_ds), Write(label_ds)
        )
        self.wait(0.5)

        slope_eq = MathTex(r"\text{slope}", r"=", r"\frac{\Delta s}{\Delta t}", font_size=30).next_to(axes_st, RIGHT, buff=1)
        self.play(Write(slope_eq))
        self.wait(1)

        # Push Limit: dt -> 0
        self.play(dt_tracker.animate.set_value(0.001), rate_func=linear, run_time=3)
        self.wait(0.5)

        self.play(
            FadeOut(line_dt), FadeOut(brace_dt), FadeOut(label_dt),
            FadeOut(line_ds), FadeOut(brace_ds), FadeOut(label_ds),
            FadeOut(label_p2), FadeOut(marker_p2),
        )

        # Swap to Live Calculus Tangent Line
        live_tangent = always_redraw(
            lambda: TangentLine(curve_st, alpha=max(0.001, min(0.999, alpha_tracker.get_value())), length=4, color=RED)
        )
        self.play(ReplacementTransform(secant_line, live_tangent))

        slope_eq_diff = MathTex(r"\text{slope}", r"=", r"v", r"=", r"\frac{ds}{dt}", font_size=30).next_to(axes_st, RIGHT, buff=1)
        self.play(TransformMatchingTex(slope_eq, slope_eq_diff))
        self.wait(1)
        box_slope_eq = SurroundingRectangle(slope_eq_diff, color=YELLOW, buff=0.2)
        self.play(Create(box_slope_eq))

        # Sweep Tangent Across Domain
        self.play(alpha_tracker.animate.set_value(0.85), rate_func=smooth, run_time=4)
        self.play(alpha_tracker.animate.set_value(0.5), rate_func=smooth, run_time=2)
        self.wait()
        
        combo_slope_eq = VGroup(slope_eq_diff, box_slope_eq)

        self.play(
            combo_slope_eq.animate.move_to(axes_st.get_top() + UP * 0.5),
            FadeOut(live_tangent), FadeOut(marker_p1), FadeOut(label_p1)
        )

        # Save Configuration Struct as Instance State
        self.displacement_graph_group = VGroup(axes_st, labels_st, curve_st, curve_st_label, slope_eq_diff, combined_delta_s_display, combo_slope_eq)
        self.play(self.displacement_graph_group.animate.to_edge(LEFT).scale(0.8), run_time=2)
        self.wait()


    # ------------------------------------------------------------------ #
    # Section 5 – Velocity Curve Interpretation                          #
    # ------------------------------------------------------------------ #

    def _v_vs_t_graph(self) -> None:
        """Animate velocity vs time graph displaying acceleration derivatives and integrals."""
        axes_vt = self._create_styled_axes([0, 10, 2], [-0.2, 2, 1], y_length=4)
        axes_vt.next_to(self.displacement_graph_group, RIGHT, buff=1)

        labels_vt = axes_vt.get_axis_labels(
            x_label=MathTex("t").shift(DOWN * 0.2),
            y_label=MathTex("v").shift(LEFT * 0.2)
        )
        self.add(axes_vt, labels_vt)

        curve_vt = axes_vt.plot(self._velocity_function, x_range=[0, 10], color=BLUE)
        curve_vt_label = MathTex("v(t)", font_size=24).next_to(curve_vt.get_end(), UP)
        self.play(Create(curve_vt), FadeIn(curve_vt_label))
        self.wait(1)

        # Setup Dynamic Tracking Geometry
        alpha_tracker = ValueTracker(0.4)
        dt_tracker = ValueTracker(0.1)

        get_v_p1 = lambda: curve_vt.point_from_proportion(alpha_tracker.get_value())
        get_v_p2 = lambda: curve_vt.point_from_proportion(min(0.999, alpha_tracker.get_value() + dt_tracker.get_value()))

        marker_vp1 = always_redraw(lambda: Dot(get_v_p1(), color=RED))
        label_vp1 = always_redraw(lambda: MathTex("P", font_size=24).next_to(marker_vp1, UP))
        marker_vp2 = always_redraw(lambda: Dot(get_v_p2(), color=YELLOW))
        label_vp2 = always_redraw(lambda: MathTex("P'", font_size=24, color=YELLOW).next_to(marker_vp2, UP))

        secant_line_vt = always_redraw(lambda: Line(get_v_p1(), get_v_p2(), color=YELLOW, stroke_width=4))

        line_v_dt = always_redraw(lambda: DashedLine(start=get_v_p1(), end=[get_v_p2()[0], get_v_p1()[1], 0], color=YELLOW))
        line_v_dv = always_redraw(lambda: DashedLine(start=[get_v_p2()[0], get_v_p1()[1], 0], end=get_v_p2(), color=YELLOW))

        brace_v_dt = always_redraw(lambda: Brace(line_v_dt, direction=DOWN, color=YELLOW))
        label_v_dt = always_redraw(lambda: MathTex(r"\Delta t", font_size=24).next_to(brace_v_dt, DOWN, buff=0.1))

        brace_v_dv = always_redraw(lambda: Brace(line_v_dv, direction=RIGHT, color=YELLOW))
        label_v_dv = always_redraw(lambda: MathTex(r"\Delta v", font_size=24).next_to(brace_v_dv, RIGHT, buff=0.1))

        self.play(Create(marker_vp1), Write(label_vp1))
        self.play(Create(marker_vp2), Write(label_vp2))
        self.play(Create(secant_line_vt))
        self.wait()

        self.play(
            Create(line_v_dt), FadeIn(brace_v_dt), Write(label_v_dt),
            Create(line_v_dv), FadeIn(brace_v_dv), Write(label_v_dv)
        )
        self.wait(0.5)

        v_slope_eq = MathTex(r"\text{slope}", r"=", r"\frac{\Delta v}{\Delta t}", font_size=30).next_to(axes_vt, DOWN, buff=1)
        self.play(Write(v_slope_eq))
        self.wait(1)

        self.play(dt_tracker.animate.set_value(0.001), rate_func=linear, run_time=3)
        self.wait(0.5)

        self.play(
            FadeOut(line_v_dt), FadeOut(brace_v_dt), FadeOut(label_v_dt),
            FadeOut(line_v_dv), FadeOut(brace_v_dv), FadeOut(label_v_dv),
            FadeOut(label_vp2), FadeOut(marker_vp2)
        )

        live_tangent_vt = always_redraw(
            lambda: TangentLine(curve_vt, alpha=max(0.001, min(0.999, alpha_tracker.get_value())), length=4, color=RED)
        )
        self.play(ReplacementTransform(secant_line_vt, live_tangent_vt))

        v_slope_eq_diff = MathTex(r"\text{slope}", r"=", r"a", r"=", r"\frac{dv}{dt}", font_size=30).next_to(axes_vt, DOWN*0.5, buff=1)
        self.play(TransformMatchingTex(v_slope_eq, v_slope_eq_diff))
        self.wait(1)

        box_v_slope = SurroundingRectangle(v_slope_eq_diff, color=YELLOW, buff=0.2)
        self.play(Create(box_v_slope))

        self.play(alpha_tracker.animate.set_value(0.85), rate_func=smooth, run_time=4)
        self.play(alpha_tracker.animate.set_value(0.5), rate_func=smooth, run_time=2)
        self.wait()

        box_v_eq_combined = VGroup(box_v_slope, v_slope_eq_diff)
        self.play(
            FadeOut(live_tangent_vt), FadeOut(marker_vp1), FadeOut(label_vp1),
            box_v_eq_combined.animate.move_to(axes_vt.get_top() + UP * 0.5)
        )
        self.wait()

        # Integral Projections Area Sequence
        t1, t2 = 0.5, 5.8
        guides = self._build_projection_guides(
            axes=axes_vt, y_function=self._velocity_function, t1=t1, t2=t2,
            y1_label_tex=r"v(t_1)", y2_label_tex=r"v(t_2)"
        )

        self.velocity_graph_group = VGroup(axes_vt, labels_vt, curve_vt, curve_vt_label, box_v_eq_combined, *guides)
        self.play(self.velocity_graph_group.animate.to_edge(UP * 2, buff=.1).scale(0.8), run_time=2)

        vel_eq_base = MathTex(r"v", r"=", r"\frac{d s}{d t}", font_size=30).move_to(RIGHT * 3.5 + DOWN * 2)
        self.play(Write(vel_eq_base))

        diff_disp_eq = MathTex(r"ds", r"=", r"v dt", font_size=30).next_to(vel_eq_base, DOWN * 0, buff=1)
        self.play(TransformMatchingTex(vel_eq_base, diff_disp_eq), run_time=2)

        delta_s_eq = MathTex(r"\Delta s", r"=", r"\int_{t_1}^{t_2} v(t) dt", font_size=30).next_to(diff_disp_eq, DOWN * 0.5, buff=1)
        self.play(Write(delta_s_eq, run_time=2))

        box_delta_s = SurroundingRectangle(delta_s_eq, color=YELLOW, buff=0.2)
        self.play(Create(box_delta_s))
        self.wait(2)

        area_vt = axes_vt.get_area(curve_vt, x_range=[t1, t2], color=BLUE, opacity=0.5)
        self.remove(diff_disp_eq)

        text_area_vt = MathTex(r"\text{Area under } v(t) \text{ from } t_1 \text{ to } t_2 \text{ equals } \Delta s", font_size=24).move_to(box_delta_s.get_center() + UP )
        self.play(Write(text_area_vt), Swap(area_vt))
        self.wait(2)

        # Clear space on Left Edge for Area Grouping
        self.remove(self.displacement_graph_group)
        self.velocity_graph_group.add(area_vt, text_area_vt, delta_s_eq, box_delta_s)
        self.play(self.velocity_graph_group.animate.to_edge(LEFT).scale(0.8), run_time=2)
        self.wait()

    # ------------------------------------------------------------------ #
    # Section 6 – Acceleration Curve Interpretation                      #
    # ------------------------------------------------------------------ #

    def _a_vs_t_graph(self) -> None:
        """Animate acceleration vs time graph, detailing jerk and change in velocity integrations."""
        axes_at = self._create_styled_axes([0, 10, 2], [-2.5, 3, 1], y_length=4)
        
        if self.velocity_graph_group is not None:
            axes_at.next_to(self.velocity_graph_group, RIGHT, buff=1)
        else:
            axes_at.to_edge(RIGHT)

        labels_at = axes_at.get_axis_labels(
            x_label=MathTex("t").shift(UP * 0.2),
            y_label=MathTex("a").shift(LEFT * 0.2),
        )
        self.add(axes_at, labels_at)

        curve_at = axes_at.plot(self._acceleration_function, x_range=[0, 10], color=RED)
        curve_at_label = MathTex("a(t)", font_size=24).next_to(curve_at.get_end(), UP)
        self.play(Create(curve_at), FadeIn(curve_at_label))
        self.wait(1.5)

        # Acceleration slope/tangent analysis removed per request.
        # Proceed directly to the integration-area interpretation below.
        self.wait(0.5)


        # --- Integration Area Interpretation under a(t) ---
        t1, t2 = 0.5, 5.8
        guides = self._build_projection_guides(
            axes=axes_at, y_function=self._acceleration_function, t1=t1, t2=t2,
            y1_label_tex=r"a(t_1)", y2_label_tex=r"a(t_2)", time_label_direction=UP
        )

        acc_eq_base = MathTex(r"a", r"=", r"\frac{d v}{d t}", font_size=30).next_to(axes_at, -DOWN*1, buff=0.8)
        self.play(Write(acc_eq_base))

        diff_vel_eq = MathTex(r"dv", r"=", r"a dt", font_size=30).next_to(acc_eq_base, DOWN * 0, buff=1)
        self.play(TransformMatchingTex(acc_eq_base, diff_vel_eq), run_time=2)

        delta_v_eq = MathTex(r"\Delta v", r"=", r"\int_{t_1}^{t_2} a(t) dt", font_size=30).next_to(diff_vel_eq, DOWN * 1, buff=1)
        self.play(Write(delta_v_eq, run_time=2))

        box_delta_v = SurroundingRectangle(delta_v_eq, color=YELLOW, buff=0.2)
        self.play(Create(box_delta_v))
        self.wait(2)

        area_at = axes_at.get_area(curve_at, x_range=[t1, t2], color=RED, opacity=0.5)
        self.remove(diff_vel_eq)
        self.wait()

        text_area_at = MathTex(r"\text{Area under } a(t) \text{ from } t_1 \text{ to } t_2 \text{ equals } \Delta v", font_size=24).next_to(box_delta_v, UP, buff=0.4)
        self.play(Write(text_area_at), Swap(area_at))
        self.wait(3)

from manim import *

class AnalyticalIntegration(Scene):
    """Derive the three primary kinematic equations through symbolic definite integration."""
    
    def construct(self):
        # ---------------------------------------------------------
        # Derivation 1: v = v_0 + a*t
        # ---------------------------------------------------------
        eq1_base = MathTex("a", "=", r"\frac{dv}{dt}", font_size=34)
        eq1_rearranged = MathTex("dv", "=", "a", "dt", font_size=34)
        eq1_integrated = MathTex(r"\int_{v_0}^v", "dv", "=", r"\int_0^t", "a", "dt", font_size=34)
        eq1_eval = MathTex("v", "-", "v_0", "=", "a", "t", font_size=34)
        eq1_final = MathTex("v", "=", "v_0", "+", "a", "t", font_size=34)

        deriv_1_group = VGroup(eq1_base, eq1_rearranged, eq1_integrated, eq1_eval, eq1_final)
        deriv_1_group.arrange(DOWN, buff=0.45).to_edge(UP, buff=0.5)

        self.play(Write(eq1_base))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq1_base.copy(), eq1_rearranged))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq1_rearranged.copy(), eq1_integrated))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq1_integrated.copy(), eq1_eval))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq1_eval.copy(), eq1_final))
        self.wait(1.5)

        # Move first equation to top-left corner
        self.play(
            FadeOut(VGroup(eq1_base, eq1_rearranged, eq1_integrated, eq1_eval)),
            eq1_final.animate.to_corner(UL, buff=0.5)
        )
        self.wait(0.5)

        # ---------------------------------------------------------
        # Derivation 2: s = s_0 + v_0*t + 0.5*a*t^2 (NEW)
        # ---------------------------------------------------------
        eq2_base = MathTex("v", "=", r"\frac{ds}{dt}", font_size=34)
        eq2_rearranged = MathTex("ds", "=", "v", "dt", font_size=34)
        # Substitute v = v_0 + at
        eq2_subbed = MathTex("ds", "=", "(", "v_0", "+", "a", "t", ")", "dt", font_size=34)
        eq2_integrated = MathTex(r"\int_{s_0}^s", "ds", "=", r"\int_0^t", "(", "v_0", "+", "a", "t", ")", "dt", font_size=34)
        eq2_eval = MathTex("s", "-", "s_0", "=", "v_0", "t", "+", r"\frac{1}{2}", "a", "t^2", font_size=34)
        eq2_final = MathTex("s", "=", "s_0", "+", "v_0", "t", "+", r"\frac{1}{2}", "a", "t^2", font_size=34)

        deriv_2_group = VGroup(eq2_base, eq2_rearranged, eq2_subbed, eq2_integrated, eq2_eval, eq2_final)
        deriv_2_group.arrange(DOWN, buff=0.4).center()

        self.play(Write(eq2_base))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq2_base.copy(), eq2_rearranged))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq2_rearranged.copy(), eq2_subbed))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq2_subbed.copy(), eq2_integrated))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq2_integrated.copy(), eq2_eval))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq2_eval.copy(), eq2_final))
        self.wait(1.5)

        # Position second final equation directly under the first one
        self.play(
            FadeOut(VGroup(eq2_base, eq2_rearranged, eq2_subbed, eq2_integrated, eq2_eval)),
            eq2_final.animate.next_to(eq1_final, DOWN, buff=0.4, aligned_edge=LEFT)
        )
        self.wait(0.5)

        # ---------------------------------------------------------
        # Derivation 3: v^2 = v_0^2 + 2*a*(s - s_0)
        # ---------------------------------------------------------
        eq3_base = MathTex("a", "=", r"\frac{dv}{dt}", font_size=34)
        eq3_chain = MathTex("a", "=", r"\frac{dv}{ds}", r"\frac{ds}{dt}", font_size=34)
        eq3_subbed = MathTex("a", "=", r"\frac{dv}{ds}", "v", font_size=34)
        eq3_rearranged = MathTex("v", "dv", "=", "a", "ds", font_size=34)
        eq3_integrated = MathTex(r"\int_{v_0}^v", "v", "dv", "=", r"\int_{s_0}^s", "a", "ds", font_size=34)
        eq3_eval = MathTex(r"\frac{1}{2}v^2", "-", r"\frac{1}{2}v_0^2", "=", "a", "(s - s_0)", font_size=34)
        eq3_final = MathTex("v^2", "=", "v_0^2", "+", "2", "a", "(s - s_0)", font_size=34)

        deriv_3_group = VGroup(eq3_base, eq3_chain, eq3_subbed, eq3_rearranged, eq3_integrated, eq3_eval, eq3_final)
        deriv_3_group.arrange(DOWN, buff=0.4).center().shift(DOWN * 0.1)

        self.play(Write(eq3_base))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq3_base.copy(), eq3_chain))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq3_chain.copy(), eq3_subbed))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq3_subbed.copy(), eq3_rearranged))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq3_rearranged.copy(), eq3_integrated))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq3_integrated.copy(), eq3_eval))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq3_eval.copy(), eq3_final))
        self.wait(1.5)
        
        # Complete the sidebar list with the third equation
        self.play(
            FadeOut(VGroup(eq3_base, eq3_chain, eq3_subbed, eq3_rearranged, eq3_integrated, eq3_eval)),
            eq3_final.animate.next_to(eq2_final, DOWN, buff=0.4, aligned_edge=LEFT)
        )
        self.wait(2)

        box_eq1 = SurroundingRectangle(eq1_final, color=YELLOW, buff=0.2)
        box_eq2 = SurroundingRectangle(eq2_final, color=YELLOW, buff=0.2)
        box_eq3 = SurroundingRectangle(eq3_final, color=YELLOW, buff=0.2)
        self.play(Create(box_eq1), Create(box_eq2), Create(box_eq3))
        self.wait(3)

        group_equations = VGroup(VGroup(eq1_final, box_eq1), VGroup(eq2_final, box_eq2), VGroup(eq3_final, box_eq3)).move_to(ORIGIN).arrange(LEFT, buff=0.5)
        self.play(group_equations.animate.move_to(ORIGIN).arrange(LEFT, buff=0.5), run_time=4)
        self.wait(3)

#-----------------
# interpolation of discreate displacement points
#-----------------
from manim import *
import numpy as np

class DiscreteToContinuous(Scene):
    @staticmethod
    def _position_function(t: float) -> float:
        return 43 * t**5 / 38400 - 9 * t**4 / 320 + 469 * t**3 / 1920 - 13 * t**2 / 16 + 211 * t / 200 + 6 / 5

    def construct(self):
        # 1. Setup Title
        table_title = Tex("Discrete to Continuous Data", font_size=36).to_edge(UP)
        self.play(Write(table_title))
        self.wait(0.5)

        # Sample discrete data points (time, displacement)
        t = np.array([0, 2, 4, 6, 8, 10])
        s = np.array([1.2, 1.6, 2.0, 3.3, 4.2, 5.5])

        # 2. Create and position the data table on the left side
        table_data = [["Time (s)", "Displacement (m)"]] + [[f"{t[i]:.1f}", f"{s[i]:.1f}"] for i in range(len(t))]
        
        table = Table(
            table_data, 
            include_outer_lines=True, 
            element_to_mobject_config={"font_size": 18}
        ).scale(0.65).to_edge(LEFT, buff=0.7).shift(DOWN * 0.2)
        
        # ---------------------------------------------------------
        # Custom Table Grid Styling (Inspired by your MathTable)
        # ---------------------------------------------------------
        # Color the top outer line and the header divider line BLUE
        table.get_horizontal_lines()[:2].set_color(BLUE)
        # Color all vertical grid lines BLUE
        table.get_vertical_lines().set_color(BLUE)
        
        # Elevate z-index layers to keep intersection rendering crisp
        table.get_horizontal_lines()[:2].set_z_index(1)
        table.get_vertical_lines().set_z_index(1)
        # ---------------------------------------------------------
        
        self.play(Create(table))
        self.wait(0.5)

        # 3. Setup Graph Coordinate System on the right side
        axes = Axes(
            x_range=[0, 10, 2],
            y_range=[0, 6, 2],
            x_length=6,
            y_length=4,
            axis_config={"color": WHITE, "include_tip": True, "tip_length": 0.1},
        ).to_edge(RIGHT, buff=0.7).shift(DOWN * 0.2)

        labels = axes.get_axis_labels(
            x_label=MathTex("t").shift(DOWN * 0.2),
            y_label=MathTex("s").shift(LEFT * 0.2)
        )

        self.play(Create(axes), Write(labels))
        self.wait(0.5)

        # 4. Generate discrete dots corresponding to the data points
        dots = VGroup(*[
            Dot(axes.c2p(t[i], s[i]), color=YELLOW, radius=0.07)
            for i in range(len(t))
        ])

        # Animate data transitioning from table rows into physical points on the graph
        self.play(
            LaggedStart(*[
                TransformFromCopy(table.get_rows()[i+1], dots[i]) 
                for i in range(len(t))
            ], lag_ratio=0.2),
            run_time=2
        )
        self.wait(1)

        # 5. Continuous Curve from the explicit s(t) function
        continuous_curve = axes.plot(
            self._position_function,
            x_range=[0, 10],
            color=BLUE,
        )
        curve_label = Tex("Continuous Model: $s(t)$", font_size=20, color=BLUE).next_to(axes, UP, buff=0.2)

        self.play(
            Create(continuous_curve), 
            Write(curve_label), 
            run_time=2
        )
        self.wait(2)