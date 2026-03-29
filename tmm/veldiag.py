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
                 start_label_direction=DOWN, end_label_direction=DOWN, 
                 label_size=24, hash_width=0.3, hash_spacing=0.05, hash_direction=DOWN,
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

class FourBarMechanism(VGroup):
    def __init__(self, origin=np.zeros(3), link2_angle=135*DEGREES, link2_length=1.50, 
                 frame_link_length=2.0, circle3_radius=4.5, circle4_radius=3.0,
                 link3_label="", link4_label="", show_construction_circles=False, **kwargs):
        """
        Create a complete four-bar linkage mechanism
        
        Args:
            origin: Position of fixed joint O2
            link2_angle: Angle of rotating link (in radians/degrees)
            link2_length: Length of rotating link (O2 to A)
            frame_link_length: Length of base/frame link
            circle3_radius: Radius of circle centered at A
            circle4_radius: Radius of circle centered at O4
            link3_label: Label for link 3 (optional)
            link4_label: Label for link 4 (optional)
            show_construction_circles: Whether to show construction circles
        """
        super().__init__(**kwargs)
        
        self.origin = np.array(origin)
        self.link2_angle = link2_angle
        self.link2_length = link2_length
        self.frame_link_length = frame_link_length
        self.circle3_radius = circle3_radius
        self.circle4_radius = circle4_radius
        
        # Calculate key points
        o2 = self.origin
        
        # Point A (end of rotating link)
        link2_end = o2 + np.array([link2_length * np.cos(link2_angle), 
                                    link2_length * np.sin(link2_angle), 0])
        a = link2_end
        
        # Point O4 (end of frame link)
        o4 = o2 + np.array([frame_link_length, 0, 0])
        
        # Frame link (fixed)
        self.frame_link = FrameLink(
            start=o2,
            end=o4,
            start_label="O_2",
            end_label="O_4",
            hash_direction=DOWN,
            hash_length=0.6,
            hash_angle=45,
            hash_width=0.2,
            hash_spacing=0.1
        )
        self.add(self.frame_link)
        
        # Link 2 (rotating) - store the line separately for get_a() method
        self.link2_line = Line(o2, a)  # Store line reference
        self.a_relative = a - o2  # Store relative position of A from O2
        self.link2 = Link(
            start=o2,
            end=a,
            start_label="",
            end_label="A",
            start_label_direction=DOWN,
            end_label_direction=LEFT,
            label_size=24
        )
        self.add(self.link2)
        
        # Construction circles
        self.circle3 = Circle(radius=circle3_radius).move_to(a)
        self.circle4 = Circle(radius=circle4_radius).move_to(o4)
        
        # Find intersection (point B)
        intersections = find_circle_intersection(a, circle3_radius, o4, circle4_radius)
        if intersections:
            b = intersections[0]
        else:
            b = (a + o4) / 2
        
        self.b = b
        
        # Links 3 and 4
        self.link3 = Link(
            start=a,
            end=b,
            end_label=link3_label if link3_label else "B",
            end_label_direction=RIGHT,
            label_size=24
        )
        
        self.link4 = Link(
            start=o4,
            end=b,
            end_label=link4_label if link4_label else "B",
            end_label_direction=RIGHT,
            label_size=24
        )
        
        self.add(self.link3, self.link4)
        
        # Store circles (can be shown/hidden)
        self.construction_circles = VGroup(self.circle3, self.circle4)
        if show_construction_circles:
            self.add(self.construction_circles)
    
    def get_a(self):
        return self.link2[0][2].get_end()        # end of link2 line

    def get_b(self):
        return self.link3[0][1].get_center()     # end_joint of link3

    def get_o2(self):
        return self.frame_link[0].get_center()   # start_joint of frame_link

    def get_o4(self):
        return self.frame_link[1].get_center()   # end_joint of frame_link

class SpaceDiag(Scene):
   def construct(self):
    # Create angle tracker for animation
    angle_tracker = ValueTracker(135 * DEGREES)
    # Create origin tracker for position
    origin_tracker = ValueTracker(0)  # 0 for ORIGIN, 1 for DOWN + LEFT

    # Create mechanism that updates with angle AND origin position
    mechanism = always_redraw(
        lambda: FourBarMechanism(
            origin=interpolate(ORIGIN+DOWN*2+LEFT, DOWN*2 + LEFT*4, origin_tracker.get_value()),
            link2_angle=angle_tracker.get_value(),
            link2_length=1.50,
            frame_link_length=2.0,
            circle3_radius=4.5,
            circle4_radius=3.0,
            show_construction_circles=False
        )
    )

    self.add(mechanism)

    # Step 1: Animate the angle from 135° to 200° 
    self.play(angle_tracker.animate.set_value(200 * DEGREES), rate_func=linear, run_time=2)

    # Step 2: Animate back to starting angle
    self.play(angle_tracker.animate.set_value(135 * DEGREES), run_time=2)

    # Step 3: SEPARATELY position it - do this after animation
    self.play(origin_tracker.animate.set_value(1), run_time=1.5)



    self.play(Write(Text("Crank-shaft Mechnasim").move_to(UP*3)))
    a = mechanism.get_a()  # Get coordinates
    b = mechanism.get_b()
    o2 = mechanism.get_o2()
    o4 = mechanism.get_o4()

    self.play(Create(Dot(a).set_color(RED), run_time=10))
    self.play(Create(Dot(b).set_color(RED)), Create(Dot(o2).set_color(RED)), Create(Dot(o4).set_color(RED)))

    vecao2 = a - o2                                      # vector from O2 to A
    unit_ao2 = vecao2 / np.linalg.norm(vecao2)           # unit vector along OA

    # Rotate 90° to get normal (perpendicular)
    normal_ao2 = np.array([-unit_ao2[1], unit_ao2[0], 0])  # [-y, x, 0]

    vela = Arrow(
        a,
        a + normal_ao2 * 1.0,   # scale as needed
        buff=0,
        color=BLUE
    )

    # Draw normal vector at point A
    self.play(Create(vela))

    labela = MathTex(r"v_{A/O_2}", font_size=24).next_to(vela.get_end(), DOWN)
    self.play(Write(labela))

    gval = VGroup(vela, labela)

    velpol = np.array([10, 0, 0]) 
    self.play(gval.animate.shift(velpol))


    velbo4 = b - o4    # vector from O4 to B
    unit_bo4 = velbo4 / np.linalg.norm(velbo4)     # unit vector along BO4
    normal_bo4 = np.array([-unit_bo4[1], unit_bo4[0], 0])  # [-y, x, 0]
    velb = Arrow(
        b,
        b + normal_bo4 * 1.0,   # scale as needed
        buff=0,
        color=GREEN
    )

    pole = vela.get_start()
    end_target = velb.get_end()   # after shift

    t = ValueTracker(0.1)           # starts at full shifted-arrow size

    velb_growing = always_redraw(lambda: Arrow(
        pole,
        pole + (end_target - pole) * t.get_value(),
        buff=0,
        color=GREEN,
        max_tip_length_to_length_ratio =0.05

    ))

    labelb_growing = always_redraw(lambda: MathTex(
        r"v_{B/O_4}", font_size=24
    ).next_to(velb_growing.get_end(), DOWN))

    # Seamless swap — t=1 means velb_growing is visually identical to gvelb
    # Replace this:

    # With this:
    self.remove(velb)
    self.add(velb_growing, labelb_growing)

    # Grow directly from current size (t=1) → target, no zero reset
    self.play(t.animate.set_value(0.5), run_time=2)
    self.play(t.animate.set_value(0.1), run_time=2)
    self.play(t.animate.set_value(0.5), run_time=2)
    # Keep velb_growing visible - don't remove it

    dashed_arrow = always_redraw(lambda: DashedVMobject(
        Arrow(
            pole,
            pole + (end_target - pole) * t.get_value(),
            buff=0,
            color=YELLOW,
            stroke_width=2,
            max_tip_length_to_length_ratio =0.05
        ),
        num_dashes=15,
        dashed_ratio=0.5
    ))

    self.add(dashed_arrow)
    self.play(t.animate.set_value(0.5), run_time=2)

    ba = b - a
    unit_ba = ba / np.linalg.norm(ba)
    normal_ba = np.array([-unit_ba[1], unit_ba[0], 0])  # [-y, x, 0]
    velba = Arrow(
        b,
        b + normal_ba * 1.0,   # scale as needed
        buff=0,
        color=PURPLE
    )
    labelba = MathTex(r"v_{B/A}", font_size=24).next_to(velba.get_end(), UP)
    
    # Shift velba to velocity polygon (start from end of vela)
    gvelba = VGroup(velba, labelba)
    velba_shift = gval[0].get_end() - b  # Shift so tail starts at end of shifted vela
    self.play(Create(velba), Write(labelba))
    self.play(gvelba.animate.shift(velba_shift))

    pole_ba = gvelba[0].get_start()  # Start of shifted velba (at end of vela)
    end_target_ba = gvelba[0].get_end()   # End of shifted velba

    tba = ValueTracker(0.1)           # starts at full shifted-arrow size

    velba_growing = always_redraw(lambda: Arrow(
        pole_ba,
        pole_ba + (end_target_ba - pole_ba) * tba.get_value(),
        buff=0,
        color=PURPLE,
        max_tip_length_to_length_ratio=0.05
    ))

    labelba_growing = always_redraw(lambda: MathTex(
        r"v_{B/A}", font_size=24
    ).next_to(velba_growing.get_end(), UP))

    self.remove(gvelba)
    self.add(velba_growing, labelba_growing)
    
    self.play(tba.animate.set_value(2), run_time=2)
