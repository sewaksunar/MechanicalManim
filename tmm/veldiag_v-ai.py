"""
four_bar_mechanism.py
=====================
Four-bar crank-rocker linkage with live velocity-polygon construction.

KEY DESIGN RULES (Manim workflow)
──────────────────────────────────
1. Single source of truth  – ALL positions are computed from ValueTrackers.
   Never cache a position in a plain variable that the animation will outlive.
2. always_redraw()         – every Mobject that must stay in sync wraps its
   constructor in always_redraw(lambda: ...).  No add_updater() spaghetti.
3. Getter functions        – get_o2/o4/a/b() read trackers and return fresh
   np.ndarray every call.  Lambdas inside always_redraw call these getters so
   the whole scene stays consistent automatically.
4. Velocity polygon math   – direction-line intersection via 2x2 linear system
   (no magic numbers, works for any crank angle).
"""

from __future__ import annotations
import numpy as np
from manim import *

# ═══════════════════════════════════════════════════════════════════════════════
# 1.  PURE GEOMETRY  (no Manim imports required)
# ═══════════════════════════════════════════════════════════════════════════════

def circle_intersections(
    c1: np.ndarray, r1: float,
    c2: np.ndarray, r2: float,
) -> list[np.ndarray]:
    """Return 0-2 intersection points of two circles (3-D, z = 0)."""
    c1, c2 = np.asarray(c1, float)[:2], np.asarray(c2, float)[:2]
    d = np.linalg.norm(c2 - c1)
    if d == 0 or d > r1 + r2 or d < abs(r1 - r2):
        return []
    a   = (r1**2 - r2**2 + d**2) / (2 * d)
    h   = np.sqrt(max(0.0, r1**2 - a**2))
    mid = c1 + a * (c2 - c1) / d
    perp = np.array([-(c2[1] - c1[1]), c2[0] - c1[0]]) / d
    return [
        np.array([mid[0] + h*perp[0], mid[1] + h*perp[1], 0.0]),
        np.array([mid[0] - h*perp[0], mid[1] - h*perp[1], 0.0]),
    ]


def perp_unit(v: np.ndarray) -> np.ndarray:
    """Left-hand perpendicular unit vector (3-D, z = 0)."""
    n = np.linalg.norm(v[:2])
    return np.array([-v[1]/n, v[0]/n, 0.0])


def unit_vec(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


def line_line_intersect(
    p0: np.ndarray, d0: np.ndarray,
    p1: np.ndarray, d1: np.ndarray,
) -> np.ndarray | None:
    """
    Intersect two 2-D parametric lines: p0 + t*d0  and  p1 + s*d1.
    Returns the 3-D intersection point, or None if parallel.
    """
    A = np.array([[d0[0], -d1[0]],
                  [d0[1], -d1[1]]])
    b = (p1 - p0)[:2]
    try:
        t, _ = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        return None
    return p0 + t * d0


# ═══════════════════════════════════════════════════════════════════════════════
# 2.  REUSABLE MOBJECTS
# ═══════════════════════════════════════════════════════════════════════════════

_JR  = 0.06   # joint radius
_LSZ = 22     # label font size
_SW  = 2.0    # hatch mark stroke width


def _pin(pos: np.ndarray, r: float = _JR) -> Circle:
    """Small filled circle representing a pin joint."""
    return (
        Circle(radius=r, color=WHITE)
        .set_fill(BLACK, opacity=1)
        .move_to(pos)
    )


class Link(VGroup):
    """
    Rigid link: line segment + pin joints at each end + optional MathTex labels.

    Parameters
    ----------
    start, end       : 3-D coordinates
    s_label, e_label : LaTeX strings (empty = no label)
    s_dir,   e_dir   : Manim direction for label placement
    """

    def __init__(
        self,
        start: np.ndarray,
        end: np.ndarray,
        *,
        s_label: str = "",
        e_label: str = "",
        s_dir: np.ndarray = DOWN,
        e_dir: np.ndarray = LEFT,
        **kw,
    ):
        super().__init__(**kw)
        s, e  = np.asarray(start, float), np.asarray(end, float)
        self.sj = _pin(s)
        self.ej = _pin(e)
        self.ln = Line(s, e)
        self.add(self.sj, self.ej, self.ln)
        if s_label:
            self.add(MathTex(s_label, font_size=_LSZ).next_to(self.sj, s_dir))
        if e_label:
            self.add(MathTex(e_label, font_size=_LSZ).next_to(self.ej, e_dir))


class FrameLink(VGroup):
    """
    Fixed-ground link: line + pin joints + inclined hatch marks below the bar.

    Hatch parameters
    ----------------
    hatch_w     : length of each hatch mark
    hatch_sp    : spacing between marks along the link
    hatch_ratio : fraction of link length that is hatched (centred)
    hatch_ang   : inclination of marks (degrees) w.r.t. the downward normal
    """

    def __init__(
        self,
        start: np.ndarray,
        end: np.ndarray,
        *,
        s_label: str = "",
        e_label: str = "",
        s_dir: np.ndarray = DOWN,
        e_dir: np.ndarray = DOWN,
        hatch_w:     float = 0.20,
        hatch_sp:    float = 0.10,
        hatch_ratio: float = 0.60,
        hatch_ang:   float = 45.0,
        **kw,
    ):
        super().__init__(**kw)
        s, e  = np.asarray(start, float), np.asarray(end, float)
        d     = e - s
        L     = np.linalg.norm(d)
        tang  = d / L
        below = -perp_unit(d)                              # downward normal

        hatch_dir = unit_vec(
            np.cos(np.radians(hatch_ang)) * below
            + np.sin(np.radians(hatch_ang)) * tang
        )

        r0 = L * (1 - hatch_ratio) / 2                    # hatched region start
        for t in np.arange(r0, r0 + L * hatch_ratio, hatch_sp):
            p = s + tang * t
            self.add(Line(p, p + hatch_dir * hatch_w,
                          color=WHITE, stroke_width=_SW))

        # Joints and main line drawn on top of hatch marks
        self.sj = _pin(s)
        self.ej = _pin(e)
        self.add(self.sj, self.ej, Line(s, e))
        if s_label:
            self.add(MathTex(s_label, font_size=_LSZ).next_to(self.sj, s_dir))
        if e_label:
            self.add(MathTex(e_label, font_size=_LSZ).next_to(self.ej, e_dir))


class FourBarMechanism(VGroup):
    """
    Complete four-bar linkage assembled from four links.

    After construction, joint positions are exposed as plain attributes:
        .o2   – fixed pivot for crank  (link 2)
        .o4   – fixed pivot for rocker (link 4)
        .pt_a – moving joint A  (crank/coupler junction)
        .pt_b – moving joint B  (coupler/rocker junction)

    Typical always_redraw usage (positions update every frame):
        mech = always_redraw(lambda: FourBarMechanism(get_o2(), ang.get_value()))

    The class-level link lengths let external getters replicate the same
    geometry without having an instance handy.
    """

    # Geometric constants – retune only here
    L2 = 1.50   # crank   (O2 -> A)
    L3 = 4.50   # coupler (A  -> B)
    L4 = 3.00   # rocker  (O4 -> B)
    L1 = 2.00   # frame   (O2 -> O4)

    def __init__(self, origin: np.ndarray, angle: float, **kw):
        super().__init__(**kw)

        o2 = np.asarray(origin, float)
        o4 = o2 + RIGHT * self.L1
        a  = o2 + np.array([
            self.L2 * np.cos(angle),
            self.L2 * np.sin(angle),
            0.0,
        ])
        pts = circle_intersections(a, self.L3, o4, self.L4)
        b   = pts[0] if pts else (a + o4) / 2

        # Expose joint positions for external consumers
        self.o2, self.o4, self.pt_a, self.pt_b = o2, o4, a, b

        self.add(
            FrameLink(o2, o4, s_label="O_2", e_label="O_4"),   # link 1 (ground)
            Link(o2, a, e_label="A", e_dir=LEFT),               # link 2 (crank)
            Link(a,  b, e_label="B", e_dir=UP),                 # link 3 (coupler)
            Link(o4, b),                                        # link 4 (rocker)
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 3.  SCENE
# ═══════════════════════════════════════════════════════════════════════════════

# Layout
_ORIGIN_START = ORIGIN + DOWN * 2 + LEFT * 1   # O2 position at start
_ORIGIN_END   = DOWN   * 2 + LEFT * 4          # O2 position after translation
_VPOLE        = RIGHT  * 3.5 + UP * 0.5        # fixed pole of velocity polygon

# Visual
_VEL_SCALE = 1.4    # arrow length multiplier


class SpaceDiag(Scene):
    """
    Phase 1 – crank sweeps 135 -> 200 -> 135 deg   (always_redraw mechanism)
    Phase 2 – mechanism translates to analysis position
    Phase 3 – velocity polygon built step-by-step
              (all elements are always_redraw so they update if crank moves)
    """

    def construct(self) -> None:

        # ── ValueTrackers: ONLY mutable state in the scene ────────────────────
        self.ang = ValueTracker(135 * DEGREES)  # crank angle
        self.sft = ValueTracker(0.0)            # translation progress (0 -> 1)

        # ── Position getters: EVERY position derives from trackers ────────────
        #    All always_redraw lambdas call these; changing them here
        #    propagates everywhere automatically.
        L = FourBarMechanism                    # shorthand for class constants

        self.get_o2 = lambda: interpolate(
            _ORIGIN_START, _ORIGIN_END, self.sft.get_value()
        )
        self.get_o4 = lambda: self.get_o2() + RIGHT * L.L1
        self.get_a  = lambda: self.get_o2() + np.array([
            L.L2 * np.cos(self.ang.get_value()),
            L.L2 * np.sin(self.ang.get_value()),
            0.0,
        ])
        self.get_b  = lambda: (
            circle_intersections(
                self.get_a(), L.L3,
                self.get_o4(), L.L4,
            ) or [(self.get_a() + self.get_o4()) / 2]
        )[0]

        # ── Live mechanism (rebuilds every frame from trackers) ───────────────
        mech = always_redraw(
            lambda: FourBarMechanism(self.get_o2(), self.ang.get_value())
        )
        self.add(mech)

        # ── Phase 1: crank sweep ──────────────────────────────────────────────
        self.play(self.ang.animate.set_value(200 * DEGREES),
                  rate_func=linear, run_time=2)
        self.play(self.ang.animate.set_value(135 * DEGREES), run_time=2)

        # ── Phase 2: translate to analysis position ───────────────────────────
        self.play(self.sft.animate.set_value(1.0), run_time=1.5)
        self.wait(0.3)

        # ── Title ─────────────────────────────────────────────────────────────
        self.play(Write(
            Text("Crank-Rocker Mechanism", font_size=30).to_edge(UP)
        ))

        # ── Phase 3: velocity polygon ─────────────────────────────────────────
        self._build_velocity_polygon()
        self.wait(2)

    # ──────────────────────────────────────────────────────────────────────────
    # Velocity polygon construction
    # ──────────────────────────────────────────────────────────────────────────

    def _build_velocity_polygon(self) -> None:
        """
        Construct the velocity polygon in four steps.

        All mobjects use always_redraw so they update live when
        the crank angle changes in Step 5.

        Velocity polygon identities used:
            v_A = v_{A/O2} : perp to (A - O2), from pole o
            v_B = v_{B/O4} : perp to (B - O4), from pole o   (unknown scale)
            v_B = v_A + v_{B/A}                               (closing condition)
            v_{B/A}        : perp to (B - A),  from tip of v_A
        Point b = intersection of the two direction lines.
        """

        pole = _VPOLE.copy()   # fixed 3-D point; does NOT change with trackers

        # ── Step 0: highlight joints on mechanism ─────────────────────────────
        joints = always_redraw(lambda: VGroup(
            Dot(self.get_a(),  color=RED,    radius=0.07),
            Dot(self.get_b(),  color=RED,    radius=0.07),
            Dot(self.get_o2(), color=YELLOW, radius=0.07),
            Dot(self.get_o4(), color=YELLOW, radius=0.07),
        ))
        self.play(Create(joints))

        # Pole dot
        pole_dot = Dot(pole, color=WHITE, radius=0.06)
        pole_lbl = MathTex("o", font_size=22).next_to(pole_dot, DL, buff=0.08)
        self.play(FadeIn(pole_dot), Write(pole_lbl))

        # ── Step 1: v_A on mechanism, then copy to polygon panel ──────────────

        # Arrow at joint A on the mechanism
        va_mech = always_redraw(lambda: Arrow(
            self.get_a(),
            self.get_a() + perp_unit(self.get_a() - self.get_o2()) * _VEL_SCALE,
            buff=0, color=BLUE, max_tip_length_to_length_ratio=0.12,
        ))
        va_mech_lbl = always_redraw(lambda:
            MathTex(r"v_A", font_size=20)
            .next_to(va_mech.get_end(), UL, buff=0.05)
        )
        self.play(GrowArrow(va_mech), Write(va_mech_lbl))
        self.wait(0.3)

        # Same vector in polygon panel, tail at pole
        va_poly = always_redraw(lambda: Arrow(
            pole,
            pole + perp_unit(self.get_a() - self.get_o2()) * _VEL_SCALE,
            buff=0, color=BLUE, max_tip_length_to_length_ratio=0.12,
        ))
        va_poly_lbl = always_redraw(lambda:
            MathTex(r"v_A", font_size=20)
            .next_to(va_poly.get_end(), UR, buff=0.05)
        )
        self.play(TransformFromCopy(va_mech, va_poly), Write(va_poly_lbl))

        # ── Step 2: v_{B/O4} direction line (dashed, from pole) ──────────────

        vb_dir = always_redraw(lambda: DashedLine(
            pole,
            pole + perp_unit(self.get_b() - self.get_o4()) * _VEL_SCALE * 2.5,
            color=GREEN, dash_length=0.12, stroke_width=2,
        ))
        vb_dir_lbl = always_redraw(lambda:
            MathTex(r"v_{B/O_4}", font_size=18)
            .next_to(vb_dir.get_end(), RIGHT, buff=0.06)
        )
        self.play(Create(vb_dir), Write(vb_dir_lbl))

        # ── Step 3: v_{B/A} direction line (dashed, from tip of v_A) ─────────

        vba_dir = always_redraw(lambda: DashedLine(
            va_poly.get_end(),
            va_poly.get_end()
            + perp_unit(self.get_b() - self.get_a()) * _VEL_SCALE * 2.5,
            color=PURPLE, dash_length=0.12, stroke_width=2,
        ))
        vba_dir_lbl = always_redraw(lambda:
            MathTex(r"v_{B/A}", font_size=18)
            .next_to(vba_dir.get_end(), RIGHT, buff=0.06)
        )
        self.play(Create(vba_dir), Write(vba_dir_lbl))

        # ── Step 4: intersection b -> solid v_B and v_{B/A} ──────────────────

        def get_b_poly() -> np.ndarray:
            """
            Find point b in the velocity polygon:
                pole   + t * perp(B-O4)  = b
                va_tip + s * perp(B-A)   = b
            Solved with a 2x2 linear system.
            """
            d_vb  = perp_unit(self.get_b() - self.get_o4())
            d_vba = perp_unit(self.get_b() - self.get_a())
            va_tip = va_poly.get_end()
            pt = line_line_intersect(pole, d_vb, va_tip, d_vba)
            # Fallback: extend v_{B/O4} direction by full scale
            return pt if pt is not None else pole + d_vb * _VEL_SCALE

        b_dot = always_redraw(lambda:
            Dot(get_b_poly(), color=YELLOW, radius=0.07)
        )
        b_lbl = always_redraw(lambda:
            MathTex("b", font_size=20).next_to(b_dot, UR, buff=0.06)
        )

        # v_B: pole -> b
        vb_solid = always_redraw(lambda: Arrow(
            pole, get_b_poly(),
            buff=0, color=GREEN, max_tip_length_to_length_ratio=0.12,
        ))
        vb_lbl = always_redraw(lambda:
            MathTex(r"v_B", font_size=20)
            .next_to(vb_solid.get_end(), UR, buff=0.05)
        )

        # v_{B/A}: va_tip -> b
        vba_solid = always_redraw(lambda: Arrow(
            va_poly.get_end(), get_b_poly(),
            buff=0, color=PURPLE, max_tip_length_to_length_ratio=0.12,
        ))
        vba_lbl = always_redraw(lambda:
            MathTex(r"v_{B/A}", font_size=20)
            .next_to(vba_solid.get_center(), RIGHT, buff=0.08)
        )

        self.play(
            Create(b_dot),   Write(b_lbl),
            GrowArrow(vb_solid),  Write(vb_lbl),
            GrowArrow(vba_solid), Write(vba_lbl),
        )
        self.wait(0.5)

        # ── Step 5: animate crank; everything updates live ────────────────────
        self.play(
            self.ang.animate.set_value(175 * DEGREES),
            rate_func=smooth, run_time=3,
        )
        self.play(
            self.ang.animate.set_value(135 * DEGREES),
            rate_func=smooth, run_time=3,
        )