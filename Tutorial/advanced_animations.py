from manim import *
import numpy as np

# ============ 1. VALUE TRACKER - Animate changing numbers ============
class ValueTrackerExample(Scene):
    def construct(self):
        # Create a value tracker (hidden variable that animates)
        k = ValueTracker(0)
        
        # Create a circle that grows based on tracker value
        circle = Circle(radius=0, color=BLUE, fill_opacity=0.7)
        circle.add_updater(lambda obj: obj.set(radius=k.get_value()))
        
        # Display the value as text
        text = Text("Radius: ", color=WHITE)
        text_value = DecimalNumber(0, color=YELLOW, num_decimal_places=1)
        text_value.add_updater(lambda obj: obj.set_value(k.get_value()))
        text_group = VGroup(text, text_value).arrange(RIGHT, buff=0.2)
        
        self.add(circle, text_group)
        
        # Animate the value tracker (which updates circle size and text)
        self.play(k.animate.set_value(3), run_time=4)
        self.wait()


# ============ 2. GRAPHING FUNCTIONS ============
class FunctionGraphing(Scene):
    def construct(self):
        # Create coordinate system
        ax = Axes(
            x_range=[-3, 3, 0.5],
            y_range=[-2, 2, 0.5],
            axis_config={"color": GREY_A},
            tips=False,
        )
        
        # Define a function
        def func(x):
            return np.sin(x)
        
        # Create the curve
        curve = ax.plot(func, color=BLUE)
        curve_label = ax.get_graph_label(curve, label="\\sin(x)")
        
        # Draw axes first
        self.play(Create(ax))
        
        # Then draw the curve
        self.play(Create(curve), Write(curve_label), run_time=3)
        
        # Add a point that moves along the curve
        dot = Dot(ax.input_to_graph_point(0, curve), color=RED, radius=0.08)
        
        # Animate the dot along the curve
        def update_dot(d):
            x = curve.get_x_min() + (self.time % 8) / 8 * (curve.get_x_max() - curve.get_x_min())
            d.move_to(ax.input_to_graph_point(x, curve))
        
        self.add(dot)
        self.play(FadeIn(dot))
        self.wait(8)


# ============ 3. MORPHING SHAPES WITH TRANSFORM ============
class MorphingShapes(Scene):
    def construct(self):
        # Create starting shape
        shape1 = Circle(radius=1, color=BLUE, fill_opacity=0.7)
        shape1.shift(LEFT * 3)
        
        # Create target shape
        shape2 = Square(side_length=2, color=GREEN, fill_opacity=0.7)
        shape2.shift(RIGHT * 3)
        
        # Add labels
        label1 = Text("Circle", font_size=24).next_to(shape1, DOWN)
        label2 = Text("Square", font_size=24).next_to(shape2, DOWN)
        
        self.add(shape1, label1, shape2, label2)
        self.wait()
        
        # Transform circle into square (morph animation)
        self.play(Transform(shape1, shape2), run_time=2)
        self.play(shape1.animate.shift(RIGHT * 6), run_time=2)
        self.wait()


# ============ 4. WAVE SIMULATION ============
class WaveSimulation(Scene):
    def construct(self):
        # Create dots in a wave pattern
        num_dots = 20
        dots = VGroup()
        
        for i in range(num_dots):
            dot = Dot(radius=0.1, color=BLUE)
            dot.move_to([i * 0.5 - 4.5, 0, 0])
            dots.add(dot)
        
        self.add(dots)
        
        # Create updater function for wave motion
        def wave_updater(group):
            time = self.time
            for i, dot in enumerate(group):
                original_x = i * 0.5 - 4.5
                # Sine wave: y = sin(x - vt)
                y = 0.5 * np.sin(original_x - time * 2)
                dot.move_to([original_x, y, 0])
        
        dots.add_updater(wave_updater)
        self.wait(5)


# ============ 5. STAGGERED GROUP ANIMATIONS ============
class StaggeredAnimation(Scene):
    def construct(self):
        # Create a group of circles
        circles = VGroup()
        for i in range(5):
            circle = Circle(radius=0.5, color=BLUE, fill_opacity=0.7)
            circle.move_to([i * 1.5 - 3, 0, 0])
            circles.add(circle)
        
        self.add(circles)
        
        # Animate each circle with a delay (stagger effect)
        self.play(
            *[FadeOut(circle) for circle in circles],
            lag_ratio=0.2,  # Delay between each animation
            run_time=3
        )
        
        self.wait()
        
        # Bring them back with stagger
        self.play(
            *[FadeIn(circle) for circle in circles],
            lag_ratio=0.2,
            run_time=3
        )


# ============ 6. ROTATING & SCALING ANIMATION ============
class RotateScale(Scene):
    def construct(self):
        # Create a group of shapes
        group = VGroup()
        
        for i in range(3):
            shape = Square(side_length=0.6, color=BLUE)
            shape.move_to([i * 1.5 - 1.5, 0, 0])
            group.add(shape)
        
        self.add(group)
        
        # Complex animation chain
        self.play(group.animate.rotate(PI/4).scale(1.5), run_time=2)
        self.play(group.animate.rotate(-PI/4).scale(0.7), run_time=2)
        self.play(group.animate.shift(DOWN * 2), run_time=1)
        self.wait()


# ============ 7. PARAMETRIC CURVES ============
class ParametricCurve(Scene):
    def construct(self):
        # Create axes
        ax = Axes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            axis_config={"color": GREY_A},
            tips=False,
        )
        
        # Parametric curve: (cos(t), sin(t)) - a circle
        curve = ax.plot_parametric_curve(
            lambda t: np.array([2*np.cos(t), 2*np.sin(t), 0]),
            t_range=[0, 2*PI],
            color=BLUE
        )
        
        self.play(Create(ax), run_time=1)
        self.play(Create(curve), run_time=3)
        
        # Add spiraling curve
        spiral = ax.plot_parametric_curve(
            lambda t: np.array([t/PI * np.cos(t), t/PI * np.sin(t), 0]),
            t_range=[0, 4*PI],
            color=RED
        )
        
        self.play(Create(spiral), run_time=3)
        self.wait()


# ============ 8. MATHMATICAL ANIMATIONS WITH LATEX ============
class MathAnimations(Scene):
    def construct(self):
        # Create equation
        eq1 = MathTex(r"f(x) = x^2")
        eq1.move_to(UP * 2)
        
        self.play(Write(eq1), run_time=1)
        self.wait()
        
        # Transform equation
        eq2 = MathTex(r"f'(x) = 2x")
        eq2.move_to(UP * 2)
        
        self.play(Transform(eq1, eq2), run_time=2)
        self.wait()
        
        # Brace annotation
        brace = Brace(eq1, UP)
        brace_text = brace.get_text("Derivative")
        
        self.play(Create(brace), Write(brace_text), run_time=1)
        self.wait()


# ============ 9. COMPOSITION - Complex Scene ============
class ComplexComposition(Scene):
    def construct(self):
        # Background
        background = Rectangle(height=8, width=14, color=GREY, fill_opacity=0.1)
        self.add(background)
        
        # Title
        title = Text("Advanced Manim Animation", font_size=40).to_edge(UP)
        self.play(Write(title), run_time=2)
        
        # Create multiple animated elements
        circle = Circle(radius=0.5, color=BLUE, fill_opacity=0.7).shift(LEFT * 3 + DOWN)
        square = Square(side_length=1, color=GREEN, fill_opacity=0.7).shift(RIGHT * 3 + DOWN)
        
        self.play(FadeIn(circle), FadeIn(square), run_time=1)
        
        # Animate both simultaneously
        self.play(
            circle.animate.move_to([0, 0, 0]).scale(2),
            square.animate.move_to([0, 0, 0]).rotate(PI/4),
            run_time=2
        )
        
        # Add text label with value tracking
        k = ValueTracker(0)
        text = DecimalNumber(0, num_decimal_places=2)
        text.add_updater(lambda obj: obj.set_value(k.get_value()).next_to(circle, UP))
        
        self.add(text)
        self.play(k.animate.set_value(100), run_time=3)
        
        self.wait()


# ============ 10. RANDOM ANIMATION ============
class RandomWalker(Scene):
    def construct(self):
        # Create a dot
        dot = Dot(color=BLUE, radius=0.1)
        path = VMobject(stroke_color=GREEN, stroke_width=2)
        
        # Initialize path at starting position
        current_pos = np.array([0, 0, 0])
        path.set_points_as_corners([current_pos])
        
        self.add(dot, path)
        
        # Random walk animation
        for i in range(50):
            # Random direction
            angle = np.random.random() * 2 * PI
            step = np.array([0.3 * np.cos(angle), 0.3 * np.sin(angle), 0])
            new_pos = current_pos + step
            
            # Clamp to screen
            new_pos[0] = np.clip(new_pos[0], -6, 6)
            new_pos[1] = np.clip(new_pos[1], -3.5, 3.5)
            
            # Add to path
            path.add_line_to(new_pos)
            
            # Animate dot
            self.play(dot.animate.move_to(new_pos), run_time=0.1)
            
            current_pos = new_pos
        
        self.wait()
