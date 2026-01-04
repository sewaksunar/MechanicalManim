from manim import *
import numpy as np
import sympy as sp
import sympy.geometry as geom

class pythagorean_theorem(Scene):
    def construct(self):
        a, b = 3, 4
        xt = 0
        yt = 0
        
        # Create points using sympy geometry
        C = geom.Point(xt, yt, 0)
        A = geom.Point(C.x + b, C.y, 0)
        CA = geom.Line(C, A)
        
        # Create a perpendicular line at C
        perpendicular_line = CA.perpendicular_line(C)
        
        # Get point B at distance 'a' along the perpendicular
        direction_vector = perpendicular_line.direction.unit
        B = C - a * direction_vector
        
        # Convert to numpy arrays
        C_np = np.array([float(C.x), float(C.y), 0])
        A_np = np.array([float(A.x), float(A.y), 0])
        B_np = np.array([float(B.x), float(B.y), 0])
        
        # Create triangle with the converted points
        triangle_shape = Polygon(
            C_np,
            A_np,
            B_np,
            color=BLUE
        )
        
        # Create labels
        labelC = MathTex("C")
        labelC.next_to(C_np, DOWN+LEFT)
        labelA = MathTex("A")
        labelA.next_to(A_np, DOWN+RIGHT)
        labelB = MathTex("B")
        labelB.next_to(B_np, UP+LEFT)
        
        # Group all elements together
        triangle = VGroup(triangle_shape, Dot(A_np), labelA, Dot(B_np), labelB, Dot(C_np), labelC)
        
        # Move to center
        triangle.move_to(ORIGIN)
        
        # Add elements to scene
        self.add(triangle)
        self.play(Create(triangle, run_time=10))
        l1 = Line(RIGHT)
        self.play(MoveAlongPath(triangle, l1))
