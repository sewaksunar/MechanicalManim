"""
6-Link Constrained Mechanism Animation (DOF = 1)
=================================================
Topology
--------
  Ground ──O2─── link2 (crank, L2=3) ───A
                                         │
                                       link3 (coupler, L3 derived)
                                         │
  Ground ──O4─── link4 (rocker, L4=4) ──B
                       └──C (at L4c=3 from O4, on same rigid rod)
                   B ── link5 (rigid arm, L5=2) ── D
                                                    │
                                                  link6 (rigid arm, L6=1.5)
                                                    │
                                                    E ← horizontal slider rail

DOF check (Grübler, planar):
  Links n = 6  (ground, link2, link3, link4, link5+6 rigid coupler, slider)
  Joints j = 7  (O2 rev, A rev, C rev, O4 rev, B rev, E rev, rail prismatic)
  M = 3(6-1) − 2×7 = 15 − 14 = 1  ✓

Constraint strategy
-------------------
  • link5 and link6 form ONE rigid body (B–D–E) that rotates about B.
    D is a labelled kink; no separate pin at D.
  • Given crank angle θ2:
      1. Solve four-bar  O2–A–C–O4  → θ4
      2. B = O4 + L4·[cos θ4, sin θ4]
      3. Solve E_y constraint  →  θ_c  (angle of rigid coupler)
      4. D = B + R(θ_c)·D_loc,  E = B + R(θ_c)·E_loc

Run with:
    manim -pql mechanism_animation.py q1      # low quality (fast preview)
    manim -pqh mechanism_animation.py q1      # high quality
"""

from manim import *
import numpy as np


class q1(Scene):
    def construct(self):
        # ─────────────────────────────────────────────────────────────
        # MECHANISM PARAMETERS
        # ─────────────────────────────────────────────────────────────
        O2 = np.array([-4.0, -1.0, 0.0])   # fixed crank pivot
        O4 = np.array([ 3.0,  2.0, 0.0])   # fixed rocker pivot

        L2  = 3.0    # crank  O2 → A
        L4  = 4.0    # rocker O4 → B  (full length)
        L4c = 3.0    # O4 → C  (C lies on rocker between O4 and B)
        L5  = 2.0    # rigid-coupler arm  B → D
        L6  = 1.5    # rigid-coupler arm  D → E  (E on horizontal rail)

        T2_0 = np.pi / 3        # initial crank angle   60°
        T4_0 = 5.0 * np.pi / 4  # initial rocker angle 225°
        TC_0 = 0.0               # initial coupler-arm angle  0°

        # ─────────────────────────────────────────────────────────────
        # DERIVED CONSTANTS
        # ─────────────────────────────────────────────────────────────
        _A0 = O2[:2] + L2  * np.array([np.cos(T2_0), np.sin(T2_0)])
        _C0 = O4[:2] + L4c * np.array([np.cos(T4_0), np.sin(T4_0)])
        L3  = float(np.linalg.norm(_A0 - _C0))   # coupler A–C length

        # Rigid coupler local vectors (B is origin, θ_c = 0)
        D_loc = np.array([L5, 0.0])
        E_loc = D_loc + L6 * np.array([-np.cos(2*np.pi/3),
                                        -np.sin(2*np.pi/3)])
        E_arm = float(np.linalg.norm(E_loc))
        E_phi = float(np.arctan2(E_loc[1], E_loc[0]))

        # Horizontal slider rail y-coordinate (constant)
        _B0 = O4[:2] + L4 * np.array([np.cos(T4_0), np.sin(T4_0)])
        EY  = float(_B0[1] + E_loc[1])          # ≈ −2.13

        # ─────────────────────────────────────────────────────────────
        # KINEMATIC SOLVERS  (continuous-branch tracking)
        # ─────────────────────────────────────────────────────────────
        def branch(cand, ref):
            """Wrap candidate angle to the branch closest to ref."""
            return ref + ((cand - ref + np.pi) % (2*np.pi) - np.pi)

        def solve_4bar(t2, t4_p):
            """Return θ4 (O4→C angle) for crank angle t2."""
            A   = O2[:2] + L2 * np.array([np.cos(t2), np.sin(t2)])
            P   = A - O4[:2]
            R   = np.linalg.norm(P)
            if R < 1e-9:
                return t4_p
            v   = np.clip((R*R + L4c*L4c - L3*L3) / (2*L4c*R), -1.0, 1.0)
            phi = np.arctan2(P[1], P[0])
            d   = np.arccos(v)
            s1  = branch(phi + d, t4_p)
            s2  = branch(phi - d, t4_p)
            return s1 if abs(s1 - t4_p) < abs(s2 - t4_p) else s2

        def solve_coupler(B2, tc_p):
            """Return θ_c (rigid-coupler angle) satisfying E_y = EY."""
            sv   = np.clip((EY - B2[1]) / E_arm, -1.0, 1.0)
            base = np.arcsin(sv) - E_phi
            alt  = np.pi - np.arcsin(sv) - E_phi
            b1   = branch(base, tc_p)
            b2   = branch(alt,  tc_p)
            return b1 if abs(b1 - tc_p) < abs(b2 - tc_p) else b2

        def all_pos(t2, t4p, tcp):
            """Return (A,B,C,D,E) 3-vectors plus updated θ4, θ_c."""
            t4  = solve_4bar(t2, t4p)
            A2  = O2[:2] + L2  * np.array([np.cos(t2), np.sin(t2)])
            C2  = O4[:2] + L4c * np.array([np.cos(t4), np.sin(t4)])
            B2  = O4[:2] + L4  * np.array([np.cos(t4), np.sin(t4)])
            tc  = solve_coupler(B2, tcp)
            cs, ss = np.cos(tc), np.sin(tc)
            Rm  = np.array([[cs, -ss], [ss, cs]])
            D2  = B2 + Rm @ D_loc
            E2  = B2 + Rm @ E_loc
            def v3(v): return np.array([v[0], v[1], 0.0])
            return v3(A2), v3(B2), v3(C2), v3(D2), v3(E2), t4, tc

        def is_valid(t2, t4p, tcp):
            """True when both sub-problem inverses have real solutions."""
            A  = O2[:2] + L2 * np.array([np.cos(t2), np.sin(t2)])
            P  = A - O4[:2]
            R  = np.linalg.norm(P)
            if R < 1e-9:
                return False
            v1 = (R*R + L4c*L4c - L3*L3) / (2*L4c*R)
            if abs(v1) > 1.0:
                return False
            t4 = solve_4bar(t2, t4p)
            B2 = O4[:2] + L4 * np.array([np.cos(t4), np.sin(t4)])
            return abs((EY - B2[1]) / E_arm) <= 1.0

        # ─────────────────────────────────────────────────────────────
        # FIND VALID CRANK RANGE  (mechanism locks at singularities)
        # ─────────────────────────────────────────────────────────────
        DT = 0.004
        t4c, tcc = T4_0, TC_0

        fwd = [T2_0]
        t2  = T2_0 + DT
        while t2 < T2_0 + 2*np.pi:
            if not is_valid(t2, t4c, tcc):
                break
            _, _, _, _, _, t4c, tcc = all_pos(t2, t4c, tcc)
            fwd.append(t2)
            t2 += DT

        t4c, tcc = T4_0, TC_0
        bwd = []
        t2  = T2_0 - DT
        while t2 > T2_0 - 2*np.pi:
            if not is_valid(t2, t4c, tcc):
                break
            _, _, _, _, _, t4c, tcc = all_pos(t2, t4c, tcc)
            bwd.append(t2)
            t2 -= DT

        T2_MAX = fwd[-1] if len(fwd) > 1 else T2_0 + 0.1
        T2_MIN = bwd[-1] if bwd          else T2_0 - 0.1

        # ─────────────────────────────────────────────────────────────
        # PRECOMPUTE ANIMATION FRAMES
        # One cycle:  init ──► max ──► min ──► init
        # ─────────────────────────────────────────────────────────────
        N = 400   # samples per half-segment
        path_t2 = np.concatenate([
            np.linspace(T2_0,   T2_MAX, N),
            np.linspace(T2_MAX, T2_MIN, 2*N),
            np.linspace(T2_MIN, T2_0,   N),
        ])

        frames = []
        t4c, tcc = T4_0, TC_0
        for t2 in path_t2:
            A, B, C, D, E, t4c, tcc = all_pos(t2, t4c, tcc)
            frames.append((A.copy(), B.copy(), C.copy(), D.copy(), E.copy()))

        NF = len(frames)
        A0, B0, C0, D0, E0 = frames[0]

        # ─────────────────────────────────────────────────────────────
        # BUILD SCENE OBJECTS
        # ─────────────────────────────────────────────────────────────

        # — Ground hatch symbol —
        def hatch_sym(pt, w=0.6, n=5):
            g = VGroup()
            g.add(Line(pt + np.array([-w/2, -0.06, 0]),
                       pt + np.array([ w/2, -0.06, 0]),
                       color=GRAY_B, stroke_width=3))
            for k in range(n + 1):
                x = -w/2 + k * w / n
                g.add(Line(pt + np.array([x,    -0.06, 0]),
                           pt + np.array([x-.15, -.30, 0]),
                           color=GRAY_B, stroke_width=1.5))
            return g

        # — Horizontal slider rail —
        RX0, RX1 = -7.5, 5.2
        rail_line = Line([RX0, EY, 0], [RX1, EY, 0],
                         color=GRAY_B, stroke_width=3)
        rail_hash = VGroup(*[
            Line([x, EY, 0], [x - 0.20, EY - 0.20, 0],
                 color=GRAY_B, stroke_width=1.2)
            for x in np.arange(RX0 + 0.15, RX1, 0.45)
        ])
        rail_grp = VGroup(rail_line, rail_hash)

        ground_O2 = hatch_sym(O2)
        ground_O4 = hatch_sym(O4)
        pin_O2    = Dot(O2, radius=0.10, color=RED)
        pin_O4    = Dot(O4, radius=0.10, color=RED)

        # — Labels —
        def mk_lbl(txt, pt, d=UP):
            return Text(txt, font_size=22).next_to(pt, d, buff=0.18)

        lO2 = mk_lbl("O₂", O2, DOWN + LEFT)
        lO4 = mk_lbl("O₄", O4, UP + RIGHT)

        # — Moving joint dots —
        dot_A = Dot(A0, radius=0.09, color=YELLOW)
        dot_B = Dot(B0, radius=0.09, color=ORANGE)
        dot_C = Dot(C0, radius=0.09, color=GREEN)
        dot_D = Dot(D0, radius=0.09, color=BLUE)
        dot_E = Dot(E0, radius=0.09, color=PURPLE)

        lA = mk_lbl("A", A0, UP + RIGHT)
        lB = mk_lbl("B", B0, DOWN + LEFT)
        lC = mk_lbl("C", C0, UP + LEFT)
        lD = mk_lbl("D", D0, DOWN + RIGHT)
        lE = mk_lbl("E", E0, UP)

        # — Links —
        link2 = Line(O2,  A0, color=YELLOW, stroke_width=5)
        link4 = Line(O4,  B0, color=GRAY,   stroke_width=6)   # rocker
        link3 = Line(A0,  C0, color=GREEN,  stroke_width=4)   # coupler
        link5 = Line(B0,  D0, color=BLUE,   stroke_width=4)   # rigid arm 1
        link6 = Line(D0,  E0, color=PURPLE, stroke_width=4)   # rigid arm 2

        # — Slider block —
        slider = Rectangle(width=1.0, height=0.45,
                           color=ORANGE,
                           fill_color=ORANGE, fill_opacity=0.65)
        slider.move_to(E0)

        # — Title (top-left) —
        title = Text("6-Link Mechanism  |  DOF = 1",
                     font_size=24, color=GRAY_A).to_corner(UL, buff=0.25)

        # ─────────────────────────────────────────────────────────────
        # STATIC BUILD-UP (mirrors original code structure)
        # ─────────────────────────────────────────────────────────────
        self.add(title, rail_grp, ground_O2, ground_O4,
                 pin_O2, pin_O4, lO2, lO4)
        self.wait(0.3)

        self.play(Create(link2), run_time=0.5)
        self.add(dot_A, lA)

        self.play(Create(link4), run_time=0.5)
        self.add(dot_B, lB, dot_C, lC)

        self.play(Create(link3), run_time=0.5)
        self.play(Create(link5), run_time=0.5)
        self.add(dot_D, lD)

        self.play(Create(link6), run_time=0.5)
        self.add(dot_E, lE)
        self.play(FadeIn(slider), run_time=0.4)
        self.wait(0.6)

        # ─────────────────────────────────────────────────────────────
        # UPDATERS  (driven by a single ValueTracker → param ∈ [0,1])
        # ─────────────────────────────────────────────────────────────
        param = ValueTracker(0.0)

        def fi():
            """Current frame index."""
            return int(np.clip(
                round(param.get_value() * (NF - 1)), 0, NF - 1))

        def line_upd(j, i=None, fs=None):
            """
            Updater factory for a line.
              j  : index of end-point in frames tuple   (A=0,B=1,C=2,D=3,E=4)
              i  : index of start-point (None if fixed start is used)
              fs : fixed 3-vector start (for links pinned to ground)
            """
            def u(mob):
                f   = frames[fi()]
                s   = fs if fs is not None else f[i]
                e   = f[j]
                if np.linalg.norm(e - s) > 1e-6:
                    mob.put_start_and_end_on(s, e)
            return u

        def dot_upd(i):
            def u(mob): mob.move_to(frames[fi()][i])
            return u

        def lbl_upd(i, d):
            def u(mob): mob.next_to(frames[fi()][i], d, buff=0.18)
            return u

        # Lines
        link2.add_updater(line_upd(0,        fs=O2))   # O2 → A
        link4.add_updater(line_upd(1,        fs=O4))   # O4 → B
        link3.add_updater(line_upd(2, i=0))            # A  → C
        link5.add_updater(line_upd(3, i=1))            # B  → D
        link6.add_updater(line_upd(4, i=3))            # D  → E

        # Slider
        slider.add_updater(lambda mob: mob.move_to(frames[fi()][4]))

        # Dots
        for dot_mob, idx in [
            (dot_A, 0), (dot_B, 1), (dot_C, 2), (dot_D, 3), (dot_E, 4)
        ]:
            dot_mob.add_updater(dot_upd(idx))

        # Labels
        for lab_mob, idx, d in [
            (lA, 0, UP + RIGHT), (lB, 1, DOWN + LEFT),
            (lC, 2, UP + LEFT),  (lD, 3, DOWN + RIGHT),
            (lE, 4, UP),
        ]:
            lab_mob.add_updater(lbl_upd(idx, d))

        # — Coupler curve trace (shows the path swept by joint C) —
        coupler_trace = TracedPath(
            lambda: frames[fi()][2],
            stroke_color=GREEN_B,
            stroke_width=1.8,
            stroke_opacity=0.75,
            dissipating_time=2.0,
        )
        self.add(coupler_trace)

        # ─────────────────────────────────────────────────────────────
        # ANIMATE  —  2 complete oscillation cycles
        # ─────────────────────────────────────────────────────────────
        CYCLE_TIME = 7.0  # seconds per half-cycle (forward or backward)

        for _ in range(2):
            self.play(param.animate.set_value(1.0),
                      run_time=CYCLE_TIME, rate_func=linear)
            self.play(param.animate.set_value(0.0),
                      run_time=CYCLE_TIME, rate_func=linear)

        self.wait(1.0)