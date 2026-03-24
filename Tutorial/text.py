from manim import *

class TextMoving(Scene):
    def construct(self):
        text = Text("Hello World")
        self.add(text)
        self.play(FadeIn(text))
        self.wait()