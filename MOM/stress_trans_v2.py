from manim import *

# ── Constants ────────────────────────────────────────────────────────────────
CUBE_SIDE  = 1.0
FONT_SIZE  = 24
FONT_SMALL = 20

# Example rotation: 40° about Z, then 25° about X  (gives a non-trivial direction cosine matrix)
ALPHA = 40 * DEGREES   # rotation about Z
BETA  = 25 * DEGREES   # rotation about X

# Build the 3×3 direction-cosine matrix R = Rx(β) · Rz(α)
def rotation_matrix(alpha: float, beta: float) -> np.ndarray:
    Rz = np.array([
        [ np.cos(alpha), np.sin(alpha), 0],
        [-np.sin(alpha), np.cos(alpha), 0],
        [0,              0,             1],
    ])
    Rx = np.array([
        [1, 0,             0            ],
        [0, np.cos(beta),  np.sin(beta) ],
        [0, -np.sin(beta), np.cos(beta) ],
    ])
    return Rx @ Rz   # rows are (X,Y,Z) expressed in (x,y,z)

R = rotation_matrix(ALPHA, BETA)
# R[i] = (l,m,n) direction cosines for the i-th primed axis
L = R[0]; M = R[1]; N = R[2]   # rows → X-axis, Y-axis, Z-axis cosines


# ── Small helpers ─────────────────────────────────────────────────────────────
def make_axes(length: float = 3.5) -> ThreeDAxes:
    r = [-5, 5, 1]
    return ThreeDAxes(x_range=r, y_range=r, z_range=r,
                      x_length=length, y_length=length, z_length=length)


def axis_labels(axes: ThreeDAxes, names=("x", "y", "z"),
                color=WHITE) -> VGroup:
    tex_x = MathTex(names[0], color=color, font_size=FONT_SIZE)
    tex_y = MathTex(names[1], color=color, font_size=FONT_SIZE)
    tex_z = MathTex(names[2], color=color, font_size=FONT_SIZE)
    tex_x.next_to(axes.x_axis.get_end(), RIGHT,    buff=0.15)
    tex_y.next_to(axes.y_axis.get_end(), UP,        buff=0.15)
    tex_z.next_to(axes.z_axis.get_end(), IN + LEFT, buff=0.15)
    return VGroup(tex_x, tex_y, tex_z)


def face_disk(center: np.ndarray, normal: np.ndarray, color: str) -> Circle:
    """Small filled marker sitting on a cube face, oriented along *normal*."""
    _ROT = {
        tuple(np.round(LEFT).astype(int)):  (-PI / 2, UP),
        tuple(np.round(RIGHT).astype(int)): ( PI / 2, UP),
        tuple(np.round(UP).astype(int)):    (-PI / 2, RIGHT),
        tuple(np.round(DOWN).astype(int)):  ( PI / 2, RIGHT),
        tuple(np.round(IN).astype(int)):    ( PI,     UP),
    }
    disk = Circle(radius=0.05, color=color, fill_opacity=1)
    disk.move_to(center)
    key = tuple(np.round(normal).astype(int))
    if key in _ROT:
        angle, axis = _ROT[key]
        disk.rotate(angle, axis=axis)
    return disk


def make_stress_cube() -> tuple[VGroup, dict[str, np.ndarray]]:
    """
    Returns (cube_group, face_centers_dict).
    face_centers_dict keys: 'right','left','top','bottom','front','back'
    """
    cube = Cube(side_length=CUBE_SIDE, fill_opacity=0.4,
                fill_color=BLUE, stroke_color=WHITE, stroke_width=1.5)
    h = CUBE_SIDE / 2
    specs = dict(
        right=(RIGHT, RED), left=(LEFT,  RED),
        top=(UP,    GREEN), bottom=(DOWN, GREEN),
        front=(OUT,  BLUE), back=(IN,   BLUE),
    )
    dots = {
        name: face_disk(direction * h, direction, color)
        for name, (direction, color) in specs.items()
    }
    face_group = VGroup(*dots.values())
    center_dot = Dot(ORIGIN, color=YELLOW, radius=0.05, fill_opacity=1)
    group = VGroup(cube, center_dot, face_group)
    # Expose face centers (pre-rotation, at origin)
    centers = {name: direction * h for name, (direction, _) in specs.items()}
    return group, centers


def stress_arrow(start: np.ndarray, end: np.ndarray, color: str) -> Arrow3D:
    return Arrow3D(start=start, end=end, color=color, resolution=8)


# ── Scene ─────────────────────────────────────────────────────────────────────
class CoordinateTransform(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=30 * DEGREES, zoom=1.8)

        # ── Original (x, y, z) axes ───────────────────────────────────────────
        orig_axes = make_axes(length=3.5)
        orig_labels = axis_labels(orig_axes, names=("x", "y", "z"), color=WHITE)
        self.add(orig_axes)
        self.add_fixed_orientation_mobjects(*orig_labels)

        # ── Rotated (X, Y, Z) axes built from direction cosines ───────────────
        # Each rotated axis is a unit vector expressed via R rows
        axis_len = 3.5 / 2          # half the ThreeDAxes length for visual balance
        rotated_axes = VGroup()
        rotated_tips = {}
        primed_colors = dict(X=YELLOW, Y=ORANGE, Z=PINK)
        for i, (name, row) in enumerate(zip(["X", "Y", "Z"], R)):
            tip = row * axis_len
            arr = Arrow3D(start=ORIGIN, end=tip,
                          color=primed_colors[name], resolution=8)
            rotated_axes.add(arr)
            rotated_tips[name] = tip

        primed_labels = VGroup()
        for name, tip in rotated_tips.items():
            lbl = MathTex(name, color=primed_colors[name], font_size=FONT_SIZE)
            lbl.next_to(tip, normalize(tip) * 0.3 + UP * 0.1, buff=0.15)
            primed_labels.add(lbl)
            self.add_fixed_orientation_mobjects(lbl)

        self.add(rotated_axes)

        # ── Direction cosine arc labels on the X-axis only (illustrative) ─────
        # Show l1, m1, n1 as dashed lines from X-tip to each original axis tip
        x_tip  = orig_axes.x_axis.get_end()
        y_tip  = orig_axes.y_axis.get_end()
        z_tip  = orig_axes.z_axis.get_end()
        X_tip  = rotated_tips["X"]

        def dashed_proj(start, end, label_tex, label_color=YELLOW):
            line = DashedLine(start, end, color=GRAY, stroke_width=1.0,
                              dash_length=0.08)
            mid  = (start + end) / 2
            lbl  = MathTex(label_tex, color=label_color, font_size=FONT_SMALL)
            lbl.next_to(mid, normalize(end - start + RIGHT) * 0.3, buff=0.1)
            return line, lbl

        dc_lines = VGroup()
        dc_labels_fixed = []

        for (s, e, tex) in [
            (X_tip, x_tip * np.dot(X_tip, x_tip / np.linalg.norm(x_tip)), r"l_1"),
            (X_tip, y_tip * np.dot(X_tip, y_tip / np.linalg.norm(y_tip)), r"m_1"),
            (X_tip, z_tip * np.dot(X_tip, z_tip / np.linalg.norm(z_tip)), r"n_1"),
        ]:
            line, lbl = dashed_proj(s, e, tex, YELLOW)
            dc_lines.add(line)
            dc_labels_fixed.append(lbl)
            self.add_fixed_orientation_mobjects(lbl)

        self.add(dc_lines, *dc_labels_fixed)

        # ── Stress cube aligned with (x, y, z) ───────────────────────────────
        cube_group, face_centers = make_stress_cube()
        self.add(cube_group)

        # Principal stress arrows on the three visible faces
        stress_specs = [
            # (face_key, comp_face_key, magnitude, color, label_tex, lbl_dir)
            ("right",  "left",   1.0, RED,   r"\sigma_{xx}", RIGHT),
            ("top",    "bottom", 0.6, GREEN, r"\sigma_{yy}", LEFT ),
            ("front",  "back",   0.8, BLUE,  r"\sigma_{zz}", UP   ),
        ]
        for fk, ck, mag, col, tex, lbl_dir in stress_specs:
            fp = face_centers[fk]
            cp = face_centers[ck]
            direction = normalize(fp)

            start      = fp + direction * mag
            start_comp = cp - direction * mag

            arrow      = stress_arrow(start, fp, col)
            arrow_comp = stress_arrow(start_comp, cp, col)

            lbl = MathTex(tex, color=col, font_size=FONT_SIZE)
            lbl.next_to(arrow.get_start(), lbl_dir, buff=0.1)
            self.add_fixed_orientation_mobjects(lbl)
            self.add(lbl, arrow, arrow_comp)

        # ── Direction cosine table (2D overlay, fixed in screen space) ────────
        # fmt: off
        table_data = [
            ["",  "x",  "y",  "z" ],
            ["X", f"l_1={L[0]:.2f}", f"m_1={L[1]:.2f}", f"n_1={L[2]:.2f}"],
            ["Y", f"l_2={M[0]:.2f}", f"m_2={M[1]:.2f}", f"n_2={M[2]:.2f}"],
            ["Z", f"l_3={N[0]:.2f}", f"m_3={N[1]:.2f}", f"n_3={N[2]:.2f}"],
        ]
        # fmt: on

        table = MathTable(
            [[MathTex(c, font_size=18) if c else MathTex("", font_size=18)
              for c in row]
             for row in table_data],
            include_outer_lines=True,
            line_config={"stroke_width": 1, "color": GRAY},
            element_to_mobject=lambda m: m,         # already MathTex
        )
        table.scale(0.55)

        title = Tex(r"\textbf{Table 2.2} Direction Cosines",
                    font_size=18, color=WHITE)
        title.next_to(table, UP, buff=0.1)

        table_group = VGroup(title, table)
        table_group.to_corner(UR, buff=0.15)

        self.add_fixed_in_frame_mobjects(table_group)

        # ── Gentle camera orbit so the scene is fully visible ─────────────────
        self.begin_ambient_camera_rotation(rate=0.15, about="theta")
        self.wait(3)
        self.stop_ambient_camera_rotation()