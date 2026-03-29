import numpy as np
from manim import *

def find_circle_intersection(center1, radius1, center2, radius2):
    """
    Find intersection points of two circles
    Returns: list of intersection points (numpy arrays)
    """
    c1 = np.array(center1)[:2]  # Get x, y coordinates
    c2 = np.array(center2)[:2]
    r1 = radius1
    r2 = radius2
    
    d = np.linalg.norm(c2 - c1)  # Distance between centers
    
    # Check if circles intersect
    if d > r1 + r2 or d < abs(r1 - r2) or d == 0:
        return []
    
    # Calculate intersection points
    a = (r1**2 - r2**2 + d**2) / (2 * d)
    h = np.sqrt(r1**2 - a**2)
    
    # Point on line between centers
    p = c1 + a * (c2 - c1) / d
    
    # Perpendicular offset
    perp = np.array([-(c2[1] - c1[1]), c2[0] - c1[0]]) / d
    
    # Two intersection points
    intersection1 = np.array([p[0] + h * perp[0], p[1] + h * perp[1], 0])
    intersection2 = np.array([p[0] - h * perp[0], p[1] - h * perp[1], 0])
    
    return [intersection1, intersection2]

class Link(VGroup):
    def __init__(self, start, end, start_label="", end_label="", joint_radius=0.05, 
                 start_label_direction=DOWN, end_label_direction=LEFT, 
                 label_size=36, **kwargs):
        """
        Create a mechanical link with optional joint labels
        
        Args:
            start: Starting point (numpy array or coordinate)
            end: Ending point (numpy array or coordinate)
            start_label: Label for start joint (e.g., "O_2")
            end_label: Label for end joint (e.g., "A")
            joint_radius: Radius of joint circles
            start_label_direction: Position for start label (UP, DOWN, LEFT, RIGHT)
            end_label_direction: Position for end label (UP, DOWN, LEFT, RIGHT)
            label_size: Font size for both labels (default 36)
        """
        super().__init__(**kwargs)
        
        # Create the link line
        link_line = Line(start, end)
        
        # Create joint circles
        start_joint = Circle(radius=joint_radius, color=WHITE).move_to(start).set_fill(BLACK, opacity=1)
        end_joint = Circle(radius=joint_radius, color=WHITE).move_to(end).set_fill(BLACK, opacity=1)
        
        vl = VGroup()
        vl.add(start_joint, end_joint, link_line)
        # Add to group
        self.add(vl)
        
        # Add labels if provided
        if start_label:
            self.add(MathTex(start_label, font_size=label_size).next_to(start_joint, start_label_direction))
        if end_label:
            self.add(MathTex(end_label, font_size=label_size).next_to(end_joint, end_label_direction))

class FrameLink(VGroup):
    def __init__(self, start, end, start_label="", end_label="", joint_radius=0.05, 
                 start_label_direction=DOWN, end_label_direction=LEFT, 
                 label_size=36, hash_width=0.3, hash_spacing=0.05, hash_direction=DOWN,
                 hash_length=0.8, hash_angle=45, **kwargs):
        """
        Create a fixed frame link (normal link with inclined hashing in center region)
        
        Args:
            start: Starting point (numpy array or coordinate)
            end: Ending point (numpy array or coordinate)
            start_label: Label for start joint
            end_label: Label for end joint
            joint_radius: Radius of joint circles
            start_label_direction: Position for start label (UP, DOWN, LEFT, RIGHT)
            end_label_direction: Position for end label (UP, DOWN, LEFT, RIGHT)
            label_size: Font size for labels
            hash_width: Width of hashing region perpendicular to the link
            hash_spacing: Spacing between hash lines
            hash_direction: Which side to hash (UP, DOWN, LEFT, RIGHT)
            hash_length: Length of hashing region (centered on link, 0-1 ratio of link length)
            hash_angle: Angle of inclination for hash marks in degrees
        """
        super().__init__(**kwargs)
        
        # Create the link line
        link_line = Line(start, end)
        
        # Create joint circles
        start_joint = Circle(radius=joint_radius, color=WHITE).move_to(start).set_fill(BLACK, opacity=1)
        end_joint = Circle(radius=joint_radius, color=WHITE).move_to(end).set_fill(BLACK, opacity=1)
        
        # Add to group
        self.add(start_joint, end_joint, link_line)
        
        # Add inclined hashing marks in center region
        direction = np.array(end) - np.array(start)
        link_length = np.linalg.norm(direction)
        direction_norm = direction / link_length  # Normalize
        perpendicular = np.array([-direction_norm[1], direction_norm[0], 0])  # Perpendicular vector
        
        # Determine base direction vector based on hash_direction
        if np.allclose(hash_direction, UP):
            base_hash_dir = perpendicular
        elif np.allclose(hash_direction, DOWN):
            base_hash_dir = -perpendicular
        elif np.allclose(hash_direction, LEFT):
            base_hash_dir = -direction_norm
        elif np.allclose(hash_direction, RIGHT):
            base_hash_dir = direction_norm
        else:
            base_hash_dir = perpendicular
        
        # Create inclined direction by mixing base direction with link direction
        angle_rad = np.radians(hash_angle)
        hash_dir_vec = np.cos(angle_rad) * base_hash_dir + np.sin(angle_rad) * direction_norm
        hash_dir_vec = hash_dir_vec / np.linalg.norm(hash_dir_vec)  # Normalize
        
        # Calculate centered hash region
        hash_region_length = link_length * hash_length
        hash_start_pos = (link_length - hash_region_length) / 2
        hash_end_pos = hash_start_pos + hash_region_length
        
        # Draw inclined hash marks only in center region
        for i in np.arange(hash_start_pos, hash_end_pos, hash_spacing):
            start_point = np.array(start) + direction_norm * i
            end_point = start_point + hash_dir_vec * hash_width
            
            hash_line = Line(
                start_point,
                end_point,
                color=WHITE,
                stroke_width=2
            )
            self.add(hash_line)
        
        # Add labels if provided
        if start_label:
            self.add(MathTex(start_label, font_size=label_size).next_to(start_joint, start_label_direction))
        
        # Add labels if provided
        if start_label:
            self.add(MathTex(start_label, font_size=label_size).next_to(start_joint, start_label_direction))
        if end_label:
            self.add(MathTex(end_label, font_size=label_size).next_to(end_joint, end_label_direction))

class SpaceDiag(Scene):
   def construct(self):
    inputang = 135 * DEGREES


    o2 = np.zeros(3)
    link2 = Line(o2, RIGHT*1.50)
    link2.set_angle(inputang)

    a = link2.get_end()
    # self.play(Create(a))

    o2 = link2.get_start()
    # self.play(Create(o2))

    glink2 = Link(
            start=o2,
            end=a,
            start_label="O_2",
            start_label_direction=DOWN,
            end_label="A",
            end_label_direction=LEFT,
            label_size=24

        )
    
    link1 = Line(o2, o2 + RIGHT*2)
    o4 = link1.get_end()

    glink1 = FrameLink(
        start=o2,
        end = o4,
        hash_direction=DOWN,
        hash_length=0.6,       # 0-1: fraction of link to hash (centered)
        hash_angle=45,         # Degree angle for inclination
        hash_width=0.2,
        hash_spacing=0.1  
    )
    # First: Complete glink1 animation
    self.play(Create(glink1), run_time=4)
    # Then: Animate glink2
    self.play(Create(glink2), run_time=4)

    clink3 = Circle(radius=4.5).move_to(a)
    clink4 = Circle(radius=3).move_to(o4)
    
    # Find intersection points of clink3 and clink4
    intersections = find_circle_intersection(a, 4.5, o4, 3)
    
    # Use the first intersection point (or choose based on your needs)
    if intersections:
        b = intersections[0]  # First intersection point
        intersection_point = Circle(radius=0.1, color=RED).move_to(b)
    else:
        b = (a + o4) / 2  # Fallback: midpoint if no intersection
        intersection_point = Circle(radius=0.1, color=YELLOW).move_to(b)

    link3 = Link(
        start=a,
        end=b,
        end_label="B",
        end_label_direction=RIGHT,
        label_size=24
    )
    link4 = Link(
        start=o4,
        end=b,
        end_label="B",
        end_label_direction=RIGHT,
        label_size=24
    )
    self.play(Create(clink3), Create(clink4))
    self.play(Create(intersection_point))
    self.play(FadeOut(clink3), FadeOut(clink4), FadeOut(intersection_point))
    self.play(Create(link3), Create(link4), run_time=4)