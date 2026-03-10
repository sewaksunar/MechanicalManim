from manim import *

class MechanicalMechanism(Scene):
    def construct(self):
        # Create gears
        gear1 = Circle(radius=1, color=BLUE, stroke_width=2)
        gear1.shift(LEFT * 4)
        
        gear2 = Circle(radius=1, color=BLUE, stroke_width=2)
        gear2.shift(RIGHT * 4)
        
        # Create connecting rod
        rod = Line(gear1.get_right(), gear2.get_left(), color=RED, stroke_width=3)
        
        # Create crank arm
        crank = Line(gear1.get_center(), gear1.get_center() + UP * 1.5, 
                     color=GREEN, stroke_width=3)
        
        # Labels
        label1 = Text("Drive Gear", font_size=24).next_to(gear1, DOWN, buff=0.5)
        label2 = Text("Driven Gear", font_size=24).next_to(gear2, DOWN, buff=0.5)
        title = Text("Mechanical Mechanism", font_size=32).to_edge(UP)
        
        # Add all objects
        self.add(gear1, gear2, rod, crank, label1, label2, title)
        
        # Animate rotation of gears
        self.play(Rotate(gear1, angle=PI, about_point=gear1.get_center()), run_time=2)
        self.play(Rotate(gear2, angle=PI, about_point=gear2.get_center()), run_time=2)
        
        self.wait(1)