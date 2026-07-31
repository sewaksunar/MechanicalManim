"""
kinematics.py – Manim animation: Position, Velocity & Acceleration
====================================================================
Scene1 : Intro           (placeholder)
Scene2 : Position vector, Δr, Δs, average/instantaneous velocity
Scene3 : Particle on Bézier path + velocity-field stamps → v(t) graph
Scene4 : Hodograph → average & instantaneous acceleration

Naming convention
─────────────────
ax_*      Axes objects
lbl_*     Labels / MathTex / Text
vec_*     Arrow mobjects (vectors)
dot_*     Dot mobjects
grp_*     VGroup collections
trk_*     ValueTracker objects
crv_*     ParametricCurve / plot results
"""

from __future__ import annotations

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService


# ══════════════════════════════════════════════════════════════════════════════
#  Shared geometry – cubic Bézier path
# ══════════════════════════════════════════════════════════════════════════════

# Control points (data-space, z=0)
_P0 = np.array([1.5, 1.8, 0])
_P1 = np.array([1.8, 1.1, 0])
_P2 = np.array([3.5, 1.5, 0])
_P3 = np.array([4.0, 4.0, 0])

# Speed / snap settings
V_SCALE    : float = 0.3   # global velocity magnitude multiplier
TIME_SNAP  : float = 0.5   # time interval between stamps (seconds)
MAX_STAMPS  : int   = 8     # keep only the first 8 stamp arrows

# Total animation time for the main particle path traversal.
ANIM_TIME  : float = 6.0


# == Pure math helpers ==================================================================

def bez(t: float) -> np.ndarray:
    """Cubic Bézier position at parameter t ∈ [0, 1]."""
    u = 1.0 - t
    return u**3*_P0 + 3*u**2*t*_P1 + 3*u*t**2*_P2 + t**3*_P3


def bez_d1(t: float) -> np.ndarray:
    """First derivative  dγ/dt  of the Bézier (analytic)."""
    u = 1.0 - t
    return 3.0 * (u**2*(_P1-_P0) + 2*u*t*(_P2-_P1) + t**2*(_P3-_P2))


def bez_d2(t: float) -> np.ndarray:
    """Second derivative  d²γ/dt²  of the Bézier (analytic)."""
    return 6.0 * ((1-t)*(_P2 - 2*_P1 + _P0) + t*(_P3 - 2*_P2 + _P1))


def vel(t: float) -> np.ndarray:
    """Velocity vector v(t) in path-data space."""
    # Non-monotonic speed profile: speed_factor will increase, decrease, then increase.
    speed_factor = 1.5 - np.cos(3 * PI * t)
    return V_SCALE * speed_factor * bez_d1(t)


def acc(t: float) -> np.ndarray:
    """Acceleration vector a(t) = dv/dt in path-data space."""
    # Corresponds to the new velocity function
    speed_factor = 1.5 - np.cos(3 * PI * t)
    speed_factor_d1 = 3 * PI * np.sin(3 * PI * t)
    return V_SCALE * (speed_factor_d1 * bez_d1(t) + speed_factor * bez_d2(t))


def _compute_arc_length_table(num_samples: int = 500) -> tuple[np.ndarray, np.ndarray]:
    """
    Pre-compute arc length parameterization for the motion profile.
    Returns (t_values, cumulative_speed), where cumulative_speed[i] is the
    cumulative "distance" (integral of speed) up to t_values[i].
    """
    t_vals = np.linspace(0, 1, num_samples)
    speeds = np.array([np.linalg.norm(vel(t)) for t in t_vals])
    cum_speed = np.cumsum(speeds)
    cum_speed = cum_speed / cum_speed[-1]  # Normalize to [0, 1]
    return t_vals, cum_speed


# Pre-compute the arc length table once at module load
_T_TABLE, _S_TABLE = _compute_arc_length_table()


def vel_rate(s: float) -> float:
    """
    Custom rate_func: maps normalised progress s → curve parameter t.
    
    Uses numerical interpolation based on the integral of the actual
    velocity magnitude, so the particle's motion correctly reflects the
    defined velocity profile (non-monotonic speed).
    """
    # Clamp s to [0, 1]
    s = np.clip(s, 0, 1)
    # Interpolate to find t such that cumulative speed ≈ s
    return float(np.interp(s, _S_TABLE, _T_TABLE))


# Pre-compute stamp times and corresponding curve parameters for equal time intervals
_STAMP_TIMES = np.arange(TIME_SNAP, ANIM_TIME + 1e-9, TIME_SNAP)[:MAX_STAMPS]
_STAMP_T_VALUES = np.array([vel_rate(t / ANIM_TIME) for t in _STAMP_TIMES])


# ── Axis factory (shared style) ───────────────────────────────────────────────

def make_axes(
    x_range: list, y_range: list,
    x_len: float, y_len: float,
    **kw
) -> Axes:
    """Return an Axes with the project's standard grey style."""
    return Axes(
        x_range=x_range, y_range=y_range,
        x_length=x_len,  y_length=y_len,
        axis_config={
            "color": GREY_B,
            "stroke_width": 2.5,
            "include_tip": True,
            "tip_length": 0.15,
            **kw,
        },
    )


# ── Arrow / dot factories (keep mob construction DRY) ────────────────────────

def vel_arrow(
    ax: Axes, t: float,
    color=YELLOW, sw: float = 2.5, tip_ratio: float = 0.14,
) -> Arrow:
    """Velocity arrow at curve parameter t, plotted on *ax*."""
    tail = ax.c2p(*bez(t)[:2])
    tip  = ax.c2p(*(bez(t) + vel(t))[:2])
    return Arrow(tail, tip, buff=0, color=color,
                 stroke_width=sw, max_tip_length_to_length_ratio=tip_ratio)


def path_dot(ax: Axes, t: float, color=RED, r: float = 0.05) -> Dot:
    """Dot at Bézier position t on *ax*."""
    return Dot(ax.c2p(*bez(t)[:2]), color=color, radius=r)


# ══════════════════════════════════════════════════════════════════════════════
#  build_vel_path_scene  – reusable composition for Scene3 & Scene4
# ══════════════════════════════════════════════════════════════════════════════

def build_vel_path_scene() -> tuple[VGroup, VGroup]:
    """
    Return (grp_full, grp_axes_crv) where:
      grp_full      – axes + curve + live dot/arrow + stamped ghost arrows
      grp_axes_crv  – axes + labels + dashed curve only
    """
    ax = make_axes([0, 3, 1], [0, 3, 1], x_len=3, y_len=3, include_tip=False)

    ax_x = ax.x_axis.get_right() + RIGHT * 0.15
    ax_y = ax.y_axis.get_top() + UP * 0.15

    lbl_axes = VGroup(
            MathTex(r"x", font_size=24).move_to(ax_x),
            MathTex(r"y", font_size=24).move_to(ax_y),
        )

    crv = DashedVMobject(
        ax.plot_parametric_curve(bez, t_range=[0, 1], color=GOLD),
        num_dashes=40,
    )

    grp_axes_crv = VGroup(ax, lbl_axes, crv)

    # Ghost stamps at equal time intervals
    grp_stamps = VGroup(*[
        mob
        for t_stamp in _STAMP_T_VALUES
        for mob in (
            path_dot(ax, t_stamp, color=RED_C, r=0.04),
            vel_arrow(ax, t_stamp, color=YELLOW_E),
        )
    ])

    grp_full = VGroup(grp_axes_crv, grp_stamps)
    return grp_full, grp_axes_crv


# ══════════════════════════════════════════════════════════════════════════════
#  Scene 1 – Intro (placeholder)
# ══════════════════════════════════════════════════════════════════════════════

class Scene1(VoiceoverScene):
    pass


# ══════════════════════════════════════════════════════════════════════════════
#  Scene 2 – Position vector, Δr, Δs, average & instantaneous velocity
# ══════════════════════════════════════════════════════════════════════════════

class Scene2(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService())

        # ── Axes ──────────────────────────────────────────────────────────────
        ax = make_axes([0, 3, 1], [0, 3, 1], x_len=3, y_len=3)
        lbl_axes = ax.get_axis_labels(
            x_label=MathTex("x").shift(DOWN),
            y_label=MathTex("y").shift(LEFT),
        )
        grp_ax = VGroup(ax, lbl_axes).move_to(DOWN)

        with self.voiceover("Here we define a path in rectangular coordinates."):
            self.play(Create(grp_ax), run_time=2)

        # ── Bézier path (re-uses the shared bez() function) ───────────────────
        crv_path = ax.plot_parametric_curve(bez, t_range=[0, 1], color=GOLD)
        lbl_path = Text("path of motion", font_size=22, color=GOLD_A).next_to(
            ax.c2p(*bez(1)[:2]), LEFT + DOWN * 4, buff=0.15
        )

        with self.voiceover("Let's define a path function s of x and y."):
            self.play(Create(crv_path), run_time=3)
            self.play(Write(lbl_path), run_time=1)
            self.wait(0.5)

        def pt(t: float) -> np.ndarray:
            """Scene-space coordinate at curve parameter t."""
            return ax.c2p(*bez(t)[:2])

        # ── Dot tracing the path ──────────────────────────────────────────────
        trk_t = ValueTracker(0)
        dot_trace = always_redraw(
            lambda: Dot(pt(trk_t.get_value()), color=RED, radius=0.07)
        )

        with self.voiceover("The particle moves along this path."):
            self.play(Create(dot_trace))
            self.wait(0.5)

        with self.voiceover("As time moves forward, it travels to the right."):
            self.play(trk_t.animate.set_value(1), run_time=2, rate_func=linear)
            self.wait(0.5)
            self.remove(dot_trace)

        # ── Static points P and P' ────────────────────────────────────────────
        pt_P  = pt(0.1)
        pt_Pp = pt(0.4)

        dot_P  = Dot(pt_P,  color=RED, radius=0.07)
        lbl_P  = MathTex("P",  font_size=30).next_to(pt_P,  UR,  buff=0.1)
        dot_Pp = Dot(pt_Pp, color=RED, radius=0.07)
        lbl_Pp = MathTex("P'", font_size=30).next_to(pt_Pp, UP,  buff=0.1)

        self.play(FadeIn(dot_P), Write(lbl_P))

        # Moving dot to animate P → P'
        trk_move = ValueTracker(0.1)
        dot_move = always_redraw(
            lambda: Dot(pt(trk_move.get_value()), color=RED, radius=0.07)
        )

        with self.voiceover("We study the motion of particle P."):
            self.add(dot_move)

        with self.voiceover("The particle travels from P to P prime."):
            self.play(trk_move.animate.set_value(0.4), run_time=2)
            self.remove(dot_move)
            self.add(dot_Pp)
            self.play(Write(lbl_Pp))
            self.wait(0.5)

        # ── Δt, Δs, average speed ─────────────────────────────────────────────
        lbl_dt = MathTex(r"\Delta t", font_size=28).next_to(pt_Pp, DL*2, buff=0.1)

        crv_arc = ax.plot_parametric_curve(
            bez, t_range=[0.1, 0.4], color=BLUE, stroke_width=6
        )
        lbl_ds = MathTex(r"\Delta s", font_size=24, color=BLUE).next_to(
            pt_Pp, DL*2, buff=0.1
        )

        lbl_ratio    = MathTex(r"\frac{\Delta s}{\Delta t}",
                               font_size=24).next_to(pt_Pp, DL*2, buff=0.1)
        lbl_avg_spd  = MathTex(r"v_{\text{avg}} = \frac{\Delta s}{\Delta t}",
                               font_size=24).next_to(pt_Pp, DL*2, buff=0.1)

        # grp_ds_dt: the mobject we keep transforming in-place
        grp_ds_dt = VGroup(lbl_dt, lbl_ds)

        with self.voiceover("In a finite time interval Δt …"):
            self.play(Write(lbl_dt))

        with self.voiceover("… the particle covers path length Δs."):
            self.play(FadeOut(lbl_dt), Create(crv_arc))
            self.play(Write(lbl_ds))
            self.wait(0.5)

        tracker = self.add_voiceover_text(
            "Both are scalar quantities, so we can form their ratio."
        )
        self.wait(tracker.get_remaining_duration(buff=0.5))

        with self.voiceover("Δs over Δt is a scalar quantity …"):
            self.play(Transform(grp_ds_dt, lbl_ratio))

        with self.voiceover("… called average speed."):
            self.play(Transform(grp_ds_dt, lbl_avg_spd))
            self.wait(2)
            self.play(FadeOut(grp_ds_dt), FadeOut(crv_arc))

        # ── Position vector r ─────────────────────────────────────────────────
        O = ax.c2p(0, 0)

        vec_r = Arrow(O, pt_P, color=RED, buff=0,
                      stroke_width=2.5, max_tip_length_to_length_ratio=0.07)
        lbl_r_bold = MathTex(r"\mathbf{r}", font_size=32, color=RED).next_to(
            vec_r.point_from_proportion(0.6), LEFT, buff=0.12
        )
        lbl_r_arrow = MathTex(r"\vec{r}", font_size=32, color=RED).next_to(
            vec_r.point_from_proportion(0.6), LEFT, buff=0.12
        )

        with self.voiceover("We draw a vector from the origin to P: the position vector r."):
            self.play(Create(vec_r), Write(lbl_r_bold))

        with self.voiceover("We can also write it with arrow notation."):
            self.play(Transform(lbl_r_bold, lbl_r_arrow))

        # ── Position vector r + Δr ────────────────────────────────────────────
        vec_rdr = Arrow(O, pt_Pp, color=BLUE, buff=0,
                        stroke_width=2.5, max_tip_length_to_length_ratio=0.07)
        lbl_rdr = MathTex(r"\vec{r}", r"+", r"\Delta\vec{r}",
                          font_size=28).next_to(
            vec_rdr.point_from_proportion(0.6), DR, buff=0.012
        )
        lbl_rdr[0].set_color(RED)
        lbl_rdr[2].set_color(GREEN)

        with self.voiceover(
            "Similarly, the vector to P prime is  r plus Δr."
        ):
            self.play(Create(vec_rdr))
            self.play(Write(lbl_rdr))

        # ── Displacement vector Δr ────────────────────────────────────────────
        vec_dr = Arrow(pt_P, pt_Pp, color=GREEN, buff=0,
                       stroke_width=2.5, max_tip_length_to_length_ratio=0.14)
        lbl_dr = MathTex(r"\Delta\vec{r}", font_size=28, color=GREEN).next_to(
            vec_dr.get_end() + RIGHT, LEFT, buff=0.1
        )

        with self.voiceover("The difference between r …"):
            self.play(Indicate(lbl_r_bold))

        with self.voiceover("… and r plus Δr …"):
            self.play(Indicate(lbl_rdr[0]), Indicate(lbl_rdr[2]))

        with self.voiceover("… is the displacement vector Δr."):
            self.play(Create(vec_dr), Write(lbl_dr))

        # ── Average velocity → instantaneous velocity ─────────────────────────
        lbl_avg_vel = MathTex(
            r"\frac{\Delta\vec{r}}{\Delta t} = \text{average velocity}",
            font_size=28,
        ).next_to(lbl_dr, DR, buff=0.1)
        lbl_avg_vel[0][0:2].set_color(GREEN)

        lbl_inst_vel = MathTex(
            r"\lim_{\Delta t \to 0} \frac{\Delta\vec{r}}{\Delta t}"
            r"= \text{instantaneous velocity}",
            font_size=28,
        ).next_to(lbl_dr, DR, buff=0.1)
        lbl_inst_vel[0][0:2].set_color(GREEN)

        self.remove(lbl_dr)

        with self.voiceover(
            "Δr over Δt is a vector quantity called average velocity."
        ):
            self.play(Write(lbl_avg_vel))

        with self.voiceover(
            "Shrinking Δt to zero gives instantaneous velocity."
        ):
            self.play(Transform(lbl_avg_vel, lbl_inst_vel))
            self.wait(2)

        self.remove(lbl_avg_vel)

        # ── Animate P' → P (limit process) ───────────────────────────────────
        self.remove(vec_rdr, vec_dr, lbl_rdr, lbl_dr, dot_Pp, lbl_Pp)

        trk_Pp = ValueTracker(0.4)

        dot_Pp_live = always_redraw(
            lambda: Dot(pt(trk_Pp.get_value()), color=RED, radius=0.07)
        )
        vec_rdr_live = always_redraw(
            lambda: Arrow(O, pt(trk_Pp.get_value()), color=BLUE, buff=0,
                          stroke_width=2.5, max_tip_length_to_length_ratio=0.07)
        )
        vec_dr_live = always_redraw(
            lambda: Arrow(pt_P, pt(trk_Pp.get_value()), color=GREEN, buff=0,
                          stroke_width=2.5, max_tip_length_to_length_ratio=0.14)
        )

        self.add(dot_Pp_live, vec_rdr_live, vec_dr_live)

        with self.voiceover(
            "As P prime approaches P, Δr tends to zero."
        ):
            self.play(FadeOut(dot_Pp))
            self.play(trk_Pp.animate.set_value(0.1), run_time=2, rate_func=linear)
            self.remove(dot_Pp_live, vec_dr_live, vec_rdr_live)

        # ── Tangent line at P → velocity vector ───────────────────────────────
        _slope_ang = np.arctan2(
            bez(0.1 + 0.01)[1] - bez(0.1)[1],
            bez(0.1 + 0.01)[0] - bez(0.1)[0],
        )
        tang = Line(
            pt_P - RIGHT * 0.5, pt_P + RIGHT * 0.5,
            color=YELLOW, stroke_width=2.5,
        ).rotate(_slope_ang, about_point=pt_P)

        with self.voiceover(
            "The instantaneous velocity points along the tangent to the curve at P."
        ):
            self.play(Create(tang))

        lbl_drdt = MathTex(r"\frac{d\vec{r}}{dt} = \vec{v}",
                           font_size=28).next_to(lbl_dr, DR, buff=0.1)

        with self.voiceover("In derivative notation, this is d r-vector / d t."):
            self.play(Write(lbl_drdt))

        vec_v = Arrow(
            pt_P, pt_P + RIGHT * 0.5, color=YELLOW, buff=0,
            stroke_width=2.5, max_tip_length_to_length_ratio=0.14,
        ).rotate(_slope_ang, about_point=pt_P)
        lbl_v = MathTex(r"\vec{v}", font_size=28, color=YELLOW).next_to(
            vec_v.get_end() + RIGHT, LEFT, buff=0.1
        )

        self.remove(tang)

        with self.voiceover(
            "The velocity vector shares the tangent's direction; "
            "its magnitude is the instantaneous speed."
        ):
            self.play(Create(vec_v), Write(lbl_v))
            self.wait(2)


# ══════════════════════════════════════════════════════════════════════════════
#  Scene 3 – Animated particle + velocity stamps → v(t) graph
#
#  Velocity field:  v(t) = V_SCALE · (t+1) · γ'(t)
#  Rate-func:       s(t) = ln(t+1)/ln 2  →  t(s) = 2^s − 1
# ══════════════════════════════════════════════════════════════════════════════

class Scene3(Scene):
    def construct(self):

        # ── Left: path axes + dashed Bézier curve ─────────────────────────────
        ax = make_axes([0, 3, 1], [0, 3, 1], x_len=3, y_len=3)
        lbl_ax = ax.get_axis_labels(x_label=MathTex("x"), y_label=MathTex("y"))

        crv_path = DashedVMobject(
            ax.plot_parametric_curve(bez, t_range=[0, 1], color=GOLD),
            num_dashes=40,
        )

        # grp_stamp collects ghost arrows; it lives *inside* grp_ax_crv so it
        # transforms with the axes automatically.
        grp_stamp   = VGroup()
        grp_ax_crv  = VGroup(ax, lbl_ax, crv_path, grp_stamp)

        self.play(Create(ax), Create(lbl_ax), Create(crv_path), run_time=3)
        self.play(grp_ax_crv.animate.shift(DOWN), run_time=2)
        self.wait(0.5)

        # ── Animated particle ────────────────────────────────────────────────
        trk_t = ValueTracker(0.0)

        dot_live   = always_redraw(lambda: path_dot(ax, trk_t.get_value(), r=0.08))

        self.play(FadeIn(dot_live))

        # Ghost-stamp updater (stamps at equal time intervals)
        nxt_snap_idx = [0]
        grp_vel_stamps = VGroup()   # velocity arrows only, for later transfer
        stamp_times = list(_STAMP_TIMES)  # Copy of actual times for later reference

        def _stamp(mob: Mobject) -> None:
            t = trk_t.get_value()
            while nxt_snap_idx[0] < len(_STAMP_T_VALUES) and t >= _STAMP_T_VALUES[nxt_snap_idx[0]]:
                t_stamp = _STAMP_T_VALUES[nxt_snap_idx[0]]
                
                grp_stamp.add(path_dot(ax, t_stamp, color=RED_C, r=0.04))
                grp_stamp.add(vel_arrow(ax, t_stamp, color=YELLOW_E))
                grp_vel_stamps.add(vel_arrow(ax, t_stamp, color=YELLOW_E))
                nxt_snap_idx[0] += 1

        dot_live.add_updater(_stamp)

        self.play(
            trk_t.animate.set_value(vel_rate(1.0)),
            run_time=ANIM_TIME,
            rate_func=linear,
        )
        dot_live.remove_updater(_stamp)
        self.wait(2)

        # ── Shift path diagram to the left ────────────────────────────────────
        grp_vel_path = VGroup(grp_ax_crv, dot_live, grp_vel_stamps)
        self.play(grp_vel_path.animate.to_edge(LEFT, buff=1), run_time=2)

        # ── Right: v(t) graph axes ────────────────────────────────────────────
        ax_vt = make_axes([0, ANIM_TIME, 1], [0, 4, 1], x_len=4, y_len=4)
        lbl_vt = ax_vt.get_axis_labels(
            x_label=MathTex(r"\text{time (s)}"), y_label=MathTex("v(t)")
        )
        grp_vt = VGroup(ax_vt, lbl_vt)
        grp_vt.move_to(ax_vt.get_right())
        self.play(Create(grp_vt), run_time=2)

        # ── Transfer velocity stamps → upright arrows on v(t) axes ───────────
        for i, arrow in enumerate(grp_vel_stamps):
            # Rotate each stamp to vertical (so length encodes speed)
            direction = arrow.get_end() - arrow.get_start()
            self.play(
                arrow.animate.rotate(
                    PI / 2 - angle_of_vector(direction),
                    about_point=arrow.get_start(),
                ),
                run_time=0.3,
            )
            # Slide to the correct time position on the v(t) axes
            if i < len(stamp_times):
                t_pos = stamp_times[i]
            else:
                t_pos = (i + 1) * TIME_SNAP
            tgt   = ax_vt.c2p(t_pos, 0)
            # Move arrow so its base is at the target position on v(t) axes
            shift_vec = tgt - arrow.get_start()
            self.play(arrow.animate.shift(shift_vec), run_time=0.5)

        # ── Draw smooth v(t) curve through the stamps ─────────────────────────
        # Map from curve parameter t to actual animation time
        def time_speed_curve(t: float) -> np.ndarray:
            # Find what animation progress s gives vel_rate(s) = t
            s = np.interp(t, _T_TABLE, _S_TABLE)
            actual_time = s * ANIM_TIME
            speed = np.linalg.norm(vel(t))
            return np.array([actual_time, speed, 0])
        
        crv_vt = ax_vt.plot_parametric_curve(
            time_speed_curve,
            t_range=[0, vel_rate(1.0)],
            color=GOLD,
        )
        self.play(Create(crv_vt), run_time=2)
        self.wait(2)


# ══════════════════════════════════════════════════════════════════════════════
#  Scene 4 – Hodograph & Acceleration
#
#  A hodograph is the curve traced by the *tip* of v(t) when all velocity
#  vectors share a common tail at the origin of velocity space.
#  The tangent to the hodograph at any point equals the instantaneous
#  acceleration  a(t) = dv/dt.
# ══════════════════════════════════════════════════════════════════════════════

class Scene4(Scene):

    # ── Helpers (use self.ax_hodo so they work in scene-space) ───────────────

    def _hodo_pt(self, t: float) -> np.ndarray:
        """Tip of the velocity vector in hodograph-axes scene space."""
        return self.ax_hodo.c2p(*vel(t)[:2])

    def _hodo_arrow(
        self, t: float, color=YELLOW_E, sw: float = 2.5,
    ) -> Arrow:
        """Velocity arrow in hodograph space (tail at origin, tip at v(t))."""
        O = self.ax_hodo.c2p(0, 0)
        return Arrow(O, self._hodo_pt(t), buff=0, color=color,
                     stroke_width=sw, max_tip_length_to_length_ratio=0.14)

    def _acc_arrow(
        self, t: float, a_scale: float = 0.4,
        color=PURPLE, sw: float = 2.5,
    ) -> Arrow:
        """
        Acceleration arrow at hodograph point v(t).
        The tail is at v(t); the tip is shifted by a_scale·a(t) in
        velocity space.
        """
        tail = self._hodo_pt(t)
        tip  = self.ax_hodo.c2p(*(vel(t) + a_scale * acc(t))[:2])
        return Arrow(tail, tip, buff=0, color=color,
                     stroke_width=sw, max_tip_length_to_length_ratio=0.14)

    # ── Main ─────────────────────────────────────────────────────────────────

    def construct(self):

        # ── Left: velocity-path diagram (reused from Scene3) ──────────────────
        grp_vel_path, _ = build_vel_path_scene()
        grp_vel_path.shift(DOWN*2)

        self.play(Create(grp_vel_path), run_time=2)
        self.play(grp_vel_path.animate.to_edge(LEFT, buff=0.5), run_time=2)
        self.wait(1)

        # ── Right: hodograph axes in velocity space ────────────────────────────
        # Velocity components range: vx ≈ [0, 1],  vy ≈ [-1, 5]
        self.ax_hodo = make_axes(
            x_range=[0, 3, 1],
            y_range=[-1, 3, 1],
            x_len=3, y_len=4,
            include_tip=False
        )

        self.ax_hodo.move_to(DOWN)

        ax_hodo_lbl_x = self.ax_hodo.x_axis.get_right() + RIGHT * 0.15
        ax_hodo_lbl_y = self.ax_hodo.y_axis.get_top() + UP * 0.15

        lbl_hodo = VGroup(
            MathTex(r"v_x", font_size=24).move_to(ax_hodo_lbl_x),
            MathTex(r"v_y", font_size=24).move_to(ax_hodo_lbl_y),
        )

        grp_hodo_axes = VGroup(self.ax_hodo, lbl_hodo)
        grp_hodo_axes.to_edge(RIGHT, buff=0.8).shift(DOWN * 0.5)


        self.play(Create(grp_hodo_axes), run_time=2)

        # ── Bring stamp arrows from left graph → hodograph arrows ────────────
        src_stamp_arrows = VGroup(
            *[mob for mob in grp_vel_path[1] if isinstance(mob, Arrow)]
        )
        grp_hodo_vecs = VGroup(*[self._hodo_arrow(t) for t in _STAMP_T_VALUES])


        self.play(
            LaggedStart(
                *[
                    TransformFromCopy(src_arrow, hodo_arrow)
                    for src_arrow, hodo_arrow in zip(src_stamp_arrows, grp_hodo_vecs)
                ],
                lag_ratio=0.25,
            ),
            run_time=3,
        )
        self.wait(1)

        # ── Hodograph curve – locus of velocity-vector tips ───────────────────
        crv_hodo = self.ax_hodo.plot_parametric_curve(
            lambda t: np.array([vel(t)[0], vel(t)[1], 0]),
            t_range=[0.0, vel_rate(1.0)],
            color=BLUE,
            stroke_width=3,
        )

        lbl_crv_hodo = Text("hodograph", font_size=18, color=BLUE).next_to(
            self._hodo_pt(0.9), RIGHT, buff=0.12
        )

        self.play(Create(crv_hodo), run_time=2)
        self.play(Write(lbl_crv_hodo))
        self.wait(1)
        self.play(FadeOut(lbl_crv_hodo))
        self.wait(0.5)

        # ── Two points on hodograph: v(tA) and v(tB) ─────────────────────────
        tA = _STAMP_T_VALUES[2]
        tB = _STAMP_T_VALUES[3]

        pt_vA = self._hodo_pt(tA)
        pt_vB = self._hodo_pt(tB)

        dot_vA = Dot(pt_vA, color=RED,    radius=0.07)
        dot_vB = Dot(pt_vB, color=ORANGE, radius=0.07)
        lbl_vA = MathTex(r"\vec{v}(t)", font_size=22, color=YELLOW).next_to(pt_vA, RIGHT,  buff=0.1)
        lbl_vB = MathTex(r"\vec{v}(t+\Delta t)", font_size=22).next_to(pt_vB, UP, buff=0.1)

        self.play(FadeIn(dot_vA), Write(lbl_vA))
        self.play(FadeIn(dot_vB), Write(lbl_vB))
        self.play(FadeOut(lbl_vB))

        # ── Δv vector ─────────────────────────────────────────────────────────
        vec_dv = Arrow(
            pt_vA, pt_vB, buff=0, color=GREEN,
            stroke_width=2.5, max_tip_length_to_length_ratio=0.14,
        )
        lbl_dv = MathTex(r"\Delta\vec{v}", font_size=22, color=GREEN).next_to(pt_vB, UP, buff=0.1)

        self.play(GrowArrow(vec_dv), Write(lbl_dv))
        self.wait(0.5)
        self.remove(vec_dv, lbl_dv)

        # ── Average acceleration ───────────────────────────────────────────────
        lbl_avg_acc = MathTex(
            r"\vec{a}_{\text{avg}} = \frac{\Delta\vec{v}}{\Delta t}",
            font_size=26,
        ).to_edge(DOWN, buff=0.6)
        lbl_avg_acc[0][0:2].set_color(GREEN)

        self.play(Write(lbl_avg_acc))
        self.wait(1)

        # ── Instantaneous acceleration (limit) ────────────────────────────────
        lbl_inst_acc = MathTex(
            r"\vec{a} = \lim_{\Delta t \to 0}"
            r"\frac{\Delta\vec{v}}{\Delta t} = \frac{d\vec{v}}{dt}",
            font_size=26,
        ).to_edge(DOWN, buff=0.6)
        lbl_inst_acc[0][0:2].set_color(GREEN)

        self.play(Transform(lbl_avg_acc, lbl_inst_acc))
        self.wait(1)

        # ── Animate tB → tA to show Δv shrinking to zero ──────────────────────
        trk_tB = ValueTracker(tB)

        dot_vB_live = always_redraw(
            lambda: Dot(self._hodo_pt(trk_tB.get_value()), color=ORANGE, radius=0.07)
        )
        vec_dv_live = always_redraw(
            lambda: Arrow(
                pt_vA, self._hodo_pt(trk_tB.get_value()),
                buff=0, color=GREEN,
                stroke_width=2.5, max_tip_length_to_length_ratio=0.14,
            )
        )
        vec_v_live = always_redraw(
            lambda: Arrow(
                self.ax_hodo.c2p(0, 0), self._hodo_pt(trk_tB.get_value()),
                buff=0, color=YELLOW_E,
                stroke_width=2.5, max_tip_length_to_length_ratio=0.14,
            )
        )

        lbl_dv_live = always_redraw(lambda:
            MathTex(r"\Delta\vec{v}", font_size=22, color=GREEN).next_to(dot_vB_live, UP, buff=0.1))
        lbl_v_live = always_redraw(lambda:
            MathTex(r"\vec{v}(t+ \Delta t)", font_size=22, color=YELLOW_E).next_to(
                dot_vB_live, RIGHT, buff=0.1
            ))


        self.remove(dot_vB, vec_dv, lbl_dv)
        self.add(dot_vB_live, vec_dv_live, vec_v_live, lbl_dv_live, lbl_v_live)


        self.play(trk_tB.animate.set_value(tA + 0.01), run_time=3, rate_func=linear)
        self.remove(dot_vB_live, vec_dv_live, vec_v_live, lbl_vB, lbl_dv_live, lbl_v_live)
        self.wait(0.5)

        # ── Tangent to hodograph at tA = direction of a(tA) ───────────────────
        # The tangent direction in hodograph space (velocity space)
        _dv_dir  = vel(tA + 0.0001) - vel(tA)
        _tang_ang = np.arctan2(_dv_dir[1], _dv_dir[0])

        tang_hodo = Line(
            pt_vA - 0.35 * np.array([np.cos(_tang_ang), np.sin(_tang_ang), 0]),
            pt_vA + 0.35 * np.array([np.cos(_tang_ang), np.sin(_tang_ang), 0]),
            color=YELLOW, stroke_width=2.5,
        )

        self.play(Create(tang_hodo))
        self.wait(0.5)

        # ── Acceleration vector at tA ─────────────────────────────────────────
        vec_acc_A = self._acc_arrow(tA, a_scale=0.25)
        lbl_acc   = MathTex(r"\vec{a}", font_size=24, color=PURPLE).next_to(
            vec_acc_A.get_end(), UR, buff=0.08
        )

        self.play(Transform(tang_hodo, vec_acc_A))
        self.play(Write(lbl_acc))
        self.wait(1)

        # ── Live acceleration arrow as tA sweeps along hodograph ─────────────
        trk_tA = ValueTracker(tA)

        dot_vA_live  = always_redraw(
            lambda: Dot(self._hodo_pt(trk_tA.get_value()), color=RED, radius=0.07)
        )
        vec_vacc_live = always_redraw(
            lambda: self._acc_arrow(trk_tA.get_value(), a_scale=0.25)
        )

        lbl_acc_live = always_redraw(lambda: MathTex(
            r"\vec{a}", font_size=24, color=PURPLE
        ).next_to(vec_vacc_live.get_end(), UR, buff=0.08))

        # corresponing v(t) dot and label for clarity
        vec_v_live = always_redraw(
            lambda: Arrow(
                self.ax_hodo.c2p(0, 0), self._hodo_pt(trk_tA.get_value()),
                buff=0, color=YELLOW_E,
                stroke_width=2.5, max_tip_length_to_length_ratio=0.14,
            )
        )
        lbl_v_live = always_redraw(lambda:
            MathTex(r"\vec{v}(t)", font_size=22, color=YELLOW_E).next_to(
                dot_vA_live, RIGHT, buff=0.1
            ))
        

        self.remove(dot_vA, tang_hodo, vec_acc_A, lbl_acc, lbl_vA)
        self.add(dot_vA_live, vec_vacc_live, lbl_acc_live, vec_v_live, lbl_v_live)

        self.play(
            trk_tA.animate.set_value(0.75),
            run_time=4,
            rate_func=there_and_back,
        )
        self.wait(0.5)
        self.remove(vec_vacc_live, lbl_acc_live)

        # ── Final formula banner ───────────────────────────────────────────────
        lbl_final = MathTex(
            r"\vec{a}(t) = \frac{d\vec{v}}{dt} = \frac{d^2\vec{r}}{dt^2}",
            font_size=30,
        ).to_edge(DOWN, buff=0.5)
        lbl_final[0][0:3].set_color(PURPLE)

        self.play(Transform(lbl_avg_acc, lbl_final))
        self.wait(3)