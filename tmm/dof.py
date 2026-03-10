from manim import *
import numpy as np

class FourBarLinkage(Scene):
    def construct(self):
        title = Text("Four-Bar Linkage", font_size=48, color=BLUE)
        self.play(Write(title))
        self.wait(0.5)
        self.play(title.animate.to_edge(UP))
        
        O2 = np.array([-3, -1.5, 0])
        O4 = np.array([3, -1.5, 0])
        
        B = np.array([-0.5, 1, 0])
        
        p1 = Circle(radius=0.15, color=RED).move_to(O2)
        p2 = Circle(radius=0.15, color=RED).move_to(O4)
        p3 = Circle(radius=0.15, color=RED).move_to(B)
        
        link2 = Line(O2, B, color=YELLOW, stroke_width=4)
        link3 = Line(B, O4, color=GREEN, stroke_width=4)
        link4 = Line(O4, O2, color=PURPLE, stroke_width=4)
        link1 = Line(np.array([-4, -1.5, 0]), np.array([4, -1.5, 0]), color=GRAY, stroke_width=6)
        
        O2_label = Text("O₂(Fixed)", font_size=20).next_to(p1, DOWN)
        O4_label = Text("O₄(Fixed)", font_size=20).next_to(p2, DOWN)
        B_label = Text("B", font_size=20).next_to(p3, UP)
        
        self.play(Create(link1), Create(link4))
        self.play(Create(link2), Create(link3))
        self.play(Create(p1), Create(p2), Create(p3))
        self.play(Write(O2_label), Write(O4_label), Write(B_label))
        self.wait(1)
        
        self.play(p3.animate.move_to([-1.5, 0.5, 0]))
        self.wait(0.5)
        self.play(p3.animate.move_to([0.5, 1, 0]))
        self.wait(0.5)
        
        self.play(FadeOut(O2_label), FadeOut(O4_label), FadeOut(B_label))
        
        dof_group = VGroup(link1, link2, link3, link4, p1, p2, p3, title)
        self.play(dof_group.animate.scale(0.6).to_edge(LEFT))
        
        calc_title = Text("DOF Calculation", font_size=40, color=BLUE)
        calc_title.next_to(dof_group, RIGHT, buff=0.5)
        self.play(Write(calc_title))
        self.wait(0.5)
        
        formula = Text("Kutzbach-Gruebler Formula:", font_size=24, color=WHITE)
        formula.next_to(calc_title, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(Write(formula))
        
        eq1 = Text("DOF = 3(n-1) - 2j - h", font_size=28, color=YELLOW)
        eq1.next_to(formula, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(eq1))
        
        where = Text("n = number of links\nj = lower pair joints\nh = higher pair joints", 
                     font_size=20, color=WHITE)
        where.next_to(eq1, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(where))
        
        values = Text("n = 4 (links)\nj = 4 (pin joints)\nh = 0 (no higher pairs)", 
                      font_size=22, color=GREEN)
        values.next_to(where, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(values))
        
        calculation = Text("DOF = 3(4-1) - 2(4) - 0\nDOF = 9 - 8 - 0\nDOF = 1", 
                          font_size=26, color=RED)
        calculation.next_to(values, DOWN, buff=0.4, aligned_edge=LEFT)
        self.play(Write(calculation))
        
        result = Text("✓ One degree of freedom", font_size=28, color=GOLD).next_to(calculation, DOWN, buff=0.5)
        self.play(Write(result))
        
        self.wait(3)


class SliderCrank(Scene):
    def construct(self):
        title = Text("Slider-Crank Mechanism", font_size=48, color=BLUE)
        self.play(Write(title))
        self.wait(0.5)
        self.play(title.animate.to_edge(UP))
        
        O2 = np.array([-2, 0, 0])
        slider_y = 0
        
        B = np.array([1, 1.5, 0])
        C = np.array([3.5, slider_y, 0])
        
        p1 = Circle(radius=0.15, color=RED).move_to(O2)
        p2 = Circle(radius=0.15, color=RED).move_to(B)
        p3 = Circle(radius=0.15, color=RED).move_to(C)
        
        link1 = Line(np.array([-3.5, 0, 0]), np.array([4, 0, 0]), color=GRAY, stroke_width=6)
        crank = Line(O2, B, color=YELLOW, stroke_width=4)
        rod = Line(B, C, color=GREEN, stroke_width=4)
        
        O2_label = Text("O₂(Fixed)", font_size=18).next_to(p1, DOWN)
        C_label = Text("C(Slider)", font_size=18).next_to(p3, DOWN)
        
        self.play(Create(link1), Create(crank), Create(rod))
        self.play(Create(p1), Create(p2), Create(p3))
        self.play(Write(O2_label), Write(C_label))
        self.wait(1)
        
        angle = 0
        crank_len = np.linalg.norm(B - O2)
        for i in range(12):
            angle += np.pi / 6
            B_new = O2 + crank_len * np.array([np.cos(angle), np.sin(angle), 0])
            rod_len = np.linalg.norm(C - B)
            BC_dist = np.sqrt(rod_len**2 - (B_new[1])**2)
            C_new = np.array([O2[0] + BC_dist, slider_y, 0])
            
            self.play(
                crank.animate.put_start_and_end_on(O2, B_new),
                rod.animate.put_start_and_end_on(B_new, C_new),
                p2.animate.move_to(B_new),
                p3.animate.move_to(C_new),
                run_time=0.3
            )
        
        self.play(FadeOut(O2_label), FadeOut(C_label))
        
        mech_group = VGroup(link1, crank, rod, p1, p2, p3, title)
        self.play(mech_group.animate.scale(0.6).to_edge(LEFT))
        
        calc_title = Text("DOF Calculation", font_size=40, color=BLUE)
        calc_title.next_to(mech_group, RIGHT, buff=0.5)
        self.play(Write(calc_title))
        self.wait(0.5)
        
        formula = Text("Kutzbach-Gruebler Formula:", font_size=24, color=WHITE)
        formula.next_to(calc_title, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(Write(formula))
        
        eq1 = Text("DOF = 3(n-1) - 2j - h", font_size=28, color=YELLOW)
        eq1.next_to(formula, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(eq1))
        
        values = Text("n = 4 (links)\nj = 4 (pin + slider joints)\nh = 0", 
                      font_size=22, color=GREEN)
        values.next_to(eq1, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(values))
        
        calculation = Text("DOF = 3(4-1) - 2(4) - 0\nDOF = 9 - 8 - 0\nDOF = 1", 
                          font_size=26, color=RED)
        calculation.next_to(values, DOWN, buff=0.4, aligned_edge=LEFT)
        self.play(Write(calculation))
        
        result = Text("✓ One degree of freedom", font_size=28, color=GOLD).next_to(calculation, DOWN, buff=0.5)
        self.play(Write(result))
        
        self.wait(3)