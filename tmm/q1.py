from manim import *
import numpy as np

class q1(Scene):
    def construct(self):
        # Fixed pivots
        O2 = np.array([-4, -1, 0])
        O4 = np.array([ 3, 2, 0])

        # Link lengths (all explicit)
        L2 = 3.0
        L4 = 4.0
        L4_partial = 3.0   # how far along link4 the coupler attaches
        L5 = 2.0           # length of coupler extension (not used in DOF calc)
        L6 = 1.5           # length of coupler extension (not used in DOF calc)
        # Joint positions
        A = O2 + L2         * np.array([np.cos(np.pi/3),  np.sin(np.pi/3), 0])
        B = O4 + L4         * np.array([-np.cos(np.pi/4), -np.sin(np.pi/4), 0])
        C = O4 + L4_partial * np.array([-np.cos(np.pi/4), -np.sin(np.pi/4), 0])

        D = B + L5 * np.array([np.cos(0), np.sin(0), 0])  # coupler end (not used in DOF calc)
        E = D + L6 * np.array([-np.cos(np.pi*2/3), -np.sin(np.pi*2/3), 0])  # coupler extension end (not used in DOF calc)

        # slider is at E

        L3 = np.linalg.norm(C - A)   # coupler length (derived from geometry)

        # Links
        link2 = Line(O2, A, color=YELLOW, stroke_width=4)
        link4 = Line(O4, B, color=GRAY,   stroke_width=6)
        link3 = Line(A,  C, color=GREEN,  stroke_width=4)
        link5 = Line(B,  D, color=BLUE,   stroke_width=4)
        link6 = Line(D,  E, color=PURPLE, stroke_width=4)

        # Labels (offset slightly so they don't overlap the dot)
        def label(text, point, direction=UP):
            return Text(text, font_size=24, color=WHITE).next_to(
                Dot(point), direction, buff=0.15
            )

        lbl_O2 = label("O2", O2, DOWN+LEFT)
        lbl_O4 = label("O4", O4, DOWN+RIGHT)
        lbl_A  = label("A",  A,  UP+RIGHT)
        lbl_B  = label("B",  B,  DOWN+LEFT)
        lbl_C  = label("C",  C,  UP+LEFT)
        lbl_D  = label("D",  D,  DOWN+RIGHT)
        lbl_E  = label("E",  E,  UP+RIGHT)  # E is not labeled since it's not part of the DOF calc

        # Draw — same order as original, labels appear with their dot
        self.add(Dot(O2, color=RED), lbl_O2)
        self.play(Create(link2))
        self.add(Dot(A, color=RED), lbl_A)

        self.add(Dot(O4, color=RED), lbl_O4)
        self.add(Dot(B,  color=RED), lbl_B)
        self.play(Create(link4))

        self.add(Dot(C, color=RED), lbl_C)
        self.play(Create(link3))

        self.add(Dot(D, color=RED), lbl_D)
        self.play(Create(link5))

        self.add(Dot(E, color=RED), lbl_E)  # E is not labeled since it's not part of the DOF calc
        self.play(Create(link6))

        # slider at E (rectangle centered on the point)
        slider = Rectangle(width=1.0, height=0.3, color=ORANGE)
        slider.move_to(E)
        self.play(Create(slider))

        # support underneath the slider with hashed fill and no boundary
        support = Rectangle(width=3, height=0.1, color=WHITE)
        support.set_stroke(width=0)
        support.set_fill(WHITE, opacity=0.4)
        support.move_to(E + DOWN * 0.2)
        self.play(Create(support))

        # add hashing lines inside the support
        hash_lines = VGroup()
        rows = 3
        for i in range(1, rows):
            y = -support.height/2 + i * (support.height / rows)
            start = support.get_center() + np.array([-support.width/2, y, 0])
            end   = support.get_center() + np.array([ support.width/2, y, 0])
            hash_lines.add(Line(start, end, color=WHITE, stroke_width=1))
        self.play(Create(hash_lines))