from manim import *
import numpy as np
import sympy as sp

class MechanismI(Scene):
    def construct(self):
        axis = Axes(
            x_range=[-.4, .8, 1],
            y_range=[-0.4, .8, 1],
            x_length=10,
            y_length=5,
            tips=False,
        )
        axis.move_to(ORIGIN+DOWN)
        labels = axis.get_axis_labels(
            MathTex(r"x").scale(0.7),
            MathTex(r"y").scale(0.7)
        )
        pO2 = axis.get_origin()
        O2 = Dot(pO2, color=YELLOW)
        labelsO2 = MathTex(r"O_2").scale(0.7)
        labelsO2.move_to(pO2 + LEFT * 0.3 + DOWN * 0.3)

        scale = 1.5
        O4O2 = 250/100 * scale
        labelsO4 = MathTex(r"O_4").scale(0.7)

        pO4 = pO2 + RIGHT * O4O2
        O4 = Dot(pO2 + RIGHT * O4O2, color=YELLOW)
        labelsO4.move_to(pO2 + RIGHT * O4O2 + LEFT * 0.3 + DOWN * 0.3)

        # link 2
        O2A = 100/100 * scale
        O2A_angle = 120 * DEGREES  # Try 0, 45, 90, 135, 180 degrees
        pA = pO2 + O2A * np.array([np.cos(O2A_angle), np.sin(O2A_angle), 0])
        A = Dot(pA, color=BLUE)
        labelsA = MathTex(r"A").scale(0.7)
        labelsA.move_to(pA + UP * 0.3 + LEFT * 0.3)

        link2 = VGroup(
            Line(pO2, pA, color=BLUE),
            A,
            labelsA
        )

        # link 3 and link 4 calculation
        BA = 250/100 * scale
        BO4 = 300/100 * scale
        
        # Circle intersection using sympy
        B_x, B_y = sp.symbols('B_x B_y', real=True)
        eq1 = (B_x - pO4[0])**2 + (B_y - pO4[1])**2 - BO4**2
        eq2 = (B_x - pA[0])**2 + (B_y - pA[1])**2 - BA**2
        
        solutions = sp.solve([eq1, eq2], (B_x, B_y))
        
        # Handle solution selection more robustly
        if len(solutions) == 0:
            # No solution - mechanism cannot reach this position
            print("Warning: No valid configuration found")
            pB = pA + RIGHT * BA  # Default fallback
        elif len(solutions) == 1:
            # Single solution (circles are tangent)
            pB = np.array([float(solutions[0][0]), float(solutions[0][1]), 0])
        else:
            # Two solutions - choose the one that forms proper mechanism
            # Typically, we want the solution where B is "above" the line O2-O4
            # or based on the elbow-up/elbow-down configuration
            
            sol1 = np.array([float(solutions[0][0]), float(solutions[0][1]), 0])
            sol2 = np.array([float(solutions[1][0]), float(solutions[1][1]), 0])
            
            # Choose based on y-coordinate (elbow-up configuration)
            # You can change this logic based on your mechanism requirements
            if sol1[1] >= sol2[1]:
                pB = sol1
            else:
                pB = sol2
            
            # Alternative: Choose based on which forms a valid four-bar linkage
            # (the one that doesn't cross itself)
            # Uncomment below if you prefer this method:
            """
            # Calculate cross product to determine orientation
            v1 = pA - pO2
            v2_1 = sol1 - pA
            v2_2 = sol2 - pA
            
            cross1 = v1[0] * v2_1[1] - v1[1] * v2_1[0]
            cross2 = v1[0] * v2_2[1] - v1[1] * v2_2[0]
            
            # Choose solution with positive cross product (counter-clockwise)
            if cross1 > cross2:
                pB = sol1
            else:
                pB = sol2
            """
        
        # link 3
        link3 = VGroup(
            Line(pA, pB, color=GREEN),
            Dot(pB, color=GREEN),
            MathTex(r"B").scale(0.7).move_to(pB + UP * 0.3 + RIGHT * 0.3)
        )

        # link 4
        link4 = VGroup(
            Line(pB, pO4, color=RED),
        )

        # Angle arc label
        # Handle special case when angle is 0 or 180 degrees
        if abs(O2A_angle) < 0.01 or abs(O2A_angle - PI) < 0.01:
            # For 0 or 180 degrees, create a small arc manually
            arc = Arc(
                radius=0.5,
                start_angle=0,
                angle=O2A_angle if abs(O2A_angle) > 0.01 else 0.1,
                arc_center=pO2
            )
        else:
            arc = Angle(Line(pO2, pO4), Line(pO2, pA), radius=0.5, other_angle=False)
        
        angle_deg = O2A_angle * 180 / PI
        value = MathTex(f"{angle_deg:.1f}^{{\\circ}}").scale(0.7)
        value.next_to(arc.get_end() + UP*0.2 + RIGHT*0.1)

        self.add(axis, labels, labelsO2, O2, labelsO4, O4, link2, link3, link4, arc, value)

from manim import *
import numpy as np
import sympy as sp

class MechanismVelocityAnalysis(Scene):
    def construct(self):
        # --- PART 1: PHYSICS SETUP ---
        # Coordinate system
        axis = Axes(
            x_range=[-.4, .8, 1], y_range=[-0.4, .8, 1],
            x_length=10, y_length=5, tips=False
        ).move_to(ORIGIN + DOWN)
        
        # Dimensions
        scale = 1.5
        pO2 = axis.get_origin()
        pO4 = pO2 + RIGHT * (250/100 * scale)
        O2A_len = 100/100 * scale
        BA_len = 250/100 * scale
        BO4_len = 300/100 * scale
        omega2 = 45 * DEGREES # rad/s
        
        # --- CALCULATE MECHANISM DATA ---
        angles = np.linspace(120*DEGREES, (120+360)*DEGREES, 120)
        pos_A, pos_B, vel_A, vel_B = [], [], [], []
        
        for angle in angles:
            # Position A
            pa = pO2 + O2A_len * np.array([np.cos(angle), np.sin(angle), 0])
            
            # Position B (Circle intersection)
            bx, by = sp.symbols('bx by', real=True)
            eq1 = (bx - pO4[0])**2 + (by - pO4[1])**2 - BO4_len**2
            eq2 = (bx - pa[0])**2 + (by - pa[1])**2 - BA_len**2
            sols = sp.solve([eq1, eq2], (bx, by))
            
            # Pick correct solution
            if len(sols) >= 1:
                s1 = np.array([float(sols[0][0]), float(sols[0][1]), 0])
                if len(sols) == 2:
                    s2 = np.array([float(sols[1][0]), float(sols[1][1]), 0])
                    pb = s1 if s1[1] >= s2[1] else s2
                else: pb = s1
            else: pb = pa + RIGHT * BA_len
            
            pos_A.append(pa)
            pos_B.append(pb)
            
            # Velocity A
            ra = pa - pO2
            va = omega2 * np.array([-ra[1], ra[0], 0])
            vel_A.append(va)
            
            # Velocity B (Matrix method)
            r_ba = pb - pa
            r_bo4 = pb - pO4
            if np.linalg.norm(r_ba[:2]) > 0.01:
                mat = np.column_stack([[-r_ba[1], r_ba[0]], [-(-r_bo4[1]), -r_bo4[0]]])
                if abs(np.linalg.det(mat)) > 0.01:
                    w = np.linalg.solve(mat, -va[:2])
                    omega3 = w[0]
                else: omega3 = 0
            else: omega3 = 0
            
            vb = va + omega3 * np.array([-r_ba[1], r_ba[0], 0])
            vel_B.append(vb)

        # --- ANIMATION PART 1: MOVING MECHANISM ---
        tracker = ValueTracker(120*DEGREES)
        
        def get_idx():
            val = tracker.get_value()
            idx = int(((val - 120*DEGREES)/(360*DEGREES)) * (len(angles)-1))
            return min(max(idx,0), len(angles)-1)

        # Live components
        ln2 = always_redraw(lambda: Line(pO2, pos_A[get_idx()], color=BLUE, stroke_width=4))
        ptA = always_redraw(lambda: Dot(pos_A[get_idx()], color=BLUE))
        ln3 = always_redraw(lambda: Line(pos_A[get_idx()], pos_B[get_idx()], color=GREEN, stroke_width=4))
        ptB = always_redraw(lambda: Dot(pos_B[get_idx()], color=GREEN))
        ln4 = always_redraw(lambda: Line(pos_B[get_idx()], pO4, color=RED, stroke_width=4))
        
        # Labels
        lbl_O2 = MathTex(r"O_2").scale(0.6).next_to(pO2, DL, 0.1)
        lbl_O4 = MathTex(r"O_4").scale(0.6).next_to(pO4, DR, 0.1)
        
        self.add(axis, Dot(pO2), Dot(pO4), lbl_O2, lbl_O4, ln2, ptA, ln3, ptB, ln4)
        
        # Play one rotation
        self.play(tracker.animate.set_value((120+360)*DEGREES), run_time=4, rate_func=linear)
        self.play(tracker.animate.set_value(120*DEGREES), run_time=0.5)
        self.wait(0.2)

        # --- PART 2: STATIC SNAPSHOT ---
        # Get data at current frame (120 degrees)
        c_pa, c_pb = pos_A[0], pos_B[0]
        c_va, c_vb = vel_A[0], vel_B[0]
        
        self.remove(ln2, ptA, ln3, ptB, ln4) # Remove live objects
        
        # Build Static Group
        mech_scale = 0.7
        
        # Angle Arc and Label
        angle_arc = Angle(
            Line(pO2, pO2+RIGHT), 
            Line(pO2, c_pa), 
            radius=0.4, color=YELLOW
        )
        angle_lbl = MathTex(r"120^\circ", color=YELLOW).scale(0.5).next_to(angle_arc, UR, buff=0.05)

        s_grp = VGroup(
            axis, Dot(pO2), Dot(pO4), lbl_O2, lbl_O4,
            Line(pO2, c_pa, color=BLUE, stroke_width=4),
            Dot(c_pa, color=BLUE), MathTex("A").scale(0.6).next_to(c_pa, UL, 0.1),
            Line(c_pa, c_pb, color=GREEN, stroke_width=4),
            Dot(c_pb, color=GREEN), MathTex("B").scale(0.6).next_to(c_pb, UR, 0.1),
            Line(c_pb, pO4, color=RED, stroke_width=4),
            angle_arc, angle_lbl
        )
        
        # Add tiny reference arrows on mechanism
        ref_va = Arrow(c_pa, c_pa + c_va*0.3, color=BLUE, buff=0, stroke_width=2)
        ref_vb = Arrow(c_pb, c_pb + c_vb*0.3, color=RED, buff=0, stroke_width=2)
        s_grp.add(ref_va, ref_vb)

        self.add(s_grp)
        
        # Move Mechanism Left
        self.play(s_grp.animate.scale(mech_scale).to_edge(LEFT, buff=0.5))
        
        # --- PART 3: VELOCITY POLYGON ---
        
        # New Position: High and Right (vectors point down-left at 120deg)
        origin_poly = RIGHT * 3.5 + UP * 1.5
        v_scale = 3.0  # Big scale
        
        # Origin
        dot_o = Dot(origin_poly, color=WHITE)
        lbl_o = MathTex("o").scale(0.7).next_to(dot_o, UR, 0.1)
        self.play(FadeIn(dot_o), Write(lbl_o))
        
        # 1. V_A (Absolute)
        # Transform from mechanism arrow to polygon arrow
        vec_a_target = np.array([c_va[0], c_va[1], 0]) * v_scale
        arrow_va = Arrow(origin_poly, origin_poly + vec_a_target, color=BLUE, buff=0, stroke_width=4)
        
        # Proxy for transform
        proxy_va = Arrow(s_grp[-2].get_start(), s_grp[-2].get_end(), color=BLUE, buff=0, stroke_width=2)
        
        lbl_va = MathTex(f"\\vec{{V}}_A ({np.linalg.norm(c_va):.2f})", color=BLUE).scale(0.6).next_to(arrow_va.get_center(), LEFT, 0.3)
        
        self.play(ReplacementTransform(proxy_va, arrow_va), FadeIn(lbl_va))
        
        dot_a = Dot(arrow_va.get_end(), color=BLUE, radius=0.06)
        lbl_pt_a = MathTex("a").scale(0.6).next_to(dot_a, LEFT, 0.1)
        self.add(dot_a, lbl_pt_a)
        
        # 2. V_BA (Relative)
        vec_ba = c_vb - c_va
        vec_ba_target = np.array([vec_ba[0], vec_ba[1], 0]) * v_scale
        arrow_vba = Arrow(arrow_va.get_end(), arrow_va.get_end() + vec_ba_target, color=GREEN, buff=0, stroke_width=4)
        
        lbl_vba = MathTex(r"\vec{V}_{BA}", color=GREEN).scale(0.6).next_to(arrow_vba, DOWN, 0.1)
        
        self.play(GrowArrow(arrow_vba), Write(lbl_vba))
        
        dot_b = Dot(arrow_vba.get_end(), color=GREEN, radius=0.06)
        lbl_pt_b = MathTex("b").scale(0.6).next_to(dot_b, DOWN, 0.1)
        self.add(dot_b, lbl_pt_b)
        
        # 3. V_B (Resultant)
        vec_b_target = np.array([c_vb[0], c_vb[1], 0]) * v_scale
        arrow_vb = Arrow(origin_poly, origin_poly + vec_b_target, color=RED, buff=0, stroke_width=4)
        
        # Proxy for transform
        proxy_vb = Arrow(s_grp[-1].get_start(), s_grp[-1].get_end(), color=RED, buff=0, stroke_width=2)
        
        lbl_vb = MathTex(f"\\vec{{V}}_B ({np.linalg.norm(c_vb):.2f})", color=RED).scale(0.6).next_to(arrow_vb.get_center(), RIGHT, 0.3)
        
        self.play(ReplacementTransform(proxy_vb, arrow_vb), FadeIn(lbl_vb))
        
        self.wait(3)