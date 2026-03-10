from manim import *
import numpy as np

class Curve(ParametricFunction):
    def __init__(self, func, t_range=(0, 1), **kwargs):
        super().__init__(
            lambda t: np.array(func(t)),
            t_range=t_range,
            **kwargs
    )
    
class Cuve(Scene):
    def construct(self):
        axes = Axes(x_range=(0, 1, 0.2), y_range=(-1, 1, 0.5))
        self.play(Create(axes))
        curve = Curve(lambda t: [t, np.sin(2 * np.pi * t), 0], color=RED)
        self.play(Create(curve))
        self.wait()