"""
Figure 16.13 – Two Rectangular Reference Frames (Manim) — STATIC
Run:
    manim -pql --save_last_frame figure_16_13.py Figure1613
    manim -pqh --save_last_frame figure_16_13.py Figure1613
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
    return Arrow3D(np.array(start, dtype=float), np.array(end, dtype=float),
                   color=color, resolution=res,
                   thickness=thick, base_radius=brad, height=ht)

def _thin(start, end, color):
    return Arrow(np.array(start, dtype=float), np.array(end, dtype=float),
                 color=color, buff=0, stroke_width=3,
                 max_tip_length_to_length_ratio=0.12)


class Intro(ThreeDScene):

    # ── tunables ──────────────────────────────────────────────────────────────
    SCENE_SHIFT = np.array([0.0, 0.0, -0.5])  # shift whole scene
    _A_LOCAL    = np.array([1.5, 1.0, 1.2])   # A relative to O
    BODY_AXES   = 1.7
    TILT_X, TILT_Y, TILT_Z = 0.4, -0.3, 0.5

    # Fixed frame axis length (all three equal → balanced look)
    FIXED_LEN = 2.8

    BEZIER_LOCAL = np.array([
        [ 0.30,  0.10,  0.10],
        [ 0.75,  0.45,  0.30],
        [ 0.35, -0.25,  0.45],
        [-0.15,  0.40, -0.20],
        [ 0.50,  0.20,  0.05],
    ])

    def construct(self):

        self.set_camera_orientation(phi=75 * DEGREES, theta=-30 * DEGREES, zoom=0.75)
        self.camera.set_focal_distance(20)

        S = self.SCENE_SHIFT
        O = ORIGIN + S
        A = self._A_LOCAL + S

        R = (
            rotation_matrix(self.TILT_Z, OUT)
            @ rotation_matrix(self.TILT_Y, UP)
            @ rotation_matrix(self.TILT_X, RIGHT)
        )
        i_p, j_p, k_p = R @ RIGHT, R @ UP, R @ OUT

        bz = np.array([R @ p + A for p in self.BEZIER_LOCAL])
        def bezier_pt(t):
            pts = bz.copy().astype(float)
            for _ in range(len(pts) - 1):
                pts = (1 - t) * pts[:-1] + t * pts[1:]
            return pts[0]

        P = bezier_pt(0.42)

        # ── Bezier path trace ─────────────────────────────────────────────────
        trace_pts = [bezier_pt(t) for t in np.linspace(0, 1.15, 250)]
        path_curve = VMobject(stroke_color=P_COLOR, stroke_width=4.8,
                              stroke_opacity=0.85)
        path_curve.set_points_smoothly([np.array(p) for p in trace_pts])

        # ═════════════════════════════════════════════════════════════════════
        # 1. FIXED FRAME  — balanced equal-length axes
        # ═════════════════════════════════════════════════════════════════════
        FL = self.FIXED_LEN
        fixed_axes = ThreeDAxes(
            x_range=[-FL/2, FL/2, FL/2],   # symmetric around origin
            y_range=[-FL/2, FL/2, FL/2],
            z_range=[-FL/2, FL/2, FL/2],
            x_length=FL,
            y_length=FL,
            z_length=FL,
            axis_config={
                "color"       : FIXED_COLOR,
                "stroke_width": 2.5,
                "include_tip" : True,
                "tip_length"  : 0.22,
                "include_ticks": False,
                "tick_size"   : 0.06,
            },
        )
        fixed_axes.shift(O)

        # Tip world positions
        x_tip = fixed_axes.x_axis.get_end()
        y_tip = fixed_axes.y_axis.get_end()
        z_tip = fixed_axes.z_axis.get_end()

        # Base-vector labels  i, j, k  — clean positioning
        lbl_i  = MathTex(r"\mathbf{i}", color=FIXED_COLOR).scale(0.65).move_to(x_tip + [ 0.40,  0.25,  0.00])
        lbl_j  = MathTex(r"\mathbf{j}", color=FIXED_COLOR).scale(0.65).move_to(y_tip + [ 0.15,  0.40,  0.00])
        lbl_k  = MathTex(r"\mathbf{k}", color=FIXED_COLOR).scale(0.65).move_to(z_tip + [-0.10,  0.00,  0.40])
        # Coordinate labels  x, y, z
        lbl_x  = MathTex("x",           color=FIXED_COLOR).scale(0.50).move_to(x_tip + [ 0.50,  0.35,  0.00])
        lbl_y  = MathTex("y",           color=FIXED_COLOR).scale(0.50).move_to(y_tip + [ 0.22,  0.50,  0.00])
        lbl_z  = MathTex("z",           color=FIXED_COLOR).scale(0.50).move_to(z_tip + [-0.08,  0.10,  0.50])
        lbl_O  = MathTex("O",           color=FIXED_COLOR).scale(0.60).move_to(O     + [-0.35, -0.35,  0.00])

        # ═════════════════════════════════════════════════════════════════════
        # 2. MOVING FRAME  — ThreeDAxes rotated then shifted to A
        # ═════════════════════════════════════════════════════════════════════
        BL   = self.BODY_AXES
        step = round(BL / 2, 2)
        moving_axes = ThreeDAxes(
            x_range=[-BL/2, BL/2, step],  # symmetric around origin
            y_range=[-BL/2, BL/2, step],
            z_range=[-BL/2, BL/2, step],
            x_length=BL, y_length=BL, z_length=BL,
            axis_config={
                "color"        : MOVING_COLOR,
                "stroke_width" : 2.5,
                "include_tip"  : True,
                "tip_length"   : 0.22,
                "include_ticks": False,
            },
        )
        moving_axes.apply_matrix(R)
        moving_axes.shift(A)

        ip_tip = A + BL * i_p
        jp_tip = A + BL * j_p
        kp_tip = A + BL * k_p

        lbl_A  = MathTex("A",             color=MOVING_COLOR).scale(0.60).move_to(A      + [-0.30, -0.30,  0.00])
        lbl_ip = MathTex(r"\mathbf{i}'",  color=MOVING_COLOR).scale(0.65).move_to(ip_tip + 0.45 * i_p)
        lbl_jp = MathTex(r"\mathbf{j}'",  color=MOVING_COLOR).scale(0.65).move_to(jp_tip + 0.45 * j_p)
        lbl_kp = MathTex(r"\mathbf{k}'",  color=MOVING_COLOR).scale(0.65).move_to(kp_tip + 0.45 * k_p)
        lbl_xp = MathTex("x'",            color=MOVING_COLOR).scale(0.48).move_to(ip_tip + 0.75 * i_p)
        lbl_yp = MathTex("y'",            color=MOVING_COLOR).scale(0.48).move_to(jp_tip + 0.75 * j_p)
        lbl_zp = MathTex("z'",            color=MOVING_COLOR).scale(0.48).move_to(kp_tip + 0.75 * k_p)

        # ═════════════════════════════════════════════════════════════════════
        # 3. r_A  O→A
        # ═════════════════════════════════════════════════════════════════════
        r_A_arr = _arr3d(O, A, RA_COLOR)
        lbl_rA  = MathTex(r"\mathbf{r}_A", color=RA_COLOR).scale(0.58)
        lbl_rA.move_to((O + A) / 2 + [-0.45, 0.10, 0.10])

        # ═════════════════════════════════════════════════════════════════════
        # 4. Ellipsoid body B
        # ═════════════════════════════════════════════════════════════════════
        a_e, b_e, c_e = 1.5, 1.0, 0.7
        ellipsoid = Surface(
            lambda u, v: A + R @ np.array([
                a_e * np.sin(v) * np.cos(u),
                b_e * np.sin(v) * np.sin(u),
                c_e * np.cos(v),
            ]),
            u_range=[0, TAU], v_range=[0, PI],
            resolution=(50, 35),
            fill_color=BODY_COLOR, fill_opacity=0.25,
            stroke_color=BLACK, stroke_width=0.0, stroke_opacity=0.0,
        )
        lbl_B = MathTex(r"\mathcal{B}", color=BODY_COLOR).scale(0.80)
        lbl_B.move_to(A + R @ np.array([a_e * 0.55, b_e * 0.85, c_e * 0.55]) + [0.40, 0.40, 0.00])

        # ═════════════════════════════════════════════════════════════════════
        # 5. ω and v_A
        # ═════════════════════════════════════════════════════════════════════
        om_dir = _norm(np.array([-0.4, 0.6, 1.0]))
        om_end = A + 1.6 * om_dir
        om_arr = _arr3d(A, om_end, OMEGA_COLOR)
        lbl_om = MathTex(r"\boldsymbol{\omega}", color=OMEGA_COLOR).scale(0.62)
        lbl_om.move_to(om_end + [-0.40, 0.35, 0.10])

        va_dir = _norm(np.array([0.7, -0.3, -0.6]))
        va_end = A + 1.4 * va_dir
        va_arr = _arr3d(A, va_end, VA_COLOR)
        lbl_vA = MathTex(r"\mathbf{v}_A", color=VA_COLOR).scale(0.60)
        lbl_vA.move_to(va_end + [0.35, -0.35, 0.10])

        # ═════════════════════════════════════════════════════════════════════
        # 6. Point P + r_P + r_P/A
        # ═════════════════════════════════════════════════════════════════════
        dot_P   = Sphere(radius=0.09, resolution=(6, 6)).set_color(P_COLOR).move_to(P)
        lbl_P   = MathTex("P", color=P_COLOR).scale(0.60).move_to(P + [0.30, 0.30, 0.00])
        r_P_mob  = _thin(O, P, RP_COLOR)
        r_PA_mob = _thin(A, P, RPA_COLOR)

        lbl_rP  = MathTex(r"\mathbf{r}_P",      color=RP_COLOR ).scale(0.56)
        lbl_rPA = MathTex(r"\mathbf{r}_{P/A}",  color=RPA_COLOR).scale(0.56)
        lbl_rP .move_to(0.5 * (O + P) + np.array([-0.50, 0.15, 0.10]))
        lbl_rPA.move_to(0.5 * (A + P) + np.array([ 0.40, 0.15, 0.10]))

        # ═════════════════════════════════════════════════════════════════════
        # All labels face the camera
        # ═════════════════════════════════════════════════════════════════════
        face_cam = [
            lbl_O, lbl_i, lbl_j, lbl_k, lbl_x, lbl_y, lbl_z,
            lbl_A, lbl_ip, lbl_jp, lbl_kp, lbl_xp, lbl_yp, lbl_zp,
            lbl_rA, lbl_B,
            lbl_om, lbl_vA,
            lbl_P, lbl_rP, lbl_rPA,
        ]
        for lbl in face_cam:
            self.add_fixed_orientation_mobjects(lbl)

        title = Text("Figure 16.13 – Two Reference Frames", font_size=26,
                     color=WHITE).to_corner(UL)
        subtitle = Text(
            "Fixed O-xyz  |  Moving A-x'y'z' in ℬ  |  Point P",
            font_size=17, color=GREY_B).next_to(title, DOWN, buff=0.08)
        self.add_fixed_in_frame_mobjects(title, subtitle)

        # ═════════════════════════════════════════════════════════════════════
        # ADD EVERYTHING — fully static
        # ═════════════════════════════════════════════════════════════════════
        self.add(
            fixed_axes,
            lbl_O, lbl_i, lbl_j, lbl_k, lbl_x, lbl_y, lbl_z,
            r_A_arr, lbl_rA,
            ellipsoid, lbl_B,
            moving_axes,
            lbl_A, lbl_ip, lbl_jp, lbl_kp,
            lbl_xp, lbl_yp, lbl_zp,
            om_arr, lbl_om,
            va_arr, lbl_vA,
            path_curve, dot_P, lbl_P,
            r_P_mob, lbl_rP,
            r_PA_mob, lbl_rPA,
            title, subtitle,
        )

