from manim import *

class IsobaricExpansion(Scene):
    def construct(self):
        # Cylinder walls
        cylinder_bottom = Line(LEFT*2 + DOWN*1.5, RIGHT*2 + DOWN*1.5, stroke_width=4)
        cylinder_top = Line(LEFT*2 + UP*1.5, RIGHT*2 + UP*1.5, stroke_width=4)
        cylinder_left = Line(LEFT*2 + UP*1.5, LEFT*2 + DOWN*1.5, stroke_width=4)
        cylinder = VGroup(cylinder_bottom, cylinder_top, cylinder_left)
        
        # Piston
        piston = Rectangle(width=0.5, height=3, color=BLUE, fill_opacity=0.5)
        piston.move_to(LEFT*1.5)
        
        # Gas Particles (Random dots)
        num_particles = 200
        particles = VGroup()
        for _ in range(num_particles):
            dot = Dot(color=YELLOW, radius=0.03)
            # Random position in initial small volume
            x = np.random.uniform(-1.98, -1.77)
            y = np.random.uniform(-1.4, 1.4)
            dot.move_to([x, y, 0])
            
            # Store relative X position (0 to 1) within the chamber
            # Chamber goes from -2.0 to -1.75 (width 0.25)
            dot.relative_x = (x - (-2.0)) / 0.25
            dot.initial_y = y
            particles.add(dot)

        self.add(cylinder, piston, particles)
        
        # Heat source (Arrows from left face)
        arrows = VGroup(*[Arrow(start=LEFT, end=RIGHT, color=RED).next_to(cylinder_left, LEFT).shift(UP * i * 0.5) for i in range(-2, 3)])
        
        self.play(FadeIn(arrows))
        
        # Animation: Expansion
        expansion_tracker = ValueTracker(0)
        
        # Updater for piston
        def update_piston(m):
            val = expansion_tracker.get_value()
            m.move_to(LEFT*1.5 + RIGHT * val)
            
        piston.add_updater(update_piston)
        
        # Updater for particles
        def update_particles(m):
            val = expansion_tracker.get_value()
            
            # Current chamber boundaries
            left_wall = -2.0
            # Piston left face: Center is (-1.5 + val), width 0.5 -> Left face is -1.75 + val
            piston_face = -1.75 + val
            current_width = piston_face - left_wall
            
            margin = 0.05
            
            for dot in m:
                # Calculate "base" position based on expansion (uniform distribution)
                base_x = left_wall + dot.relative_x * current_width
                
                # Add random vibration (jitter)
                # Increasing jitter as expansion happens to simulate heating? 
                # User said "increase vibration". Let's make it constant but large.
                jitter_amount = 0.1
                dx = np.random.uniform(-jitter_amount, jitter_amount)
                dy = np.random.uniform(-jitter_amount, jitter_amount)
                
                new_x = base_x + dx
                new_y = dot.initial_y + dy # Vibrating around initial Y
                
                # Clamp X to stay inside chamber
                if new_x < left_wall + margin:
                    new_x = left_wall + margin + abs(dx)
                elif new_x > piston_face - margin:
                    new_x = piston_face - margin - abs(dx)
                
                # Clamp Y to stay inside cylinder
                if new_y < -1.5 + margin:
                    new_y = -1.5 + margin + abs(dy)
                elif new_y > 1.5 - margin:
                    new_y = 1.5 - margin - abs(dy)
                
                dot.move_to([new_x, new_y, 0])

        particles.add_updater(update_particles)
        
        self.play(
            expansion_tracker.animate.set_value(3),
            run_time=4,
            rate_func=linear
        )
        self.wait()
