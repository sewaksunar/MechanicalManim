from manim import *
import numpy as np
from sympy import symbols, cos, sin, solve, sqrt, atan2, pi as sym_pi
from sympy import Matrix, simplify, N as sympy_N

class VP1(Scene):
    """
    Four-bar linkage ve2004locity analysis using SymPy for accurate calculations
    Split screen: Left - Mechanism, Right - Velocity Polygon
    """
    
    def construct(self):
        # Given dimensions (in inches)
        R_BA_val = 4   # Link 2 (crank)
        R_CB_val = 18  # Link 3 (coupler BC)
        R_CD_val = 11  # Link 4 (rocker)
        R_DA_val = 10  # Ground link
        R_GB_val = 10  # Distance from B to G
        R_EG_val = 4   # Distance from G to E
        R_HD_val = 7   # Distance from D to H
        R_FH_val = 3   # Distance from H to F
        
        # Scale for visualization
        scale = 0.25
        R_BA = R_BA_val * scale
        R_CB = R_CB_val * scale
        R_CD = R_CD_val * scale
        R_DA = R_DA_val * scale
        R_GB = R_GB_val * scale
        R_EG = R_EG_val * scale
        R_HD = R_HD_val * scale
        R_FH = R_FH_val * scale
        
        # Initial angle of crank 2 (120 degrees)
        theta2_deg = 120
        theta2 = theta2_deg * DEGREES
        
        # Angular velocity of crank 2
        omega2_rpm = 900
        omega2 = omega2_rpm * 2 * PI / 60  # rad/s
        
        # Title
        title = Text("Four-Bar Linkage Velocity Analysis", font_size=30)
        title.to_edge(UP, buff=0.15)
        self.play(Write(title))
        self.wait(0.5)
        
        # Create dividing lines for four quadrants
        h_divider = Line(LEFT * 7, RIGHT * 7, color=WHITE).move_to(DOWN * 0.5).set_stroke(width=2)
        v_divider = Line(UP * 3, DOWN * 3.5, color=WHITE).set_stroke(width=2)
        
        # Quadrant labels
        mech_label = Text("(a) Mechanism", font_size=20).move_to(LEFT * 3.5 + UP * 2.5).set_color(GREY)
        vel_label = Text("(b) Velocity Polygon", font_size=20).move_to(RIGHT * 3.5 + UP * 2.5).set_color(GREY)
        vec_alg_label_title = Text("(c) Vector Addition", font_size=20).move_to(LEFT * 3.5 + DOWN * 0.7).set_color(GREY)
        calc_label_title = Text("(d) Calculations", font_size=20).move_to(RIGHT * 3.5 + DOWN * 0.7).set_color(GREY)
        
        # ========== TOP LEFT: MECHANISM ==========
        # Position mechanism on left side
        A = LEFT * 4.5 + UP * 1
        D = A + RIGHT * R_DA
        
        # Use SymPy for position analysis
        theta3_sym, theta4_sym = symbols('theta3 theta4')
        
        eq1 = R_BA_val * cos(theta2_deg * sym_pi / 180) + R_CB_val * cos(theta3_sym) - R_DA_val - R_CD_val * cos(theta4_sym)
        eq2 = R_BA_val * sin(theta2_deg * sym_pi / 180) + R_CB_val * sin(theta3_sym) - R_CD_val * sin(theta4_sym)
        
        solutions = solve([eq1, eq2], [theta3_sym, theta4_sym])
        
        if len(solutions) > 0:
            sol = solutions[0] if len(solutions) == 1 else solutions[1]
            theta3_val = float(sympy_N(sol[0]))
            theta4_val = float(sympy_N(sol[1]))
        else:
            theta3_val = 0.5
            theta4_val = 0.3
        
        theta3 = theta3_val
        theta4 = theta4_val
        
        # Calculate positions
        B = A + R_BA * np.array([np.cos(theta2), np.sin(theta2), 0])
        C = D + R_CD * np.array([np.cos(theta4), np.sin(theta4), 0])
        
        # Calculate G, E, H, F
        BC_unit = (C - B) / np.linalg.norm(C - B)
        G = B + R_GB * BC_unit
        BC_perp = np.array([BC_unit[1], -BC_unit[0], 0])
        E = G + R_EG * BC_perp
        
        DC_unit = (C - D) / np.linalg.norm(C - D)
        H = D + R_HD * DC_unit
        CD_perp = np.array([DC_unit[1], -DC_unit[0], 0])
        F = H + R_FH * CD_perp
        
        # Velocity analysis with SymPy
        A_matrix = Matrix([
            [R_CB_val * sin(theta3_val), -R_CD_val * sin(theta4_val)],
            [-R_CB_val * cos(theta3_val), R_CD_val * cos(theta4_val)]
        ])
        
        b_vector = Matrix([
            R_BA_val * omega2 * sin(theta2),
            -R_BA_val * omega2 * cos(theta2)
        ])
        
        omega_solution = A_matrix.inv() * b_vector
        omega3 = float(sympy_N(omega_solution[0]))
        omega4 = float(sympy_N(omega_solution[1]))
        
        # Calculate velocities
        vB = omega2 * R_BA_val * np.array([-np.sin(theta2), np.cos(theta2), 0])
        vG = vB + omega3 * R_GB_val * np.array([-BC_unit[1], BC_unit[0], 0])
        vE = vG + omega3 * R_EG_val * np.array([-BC_perp[1], BC_perp[0], 0])
        vH = omega4 * R_HD_val * np.array([-DC_unit[1], DC_unit[0], 0])
        vF = vH + omega4 * R_FH_val * np.array([-CD_perp[1], CD_perp[0], 0])
        vC = omega4 * R_CD_val * np.array([-np.sin(theta4), np.cos(theta4), 0])
        
        # Calculate magnitudes and angles
        vB_mag = np.linalg.norm(vB)
        vC_mag = np.linalg.norm(vC)
        vG_mag = np.linalg.norm(vG)
        vE_mag = np.linalg.norm(vE)
        vH_mag = np.linalg.norm(vH)
        vF_mag = np.linalg.norm(vF)
        
        # Calculate angles (in degrees, measured from positive x-axis)
        angle_vB = np.degrees(np.arctan2(vB[1], vB[0]))
        angle_vC = np.degrees(np.arctan2(vC[1], vC[0]))
        angle_vG = np.degrees(np.arctan2(vG[1], vG[0]))
        angle_vE = np.degrees(np.arctan2(vE[1], vE[0]))
        angle_vH = np.degrees(np.arctan2(vH[1], vH[0]))
        angle_vF = np.degrees(np.arctan2(vF[1], vF[0]))
        
        # Create proper hinge supports
        # Support A
        support_A_plate = Rectangle(width=0.5, height=0.08, color=GREY, 
                                    fill_opacity=1).move_to(A + DOWN * 0.35)
        hinge_A_outer = Circle(radius=0.16, color=GREY).move_to(A).set_stroke(width=3).set_fill(opacity=0)
        hinge_A_inner = Circle(radius=0.12, color=WHITE).move_to(A).set_fill(WHITE, opacity=1)
        hinge_A_support = Line(A, A + DOWN * 0.3, color=GREY, stroke_width=5)
        
        hatches_A = VGroup()
        for i in range(6):
            x_offset = -0.25 + i * 0.1
            hatch = Line(
                A + DOWN * 0.39 + RIGHT * x_offset,
                A + DOWN * 0.52 + RIGHT * (x_offset + 0.07),
                color=GREY, stroke_width=2
            )
            hatches_A.add(hatch)
        
        # Support D
        support_D_plate = Rectangle(width=0.5, height=0.08, color=GREY, 
                                    fill_opacity=1).move_to(D + DOWN * 0.35)
        hinge_D_outer = Circle(radius=0.16, color=GREY).move_to(D).set_stroke(width=3).set_fill(opacity=0)
        hinge_D_inner = Circle(radius=0.12, color=WHITE).move_to(D).set_fill(WHITE, opacity=1)
        hinge_D_support = Line(D, D + DOWN * 0.3, color=GREY, stroke_width=5)
        
        hatches_D = VGroup()
        for i in range(6):
            x_offset = -0.25 + i * 0.1
            hatch = Line(
                D + DOWN * 0.39 + RIGHT * x_offset,
                D + DOWN * 0.52 + RIGHT * (x_offset + 0.07),
                color=GREY, stroke_width=2
            )
            hatches_D.add(hatch)
        
        # Draw links
        link2 = Line(A, B, color=RED).set_stroke(width=5)
        link3 = Polygon(B, C, E, fill_color=BLUE_E, fill_opacity=0.3, 
                       stroke_color=GREEN, stroke_width=4)
        link4 = Polygon(D, C, F, fill_color=BLUE_E, fill_opacity=0.3,
                       stroke_color=BLUE, stroke_width=4)
        
        # Pin joints
        pivot_B = Circle(radius=0.09, color=YELLOW).move_to(B).set_fill(YELLOW, opacity=1)
        pivot_C = Circle(radius=0.09, color=YELLOW).move_to(C).set_fill(YELLOW, opacity=1)
        
        # Points
        point_G = Dot(G, color=ORANGE, radius=0.07)
        point_E = Dot(E, color=ORANGE, radius=0.09)
        point_H = Dot(H, color=PURPLE, radius=0.07)
        point_F = Dot(F, color=PURPLE, radius=0.09)
        
        # Lines
        dash_GE = Line(G, E, color=GREY, stroke_width=2)
        dash_HF = Line(H, F, color=GREY, stroke_width=2)
        
        # Create velocity arrows at mechanism points (scaled smaller for mechanism display)
        mech_scale = 0.002  # Smaller scale for mechanism arrows
        
        # Mechanism velocity vectors
        vB_mech = Arrow(B, B + vB * mech_scale, color=RED, buff=0, stroke_width=3, tip_length=0.15)
        vC_mech = Arrow(C, C + vC * mech_scale, color=BLUE, buff=0, stroke_width=3, tip_length=0.15)
        vE_mech = Arrow(E, E + vE * mech_scale, color="#AE2E00", buff=0, stroke_width=4, tip_length=0.15)
        vF_mech = Arrow(F, F + vF * mech_scale, color="#9D4EDD", buff=0, stroke_width=4, tip_length=0.15)
        vG_mech = Arrow(G, G + vG * mech_scale, color=ORANGE, buff=0, stroke_width=2, tip_length=0.12)
        vH_mech = Arrow(H, H + vH * mech_scale, color=PURPLE, buff=0, stroke_width=2, tip_length=0.12)
        
        # ========== BOTTOM LEFT: VECTOR ALGEBRA ==========
        vec_alg_center = LEFT * 3.5 + DOWN * 2
        vec_alg_scale = 0.0035  # Scale for vector algebra diagrams
        
        # Create vector components for vG = vB + (ω3 × rGB)
        vGB_component = omega3 * R_GB_val * np.array([-BC_unit[1], BC_unit[0], 0])
        
        # Vector algebra for vG
        vG_alg_origin = vec_alg_center
        vG_alg_vB = Arrow(vG_alg_origin, vG_alg_origin + vB * vec_alg_scale, 
                         color=RED, buff=0, stroke_width=3, tip_length=0.12)
        vG_alg_vGB = Arrow(vG_alg_origin + vB * vec_alg_scale, 
                          vG_alg_origin + vB * vec_alg_scale + vGB_component * vec_alg_scale,
                          color=GREEN, buff=0, stroke_width=3, tip_length=0.12)
        vG_alg_result = Arrow(vG_alg_origin, vG_alg_origin + vG * vec_alg_scale,
                             color=ORANGE, buff=0, stroke_width=4, tip_length=0.15)
        vG_alg_label = Text("vG = vB + ω₃×rGB", font_size=14, color=ORANGE).move_to(LEFT * 3.5 + DOWN * 1.2)
        vG_alg_vB_label = MathTex("v_B", font_size=10, color=RED).next_to(vG_alg_vB.get_center(), DOWN, buff=0.08)
        vG_alg_vGB_label = MathTex("\\omega_3 r_{GB}", font_size=10, color=GREEN).next_to(vG_alg_vGB.get_center(), UP, buff=0.08)
        vG_alg_result_label = MathTex("v_G", font_size=10, color=ORANGE).next_to(vG_alg_result.get_end(), RIGHT, buff=0.08)
        
        # Create vector components for vE = vG + (ω3 × rGE)
        vGE_component = omega3 * R_EG_val * np.array([-BC_perp[1], BC_perp[0], 0])
        
        # Vector algebra for vE
        vE_alg_origin = vec_alg_center
        vE_alg_vG = Arrow(vE_alg_origin, vE_alg_origin + vG * vec_alg_scale,
                         color=ORANGE, buff=0, stroke_width=3, tip_length=0.12)
        vE_alg_vGE = Arrow(vE_alg_origin + vG * vec_alg_scale,
                          vE_alg_origin + vG * vec_alg_scale + vGE_component * vec_alg_scale,
                          color=YELLOW, buff=0, stroke_width=3, tip_length=0.12)
        vE_alg_result = Arrow(vE_alg_origin, vE_alg_origin + vE * vec_alg_scale,
                             color="#FF6B35", buff=0, stroke_width=4, tip_length=0.15)
        vE_alg_label = Text("vE = vG + ω₃×rGE", font_size=14, color="#FF6B35").move_to(LEFT * 3.5 + DOWN * 1.2)
        vE_alg_vG_label = MathTex("v_G", font_size=10, color=ORANGE).next_to(vE_alg_vG.get_center(), DOWN, buff=0.08)
        vE_alg_vGE_label = MathTex("\\omega_3 r_{GE}", font_size=10, color=YELLOW).next_to(vE_alg_vGE.get_center(), RIGHT, buff=0.08)
        vE_alg_result_label = MathTex("v_E", font_size=10, color="#FF6B35").next_to(vE_alg_result.get_end(), LEFT, buff=0.08)
        
        # Create vector components for vF = vH + (ω4 × rHF)
        vHF_component = omega4 * R_FH_val * np.array([-CD_perp[1], CD_perp[0], 0])
        
        # Vector algebra for vF
        vF_alg_origin = vec_alg_center
        vF_alg_vH = Arrow(vF_alg_origin, vF_alg_origin + vH * vec_alg_scale,
                         color=PURPLE, buff=0, stroke_width=3, tip_length=0.12)
        vF_alg_vHF = Arrow(vF_alg_origin + vH * vec_alg_scale,
                          vF_alg_origin + vH * vec_alg_scale + vHF_component * vec_alg_scale,
                          color=YELLOW, buff=0, stroke_width=3, tip_length=0.12)
        vF_alg_result = Arrow(vF_alg_origin, vF_alg_origin + vF * vec_alg_scale,
                             color="#9D4EDD", buff=0, stroke_width=4, tip_length=0.15)
        vF_alg_label = Text("vF = vH + ω₄×rHF", font_size=14, color="#9D4EDD").move_to(LEFT * 3.5 + DOWN * 1.2)
        vF_alg_vH_label = MathTex("v_H", font_size=10, color=PURPLE).next_to(vF_alg_vH.get_center(), DOWN, buff=0.08)
        vF_alg_vHF_label = MathTex("\\omega_4 r_{HF}", font_size=10, color=YELLOW).next_to(vF_alg_vHF.get_center(), RIGHT, buff=0.08)
        vF_alg_result_label = MathTex("v_F", font_size=10, color="#9D4EDD").next_to(vF_alg_result.get_end(), LEFT, buff=0.08)
        
        # Labels
        label_A = Text("A", font_size=20).next_to(A, LEFT, buff=0.1)
        label_B = Text("B", font_size=20).next_to(B, LEFT, buff=0.1)
        label_C = Text("C", font_size=20).next_to(C, UP, buff=0.1)
        label_D = Text("D", font_size=20).next_to(D, RIGHT, buff=0.1)
        label_E = Text("E", font_size=20).next_to(E, DOWN, buff=0.1)
        label_F = Text("F", font_size=20).next_to(F, RIGHT, buff=0.1)
        label_G = Text("G", font_size=20).next_to(G, UP, buff=0.1)
        label_H = Text("H", font_size=20).next_to(H, UP, buff=0.1)
        
        label_2 = Text("2", font_size=18, color=RED).move_to((A + B) / 2 + LEFT * 0.25)
        label_3 = Text("3", font_size=18, color=GREEN).move_to((B + C + E) / 3)
        label_4 = Text("4", font_size=18, color=BLUE).move_to((D + C + F) / 3)
        
        angle_arc = Arc(radius=0.35, start_angle=0, angle=theta2, 
                       arc_center=A, color=YELLOW)
        angle_label = MathTex(r"120^\circ", font_size=16, color=YELLOW).next_to(angle_arc, RIGHT, buff=0.05)
        
        # ========== TOP RIGHT: VELOCITY POLYGON ==========        
        # Origin for velocity polygon - positioned in top right quadrant
        O_vel = RIGHT * 3.5 + UP * 1.2
        
        # Scale for velocity vectors
        vel_scale = 0.004
        
        # Velocity vectors from origin O
        O_point = Dot(O_vel, color=WHITE, radius=0.08)
        O_label = MathTex("O", font_size=22).next_to(O_vel, DOWN+LEFT, buff=0.15)
        
        # vB vector
        B_vel = O_vel + vB * vel_scale
        vB_arrow = Arrow(O_vel, B_vel, color=RED, buff=0, stroke_width=5, tip_length=0.2, max_tip_length_to_length_ratio=0.15)
        B_vel_point = Dot(B_vel, color=RED, radius=0.08)
        B_vel_label = MathTex("B", font_size=24, color=RED).next_to(B_vel, UP, buff=0.15)
        vB_mag_label = MathTex(f"{vB_mag:.1f}", font_size=14, color=RED).move_to((O_vel + B_vel) / 2 + UP * 0.2)
        
        # vC vector
        C_vel = O_vel + vC * vel_scale
        vC_arrow = Arrow(O_vel, C_vel, color=BLUE, buff=0, stroke_width=5, tip_length=0.2, max_tip_length_to_length_ratio=0.15)
        C_vel_point = Dot(C_vel, color=BLUE, radius=0.08)
        C_vel_label = MathTex("C", font_size=24, color=BLUE).next_to(C_vel, RIGHT, buff=0.15)
        vC_mag_label = MathTex(f"{vC_mag:.1f}", font_size=14, color=BLUE).move_to((O_vel + C_vel) / 2 + RIGHT * 0.25)
        
        # vG vector
        G_vel = O_vel + vG * vel_scale
        vG_arrow = Arrow(O_vel, G_vel, color=ORANGE, buff=0, stroke_width=4, tip_length=0.18, max_tip_length_to_length_ratio=0.15)
        G_vel_point = Dot(G_vel, color=ORANGE, radius=0.07)
        G_vel_label = MathTex("G", font_size=20, color=ORANGE).next_to(G_vel, UP+LEFT, buff=0.12)
        
        # vE vector
        E_vel = O_vel + vE * vel_scale
        vE_arrow = Arrow(O_vel, E_vel, color="#FF6B35", buff=0, stroke_width=6, tip_length=0.22, max_tip_length_to_length_ratio=0.15)
        E_vel_point = Dot(E_vel, color="#FF6B35", radius=0.10)
        E_vel_label = MathTex("E", font_size=26, color="#FF6B35").next_to(E_vel, LEFT, buff=0.15)
        vE_mag_label = MathTex(f"{vE_mag:.1f}", font_size=14, color="#FF6B35").move_to((O_vel + E_vel) / 2 + LEFT * 0.3)
        
        # vH vector
        H_vel = O_vel + vH * vel_scale
        vH_arrow = Arrow(O_vel, H_vel, color=PURPLE, buff=0, stroke_width=4, tip_length=0.18, max_tip_length_to_length_ratio=0.15)
        H_vel_point = Dot(H_vel, color=PURPLE, radius=0.07)
        H_vel_label = MathTex("H", font_size=20, color=PURPLE).next_to(H_vel, DOWN, buff=0.12)
        
        # vF vector
        F_vel = O_vel + vF * vel_scale
        vF_arrow = Arrow(O_vel, F_vel, color="#9D4EDD", buff=0, stroke_width=6, tip_length=0.22, max_tip_length_to_length_ratio=0.15)
        F_vel_point = Dot(F_vel, color="#9D4EDD", radius=0.10)
        F_vel_label = MathTex("F", font_size=26, color="#9D4EDD").next_to(F_vel, DOWN+RIGHT, buff=0.15)
        vF_mag_label = MathTex(f"{vF_mag:.1f}", font_size=14, color="#9D4EDD").move_to((O_vel + F_vel) / 2 + DOWN * 0.25 + RIGHT * 0.15)
        
        # Relative velocity arrows - more professional styling
        BC_rel = DashedLine(B_vel, C_vel, color=GREEN, dash_length=0.1, stroke_width=3, stroke_opacity=0.6)
        GE_rel = DashedLine(G_vel, E_vel, color=ORANGE, dash_length=0.1, stroke_width=2, stroke_opacity=0.5)
        HF_rel = DashedLine(H_vel, F_vel, color=PURPLE, dash_length=0.1, stroke_width=2, stroke_opacity=0.5)
        
        # ========== BOTTOM RIGHT: CALCULATIONS ==========
        calc_area = RIGHT * 3.5 + DOWN * 2
        
        # vB calculation
        vB_calc = VGroup(
            Text("Point B:", font_size=14, color=RED),
            MathTex(r"v_B = \omega_2 \times r_{BA}", font_size=12, color=WHITE),
            MathTex(f"= {omega2:.2f} \\times {R_BA_val}", font_size=12, color=WHITE),
            MathTex(f"|v_B| = {vB_mag:.1f}\\text{{ in/s}}", font_size=12, color=YELLOW),
            MathTex(f"\\angle = {angle_vB:.1f}^\\circ", font_size=12, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        vB_calc.move_to(calc_area)
        vB_calc_box = SurroundingRectangle(vB_calc, color=RED, buff=0.08, corner_radius=0.05)
        
        # vC calculation
        vC_calc = VGroup(
            Text("Point C:", font_size=14, color=BLUE),
            MathTex(r"v_C = \omega_4 \times r_{CD}", font_size=12, color=WHITE),
            MathTex(f"= {omega4:.2f} \\times {R_CD_val}", font_size=12, color=WHITE),
            MathTex(f"|v_C| = {vC_mag:.1f}\\text{{ in/s}}", font_size=12, color=YELLOW),
            MathTex(f"\\angle = {angle_vC:.1f}^\\circ", font_size=12, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        vC_calc.move_to(calc_area)
        vC_calc_box = SurroundingRectangle(vC_calc, color=BLUE, buff=0.08, corner_radius=0.05)
        
        # vG calculation
        vG_calc = VGroup(
            Text("Point G:", font_size=14, color=ORANGE),
            MathTex(r"v_G = v_B + \omega_3 \times r_{GB}", font_size=11, color=WHITE),
            MathTex(f"\\omega_3 = {omega3:.2f}\\text{{ rad/s}}", font_size=11, color=WHITE),
            MathTex(f"|v_G| = {vG_mag:.1f}\\text{{ in/s}}", font_size=12, color=YELLOW),
            MathTex(f"\\angle = {angle_vG:.1f}^\\circ", font_size=12, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        vG_calc.move_to(calc_area)
        vG_calc_box = SurroundingRectangle(vG_calc, color=ORANGE, buff=0.08, corner_radius=0.05)
        
        # vE calculation
        vE_calc = VGroup(
            Text("Point E:", font_size=14, color="#FF6B35"),
            MathTex(r"v_E = v_G + \omega_3 \times r_{GE}", font_size=11, color=WHITE),
            MathTex(f"r_{{GE}} = {R_EG_val}\\text{{ in}}", font_size=11, color=WHITE),
            MathTex(f"|v_E| = {vE_mag:.1f}\\text{{ in/s}}", font_size=12, color=YELLOW),
            MathTex(f"\\angle = {angle_vE:.1f}^\\circ", font_size=12, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        vE_calc.move_to(calc_area)
        vE_calc_box = SurroundingRectangle(vE_calc, color="#FF6B35", buff=0.08, corner_radius=0.05)
        
        # vH calculation
        vH_calc = VGroup(
            Text("Point H:", font_size=14, color=PURPLE),
            MathTex(r"v_H = \omega_4 \times r_{HD}", font_size=12, color=WHITE),
            MathTex(f"r_{{HD}} = {R_HD_val}\\text{{ in}}", font_size=12, color=WHITE),
            MathTex(f"|v_H| = {vH_mag:.1f}\\text{{ in/s}}", font_size=12, color=YELLOW),
            MathTex(f"\\angle = {angle_vH:.1f}^\\circ", font_size=12, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        vH_calc.move_to(calc_area)
        vH_calc_box = SurroundingRectangle(vH_calc, color=PURPLE, buff=0.08, corner_radius=0.05)
        
        # vF calculation
        vF_calc = VGroup(
            Text("Point F:", font_size=14, color="#9D4EDD"),
            MathTex(r"v_F = v_H + \omega_4 \times r_{HF}", font_size=11, color=WHITE),
            MathTex(f"r_{{HF}} = {R_FH_val}\\text{{ in}}", font_size=11, color=WHITE),
            MathTex(f"|v_F| = {vF_mag:.1f}\\text{{ in/s}}", font_size=12, color=YELLOW),
            MathTex(f"\\angle = {angle_vF:.1f}^\\circ", font_size=12, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        vF_calc.move_to(calc_area)
        vF_calc_box = SurroundingRectangle(vF_calc, color="#9D4EDD", buff=0.08, corner_radius=0.05)
        
        # Results - displayed at bottom
        results = VGroup(
            MathTex(r"\omega_2 = 900 \text{ rpm, } \theta_2 = 120^\circ \quad"
                    r"\omega_3 = " + f"{omega3:.2f}" + r" \text{ rad/s} \quad"
                    r"\omega_4 = " + f"{omega4:.2f}" + r" \text{ rad/s} \quad"
                    r"|v_E| = " + f"{vE_mag:.2f}" + r" \text{ in/s} \quad"
                    r"|v_F| = " + f"{vF_mag:.2f}" + r" \text{ in/s}", 
                    font_size=14, color=WHITE),
        )
        results.to_edge(DOWN, buff=0.2)
        
        # Animation sequence
        self.play(Create(h_divider), Create(v_divider))
        self.play(
            Write(mech_label), Write(vel_label),
            Write(vec_alg_label_title), Write(calc_label_title)
        )
        self.wait(0.3)
        
        # Draw mechanism
        self.play(
            Create(hinge_A_support), Create(hinge_D_support),
            Create(support_A_plate), Create(support_D_plate),
            Create(hatches_A), Create(hatches_D),
        )
        self.play(
            Create(link2), Create(link3), Create(link4),
            Create(hinge_A_outer), Create(hinge_A_inner),
            Create(hinge_D_outer), Create(hinge_D_inner),
            Create(pivot_B), Create(pivot_C),
            Create(point_G), Create(point_E),
            Create(point_H), Create(point_F),
            Create(dash_GE), Create(dash_HF)
        )
        self.play(
            Write(label_A), Write(label_B), Write(label_C), Write(label_D),
            Write(label_E), Write(label_F), Write(label_G), Write(label_H),
            Write(label_2), Write(label_3), Write(label_4)
        )
        self.play(Create(angle_arc), Write(angle_label))
        self.wait(0.5)
        
        # Show velocity vectors on mechanism
        self.play(
            Create(vB_mech), Create(vC_mech), 
            Create(vE_mech), Create(vF_mech),
            Create(vG_mech), Create(vH_mech)
        )
        self.wait(0.5)
        
        # Draw velocity polygon with transfer animation
        self.play(Create(O_point), Write(O_label))
        
        # Transfer vB from mechanism to polygon
        vB_transfer = vB_mech.copy()
        self.play(
            Create(vB_calc_box), Write(vB_calc),
            run_time=0.8
        )
        self.wait(0.5)
        self.play(
            Transform(vB_transfer, vB_arrow),
            FadeIn(B_vel_point),
            Write(B_vel_label),
            Write(vB_mag_label),
            run_time=1.2
        )
        self.remove(vB_transfer)
        self.add(vB_arrow)
        self.wait(0.3)
        self.play(FadeOut(vB_calc_box), FadeOut(vB_calc))
        
        # Transfer vC from mechanism to polygon
        vC_transfer = vC_mech.copy()
        self.play(
            Create(vC_calc_box), Write(vC_calc),
            run_time=0.8
        )
        self.wait(0.5)
        self.play(
            Transform(vC_transfer, vC_arrow),
            FadeIn(C_vel_point),
            Write(C_vel_label),
            Write(vC_mag_label),
            run_time=1.2
        )
        self.remove(vC_transfer)
        self.add(vC_arrow)
        self.play(Create(BC_rel))
        self.wait(0.3)
        self.play(FadeOut(vC_calc_box), FadeOut(vC_calc))
        
        # Transfer vG from mechanism to polygon with vector algebra
        vG_transfer = vG_mech.copy()
        self.play(
            Create(vG_calc_box), Write(vG_calc),
            run_time=0.8
        )
        # Show vector algebra: vG = vB + (ω3 × rGB)
        self.play(
            Write(vG_alg_label),
            Create(vG_alg_vB), Write(vG_alg_vB_label),
            run_time=0.8
        )
        self.play(
            Create(vG_alg_vGB), Write(vG_alg_vGB_label),
            run_time=0.8
        )
        self.play(
            Create(vG_alg_result), Write(vG_alg_result_label),
            run_time=0.8
        )
        self.wait(0.5)
        self.play(
            Transform(vG_transfer, vG_arrow),
            FadeIn(G_vel_point),
            Write(G_vel_label),
            run_time=1.0
        )
        self.remove(vG_transfer)
        self.add(vG_arrow)
        self.wait(0.3)
        self.play(
            FadeOut(vG_calc_box), FadeOut(vG_calc),
            FadeOut(vG_alg_label), FadeOut(vG_alg_vB), FadeOut(vG_alg_vB_label),
            FadeOut(vG_alg_vGB), FadeOut(vG_alg_vGB_label),
            FadeOut(vG_alg_result), FadeOut(vG_alg_result_label)
        )
        
        # Transfer vE from mechanism to polygon with vector algebra
        vE_transfer = vE_mech.copy()
        self.play(
            Create(vE_calc_box), Write(vE_calc),
            run_time=0.8
        )
        # Show vector algebra: vE = vG + (ω3 × rGE)
        self.play(
            Write(vE_alg_label),
            Create(vE_alg_vG), Write(vE_alg_vG_label),
            run_time=0.8
        )
        self.play(
            Create(vE_alg_vGE), Write(vE_alg_vGE_label),
            run_time=0.8
        )
        self.play(
            Create(vE_alg_result), Write(vE_alg_result_label),
            run_time=0.8
        )
        self.wait(0.5)
        self.play(
            Transform(vE_transfer, vE_arrow),
            FadeIn(E_vel_point),
            Write(E_vel_label),
            Write(vE_mag_label),
            run_time=1.2
        )
        self.remove(vE_transfer)
        self.add(vE_arrow)
        self.play(Create(GE_rel))
        self.wait(0.3)
        self.play(
            FadeOut(vE_calc_box), FadeOut(vE_calc),
            FadeOut(vE_alg_label), FadeOut(vE_alg_vG), FadeOut(vE_alg_vG_label),
            FadeOut(vE_alg_vGE), FadeOut(vE_alg_vGE_label),
            FadeOut(vE_alg_result), FadeOut(vE_alg_result_label)
        )
        
        # Transfer vH from mechanism to polygon
        vH_transfer = vH_mech.copy()
        self.play(
            Create(vH_calc_box), Write(vH_calc),
            run_time=0.8
        )
        self.wait(0.5)
        self.play(
            Transform(vH_transfer, vH_arrow),
            FadeIn(H_vel_point),
            Write(H_vel_label),
            run_time=1.0
        )
        self.remove(vH_transfer)
        self.add(vH_arrow)
        self.wait(0.3)
        self.play(FadeOut(vH_calc_box), FadeOut(vH_calc))
        
        # Transfer vF from mechanism to polygon with vector algebra
        vF_transfer = vF_mech.copy()
        self.play(
            Create(vF_calc_box), Write(vF_calc),
            run_time=0.8
        )
        # Show vector algebra: vF = vH + (ω4 × rHF)
        self.play(
            Write(vF_alg_label),
            Create(vF_alg_vH), Write(vF_alg_vH_label),
            run_time=0.8
        )
        self.play(
            Create(vF_alg_vHF), Write(vF_alg_vHF_label),
            run_time=0.8
        )
        self.play(
            Create(vF_alg_result), Write(vF_alg_result_label),
            run_time=0.8
        )
        self.wait(0.5)
        self.play(
            Transform(vF_transfer, vF_arrow),
            FadeIn(F_vel_point),
            Write(F_vel_label),
            Write(vF_mag_label),
            run_time=1.2
        )
        self.remove(vF_transfer)
        self.add(vF_arrow)
        self.play(Create(HF_rel))
        self.wait(0.3)
        self.play(
            FadeOut(vF_calc_box), FadeOut(vF_calc),
            FadeOut(vF_alg_label), FadeOut(vF_alg_vH), FadeOut(vF_alg_vH_label),
            FadeOut(vF_alg_vHF), FadeOut(vF_alg_vHF_label),
            FadeOut(vF_alg_result), FadeOut(vF_alg_result_label)
        )
        self.wait(0.5)
        
        # Show results
        self.play(Write(results))
        self.wait(3)