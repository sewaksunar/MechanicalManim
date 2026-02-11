from manim import *
import numpy as np
class Slider(MovingCameraScene):
    def construct(self):
        slider = Square(side_length=4, color=BLUE, fill_opacity=0.5)
        self.play(Create(slider))
        leftslider = Square(side_length=0.5, color=RED, fill_opacity=1).move_to(LEFT*2)
        self.play(Create(leftslider))
        center = leftslider.get_center()
        self.play(self.camera.frame.animate.move_to(center).set(width=5))

# Peltion of the blade is not working, 
# so I will just make a simple polygon and 
# move the camera to it.
class CurveBlade(MovingCameraScene):
    def construct(self):
        blade = Polygon(ORIGIN, RIGHT, UP, color=GREEN, fill_opacity=0.5)
        # self.play(Create(blade))
        center = blade.get_center()
        self.cam_center = blade.get_center()
        v_line = Line(DOWN*3, UP*3, color=BLUE)
        self.add(v_line)
        h_line = Line(ORIGIN, RIGHT*3, color=RED)
        self.add(h_line)

        # inlet angle is 30 degrees, so we can calculate the point on the blade at that angle
        outlet_angle = 140 * DEGREES
        length = 100
        outlet_line = Line(RIGHT*3, [length * np.cos(outlet_angle), length * np.sin(outlet_angle), 0], color=YELLOW)
        self.add(outlet_line)

        inlet_angle = 210 * DEGREES
        inlet_line = Line(RIGHT*3, [length * np.cos(inlet_angle), length * np.sin(inlet_angle), 0], color=YELLOW)
        self.add(inlet_line)

        inlet_point = np.linalg.solve(inlet_line,outlet_line)
        outlet_point = np.linalg.solve(outlet_line,inlet_line)
        self.add(Dot(inlet_point, color=ORANGE))
        self.add(Dot(outlet_point, color=ORANGE))

    def blade(self):
        n_points = 120
        angles = np.linspace(0, 2 * PI, n_points)

        blade_points = [
            [
                self.cam_center[0] + self.get_cam_radius(theta) * np.cos(theta),
                self.cam_center[1] + self.get_cam_radius(theta) * np.sin(theta),
                0
            ]
            for theta in angles
        ]

        blade = Polygon(
            *blade_points,
            color=TEAL_D,
            fill_opacity=0.8,
            stroke_color=TEAL_B,
            stroke_width=2.5
        )

        return blade
    
    def get_cam_radius(self, theta):
        """Calculate cam radius at given angle with smooth profile"""
        self.max_variation = 0.6
        self.base_radius = 2.0
        variation = self.max_variation * (
            0.6 + 0.25 * np.sin(2 * theta) + 0.15 * np.sin(3 * theta)
        )
        return self.base_radius + variation