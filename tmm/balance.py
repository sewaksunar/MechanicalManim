"""
Shaft Balancing Animation — Manim CE

Problem:
  Masses A(200kg,80mm), B(300kg,70mm), C(400kg,60mm), D(200kg,80mm)
  at planes 0, 300, 400, 700 mm from A.
  Angles (anticlockwise): A=0°, B=45°, C=115°, D=235°
  Balancing planes X (100mm), Y (500mm from A), radius = 100mm

Run with:
  manim -pql shaft_balancing.py ShaftBalancing       # low quality preview
  manim -pqh shaft_balancing.py ShaftBalancing       # high quality
"""

from manim import *
import numpy as np


# ═══════════════════════════════════════════════════════════════════════
#  NUMERICAL SOLUTION
# ═══════════════════════════════════════════════════════════════════════
def solve():
    masses  = [200, 300, 400, 200]        # kg:  A  B  C  D
    radii   = [80,  70,  60,  80]         # mm
    axial   = [0,  300, 400, 700]         # mm from A
    ang_deg = [0,   45, 115, 235]         # anticlockwise from A
    ang_rad = [np.radians(a) for a in ang_deg]
    X_pos, Y_pos, Rb = 100, 500, 100      # mm

    mr  = [m * r for m, r in zip(masses, radii)]
    dX  = [p - X_pos for p in axial]     # distances from plane X
    dYX = Y_pos - X_pos                  # = 400 mm

    # ── Take moments about X to find mY ───────────────────────────────
    sx = sum(mr[i] * dX[i] * np.cos(ang_rad[i]) for i in range(4))
    sy = sum(mr[i] * dX[i] * np.sin(ang_rad[i]) for i in range(4))
    mrl_Y_x, mrl_Y_y = -sx, -sy
    mrl_Y_mag = np.hypot(mrl_Y_x, mrl_Y_y)
    tY   = np.arctan2(mrl_Y_y, mrl_Y_x)
    mY   = mrl_Y_mag / (Rb * dYX)
    tY_d = np.degrees(tY) % 360

    # ── Force balance to find mX ───────────────────────────────────────
    mr_Y = mY * Rb
    fx = sum(mr[i] * np.cos(ang_rad[i]) for i in range(4)) + mr_Y * np.cos(tY)
    fy = sum(mr[i] * np.sin(ang_rad[i]) for i in range(4)) + mr_Y * np.sin(tY)
    mr_X_x, mr_X_y = -fx, -fy
    mr_X_mag = np.hypot(mr_X_x, mr_X_y)
    tX   = np.arctan2(mr_X_y, mr_X_x)
    mX   = mr_X_mag / Rb
    tX_d = np.degrees(tX) % 360

    return dict(
        masses=masses, radii=radii, axial=axial,
        ang_deg=ang_deg, ang_rad=ang_rad, mr=mr, dX=dX, dYX=dYX,
        mrl_Y_x=mrl_Y_x, mrl_Y_y=mrl_Y_y, mrl_Y_mag=mrl_Y_mag,
        tY=tY, mY=mY, tY_d=tY_d,
        mr_X_x=mr_X_x, mr_X_y=mr_X_y, mr_X_mag=mr_X_mag,
        tX=tX, mX=mX, tX_d=tX_d, Rb=Rb
    )


S = solve()


# ═══════════════════════════════════════════════════════════════════════
#  MANIM SCENE
# ═══════════════════════════════════════════════════════════════════════
class ShaftBalancing(Scene):

    # ── utilities ──────────────────────────────────────────────────────
    def wipe(self):
        if self.mobjects:
            self.play(FadeOut(*self.mobjects), run_time=0.6)

    def heading(self, text, color=YELLOW):
        t = Text(text, font_size=32, color=color).to_edge(UP)
        self.play(Write(t), run_time=0.6)
        return t

    def result_banner(self, text, color=GREEN):
        t = Text(text, font_size=26, color=color).to_edge(DOWN, buff=0.35)
        b = SurroundingRectangle(t, color=color, buff=0.15, stroke_width=2)
        self.play(Write(t), Create(b), run_time=0.7)
        return VGroup(t, b)

    # ── Scene 1 · Title + problem statement ────────────────────────────
    def scene_title(self):
        title = Text("Dynamic Shaft Balancing", font_size=48, color=YELLOW)
        under = Underline(title, color=YELLOW)
        self.play(Write(title), Create(under))

        lines = [
            "Masses  A:200kg  B:300kg  C:400kg  D:200kg",
            "Radii   A:80mm   B:70mm   C:60mm   D:80mm",
            "Angles  A:0°     B:45°    C:115°   D:235°  (anticlockwise)",
            "Axial   A:0mm   X:100mm  B:300mm  C:400mm  Y:500mm  D:700mm",
            "Balancing radius = 100 mm  ·  Find mX (plane X) and mY (plane Y)",
        ]
        data = VGroup(*[Text(l, font_size=21, color=WHITE) for l in lines])
        data.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        data.next_to(title, DOWN, buff=0.55)
        self.play(FadeIn(data), run_time=1.0)
        self.wait(2)
        self.wipe()

    # ── Scene 2 · Space diagram ────────────────────────────────────────
    def scene_space_diagram(self):
        self.heading("Space Diagram (Side View)")

        shaft = Line(LEFT * 5.8, RIGHT * 5.8, color=GRAY, stroke_width=5)
        self.play(Create(shaft))

        def xp(mm):          # mm → screen x
            return mm / 700 * 10.6 - 5.3

        planes = [
            ('A', 0,   RED),    ('X', 100, ORANGE),
            ('B', 300, BLUE),   ('C', 400, GREEN),
            ('Y', 500, ORANGE), ('D', 700, YELLOW),
        ]
        p_objs = []
        for name, mm, col in planes:
            ln = DashedLine([xp(mm), -1.3, 0], [xp(mm), 1.3, 0],
                            color=col, stroke_width=2.5)
            lb = Text(name, font_size=26, color=col).move_to([xp(mm), 1.7, 0])
            p_objs += [ln, lb]
        self.play(*[Create(o) for o in p_objs], run_time=1.0)

        # dimension brackets
        dims = [
            (0,   100, "100"),
            (100, 500, "400"),
            (500, 700, "200"),
            (0,   700, "700"),
        ]
        ys = [-1.9, -1.9, -1.9, -2.65]
        d_objs = []
        for (x1, x2, lbl), y in zip(dims, ys):
            arr = DoubleArrow([xp(x1), y, 0], [xp(x2), y, 0],
                              buff=0, color=WHITE, stroke_width=1.5, tip_length=0.12)
            txt = Text(f"{lbl}mm", font_size=15, color=WHITE).move_to(
                [(xp(x1) + xp(x2)) / 2, y - 0.28, 0])
            d_objs += [arr, txt]
        self.play(*[Create(o) for o in d_objs])

        # mass callouts
        m_objs = []
        for i, (nm, col) in enumerate(zip('ABCD', [RED, BLUE, GREEN, YELLOW])):
            t = Text(
                f"{nm}  {S['masses'][i]}kg\nr={S['radii'][i]}mm\nθ={S['ang_deg'][i]}°",
                font_size=17, color=col).move_to([xp(S['axial'][i]), 3.05, 0])
            m_objs.append(t)
        self.play(*[Write(t) for t in m_objs])
        self.wait(2)
        self.wipe()

    # ── Scene 3 · Polar / end-on view ──────────────────────────────────
    def scene_polar_view(self):
        self.heading("Polar (End-On) View — mr Vectors")

        O = ORIGIN
        R = 2.4
        circ  = Circle(radius=R, color=DARK_GRAY, stroke_width=1)
        xref  = DashedLine(O, O + RIGHT * R, color=DARK_GRAY, stroke_width=1)
        xlab  = Text("0°", font_size=18, color=DARK_GRAY).next_to(O + RIGHT * R, RIGHT, 0.05)
        self.play(Create(circ), Create(xref), Write(xlab))

        # degree markers
        for ad in [90, 180, 270]:
            a = np.radians(ad)
            p = O + R * 1.12 * np.array([np.cos(a), np.sin(a), 0])
            self.add(Text(f"{ad}°", font_size=16, color=DARK_GRAY).move_to(p))

        scale = R * 0.9 / max(S['mr'])
        cols  = [RED, BLUE, GREEN, YELLOW]

        for i, (col, nm) in enumerate(zip(cols, 'ABCD')):
            a   = S['ang_rad'][i]
            ep  = O + S['mr'][i] * scale * np.array([np.cos(a), np.sin(a), 0])
            arr = Arrow(O, ep, buff=0, color=col, stroke_width=3,
                        tip_length=0.22, max_stroke_width_to_length_ratio=6)
            lp  = O + (S['mr'][i] * scale + 0.5) * np.array([np.cos(a), np.sin(a), 0])
            lbl = Text(f"{nm}\n{S['mr'][i]:.0f} kg·mm",
                       font_size=19, color=col).move_to(lp)
            self.play(GrowArrow(arr), Write(lbl), run_time=0.7)

        self.play(FadeIn(
            Text("Lengths proportional to mr (kg·mm)", font_size=21, color=GRAY)
            .to_edge(DOWN, buff=0.4)))
        self.wait(2)
        self.wipe()

    # ── Scene 4 · Moment polygon (about X) ────────────────────────────
    def scene_moment_polygon(self):
        self.heading("Moment Polygon about Plane X  →  Find mY")

        mrl = [S['mr'][i] * S['dX'][i] for i in range(4)]
        vecs = [np.array([mrl[i] * np.cos(S['ang_rad'][i]),
                          mrl[i] * np.sin(S['ang_rad'][i])]) for i in range(4)]
        close = np.array([S['mrl_Y_x'], S['mrl_Y_y']])

        all_v   = vecs + [close]
        max_mag = max(np.linalg.norm(v) for v in all_v)
        sc      = 2.5 / max_mag

        cols  = [RED, BLUE, GREEN, YELLOW]
        start = np.array([-2.3, -0.7, 0])
        tip   = start.copy()
        objs  = []

        for i in range(4):
            s = tip.copy()
            e = tip + np.append(vecs[i] * sc, 0)
            arr = Arrow(s, e, buff=0, color=cols[i], stroke_width=3,
                        tip_length=0.18, max_stroke_width_to_length_ratio=6)
            mid  = (s + e) / 2
            perp = np.array([-(e - s)[1], (e - s)[0], 0])
            norm = np.linalg.norm(perp)
            if norm > 0.01:
                perp = perp / norm * 0.35
            lbl  = Text(f"mrl_{'ABCD'[i]}\n{mrl[i]/1e6:.2f}×10⁶",
                        font_size=16, color=cols[i]).move_to(mid + perp)
            self.play(GrowArrow(arr), Write(lbl), run_time=0.65)
            objs += [arr, lbl]
            tip = e.copy()

        # closing vector = mrl_Y
        c_arr = Arrow(tip, start, buff=0, color=ORANGE,
                      stroke_width=3, tip_length=0.2,
                      max_stroke_width_to_length_ratio=6)
        mid_c = (tip + start) / 2
        c_lbl = Text(
            f"mrl_Y = {S['mrl_Y_mag']:.2e} kg·mm²\nθY = {S['tY_d']:.1f}°",
            font_size=19, color=ORANGE).next_to(mid_c, DOWN, 0.15)
        self.play(GrowArrow(c_arr), Write(c_lbl), run_time=0.9)

        self.result_banner(
            f"mY  =  mrl_Y / (r × d_YX)  =  {S['mY']:.1f} kg   at   θY = {S['tY_d']:.1f}°",
            color=ORANGE)
        self.wait(2.5)
        self.wipe()

    # ── Scene 5 · Force polygon ────────────────────────────────────────
    def scene_force_polygon(self):
        self.heading("Force Polygon  →  Find mX")

        mr_vals = S['mr'] + [S['mY'] * S['Rb']]
        angs    = list(S['ang_rad']) + [S['tY']]
        cols    = [RED, BLUE, GREEN, YELLOW, ORANGE]
        names   = list('ABCD') + ['Y']
        close   = np.array([S['mr_X_x'], S['mr_X_y']])

        all_v   = [np.array([mr_vals[i]*np.cos(angs[i]),
                              mr_vals[i]*np.sin(angs[i])]) for i in range(5)] + [close]
        max_mag = max(np.linalg.norm(v) for v in all_v)
        sc      = 2.6 / max_mag

        start = np.array([-2.5, -1.0, 0])
        tip   = start.copy()
        objs  = []

        for mr, ang, col, nm in zip(mr_vals, angs, cols, names):
            s = tip.copy()
            e = tip + sc * np.array([mr * np.cos(ang), mr * np.sin(ang), 0])
            arr = Arrow(s, e, buff=0, color=col, stroke_width=3,
                        tip_length=0.18, max_stroke_width_to_length_ratio=6)
            mid  = (s + e) / 2
            perp = np.array([-(e - s)[1], (e - s)[0], 0])
            norm = np.linalg.norm(perp)
            if norm > 0.01:
                perp = perp / norm * 0.32
            lbl = Text(f"mr_{nm}", font_size=17, color=col).move_to(mid + perp)
            self.play(GrowArrow(arr), Write(lbl), run_time=0.55)
            objs += [arr, lbl]
            tip = e.copy()

        c_arr = Arrow(tip, start, buff=0, color=PURPLE, stroke_width=3,
                      tip_length=0.2, max_stroke_width_to_length_ratio=6)
        mid_c = (tip + start) / 2
        c_lbl = Text(
            f"mr_X = {S['mr_X_mag']:.0f} kg·mm\nθX = {S['tX_d']:.1f}°",
            font_size=19, color=PURPLE).next_to(mid_c, UP, 0.15)
        self.play(GrowArrow(c_arr), Write(c_lbl), run_time=0.9)

        self.result_banner(
            f"mX  =  mr_X / r  =  {S['mX']:.1f} kg   at   θX = {S['tX_d']:.1f}°",
            color=PURPLE)
        self.wait(2.5)
        self.wipe()

    # ── Scene 6 · Final results ────────────────────────────────────────
    def scene_results(self):
        title = Text("Final Balancing Results", font_size=44, color=YELLOW)
        under = Underline(title, color=YELLOW)
        self.play(Write(title), Create(under))
        self.play(VGroup(title, under).animate.to_edge(UP))

        # Result cards
        for plane, mass, angle, col, shift in [
            ("Plane  X", f"{S['mX']:.1f} kg", f"{S['tX_d']:.1f}°", PURPLE, UP * 0.8),
            ("Plane  Y", f"{S['mY']:.1f} kg", f"{S['tY_d']:.1f}°", ORANGE, DOWN * 0.6),
        ]:
            card = VGroup(
                Text(plane,   font_size=28, color=col),
                Text(f"Mass  = {mass}",  font_size=32, color=WHITE),
                Text(f"Angle = {angle}", font_size=32, color=WHITE),
            ).arrange(RIGHT, buff=0.8)
            card.move_to(shift)
            box = SurroundingRectangle(card, color=col, buff=0.2, stroke_width=2)
            self.play(FadeIn(card), Create(box))

        # Verification polar — all 6 masses
        pc = DOWN * 2.7
        Circle(radius=1.35, color=DARK_GRAY, stroke_width=1).move_to(pc)
        self.play(Create(Circle(radius=1.35, color=DARK_GRAY, stroke_width=1).move_to(pc)),
                  Create(Line(pc, pc + RIGHT * 1.45, color=DARK_GRAY, stroke_width=1)))

        all_m   = S['masses'] + [S['mX'], S['mY']]
        all_r   = S['radii']  + [S['Rb'],  S['Rb']]
        all_a   = S['ang_rad'] + [S['tX'],  S['tY']]
        all_col = [RED, BLUE, GREEN, YELLOW, PURPLE, ORANGE]
        all_nm  = list('ABCD') + ['X', 'Y']
        mx_mr   = max(m * r for m, r in zip(all_m, all_r))
        sc      = 1.25 / mx_mr

        for m, r, a, col, nm in zip(all_m, all_r, all_a, all_col, all_nm):
            ep  = pc + m * r * sc * np.array([np.cos(a), np.sin(a), 0])
            arr = Arrow(pc, ep, buff=0, color=col, stroke_width=2,
                        tip_length=0.12, max_stroke_width_to_length_ratio=6)
            lb  = Text(nm, font_size=16, color=col).move_to(
                ep + 0.22 * np.array([np.cos(a), np.sin(a), 0]))
            self.play(GrowArrow(arr), Write(lb), run_time=0.35)

        self.play(Write(
            Text("✓  Shaft is dynamically balanced", font_size=28, color=GREEN)
            .to_edge(DOWN, buff=0.3)))
        self.wait(3)

    # ── construct ──────────────────────────────────────────────────────
    def construct(self):
        self.scene_title()
        self.scene_space_diagram()
        self.scene_polar_view()
        self.scene_moment_polygon()
        self.scene_force_polygon()
        self.scene_results()