from manim import *

class BeamReaction(Scene):
    def construct(self):
        # Beam
        beam_length = 6
        beam = Rectangle(width=beam_length, height=0.2, color=WHITE, fill_opacity=1)
        
        # Supports
        # Center them at the ends of the beam so the reaction point (top tip) is exactly at the end
        support_left = Triangle(color=GREY, fill_opacity=1).scale(0.3).next_to(beam, DOWN, buff=0)
        support_left.set_x(beam.get_left()[0])
        
        support_right = Triangle(color=GREY, fill_opacity=1).scale(0.3).next_to(beam, DOWN, buff=0)
        support_right.set_x(beam.get_right()[0])
        
        # Load (Arrow only, no text)
        load_arrow = Arrow(start=UP*2, end=DOWN*0.1, color=RED, buff=0)
        load = VGroup(load_arrow)
        
        # Reactions
        r_left = Arrow(start=DOWN, end=UP*0.5, color=GREEN).next_to(support_left, DOWN)
        r_right = Arrow(start=DOWN, end=UP*0.5, color=GREEN).next_to(support_right, DOWN)
        
        self.add(beam, support_left, support_right, load, r_left, r_right)
        
        # Animation: Move load and update reactions
        # We need a value tracker for the load position
        # Start at left support (x = -3)
        x_tracker = ValueTracker(-3)
        
        # Update load position
        load.add_updater(lambda m: m.next_to(beam.get_center() + RIGHT * x_tracker.get_value(), UP, buff=0))
        
        # Reaction updaters
        # Beam spans from x = -3 to x = 3 (length 6)
        # Left support at x = -3, Right support at x = 3
        
        def update_r_left(m):
            x = x_tracker.get_value()
            # Distance from right support = 3 - x
            # Total length = 6
            # Reaction is proportional to distance from OTHER support
            # R_left = F * (3 - x) / 6
            mag = (3 - x) / 6
            # Visual scaling
            scale = 2.0
            
            # Tip touches the beam (top of support)
            tip = support_left.get_top()
            # Tail is below
            tail = tip - UP * mag * scale
            
            m.put_start_and_end_on(tail, tip)

        def update_r_right(m):
            x = x_tracker.get_value()
            # Distance from left support = x - (-3) = x + 3
            # R_right = F * (x + 3) / 6
            mag = (x + 3) / 6
            # Visual scaling
            scale = 2.0
            
            # Tip touches the beam (top of support)
            tip = support_right.get_top()
            # Tail is below
            tail = tip - UP * mag * scale
            
            m.put_start_and_end_on(tail, tip)

        r_left.add_updater(update_r_left)
        r_right.add_updater(update_r_right)
        
        # Animate from left (-3) to right (3) and back
        self.play(x_tracker.animate.set_value(3), run_time=6, rate_func=there_and_back)
        self.wait()
