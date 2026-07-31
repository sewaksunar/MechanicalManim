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
        # Fixed end is at x=0 (start), free end is at x=L (end)

        if self.span_len == 0:
            return

        k = self.P / (6.0 * self.E * self.I)
        num_points = 80
        x_targets = np.linspace(0.0, self.span_len, num_points)

        for i, line in enumerate(self.lines):
            d = self.line_offsets[i]
            points = []

            for x in x_targets:
                y_deflection = -(k * x**2) * (3.0 * self.span_len - x) * alpha
                slope = -(3.0 * k * x) * (2.0 * self.span_len - x) * alpha

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
        for y in np.linspace(-t/2, t/2, 10):
            line = Line(ORIGIN, RIGHT * L).shift(UP * y)
            lines.append(line)
        
        # Group all lines together
        beam = VGroup(*lines)

        beam.move_to(ORIGIN)
        
        self.play(Beam(beam, E=5, I=1, P=0.1, L=L), run_time=2, rate_func=linear)
        self.wait(2)

        ref_line = lines[len(lines) // 2]
        middle_line = Line(ref_line.get_start(), ref_line.get_start() + RIGHT * L).set_color(RED)
        self.play(Create(middle_line))

        self.play(Beam(middle_line, E=5, I=1, P=0.1, L=L), run_time=1, rate_func=linear)
        self.wait(2)

        # force vector
        force_vec = Arrow(ref_line.get_end(), ref_line.get_end() + UP * 0.5, buff=0).set_color(YELLOW)
        self.play(Create(force_vec))