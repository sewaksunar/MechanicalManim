## SYMMETRIC MEMBERS IN PURE BENDING
from manim import *

class BeamBending(Animation):
    def __init__(self, beam, neutral_line, rho, L, **kwargs):
        super().__init__(beam, **kwargs)
        self.rho = rho
        self.L = L
        # Snapshot everything BEFORE animation mutates anything
        self.neutral_center = neutral_line.get_center().copy()
        self.fiber_data = [
            {
                "y_offset": line.get_center()[1] - neutral_line.get_center()[1],
                "color":    line.get_color(),
                "sw":       line.get_stroke_width(),
            }
            for line in beam
        ]

    def interpolate_mobject(self, alpha):
        circle_center = self.neutral_center + UP * self.rho
        theta_total   = self.L / self.rho
        span          = max(theta_total * alpha, 1e-9)   # avoid zero-range crash
        t_range       = [-span / 2, span / 2]

        bent = VGroup()
        for fd in self.fiber_data:
            y   = fd["y_offset"]          # signed distance from neutral axis
            r   = self.rho - y            # radius for this fiber
            curve = ParametricFunction(
                lambda t, r=r: (           # r=r fixes the closure capture
                    circle_center
                    + RIGHT * r * np.sin(t)
                    - UP    * r * np.cos(t)
                ),
                t_range=t_range,
                color=fd["color"],
                stroke_width=fd["sw"],
            )
            bent.add(curve)

        self.mobject.become(bent)

class PureBending(Scene):
    def construct(self):
        L = 6  # Length of the beam
        t = 2 # Thickness of the beam
        
        axes_origin = DOWN*t*1 + LEFT*L*0.5

        axes = Axes(
            x_range=[-L/5, L/2, 4],
            y_range=[-t*1.3, t*4, 4],
            x_length=L*2,
            y_length=t*3.5,
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

        # Inverted-T cross section (flange at bottom, web above)
        section_center = bottom_line.get_center() + RIGHT * L *1
        flange_width = 3.0
        flange_thickness = 0.8
        web_width = 1
        web_height = t - flange_thickness

        x0, y0, _ = section_center
        polygon = [
            np.array([x0 - flange_width / 2, y0, 0]),
            np.array([x0 + flange_width / 2, y0, 0]),
            np.array([x0 + flange_width / 2, y0 + flange_thickness, 0]),
            np.array([x0 + web_width / 2, y0 + flange_thickness, 0]),
            np.array([x0 + web_width / 2, y0 + flange_thickness + web_height, 0]),
            np.array([x0 - web_width / 2, y0 + flange_thickness + web_height, 0]),
            np.array([x0 - web_width / 2, y0 + flange_thickness, 0]),
            np.array([x0 - flange_width / 2, y0 + flange_thickness, 0]),
        ]

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

        def moment_of_inertia(vertices):
            n = len(vertices)
            area = 0.0
            Ixx = 0.0
            Iyy = 0.0
            for i in range(n):
                x0, y0, z0 = vertices[i]
                x1, y1, z1 = vertices[(i + 1) % n]  # Connect back to the first vertex
                
                # Shoelace formula component
                cross_product = (x0 * y1) - (x1 * y0)
                area += cross_product
                Ixx += (y0**2 + y0*y1 + y1**2) * cross_product
                Iyy += (x0**2 + x0*x1 + x1**2) * cross_product
            area *= 0.5
            Ixx *= 0.5
            Iyy *= 0.5
            return area, Ixx, Iyy
        
        print(moment_of_inertia(polygon)[1])  # Ixx
        I = moment_of_inertia(polygon)[1]
        E = 0.4
        M = 10
        rho = (E * I) / M
        # rho = 4
        # beam after bending
        theta_total = L / rho
        circle_center = neutral_line.get_center() + UP * rho
        neutral_line_bending = ParametricFunction(
            lambda theta: circle_center + RIGHT * rho * np.sin(theta) - UP * rho * np.cos(theta),
            t_range=[-theta_total / 2, theta_total / 2],
            color=ORANGE,
            stroke_width=2
        )


        neutral_line_center_circle = np.array(neutral_line.get_center())
        neutral_line_center_circle += np.array([0, rho, 0])
        self.add(Dot(neutral_line_center_circle, color=RED, radius=0.05))

        self.add(Dot(neutral_line_bending.get_start(), color=RED, radius=0.05))
        self.add(Dot(neutral_line_bending.get_end(), color=RED, radius=0.05))


        # top_line_bending
        top_line_bending = ParametricFunction(
            lambda theta: circle_center + RIGHT * (rho-t/2) * np.sin(theta) - UP * (rho-t/2) * np.cos(theta),
            t_range=[-theta_total / 2, theta_total / 2],
            color=ORANGE,
            stroke_width=2
        )
        self.add(top_line_bending)

        # bottom_line_bending
        bottom_line_bending = ParametricFunction(
            lambda theta: circle_center + RIGHT * (rho+t/2) * np.sin(theta) - UP * (rho+t/2) * np.cos(theta),
            t_range=[-theta_total / 2, theta_total / 2],
            color=ORANGE,
            stroke_width=2
        )
        self.add(bottom_line_bending)

        r_rho_line = Line(bottom_line_bending.get_start(), neutral_line_center_circle, stroke_width=0.5, color=YELLOW)
        self.add(r_rho_line)

        l_rho_line = Line(bottom_line_bending.get_end(), neutral_line_center_circle, stroke_width=0.5, color=YELLOW)
        self.add(l_rho_line)

        num_samples = 20
        theta_samples = np.linspace(-theta_total / 2, theta_total / 2, num_samples)
        top_points = [
            circle_center + RIGHT * (rho - t / 2) * np.sin(theta) - UP * (rho - t / 2) * np.cos(theta)
            for theta in theta_samples
        ]
        bottom_points = [
            circle_center + RIGHT * (rho + t / 2) * np.sin(theta) - UP * (rho + t / 2) * np.cos(theta)
            for theta in theta_samples[::-1]
        ]
        d_cross_section = Polygon(
            *(top_points + bottom_points),
            color=BLUE,
            fill_opacity=0.5,
            stroke_width=2,
        )
        self.add(d_cross_section)

        self.play(
            BeamBending(beam, neutral_line, rho, L),
            Transform(neutral_line, neutral_line_bending),
            run_time=5,
        )