## SYMMETRIC MEMBERS IN PURE BENDING
from manim import *


class PureBending(Scene):
    def construct(self):
        L = 4  # Length of the beam
        t = 0.5  # Thickness of the beam
        
        axes_origin = DOWN*t

        axes = Axes(
            x_range=[0, L, 1],
            y_range=[-t*1, t*3, 1],
            x_length=L*1,
            y_length=t*8,
            axis_config={"include_ticks": False, "include_numbers": False},
            tips=False            
        )

        axes.shift(axes_origin - axes.c2p(0, 0))
        y_label = axes.get_y_axis_label(
            Tex("$y$").scale(0.65),
            edge=UP,
            direction=UP,
            buff=0.1,
        )
        x_label = axes.get_x_axis_label(
            Tex("$x$").scale(0.65),
            edge=RIGHT,
            direction=RIGHT,
            buff=0.1,
        )
        self.add(axes, x_label, y_label)

        lines = []
        for y in np.linspace(-t/2, t/2, 3):
            line = Line(LEFT*L/2, RIGHT*L/2).shift(UP*y)
            lines.append(line)

        beam = VGroup(*lines)
        beam.move_to(axes_origin)
        self.add(beam)

        top_line = lines[-1]
        mid_line = lines[len(lines) // 2]
        bottom_line = lines[0]
        neutral_line = mid_line.shift(UP * (t/2 - 0)) # neutral line is at the mid line for symmetric beams

        beam_block = Polygon(
            top_line.get_start(), top_line.get_end(), bottom_line.get_end(), bottom_line.get_start(),
            color=ORANGE, fill_opacity=0.5, stroke_width=2)
        self.add(beam_block)

        # bending shape
        # 1/rho = M/EI, where M is the bending moment and I is the second moment of area
        E = 1  # Assume a constant Young's modulus for simplicity
        I = (t**3) / 12  # Second moment of area for a rectangular cross-section
        M = 1  # Assume a constant bending moment for simplicity
        rho = (E*I)/M
        rho = 2 # neutral line radius of curvature
        y1 = rho * (1 - np.cos(axes.c2p(0, 0)[0] / rho)) # top line radius
        y2 = rho * (1 - np.cos(axes.c2p(0, 0)[0] / rho)) # mid line radius
        y3 = rho * (1 - np.cos(axes.c2p(0, 0)[0] / rho)) # bottom line radius
        top_line_center_circle = np.array(top_line.get_center())
        top_line_center_circle += np.array([0, rho, 0])
        self.add(Dot(top_line_center_circle, color=RED))
        
        # cross section
        h_line = Line(
            axes.c2p(0, 0, 0),
            axes.c2p(0, t, 0),
            color=RED,
            stroke_width=2,
        )
        print(h_line.get_start())
        print(h_line.get_end())
        h_line.move_to(RIGHT*L)
        self.add(h_line)
