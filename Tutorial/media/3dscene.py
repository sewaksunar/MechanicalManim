from manim import *

class CameraSetup(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=(-3, 3, 1),
            y_range=(-3, 3, 1),
            z_range=(-3, 3, 1),
            x_length=6,
            y_length=6,
            z_length=6,
            axis_config={"color": BLUE},
        )

        # Manually place labels at the tip of each axis
        label_x = Text("X", font_size=28, color=RED).move_to(axes.c2p(3.4, 0, 0))
        label_y = Text("Y", font_size=28, color=GREEN).move_to(axes.c2p(0, 3.4, 0))
        label_z = Text("Z", font_size=28, color=YELLOW).move_to(axes.c2p(0, 0, 3.4))

        # Line segment from point A to point B in 3D space
        point_a = axes.c2p(-2, -2, -1)
        point_b = axes.c2p(2, 2, 1)

        line = Line3D(
            start=point_a,
            end=point_b,
            color=ORANGE,
            thickness=0.03,
        )

        # Dot markers at endpoints
        dot_a = Sphere(radius=0.08, color=RED).move_to(point_a)
        dot_b = Sphere(radius=0.08, color=GREEN).move_to(point_b)

        # Labels for the endpoints
        label_a = Text("A", font_size=24, color=RED).move_to(point_a + np.array([-0.3, -0.3, 0]))
        label_b = Text("B", font_size=24, color=GREEN).move_to(point_b + np.array([0.3, 0.3, 0]))

        # Set initial camera
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)

        # self.add(axes)
        # self.wait()

        # ✅ Billboard all labels so they always face the camera
        self.add_fixed_orientation_mobjects(label_x, label_y, label_z)
        self.add_fixed_orientation_mobjects(label_a, label_b)

        # Animate drawing the line and dots
        self.play(Create(line), run_time=2)
        self.play(
            FadeIn(dot_a), FadeIn(dot_b),
            Write(label_a), Write(label_b),
            Write(label_x), Write(label_y), Write(label_z),
        )
        self.wait()

        # Rotate camera — labels will track the camera
        self.move_camera(phi=60 * DEGREES, theta=-30 * DEGREES, run_time=3)
        self.wait()

        # Extra rotation to clearly demonstrate billboarding
        self.move_camera(phi=45 * DEGREES, theta=60 * DEGREES, run_time=3)
        self.wait()