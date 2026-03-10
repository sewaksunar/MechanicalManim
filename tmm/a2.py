"""
6-Link Mechanism  –  DOF = 2
==============================
Grübler count:
  Links  n = 7   (ground, crank/link2, coupler/link3, rocker/link4,
                   link5, link6, slider)
  Joints j = 8   (O2 rev, A rev, C rev, O4 rev, B rev, D rev, E rev,
                   rail prismatic)
  M = 3(n−1) − 2j = 3(6) − 2(8) = 18 − 16 = 2  ✓

Two independent inputs
  θ₂  – crank angle          (motor at O2)
  x_E – slider x-position    (actuator, rail is horizontal)

Kinematic solution each frame
  1. A  = O2 + L2·[cosθ₂, sinθ₂]
  2. E  = [x_E, y_rail]
  3. Four-bar O2–A–C–O4  →  θ₄  →  B, C
  4. Two-link IK  B–D–E   →  θ₅  →  D

Visual fixes vs previous version
  • Camera zoomed in (MovingCameraScene, frame_width ≈ 11 u)
  • Rail width matches actual slider travel + margin  (not full-frame)
  • All VGroup component classes preserved for easy reuse

Run:
    manim -pql mechanism_animation.py q1
    manim -pqh mechanism_animation.py q1
"""

from manim import *
import numpy as np


# ══════════════════════════════════════════════════════════════════════════════
#  Pure math helpers
# ══════════════════════════════════════════════════════════════════════════════

def wrap_branch(cand: float, ref: float) -> float:
    return ref + ((cand - ref + np.pi) % (2.0 * np.pi) - np.pi)


def v3(xy) -> np.ndarray:
    return np.array([float(xy[0]), float(xy[1]), 0.0])


# ══════════════════════════════════════════════════════════════════════════════
#  Reusable VGroup components
# ══════════════════════════════════════════════════════════════════════════════

class GroundSupport(VGroup):
    """
    Hatched fixed-pivot symbol.

    Usage
    -----
        g = GroundSupport(pivot_3d)
        scene.add(g)
    """
    def __init__(self, pivot: np.ndarray,
                 width: float = 0.65, n_hash: int = 6,
                 color=LIGHT_GRAY, **kwargs):
        super().__init__(**kwargs)
        # horizontal bar
        self.add(Line(
            pivot + np.array([-width / 2, -0.05, 0]),
            pivot + np.array([ width / 2, -0.05, 0]),
            color=color, stroke_width=2.5))
        # diagonal hatch lines
        for k in range(n_hash + 1):
            x = -width / 2 + k * width / n_hash
            self.add(Line(
                pivot + np.array([x,        -0.05, 0]),
                pivot + np.array([x - 0.12,  -0.23, 0]),
                color=color, stroke_width=1.3))


class SliderRail(VGroup):
    """
    Horizontal slider rail — solid line + hatch marks below.
    Width is derived from the actual slider travel + margin.

    Usage
    -----
        rail = SliderRail(x_start, x_end, y)
        scene.add(rail)
    """
    def __init__(self, x_start: float, x_end: float, y: float,
                 spacing: float = 0.38, color=LIGHT_GRAY, **kwargs):
        super().__init__(**kwargs)
        self.add(Line([x_start, y, 0], [x_end, y, 0],
                      color=color, stroke_width=2.5))
        for x in np.arange(x_start + 0.12, x_end, spacing):
            self.add(Line(
                [x,        y,        0],
                [x - 0.15, y - 0.15, 0],
                color=color, stroke_width=1.1))


class PinJoint(VGroup):
    """
    Revolute-joint marker: filled circle with stroke.

    Updater pattern
    ---------------
        pin.add_updater(lambda m: m.move_joint_to(new_pos))
    """
    def __init__(self, position: np.ndarray,
                 radius: float = 0.10,
                 stroke_color=WHITE, fill_color=BLACK, **kwargs):
        super().__init__(**kwargs)
        self._c = Circle(radius=radius, color=stroke_color,
                         fill_color=fill_color, fill_opacity=1,
                         stroke_width=2).move_to(position)
        self.add(self._c)

    def move_joint_to(self, pos: np.ndarray):
        self._c.move_to(pos)
        return self


class JointLabel(VGroup):
    """
    Text label that follows a joint position.

    Updater pattern
    ---------------
        lbl.add_updater(lambda m: m.follow_joint(new_pos))
    """
    def __init__(self, text: str, position: np.ndarray,
                 direction=UP, font_size: int = 20,
                 color=WHITE, buff: float = 0.18, **kwargs):
        super().__init__(**kwargs)
        self._dir  = direction
        self._buff = buff
        self._t = Text(text, font_size=font_size, color=color)
        self._t.next_to(position, direction, buff=buff)
        self.add(self._t)

    def follow_joint(self, pos: np.ndarray):
        self._t.next_to(pos, self._dir, buff=self._buff)
        return self


class MechanismLink(VGroup):
    """
    A rigid bar between two joint positions.

    Updater pattern
    ---------------
        lnk.add_updater(lambda m: m.set_endpoints(start, end))

    Note
    ----
        Use `.line` to target `Create()` animations.
    """
    def __init__(self, start: np.ndarray, end: np.ndarray,
                 color=WHITE, stroke_width: float = 4, **kwargs):
        super().__init__(**kwargs)
        self._line = Line(start, end, color=color,
                          stroke_width=stroke_width)
        self.add(self._line)

    @property
    def line(self):
        return self._line

    def set_endpoints(self, start: np.ndarray, end: np.ndarray):
        if np.linalg.norm(end - start) > 1e-6:
            self._line.put_start_and_end_on(start, end)
        return self


class SliderBlock(VGroup):
    """
    Rectangular block riding on a horizontal rail.

    Updater pattern
    ---------------
        blk.add_updater(lambda m: m.move_slider_to(E_pos))
    """
    def __init__(self, position: np.ndarray,
                 width: float = 0.95, height: float = 0.38,
                 corner_radius: float = 0.07,
                 stroke_color=BLUE_B, fill_color=BLUE_D, **kwargs):
        super().__init__(**kwargs)
        self._r = RoundedRectangle(
            width=width, height=height,
            corner_radius=corner_radius,
            color=stroke_color,
            fill_color=fill_color, fill_opacity=0.85,
            stroke_width=2.2).move_to(position)
        self.add(self._r)

    @property
    def rect(self):
        return self._r

    def move_slider_to(self, pos: np.ndarray):
        self._r.move_to(pos)
        return self


class ActuatorArrow(VGroup):
    """
    Small arrow indicating the x_E (slider) input.
    Tail is offset below-left of the slider pin.

    Updater pattern
    ---------------
        arr.add_updater(lambda m: m.follow_slider(E_pos))
    """
    _TAIL = np.array([-0.75, -0.60, 0.0])
    _TIP  = np.array([ 0.0,  -0.15, 0.0])

    def __init__(self, e_pos: np.ndarray, color=BLUE_B, **kwargs):
        super().__init__(**kwargs)
        self._a = Arrow(
            start=e_pos + self._TAIL,
            end=e_pos   + self._TIP,
            color=color, buff=0,
            max_tip_length_to_length_ratio=0.28,
            stroke_width=2.2)
        self.add(self._a)

    def follow_slider(self, e_pos: np.ndarray):
        self._a.put_start_and_end_on(
            e_pos + self._TAIL,
            e_pos + self._TIP)
        return self


class InfoHUD(VGroup):
    """
    Top-left legend: DOF count + two input descriptions.

    Usage
    -----
        hud = InfoHUD(dof=2,
                      input1="Input 1 : θ₂  (crank motor)",
                      input2="Input 2 : x_E  (slider actuator)")
    """
    def __init__(self, dof: int = 2,
                 input1: str = "Input 1 : θ₂  (crank motor)",
                 input2: str = "Input 2 : x_E  (slider actuator)",
                 **kwargs):
        super().__init__(**kwargs)
        t0 = Text(f"DOF = {dof}", font_size=22, color=YELLOW
                  ).to_corner(UL, buff=0.25)
        t1 = Text(input1, font_size=17, color=YELLOW_B
                  ).next_to(t0, DOWN, aligned_edge=LEFT, buff=0.08)
        t2 = Text(input2, font_size=17, color=BLUE_B
                  ).next_to(t1, DOWN, aligned_edge=LEFT, buff=0.05)
        self.add(t0, t1, t2)


# ══════════════════════════════════════════════════════════════════════════════
#  Kinematic solver
# ══════════════════════════════════════════════════════════════════════════════

class MechanismSolver:
    """
    Closed-form position analysis for the 6-link DOF-2 mechanism.

    Parameters
    ----------
    O2, O4         : 2-D ground pivot positions
    L2             : crank length  (O2 → A)
    L4             : rocker full length  (O4 → B)
    L4c            : O4 → C  (C lies on rocker between O4 and B)
    L5, L6         : link5 (B→D) and link6 (D→E) lengths
    T2_0, T4_0     : initial crank / rocker angles (for branch initialisation)

    Public API
    ----------
    .y_rail, .x_E0  – rail y-coordinate and initial slider x-position
    .solve(t2, xE)  – returns (A,B,C,D,E) 3-vectors or None
    .precompute(t2_arr, xE_arr) – batch solve, returns list of frame tuples
    """

    def __init__(self,
                 O2: np.ndarray, O4: np.ndarray,
                 L2: float, L4: float, L4c: float,
                 L5: float, L6: float,
                 T2_0: float, T4_0: float):

        self.O2, self.O4 = O2, O4
        self.L2, self.L4, self.L4c = L2, L4, L4c
        self.L5, self.L6 = L5, L6

        # derive L3 and rail constants from initial pose
        A0  = O2 + L2  * np.array([np.cos(T2_0), np.sin(T2_0)])
        C0  = O4 + L4c * np.array([np.cos(T4_0), np.sin(T4_0)])
        B0  = O4 + L4  * np.array([np.cos(T4_0), np.sin(T4_0)])
        self.L3 = float(np.linalg.norm(A0 - C0))

        T5_0    = 0.0
        D0      = B0 + L5 * np.array([np.cos(T5_0), np.sin(T5_0)])
        l6_dir  = np.array([-np.cos(2 * np.pi / 3), -np.sin(2 * np.pi / 3)])
        E0      = D0 + L6 * l6_dir

        self.y_rail = float(E0[1])
        self.x_E0   = float(E0[0])

        # mutable branch state
        self._t4 = T4_0
        self._t5 = T5_0

    # ── private sub-solvers ────────────────────────────────────────────────

    def _four_bar(self, t2: float):
        A  = self.O2 + self.L2 * np.array([np.cos(t2), np.sin(t2)])
        P  = A - self.O4
        d  = np.linalg.norm(P)
        if d < 1e-9:
            return None
        cv = (d*d + self.L4c**2 - self.L3**2) / (2.0 * self.L4c * d)
        if abs(cv) > 1.0:
            return None
        phi   = np.arctan2(P[1], P[0])
        delta = np.arccos(np.clip(cv, -1.0, 1.0))
        s1 = wrap_branch(phi + delta, self._t4)
        s2 = wrap_branch(phi - delta, self._t4)
        return s1 if abs(s1 - self._t4) <= abs(s2 - self._t4) else s2

    def _two_link_ik(self, B2: np.ndarray, E2: np.ndarray):
        BE  = E2 - B2
        d   = np.linalg.norm(BE)
        lo  = abs(self.L5 - self.L6)
        hi  = self.L5 + self.L6
        if not (lo <= d <= hi):
            return None
        cv    = (d*d + self.L5**2 - self.L6**2) / (2.0 * d * self.L5)
        alpha = np.arccos(np.clip(cv, -1.0, 1.0))
        phi   = np.arctan2(BE[1], BE[0])
        s1 = wrap_branch(phi + alpha, self._t5)
        s2 = wrap_branch(phi - alpha, self._t5)
        return s1 if abs(s1 - self._t5) <= abs(s2 - self._t5) else s2

    # ── public API ─────────────────────────────────────────────────────────

    def solve(self, t2: float, xE: float):
        t4 = self._four_bar(t2)
        if t4 is None:
            return None

        A = v3(self.O2 + self.L2  * np.array([np.cos(t2), np.sin(t2)]))
        C = v3(self.O4 + self.L4c * np.array([np.cos(t4), np.sin(t4)]))
        B = v3(self.O4 + self.L4  * np.array([np.cos(t4), np.sin(t4)]))
        E = v3([xE, self.y_rail])

        t5 = self._two_link_ik(B[:2], E[:2])
        if t5 is None:
            return None

        D = v3(B[:2] + self.L5 * np.array([np.cos(t5), np.sin(t5)]))
        self._t4, self._t5 = t4, t5
        return A, B, C, D, E

    def precompute(self, t2_arr: np.ndarray,
                   xE_arr: np.ndarray) -> list:
        frames, last = [], None
        for t2, xE in zip(t2_arr, xE_arr):
            res = self.solve(t2, xE)
            if res is None:
                if last:
                    frames.append(last)
            else:
                last = tuple(p.copy() for p in res)
                frames.append(last)
        return frames


# ══════════════════════════════════════════════════════════════════════════════
#  Scene  (MovingCameraScene so we can set a tighter frame)
# ══════════════════════════════════════════════════════════════════════════════

class q1(MovingCameraScene):

    # ── mechanism geometry ────────────────────────────────────────────────────
    O2   = np.array([-4.0, -1.0])
    O4   = np.array([ 3.0,  2.0])
    L2   = 3.0
    L4   = 4.0
    L4c  = 3.0
    L5   = 2.0
    L6   = 1.5
    T2_0 = np.pi / 3
    T4_0 = 5.0 * np.pi / 4

    # ── animation settings ────────────────────────────────────────────────────
    N_FRAMES   = 720
    XE_FREQ    = 3      # slider oscillations per crank revolution
    XE_AMP     = 1.0    # ± slider amplitude (units)
    CYCLE_TIME = 10.0   # seconds per full param sweep
    N_CYCLES   = 2

    def construct(self):

        # ── zoom camera to fit mechanism tightly ──────────────────────────────
        # default frame is 14×8; we zoom to ~11×6.2 and centre on mechanism
        self.camera.frame.set(width=11.0)
        self.camera.frame.move_to([-0.3, 0.1, 0])

        # ── 1. kinematics ─────────────────────────────────────────────────────
        solver = MechanismSolver(
            O2=self.O2, O4=self.O4,
            L2=self.L2, L4=self.L4, L4c=self.L4c,
            L5=self.L5, L6=self.L6,
            T2_0=self.T2_0, T4_0=self.T4_0)

        t2_arr = self.T2_0 + np.linspace(0.0, 2.0 * np.pi, self.N_FRAMES)
        xE_arr = (solver.x_E0 + self.XE_AMP *
                  np.sin(self.XE_FREQ *
                         np.linspace(0.0, 2.0 * np.pi, self.N_FRAMES)))

        frames = solver.precompute(t2_arr, xE_arr)
        if len(frames) < 2:
            raise RuntimeError("No valid frames — check mechanism geometry.")

        NF = len(frames)
        A0, B0, C0, D0, E0 = frames[0]
        O2_pt = v3(self.O2)
        O4_pt = v3(self.O4)

        # ── 2. build scene objects using component classes ─────────────────────

        # static environment
        hud       = InfoHUD(dof=2)
        ground_O2 = GroundSupport(O2_pt)
        ground_O4 = GroundSupport(O4_pt)
        pin_O2    = PinJoint(O2_pt, stroke_color=RED)
        pin_O4    = PinJoint(O4_pt, stroke_color=RED)
        lbl_O2    = JointLabel("O₂", O2_pt, direction=DOWN + LEFT)
        lbl_O4    = JointLabel("O₄", O4_pt, direction=UP + RIGHT)

        # rail width = actual slider travel + 0.7 margin each side (no more full-frame rail)
        xE_min = float(xE_arr.min())
        xE_max = float(xE_arr.max())
        rail = SliderRail(x_start=xE_min - 0.7,
                          x_end=xE_max   + 0.7,
                          y=solver.y_rail)

        # moving links
        link2 = MechanismLink(O2_pt, A0, color=YELLOW,      stroke_width=4.5)
        link4 = MechanismLink(O4_pt, B0, color=LIGHT_GRAY,  stroke_width=5.5)
        link3 = MechanismLink(A0,    C0, color=GREEN,        stroke_width=3.5)
        link5 = MechanismLink(B0,    D0, color=BLUE,         stroke_width=3.5)
        link6 = MechanismLink(D0,    E0, color=PURPLE,       stroke_width=3.5)

        # pin joints
        pin_A = PinJoint(A0, stroke_color=YELLOW)
        pin_B = PinJoint(B0, stroke_color=ORANGE)
        pin_C = PinJoint(C0, stroke_color=GREEN)
        pin_D = PinJoint(D0, stroke_color=BLUE)
        pin_E = PinJoint(E0, stroke_color=PURPLE)

        # labels
        lbl_A = JointLabel("A", A0, direction=UP + RIGHT)
        lbl_B = JointLabel("B", B0, direction=DOWN + LEFT)
        lbl_C = JointLabel("C", C0, direction=UP + LEFT)
        lbl_D = JointLabel("D", D0, direction=DOWN + RIGHT)
        lbl_E = JointLabel("E", E0, direction=UP)

        # slider + actuator
        slider    = SliderBlock(E0)
        act_arrow = ActuatorArrow(E0)

        # ── 3. staged build-up ────────────────────────────────────────────────

        self.add(hud, rail, ground_O2, ground_O4,
                 pin_O2, pin_O4, lbl_O2, lbl_O4)
        self.wait(0.3)

        self.play(Create(link2.line), run_time=0.5);  self.add(pin_A, lbl_A)
        self.play(Create(link4.line), run_time=0.5);  self.add(pin_B, lbl_B,
                                                                pin_C, lbl_C)
        self.play(Create(link3.line), run_time=0.5)
        self.play(Create(link5.line), run_time=0.5);  self.add(pin_D, lbl_D)
        self.play(Create(link6.line), run_time=0.5);  self.add(pin_E, lbl_E)
        self.play(FadeIn(slider), FadeIn(act_arrow),  run_time=0.5)
        self.wait(0.7)

        # ── 4. single ValueTracker drives all updaters ────────────────────────

        param = ValueTracker(0.0)

        def fi() -> int:
            return int(np.clip(
                round(param.get_value() * (NF - 1)), 0, NF - 1))

        # links
        link2.add_updater(lambda m: m.set_endpoints(O2_pt,           frames[fi()][0]))
        link4.add_updater(lambda m: m.set_endpoints(O4_pt,           frames[fi()][1]))
        link3.add_updater(lambda m: m.set_endpoints(frames[fi()][0], frames[fi()][2]))
        link5.add_updater(lambda m: m.set_endpoints(frames[fi()][1], frames[fi()][3]))
        link6.add_updater(lambda m: m.set_endpoints(frames[fi()][3], frames[fi()][4]))

        # joints
        for pin_mob, idx in [(pin_A,0),(pin_B,1),(pin_C,2),(pin_D,3),(pin_E,4)]:
            pin_mob.add_updater(
                lambda m, i=idx: m.move_joint_to(frames[fi()][i]))

        # labels
        dirs = [UP+RIGHT, DOWN+LEFT, UP+LEFT, DOWN+RIGHT, UP]
        for lbl_mob, idx, d in zip(
                [lbl_A, lbl_B, lbl_C, lbl_D, lbl_E], range(5), dirs):
            lbl_mob.add_updater(
                lambda m, i=idx: m.follow_joint(frames[fi()][i]))

        # slider + arrow
        slider.add_updater(
            lambda m: m.move_slider_to(frames[fi()][4]))
        act_arrow.add_updater(
            lambda m: m.follow_slider(frames[fi()][4]))

        # ── 5. trace paths ────────────────────────────────────────────────────

        coupler_trace = TracedPath(
            lambda: frames[fi()][2].copy(),
            stroke_color=GREEN_B, stroke_width=2.0,
            stroke_opacity=0.85, dissipating_time=4.5)

        slider_trace = TracedPath(
            lambda: frames[fi()][4].copy(),
            stroke_color=BLUE_B, stroke_width=1.5,
            stroke_opacity=0.55, dissipating_time=2.5)

        self.add(coupler_trace, slider_trace)

        # ── 6. animate ────────────────────────────────────────────────────────
        for _ in range(self.N_CYCLES):
            self.play(param.animate.set_value(1.0),
                      run_time=self.CYCLE_TIME, rate_func=linear)
            self.play(param.animate.set_value(0.0),
                      run_time=self.CYCLE_TIME, rate_func=linear)

        self.wait(1.0)