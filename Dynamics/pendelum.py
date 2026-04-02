from manim import *
import numpy as np

class DampedPendulum(Animation):
    def __init__(self, pendulum, amplitude: float, damping: float = 0.1, frequency: float = 2, **kwargs) -> None:
        super().__init__(pendulum, **kwargs)
        self.amplitude = amplitude  # Max angle in radians
        self.damping = damping      # Damping coefficient (0-1)
        self.frequency = frequency  # Oscillation frequency
        self.previous_angle = 0

    def interpolate_mobject(self, alpha: float) -> None:
        # Damped oscillation: A * e^(-damping*t) * sin(2*pi*frequency*t)
        # where alpha goes from 0 to 1
        t = alpha
        # Calculate damped amplitude
        damped_amplitude = self.amplitude * np.exp(-self.damping * t)
        # Calculate angle with oscillation
        angle = damped_amplitude * np.sin(2 * np.pi * self.frequency * t)
        
        # Calculate rotation delta
        delta_angle = angle - self.previous_angle
        # Rotate the mobject around the origin (pivot point)
        self.mobject.rotate(delta_angle, about_point=ORIGIN)
        # Update previous angle
        self.previous_angle = angle

class Pendulum(Scene):
    def construct(self):
        rod = Line(ORIGIN, 2*DOWN, color=WHITE)
        bob = Circle(radius=0.3, color=RED, fill_opacity=1).move_to(rod.get_end())
        pivot = Circle(radius=0.1, color=BLUE, fill_opacity=1).move_to(rod.get_start())

        pendulum = VGroup(pivot, rod, bob)

        self.play(DampedPendulum(pendulum, amplitude=np.radians(45), damping=2.0, frequency=2, run_time=10))
