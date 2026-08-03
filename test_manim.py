from manim import *

class Test(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
        self.wait()
