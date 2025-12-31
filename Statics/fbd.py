from manim import *
import numpy as np
# import sympy as sp

class FreeBodyDiagram(Scene):
    def construct(self):
        block = Square(side_length=2, fill_color=BLUE, fill_opacity=1)
        self.add(block)
        self.play(Create(block))
        self.play(block.animate.set_fill(RED, opacity=1))
        self.wait(5)


class ShearNormalForceElement(Scene):
    """
    Creates a professional beam element showing internal shear force (V) and normal force (N)
    with proper mechanical engineering conventions and accurate design.
    """
    def construct(self):
        # Configure camera and background for professional appearance
        self.camera.background_color = WHITE
        
        # ===== CREATE BEAM ELEMENT =====
        # Main beam element with professional coloring
        beam = Rectangle(width=2.5, height=1.2, fill_color="#E8F4F8", 
                        fill_opacity=1, stroke_width=2.5, stroke_color=BLACK)
        beam.shift(DOWN * 0.3)
        
        # Add hatching lines to indicate a section cut (left side)
        hatch_left = VGroup()
        for i in range(4):
            hatch = Line(start=beam.get_left() + UP * (0.6 - i * 0.35),
                        end=beam.get_left() + LEFT * 0.15 + UP * (0.6 - i * 0.35),
                        stroke_width=1.5, color=BLACK)
            hatch_left.add(hatch)
        
        # Add hatching lines to indicate a section cut (right side)
        hatch_right = VGroup()
        for i in range(4):
            hatch = Line(start=beam.get_right() + UP * (0.6 - i * 0.35),
                        end=beam.get_right() + RIGHT * 0.15 + UP * (0.6 - i * 0.35),
                        stroke_width=1.5, color=BLACK)
            hatch_right.add(hatch)
        
        # ===== LEFT SIDE FORCES =====
        # Normal Force (N) - pointing left (compression)
        normal_left = Arrow(start=beam.get_left() + UP * 0.35, 
                           end=beam.get_left() + LEFT * 1.3 + UP * 0.35,
                           buff=0, stroke_width=3.5, color="#C41E3A", 
                           tip_length=0.25, max_tip_length_to_length_ratio=0.15)
        normal_left_label = MathTex("N", font_size=36, color="#C41E3A").next_to(normal_left, UP, buff=0.25)
        
        # Shear Force (V) - pointing down (positive shear convention)
        shear_left = Arrow(start=beam.get_left() + DOWN * 0.35,
                          end=beam.get_left() + DOWN * 1.15 + DOWN * 0.35,
                          buff=0, stroke_width=3.5, color="#0066CC",
                          tip_length=0.25, max_tip_length_to_length_ratio=0.15)
        shear_left_label = MathTex("V", font_size=36, color="#0066CC").next_to(shear_left, LEFT, buff=0.3)
        
        # ===== RIGHT SIDE FORCES =====
        # Normal Force (N) - pointing right (equal and opposite)
        normal_right = Arrow(start=beam.get_right() + UP * 0.35,
                            end=beam.get_right() + RIGHT * 1.3 + UP * 0.35,
                            buff=0, stroke_width=3.5, color="#C41E3A",
                            tip_length=0.25, max_tip_length_to_length_ratio=0.15)
        normal_right_label = MathTex("N", font_size=36, color="#C41E3A").next_to(normal_right, UP, buff=0.25)
        
        # Shear Force (V) - pointing up (equal and opposite)
        shear_right = Arrow(start=beam.get_right() + DOWN * 0.35,
                           end=beam.get_right() + UP * 1.15 + DOWN * 0.35,
                           buff=0, stroke_width=3.5, color="#0066CC",
                           tip_length=0.25, max_tip_length_to_length_ratio=0.15)
        shear_right_label = MathTex("V", font_size=36, color="#0066CC").next_to(shear_right, RIGHT, buff=0.3)
        
        # ===== BENDING MOMENT INDICATORS =====
        # Moment indicators (curved arrows showing moment direction convention)
        moment_left_arc = ArcBetweenPoints(
            beam.get_left() + LEFT * 0.5 + UP * 0.7,
            beam.get_left() + LEFT * 0.5 + DOWN * 0.7,
            angle=PI/2, stroke_width=2, color="#8B4513"
        )
        moment_left_label = MathTex("M", font_size=32, color="#8B4513").next_to(moment_left_arc, LEFT, buff=0.15)
        
        moment_right_arc = ArcBetweenPoints(
            beam.get_right() + RIGHT * 0.5 + DOWN * 0.7,
            beam.get_right() + RIGHT * 0.5 + UP * 0.7,
            angle=PI/2, stroke_width=2, color="#8B4513"
        )
        moment_right_label = MathTex("M", font_size=32, color="#8B4513").next_to(moment_right_arc, RIGHT, buff=0.15)
        
        # ===== TITLE =====
        title = Tex(r"\textbf{Internal Forces at Section Cut}", font_size=40, color=BLACK)
        title.to_edge(UP, buff=0.4)
        
        # ===== LEGEND AND SIGN CONVENTION =====
        # Create professional legend box
        legend_bg = Rectangle(width=5.2, height=3.2, fill_color="#F5F5F5", 
                             fill_opacity=0.95, stroke_width=1.5, stroke_color="#333333")
        
        legend_title = Tex(r"\textbf{Sign Convention \& Definitions:}", font_size=22, color=BLACK)
        
        # Legend items with proper formatting
        legend_items = VGroup(
            VGroup(
                MathTex("N", color="#C41E3A", font_size=26),
                Tex("= Normal Force (axial stress)", font_size=18, color=BLACK),
            ).arrange(RIGHT, buff=0.4),
            VGroup(
                MathTex("V", color="#0066CC", font_size=26),
                Tex("= Shear Force (transverse stress)", font_size=18, color=BLACK),
            ).arrange(RIGHT, buff=0.4),
            VGroup(
                MathTex("M", color="#8B4513", font_size=26),
                Tex("= Bending Moment (internal moment)", font_size=18, color=BLACK),
            ).arrange(RIGHT, buff=0.4),
        ).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        
        # Combine legend components
        legend = VGroup(legend_title, legend_items).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        legend.scale(0.95)
        legend.shift([0.05, 0.05, 0])  # Slight offset for padding
        
        legend_bg.match_height(legend, stretch=True).scale(1.08, about_point=legend.get_center())
        legend_bg.match_width(legend, stretch=True).scale(1.08, about_point=legend.get_center())
        legend_bg.shift(legend.get_center() - legend_bg.get_center())
        
        legend_group = VGroup(legend_bg, legend)
        legend_group.to_corner(DR, buff=0.35)
        
        # ===== ANIMATION SEQUENCE =====
        # Add title
        self.add(title)
        self.wait(0.8)
        
        # Create beam with hatching to show section cut
        self.play(Create(beam), Create(hatch_left), Create(hatch_right), run_time=1.5)
        self.wait(0.7)
        
        # Add left side forces with sequential timing for clarity
        self.play(Create(normal_left), run_time=0.9)
        self.play(Write(normal_left_label), run_time=0.5)
        self.wait(0.4)
        self.play(Create(shear_left), run_time=0.9)
        self.play(Write(shear_left_label), run_time=0.5)
        self.wait(0.6)
        
        # Add right side forces (equal and opposite for equilibrium)
        self.play(Create(normal_right), run_time=0.9)
        self.play(Write(normal_right_label), run_time=0.5)
        self.wait(0.4)
        self.play(Create(shear_right), run_time=0.9)
        self.play(Write(shear_right_label), run_time=0.5)
        self.wait(0.6)
        
        # Add moment indicators last
        self.play(Create(moment_left_arc), Create(moment_right_arc), run_time=1)
        self.play(Write(moment_left_label), Write(moment_right_label), run_time=0.6)
        self.wait(0.8)
        
        # Add legend with fade in
        self.play(FadeIn(legend_group), run_time=1.2)
        self.wait(3)