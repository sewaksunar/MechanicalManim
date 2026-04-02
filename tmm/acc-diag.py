from manim import *

class AccDiag(Scene):
    def construct(self):
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 5, 10],
            x_length=5,
            y_length=10,
            axis_config={"color": BLUE},
        )
        axes.move_to(ORIGIN)
        self.play(Create(axes))

        length_scale = 0.1

        # --- O4 ---
        O4_data = np.array([0.0, 0.0])
        O4 = Dot(axes.c2p(*O4_data), color=RED)
        gO4 = VGroup(O4, MathTex("O4", font_size=24).next_to(O4, LEFT+DOWN, buff=0.1))
        self.play(Create(gO4))

        # --- O2 ---
        O2_data = np.array([0.0, 300 * length_scale])
        O2 = Dot(axes.c2p(*O2_data), color=GREEN)
        gO2 = VGroup(O2, MathTex("O2", font_size=24).next_to(O2, LEFT+UP, buff=0.1))
        self.play(Create(gO2))

        # --- O2A ---
        O2A_end_data = O2_data + np.array([0.0, 175 * length_scale])
        O2A = Line(axes.c2p(*O2_data), axes.c2p(*O2A_end_data), color=YELLOW)
        O2A.rotate(195 * DEGREES, about_point=axes.c2p(*O2_data))

        A = Dot(O2A.get_end(), color=ORANGE)
        gO2A = VGroup(O2A, A, MathTex("A", font_size=24).next_to(A, RIGHT+UP, buff=0.1))
        self.play(Create(gO2A))

        # --- O4A ---
        A_data = np.array(axes.p2c(A.get_center()))
        direction_data = A_data - O4_data
        direction_data /= np.linalg.norm(direction_data)
        O4A_end_data = O4_data + direction_data * 700 * length_scale

        O4A = Line(axes.c2p(*O4_data), axes.c2p(*O4A_end_data), color=PURPLE)
        gO4A = VGroup(O4A, MathTex("O4A", font_size=24).next_to(O4A.get_midpoint(), RIGHT, buff=0.1))
        self.play(Create(gO4A))

        # --- Move everything to center ---
        everything = VGroup(axes, gO4, gO2, gO2A, gO4A)
        self.play(everything.animate.move_to(ORIGIN), run_time=1.5)

        self.wait(2)