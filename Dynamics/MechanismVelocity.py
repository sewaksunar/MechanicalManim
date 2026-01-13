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

class MechanismAnimation(Scene):
    def construct(self):
        """Animated version showing the mechanism in motion with velocity analysis"""
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
        scale = 1.5
        O4O2 = 250/100 * scale
        pO4 = pO2 + RIGHT * O4O2
        
        O2 = Dot(pO2, color=YELLOW)
        O4 = Dot(pO4, color=YELLOW)
        labelsO2 = MathTex(r"O_2").scale(0.7).move_to(pO2 + LEFT * 0.3 + DOWN * 0.3)
        labelsO4 = MathTex(r"O_4").scale(0.7).move_to(pO4 + LEFT * 0.3 + DOWN * 0.3)
        
        self.add(axis, labels, O2, O4, labelsO2, labelsO4)
        
        # Parameters
        O2A = 100/100 * scale
        BA = 250/100 * scale
        BO4 = 300/100 * scale
        
        # Angular velocity of link 2 (rad/s)
        omega2 = 45 * DEGREES  # 45°/s converted to rad/s
        
        # Pre-calculate mechanism positions and velocities
        angles = np.linspace(120*DEGREES, (120+360)*DEGREES, 120)
        positions_A = []
        positions_B = []
        velocities_A = []
        velocities_B = []
        omega3_values = []
        omega4_values = []
        
        for i, angle in enumerate(angles):
            pA = pO2 + O2A * np.array([np.cos(angle), np.sin(angle), 0])
            
            # Solve for B
            B_x, B_y = sp.symbols('B_x B_y', real=True)
            eq1 = (B_x - pO4[0])**2 + (B_y - pO4[1])**2 - BO4**2
            eq2 = (B_x - pA[0])**2 + (B_y - pA[1])**2 - BA**2
            solutions = sp.solve([eq1, eq2], (B_x, B_y))
            
            if len(solutions) >= 1:
                sol1 = np.array([float(solutions[0][0]), float(solutions[0][1]), 0])
                if len(solutions) == 2:
                    sol2 = np.array([float(solutions[1][0]), float(solutions[1][1]), 0])
                    pB = sol1 if sol1[1] >= sol2[1] else sol2
                else:
                    pB = sol1
            else:
                pB = pA + RIGHT * BA
            
            positions_A.append(pA)
            positions_B.append(pB)
            
            # Calculate velocities
            # V_A = omega2 × r_A (cross product in 2D: perpendicular to radius)
            r_A = pA - pO2
            v_A = omega2 * np.array([-r_A[1], r_A[0], 0])  # Perpendicular, magnitude = omega2 * r
            velocities_A.append(v_A)
            
            # Calculate omega3 and omega4 using velocity analysis
            # V_B = V_A + omega3 × r_BA  (velocity of B relative to A)
            # V_B = omega4 × r_BO4        (velocity of B about O4)
            r_BA = pB - pA
            r_BO4 = pB - pO4
            
            # Using relative velocity equation
            # V_A + omega3 × r_BA = omega4 × r_BO4
            # Rearranging: omega3 × r_BA - omega4 × r_BO4 = -V_A
            
            # In 2D: omega × r = omega * [-r_y, r_x]
            # So: omega3 * [-r_BA_y, r_BA_x] - omega4 * [-r_BO4_y, r_BO4_x] = -v_A
            
            if np.linalg.norm(r_BA[:2]) > 0.01 and np.linalg.norm(r_BO4[:2]) > 0.01:
                # Matrix: [r_BA_perp | -r_BO4_perp] · [omega3; omega4] = -v_A
                r_BA_perp = np.array([-r_BA[1], r_BA[0]])
                r_BO4_perp = np.array([-r_BO4[1], r_BO4[0]])
                
                A_mat = np.column_stack([r_BA_perp, -r_BO4_perp])
                if np.abs(np.linalg.det(A_mat)) > 0.01:
                    omega_vals = np.linalg.solve(A_mat, -v_A[:2])
                    omega3 = omega_vals[0]
                    omega4 = omega_vals[1]
                else:
                    omega3 = 0
                    omega4 = 0
            else:
                omega3 = 0
                omega4 = 0
            
            omega3_values.append(omega3)
            omega4_values.append(omega4)
            
            # Calculate V_B using either equation (they should give same result)
            # V_B = V_A + omega3 × r_BA
            v_B_from_A = v_A + omega3 * np.array([-r_BA[1], r_BA[0], 0])
            velocities_B.append(v_B_from_A)
        
        # Create updatable mechanism
        angle_tracker = ValueTracker(120*DEGREES)
        
        def get_index():
            angle_val = angle_tracker.get_value()
            idx = int(((angle_val - 120*DEGREES) / (360*DEGREES)) * (len(angles) - 1))
            return min(max(idx, 0), len(angles) - 1)
        
        def get_mechanism_data():
            idx = get_index()
            return (positions_A[idx], positions_B[idx], 
                    velocities_A[idx], velocities_B[idx],
                    omega3_values[idx], omega4_values[idx])
        
        # Create paths
        path_A = TracedPath(
            lambda: get_mechanism_data()[0],
            stroke_color=BLUE,
            stroke_width=2,
            stroke_opacity=0.6
        )
        
        path_B = TracedPath(
            lambda: get_mechanism_data()[1],
            stroke_color=GREEN,
            stroke_width=2,
            stroke_opacity=0.6
        )
        
        # Create mechanism parts
        link2 = always_redraw(lambda: Line(
            pO2,
            get_mechanism_data()[0],
            color=BLUE,
            stroke_width=4
        ))
        
        pointA = always_redraw(lambda: Dot(
            get_mechanism_data()[0],
            color=BLUE,
            radius=0.08
        ))
        
        labelA = always_redraw(lambda: MathTex(r"A").scale(0.7).next_to(
            get_mechanism_data()[0],
            UP * 0.5 + LEFT * 0.3
        ))
        
        link3 = always_redraw(lambda: Line(
            get_mechanism_data()[0],
            get_mechanism_data()[1],
            color=GREEN,
            stroke_width=4
        ))
        
        pointB = always_redraw(lambda: Dot(
            get_mechanism_data()[1],
            color=GREEN,
            radius=0.08
        ))
        
        labelB = always_redraw(lambda: MathTex(r"B").scale(0.7).next_to(
            get_mechanism_data()[1],
            UP * 0.5 + RIGHT * 0.3
        ))
        
        link4 = always_redraw(lambda: Line(
            get_mechanism_data()[1],
            pO4,
            color=RED,
            stroke_width=4
        ))
        
        # Angle arc and value
        arc = always_redraw(lambda: Arc(
            radius=0.5,
            start_angle=0*DEGREES,
            angle=angle_tracker.get_value(),
            arc_center=pO2,
            color=YELLOW
        ))
        
        angle_value = always_redraw(lambda: DecimalNumber(
            angle_tracker.get_value() * 180 / PI,
            num_decimal_places=1,
            unit=r"^{\circ}"
        ).scale(0.6).next_to(arc.get_end() + UP * 0.15 + RIGHT * 0.15))
        
        # Velocity vectors with actual magnitude
        def get_velocity_arrow_A():
            pA, pB, vA, vB, omega3, omega4 = get_mechanism_data()
            v_mag = np.linalg.norm(vA)
            if v_mag > 0.01:
                v_dir = vA / v_mag
                # Scale for visualization (0.5 units per unit velocity)
                arrow = Arrow(
                    pA,
                    pA + v_dir * v_mag * 0.5,
                    color=BLUE,
                    buff=0,
                    stroke_width=4,
                    max_tip_length_to_length_ratio=0.2
                )
                return arrow
            return VGroup()
        
        velocity_arrow_A = always_redraw(get_velocity_arrow_A)
        
        def get_velocity_arrow_B():
            pA, pB, vA, vB, omega3, omega4 = get_mechanism_data()
            v_mag = np.linalg.norm(vB)
            if v_mag > 0.01:
                v_dir = vB / v_mag
                arrow = Arrow(
                    pB,
                    pB + v_dir * v_mag * 0.5,
                    color=GREEN,
                    buff=0,
                    stroke_width=4,
                    max_tip_length_to_length_ratio=0.2
                )
                return arrow
            return VGroup()
        
        velocity_arrow_B = always_redraw(get_velocity_arrow_B)
        
        # Velocity magnitude labels
        v_A_label = always_redraw(lambda: DecimalNumber(
            np.linalg.norm(get_mechanism_data()[2]),
            num_decimal_places=2,
        ).scale(0.5).next_to(get_mechanism_data()[0] + get_mechanism_data()[2] * 0.5 * 0.5, UP * 0.3).set_color(BLUE))
        
        v_B_label = always_redraw(lambda: DecimalNumber(
            np.linalg.norm(get_mechanism_data()[3]),
            num_decimal_places=2,
        ).scale(0.5).next_to(get_mechanism_data()[1] + get_mechanism_data()[3] * 0.5 * 0.5, DOWN * 0.3).set_color(GREEN))
        
        # Angular velocity display
        # omega_display = VGroup(
        #     MathTex(r"\omega_2 = 45^{\circ}/s", color=BLUE).scale(0.6),
        #     always_redraw(lambda: MathTex(
        #         r"\omega_3 = " + f"{get_mechanism_data()[4] * 180 / PI:.1f}" + r"^{\circ}/s",
        #         color=GREEN
        #     ).scale(0.6)),
        #     always_redraw(lambda: MathTex(
        #         r"\omega_4 = " + f"{get_mechanism_data()[5] * 180 / PI:.1f}" + r"^{\circ}/s",
        #         color=RED
        #     ).scale(0.6))
        # ).arrange(DOWN, aligned_edge=LEFT).to_corner(UL)
        
        self.add(path_A, path_B)
        self.add(link2, pointA, labelA, link3, pointB, labelB, link4)
        self.add(arc, angle_value)
        self.add(velocity_arrow_A, velocity_arrow_B)
        self.add(v_A_label, v_B_label)
        # self.add(omega_display)
        
        # Animate full rotation at constant angular velocity
        self.play(angle_tracker.animate.set_value((120+360)*DEGREES), run_time=10, rate_func=linear)
        self.wait()