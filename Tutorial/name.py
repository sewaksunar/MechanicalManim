from manim import *

class Letters(Animation):
    def __init__(self, letters, **kwargs):
    # Pass number as the mobject of the animation
        mobject = VGroup(*letters)
        super().__init__(mobject, **kwargs)
        self.letters = letters

    def interpolate_mobject(self, alpha):
        # Calculate which letter and its progress
        num_letters = len(self.letters)
        letter_duration = 1.0 / num_letters
        
        # Reset all letters to invisible
        for letter in self.letters:
            letter.set_opacity(0)
        
        # Find which letter(s) to show
        for i, letter in enumerate(self.letters):
            # Time window for this letter: from i*letter_duration to (i+1)*letter_duration
            letter_start = i * letter_duration
            letter_end = (i + 1) * letter_duration
            
            if letter_start <= alpha <= letter_end:
                # This letter's turn
                local_progress = (alpha - letter_start) / letter_duration
                
                if i == num_letters - 1:
                    # Last letter: fade in and stay
                    opacity = min(local_progress * 2, 1.0)
                else:
                    # Other letters: fade in then out
                    if local_progress < 0.5:
                        opacity = local_progress * 2  # Fade in
                    else:
                        opacity = (1 - local_progress) * 2  # Fade out
                
                letter.set_opacity(opacity).align_to(letter.get_center())
                break

class Name(Scene):
    def construct(self):
        # Create a list of letters
        letters = [Text(letter) for letter in "Sewak Sunar"]
        # Arrange them horizontally in a group
        letters_group = VGroup(*letters).arrange(RIGHT, buff=0.2)
        # Extract the arranged letters from the group
        letters = list(letters_group)

        self.play(Letters(letters), run_time=2)
        self.wait(2)     

# deflection of cantilever beam animation
class Beam(Animation):
    def __init__(self, mobject, E, I, P, L, **kwargs):
        super().__init__(mobject, **kwargs)
        self.E = E  # Young's modulus 
        self.I = I  # Moment of inertia 
        self.P = P  # Load at the free end
        self.L = L  # Length of the beam
        self.lines = list(mobject.submobjects) if len(mobject.submobjects) > 0 else [mobject]
        # Store original endpoints of each line
        self.original_lines = []
        for line in self.lines:
            self.original_lines.append({
                'start': line.get_start().copy(),
                'end': line.get_end().copy(),
            })
            # print(line.get_start(), line.get_end())

        starts = np.array([item['start'] for item in self.original_lines])
        ends = np.array([item['end'] for item in self.original_lines])
        self.center_start = np.mean(starts, axis=0)
        self.center_end = np.mean(ends, axis=0)
        center_vec = self.center_end - self.center_start
        self.span_len = np.linalg.norm(center_vec)
        if self.span_len == 0:
            self.tangent0 = np.array([1.0, 0.0, 0.0])
            self.normal0 = np.array([0.0, 1.0, 0.0])
        else:
            self.tangent0 = center_vec / self.span_len
            self.normal0 = np.array([-self.tangent0[1], self.tangent0[0], 0.0])
            normal_len = np.linalg.norm(self.normal0)
            if normal_len == 0:
                self.normal0 = np.array([0.0, 1.0, 0.0])
            else:
                self.normal0 /= normal_len

        self.line_offsets = []
        for item in self.original_lines:
            start_offset = np.dot(item['start'] - self.center_start, self.normal0)
            end_offset = np.dot(item['end'] - self.center_end, self.normal0)
            self.line_offsets.append(0.5 * (start_offset + end_offset))
        
    def interpolate_mobject(self, alpha):
        # deflection at x point from fixed end
        # y = - (P * x^2) / (6 * E * I) * (3L - x)
        # Fixed end is at x=0 (left/start), free end is at x=L (right/end)

        if self.span_len == 0:
            return

        k = self.P / (6.0 * self.E * self.I)
        num_points = 80
        x_targets = np.linspace(0.0, self.span_len, num_points)

        for i, line in enumerate(self.lines):
            d = self.line_offsets[i]
            points = []

            for x in x_targets:
                # Use xi measured from the fixed end (left side in this scene).
                xi = x
                y_deflection = -(k * xi**2) * (3.0 * self.span_len - xi) * alpha
                slope = -(3.0 * k * xi) * (2.0 * self.span_len - xi) * alpha

                center_pt = self.center_start + self.tangent0 * x + self.normal0 * y_deflection

                denom = np.sqrt(1.0 + slope**2)
                normal_now = (-slope * self.tangent0 + self.normal0) / denom
                points.append(center_pt + d * normal_now)

            line.set_points_as_corners(points)
        
class BeamScene(Scene):
    def construct(self):
        L = 4  # Length of the beam
        t = 0.5  # Thickness of the beam
        
        # Create multiple lines bundled together to form a thick beam
        lines = []
        for y in np.linspace(-t/2, t/2, 30):
            line = Line(ORIGIN, RIGHT * L).shift(UP * y).set_color(ORANGE).set_opacity(1).set_stroke(width=2)
            lines.append(line)
        
        # Group all lines together
        beam = VGroup(*lines)

        beam.move_to(ORIGIN)

        ref_line = lines[len(lines) // 2]
        top_line = lines[-1]
        fixed_end = ref_line.get_start()
        free_end = ref_line.get_end()

        wall = Rectangle(width=0.22, height=1.4, stroke_width=2).set_fill(BLUE_E, opacity=0.5)

        desired_origin = np.array([fixed_end[0], ref_line.get_center()[1], 0.0])

        axes = Axes(
            x_range=[0, L*1.5, 1],
            y_range=[-t*3, t*3, 1],
            x_length=L*1.5,
            y_length=t*8,
            axis_config={"include_ticks": False, "include_numbers": False}            
        )

        axes.shift(desired_origin - axes.c2p(0, 0))
        wall.align_to(axes.c2p(0, 0), RIGHT)
        wall.set_y(axes.c2p(0, 0)[1])

        y_label = axes.get_y_axis_label(
            Tex("$y$").scale(0.65),
            edge=UP,
            direction=UP,
            buff=0.1,
        )
        x_label = axes.get_x_axis_label(
            Tex("$x$").scale(0.65),
            edge=RIGHT,
            direction=RIGHT,
            buff=0.1,
        )
        

        # Keep the wall pinned to the y-axis, and move beam so its fixed end touches the wall.
        beam_shift_x = wall.get_right()[0] - fixed_end[0]
        beam.shift(RIGHT * beam_shift_x)
        beam.shift(UP * (axes.c2p(0, 0)[1] - ref_line.get_center()[1]))
        fixed_end = ref_line.get_start()
        free_end = ref_line.get_end()

        load_arrow = always_redraw(
            lambda: Arrow(
                top_line.get_end() + UP * 0.9,
                top_line.get_end(),
                buff=0,
                stroke_width=4,
                color=RED,
            )
        )
        p_label = always_redraw(
            lambda: MathTex("P", color=RED).scale(0.7).next_to(load_arrow, RIGHT, buff=0.08)
        )

        sec_pt = fixed_end + RIGHT * (0.35 * L)
        section_line = DashedLine(sec_pt + UP * 0.8, sec_pt + DOWN * 0.8, dash_length=0.08, color=GRAY_B)
        x_top_label = MathTex("X").scale(0.55).next_to(section_line, UP, buff=0.04)
        x_bottom_label = MathTex("X").scale(0.55).next_to(section_line, DOWN, buff=0.04)

        x_dim = DoubleArrow(
            fixed_end + DOWN * 0.7,
            sec_pt + DOWN * 0.7,
            buff=0,
            stroke_width=1.6,
            tip_length=0.08,
        )
        x_dim_label = MathTex("x").scale(0.6).next_to(x_dim, DOWN, buff=0.07)

        # Dimension for the full length L
        end_free_pt = fixed_end + RIGHT *  L
        dim_extension_line_free_end = DashedLine(end_free_pt + UP * t/2, end_free_pt + DOWN * 2, dash_length=0.08, color=GRAY_B)

        l_dim = DoubleArrow(
            fixed_end + DOWN*1.8,
            free_end + DOWN*1.8,
            buff=0,
            stroke_width=1.6,
            tip_length=0.08,
        )
        l_dim_label = MathTex("L").scale(0.7).next_to(l_dim, DOWN, buff=0.06)

        self.add(wall, beam, x_label, y_label, axes, section_line, dim_extension_line_free_end, x_top_label, x_bottom_label, x_dim, x_dim_label, l_dim, l_dim_label)
        self.play(FadeIn(load_arrow), FadeIn(p_label), run_time=0.8)
        
        self.play(Beam(beam, E=5, I=1, P=0.1, L=L), run_time=2, rate_func=linear)
        self.wait(2)

## SYMMETRIC MEMBERS IN PURE BENDING
class BeamLoadingMiddle(Scene):
    def construct(self):
        axes_origin = LEFT* 2
        L = 4  # Length of the beam
        t = 0.5  # Thickness of the beam
        axes = Axes(
            x_range=[0, L*1.5, 1],
            y_range=[-t*3, t*3, 1],
            x_length=L*1.5,
            y_length=t*8,
            axis_config={"include_ticks": False, "include_numbers": False}            
        )

        axes.shift(axes_origin - axes.c2p(0, 0))
        y_label = axes.get_y_axis_label(
            Tex("$y$").scale(0.65),
            edge=UP,
            direction=UP,
            buff=0.1,
        )
        x_label = axes.get_x_axis_label(
            Tex("$x$").scale(0.65),
            edge=RIGHT,
            direction=RIGHT,
            buff=0.1,
        )
        self.add(axes, x_label, y_label)

