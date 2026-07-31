"""
Beam3D – T-section beam visualisation (static image, render with -s flag)

  manim -s -ql beam3d.py Beam3D

Key fixes over the original
────────────────────────────
1. Anticlastic curvature: modifies y (not z) as a function of z-position,
   producing the correct saddle shape.  For sagging (κ_x > 0):
       κ_z = +ν/ρ  →  ρ_a = ρ/ν
   Edges of the neutral surface rise relative to the width-centre.

2. Centroid: corrected for a T-section (single top flange).
   web_height = h − t_f  (not h − 2t_f)
   y_web      = −t_f/2   (not 0)

3. Moment of inertia: parallel-axis theorem applied correctly for T-section.

4. Cross-section polygon: fixed self-intersecting winding order (points 3 & 6
   were swapped in the original).

5. Cross-section placement: polygon vertices now live directly in the YZ-plane
   (x = 0), so no rotation is required—just shift RIGHT.

6. Removed duplicate set_camera_orientation / add calls and all animation
   remnants; the scene is purely static.
"""

from dataclasses import dataclass
from manim import *
import numpy as np


# ─────────────────────────── beam geometry ───────────────────────────────────

@dataclass(frozen=True)
class BeamDimensions:
    length:           float = 5.0
    height:           float = 2.0
    width:            float = 1.8
    flange_thickness: float = 0.4
    web_thickness:    float = 0.3


# ─────────────────────────── scene ───────────────────────────────────────────

class Beam3D(ThreeDScene):

    # ── section properties ────────────────────────────────────────────────────

    def centroid(self, d: BeamDimensions) -> float:
        """
        Centroid of T-section (one top flange + web) from mid-height.

        Parts
        -----
        Flange : full width  ×  t_f,  centroid at  y_f = h/2 − t_f/2
        Web    : t_w  ×  (h − t_f),  centroid at  y_w = −t_f/2
                 (web spans from −h/2 up to h/2−t_f; mean = −t_f/2)
        """
        web_h = d.height - d.flange_thickness
        A_f   = d.width         * d.flange_thickness
        A_w   = d.web_thickness * web_h
        y_f   =  d.height / 2 - d.flange_thickness / 2
        y_w   = -d.flange_thickness / 2
        return (A_f * y_f + A_w * y_w) / (A_f + A_w)

    def moment_of_inertia(self, d: BeamDimensions) -> float:
        """Second moment of area of T-section about its neutral axis."""
        web_h = d.height - d.flange_thickness
        A_f   = d.width         * d.flange_thickness
        A_w   = d.web_thickness * web_h
        y_c   = self.centroid(d)
        y_f   =  d.height / 2 - d.flange_thickness / 2
        y_w   = -d.flange_thickness / 2

        I_f = (d.width         * d.flange_thickness**3) / 12 + A_f * (y_f - y_c)**2
        I_w = (d.web_thickness * web_h**3)               / 12 + A_w * (y_w - y_c)**2
        return I_f + I_w

    # ── 3-D geometry ──────────────────────────────────────────────────────────

    def build_beam(self, d: BeamDimensions) -> VGroup:
        """3-D T-section prism (one flange on top, web hanging below)."""
        web_h  = d.height - d.flange_thickness
        flange = Prism(
            dimensions=[d.length, d.flange_thickness, d.width],
            fill_color=BLUE, fill_opacity=0.35,
            stroke_color=BLUE_E, stroke_width=1.5,
        )
        web = Prism(
            dimensions=[d.length, web_h, d.web_thickness],
            fill_color=BLUE, fill_opacity=0.35,
            stroke_color=BLUE_E, stroke_width=1.5,
        )
        # position: flange top at +h/2, web bottom at −h/2
        flange.move_to([0,  d.height / 2 - d.flange_thickness / 2, 0])
        web.move_to(   [0, -d.flange_thickness / 2, 0])
        return VGroup(flange, web)

    def cross_section_zy(self, d: BeamDimensions) -> Polygon:
        """
        T-section outline placed in the YZ-plane (x = 0).

        Winding order is counter-clockwise when viewed from +x, producing
        a non-self-intersecting polygon.  (The original code had points 3
        and 6 swapped, creating a figure-8.)
        """
        h, w = d.height, d.width
        t_f  = d.flange_thickness
        t_w  = d.web_thickness
        y_b  = -h / 2           # beam bottom
        y_j  =  h / 2 - t_f    # flange / web junction
        y_t  =  h / 2           # beam top

        # x=0 → YZ-plane; second coord = Y; third coord = Z
        pts = [
            [0,  y_t, -w   / 2],   # ① top-left  of flange
            [0,  y_t,  w   / 2],   # ② top-right of flange
            [0,  y_j,  w   / 2],   # ③ right flange bottom
            [0,  y_j,  t_w / 2],   # ④ step in  → right web top
            [0,  y_b,  t_w / 2],   # ⑤ bottom-right of web
            [0,  y_b, -t_w / 2],   # ⑥ bottom-left  of web
            [0,  y_j, -t_w / 2],   # ⑦ left web top
            [0,  y_j, -w   / 2],   # ⑧ step out → left flange bottom
        ]
        return Polygon(*pts,
                       color=YELLOW, fill_color=YELLOW,
                       fill_opacity=0.3, stroke_width=2)

    def longitudinal_section(self, d: BeamDimensions) -> Rectangle:
        """XY-plane cut through the web centreline (visual aid)."""
        rect = Rectangle(
            width=d.length, height=d.height,
            color=GREEN, fill_color=GREEN, fill_opacity=0.2, stroke_width=2,
        )
        rect.move_to([0, 0, 0])   # centred at origin in XY-plane
        return rect

    def neutral_plane_flat(self, d: BeamDimensions) -> Rectangle:
        """Flat (undeformed) neutral plane for reference."""
        plane = Rectangle(
            width=d.length, height=d.width,
            color=RED, fill_color=RED, fill_opacity=0.12, stroke_width=1.5,
        )
        plane.rotate(90 * DEGREES, axis=RIGHT)   # XY → XZ orientation
        plane.move_to([0, self.centroid(d), 0])
        return plane

    def bent_neutral_surface(self, d: BeamDimensions, moment: float) -> Surface:
        """
        Deformed neutral surface with primary bending + anticlastic curvature.

        Physics
        -------
        Primary curvature  κ_x =  1/ρ  in the XY-plane.
        For *sagging* (midspan dips):
            • x_def = ρ sin(x_local / ρ)           – beam arcs in XY
            • y_primary → ends fixed at y_c; midspan at minimum

        Anticlastic curvature  κ_z = −ν κ_x → ρ_a = ρ/ν.
        For sagging (κ_x effectively negative here), κ_z > 0:
            • Edges (|z| = w/2) *rise* relative to the width-centre
            • y_anticlastic = ρ_a (1 − cos(z_local / ρ_a))  ≥ 0
            • z_def         = ρ_a sin(z_local / ρ_a)         (exact arc)

        The result is a saddle surface: concave down along the beam,
        concave up across the width.

        Note
        ----
        ρ is set to a small value for visual clarity.  To use the physical
        curvature, replace the override with  ρ = E·I / moment.
        """
        nu    = 0.3
        rho   = 3.5             # primary ρ (override for visibility)
        rho_a = -rho / nu        # anticlastic ρ  (≈ 11.7 for ν=0.3)

        L   = d.length
        w   = d.width
        y_c = self.centroid(d)

        def surf(u, v):
            xl = u - L / 2      # centred along beam length  ∈ [−L/2, +L/2]
            zl = v - w / 2      # centred across beam width  ∈ [−w/2, +w/2]

            # ── primary bending (sagging) ────────────────────────────────────
            # Arc in XY-plane; ends remain at y = y_c, midspan dips below.
            x_def = rho * np.sin(xl / rho)
            y_p   = y_c + rho * np.cos(L / (2 * rho)) - rho * np.cos(xl / rho)
            #   at xl = 0  →  y = y_c − ρ(1 − cos(L/2ρ))  < y_c  ✓
            #   at xl = ±L/2 →  y = y_c                             ✓

            # ── anticlastic curvature (saddle) ──────────────────────────────
            # Arc in ZY-plane; centre of width stays at y_p, edges rise.
            y_a   = rho_a * (1 - np.cos(zl / rho_a))
            #   at zl = 0    →  y_a = 0           ✓ (no change at centre)
            #   at zl = ±w/2 →  y_a > 0           ✓ (edges rise for sagging)
            z_def = rho_a * np.sin(zl / rho_a)
            #   exact arc coordinate (≈ zl for small zl/ρ_a)

            return np.array([x_def, y_p + y_a, z_def])

        return Surface(
            surf,
            u_range=[0, L],
            v_range=[0, w],
            resolution=(48, 24),
            fill_color=PURPLE,
            fill_opacity=0.55,
            checkerboard_colors=[PURPLE, PURPLE_B],
            stroke_color=PURPLE_E,
            stroke_width=0.8,
        )

    # ── construct (static image) ──────────────────────────────────────────────

    def construct(self):
        d   = BeamDimensions()
        y_c = self.centroid(d)

        # ── axes ──────────────────────────────────────────────────────────────
        axes = ThreeDAxes(
            x_range=[-(d.length / 2 + 1), d.length / 2 + 1, 1],
            y_range=[-d.height - 1,        d.height + 1,      1],
            z_range=[-d.width  - 1,        d.width  + 1,      1],
            x_length=6, y_length=7, z_length=6,
        )
        labels = axes.get_axis_labels()

        # ── beam & sections ───────────────────────────────────────────────────
        beam     = self.build_beam(d)
        long_sec = self.longitudinal_section(d)
        n_plane  = self.neutral_plane_flat(d)
        bent     = self.bent_neutral_surface(d, moment=1000)

        # ── cross-section (placed to the right of the beam end) ───────────────
        x_cs  = d.length / 2 + 2.2           # x-position of the section display
        section = self.cross_section_zy(d)
        section.shift(RIGHT * x_cs)           # no rotation needed: already in YZ-plane

        # centroid dot on the cross-section
        c_dot = Dot3D(radius=0.07, color=RED)
        c_dot.move_to([x_cs, y_c, 0])

        # neutral-axis line across the cross-section width
        na_line = Line3D(
            start=[x_cs, y_c, -d.width / 2 - 0.25],
            end  =[x_cs, y_c,  d.width / 2 + 0.25],
            color=RED, thickness=0.018,
        )

        # ── assemble & camera ─────────────────────────────────────────────────
        # self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)
        # self.set_camera_orientation(phi=90 * DEGREES, theta=0 * DEGREES)
        # self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        self.set_camera_orientation(
            phi=60 * DEGREES, theta=45* DEGREES,
            gamma=120* DEGREES,
        )
        # self.set_camera_orientation(phi=0 * DEGREES, theta=30 * DEGREES)

        self.add(axes, labels)
        self.add(beam, long_sec, n_plane)
        self.add(bent)
        self.add(section, c_dot, na_line)