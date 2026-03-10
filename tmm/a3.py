"""
Inline Crank-Slider Mechanism  ─  DOF = 1
==========================================
Grübler:
  n = 4  (ground, crank, connecting-rod, piston/slider)
  j = 4  (O revolute, A revolute, B revolute, rail prismatic)
  M = 3(n−1) − 2j = 3(3) − 2(4) = 1  ✓

Single input:  θ  (crank angle, motor at O)

Kinematics (inline, zero offset):
  A = O + R·[cosθ, sinθ]                  crank pin
  B = [A_x + √(L²−A_y²),  y_rail]         piston pin

Run:
    manim -pql crank_slider.py q1      # preview
    manim -pqh crank_slider.py q1      # HD render
"""

from manim import *
import numpy as np


# ══════════════════════════════════════════════════════════════════════════════
#  Colour palette  (dark engineering aesthetic)
# ══════════════════════════════════════════════════════════════════════════════
C_BG       = "#0D1117"   # scene background
C_CRANK    = "#E74C3C"   # crank arm / disk rim
C_DISK_BG  = "#1C2833"   # crank disk fill
C_ROD      = "#2E86C1"   # connecting rod
C_PISTON   = "#7F8C8D"   # piston body (silver-gray)
C_PISTON_F = "#4D5656"   # piston fill
C_CYL      = "#A9B7C6"   # cylinder walls
C_GROUND   = "#566573"   # ground hatching
C_PIN      = "#F4D03F"   # joint pins / bearings  (gold)
C_LABEL    = "#ECF0F1"   # text
C_TDC      = "#2ECC71"   # TDC marker (green)
C_BDC      = "#E67E22"   # BDC marker (orange)
C_TRACE    = "#E74C3C"   # crank-pin trace


# ══════════════════════════════════════════════════════════════════════════════
#  Helper
# ══════════════════════════════════════════════════════════════════════════════
def v3(xy) -> np.ndarray:
    """2-D array-like → 3-D Manim vector."""
    return np.array([float(xy[0]), float(xy[1]), 0.0])


# ══════════════════════════════════════════════════════════════════════════════
#  Reusable VGroup components
# ══════════════════════════════════════════════════════════════════════════════

class GroundMount(VGroup):
    """
    Heavy base plate + diagonal hatch under the crank bearing.

    Usage
    -----
        GroundMount(pivot_3d, width=1.4)
    """
    def __init__(self, pivot: np.ndarray,
                 width: float = 1.4,
                 color=C_GROUND, **kwargs):
        super().__init__(**kwargs)
        # ── solid base plate ──────────────────────────────────────────────────
        plate = Rectangle(
            width=width, height=0.18,
            fill_color="#1C2833", fill_opacity=1,
            color=color, stroke_width=2.5,
        ).move_to(pivot + DOWN * 0.09)
        self.add(plate)
        # ── diagonal hatch lines ──────────────────────────────────────────────
        n = 8
        for k in range(n):
            x = pivot[0] - width / 2 + (k + 0.5) * width / n
            self.add(Line(
                [x,        pivot[1] - 0.18, 0],
                [x - 0.14, pivot[1] - 0.36, 0],
                color=color, stroke_width=1.2))
        # ── bottom baseline ───────────────────────────────────────────────────
        self.add(Line(
            pivot + np.array([-width / 2 - 0.05, -0.18, 0]),
            pivot + np.array([ width / 2 + 0.05, -0.18, 0]),
            color=color, stroke_width=2.0))


class CylinderBlock(VGroup):
    """
    Horizontal cylinder: two wall lines + closed right end cap +
    faint centreline.

    Parameters
    ----------
    x_left  : left opening of the bore (piston enters from here)
    x_right : closed end (right wall)
    y       : centreline y-coordinate
    bore_r  : half-bore height
    """
    def __init__(self, x_left: float, x_right: float,
                 y: float, bore_r: float = 0.40,
                 color=C_CYL, **kwargs):
        super().__init__(**kwargs)
        kw = dict(color=color, stroke_width=3.5)
        # top and bottom walls
        self.add(Line([x_left, y + bore_r, 0], [x_right, y + bore_r, 0], **kw))
        self.add(Line([x_left, y - bore_r, 0], [x_right, y - bore_r, 0], **kw))
        # closed right end cap
        self.add(Line([x_right, y + bore_r, 0], [x_right, y - bore_r, 0], **kw))
        # faint centreline (dashed)
        self.add(DashedLine(
            [x_left, y, 0], [x_right, y, 0],
            color=color, stroke_width=1.0, stroke_opacity=0.35,
            dash_length=0.18, dashed_ratio=0.4))


class DeadCentreMarker(VGroup):
    """
    Dashed vertical line + small label marking TDC or BDC.

    Parameters
    ----------
    x       : x-position of the dead-centre line
    y       : centreline y
    bore_r  : half-bore height (marker spans slightly outside bore)
    label   : "TDC" or "BDC"
    color   : marker color
    """
    def __init__(self, x: float, y: float, bore_r: float,
                 label: str, color=C_TDC, **kwargs):
        super().__init__(**kwargs)
        top = [x, y + bore_r + 0.22, 0]
        bot = [x, y - bore_r - 0.10, 0]
        self.add(DashedLine(top, bot,
                            color=color, stroke_width=1.5,
                            stroke_opacity=0.75,
                            dash_length=0.12, dashed_ratio=0.45))
        self.add(Text(label, font_size=15, color=color)
                 .next_to(top, UP, buff=0.05))


class CrankDisk(VGroup):
    """
    Static visual crank disk: filled circle + rim + 8 tick marks +
    central bearing dot.  The crank arm is drawn separately so it can
    rotate independently.

    Parameters
    ----------
    center : 3-D pivot position
    radius : disk radius
    """
    def __init__(self, center: np.ndarray,
                 radius: float = 0.72, **kwargs):
        super().__init__(**kwargs)
        # filled disk
        self.add(Circle(radius=radius,
                        fill_color=C_DISK_BG, fill_opacity=1,
                        color=C_CRANK, stroke_width=3.0
                        ).move_to(center))
        # tick marks at every 45°
        for a in np.linspace(0, 2 * np.pi, 8, endpoint=False):
            p_in  = center + (radius - 0.12) * np.array([np.cos(a), np.sin(a), 0])
            p_out = center +  radius          * np.array([np.cos(a), np.sin(a), 0])
            self.add(Line(p_in, p_out, color=C_CRANK, stroke_width=2.0))
        # central bearing
        self.add(Dot(center, radius=0.09, color=C_PIN))


class BearingRing(VGroup):
    """
    Bearing ring (annular circle) around a pin joint.

    Parameters
    ----------
    position    : 3-D centre
    outer_r     : outer ring radius
    color       : ring stroke color
    fill_color  : ring interior fill
    """
    def __init__(self, position: np.ndarray,
                 outer_r: float = 0.16,
                 color=C_ROD, fill_color=C_DISK_BG, **kwargs):
        super().__init__(**kwargs)
        self.add(Circle(radius=outer_r,
                        color=color, stroke_width=2.5,
                        fill_color=fill_color, fill_opacity=1
                        ).move_to(position))

    def move_bearing_to(self, pos: np.ndarray):
        self[0].move_to(pos)
        return self


class InfoPanel(VGroup):
    """
    Top-left HUD: mechanism title + DOF badge + input description.

    Parameters
    ----------
    title : mechanism name string
    dof   : degrees of freedom
    input_label : description of the driving input
    """
    def __init__(self,
                 title: str  = "Inline Crank-Slider",
                 dof: int    = 1,
                 input_label: str = "Input : θ  (motor at O)",
                 **kwargs):
        super().__init__(**kwargs)
        t0 = Text(title,       font_size=24, color=C_LABEL)
        t1 = Text(f"DOF = {dof}", font_size=20, color=YELLOW)
        t2 = Text(input_label, font_size=17, color=YELLOW_B)

        t1.next_to(t0, DOWN, aligned_edge=LEFT, buff=0.09)
        t2.next_to(t1, DOWN, aligned_edge=LEFT, buff=0.06)
        self.add(VGroup(t0, t1, t2).to_corner(UL, buff=0.28))


# ══════════════════════════════════════════════════════════════════════════════
#  Scene
# ══════════════════════════════════════════════════════════════════════════════

class q1(MovingCameraScene):

    # ── mechanism parameters ──────────────────────────────────────────────────
    O_POS  = np.array([-3.0, 0.0])   # crank centre (ground pivot)
    R      = 1.2                      # crank radius
    L      = 3.4                      # connecting-rod length
    T0     = 0.0                      # initial crank angle

    # ── visual parameters ─────────────────────────────────────────────────────
    DISK_R  = 0.72    # crank disk radius
    BORE_R  = 0.40    # cylinder bore half-height
    PIN_R   = 0.09    # pin dot radius
    ROD_W   = 7       # connecting-rod stroke width
    ARM_W   = 9       # crank arm stroke width
    PISTON_W = 0.55   # piston block width (along slider axis)
    PISTON_H = None   # set in construct from BORE_R

    # ── animation ─────────────────────────────────────────────────────────────
    CYCLES     = 4          # total crank revolutions
    REV_TIME   = 5.5        # seconds per revolution

    def construct(self):

        # ── camera ────────────────────────────────────────────────────────────
        self.camera.frame.set(width=10.0)
        self.camera.frame.move_to([-0.5, 0.25, 0])
        self.camera.background_color = C_BG

        # ── derived constants ─────────────────────────────────────────────────
        y_rail = self.O_POS[1]            # inline: rail on crank centreline
        x_tdc  = self.O_POS[0] + self.R + self.L  # B at θ=0  (outer dead centre)
        x_bdc  = self.O_POS[0] - self.R + self.L  # B at θ=π  (inner dead centre)
        stroke = x_tdc - x_bdc           # = 2R

        pw = self.PISTON_W
        ph = self.BORE_R * 1.75           # piston height < bore

        # cylinder extents
        cyl_left  = x_bdc - pw / 2 - 0.12
        cyl_right = x_tdc + pw / 2 + 0.28

        # ── kinematic getters (closures over param) ───────────────────────────
        param = ValueTracker(0.0)

        def theta() -> float:
            return self.T0 + param.get_value() * 2.0 * np.pi

        def get_A() -> np.ndarray:
            t = theta()
            return v3(self.O_POS + self.R * np.array([np.cos(t), np.sin(t)]))

        def get_B() -> np.ndarray:
            A  = get_A()
            dy = A[1] - y_rail
            dx = np.sqrt(max(self.L ** 2 - dy ** 2, 1e-9))
            return v3([A[0] + dx, y_rail])

        # ── static objects ────────────────────────────────────────────────────

        ground    = GroundMount(v3(self.O_POS), width=1.5)
        cylinder  = CylinderBlock(cyl_left, cyl_right, y_rail, self.BORE_R)
        odc_mark  = DeadCentreMarker(x_tdc, y_rail, self.BORE_R, "ODC", color=C_TDC)
        idc_mark  = DeadCentreMarker(x_bdc, y_rail, self.BORE_R, "IDC", color=C_BDC)
        panel     = InfoPanel()

        # stroke dimension line (below cylinder)
        dim_y     = y_rail - self.BORE_R - 0.52
        dim_arrow = DoubleArrow(
            start=[x_bdc, dim_y, 0],
            end=[x_tdc,   dim_y, 0],
            color=C_LABEL, buff=0,
            stroke_width=1.5,
            max_tip_length_to_length_ratio=0.06)
        dim_label = Text(f"Stroke = 2R = {stroke:.1f}",
                         font_size=15, color=C_LABEL
                         ).next_to(dim_arrow, DOWN, buff=0.08)
        dim_grp = VGroup(dim_arrow, dim_label)

        # static crank disk
        disk = CrankDisk(v3(self.O_POS), radius=self.DISK_R)

        # fixed pivot label
        lbl_O = Text("O", font_size=19, color=C_LABEL
                     ).next_to(v3(self.O_POS) + DOWN * 0.15, DL, buff=0.28)

        # ── dynamic objects (always_redraw) ───────────────────────────────────

        # — crank arm (spoke, rotates with θ) —
        crank_arm = always_redraw(lambda: Line(
            v3(self.O_POS), get_A(),
            color=C_CRANK, stroke_width=self.ARM_W,
        ))

        # — counterweight (opposite end of crank arm) —
        cw_len = self.DISK_R * 0.6   # counterweight stub length
        counterweight = always_redraw(lambda: Line(
            v3(self.O_POS),
            v3(self.O_POS - cw_len * np.array([
                np.cos(theta()), np.sin(theta())])),
            color=C_CRANK, stroke_width=self.ARM_W * 1.8,
            stroke_opacity=0.70,
        ))

        # — connecting rod body —
        rod = always_redraw(lambda: Line(
            get_A(), get_B(),
            color=C_ROD, stroke_width=self.ROD_W,
        ))

        # — big-end bearing (around crank pin A) —
        big_end = always_redraw(lambda: Circle(
            radius=self.PIN_R + 0.10,
            color=C_ROD, stroke_width=3.0,
            fill_color=C_DISK_BG, fill_opacity=1,
        ).move_to(get_A()))

        # — small-end bearing (around piston pin B) —
        small_end = always_redraw(lambda: Circle(
            radius=self.PIN_R + 0.07,
            color=C_ROD, stroke_width=2.5,
            fill_color=C_DISK_BG, fill_opacity=1,
        ).move_to(get_B()))

        # — crank pin dot (on top of big-end) —
        crank_pin = always_redraw(lambda: Dot(
            get_A(), radius=self.PIN_R, color=C_PIN))

        # — piston pin dot (on top of small-end) —
        piston_pin = always_redraw(lambda: Dot(
            get_B(), radius=self.PIN_R * 0.85, color=C_PIN))

        # — piston block —
        def make_piston() -> VGroup:
            B  = get_B()
            cx = B[0] + pw / 2      # piston geometry: B is at the left face
            cy = B[1]
            g  = VGroup()
            # body
            body = Rectangle(
                width=pw, height=ph,
                fill_color=C_PISTON_F, fill_opacity=1,
                color=C_PISTON, stroke_width=2.5,
            ).move_to([cx, cy, 0])
            g.add(body)
            # two piston ring grooves
            for dy_frac in [-0.28, 0.28]:
                dy = ph / 2 * dy_frac * 2
                g.add(Line(
                    [cx - pw * 0.46, cy + dy, 0],
                    [cx + pw * 0.46, cy + dy, 0],
                    color="#1C2833", stroke_width=1.8))
            # gudgeon pin (piston-pin axis marker)
            g.add(Line([cx, cy - ph * 0.15, 0], [cx, cy + ph * 0.15, 0],
                       color=C_PIN, stroke_width=2.0))
            return g

        piston = always_redraw(make_piston)

        # — crank angle arc + numeric readout —
        def make_angle_arc() -> VGroup:
            t   = theta() % (2 * np.pi)
            deg = np.degrees(t)
            arc = Arc(
                radius=0.48,
                start_angle=0.0,
                angle=t,
                arc_center=v3(self.O_POS),
                color=YELLOW_B, stroke_width=2.0, stroke_opacity=0.85,
            )
            lbl = Text(f"{deg:5.1f}°", font_size=15, color=YELLOW_B
                       ).next_to(v3(self.O_POS) + RIGHT * 0.55, UR, buff=0.05)
            return VGroup(arc, lbl)

        angle_arc = always_redraw(make_angle_arc)

        # — stroke-percentage readout (top-right) —
        def make_stroke_txt() -> Mobject:
            Bx  = get_B()[0]
            pct = (Bx - x_bdc) / stroke * 100
            return Text(f"Stroke: {pct:5.1f} %",
                        font_size=17, color=C_LABEL
                        ).to_corner(UR, buff=0.28)

        stroke_txt = always_redraw(make_stroke_txt)

        # — piston velocity bar (below dimension line) —
        def make_vel_bar() -> VGroup:
            t  = theta()
            # analytical piston velocity (normalised): dB_x/dθ / R
            # d(B_x)/dθ = −R sinθ − (R² sinθ cosθ)/√(L²−R²sin²θ)
            st = np.sin(t)
            ct = np.cos(t)
            denom = np.sqrt(max(self.L ** 2 - (self.R * st) ** 2, 1e-6))
            vel_norm = -(st + self.R * st * ct / denom)   # in [-1,1] approx
            # clamp to ±1
            vel_norm = np.clip(vel_norm, -1.0, 1.0)
            bar_max  = 1.8
            bar_y    = dim_y - 0.52
            bar_x0   = (x_bdc + x_tdc) / 2
            g = VGroup()
            # background track
            g.add(Line([bar_x0 - bar_max, bar_y, 0],
                       [bar_x0 + bar_max, bar_y, 0],
                       color=C_GROUND, stroke_width=2.5))
            # velocity fill bar
            bar_color = C_TDC if vel_norm >= 0 else C_BDC
            g.add(Line([bar_x0, bar_y, 0],
                       [bar_x0 + vel_norm * bar_max, bar_y, 0],
                       color=bar_color, stroke_width=7.0))
            # zero tick
            g.add(Dot([bar_x0, bar_y, 0], radius=0.04, color=C_LABEL))
            # label
            g.add(Text("Piston velocity", font_size=14, color=C_GROUND
                       ).next_to([bar_x0, bar_y, 0], DOWN, buff=0.10))
            return g

        vel_bar = always_redraw(make_vel_bar)

        # — joint labels —
        lbl_A = always_redraw(lambda: Text("A", font_size=18, color=C_LABEL)
                              .next_to(get_A(), UR, buff=0.13))
        lbl_B = always_redraw(lambda: Text("B", font_size=18, color=C_LABEL)
                              .next_to(get_B() + UP * 0.25, UP, buff=0.08))

        # — crank-pin circular trace —
        crank_trace = TracedPath(
            lambda: get_A().copy(),
            stroke_color=C_TRACE, stroke_width=1.5, stroke_opacity=0.40)

        # ── z-ordered scene assembly ──────────────────────────────────────────
        # Layer order (back → front):
        #   ground, cylinder, dead-centre markers, dim line,
        #   disk, counterweight, crank arm, rod,
        #   big/small end bearings, piston, pins, labels

        self.add(ground, cylinder, odc_mark, idc_mark, dim_grp, panel)
        self.wait(0.3)

        # ── staged build-up animation ─────────────────────────────────────────
        self.play(FadeIn(disk, lbl_O), run_time=0.5)
        self.play(Create(counterweight), Create(crank_arm), run_time=0.6)
        self.add(big_end, crank_pin, lbl_A)

        self.play(Create(rod), run_time=0.5)
        self.add(small_end, piston_pin)

        self.play(FadeIn(piston), run_time=0.4)
        self.add(lbl_B, angle_arc, stroke_txt, vel_bar, crank_trace)
        self.wait(0.6)

        # ── main animation ────────────────────────────────────────────────────
        self.play(
            param.animate.set_value(float(self.CYCLES)),
            run_time=self.CYCLES * self.REV_TIME,
            rate_func=linear,
        )
        self.wait(1.2)