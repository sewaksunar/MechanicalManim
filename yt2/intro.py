"""
Rectilinear Motion — Manim animation
Covers: displacement, average vs instantaneous velocity, and acceleration.
"""

from manim import *


class  RectilinearMotion(Scene):
    def construct(self):
        self._build_diagram()
        self._show_velocity_equations()
        self._show_acceleration_equations()

    # ------------------------------------------------------------------ #
    #  Section 1 – Diagram                                                #
    # ------------------------------------------------------------------ #

    def _build_diagram(self) -> None:
        """Draw the number line, label the origin, and animate the particle."""

        # --- number line ---
        line = Line(LEFT * 3, RIGHT * 3, color=WHITE)

        # --- origin ---
        origin_dot = Dot(ORIGIN, color=RED)
        origin_label = MathTex("O", font_size=24).next_to(origin_dot, UP)

        # --- axis end labels ---
        minus_s = MathTex("-s", font_size=24).next_to(line.get_start(), LEFT)
        plus_s = MathTex("s", font_size=24).next_to(line.get_end(), RIGHT)

        self.add(origin_dot, origin_label)
        self.play(FadeIn(line))
        self.add(minus_s, plus_s)
        self.wait()

        # --- initial position P at t = t ---
        initial_dot = Dot(RIGHT * 1.5, color=BLUE)
        init_pos_label = MathTex("P", font_size=24).next_to(initial_dot, UP)
        init_time_label = (
            MathTex(r"\text{at }t = t", font_size=24)
            .next_to(init_pos_label, UP)          # BUG FIX: use the Mobject, not .get_center()
        )

        # FIX: particle must be shown before it can be animated
        self.play(
            FadeIn(initial_dot),
            FadeIn(init_pos_label),
            FadeIn(init_time_label),
        )

        # --- displacement arrow from O to P ---
        dim_arrow = Arrow(ORIGIN, initial_dot.get_center(), buff=0, color=YELLOW)
        dim_label = MathTex("s", font_size=24).next_to(dim_arrow, DOWN)
        self.play(GrowArrow(dim_arrow), FadeIn(dim_label))
        self.wait()

        # --- move particle to P' ---
        # Use a separate, visible particle dot that we actually animate
        particle = initial_dot.copy().set_color(BLUE)
        self.add(particle)
        self.play(
            particle.animate.move_to(initial_dot.get_center() + RIGHT * 0.5),
            run_time=2,
            rate_func=smooth,
        )

        final_dot = particle.copy()
        label_final = MathTex("P'", font_size=24).next_to(final_dot, UP)
        self.play(FadeIn(final_dot), FadeIn(label_final))

        # --- Δs arrow ---
        delta_arrow = Arrow(
            initial_dot.get_center(), final_dot.get_center(), buff=0, color=GREEN
        )
        self.play(GrowArrow(delta_arrow))
        self.wait()

        displacement_label = MathTex(r"\Delta s", font_size=24).next_to(delta_arrow, DOWN)
        change_time_label = (
            MathTex(r"\text{in } \Delta t", font_size=24)
            .next_to(displacement_label, DOWN)    # BUG FIX: use the Mobject, not .get_center()
        )
        self.play(FadeIn(displacement_label), FadeIn(change_time_label))

        # --- tidy up: remove the free particle dot, push diagram to top ---
        self.remove(particle)
        self.diagram_group = VGroup(
            line, origin_dot, origin_label, minus_s, plus_s,
            initial_dot, init_pos_label, init_time_label,
            dim_arrow, dim_label,
            final_dot, label_final,
            delta_arrow, displacement_label, change_time_label,
        )
        self.play(self.diagram_group.animate.to_edge(UP), run_time=2)

    # ------------------------------------------------------------------ #
    #  Section 2 – Velocity equations                                     #
    # ------------------------------------------------------------------ #

    def _show_velocity_equations(self) -> None:
        """Animate the step-by-step derivation of instantaneous velocity."""

        # Step 1 – average velocity
        vel_avg = MathTex(r"v", r"=", r"\frac{\Delta s}{\Delta t}", font_size=36)
        self.play(Write(vel_avg))

        # FIX: give the label enough screen time before fading
        avg_note = Tex("This is average velocity", font_size=30).next_to(vel_avg, DOWN)
        self.play(FadeIn(avg_note))
        self.wait(1.5)
        self.play(FadeOut(avg_note))

        # Step 2 – limit form
        vel_limit = MathTex(
            r"v", r"=", r"\lim_{\Delta t \to 0}", r"\frac{\Delta s}{\Delta t}",
            font_size=36,
        )
        self.play(TransformMatchingTex(vel_avg, vel_limit))
        self.wait(1.5)

        # Step 3 – Leibniz notation
        vel_deriv = MathTex(r"v", r"=", r"\frac{ds}{dt}", font_size=36)
        self.play(TransformMatchingTex(vel_limit, vel_deriv))
        self.wait(1.5)

        # Step 4 – dot notation
        vel_dot = MathTex(r"v", r"=", r"\frac{ds}{dt}", r"=", r"\dot{s}", font_size=36)
        self.play(TransformMatchingTex(vel_deriv, vel_dot))
        self.wait(2)

        # Box and pin to left
        box_vel = SurroundingRectangle(vel_dot, color=YELLOW, buff=0.2)
        self.play(Create(box_vel))
        self.eq1_group = VGroup(vel_dot, box_vel)
        self.wait()

    # ------------------------------------------------------------------ #
    #  Section 3 – Acceleration equations                                 #
    # ------------------------------------------------------------------ #

    def _show_acceleration_equations(self) -> None:
        """Animate the step-by-step derivation of instantaneous acceleration."""

        # Step 1 – average acceleration, positioned below eq1_group
        acc_avg = MathTex(r"a", r"=", r"\frac{\Delta v}{\Delta t}", font_size=36).next_to(self.eq1_group, DOWN, buff=1)
        self.play(Write(acc_avg))

        avg_note = Tex("This is average acceleration", font_size=30).next_to(acc_avg, DOWN)
        self.play(FadeIn(avg_note))
        self.wait(1.5)
        self.play(FadeOut(avg_note))

        # Step 2 – limit form
        acc_limit = MathTex(
            r"a", r"=", r"\lim_{\Delta t \to 0}", r"\frac{\Delta v}{\Delta t}",
            font_size=36,
        ).next_to(self.eq1_group, DOWN, buff=1)
        self.play(TransformMatchingTex(acc_avg, acc_limit))
        self.wait(1.5)

        # Step 3 – Leibniz notation
        acc_deriv = MathTex(r"a", r"=", r"\frac{dv}{dt}", font_size=36).next_to(self.eq1_group, DOWN, buff=1)
        self.play(TransformMatchingTex(acc_limit, acc_deriv))
        self.wait(1.5)

        # Step 4 – dot notation
        acc_vel_dot = MathTex(r"a", r"=", r"\frac{dv}{dt}", r"=", r"\dot{v}", r"=", r"\frac{d^2s}{dt^2}", r"=", r"\ddot{s}", font_size=36).next_to(self.eq1_group, DOWN, buff=1)
        self.play(TransformMatchingTex(acc_deriv, acc_vel_dot))
        self.wait(2)
        
        group_acc = VGroup(acc_vel_dot)
        box_acc = SurroundingRectangle(group_acc, color=YELLOW, buff=0.2)
        self.play(Create(box_acc))

class GraphicalInterpretations(Scene):
    def construct(self):
    # # key eqn on top
    #     vel = MathTex(r"v", r"=", r"\frac{ds}{dt}", r"=", r"\dot{s}", font_size=36)
    #     box_vel = SurroundingRectangle(vel, color=YELLOW, buff=0.2)
    #     eq1_group = VGroup(vel, box_vel).to_edge(UP)

    #     acc = MathTex(r"a", r"=", r"\frac{dv}{dt}", r"=", r"\dot{v}", r"=", r"\frac{d^2s}{dt^2}", r"=", r"\ddot{s}", font_size=36)
    #     box_acc = SurroundingRectangle(acc, color=YELLOW, buff=0.2)
    #     eq2_group = VGroup(acc, box_acc).next_to(eq1_group, DOWN, buff=1)
    #     eq = VGroup(eq1_group, eq2_group).arrange(LEFT*2, aligned_edge=LEFT).to_edge(UP)
    #     self.add(eq)


        self._s_vs_t_graph()

        self._v_vs_t_graph()

    def _s_vs_t_graph(self) -> None:
        """Animate a position vs time graph, showing how velocity and acceleration relate to the curve."""
        
        # --- PHASE 1: Axes and Curve Setup ---
        t_max, t_min = 10, 0
        axes_s_t = Axes(
            x_range=[t_min, t_max, 2],
            y_range=[0, 6, 2],
            x_length=6,
            y_length=4,
            axis_config={"color": WHITE, "include_tip": True, "tip_length": 0.1},
        )
        # axes_s_t.add_coordinates()
        s_t_label = axes_s_t.get_axis_labels(x_label="t", y_label="s")
        
        self.play(Create(axes_s_t), Write(s_t_label))
        self.wait()

        def s_t_func(t):
            return 43*t**5/38400 - 9*t**4/320 + 469*t**3/1920 - 13*t**2/16 + 211*t/200 + 6/5

        s_t_curve = axes_s_t.plot(
            s_t_func,
            x_range=[0, 10],
            color=BLUE
        )

        
        self.play(Create(s_t_curve))

        # --- PHASE 2: Moving Dot and Tangent Exploration ---
        alpha_tracker = ValueTracker(0.1)

        dotP = always_redraw(
            lambda: Dot(
                axes_s_t.c2p(
                    t_min + alpha_tracker.get_value() * (t_max - t_min),
                    s_t_func(t_min + alpha_tracker.get_value() * (t_max - t_min)),
                ),
                color=RED,
            )
        )
        labelP = always_redraw(lambda: MathTex("P", font_size=24).next_to(dotP, UP))
        self.add(dotP, labelP)
        
        # Slope line exploration
        slope_line = always_redraw(
            lambda: TangentLine(
                s_t_curve,
                alpha=max(0.001, min(0.999, alpha_tracker.get_value())),
                length=4,
                color=BLUE_D,
            )
        )
        self.add(slope_line)
        self.play(alpha_tracker.animate.set_value(0.9), rate_func=linear, run_time=4)
        self.play(alpha_tracker.animate.set_value(0.8), rate_func=linear, run_time=1)
        self.wait()
        self.remove(slope_line)

        # --- PHASE 3: The Secant to Tangent Limit ---
        alpha_base = alpha_tracker.get_value()  # Dynamically link to where the tracker stopped
        dt_tracker = ValueTracker(0.15) 
        
        # Calculate moving point dynamically with a safety clamp to prevent out-of-bounds crashes
        def get_p2():
            clamped_alpha = min(0.999, alpha_base + dt_tracker.get_value())
            return s_t_curve.point_from_proportion(clamped_alpha)

        # Define all dynamic geometries
        chord_line = always_redraw(lambda: Line(dotP.get_center(), get_p2(), color=YELLOW, stroke_width=4))

        h_line_ele = always_redraw(lambda: DashedLine(
            start=dotP.get_center(),
            end=[get_p2()[0], dotP.get_center()[1], 0],
            color=YELLOW
        ))
        
        v_line_ele = always_redraw(lambda: DashedLine(
            start=[get_p2()[0], dotP.get_center()[1], 0],
            end=get_p2(),
            color=YELLOW
        ))

        # Dynamic braces and labels
        h_brace = always_redraw(lambda: Brace(h_line_ele, direction=DOWN, color=YELLOW))
        h_label = MathTex(r"\Delta t", font_size=24)
        h_label.add_updater(lambda m: m.next_to(h_brace, DOWN, buff=0.1))

        v_brace = always_redraw(lambda: Brace(v_line_ele, direction=RIGHT, color=YELLOW))
        v_label = MathTex(r"\Delta s", font_size=24)
        v_label.add_updater(lambda m: m.next_to(v_brace, RIGHT, buff=0.1))

        p_prime_label = MathTex(r"P'", font_size=24, color=YELLOW)
        p_prime_label.add_updater(lambda m: m.move_to(get_p2() + UP * 0.25))

        p_prime_dot = always_redraw(lambda: Dot(get_p2(), color=YELLOW))


        # Play Phase 3 Initial Animations``
        self.play(Flash(dotP.get_center(), color=YELLOW, line_length=0.2, num_lines=8))
        self.play(Create(chord_line))
        self.wait()
        self.play(Flash(get_p2(), color=YELLOW, line_length=0.2, num_lines=8), Create(p_prime_dot))
        self.wait()
        self.play(Write(p_prime_label))
        self.wait()
        self.play(
            Create(h_line_ele), Create(h_brace), Write(h_label),
            Create(v_line_ele), Create(v_brace), Write(v_label)
            
        )
        self.wait(0.5)

        # Show slope formula
        slope_formula = MathTex(r"\text{slope}", r"=", r"\frac{\Delta s}{\Delta t}", font_size=30).next_to(axes_s_t, RIGHT, buff=1)
        self.play(Write(slope_formula))
        self.wait(0.5)

        # Shrink the interval (Limit as dt -> 0)
        self.play(dt_tracker.animate.set_value(0.00001), rate_func=linear, run_time=3)
        self.wait(0.2)

        # IMPORTANT: Clear updaters before fading to prevent invisible objects from processing/crashing
        h_label.clear_updaters()
        v_label.clear_updaters()
        p_prime_label.clear_updaters()

        # The Final Replacement
        tangent_line = TangentLine(s_t_curve, alpha=alpha_base, length=3.0, color=RED)

        self.play(
            FadeOut(h_line_ele), FadeOut(h_brace), FadeOut(h_label),
            FadeOut(v_line_ele), FadeOut(v_brace), FadeOut(v_label),
            FadeOut(p_prime_label), FadeOut(p_prime_dot),
            ReplacementTransform(chord_line, tangent_line),
            run_time=1
        )
        slope_formula_dif = MathTex(r"\text{slope}", r"=", r"v", r"=", r"\frac{ds}{dt}", font_size=30).next_to(axes_s_t, RIGHT, buff=1)
        self.play(TransformMatchingTex(slope_formula, slope_formula_dif))
        self.wait()

        self.remove(slope_formula_dif, tangent_line, dotP, labelP)

        self.wait(2)

    ### integration of ds to get displacement between two times
        t1 = 2.1
        t2 = 5.8
        
        l_vertical = DashedLine(
            start=axes_s_t.c2p(t1, 0, 0),
            end=axes_s_t.c2p(t1, s_t_func(t1), 0),
            color=GREEN
        )
        r_vertical = DashedLine(
            start=axes_s_t.c2p(t2, 0, 0),
            end=axes_s_t.c2p(t2, s_t_func(t2), 0),
            color=GREEN
        )

        label_t1 = MathTex(r"t_1", font_size=24).next_to(axes_s_t.c2p(t1, 0, 0), DOWN)
        label_t2 = MathTex(r"t_2", font_size=24).next_to(axes_s_t.c2p(t2, 0, 0), DOWN)
        self.play(Succession(Write(label_t1), Create(l_vertical), Write(label_t2), Create(r_vertical)))

        l_horizontal = DashedLine(
            start=axes_s_t.c2p(0, s_t_func(t1), 0),
            end=axes_s_t.c2p(t1, s_t_func(t1), 0),
            color=GREEN
        )

        r_horizontal = DashedLine(
            start=axes_s_t.c2p(0, s_t_func(t2), 0),
            end=axes_s_t.c2p(t2, s_t_func(t2), 0),
            color=GREEN
        )
        label_s1 = MathTex(r"s(t_1)", font_size=24).next_to(axes_s_t.c2p(0, s_t_func(t1), 0), LEFT)
        label_s2 = MathTex(r"s(t_2)", font_size=24).next_to(axes_s_t.c2p(0, s_t_func(t2), 0), LEFT)

        self.play(Succession(Create(l_horizontal), Create(r_horizontal), Write(label_s1), Write(label_s2)))

        group = VGroup(axes_s_t, s_t_label, s_t_curve, l_vertical, r_vertical, label_t1, label_t2, l_horizontal, r_horizontal, label_s1, label_s2)
        self.play(group.animate.move_to(LEFT * 3), run_time=2)

        # left calculation comumn
        # displacemnt 
        dis_eqn = MathTex(r"\Delta s", r"=", r"s(t_2) - s(t_1)", font_size=30).next_to(group, RIGHT, buff=1)
        self.play(Write(dis_eqn))
        self.remove(group, dis_eqn)
        global group_vel 
        group_vel= group.copy()

    def _v_vs_t_graph(self) -> None:
        """Animate a velocity vs time graph, showing how acceleration relates to the curve."""
        
        v_vs_t_axes = Axes(
            x_range=[0, 10, 2],
            y_range=[-1, 2, 1],
            x_length=6,
            y_length=4,
            axis_config={"color": WHITE, "include_tip": True, "tip_length": 0.1},
        )
        v_vs_t_label = v_vs_t_axes.get_axis_labels(x_label="t", y_label="v")
        self.play(Create(v_vs_t_axes), Write(v_vs_t_label))
        def v_t_func(t):
            return 215*t**4/38400 - 9*t**3/80 + 1407*t**2/1920 - 13*t/8 + 211/200

        v_t_curve = v_vs_t_axes.plot(
            v_t_func,
            x_range=[0, 10],
            color=BLUE
        )
        self.play(Create(v_t_curve))
        self.wait(2)

        t1 = 2.1
        t2 = 5.8
        l_vertical = DashedLine(
            start=v_vs_t_axes.c2p(t1, 0, 0),
            end=v_vs_t_axes.c2p(t1, v_t_func(t1), 0),
            color=GREEN
        )
        r_vertical = DashedLine(
            start=v_vs_t_axes.c2p(t2, 0, 0),
            end=v_vs_t_axes.c2p(t2, v_t_func(t2), 0),
            color=GREEN
        )
        label_t1 = MathTex(r"t_1", font_size=24).next_to(v_vs_t_axes.c2p(t1, 0, 0), DOWN)
        label_t2 = MathTex(r"t_2", font_size=24).next_to(v_vs_t_axes.c2p(t2, 0, 0), DOWN)
        self.play(Succession(Write(label_t1), Create(l_vertical), Write(label_t2), Create(r_vertical)))
        l_horizontal = DashedLine(
            start=v_vs_t_axes.c2p(0, v_t_func(t1), 0),
            end=v_vs_t_axes.c2p(t1, v_t_func(t1), 0),
            color=GREEN
        )
        r_horizontal = DashedLine(
            start=v_vs_t_axes.c2p(0, v_t_func(t2), 0),
            end=v_vs_t_axes.c2p(t2, v_t_func(t2), 0),
            color=GREEN
        )
        label_v1 = MathTex(r"v(t_1)", font_size=24).next_to(v_vs_t_axes.c2p(0, v_t_func(t1), 0), LEFT)
        label_v2 = MathTex(r"v(t_2)", font_size=24).next_to(v_vs_t_axes.c2p(0, v_t_func(t2), 0), LEFT)

        self.play(Succession(Create(l_horizontal), Create(r_horizontal), Write(label_v1), Write(label_v2)))

        group = VGroup(v_vs_t_axes, v_vs_t_label, v_t_curve, l_vertical, r_vertical, label_t1, label_t2, l_horizontal, r_horizontal, label_v1, label_v2)
        self.play(group.animate.move_to(LEFT * 3), run_time=2)

        # dis calculation
        dis_eqn_deno = MathTex(r"\Delta s", r"=", r"s(t_2) - s(t_1)", font_size=30).next_to(group, RIGHT+UP, buff=1)
        self.play(Write(dis_eqn_deno))

        dis_eqn = MathTex(r"v", r"=", r"\frac{\d s}{\d t}", font_size=30).next_to(dis_eqn_deno, buff=0.5)
        self.play(Write(dis_eqn_deno))
        self.play(TransformMatchingTex(dis_eqn_deno, dis_eqn))

        diff_dis_vel_eqn = MathTex(r"ds", r"=", r"v dt", font_size=30).next_to(dis_eqn, DOWN, buff=0.5)
        self.play(TransformMatchingTex(dis_eqn, diff_dis_vel_eqn))

        # total displacement
        dis = MathTex(r"\Delta s", r"=", r"\int_{t_1}^{t_2} v(t) dt", font_size=30).next_to(diff_dis_vel_eqn, DOWN, buff=0.5)
        self.play(Write(dis))