from manim import *
from reactive_manim import *  # for math labels that update with moving points
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
import numpy as np
from sympy import integrate
import sympy

# ──────────────────────────────────────────
# Scene 1 (placeholder)
# ──────────────────────────────────────────
class Intro(VoiceoverScene):
    pass

# ──────────────────────────────────────────
# Scene 2 – Position vector, Δr and Δs
# ──────────────────────────────────────────
class Scene2(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService())
        axes_ptn = Axes(
            x_range=[0, 3, 1],
            y_range=[0, 3, 1],
            x_length=3,
            y_length=3,
            axis_config={
                "color": GREY_B,
                "stroke_width": 2.5,
                "include_tip": True,
                "tip_length": 0.15,
            },
        )
        axes_ptn_lbl = axes_ptn.get_axis_labels(
            x_label=MathTex("x").shift(DOWN),
            y_label=MathTex("y").shift(LEFT)
        )
        group_axes_ptn = VGroup(axes_ptn, axes_ptn_lbl)
        group_axes_ptn.move_to(DOWN)


        # rectrangular coordinate axes
        with self.voiceover("Here we define a path in rectangular coordinates."):
            self.play(Create(group_axes_ptn), run_time=2)

        # curve path of particle
        def curve_pt(t):
            start_point     = np.array([1.5, 1.8, 0])
            control_point_1 = np.array([1.8, 1.1, 0])
            control_point_2 = np.array([3.5, 1.5, 0])
            end_point       = np.array([4,   4,   0])
            return (
                (1 - t) ** 3 * start_point
                + 3 * (1 - t) ** 2 * t * control_point_1
                + 3 * (1 - t) * t ** 2 * control_point_2
                + t ** 3 * end_point
            )

        curve_mob = axes_ptn.plot_parametric_curve(curve_pt, t_range=[0, 1], color=GOLD)

        path_lbl = Text(
            "path of motion", font_size=22, color=GOLD_A
        ).next_to(curve_pt(1), LEFT + DOWN * 4, buff=0.15)

        with self.voiceover("Let's define a path function s of x and y in this coordinate system"):
            self.play(Create(curve_mob), run_time=3)
            self.play(Write(path_lbl), run_time=1)
            self.wait(0.5)

        path_label = Text(
            "path of motion", font_size=22, color=GOLD_A
        ).next_to(curve_pt(1), LEFT + DOWN * 4, buff=0.15)
        self.play(Write(path_label), run_time=1)
        self.wait(0.5)
        self.remove(path_label)

        def get_pt(t):
            return axes_ptn.c2p(*curve_pt(t)[:2])

        # ── animated dot tracing the curve ──────────────────────────────────
        t_tracker = ValueTracker(0)
        dot_trace = always_redraw(
            lambda: Dot(get_pt(t_tracker.get_value()), color=RED, radius=0.07)
        )
        
        with self.voiceover("Particle moves along this path"):
            self.play(Create(dot_trace), run_time=1)
            self.wait(0.5)

        with self.voiceover("as the time moving forward, it moves toward the right"):
            self.play(t_tracker.animate.set_value(1), run_time=2, rate_func=linear)
            self.wait(0.5)
            self.remove(dot_trace)

        # ── static points P and P' ──────────────────────────────────────────
        pt_P  = get_pt(0.1)
        pt_Pp = get_pt(0.4)

        # BUG 2 FIX: the original code added a *static* dot_P via self.add(),
        #            then immediately re-assigned the name `dot_P` to an
        #            always_redraw version — leaving a phantom static dot on
        #            screen for the rest of the scene.
        #            Fix: use separate, clearly named variables.
        dot_P  = Dot(pt_P,  color=RED, radius=0.07)
        lbl_P  = MathTex("P",  font_size=30).next_to(pt_P,  UR,  buff=0.1)
        dot_Pp = Dot(pt_Pp, color=RED, radius=0.07)
        lbl_Pp = MathTex("P'", font_size=30).next_to(pt_Pp, UP,  buff=0.1)

        self.play(FadeIn(dot_P), Write(lbl_P), run_time=1)

        # animate a separate moving dot from P → P' to show the motion interval
        tracker_P   = ValueTracker(0.1)
        dot_moving  = always_redraw(
            lambda: Dot(get_pt(tracker_P.get_value()), color=RED, radius=0.07)
        )
        with self.voiceover("We will study the motion of particle P,"):
            self.add(dot_moving)
            
        with self.voiceover("the particle travels from P to P prime"):
            self.play(tracker_P.animate.set_value(0.4), run_time=2)
            self.remove(dot_moving)   
            self.add(dot_Pp)                     # done animating; show static P'
            self.play(Write(lbl_Pp), run_time=1)
            self.wait(0.5)

        # ── Δt label ────────────────────────────────────────────────────────
        lbl_dt = MathTex(r"\Delta t", font_size=28).next_to(pt_Pp, DL * 2, buff=0.1)


        # ── highlighted arc P→P' and Δs label ───────────────────────────────
        pathPPp  = axes_ptn.plot_parametric_curve(
            curve_pt, t_range=[0.1, 0.4], color=BLUE, stroke_width=6
        )
        path_lbl = MathTex(r"\Delta s", font_size=24, color=BLUE).next_to(
            pt_Pp, DL * 2, buff=0.1
        )

        # ── average speed ────────────────────────────────────────────────────
        del_s_t = VGroup(lbl_dt, path_lbl)

        lbl_avg_speed      = MathTex(r"\frac{\Delta s}{\Delta t}",
                                     font_size=24).next_to(pt_Pp, DL * 2, buff=0.1)
        comp_lbl_avg_speed = MathTex(r"v_{\text{avg}} = \frac{\Delta s}{\Delta t}",
                                     font_size=24).next_to(pt_Pp, DL * 2, buff=0.1)

        # BUG 3 FIX: after Transform(A, B), A is the mobject that lives in the
        #            scene (now *looking* like B); B itself is never added.
        #            The original code then tried Transform(lbl_avg_speed, …)
        #            and FadeOut(lbl_avg_speed), but lbl_avg_speed was never
        #            in the scene — del_s_t is the mobject to keep transforming.

        with self.voiceover("in finite time interval Delta t."):
            self.play(Write(lbl_dt), run_time=1)

        with self.voiceover("covering a path length Delta s."):
            self.play(FadeOut(lbl_dt), Create(pathPPp))   
            self.play(Write(path_lbl), run_time=1)
            self.wait(0.5)

        tracker = self.add_voiceover_text(
            "both of this are scalar quantities, so we can write them as a ratio"
        )
        self.wait(tracker.get_remaining_duration(buff=0.5))

        with self.voiceover("quanityDelta s over Delta t, resulting scaler quanity"):
            self.play(Transform(del_s_t, lbl_avg_speed),    run_time=1)


        with self.voiceover("is the average speed"):
            self.play(Transform(del_s_t, comp_lbl_avg_speed), run_time=1)
            self.wait(2)
            self.play(FadeOut(del_s_t), FadeOut(pathPPp),   run_time=0.5)

        # ── position vector r ────────────────────────────────────────────────
        O = axes_ptn.c2p(0, 0)
        vec_r = Arrow(
            O, pt_P, color=RED, buff=0,
            stroke_width=2.5, max_tip_length_to_length_ratio=0.07
        )
        lbl_r = MathTex(r"\vec{r}", font_size=32, color=RED).next_to(
            vec_r.point_from_proportion(0.6), LEFT, buff=0.12
        )

        # BUG 4 FIX: lbl_r was created but never added to the scene before
        #            Transform(lbl_r, or_lbl_r) was called on it, so nothing
        #            visible happened.  Also, both labels showed the same
        #            \vec{r} — the original had \mathbf{r} vs \vec{r} as the
        #            "before/after" pair, which makes the transform meaningful.
        #            Fixed by writing lbl_r (\mathbf{r}) first, then
        #            transforming to or_lbl_r (\vec{r}).
        lbl_r_bold = MathTex(r"\mathbf{r}", font_size=32, color=RED).next_to(
            vec_r.point_from_proportion(0.6), LEFT, buff=0.12
        )

        with self.voiceover("We draw a vecotor form origin to point P, called position vector r."):
            self.play(Create(vec_r), Write(lbl_r_bold), run_time=1)

        with self.voiceover("We can also write it in arrow notation."):
            self.play(Transform(lbl_r_bold, lbl_r), run_time=1)   # bold → arrow notation

        # ── position vector r + Δr ──────────────────────────────────────────
        vec_rdr = Arrow(
            O, pt_Pp, color=BLUE, buff=0,
            stroke_width=2.5, max_tip_length_to_length_ratio=0.07
        )
        lbl_rdr = MathTex(r"\vec{r}", r"+", r"\Delta\vec{r}", font_size=28).next_to(
            vec_rdr.point_from_proportion(0.6), DR, buff=0.012
        )
        lbl_rdr[0].set_color(RED)
        lbl_rdr[2].set_color(GREEN)

        with self.voiceover("Similarly, we draw a vector from the origin to point P prime, called the position vector r plus Delta r."):
            self.play(Create(vec_rdr), run_time=1)
            self.play(Create(lbl_rdr),  run_time=1)

        # ── displacement vector Δr ──────────────────────────────────────────
        vec_dr = Arrow(
            pt_P, pt_Pp, color=GREEN, buff=0,
            stroke_width=2.5, max_tip_length_to_length_ratio=0.14
        )
        lbl_dr = MathTex(r"\Delta\vec{r}", font_size=28, color=GREEN).next_to(
            vec_dr.get_end() + RIGHT, LEFT, buff=0.1
        )
        
        with self.voiceover("the difference in position vecotor r"):
            self.play(Indicate(lbl_r))

        with self.voiceover("and r plus Delta r"):
            self.play(Indicate(lbl_rdr[0]), Indicate(lbl_rdr[2]))

        with self.voiceover("is displacement vector Delta r."):
            self.play(Create(vec_dr), run_time=1)
            self.play(Write(lbl_dr),  run_time=1)


        lbl_avg_vel = MathTex(
            r"\frac{\Delta\vec{r}}{\Delta t} = \text{average velocity}",
            font_size=28
        ).next_to(lbl_dr, DR, buff=0.1)
        lbl_avg_vel[0][0:2].set_color(GREEN)
        lbl_avg_vel[0][3:5].set_color(WHITE)

        self.remove(lbl_dr)

        with self.voiceover("the ratio of displacement vector Delta r over time interval Delta t is a vector quanity, called average velocity."):
            self.play(Write(lbl_avg_vel), run_time=1)

        # ── instantaneous velocity ──────────────────────────────────────────
        lbl_limit_vel = MathTex(
            r"\lim_{\Delta t \to 0} \frac{\Delta\vec{r}}{\Delta t}"
            r"= \text{instantaneous velocity}",
            font_size=28
        ).next_to(lbl_dr, DR, buff=0.1)

        lbl_limit_vel[0][0:2].set_color(GREEN)
        lbl_limit_vel[0][3:5].set_color(WHITE)

        # show instantaneous-velocity label first
        with self.voiceover("if we shrink the time interval Delta t to zero, the ratio of Delta r over Delta t approaches a limit, which is called instantaneous velocity."):
            self.play(Transform(lbl_avg_vel, lbl_limit_vel), run_time=1)


        self.remove(lbl_avg_vel)

        
        # move P' toward P to show the limit process: remove static copies
        self.remove(vec_rdr, vec_dr, lbl_rdr, lbl_dr, dot_Pp, lbl_Pp)

        tracker_Pp = ValueTracker(0.4)

        dotPp_moving = always_redraw(
            lambda: Dot(get_pt(tracker_Pp.get_value()), color=RED, radius=0.07)
        )

        # dotPp_lbl = always_redraw(
        #     lambda: MathTex("P'", font_size=30).next_to(get_pt(tracker_Pp.get_value()), UP, buff=0.1)
        # )
        vec_rdr_moving = always_redraw(
            lambda: Arrow(
                O,
                get_pt(tracker_Pp.get_value()),
                color=BLUE,
                buff=0,
                stroke_width=2.5,
                max_tip_length_to_length_ratio=0.07,
            )
        )
        # lbl_rdr_moving = always_redraw(
        #     lambda: MathTex(r"\vec{r}", r"+", r"\Delta\vec{r}", font_size=28).next_to(
        #         vec_rdr_moving.point_from_proportion(0.6), DR, buff=0.012
        #     )
        # )
        vec_dr_moving = always_redraw(
            lambda: Arrow(
                pt_P,
                get_pt(tracker_Pp.get_value()),
                color=GREEN,
                buff=0,
                stroke_width=2.5,
                max_tip_length_to_length_ratio=0.14,
            )
        )
        # lbl_dr_moving = always_redraw(
        #     lambda: MathTex(r"\Delta\vec{r}", font_size=28, color=GREEN).next_to(
        #         vec_dr_moving.get_end() + RIGHT, LEFT, buff=0.1
        #     )
        # )

        self.add(dotPp_moving, vec_rdr_moving, vec_dr_moving)

        with self.voiceover("As point P prime approaches P, r plus Delta r collapses to r, and Delta r tends to zero."):
            self.play(FadeOut(dot_Pp))  # remove static P prime to avoid confusion with moving dot
            self.play(tracker_Pp.animate.set_value(0.1), run_time=2, rate_func=linear)
            self.remove(dotPp_moving, vec_dr_moving)

        self.play(
            FadeOut(vec_dr_moving),
            run_time=1,
        )

        # tangnet line at P to show the direction of instantaneous velocity
        tangent_line = Line(
            start=pt_P - RIGHT * 0.5,
            end=pt_P + RIGHT * 0.5,
            color=YELLOW,
            stroke_width=2.5,
        ).rotate(
            angle=np.arctan2(
                curve_pt(0.1 + 0.01)[1] - curve_pt(0.1)[1],
                curve_pt(0.1 + 0.01)[0] - curve_pt(0.1)[0],
            ),
            about_point=pt_P
        )
        with self.voiceover("the instantaneous velocity has the same direction as the tangent line to the curve at point P."):
            self.play(Create(tangent_line), run_time=1)

        self.remove(dotPp_moving, vec_rdr_moving, lbl_limit_vel)
        # leave the original static P and its label in place
        self.wait(0.5)

        lbl_ds_dt = MathTex(
            r"\frac{d\vec{r}}{dt} = \vec{v}",
            font_size=28
        ).next_to(lbl_dr, DR, buff=0.1)

        with self.voiceover("we can also write it in derivative notation, as d r over d t."):
            self.play(Create(lbl_ds_dt), run_time=1)

        # replacing tangent line by velocity vector to show they have the same direction
        # by dash line bcz magniture is unknown
        vec_v = Arrow(
            pt_P, pt_P + RIGHT * 0.5, color=YELLOW, buff=0,
            stroke_width=2.5, max_tip_length_to_length_ratio=0.14,
        ).rotate(
            angle=np.arctan2(
                curve_pt(0.1 + 0.01)[1] - curve_pt(0.1)[1],
                curve_pt(0.1 + 0.01)[0] - curve_pt(0.1)[0],
            ),
            about_point=pt_P
        )
        lbl_v = MathTex(r"\vec{v}", font_size=28, color=YELLOW).next_to(
            vec_v.get_end() + RIGHT, LEFT, buff=0.1
        )
        self.remove(tangent_line)

        # from this path plot we can only get the direction of direciton but no magniture
        with self.voiceover("the velocity vector has the same direction as the tangent line, and its magnitude is the instantaneous speed."):
            self.play(Create(vec_v), Write(lbl_v), run_time=1)
            self.wait(2)

        ## also at infintesamlly time interval, del s and ds are equal
        ## so magnitude of vec v gives the speed at that instnat 

"""
Scene3 – Particle moving along a Bézier curve at a physically-correct speed.

Velocity field:  v(t) = SCALE · (t+1) · γ'(t)
  where γ(t) is the Bézier curve and γ'(t) is its analytic tangent.

Rate-function derivation
────────────────────────
We want  dγ/dτ = v(t),  so
    dγ/dt · dt/dτ = SCALE·(t+1)·γ'(t)
    ⟹  dt/dτ = SCALE·(t+1)
    ⟹  τ(t)  = ∫₀ᵗ dt'/(SCALE·(t'+1)) = ln(t+1)/SCALE

Normalise by τ(1) = ln 2 / SCALE:
    s(t) = ln(t+1)/ln 2      (normalised progress, s ∈ [0,1])
    t(s) = 2^s − 1            (inverse → used as rate_func)
"""

from manim import *
import numpy as np

# ── Bézier control points (data-space coordinates) ───────────────────────────
P0 = np.array([1.5, 1.8, 0])
P1 = np.array([1.8, 1.1, 0])
P2 = np.array([3.5, 1.5, 0])
P3 = np.array([4.0, 4.0, 0])

VELOCITY_SCALE = 0.3   # global speed multiplier
SNAP_INTERVAL  = 0.1   # leave a ghost arrow every Δt = 0.1 along the curve


# ── Pure functions (no Manim state) ──────────────────────────────────────────

def bezier(t: float) -> np.ndarray:
    """Cubic Bézier position at parameter t ∈ [0, 1]."""
    u = 1.0 - t
    return u**3*P0 + 3*u**2*t*P1 + 3*u*t**2*P2 + t**3*P3


def bezier_tangent(t: float) -> np.ndarray:
    """Analytic derivative  dγ/dt  of the cubic Bézier (no finite differences)."""
    u = 1.0 - t
    return 3.0 * (
        u**2 * (P1 - P0)
        + 2*u*t * (P2 - P1)
        + t**2  * (P3 - P2)
    )


def velocity(t: float) -> np.ndarray:
    """Velocity vector  v(t) = SCALE·(t+1)·dγ/dt  in data-space."""
    return VELOCITY_SCALE * (t + 1.0) * bezier_tangent(t)


def velocity_rate(s: float) -> float:
    """
    Custom rate_func: normalised time s ∈ [0,1] → curve parameter t ∈ [0,1].

    Derived by inverting  s(t) = ln(t+1)/ln 2  →  t(s) = 2^s − 1.
    Passing this as rate_func makes the ValueTracker advance at the speed
    dictated by the velocity field rather than at constant speed.
    """
    return 2.0**s - 1.0


# Total physical animation time  T = ln(2) / SCALE
TOTAL_ANIM_TIME: float = np.log(2) / VELOCITY_SCALE


def build_velocity_path_scene() -> tuple[VGroup, VGroup]:
    """Rebuild the final Scene3 velocity-path composition for reuse in Scene4."""
    axes = Axes(
        x_range=[0, 3, 1],
        y_range=[0, 3, 1],
        x_length=3,
        y_length=3,
        axis_config={
            "color": GREY_B,
            "stroke_width": 2.5,
            "include_tip": True,
            "tip_length": 0.15,
        },
    )
    axis_labels = axes.get_axis_labels(
        x_label=MathTex("x"),
        y_label=MathTex("y"),
    )

    curve_mobj = DashedVMobject(
        axes.plot_parametric_curve(bezier, t_range=[0, 1], color=GOLD),
        num_dashes=40,
    )
    grp_axes_curve = VGroup(axes, axis_labels, curve_mobj)

    t_tracker = ValueTracker(0.8)
    live_dot = Dot(axes.c2p(*bezier(t_tracker.get_value())[:2]), color=RED, radius=0.08)
    live_arrow = Arrow(
        axes.c2p(*bezier(t_tracker.get_value())[:2]),
        axes.c2p(*(bezier(t_tracker.get_value()) + velocity(t_tracker.get_value()))[:2]),
        buff=0,
        color=YELLOW,
        stroke_width=2.5,
        max_tip_length_to_length_ratio=0.14,
    )

    next_snap = SNAP_INTERVAL
    vel_stamp = VGroup()
    while next_snap <= 0.8 + 1e-9:
        vel_stamp.add(
            Arrow(
                axes.c2p(*bezier(next_snap)[:2]),
                axes.c2p(*(bezier(next_snap) + velocity(next_snap))[:2]),
                buff=0,
                color=YELLOW_E,
                stroke_width=2.5,
                max_tip_length_to_length_ratio=0.14,
            )
        )
        next_snap += SNAP_INTERVAL

    grp_velocity_path = VGroup(grp_axes_curve, live_dot, live_arrow, vel_stamp)
    grp_velocity_path.to_edge(LEFT, buff=1)
    return grp_velocity_path, VGroup(axes, axis_labels, curve_mobj)


# ── Scene ─────────────────────────────────────────────────────────────────────

class Scene3(Scene):
    def construct(self):

        # ── Axes ──────────────────────────────────────────────────────────────
        axes = Axes(
            x_range=[0, 3, 1],
            y_range=[0, 3, 1],
            x_length=3,
            y_length=3,
            axis_config={
                "color":        GREY_B,
                "stroke_width": 2.5,
                "include_tip":  True,
                "tip_length":   0.15,
            },
        )
        axis_labels = axes.get_axis_labels(
            x_label=MathTex("x"),
            y_label=MathTex("y"),
        )
        
        # ── Local mobject constructors ─────────────────────────────────────────

        def make_arrow(t: float, color=YELLOW) -> Arrow:
            """Velocity arrow at curve parameter t."""
            tail = axes.c2p(*bezier(t)[:2])
            tip  = axes.c2p(*(bezier(t) + velocity(t))[:2])
            return Arrow(
                tail, tip,
                buff=0,
                color=color,
                stroke_width=2.5,
                max_tip_length_to_length_ratio=0.14,
            )

        def make_dot(t: float, color=RED, radius=0.05) -> Dot:
            """Small dot at curve position t."""
            return Dot(axes.c2p(*bezier(t)[:2]), color=color, radius=radius)

        # ── Phase 1: draw axes + curve ─────────────────────────────────────────


        curve_mobj = DashedVMobject(
            axes.plot_parametric_curve(bezier, t_range=[0, 1], color=GOLD),
            num_dashes=40,
        )

        self.play(Create(axes), Create(axis_labels), Create(curve_mobj), run_time=3)
        grp_axes_curve = VGroup(axes, axis_labels, curve_mobj)
        grp_stamp = VGroup()
        grp_axes_curve.add(grp_stamp)
        self.play(grp_axes_curve.animate.shift(DOWN), run_time=2)
        self.wait(0.5)

        # axes = grp_axes_curve[0]
        # axis_labels = grp_axes_curve[1]
        # curve_mobj = grp_axes_curve[2]

        # # ── Phase 2: preview – static velocity arrows at sample points ─────────
        # sample_ts     = np.arange(0.0, 1.0, SNAP_INTERVAL)
        # preview_dots  = VGroup(*[make_dot(t) for t in sample_ts])
        # preview_arrows = VGroup(*[make_arrow(t) for t in sample_ts])

        # self.play(
        #     LaggedStart(
        #         *[AnimationGroup(FadeIn(d), GrowArrow(a))
        #           for d, a in zip(preview_dots, preview_arrows)],
        #         lag_ratio=0.4,
        #     ),
        #     run_time=2,
        # )
        # self.wait(1)

        # # Fade out preview; the moving particle will stamp its own ghost arrows.
        # self.play(FadeOut(preview_dots, preview_arrows), run_time=0.6)

        # ── Phase 3: animated particle + live velocity arrow ───────────────────
        t_tracker = ValueTracker(0.0)

        live_dot = always_redraw(
            lambda: make_dot(t_tracker.get_value(), radius=0.08)
        )
        live_arrow = always_redraw(
            lambda: make_arrow(t_tracker.get_value())
        )

        self.play(FadeIn(live_dot), FadeIn(live_arrow))

        # Ghost-stamp updater: whenever t crosses a SNAP_INTERVAL boundary,
        # freeze a faded copy of the arrow and dot at that position.
        next_snap = [SNAP_INTERVAL]   # list cell so the closure can mutate it
        
        vel_stamp = VGroup()  # for debugging: show the velocity vector stamps separately from the position dots
        def stamp_ghost(_mob: Mobject) -> None:
            t = t_tracker.get_value()
            while next_snap[0] <= 1.0 + 1e-9 and t >= next_snap[0]:
                g = next_snap[0]
                # add stamps to grp_stamp so they follow grp_axes_curve transforms
                grp_stamp.add(make_dot(g,   color=RED_C,    radius=0.04))
                grp_stamp.add(make_arrow(g, color=YELLOW_E))
                next_snap[0] += SNAP_INTERVAL

                vel_stamp.add(make_arrow(g, color=YELLOW_E))  # for debugging: add to separate group to show velocity stamps only
        
        live_dot.add_updater(stamp_ghost)

        # Animate t from 0 → 1 using the velocity-derived rate function so that
        # the particle's on-screen speed matches the velocity field exactly.
        self.play(
            t_tracker.animate.set_value(0.8),
            run_time=TOTAL_ANIM_TIME,
            rate_func=velocity_rate,
        )

        live_dot.remove_updater(stamp_ghost)
        self.wait(2)

        grp_velocity_path = VGroup(grp_axes_curve, live_dot, live_arrow, vel_stamp)  # keep the ghost arrows but not the axis labels
        self.play(grp_velocity_path.animate.to_edge(LEFT, buff=1), run_time=2)

        # constructing velocity vs time graph is left as an exercise for the reader :)
        axes_velocity = Axes(
            x_range=[0, 4, 1],
            y_range=[0, 4, 1],
            x_length=4,
            y_length=4,
            axis_config={
                "color":        GREY_B,
                "stroke_width": 2.5,
                "include_tip":  True,
                "tip_length":   0.15,
            },
        )

        axis_vel_lbl = axes_velocity.get_axis_labels(
            x_label=MathTex("t"),
            y_label=MathTex("v(t)"),
        )

        grp_velocity_graph = VGroup(axes_velocity, axis_vel_lbl)
        grp_velocity_graph.move_to(axes_velocity.get_right() )

        self.play(Create(grp_velocity_graph), run_time=2)


        # vel_stamp_0 = vel_stamp[0]
        # # making it vertical for easier comparison with the velocity graph (which is left as an exercise to the reader)
        # direction = vel_stamp_0.get_end() - vel_stamp_0.get_start()
        # vel_stamp_0.rotate(PI / 2 - angle_of_vector(direction), about_point=vel_stamp_0.get_start())
        
        # t0 =SNAP_INTERVAL* axes_velocity.x_length / TOTAL_ANIM_TIME 
        # ptn1 = axes_velocity.c2p(t0, 0)  # start at origin of velocity graph
        # self.play(
        #     vel_stamp_0.animate.shift(ptn1 - vel_stamp_0.get_start()),
        #     run_time=1,
        # )
        
        # self.wait(1)

        # for rest of the velocity stamps, just move them to the right without changing their vertical position (which encodes the velocity magnitude)
        interval_scale = 4
        for i in range(0, len(vel_stamp)):
            arrow = vel_stamp[i]
            direction = arrow.get_end() - arrow.get_start()
            self.play(arrow.animate.rotate(PI / 2 - angle_of_vector(direction), about_point=arrow.get_start()))
            t_intv = (i+1) * SNAP_INTERVAL * interval_scale

            ptn = axes_velocity.c2p(t_intv, 0)

            self.play(
                arrow.animate.shift(ptn - arrow.get_start()),
                run_time=1,
            )

        def velocity_magnitude(t: float) -> np.ndarray:
            """Velocity vector  v(t) = SCALE·(t+1)·dγ/dt  in data-space."""
            return VELOCITY_SCALE * (t + 1.0) * bezier_tangent(t)
        
        curve_velocity = axes_velocity.plot_parametric_curve(
            lambda t: np.array([
                interval_scale * t,
                np.linalg.norm(velocity_magnitude(t)),
                0,
            ]),
            t_range=[0, 1],
            color=GOLD,
        )
        self.play(Create(curve_velocity), run_time=2)
        self.wait(2)
        
##
## here we make accleration Hodograph

##
class Scene4(Scene):
    def construct(self):
        ## in left we have curves
        grp_velocity_path, _ = build_velocity_path_scene()
        grp_velocity_path.shift(DOWN)
        
        self.play(Create(grp_velocity_path), run_time=2)
        self.play(grp_velocity_path.animate.to_edge(LEFT, buff=1), run_time=2)
        self.wait(2)
        