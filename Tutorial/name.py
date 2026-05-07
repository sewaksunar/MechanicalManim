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
        # Store original endpoints of each line
        self.original_lines = []
        for line in mobject:
            self.original_lines.append({
                'start': line.get_start().copy(),
                'end': line.get_end().copy(),
            })
        
    def interpolate_mobject(self, alpha):
        # deflection at x point from fixed end
        # y = - (P * x^2) / (6 * E * I) * (3L - x)
        # Fixed end is at x=0 (start), free end is at x=L (end)
        
        for i, line in enumerate(self.mobject):
            orig = self.original_lines[i]
            start_orig = orig['start'].copy()  # Fixed end at x=0, should not move vertically
            end_orig = orig['end'].copy()      # Free end at x=L
            
            # Create intermediate points for curved deflection
            points = []
            num_points = 20
            
            for j in range(num_points):
                # Parameter from 0 to 1 along the line
                t = j / (num_points - 1)
                
                # Current x position along the beam (from 0 to L)
                x = start_orig[0] + t * (end_orig[0] - start_orig[0])
                # Current y position (original)
                y = start_orig[1] + t * (end_orig[1] - start_orig[1])
                
                # Apply cantilever beam deflection formula
                # y_deflection = - (P * x^2) / (6 * E * I) * (3L - x)
                if x <= self.L:
                    y_deflection = - (self.P * x**2) / (6 * self.E * self.I) * (3 * self.L - x)
                    y_deflection *= alpha  # Scale deflection with animation progress
                else:
                    y_deflection = 0
                
                points.append(np.array([x, y + y_deflection, 0]))
            
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
        
        self.play(Beam(beam, E=5, I=1, P=0.1, L=L), run_time=2)
        self.wait(2)

        middle_line = Line(ORIGIN, RIGHT * L*1.5).set_color(RED)
        self.play(Create(middle_line))

        middle_line_deflection = Line(ORIGIN, RIGHT * L).set_color(RED)
        self.play(Beam(middle_line_deflection, E=5, I=1, P=0.1, L=L*1.5), run_time=1)
        self.wait(2)