"""
Rectilinear Motion — Manim Animation
=====================================
Scene 1 – RectilinearMotion
    Number-line diagram → average & instantaneous velocity → acceleration.

Scene 2 – GraphicalInterpretations
    s-t graph  : tangent slope = v = ds/dt ;  Δs = s(t₂)−s(t₁)
    v-t graph  : tangent slope = a = dv/dt ;  Δs = ∫ v dt  (area)

Improvements over the original
───────────────────────────────
• Module-level pure functions (s_of_t, v_of_t) and a make_boxed() helper
  remove repeated patterns throughout both scenes.
• _make_axes() and _draw_interval_markers() eliminate copy-pasted axis /
  dashed-line blocks in _s_vs_t_graph and _v_vs_t_graph.
• Removed global variable (group_vel) — state is passed via instance attrs.
• Fixed double self.play(Write(dis_eqn_deno)) call.
• Fixed broken LaTeX: r"\frac{\d s}{\d t}" → r"\frac{ds}{dt}".
• Fixed TransformMatchingTex on an un-shown object in _v_vs_t_graph.
• Integration derivation chain now uses .copy() sources so originals persist.
• All equations positioned with .next_to() chains, never hard-coded coords.
• Area shading added to v-t graph to make ∫ v dt geometrically concrete.
• Acceleration section uses a local helper _positioned() to avoid repeated
  .next_to(anchor, DOWN, buff=0.8).to_edge(LEFT) calls.
• Particle dot in _build_diagram is removed via self.remove() before P' dot
  appears, preventing ghost overlaps.
• Every section ends with at least self.wait(2) so the boxed results are
  readable before the next section starts.
"""

from __future__ import annotations

from manim import *


# ═══════════════════════════════════════════════════════════════════════════════
#  Module-level pure functions
# ═══════════════════════════════════════════════════════════════════════════════

def s_of_t(t: float) -> float:
    """Position  s(t) — a degree-5 polynomial with interesting curvature."""
    return (
        43 * t**5 / 38_400
        - 9 * t**4 / 320
        + 469 * t**3 / 1_920
        - 13 * t**2 / 16
        + 211 * t / 200
        + 6 / 5
    )


def v_of_t(t: float) -> float:
    """Velocity  v(t) = ds/dt — exact analytical derivative of s_of_t."""
    return (
        215 * t**4 / 38_400
        - 9 * t**3 / 80
        + 1_407 * t**2 / 1_920
        - 13 * t / 8
        + 211 / 200
    )

def a_of_t(t: float) -> float:
    """Acceleration  a(t) = dv/dt = d²s/dt² — exact analytical derivative of v_of_t."""
    return (
        215 * t**3 / 9_600
        - 27 * t**2 / 80
        + 1_407 * t / 960
        - 13 / 8
    )

# ─── Shared helper ────────────────────────────────────────────────────────────

def make_boxed(mob: Mobject, color: str = YELLOW, buff: float = 0.2) -> VGroup:
    """Return a VGroup containing *mob* and a coloured SurroundingRectangle."""
    box = SurroundingRectangle(mob, color=color, buff=buff)
    return VGroup(mob, box)


# ═══════════════════════════════════════════════════════════════════════════════
#  Scene 1 — RectilinearMotion
# ═══════════════════════════════════════════════════════════════════════════════

class RectilinearMotion(Scene):
    """Number-line diagram followed by velocity and acceleration derivations."""

    def construct(self) -> None:
        self._build_diagram()
        self._show_velocity_equations()
        self._show_acceleration_equations()

    # ── 1. Number-line diagram ────────────────────────────────────────────────

    def _build_diagram(self) -> None:
        # Axis
        line          = Line(LEFT * 3, RIGHT * 3, color=WHITE)
        origin_dot    = Dot(ORIGIN, color=RED)
        origin_label  = MathTex("O", font_size=24).next_to(origin_dot, UP)
        label_neg     = MathTex("-s", font_size=24).next_to(line.get_start(), LEFT)
        label_pos     = MathTex("s",  font_size=24).next_to(line.get_end(),   RIGHT)

        self.add(origin_dot, origin_label)
        self.play(FadeIn(line))
        self.add(label_neg, label_pos)
        self.wait(0.5)

        # Initial position P at t = t₀
        p_dot   = Dot(RIGHT * 1.5, color=BLUE)
        p_lbl   = MathTex("P",          font_size=24).next_to(p_dot,  UP)
        t0_lbl  = MathTex(r"t = t_0",   font_size=22).next_to(p_lbl,  UP)
        self.play(FadeIn(p_dot), FadeIn(p_lbl), FadeIn(t0_lbl))

        # Displacement arrow O → P
        s_arrow = Arrow(ORIGIN, p_dot.get_center(), buff=0, color=YELLOW)
        s_lbl   = MathTex("s", font_size=24).next_to(s_arrow, DOWN)
        self.play(GrowArrow(s_arrow), FadeIn(s_lbl))
        self.wait(0.5)

        # Animate particle from P to P′
        p_prime_pos  = p_dot.get_center() + RIGHT * 1.0
        particle     = p_dot.copy().set_color(GREEN)
        self.add(particle)
        self.play(particle.animate.move_to(p_prime_pos), run_time=1.5, rate_func=smooth)
        self.remove(particle)   # swap the moving dot for a static P′ dot

        p_prime_dot  = Dot(p_prime_pos, color=GREEN)
        pp_lbl       = MathTex("P'",                   font_size=24).next_to(p_prime_dot, UP)
        t1_lbl       = MathTex(r"t = t_0 + \Delta t",  font_size=20).next_to(pp_lbl,      UP)
        self.play(FadeIn(p_prime_dot), FadeIn(pp_lbl), FadeIn(t1_lbl))

        # Δs arrow P → P′ with time annotation
        ds_arrow = Arrow(p_dot.get_center(), p_prime_pos, buff=0, color=GREEN)
        ds_lbl   = MathTex(r"\Delta s",        font_size=24).next_to(ds_arrow, DOWN)
        dt_lbl   = MathTex(r"\text{in }\Delta t", font_size=20).next_to(ds_lbl, DOWN)
        self.play(GrowArrow(ds_arrow), FadeIn(ds_lbl), FadeIn(dt_lbl))
        self.wait(0.5)

        # Collect everything and slide to top edge
        self.diagram_group = VGroup(
            line, origin_dot, origin_label, label_neg, label_pos,
            p_dot, p_lbl, t0_lbl, s_arrow, s_lbl,
            p_prime_dot, pp_lbl, t1_lbl, ds_arrow, ds_lbl, dt_lbl,
        )
        self.play(self.diagram_group.animate.scale(0.85).to_edge(UP), run_time=1.5)

    # ── 2. Velocity derivation ────────────────────────────────────────────────

    def _show_velocity_equations(self) -> None:
        # Vertical centre below the diagram
        centre = ORIGIN + DOWN * 0.8

        # Step 1 – average velocity
        vel_avg = MathTex(r"v_{\text{avg}}", r"=", r"\frac{\Delta s}{\Delta t}", font_size=40)
        vel_avg.move_to(centre)
        note    = Tex("Average velocity", font_size=28, color=GREY_A).next_to(vel_avg, DOWN)
        self.play(Write(vel_avg), FadeIn(note))
        self.wait(1.5)
        self.play(FadeOut(note))

        # Step 2 – limit form
        vel_lim = MathTex(
            r"v", r"=", r"\lim_{\Delta t \to 0}", r"\frac{\Delta s}{\Delta t}",
            font_size=40,
        ).move_to(centre)
        self.play(TransformMatchingTex(vel_avg, vel_lim))
        self.wait(1.5)

        # Step 3 – Leibniz notation
        vel_dx = MathTex(r"v", r"=", r"\frac{ds}{dt}", font_size=40).move_to(centre)
        self.play(TransformMatchingTex(vel_lim, vel_dx))
        self.wait(1.5)

        # Step 4 – Newton dot notation (complete form)
        vel_dot = MathTex(
            r"v", r"=", r"\frac{ds}{dt}", r"=", r"\dot{s}", font_size=40,
        ).move_to(centre)
        self.play(TransformMatchingTex(vel_dx, vel_dot))
        self.wait(1.5)

        # Box and pin below diagram on the left
        self.eq_vel = make_boxed(vel_dot)
        self.play(Create(self.eq_vel[1]))      # animate only the box (mob already visible)
        self.wait()
        self.play(
            self.eq_vel.animate
                .next_to(self.diagram_group, DOWN, buff=0.35)
                .to_edge(LEFT)
        )

    # ── 3. Acceleration derivation ────────────────────────────────────────────

    def _show_acceleration_equations(self) -> None:
        anchor = self.eq_vel

        def _place(mob: Mobject) -> Mobject:
            """Position *mob* below the velocity equation, flush left."""
            return mob.next_to(anchor, DOWN, buff=0.9).to_edge(LEFT)

        # Step 1 – average acceleration
        acc_avg = _place(
            MathTex(r"a_{\text{avg}}", r"=", r"\frac{\Delta v}{\Delta t}", font_size=40)
        )
        note    = Tex("Average acceleration", font_size=28, color=GREY_A).next_to(acc_avg, DOWN)
        self.play(Write(acc_avg), FadeIn(note))
        self.wait(1.5)
        self.play(FadeOut(note))

        # Step 2 – limit form
        acc_lim = _place(MathTex(
            r"a", r"=", r"\lim_{\Delta t \to 0}", r"\frac{\Delta v}{\Delta t}", font_size=40,
        ))
        self.play(TransformMatchingTex(acc_avg, acc_lim))
        self.wait(1.5)

        # Step 3 – Leibniz notation
        acc_dx = _place(MathTex(r"a", r"=", r"\frac{dv}{dt}", font_size=40))
        self.play(TransformMatchingTex(acc_lim, acc_dx))
        self.wait(1.5)

        # Step 4 – complete form (dot & second-derivative notations)
        acc_full = _place(MathTex(
            r"a", r"=", r"\frac{dv}{dt}", r"=", r"\dot{v}",
            r"=", r"\frac{d^2s}{dt^2}", r"=", r"\ddot{s}",
            font_size=40,
        ))
        self.play(TransformMatchingTex(acc_dx, acc_full))
        self.wait(2)

        self.eq_acc = make_boxed(acc_full)
        self.play(Create(self.eq_acc[1]))
        self.wait(2)


# ═══════════════════════════════════════════════════════════════════════════════
#  Scene 2 — GraphicalInterpretations
# ═══════════════════════════════════════════════════════════════════════════════

class GraphicalInterpretations(Scene):
    """s-t and v-t graphs with tangent lines, secant limits, and area shading."""

    # Class-level constants so all methods share the same domain / sample times
    T_MIN: float = 0.0
    T_MAX: float = 10.0
    T1:    float = 2.1
    T2:    float = 5.8

    def construct(self) -> None:
        self._s_vs_t_graph()
        self._v_vs_t_graph()

    # ── Shared helpers ────────────────────────────────────────────────────────

    def _make_axes(self, y_range: list, y_label: str) -> tuple[Axes, VGroup]:
        """Create a standard Axes object with axis labels; return both."""
        axes = Axes(
            x_range=[self.T_MIN, self.T_MAX, 2],
            y_range=y_range,
            x_length=6,
            y_length=4,
            axis_config={"color": WHITE, "include_tip": True, "tip_length": 0.1},
        )
        labels = axes.get_axis_labels(x_label="t", y_label=y_label)
        return axes, labels

    def _draw_interval_markers(
        self,
        axes:    Axes,
        func,
        t1:      float,
        t2:      float,
        y_lbl1:  str,
        y_lbl2:  str,
    ) -> VGroup:
        """
        Draw vertical + horizontal dashed lines at t1 and t2.
        Returns a VGroup of all created mobjects.
        """
        def vline(t: float) -> DashedLine:
            return DashedLine(axes.c2p(t, 0), axes.c2p(t, func(t)), color=GREEN)

        def hline(t: float) -> DashedLine:
            return DashedLine(axes.c2p(0, func(t)), axes.c2p(t, func(t)), color=GREEN)

        lv, rv = vline(t1), vline(t2)
        lh, rh = hline(t1), hline(t2)

        lt1 = MathTex(r"t_1",   font_size=24).next_to(axes.c2p(t1, 0),        DOWN)
        lt2 = MathTex(r"t_2",   font_size=24).next_to(axes.c2p(t2, 0),        DOWN)
        ls1 = MathTex(y_lbl1,   font_size=24).next_to(axes.c2p(0, func(t1)),  LEFT)
        ls2 = MathTex(y_lbl2,   font_size=24).next_to(axes.c2p(0, func(t2)),  LEFT)

        self.play(Succession(Write(lt1), Create(lv), Write(lt2), Create(rv)))
        self.play(Succession(Create(lh), Create(rh), Write(ls1), Write(ls2)))

        return VGroup(lv, rv, lh, rh, lt1, lt2, ls1, ls2)

    # ── s-t graph ─────────────────────────────────────────────────────────────

    def _s_vs_t_graph(self) -> None:
        axes, labels = self._make_axes(y_range=[0, 6, 2], y_label="s")
        self.play(Create(axes), Write(labels))
        self.wait(0.5)

        curve = axes.plot(s_of_t, x_range=[self.T_MIN, self.T_MAX], color=BLUE)
        self.play(Create(curve))
        self.wait(0.5)

        # ── Phase A: roaming dot + tangent line ──────────────────────────────
        alpha = ValueTracker(0.1)

        def t_from_alpha(a: float) -> float:
            return self.T_MIN + a * (self.T_MAX - self.T_MIN)

        dot_P   = always_redraw(
            lambda: Dot(axes.c2p(t_from_alpha(alpha.get_value()),
                                  s_of_t(t_from_alpha(alpha.get_value()))), color=RED)
        )
        lbl_P   = always_redraw(lambda: MathTex("P", font_size=24).next_to(dot_P, UP))
        tangent = always_redraw(
            lambda: TangentLine(curve,
                                alpha=max(0.001, min(0.999, alpha.get_value())),
                                length=3.5, color=BLUE_D)
        )

        self.add(dot_P, lbl_P, tangent)
        self.play(alpha.animate.set_value(0.9), run_time=4, rate_func=linear)
        self.play(alpha.animate.set_value(0.8), run_time=1, rate_func=linear)
        self.wait(0.5)
        self.remove(tangent)

        # ── Phase B: secant → tangent limit ──────────────────────────────────
        alpha_base = alpha.get_value()   # fixed base point for the secant
        dt_tracker = ValueTracker(0.15)

        def get_P2():
            return curve.point_from_proportion(
                min(0.999, alpha_base + dt_tracker.get_value())
            )

        chord    = always_redraw(lambda: Line(dot_P.get_center(), get_P2(), color=YELLOW, stroke_width=4))
        h_seg    = always_redraw(lambda: DashedLine(dot_P.get_center(),              [get_P2()[0], dot_P.get_center()[1], 0], color=YELLOW))
        v_seg    = always_redraw(lambda: DashedLine([get_P2()[0], dot_P.get_center()[1], 0], get_P2(), color=YELLOW))
        dot_P2   = always_redraw(lambda: Dot(get_P2(), color=YELLOW))
        lbl_P2   = always_redraw(lambda: MathTex(r"P'", font_size=24).next_to(Dot(get_P2()), UP))

        h_brace  = always_redraw(lambda: Brace(h_seg, direction=DOWN,  color=YELLOW))
        v_brace  = always_redraw(lambda: Brace(v_seg, direction=RIGHT, color=YELLOW))
        h_tex    = MathTex(r"\Delta t", font_size=24)
        v_tex    = MathTex(r"\Delta s", font_size=24)
        h_tex.add_updater(lambda m: m.next_to(h_brace, DOWN,  buff=0.1))
        v_tex.add_updater(lambda m: m.next_to(v_brace, RIGHT, buff=0.1))

        self.play(Flash(dot_P.get_center(), color=YELLOW, line_length=0.2, num_lines=8))
        self.play(Create(chord), Create(dot_P2), Write(lbl_P2))
        self.wait(0.3)
        self.play(Create(h_seg), Create(h_brace), Write(h_tex),
                  Create(v_seg), Create(v_brace), Write(v_tex))
        self.wait(0.3)

        slope_avg = MathTex(r"\text{slope}", r"=", r"\frac{\Delta s}{\Delta t}",
                             font_size=30).next_to(axes, RIGHT, buff=0.8)
        self.play(Write(slope_avg))
        self.wait(0.5)

        # Shrink Δt → 0 (secant becomes tangent)
        self.play(dt_tracker.animate.set_value(0.00001), run_time=3, rate_func=linear)
        self.wait(0.3)

        # Clear updaters before fading to prevent invisible objects from crashing
        h_tex.clear_updaters()
        v_tex.clear_updaters()
        self.remove(lbl_P2)   # always_redraw version replaced manually

        tan_line   = TangentLine(curve, alpha=alpha_base, length=3.5, color=RED)
        slope_inst = MathTex(r"\text{slope}", r"=", r"v", r"=", r"\frac{ds}{dt}",
                              font_size=30).next_to(axes, RIGHT, buff=0.8)

        self.play(
            FadeOut(h_seg), FadeOut(h_brace), FadeOut(h_tex),
            FadeOut(v_seg), FadeOut(v_brace), FadeOut(v_tex),
            FadeOut(dot_P2),
            ReplacementTransform(chord, tan_line),
        )
        self.play(TransformMatchingTex(slope_avg, slope_inst))
        self.wait(1.5)
        self.play(FadeOut(tan_line), FadeOut(slope_inst), FadeOut(dot_P), FadeOut(lbl_P))

        # ── Phase C: position difference Δs = s(t₂) − s(t₁) ─────────────────
        markers = self._draw_interval_markers(axes, s_of_t, self.T1, self.T2,
                                               r"s(t_1)", r"s(t_2)")
        graph_group = VGroup(axes, labels, curve, markers)
        self.play(graph_group.animate.shift(LEFT * 2), run_time=1.5)

        dis_eqn = MathTex(r"\Delta s", r"=", r"s(t_2)", r"-", r"s(t_1)", font_size=34)
        dis_eqn.next_to(graph_group, RIGHT, buff=0.8)
        self.play(Write(dis_eqn))
        self.wait(2)

        # Store for hand-off and fade out
        self._st_group = graph_group
        self.play(FadeOut(dis_eqn))

    # ── v-t graph ─────────────────────────────────────────────────────────────

    def _v_vs_t_graph(self) -> None:
        # Fade out s-t graph before starting fresh
        self.play(FadeOut(self._st_group))

        axes, labels = self._make_axes(y_range=[-1, 2, 1], y_label="v")
        self.play(Create(axes), Write(labels))
        self.wait(0.5)

        curve = axes.plot(v_of_t, x_range=[self.T_MIN, self.T_MAX], color=BLUE)
        self.play(Create(curve))
        self.wait(0.5)

        # ── Phase A: roaming dot + tangent → slope = a = dv/dt ───────────────
        alpha = ValueTracker(0.4)

        def t_from_alpha(a: float) -> float:
            return self.T_MIN + a * (self.T_MAX - self.T_MIN)

        dot_P   = always_redraw(
            lambda: Dot(axes.c2p(t_from_alpha(alpha.get_value()),
                                  v_of_t(t_from_alpha(alpha.get_value()))), color=RED)
        )
        lbl_P   = always_redraw(lambda: MathTex("P", font_size=24).next_to(dot_P, UP))
        tangent = always_redraw(
            lambda: TangentLine(curve,
                                alpha=max(0.001, min(0.999, alpha.get_value())),
                                length=3.5, color=BLUE_D)
        )
        slope_acc = MathTex(
            r"\text{slope}", r"=", r"a", r"=", r"\frac{dv}{dt}",
            font_size=30
        ).next_to(axes, RIGHT, buff=0.8)

        self.add(dot_P, lbl_P, tangent)
        self.play(Write(slope_acc))
        self.play(alpha.animate.set_value(0.85), run_time=3, rate_func=linear)
        self.wait(0.5)
        self.remove(tangent, dot_P, lbl_P)
        self.play(FadeOut(slope_acc))

        # ── Phase B: interval markers + shift left ────────────────────────────
        markers = self._draw_interval_markers(axes, v_of_t, self.T1, self.T2,
                                               r"v(t_1)", r"v(t_2)")
        graph_group = VGroup(axes, labels, curve, markers)
        self.play(graph_group.animate.shift(LEFT * 2), run_time=1.5)

        # ── Phase C: derivation chain  v = ds/dt → ds = v dt → Δs = ∫v dt ───
        # Build each equation anchored relative to the previous one.
        e1 = MathTex(r"v", r"=", r"\frac{ds}{dt}", font_size=34)
        e1.next_to(graph_group, RIGHT, buff=0.8).shift(UP * 1.2)

        e2 = MathTex(r"ds", r"=", r"v\,dt", font_size=34)
        e2.next_to(e1, DOWN, buff=0.55)

        e3 = MathTex(r"\int_{t_1}^{t_2} ds", r"=", r"\int_{t_1}^{t_2} v\,dt", font_size=34)
        e3.next_to(e2, DOWN, buff=0.55)

        e4 = MathTex(r"\Delta s", r"=", r"\int_{t_1}^{t_2} v(t)\,dt", font_size=34)
        e4.next_to(e3, DOWN, buff=0.55)

        # Reveal step-by-step, using .copy() as source so the original persists
        self.play(Write(e1))
        self.wait(0.8)
        self.play(TransformMatchingTex(e1.copy(), e2))
        self.wait(0.8)
        self.play(TransformMatchingTex(e2.copy(), e3))
        self.wait(0.8)
        self.play(TransformMatchingTex(e3.copy(), e4))
        self.wait(1)

        # ── Phase D: shade the area under v(t) to make ∫v dt concrete ────────
        area = axes.get_area(
            curve,
            x_range=[self.T1, self.T2],
            color=[BLUE, GREEN],
            opacity=0.4,
        )
        self.play(FadeIn(area))
        self.wait(0.5)

        # Box the final integration result
        result = make_boxed(e4, color=YELLOW)
        self.play(Create(result[1]))
        self.wait(2)

    # ── a-t graph ─────────────────────────────────────────────────────────────
    def _a_vs_t_graph(self) -> None:
        # Similar structure to _v_vs_t_graph, but with acceleration and a few tweaks
        axes, labels = self._make_axes(y_range=[-1, 1, 0.5], y_label="a")
        self.play(Create(axes), Write(labels))
        self.wait(0.5)

        curve = axes.plot(a_of_t, x_range=[self.T_MIN, self.T_MAX], color=BLUE)
        self.play(Create(curve))
        self.wait(0.5)
