
from dataclasses import dataclass

from manim import *


@dataclass(frozen=True)
class BeamDimensions:
    length: float = 6.0
    height: float = 2.0
    width: float = 1.8
    flange_thickness: float = 0.6
    web_thickness: float = 0.6


class PureBending(ThreeDScene):
    def build_beam(self, dims: BeamDimensions) -> VGroup:
        flange = Prism(
            dimensions=[dims.length, dims.flange_thickness, dims.width],
            fill_color=BLUE,
            fill_opacity=0.35,
            stroke_color=BLUE_E,
            stroke_width=1.5,
        )
        web_height = dims.height - dims.flange_thickness
        web = Prism(
            dimensions=[dims.length, web_height, dims.web_thickness],
            fill_color=BLUE,
            fill_opacity=0.35,
            stroke_color=BLUE_E,
            stroke_width=1.5,
        )

        flange.move_to([0, dims.height / 2 - dims.flange_thickness / 2, 0])
        web.move_to([0, -dims.flange_thickness / 2, 0])

        return VGroup(flange, web)

    def build_longitudinal_section_xy(self, dims: BeamDimensions) -> Rectangle:
        # This section is kept in the XY plane (z = 0).
        return Rectangle(
            width=dims.length,
            height=dims.height,
            color=YELLOW,
            fill_color=YELLOW,
            fill_opacity=0.25,
            stroke_width=3,
        )

    def build_side_cross_section_zy(self, dims: BeamDimensions) -> Polygon:
        flange_width = dims.width
        flange_thickness = dims.flange_thickness
        web_width = dims.web_thickness

        y_bottom = -dims.height / 2
        y_web_top = dims.height / 2 - flange_thickness
        y_top = dims.height / 2
        z_left_flange = -flange_width / 2
        z_right_flange = flange_width / 2
        z_left_web = -web_width / 2
        z_right_web = web_width / 2

        # Build a standard T-section in the local XY plane, then rotate it onto the ZY plane.
        polygon_points = [
            [z_left_web, y_bottom, 0],
            [z_right_web, y_bottom, 0],
            [z_right_web, y_web_top, 0],
            [z_right_flange, y_web_top, 0],
            [z_right_flange, y_top, 0],
            [z_left_flange, y_top, 0],
            [z_left_flange, y_web_top, 0],
            [z_left_web, y_web_top, 0],
        ]

        section = Polygon(
            *polygon_points,
            color=ORANGE,
            fill_color=ORANGE,
            fill_opacity=0.25,
            stroke_width=2.5,
        )
        section.rotate(PI / 2, axis=UP)
        section.move_to([dims.length / 2, 0, 0])
        return section

    def build_cross_section_xz(self, dims: BeamDimensions) -> Rectangle:
        section = Rectangle(
            width=dims.length,
            height=dims.width,
            color=TEAL,
            fill_color=TEAL,
            fill_opacity=0.2,
            stroke_width=2,
        )
        section.rotate(PI / 2, axis=RIGHT)
        section.move_to([0, dims.height / 2 - dims.flange_thickness / 2, 0])
        return section

    def build_neutral_axis(self, dims: BeamDimensions) -> Line3D:
        return Line3D(
            start=[-dims.length / 2, 0, 0],
            end=[dims.length / 2, 0, 0],
            color=RED,
            thickness=0.02,
        )

    def construct(self):
        dims = BeamDimensions()

        axes = ThreeDAxes(
            x_range=[-4, 4, 1],
            y_range=[-3, 3, 1],
            z_range=[-3, 3, 1],
            x_length=10,
            y_length=6,
            z_length=6,
            axis_config={"include_ticks": False, "include_numbers": False},
        )

        beam = self.build_beam(dims)
        section_xy = self.build_longitudinal_section_xy(dims)
        section_zy = self.build_side_cross_section_zy(dims)
        section_xz = self.build_cross_section_xz(dims)
        neutral_axis = self.build_neutral_axis(dims)

        x_label = MathTex("x", color=RED).scale(0.7).move_to(axes.c2p(4.25, 0, 0))
        y_label = MathTex("y", color=GREEN).scale(0.7).move_to(axes.c2p(0, 3.25, 0))
        z_label = MathTex("z", color=BLUE).scale(0.7).move_to(axes.c2p(0, 0, 3.25))
        self.add_fixed_orientation_mobjects(x_label, y_label, z_label)

        self.set_camera_orientation(
            phi=60 * DEGREES, theta=45* DEGREES,
            gamma=120* DEGREES,
        )


        # Static scene for fast single-frame rendering.
        self.add(axes, beam, section_xy, section_xz, section_zy, neutral_axis)
        self.add(x_label, y_label, z_label)
        self.wait()
        self.remove(section_xy)
        self.wait()
        self.remove(section_xz)

        self.wait()
        
        section_zy.shift(RIGHT * 1)

        self.add(section_zy)
        self.wait()
        section_zy.rotate(90 * DEGREES, axis=UP)

        self.add(section_zy)
        self.wait()

