from manim import *
import numpy as np

class SigmaVsTheta(Scene):
    def construct(self):
        # Parameters
        sigma_x = 10
        sigma_y = 2
        tau_xy = 4
        
        # Theta values (0 to 2pi)
        n_points = 400
        theta = np.linspace(0, 2 * np.pi, n_points)
        sigma_xx_prime = sigma_x * np.cos(theta) ** 2 + sigma_y * np.sin(theta) ** 2 + 2 * tau_xy * np.sin(theta) * np.cos(theta)
        
        # Axes
        axes = Axes(
            x_range=[0, 360, 45],
            y_range=[min(sigma_xx_prime)-1, max(sigma_xx_prime)+1, 2],
            x_length=8,
            y_length=4,
            axis_config={"include_tip": False},
            x_axis_config={"numbers_to_include": [0, 90, 180, 270, 360]},
        )
        axes.to_edge(DOWN)
        x_label = axes.get_x_axis_label(r"\theta\ (deg)")
        y_label = axes.get_y_axis_label(r"\sigma_{xx}'")
        self.play(Create(axes), Write(x_label), Write(y_label))
        
        # Convert theta to degrees for plotting
        theta_deg = np.degrees(theta)
        # Create graph points
        graph = axes.plot_line_graph(
            x_values=theta_deg,
            y_values=sigma_xx_prime,
            add_vertex_dots=False,
            line_color=YELLOW
        )
        self.play(Create(graph))
        self.wait(2)
