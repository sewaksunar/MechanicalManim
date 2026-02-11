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