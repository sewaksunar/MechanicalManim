from manim import *

class MyAxes(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            z_range=[-5, 5, 1],
            x_length=6,
            y_length=6,
            z_length=6,
        )

        # self.set_camera_orientation(phi=60 * DEGREES, theta=-60 * DEGREES)
        # axes.rotate(PI / 2, axis=RIGHT)

        self.set_camera_orientation(phi=60 * DEGREES, theta=-60* DEGREES)
        axes.rotate(PI / 2, axis=RIGHT)
        self.add(axes)

        x_label = MathTex("x").next_to(axes.x_axis.get_end(), RIGHT)
        y_label = MathTex("y").next_to(axes.y_axis.get_end(), UP)
        z_label = MathTex("z").next_to(axes.z_axis.get_end(), IN + LEFT)

        # Stays at 3D tip position but always faces the screen
        self.add_fixed_orientation_mobjects(x_label, y_label, z_label)
        
        # self.begin_ambient_camera_rotation(rate=0.3, about="theta")
        # self.wait(2)
        # self.stop_ambient_camera_rotation()
        self.wait(1)
        def sine_wave(t):
            return axes.c2p(t, np.sin(t), 0)
        sine_wave = ParametricFunction(
            # lambda t: axes.c2p(t, np.sin(t), 0),
            sine_wave,
            t_range=[-TAU, TAU],
            color=YELLOW,
            stroke_width=4,
        )
        self.add(sine_wave)
        cube = Cube(side_length=1, fill_opacity=0.7, fill_color=BLUE)
        self.add(cube)

        self.begin_ambient_camera_rotation(rate=0.3, about="theta")
        self.wait(2)
        self.stop_ambient_camera_rotation()