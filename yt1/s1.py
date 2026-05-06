from manim import *
import numpy as np

class CoriolisDemo(Scene):
    def construct(self):

    # ── Start at screen centre ─────────────────────────────────────
        axes = Axes(
            x_range=[0, 6], y_range=[0, 6],
            x_length=6, y_length=6,
            axis_config={"include_tip": True, "color": WHITE},
            
        ).move_to(ORIGIN)   # center ma rakyau

        x_label = axes.get_x_axis_label("x")
        y_label = axes.get_y_axis_label("y")

        origin_fixed = np.array(axes.c2p(0, 0)) 
        self.add(axes, x_label, y_label)

        #  All trackers

        # center postion of link 2 (square)
        cx_tr    = ValueTracker(np.array(axes.c2p(4, 2))[0])
        cy_tr    = ValueTracker(np.array(axes.c2p(4, 2))[1])

        c = Dot(np.array([cx_tr.get_value(), cy_tr.get_value(), 0]))

        # global axis tracker
        ox_tr    = ValueTracker(0.0)    # global offset x 
        oy_tr    = ValueTracker(0.0)    # global offset y


        angle_tr = ValueTracker(0.0)
        t_tr     = ValueTracker(0.0)

        s = 2.5 * 0.38
        cp = [
            np.array([-s, -s, 0.0]),
            np.array([-0.5*s, +s, 0.0]),
            np.array([+0.5*s, +0.5*s, 0.0]),
            np.array([+s, +s, 0.0]),
        ]

        # total time period
        T = 4.0

        # side length of square link 2
        side = 2.5
        
        # angular velocity of 
        def omega(t):
            return (np.pi**2 / (12 * T)) * np.sin(np.pi * t / T)

        def v_path(t):
            return (np.pi / (2 * T)) * np.sin(np.pi * t / T)

        state     = {"angle": 0.0, "t_param": 0.0, "elapsed": 0.0, "done": False}
        rev_state = {"elapsed": 0.0, "done": False}

        fwd = VMobject()
        def integrate_fwd(mob, dt):
            if state["done"]: return
            t = state["elapsed"]
            if t >= T:
                angle_tr.set_value(PI / 6); t_tr.set_value(1.0)
                state["done"] = True; return
            state["angle"]   += omega(t) * dt
            state["t_param"]  = min(state["t_param"] + v_path(t) * dt, 1.0)
            state["elapsed"] += dt
            angle_tr.set_value(state["angle"]); t_tr.set_value(state["t_param"])
        fwd.add_updater(integrate_fwd)

        rev = VMobject()
        def integrate_rev(mob, dt):
            if rev_state["done"]: return
            t = rev_state["elapsed"]
            if t >= T:
                angle_tr.set_value(0.0); t_tr.set_value(0.0)
                rev_state["done"] = True; return
            state["angle"]   -= omega(t) * dt
            state["t_param"]  = max(state["t_param"] - v_path(t) * dt, 0.0)
            rev_state["elapsed"] += dt
            angle_tr.set_value(state["angle"]); t_tr.set_value(state["t_param"])
        rev.add_updater(integrate_rev)

        #  to_world: origin shifts with ox_tr, oy_tr 
        def get_origin():
            return origin_fixed + np.array([ox_tr.get_value(), oy_tr.get_value(), 0.0])

        def to_world(local_pt, angle):
            orig   = get_origin()
            center = np.array([cx_tr.get_value(), cy_tr.get_value(), 0.0])
            offset = np.array([ox_tr.get_value(), oy_tr.get_value(), 0.0])
            c, sa  = np.cos(angle), np.sin(angle)
            R = np.array([[c, -sa, 0.0], [sa, c, 0.0], [0.0, 0.0, 1.0]])
            return orig + R @ (center - origin_fixed + local_pt)

        def bezier_pt(t):
            mt = 1 - t
            return (mt**3*cp[0] + 3*mt**2*t*cp[1] + 3*mt*t**2*cp[2] + t**3*cp[3])

        #  Scene objects 
        origin_dot = always_redraw(lambda: Dot(
            get_origin(), color=WHITE, radius=0.07
        ))

        square = always_redraw(lambda: Square(
            side_length=side, color=GRAY, stroke_width=0, fill_color=GRAY, fill_opacity=0.5
        ).move_to(to_world(ORIGIN, angle_tr.get_value())
        ).rotate(angle_tr.get_value()))

        arm = always_redraw(lambda: DashedLine(
            get_origin(),
            to_world(ORIGIN, angle_tr.get_value()),
            color=GRAY, dash_length=0.15, stroke_width=1.5,
        ))

        bezier_mob = always_redraw(lambda: CubicBezier(
            *[to_world(cp[i], angle_tr.get_value()) for i in range(4)],
            color=BLUE_B, stroke_width=2.5,
        ))

        dot = Dot(color=RED, radius=0.12)
        dot.move_to(to_world(bezier_pt(0.0), 0.0))
        dot.add_updater(lambda m: m.move_to(
            to_world(bezier_pt(t_tr.get_value()), angle_tr.get_value())
        ))

        omega_label = always_redraw(lambda: MathTex(
            rf"\omega = {np.degrees(omega(state['elapsed'])):.2f}\ °/s",
            font_size=26, color=YELLOW
        ).to_corner(UR, buff=0.4))

        v_label = always_redraw(lambda: MathTex(
            rf"\dot{{s}} = {v_path(state['elapsed']):.3f}\ /s",
            font_size=26, color=GREEN_B
        ).next_to(omega_label, DOWN, buff=0.15))

        angle_label = always_redraw(lambda: MathTex(
            rf"\theta = {np.degrees(angle_tr.get_value()):.1f}°",
            font_size=26, color=WHITE
        ).next_to(v_label, DOWN, buff=0.15))

        self.add(origin_dot, arm, square, bezier_mob, dot,
                 omega_label, v_label, angle_label)
        self.wait(0.3)

        # ── Forward pass ───────────────────────────────────────────────
        trail = TracedPath(dot.get_center, stroke_color=GREEN_B, stroke_width=2.5)
        self.add(trail, fwd)
        self.wait(T + 0.3)

        self.wait(0.5)
        self.play(FadeOut(trail), run_time=0.4)
        self.remove(fwd)

        # ── Reverse pass ───────────────────────────────────────────────
        self.add(rev)
        self.wait(T + 0.3)
        self.remove(rev)

        angle_tr.set_value(0.0)
        t_tr.set_value(0.0)
        self.wait(1.0)

# ── Move whole system to left after animation ──────────────────
        target  = np.array([-2, 0.0, 0.0])   # left side of screen

        dx = target[0] 
        dy = target[1]

        self.play(
            ox_tr.animate.set_value(dx),
            oy_tr.animate.set_value(dy),
            axes.animate.shift(np.array([dx, dy, 0.0])),
            x_label.animate.shift(np.array([dx, dy, 0.0])),
            y_label.animate.shift(np.array([dx, dy, 0.0])),
            run_time=1.5
        )
        self.wait(1.0)

        # ── Reset trackers for second forward pass ─────────────────────
        angle_tr.set_value(0.0)
        t_tr.set_value(0.0)

        state2 = {"angle": 0.0, "t_param": 0.0, "elapsed": 0.0, "done": False}

        # ── First half integrator (0 → T/2) ───────────────────────────
        T_half = T / 2.0
        fwd2a = VMobject()
        def integrate_fwd2a(mob, dt):
            if state2["done"]: return
            t = state2["elapsed"]
            if t >= T_half:
                state2["done"] = True; return
            state2["angle"]   += omega(t) * dt
            state2["t_param"]  = min(state2["t_param"] + v_path(t) * dt, 1.0)
            state2["elapsed"] += dt
            angle_tr.set_value(state2["angle"])
            t_tr.set_value(state2["t_param"])
        fwd2a.add_updater(integrate_fwd2a)

        # ── Second half integrator (T/2 → T) ──────────────────────────
        fwd2b_done = {"done": False}
        fwd2b = VMobject()
        def integrate_fwd2b(mob, dt):
            if fwd2b_done["done"]: return
            t = state2["elapsed"]
            if t >= T:
                angle_tr.set_value(PI / 6); t_tr.set_value(1.0)
                fwd2b_done["done"] = True; return
            state2["angle"]   += omega(t) * dt
            state2["t_param"]  = min(state2["t_param"] + v_path(t) * dt, 1.0)
            state2["elapsed"] += dt
            angle_tr.set_value(state2["angle"])
            t_tr.set_value(state2["t_param"])
        fwd2b.add_updater(integrate_fwd2b)

        # ── Velocity helpers ───────────────────────────────────────────
        def bezier_tangent(t):
            """Cubic bezier derivative (local frame, unnormalised)."""
            mt = 1 - t
            return 3 * (mt**2 * (cp[1] - cp[0])
                      + 2*mt*t * (cp[2] - cp[1])
                      +    t**2 * (cp[3] - cp[2]))

        def get_R(angle):
            c, sa = np.cos(angle), np.sin(angle)
            return np.array([[c, -sa, 0.0], [sa, c, 0.0], [0.0, 0.0, 1.0]])

        def get_v_rel_world():
            """Relative velocity: tangent rotated to world frame, scaled by v_path."""
            angle = angle_tr.get_value()
            t     = t_tr.get_value()
            tang  = bezier_tangent(t)
            speed = v_path(state2["elapsed"])
            tang_norm = tang / (np.linalg.norm(tang) + 1e-9)
            return get_R(angle) @ (tang_norm * speed * 2.5)   # 2.5 = display scale

        def get_v_transport_world():
            """Transport velocity: ω × r (perpendicular to arm, CCW)."""
            angle = angle_tr.get_value()
            w     = omega(state2["elapsed"])
            # r = vector from shifted origin to dot
            r = dot.get_center() - get_origin()
            # ω × r in 2D = ω * perp(r)
            perp_r = np.array([-r[1], r[0], 0.0])
            return perp_r * w * 4.0   # 4.0 = display scale

        def get_v_coriolis_world():
            """Coriolis: 2ω × v_rel — perpendicular to v_rel."""
            w     = omega(state2["elapsed"])
            v_rel = get_v_rel_world()
            perp  = np.array([-v_rel[1], v_rel[0], 0.0])
            return perp * 2 * w * 4.0

        # ── Analysis arrows (always_redraw so they live-update) ────────
        arrow_vrel = always_redraw(lambda: Arrow(
            dot.get_center(),
            dot.get_center() + get_v_rel_world(),
            color=BLUE_B, buff=0, stroke_width=3,
            max_tip_length_to_length_ratio=0.2
        ))
        label_vrel = always_redraw(lambda: MathTex(
            r"\vec{v}_{rel}", font_size=28, color=BLUE_B
        ).next_to(dot.get_center() + get_v_rel_world(), UR, buff=0.1))

        arrow_vtrans = always_redraw(lambda: Arrow(
            dot.get_center(),
            dot.get_center() + get_v_transport_world(),
            color=YELLOW, buff=0, stroke_width=3,
            max_tip_length_to_length_ratio=0.2
        ))
        label_vtrans = always_redraw(lambda: MathTex(
            r"\vec{\omega} \times \vec{r}", font_size=28, color=YELLOW
        ).next_to(dot.get_center() + get_v_transport_world(), RIGHT, buff=0.1))

        arrow_vcor = always_redraw(lambda: Arrow(
            dot.get_center(),
            dot.get_center() + get_v_coriolis_world(),
            color=GREEN_B, buff=0, stroke_width=3,
            max_tip_length_to_length_ratio=0.2
        ))
        label_vcor = always_redraw(lambda: MathTex(
            r"2\vec{\omega} \times \vec{v}_{rel}", font_size=28, color=GREEN_B
        ).next_to(dot.get_center() + get_v_coriolis_world(), DR, buff=0.1))

        # ── Run first half ─────────────────────────────────────────────
        trail2 = TracedPath(dot.get_center, stroke_color=GREEN_B, stroke_width=2.5)
        self.add(trail2, fwd2a)
        self.wait(T_half + 0.2)
        self.remove(fwd2a)

        # ── Pause and show analysis ────────────────────────────────────
        self.wait(0.3)
        self.play(
            FadeIn(arrow_vrel),   FadeIn(label_vrel),
            # FadeIn(arrow_vtrans), FadeIn(label_vtrans),
            # FadeIn(arrow_vcor),   FadeIn(label_vcor),
            run_time=0.8
        )
        self.wait(2.0)   # ← analysis pause — arrows live-update with current state

        # ── Resume second half ─────────────────────────────────────────
        self.add(fwd2b)
        self.wait(T_half + 0.2)
        self.remove(fwd2b)

        self.wait(1.0)

        # Create new coordinate system at bottom-left corner of square, rotated with it
        new_axes = always_redraw(lambda: Axes(
            x_range=[0, side], y_range=[0, side],
            x_length=side, y_length=side,
            axis_config={"include_tip": True, "color": YELLOW},
            tips=True,
        ).move_to(square.get_corner(DOWN + LEFT)).rotate(angle_tr.get_value(), about_point=square.get_corner(np.array([0, 0, 0]))))
        
        self.add(new_axes)

        self.wait(2.0)

































