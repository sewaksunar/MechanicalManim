"""
Figure 16.13 – Two Rectangular Reference Frames (Manim)
=======================================================
• Fixed frame  : ThreeDAxes  O-xyz          (gold)
• Moving frame : ThreeDAxes  A-x'y'z'       (cyan)  ← rotated & shifted
                 embedded in rigid body B (translucent ellipsoid)
• Point P      : moves inside B along a Bezier curve
                 r_P = O->P (orange)   r_P/A = A->P (magenta)

How the moving ThreeDAxes is rotated:
  1. Create axes with ranges starting at 0 so all three axes extend
     in the +x/+y/+z direction from their common origin.
  2. apply_matrix(R)  – rotates the whole object using the Euler matrix.
  3. shift(A)         – moves the origin to world-point A.

All labels use add_fixed_orientation_mobjects → always face the camera.

Run:
    manim -pql figure_16_13.py Figure1613   # fast preview
    manim -pqh figure_16_13.py Figure1613   # HD
"""

from manim import *
import numpy as np


# ── colours ──────────────────────────────────────────────────────────────────
FIXED_COLOR  = GOLD
MOVING_COLOR = "#00D4FF"
BODY_COLOR   = "#7EC8E3"
OMEGA_COLOR  = GREEN_C
VA_COLOR     = RED_C
RA_COLOR     = YELLOW_E
RP_COLOR     = ORANGE
RPA_COLOR    = "#FF44FF"
P_COLOR      = WHITE


def _norm(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-10 else v


def _arr3d(start, end, color, res=6, thick=0.025, brad=0.045, ht=0.22):
    return Arrow3D(np.array(start, dtype=float),
                   np.array(end,   dtype=float),
                   color=color, resolution=res,
                   thickness=thick, base_radius=brad, height=ht)


def _thin(start, end, color):
    """Fast updatable 2-D arrow (r_P, r_P/A)."""
    return Arrow(np.array(start, dtype=float),
                 np.array(end,   dtype=float),
                 color=color, buff=0, stroke_width=3,
                 max_tip_length_to_length_ratio=0.12)


class Intro(ThreeDScene):

    # ── shift whole scene (Z < 0 → down on screen with phi=70°) ──────────────
    SCENE_SHIFT = np.array([0.0, 0.0, -1.0])

    # ── geometry ──────────────────────────────────────────────────────────────
    _A_LOCAL  = np.array([1.2, 0.8, 1.0])   # moving-frame origin relative to O
    BODY_AXES = 1.7                           # length of moving-frame axes
    TILT_X, TILT_Y, TILT_Z = 0.4, -0.3, 0.5

    BEZIER_LOCAL = np.array([               # P's path in body-local coords
        [ 0.30,  0.10,  0.10],
        [ 0.75,  0.45,  0.30],
        [ 0.35, -0.25,  0.45],
        [-0.15,  0.40, -0.20],
        [ 0.50,  0.20,  0.05],
    ])

    def construct(self):

        # ── camera ────────────────────────────────────────────────────────────
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)

        S  = self.SCENE_SHIFT
        O  = ORIGIN + S
        A  = self._A_LOCAL + S

        # ── rotation matrix for moving frame ──────────────────────────────────
        R = (
            rotation_matrix(self.TILT_Z, OUT)
            @ rotation_matrix(self.TILT_Y, UP)
            @ rotation_matrix(self.TILT_X, RIGHT)
        )
        i_p, j_p, k_p = R @ RIGHT, R @ UP, R @ OUT

        # ── Bezier helper ─────────────────────────────────────────────────────
        bz = np.array([R @ p + A for p in self.BEZIER_LOCAL])

        def bezier_pt(t):
            pts = bz.copy().astype(float)
            for _ in range(len(pts) - 1):
                pts = (1 - t) * pts[:-1] + t * pts[1:]
            return pts[0]

        # ═════════════════════════════════════════════════════════════════════
        # 1. FIXED FRAME  –  ThreeDAxes at O
        # ═════════════════════════════════════════════════════════════════════
        fixed_axes = ThreeDAxes(
            x_range=(-10, 50, 5),
            y_range=(-10, 10, 5),
            z_range=(-10, 10, 5),
            x_length=9,
            y_length=3,
            z_length=3,
            axis_config={
                "color": FIXED_COLOR,
                "stroke_width": 2,
                "include_tip": True,
                "tip_length": 0.20,
            },
        )
        fixed_axes.shift(O)

        fixed_labels = fixed_axes.get_axis_labels(
            x_label=MathTex(r"\mathbf{i}", color=FIXED_COLOR).scale(0.65),
            y_label=MathTex(r"\mathbf{j}", color=FIXED_COLOR).scale(0.65),
            z_label=MathTex(r"\mathbf{k}", color=FIXED_COLOR).scale(0.65),
        )

        lbl_O = MathTex("O", color=FIXED_COLOR).scale(0.60).move_to(O + [-0.3, -0.3, 0])
        lbl_x = MathTex("x", color=FIXED_COLOR).scale(0.50).move_to(
                    fixed_axes.x_axis.get_end() + [ 0.35, -0.20,  0.00])
        lbl_y = MathTex("y", color=FIXED_COLOR).scale(0.50).move_to(
                    fixed_axes.y_axis.get_end() + [ 0.20,  0.35,  0.00])
        lbl_z = MathTex("z", color=FIXED_COLOR).scale(0.50).move_to(
                    fixed_axes.z_axis.get_end() + [-0.20,  0.00,  0.35])

        # ═════════════════════════════════════════════════════════════════════
        # 2. MOVING FRAME  –  ThreeDAxes rotated by R and shifted to A
        #
        #    Strategy:
        #      • Use one-sided ranges [0, BL, step] so every axis starts at
        #        the shared origin and extends outward (no negative half).
        #      • apply_matrix(R)  →  rotates axes into body orientation.
        #      • shift(A)         →  moves origin to world-point A.
        # ═════════════════════════════════════════════════════════════════════
        BL   = self.BODY_AXES
        step = round(BL / 2, 2)

        moving_axes = ThreeDAxes(
            x_range=[0, BL, step],
            y_range=[0, BL, step],
            z_range=[0, BL, step],
            x_length=BL,
            y_length=BL,
            z_length=BL,
            axis_config={
                "color": MOVING_COLOR,
                "stroke_width": 2,
                "include_tip": True,
                "tip_length": 0.20,
                "include_ticks": False,    # cleaner look for a local frame
            },
        )
        # Rotate first, then translate
        moving_axes.apply_matrix(R)
        moving_axes.shift(A)

        # Tip positions in world space (after rotation + shift)
        ip_tip = A + BL * i_p
        jp_tip = A + BL * j_p
        kp_tip = A + BL * k_p

        # Labels at axis tips
        lbl_A  = MathTex("A",  color=MOVING_COLOR).scale(0.60).move_to(A + [ 0.22, -0.22,  0.10])
        lbl_ip = MathTex(r"\mathbf{i}'", color=MOVING_COLOR).scale(0.65).move_to(ip_tip + 0.40 * i_p)
        lbl_jp = MathTex(r"\mathbf{j}'", color=MOVING_COLOR).scale(0.65).move_to(jp_tip + 0.40 * j_p)
        lbl_kp = MathTex(r"\mathbf{k}'", color=MOVING_COLOR).scale(0.65).move_to(kp_tip + 0.40 * k_p)
        lbl_xp = MathTex("x'", color=MOVING_COLOR).scale(0.45).move_to(ip_tip + 0.78 * i_p)
        lbl_yp = MathTex("y'", color=MOVING_COLOR).scale(0.45).move_to(jp_tip + 0.78 * j_p)
        lbl_zp = MathTex("z'", color=MOVING_COLOR).scale(0.45).move_to(kp_tip + 0.78 * k_p)

        # ═════════════════════════════════════════════════════════════════════
        # 3. r_A
        # ═════════════════════════════════════════════════════════════════════
        r_A_arr = _arr3d(O, A, RA_COLOR)
        lbl_rA  = MathTex(r"\mathbf{r}_A", color=RA_COLOR).scale(0.60)
        lbl_rA.move_to((O + A) / 2 + [-0.38, 0, 0.25])

        # ═════════════════════════════════════════════════════════════════════
        # 4. Ellipsoid body B (low-res for speed)
        # ═════════════════════════════════════════════════════════════════════
        a_e, b_e, c_e = 1.5, 1.0, 0.7
        ellipsoid = Surface(
            lambda u, v: A + R @ np.array([
                a_e * np.sin(v) * np.cos(u),
                b_e * np.sin(v) * np.sin(u),
                c_e * np.cos(v),
            ]),
            u_range=[0, TAU], v_range=[0, PI],
            resolution=(12, 8),
            fill_color=BODY_COLOR, fill_opacity=0.20,
            stroke_color=BODY_COLOR, stroke_width=0.5, stroke_opacity=0.4,
        )
        lbl_B = MathTex(r"\mathcal{B}", color=BODY_COLOR).scale(0.80)
        lbl_B.move_to(A + R @ np.array([a_e * 0.5, b_e * 0.8, c_e * 0.5]) + [0.3, 0.3, 0])

        # ═════════════════════════════════════════════════════════════════════
        # 5. ω and v_A
        # ═════════════════════════════════════════════════════════════════════
        om_dir = _norm(np.array([-0.4, 0.6, 1.0]))
        om_end = A + 1.55 * om_dir
        om_arr = _arr3d(A, om_end, OMEGA_COLOR)
        lbl_om = MathTex(r"\boldsymbol{\omega}", color=OMEGA_COLOR).scale(0.65)
        lbl_om.move_to(om_end + [-0.35, 0.25, 0.15])

        va_dir = _norm(np.array([0.7, -0.3, -0.6]))
        va_end = A + 1.35 * va_dir
        va_arr = _arr3d(A, va_end, VA_COLOR)
        lbl_vA = MathTex(r"\mathbf{v}_A", color=VA_COLOR).scale(0.60)
        lbl_vA.move_to(va_end + [0.3, -0.25, -0.1])

        # ═════════════════════════════════════════════════════════════════════
        # 6. Point P + position vectors
        # ═════════════════════════════════════════════════════════════════════
        P0 = bezier_pt(0.0)

        dot_P = Sphere(radius=0.09, resolution=(6, 6))
        dot_P.set_color(P_COLOR)
        dot_P.move_to(P0)

        lbl_P    = MathTex("P", color=P_COLOR).scale(0.60).move_to(P0 + [0.22, 0.22, 0.10])
        r_P_mob  = _thin(O, P0, RP_COLOR)
        r_PA_mob = _thin(A, P0, RPA_COLOR)

        lbl_rP  = MathTex(r"\mathbf{r}_P",     color=RP_COLOR ).scale(0.58)
        lbl_rPA = MathTex(r"\mathbf{r}_{P/A}", color=RPA_COLOR).scale(0.58)

        def _midlbl(lbl, p1, p2, off):
            lbl.move_to(0.5 * (np.array(p1) + np.array(p2)) + np.array(off))

        _midlbl(lbl_rP,  O, P0, [-0.42, 0.15, 0.22])
        _midlbl(lbl_rPA, A, P0, [ 0.32, 0.15, 0.12])

        trace_pts = [bezier_pt(t) for t in np.linspace(0, 1, 40)]
        # path_curve visualization skipped for OpenGL compatibility
        # path_curve = OpenGLVMobject(stroke_color=P_COLOR, stroke_width=1.5, stroke_opacity=0.55)
        # path_curve.set_points_smoothly([np.array(p) for p in trace_pts])

        # ═════════════════════════════════════════════════════════════════════
        # ALL labels → face the camera at all times
        # ═════════════════════════════════════════════════════════════════════
        all_labels = [
            lbl_O, lbl_x, lbl_y, lbl_z,
            lbl_A, lbl_ip, lbl_jp, lbl_kp, lbl_xp, lbl_yp, lbl_zp,
            lbl_rA, lbl_B,
            lbl_om, lbl_vA,
            lbl_P, lbl_rP, lbl_rPA,
        ]
        for child in fixed_labels:            # fixed_axes axis labels
            self.add_fixed_orientation_mobjects(child)
        for lbl in all_labels:
            self.add_fixed_orientation_mobjects(lbl)

        # ── screen-pinned title ───────────────────────────────────────────────
        title = Text("Figure 16.13 – Two Reference Frames", font_size=26,
                     color=WHITE).to_corner(UL)
        subtitle = Text(
            "Fixed O-xyz  |  Moving A-x'y'z' in ℬ  |  Point P inside ℬ",
            font_size=17, color=GREY_B).next_to(title, DOWN, buff=0.08)
        self.add_fixed_in_frame_mobjects(title, subtitle)

        # ═════════════════════════════════════════════════════════════════════
        # ANIMATIONS
        # ═════════════════════════════════════════════════════════════════════

        # Skip Write animation for fixed-in-frame objects (OpenGL compatibility)
        # self.play(Write(title), Write(subtitle), run_time=0.8)

        # 1. Fixed frame
        self.play(Create(fixed_axes), run_time=1.2)
        self.play(
            Write(lbl_O),
            Write(lbl_x), Write(lbl_y), Write(lbl_z),
            *[Write(c) for c in fixed_labels],
            run_time=0.7,
        )

        # 2. r_A
        self.play(Create(r_A_arr), Write(lbl_rA), run_time=0.8)

        # 3. Ellipsoid body
        self.play(Create(ellipsoid), Write(lbl_B), run_time=1.0)

        # 4. Moving frame (ThreeDAxes, rotated + shifted)
        self.play(Create(moving_axes), Write(lbl_A), run_time=1.2)
        self.play(
            Write(lbl_ip), Write(lbl_jp), Write(lbl_kp),
            Write(lbl_xp), Write(lbl_yp), Write(lbl_zp),
            run_time=0.6,
        )

        # 5. ω and v_A
        self.play(Create(om_arr), Write(lbl_om), run_time=0.6)
        self.play(Create(va_arr), Write(lbl_vA), run_time=0.6)

        self.wait(0.3)

        # 6. Introduce P + its position vectors
        self.play(FadeIn(dot_P, scale=1.5), Write(lbl_P), run_time=0.6)
        self.play(
            Create(r_P_mob),  Write(lbl_rP),
            Create(r_PA_mob), Write(lbl_rPA),
            run_time=0.9,
        )

        self.wait(0.4)

        # 7. Trace Bezier and animate P moving along it
        # self.play(Create(path_curve), run_time=0.7)  # Skipped for OpenGL compatibility

        driver = Dot(radius=0)  # Invisible driver for UpdateFromAlphaFunc

        def update_scene(mob, alpha):
            P_now = bezier_pt(alpha)
            dot_P.move_to(P_now)
            lbl_P.move_to(P_now + np.array([0.22, 0.22, 0.10]))
            r_P_mob.put_start_and_end_on(O, P_now)
            _midlbl(lbl_rP,  O, P_now, [-0.42, 0.15, 0.22])
            r_PA_mob.put_start_and_end_on(A, P_now)
            _midlbl(lbl_rPA, A, P_now, [ 0.32, 0.15, 0.12])

        self.play(
            UpdateFromAlphaFunc(driver, update_scene),
            run_time=3.5, rate_func=there_and_back_with_pause,
        )

        self.wait(0.4)

        # 8. Slow camera orbit
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(5)
        self.stop_ambient_camera_rotation()
        self.wait(0.5)