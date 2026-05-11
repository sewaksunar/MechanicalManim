## SYMMETRIC MEMBERS IN PURE BENDING
from manim import *


class PureBending(Scene):
    def construct(self):
        L = 6  # Length of the beam
        t = 2 # Thickness of the beam
        
        axes_origin = DOWN*t + LEFT*L*0.5

        axes = Axes(
            x_range=[-L/5, L/2, 4],
            y_range=[-t*1, t*3, 4],
            x_length=L*2,
            y_length=t*3,
            axis_config={"include_ticks": False, "include_numbers": False},
            tips=False,
            stroke_width = 0.5            
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
            line = Line(LEFT*L/2, RIGHT*L/2, stroke_width=2).shift(UP*y)
            lines.append(line)

        beam = VGroup(*lines)
        beam.move_to(axes_origin)
        self.add(beam)

        top_line = lines[-1]
        mid_line = lines[len(lines) // 2]
        bottom_line = lines[0]

        beam_block = Polygon(
            top_line.get_start(), top_line.get_end(), bottom_line.get_end(), bottom_line.get_start(),
            color=BLUE, fill_opacity=0.5, stroke_width=2)
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
    
        A1 =bottom_line.get_center() + RIGHT*L*0.6

        b1 = 3
        A2 = A1 + RIGHT*b1

        mid_A1A2 = (A1 + A2) / 2

        mid_B1B2 = mid_A1A2 + UP*t

        b2 = 0.5
        B1 = mid_B1B2 - RIGHT*b2/2
        B2 = mid_B1B2 + RIGHT*b2/2
        
        polygon = [A1, A2, B2, B1]

        cross_section = Polygon(
            *polygon,
            color=BLUE, fill_opacity=0.5, stroke_width=2)
        self.add(cross_section)


        def polygon_centroid(vertices):
            n = len(vertices)
            area = 0.0
            cx = 0.0
            cy = 0.0
            cz = 0.0

            for i in range(n):
                x0, y0, z0 = vertices[i]
                x1, y1, z1 = vertices[(i + 1) % n]  # Connect back to the first vertex
                
                # Shoelace formula component
                cross_product = (x0 * y1) - (x1 * y0)
                area += cross_product
                cx += (x0 + x1) * cross_product
                cy += (y0 + y1) * cross_product

            area *= 0.5
            # The centroid coordinates
            cx = cx / (6.0 * area)
            cy = cy / (6.0 * area)
            
            return cx, cy, cz

        polygon = [A1, A2, B2, B1]
        print(polygon_centroid(polygon))  # Output: (2.0, 2.0)
        centroid = polygon_centroid(polygon)
        self.add(Dot(centroid, color=RED, radius=0.03))

        # centroid line along beam length
        l_end_cl = centroid + LEFT*L/2

        r_end_cl = centroid + RIGHT *L/2

        centroid_abl = Line(l_end_cl, r_end_cl, stroke_width=0.5)
        self.add(centroid_abl)
        
        # neutral axes = centroid axes for symmetrical cross section along y-axes
        # Same centroid height, but spanning the beam length
        neutral_shift = UP * (centroid[1] - top_line.get_center()[1])
        neutral_line = Line(top_line.get_start(), top_line.get_end(), stroke_width=2, color=ORANGE)
        neutral_line.shift(neutral_shift)
        self.add(neutral_line)


        # beam after bending
        def bending_shape(x):
            return rho * (1 - np.cos(x / rho))
        bending_curve = ParametricFunction(
            lambda t: axes.c2p(t, bending_shape(t)),
            t_range=[-L/2, L/2],
            color=GREEN,
            stroke_width=2
        )
        bending_curve.shift(neutral_line.get_center() - axes.c2p(0, 0))
        self.add(bending_curve)