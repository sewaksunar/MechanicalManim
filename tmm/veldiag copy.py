from manim import *

class VelDiag(Scene):
    def create_point_with_label(self, pos, label_text, label_dir=DOWN):
        """Create a Dot with a label at specified position and direction"""
        dot = Dot(pos)
        label = MathTex(label_text).next_to(dot, label_dir)
        return dot, label
    
    def create_point_from_polar(self, origin, angle_deg, distance, label_text, label_dir=DOWN):
        """Create a point from polar coordinates (angle, distance) relative to origin"""
        angle_rad = np.deg2rad(angle_deg)
        pos = origin + np.array([np.cos(angle_rad), np.sin(angle_rad), 0]) * distance
        return self.create_point_with_label(pos, label_text, label_dir)
    
    def setup_mechanism(self):
        """Setup all mechanism components without animating"""
        # Define constants
        self.SCALE = 1.5
        self.OFFSET = 4.5
        
        # Store all positions
        self.positions = {}
        self.mobjects_dict = {}  # Renamed to avoid conflict with Scene.mobjects
        
        # Create origin O2
        self.positions['O2'] = np.zeros(3)
        self.mobjects_dict['pointO2'], self.mobjects_dict['label_O2'] = self.create_point_with_label(
            self.positions['O2'], r"O_2", DOWN
        )
        
        # Create point A at 120° from O2
        self.mobjects_dict['pointA'], self.mobjects_dict['label_A'] = self.create_point_from_polar(
            self.positions['O2'], 120, self.SCALE, r"A", LEFT
        )
        self.positions['A'] = self.mobjects_dict['pointA'].get_center()
        
        # Create line O2-A (can be animated)
        self.mobjects_dict['line_O2A'] = Line(self.positions['O2'], self.positions['A'])
        
        # Create reference horizontal line from O2
        self.positions['tempB'] = self.positions['O2'] + np.array([5, 0, 0])
        self.mobjects_dict['line_O2_ref'] = Line(self.positions['O2'], self.positions['tempB'])
        
        # Create point B on horizontal line from O2
        self.positions['B'] = self.positions['O2'] + np.array([self.OFFSET, 0, 0])
        self.mobjects_dict['pointB'], self.mobjects_dict['label_B'] = self.create_point_with_label(
            self.positions['B'], "B", DOWN
        )
        
        # Store original link length AB (rigid constraint)
        self.AB_length = np.linalg.norm(self.positions['B'] - self.positions['A'])
        
        # Create line A-B (can be animated)
        self.mobjects_dict['line_AB'] = Line(self.positions['A'], self.positions['B'])
    
    def calculate_B_position(self, A_pos):
        """
        Calculate B position on horizontal line through O2, maintaining AB link length
        B slides horizontally, constrained to y = O2_y
        """
        O2_y = self.positions['O2'][1]
        A_x, A_y = A_pos[0], A_pos[1]
        
        # Solve: (B_x - A_x)^2 + (O2_y - A_y)^2 = AB_length^2
        # B_x = A_x ± sqrt(AB_length^2 - (O2_y - A_y)^2)
        discriminant = self.AB_length**2 - (O2_y - A_y)**2
        
        if discriminant >= 0:
            B_x = A_x + np.sqrt(discriminant)  # Take positive solution (slides right)
        else:
            # If constraint cannot be satisfied, keep B at O2 level
            B_x = A_x
        
        return np.array([B_x, O2_y, 0])
    
    def draw_initial_diagram(self):
        """Animate the initial static diagram"""
        # Fade in origin
        self.play(FadeIn(self.mobjects_dict['pointO2']), Write(self.mobjects_dict['label_O2']))
        
        # Fade in point A
        self.play(FadeIn(self.mobjects_dict['pointA']), Write(self.mobjects_dict['label_A']))
        
        # Create line O2-A
        self.play(Create(self.mobjects_dict['line_O2A']))
        
        # Create reference line
        self.play(Create(self.mobjects_dict['line_O2_ref']))
        
        # Create point B
        self.play(FadeIn(self.mobjects_dict['pointB']), Write(self.mobjects_dict['label_B']))
        
        # Create line A-B
        self.play(Create(self.mobjects_dict['line_AB']))
        
        self.wait(1)
    
    def add_motions(self):
        """Add motion animations - input O2A rotates, B slides horizontally - all synchronized"""
        # Rotation angle for input link O2A
        rotation_angle = PI*6
        
        # Create updater function for B to follow the constraint as A rotates
        def update_B_position(mob):
            """Update function called every frame to keep B constrained"""
            A_pos = self.mobjects_dict['pointA'].get_center()
            new_B_pos = self.calculate_B_position(A_pos)
            self.mobjects_dict['pointB'].move_to(new_B_pos)
            self.mobjects_dict['label_B'].next_to(self.mobjects_dict['pointB'], DOWN)
            self.mobjects_dict['line_AB'].put_start_and_end_on(A_pos, new_B_pos)
        
        # Add the updater to B
        self.mobjects_dict['pointB'].add_updater(update_B_position)
        
        # Animate everything simultaneously in one call
        self.play(
            self.mobjects_dict['line_O2A'].animate.rotate(rotation_angle, about_point=self.positions['O2']),
            self.mobjects_dict['pointA'].animate.rotate(rotation_angle, about_point=self.positions['O2']),
            self.mobjects_dict['label_A'].animate.rotate(rotation_angle, about_point=self.positions['O2']),
            run_time=2
        )
        
        # Remove the updater after animation
        self.mobjects_dict['pointB'].remove_updater(update_B_position)
        
        # Update stored positions
        self.positions['A'] = self.mobjects_dict['pointA'].get_center()
        self.positions['B'] = self.mobjects_dict['pointB'].get_center()
        self.positions['B'] = self.mobjects_dict['pointB'].get_center()
        
        self.wait(1)
    
    def construct(self):
        # Setup mechanism
        self.setup_mechanism()
        
        # Draw initial static diagram
        self.draw_initial_diagram()
        
        # Add motions
        self.add_motions()
        
        self.wait(3)
