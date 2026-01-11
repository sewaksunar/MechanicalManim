from manim import *
import numpy as np
import sympy as sp
from sympy.geometry import Point, Line as SpLine, Segment

class pythagorean_theorem(Scene):
    def cad_dimension(self, start, end, label_text, offset_val=0.5, scale=0.7, 
                            arrow_size=0.15, ext_line_extension=0.1):
        """Creates a CAD-style dimension with extension lines, arrows, and text."""
        # Convert to sympy Points for exact geometry
        p1 = Point(float(start[0]), float(start[1]))
        p2 = Point(float(end[0]), float(end[1]))
        
        # Create the main segment
        main_seg = Segment(p1, p2)
        dist = float(main_seg.length)
        
        if dist == 0:
            return VGroup()
        
        # Get perpendicular line at midpoint
        midpoint_sp = main_seg.midpoint
        main_line = SpLine(p1, p2)
        perp_line = main_line.perpendicular_line(midpoint_sp)
        
        # Get direction vector for the perpendicular
        perp_dir = perp_line.direction.unit
        perp_dir_np = np.array([float(perp_dir.x), float(perp_dir.y), 0])
        
        # Determine offset direction based on sign
        if offset_val < 0:
            perp_dir_np = -perp_dir_np
        offset_distance = abs(offset_val)
        
        # Calculate dimension line endpoints by offsetting along perpendicular
        dim_start = start + perp_dir_np * offset_distance
        dim_end = end + perp_dir_np * offset_distance
        
        # Direction along the main line
        direction = end - start
        unit_dir = direction / np.linalg.norm(direction)
        
        # Extension Lines (perpendicular to main line)
        ext_line_1 = Line(
            start - perp_dir_np * 0.1,
            dim_start + perp_dir_np * ext_line_extension,
            color=GRAY, 
            stroke_width=1
        )
        ext_line_2 = Line(
            end - perp_dir_np * 0.1,
            dim_end + perp_dir_np * ext_line_extension,
            color=GRAY,
            stroke_width=1
        )
        
        # Dimension Line (parallel to main line)
        dim_line = Line(dim_start, dim_end, color=GRAY, stroke_width=2)
        
        # Arrows pointing along the dimension line
        arrow_1 = Arrow(
            dim_start + unit_dir * arrow_size,
            dim_start,
            buff=0,
            color=GRAY,
            stroke_width=2,
            max_tip_length_to_length_ratio=1,
            tip_length=arrow_size
        )
        arrow_2 = Arrow(
            dim_end - unit_dir * arrow_size,
            dim_end,
            buff=0,
            color=GRAY,
            stroke_width=2,
            max_tip_length_to_length_ratio=1,
            tip_length=arrow_size
        )
        
        # Dimension Text
        label = MathTex(label_text).scale(scale)
        
        # Calculate angle of the main line
        angle = float(sp.atan2(p2.y - p1.y, p2.x - p1.x))
        
        # Keep text upright
        if PI/2 < angle <= PI or -PI <= angle < -PI/2:
            angle += PI
        
        label.rotate(angle)
        
        # Position text at midpoint of dimension line
        midpoint = (dim_start + dim_end) / 2
        label.move_to(midpoint + perp_dir_np * 0.3)
        
        return VGroup(ext_line_1, ext_line_2, dim_line, arrow_1, arrow_2, label)
    
    def construct(self):
        a, b = 3, 4
        
        # Create points directly with numpy
        C_np = np.array([0, 0, 0])
        A_np = np.array([b, 0, 0])
        B_np = np.array([0, a, 0])
        
        # Create triangle with the points
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
        
        # Create dots
        dotA = Dot(A_np)
        dotB = Dot(B_np)
        dotC = Dot(C_np)
        
        # Group all elements together
        triangle = VGroup(triangle_shape, dotA, labelA, dotB, labelB, dotC, labelC)
        title = Title(f"Pythagoras Theorem")
        self.add(title)

        # Add and animate (don't move to center yet)
        self.add(triangle.move_to(ORIGIN))
        self.play(Create(triangle), run_time=3)
        
        # Create dimensions BEFORE moving to center
        # Get actual vertex positions from the triangle
        vertices = triangle_shape.get_vertices()
        C_actual = vertices[0]
        A_actual = vertices[1]
        B_actual = vertices[2]
        
        c_dim = self.cad_dimension(A_actual, B_actual, "c", offset_val=-0.3)
        a_dim = self.cad_dimension(C_actual, B_actual, "a", offset_val=-0.3)
        b_dim = self.cad_dimension(C_actual, A_actual, "b", offset_val=-0.3)
        
        # Group dimensions with triangle
        full_diagram = VGroup(triangle, c_dim, a_dim, b_dim)
        
        self.play(Create(c_dim), run_time=1)
        self.play(Create(a_dim), run_time=1)
        self.play(Create(b_dim), run_time=1)
        
        # Now move everything to center together
        self.play(full_diagram.animate.move_to(LEFT*3), run_time=1)
        
        # annotation
        anno_c = MathTex(
            r"c \ \text{is the hypotenous}"
        )
        anno_a = MathTex(
            r"a \ \text{is the perpendicular}"
        )
        anno_b = MathTex(
            r"b \ \text{is the base}"
        )

        self.play(AnimationGroup(Indicate(c_dim, scale_factor=1),Indicate(labelC), Write(anno_c.move_to(RIGHT*3))))
        self.play(AnimationGroup(Indicate(a_dim, scale_factor=1),Indicate(labelA), Write(anno_a.next_to(RIGHT*3, DOWN))))
        self.play(AnimationGroup(Indicate(b_dim, scale_factor=1),Indicate(labelB), Write(anno_b.next_to(RIGHT*3, DOWN*3))))

        anno = VGroup(anno_a, anno_b, anno_c)
        self.play(FadeOut(anno))

        equ = MathTex(r"c^2 = a^2 + b^2")
        self.play(Write(equ.move_to(RIGHT*3)))
        
        self.wait(2)

        # hin = Text("नमस्ते! मेरो नाम सेवक हो।", font="sans-serif")
        # self.play(Write(hin))
from manim import *

class InscribedAngleTheoremI(Scene):
    def construct(self):
        # Create trackers for animation
        radius_tracker = ValueTracker(2)
        angle1_tracker = ValueTracker(60)
        angle2_tracker = ValueTracker(120)
        angle3_tracker = ValueTracker(230)
        angle4_tracker = ValueTracker(330)
        
        # Create circle with always_redraw
        c = always_redraw(lambda: Circle(
            radius=radius_tracker.get_value(), 
            color=WHITE
        ).move_to(ORIGIN))
        
        # Create points that update based on trackers
        dot_p1 = always_redraw(lambda: Dot(
            Circle(radius=radius_tracker.get_value()).point_at_angle(angle1_tracker.get_value()*DEGREES),
            color=YELLOW
        ))
        dot_p2 = always_redraw(lambda: Dot(
            Circle(radius=radius_tracker.get_value()).point_at_angle(angle2_tracker.get_value()*DEGREES),
            color=YELLOW
        ))
        dot_p3 = always_redraw(lambda: Dot(
            Circle(radius=radius_tracker.get_value()).point_at_angle(angle3_tracker.get_value()*DEGREES),
            color=YELLOW
        ))
        dot_p4 = always_redraw(lambda: Dot(
            Circle(radius=radius_tracker.get_value()).point_at_angle(angle4_tracker.get_value()*DEGREES),
            color=YELLOW
        ))
        
        # Create lines that update
        line1 = always_redraw(lambda: Line(
            Circle(radius=radius_tracker.get_value()).point_at_angle(angle1_tracker.get_value()*DEGREES),
            Circle(radius=radius_tracker.get_value()).point_at_angle(angle3_tracker.get_value()*DEGREES),
            color=BLUE
        ))
        line2 = always_redraw(lambda: Line(
            Circle(radius=radius_tracker.get_value()).point_at_angle(angle1_tracker.get_value()*DEGREES),
            Circle(radius=radius_tracker.get_value()).point_at_angle(angle4_tracker.get_value()*DEGREES),
            color=BLUE
        ))
        line3 = always_redraw(lambda: Line(
            Circle(radius=radius_tracker.get_value()).point_at_angle(angle2_tracker.get_value()*DEGREES),
            Circle(radius=radius_tracker.get_value()).point_at_angle(angle3_tracker.get_value()*DEGREES),
            color=RED
        ))
        line4 = always_redraw(lambda: Line(
            Circle(radius=radius_tracker.get_value()).point_at_angle(angle2_tracker.get_value()*DEGREES),
            Circle(radius=radius_tracker.get_value()).point_at_angle(angle4_tracker.get_value()*DEGREES),
            color=RED
        ))
        
        # Create arc that updates
        arc = always_redraw(lambda: Arc(
            radius=radius_tracker.get_value(),
            start_angle=angle3_tracker.get_value()*DEGREES,
            angle=(angle4_tracker.get_value() - angle3_tracker.get_value())*DEGREES,
            color=GREEN,
            stroke_width=6
        ))
        
        # Create angles that update
        angle1 = always_redraw(lambda: Angle(
            Line(
                Circle(radius=radius_tracker.get_value()).point_at_angle(angle1_tracker.get_value()*DEGREES),
                Circle(radius=radius_tracker.get_value()).point_at_angle(angle3_tracker.get_value()*DEGREES)
            ),
            Line(
                Circle(radius=radius_tracker.get_value()).point_at_angle(angle1_tracker.get_value()*DEGREES),
                Circle(radius=radius_tracker.get_value()).point_at_angle(angle4_tracker.get_value()*DEGREES)
            ),
            radius=0.5,
            color=YELLOW
        ))
        
        angle2 = always_redraw(lambda: Angle(
            Line(
                Circle(radius=radius_tracker.get_value()).point_at_angle(angle2_tracker.get_value()*DEGREES),
                Circle(radius=radius_tracker.get_value()).point_at_angle(angle3_tracker.get_value()*DEGREES)
            ),
            Line(
                Circle(radius=radius_tracker.get_value()).point_at_angle(angle2_tracker.get_value()*DEGREES),
                Circle(radius=radius_tracker.get_value()).point_at_angle(angle4_tracker.get_value()*DEGREES)
            ),
            radius=0.5,
            color=YELLOW
        ))
        
        # Labels
        label1 = always_redraw(lambda: MathTex(r"\theta_1", color=BLUE).scale(0.7).next_to(
            Circle(radius=radius_tracker.get_value()).point_at_angle(angle1_tracker.get_value()*DEGREES),
            DOWN, buff=0.3
        ))
        label2 = always_redraw(lambda: MathTex(r"\theta_2", color=RED).scale(0.7).next_to(
            Circle(radius=radius_tracker.get_value()).point_at_angle(angle2_tracker.get_value()*DEGREES),
            DOWN, buff=0.3
        ))
        
        # Initial creation
        self.play(Create(c))
        self.wait(0.5)
        
        self.play(
            Create(line1), Create(line2), 
            Create(dot_p1), Create(dot_p3), Create(dot_p4)
        )
        self.wait(0.5)
        
        self.play(Create(line3), Create(line4), Create(dot_p2))
        self.wait(0.5)
        
        self.play(Create(arc))
        self.wait(0.5)
        
        self.play(Create(angle1), Write(label1))
        self.wait(0.3)
        self.play(Create(angle2), Write(label2))
        self.wait(1)
        
        # Add theorem statement
        theorem = VGroup(
            Text("Inscribed Angle Theorem:", font_size=24, color=YELLOW),
            Text("Angles subtending the same arc are equal", font_size=20)
        ).arrange(DOWN, buff=0.2)
        theorem.to_edge(UP, buff=0.5)
        
        self.play(Write(theorem))
        self.wait(1)
        
        # ANIMATE: Move p1 smoothly
        self.play(
            angle1_tracker.animate.set_value(80),
            run_time=2,
            rate_func=smooth
        )
        self.wait(0.5)
        
        self.play(
            angle1_tracker.animate.set_value(45),
            run_time=2,
            rate_func=smooth
        )
        self.wait(0.5)
        
        self.play(
            angle1_tracker.animate.set_value(90),
            run_time=2,
            rate_func=smooth
        )
        self.wait(0.5)
        
        # ANIMATE: Move p2 smoothly
        self.play(
            angle2_tracker.animate.set_value(140),
            run_time=2,
            rate_func=smooth
        )
        self.wait(0.5)
        
        self.play(
            angle2_tracker.animate.set_value(100),
            run_time=2,
            rate_func=smooth
        )
        self.wait(0.5)
        
        # ANIMATE: Change circle radius smoothly
        self.play(
            radius_tracker.animate.set_value(2.5),
            run_time=2,
            rate_func=smooth
        )
        self.wait(0.5)
        
        self.play(
            radius_tracker.animate.set_value(1.5),
            run_time=2,
            rate_func=smooth
        )
        self.wait(0.5)
        
        self.play(
            radius_tracker.animate.set_value(2.8),
            run_time=2,
            rate_func=smooth
        )
        self.wait(0.5)
        
        # ANIMATE: Combine multiple changes
        self.play(
            angle1_tracker.animate.set_value(70),
            angle2_tracker.animate.set_value(115),
            radius_tracker.animate.set_value(2.2),
            run_time=3,
            rate_func=smooth
        )
        self.wait(1)
        
        # Final message
        final_text = Text(
            "The theorem holds for any circle size and vertex position!",
            font_size=20,
            color=GREEN
        ).to_edge(DOWN, buff=0.5)
        
        self.play(Write(final_text))
        self.wait(3)