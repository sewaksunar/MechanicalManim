from manim import *

# ── Constants ────────────────────────────────────────────────────────────────
CUBE_SIDE   = 1.0
CUBE_COLOR  = BLUE
STROKE_COL  = RED
FONT_SIZE   = 24
ROTATION    = PI / 3          # applied to the whole cube group

# Normal → rotation needed to orient a flat Circle perpendicular to that normal
_FACE_ROTATIONS: dict[tuple, tuple[float, np.ndarray]] = {
    tuple(LEFT):  (-PI / 2, UP),
    tuple(RIGHT): ( PI / 2, UP),
    tuple(UP):    (-PI / 2, RIGHT),
    tuple(DOWN):  ( PI / 2, RIGHT),
    tuple(IN):    ( PI,     UP),
    # OUT is the default Circle orientation (facing camera), so no rotation needed
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def face_disk(center: np.ndarray, normal: np.ndarray, color: str) -> Circle:
    """Small filled circle sitting on a cube face, oriented along *normal*."""
    disk = Circle(radius=0.05, color=color, fill_opacity=1)
    disk.move_to(center)
    key = tuple(np.round(normal).astype(int))
    if key in _FACE_ROTATIONS:
        angle, axis = _FACE_ROTATIONS[key]
        disk.rotate(angle, axis=axis)
    return disk


def stress_arrow(start: np.ndarray, end: np.ndarray, color: str) -> Arrow3D:
    """Arrow3D pointing from *start* to *end* in the given color."""
    return Arrow3D(start=start, end=end, color=color, resolution=8)


# ── Scene ─────────────────────────────────────────────────────────────────────
class MyAxes(ThreeDScene):
    def construct(self):
        # ── Axes ──────────────────────────────────────────────────────────────
        axes = ThreeDAxes(
            x_range=[-5, 5, 1], y_range=[-5, 5, 1], z_range=[-5, 5, 1],
            x_length=4, y_length=4, z_length=4,
        )
        self.set_camera_orientation(phi=60 * DEGREES, theta=30 * DEGREES, zoom=2)
        self.add(axes)

        x_label = MathTex("x").next_to(axes.x_axis.get_end(), RIGHT)
        y_label = MathTex("y").next_to(axes.y_axis.get_end(), UP)
        z_label = MathTex("z").next_to(axes.z_axis.get_end(), IN + LEFT)
        self.add_fixed_orientation_mobjects(x_label, y_label, z_label)

        # ── Cube + face markers ───────────────────────────────────────────────
        cube = Cube(
            side_length=CUBE_SIDE,
            fill_opacity=0.5,
            fill_color=CUBE_COLOR,
            stroke_color=STROKE_COL,
            stroke_width=2,
        )

        half = CUBE_SIDE / 2
        face_specs = [
            (LEFT,  RED),
            (RIGHT, RED),
            (UP,    GREEN),
            (DOWN,  GREEN),
            (OUT,   BLUE),
            (IN,    BLUE),
        ]
        face_dots = VGroup(*[
            face_disk(direction * half, direction, color)
            for direction, color in face_specs
        ])

        # Unpack for direct access by name
        (left_dot, right_dot,
         top_dot,  bottom_dot,
         front_dot, back_dot) = face_dots

        center_dot = Dot(ORIGIN, color=YELLOW, radius=0.05, fill_opacity=1)

        # Rotate the whole group once instead of rotating each part separately
        cube_group = VGroup(cube, center_dot, face_dots)
        cube_group.rotate(ROTATION, axis=Z_AXIS)

        # ── Reference line (computed after rotation) ──────────────────────────
        line = Line(right_dot.get_center(), cube.get_center(),
                    color=YELLOW, stroke_width=2)

        self.add(line, cube_group)

        # ── Stress-vector builder ─────────────────────────────────────────────
        def add_stress(
            face_dot_pos: np.ndarray,
            face_dot_pos_comp: np.ndarray,
            cube_center: np.ndarray,
            magnitude: float,
            color: str,
            label_tex: str,
            label_direction: np.ndarray,
        ):
            """
            Draw a principal stress arrow pointing *toward* a face dot and its
            complement on the opposite face, then attach a fixed-orientation label.
            """
            direction = normalize(face_dot_pos - cube_center)

            # Primary arrow (tail outside → tip at face)
            start = face_dot_pos + direction * magnitude
            arrow = stress_arrow(start, face_dot_pos, color)

            # Complementary arrow on opposite face
            start_comp = face_dot_pos_comp - direction * magnitude
            arrow_comp = stress_arrow(start_comp, face_dot_pos_comp, color)

            label = MathTex(label_tex, color=color, font_size=FONT_SIZE).next_to(
                arrow.get_start(), label_direction, buff=0.1
            )
            self.add_fixed_orientation_mobjects(label)
            self.add(label, arrow, arrow_comp)

        c = cube.get_center()

        add_stress(right_dot.get_center(),  left_dot.get_center(),   c, 1.0, RED,   r"\sigma_{xx}", RIGHT)
        add_stress(top_dot.get_center(),    bottom_dot.get_center(), c, 0.5, GREEN, r"\sigma_{yy}", LEFT)
        add_stress(front_dot.get_center(),  back_dot.get_center(),   c, 0.8, BLUE,  r"\sigma_{zz}", UP)