from manim import *
from dataclasses import dataclass

@dataclass(frozen=True)
class BeamDimensions:
    length: float = 5.0
    height: float = 2.0
    width: float = 1.8
    flange_thickness: float = 0.6
    web_thickness: float = 0.6

class Beam3D(ThreeDScene):
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
    def construct(self):
        dims = BeamDimensions()
        axes = ThreeDAxes(
            x_range=[-(dims.length / 2 + 1), dims.length / 2 + 1, 1],
            y_range=[-dims.height - 1, dims.height + 1, 1],
            z_range=[-dims.width - 1, dims.width + 1, 1],
            x_length=6,
            y_length=7,
            z_length=6,
        )
        self.set_camera_orientation(phi=45 * DEGREES, theta=45 * DEGREES)

        labels = axes.get_axis_labels()
        self.add(axes, labels)
        beam = self.build_beam(dims)
        self.add(beam)
        # self.move_camera(phi=45 * DEGREES, theta=45 * DEGREES, run_time=4)
        self.set_camera_orientation(phi=None, theta=None)
        section = self.cross_section_zy(dims)
        self.add(section)

        section.rotate(90 * DEGREES, axis=UP, about_point=ORIGIN)
        
        section.shift(RIGHT * (dims.length / 2 + 2))

        self.add(section)

        long_section = self.longitudinal_section_xy(dims)
        self.add(long_section)

        centroid = Dot(radius=0.05).move_to([0, self.centroid(dims), 0])
        centroid.shift(RIGHT * (dims.length / 2 + 2))
        self.add(centroid)
        self.add(self.neutral_plane(dims).shift(RIGHT * (dims.length / 2 + 2)))

        self.add(self.bend_neutral_plane(dims, moment=1000).shift(RIGHT * (dims.length / 2 + 2)))

        # self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        # self.set_camera_orientation(phi=90 * DEGREES, theta=0 * DEGREES)
        # self.set_camera_orientation(
        #     phi=60 * DEGREES, theta=45* DEGREES,
        #     gamma=120* DEGREES,
        # )
        # The standard way to get your exact view
        # self.set_camera_orientation(phi=90 * DEGREES, theta=90 * DEGREES)
        # Force a true, mathematically flat orthographic projection
        # self.set_camera_orientation(phi=90 * DEGREES, theta=90 * DEGREES)
        # The standard "3D Angle" view
        # self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        # Standard view: X is horizontal (right), Y is vertical (up)
        # self.set_camera_orientation(phi=90 * DEGREES, theta=0 * DEGREES, gamma=90 * DEGREES)
        # The standard way to get your exact drawing orientation
        # The precise configuration to match your drawing exactly
        self.set_camera_orientation(phi=60 * DEGREES, theta=-135 * DEGREES, gamma=45 * DEGREES)

        # self.set_camera_orientation(phi=60 * DEGREES, theta=45 * DEGREES)
        # self.set_camera_orientation(phi=90 * DEGREES, theta=90 * DEGREES, gamma=0 * DEGREES)    # cross section yz plane
    
    def cross_section_zy(self, dims: BeamDimensions) -> Polygon:
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
        points = [
            [z_left_flange, y_top, 0],
            [z_right_flange, y_top, 0],
            [z_right_flange, y_web_top, 0],
            [z_left_web, y_web_top, 0],
            [z_left_web, y_bottom, 0],
            [z_right_web, y_bottom, 0],
            [z_right_web, y_web_top, 0],
            [z_left_flange, y_web_top, 0],
        ]
        section = Polygon(*points, color=YELLOW, fill_color=YELLOW, fill_opacity=0.25)
        section.rotate(90 * DEGREES, axis=UP, about_point=ORIGIN)
        return section
    
    def longitudinal_section_xy(self, dims: BeamDimensions) -> Rectangle:
        section = Rectangle(
            width=dims.length,
            height=dims.height,
            color=GREEN,
            fill_color=GREEN,
            fill_opacity=0.25,
            stroke_width=2,
        )
        return section
    
    # for symmetrical about xy place, nutral axis is centroid of cross section
    def centroid(self, dims: BeamDimensions) -> float:
        A_flange = dims.width * dims.flange_thickness
        A_web = dims.web_thickness * (dims.height - 2 * dims.flange_thickness)
        y_flange = dims.height / 2 - dims.flange_thickness / 2
        y_web = 0
        centroid = (A_flange * y_flange + A_web * y_web) / (A_flange + A_web)   
        return centroid
    
    def neutral_plane(self, dims: BeamDimensions) -> Rectangle:
        y_centroid = self.centroid(dims)
        plane = Rectangle(
            width=dims.length,
            height=dims.width,
            color=RED,
            fill_color=RED,
            fill_opacity=0.25,
            stroke_width=2,
        )
        plane.rotate(90 * DEGREES, axis=RIGHT)
        plane.move_to([0, y_centroid, 0])
        return plane
    
    # giving positive bending moment from two ends about z axis
    
    # neutral plane is at y = centroid, so deformation is zero there, and maximum at top and bottom
    def bend_neutral_plane(self, dims: BeamDimensions, moment: float) -> Surface:
        E = 200e9  # Young's modulus in Pascals
        I = (dims.width * dims.height**3 - (dims.width - dims.web_thickness) * (dims.height - 2 * dims.flange_thickness)**3) / 12
        rho = moment / (E * I)
        rho = 4 # for testing: radius of curvature
        nu = 0.3  # Poisson's ratio
        L = dims.length
        y_centroid = self.centroid(dims)
        rho_anticlastic = -rho / nu  # anticlastic radius of curvature
        rho_anticlastic = 3 # for testing
        section = Surface(
            lambda u, v: np.array([
                u - L/2,  # keep x-axis length fixed
                y_centroid + rho * (1 - np.cos((u - L/2) / rho)) - rho * (1 - np.cos(L / (2 * rho))),  # primary bending (y)
                (v - dims.width / 2) + rho_anticlastic * (1 - np.cos((v - dims.width / 2) / rho_anticlastic)) - rho_anticlastic * (1 - np.cos(dims.width / (2 * rho_anticlastic)))  # anticlastic curvature (z) - transverse arc
            ]),
            u_range=[0, L],
            v_range=[0, dims.width],
            fill_color=PURPLE,
            fill_opacity=0.25,
            stroke_color=PURPLE_E,
            stroke_width=1.5,
        )
        return section
                
