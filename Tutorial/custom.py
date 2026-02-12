from manim import *
import numpy as np
class Slider(MovingCameraScene):
    def construct(self):
        slider = Square(side_length=4, color=BLUE, fill_opacity=0.5)
        self.play(Create(slider))
        leftslider = Square(side_length=0.5, color=RED, fill_opacity=1).move_to(LEFT*2)
        self.play(Create(leftslider))
        center = leftslider.get_center()
        self.play(self.camera.frame.animate.move_to(center).set(width=5))
        self.interactive_embed()


# Peltion of the blade is not working, 
# so I will just make a simple polygon and 
# move the camera to it.
class CurveBlade(MovingCameraScene):
    def construct(self):
        blade = Polygon(ORIGIN, RIGHT, UP, color=GREEN, fill_opacity=0.5)
        # self.play(Create(blade))
        center = blade.get_center()
        self.cam_center = blade.get_center()
        v_line = Line(DOWN*3, UP*3, color=BLUE)
        self.add(v_line)
        h_line = Line(ORIGIN, RIGHT*3, color=RED)
        self.add(h_line)

        # inlet angle is 30 degrees, so we can calculate the point on the blade at that angle
        outlet_angle = 140 * DEGREES
        length = 100
        outlet_line = Line(RIGHT*3, [length * np.cos(outlet_angle), length * np.sin(outlet_angle), 0], color=YELLOW)
        self.add(outlet_line)

        inlet_angle = 210 * DEGREES
        inlet_line = Line(RIGHT*3, [length * np.cos(inlet_angle), length * np.sin(inlet_angle), 0], color=YELLOW)
        self.add(inlet_line)

        inlet_point = np.linalg.solve(inlet_line,outlet_line)
        outlet_point = np.linalg.solve(outlet_line,inlet_line)
        self.add(Dot(inlet_point, color=ORANGE))
        self.add(Dot(outlet_point, color=ORANGE))

    def blade(self):
        n_points = 120
        angles = np.linspace(0, 2 * PI, n_points)

        blade_points = [
            [
                self.cam_center[0] + self.get_cam_radius(theta) * np.cos(theta),
                self.cam_center[1] + self.get_cam_radius(theta) * np.sin(theta),
                0
            ]
            for theta in angles
        ]

        blade = Polygon(
            *blade_points,
            color=TEAL_D,
            fill_opacity=0.8,
            stroke_color=TEAL_B,
            stroke_width=2.5
        )

        return blade
    
    def get_cam_radius(self, theta):
        """Calculate cam radius at given angle with smooth profile"""
        self.max_variation = 0.6
        self.base_radius = 2.0
        variation = self.max_variation * (
            0.6 + 0.25 * np.sin(2 * theta) + 0.15 * np.sin(3 * theta)
        )
        return self.base_radius + variation


class Interactive4D(ThreeDScene):
    """Interactive 4D projection example (tesseract).

    RUN WITH:  manim -p --renderer=opengl custom.py Interactive4D

    - Uses a simple perspective projection from 4D -> 3D along the w-axis.
    - ValueTrackers control rotations in two 4D planes and projection depth.
    - In interactive mode: self.rot_xw, self.rot_yz, self.eye are accessible.
    """

    def construct(self):
        # Basic 3D axes and camera setup
        axes = ThreeDAxes()
        self.set_camera_orientation(phi=65 * DEGREES, theta=30 * DEGREES)
        self.add(axes)

        # Create 4D vertices for a unit tesseract (all combinations of ±1)
        self.verts4 = [np.array([x, y, z, w], dtype=float)
                       for x in (-1, 1)
                       for y in (-1, 1)
                       for z in (-1, 1)
                       for w in (-1, 1)]

        # Build edges: vertices that differ in exactly one coordinate
        self.edges = []
        for i, a in enumerate(self.verts4):
            for j, b in enumerate(self.verts4):
                if j <= i:
                    continue
                if np.sum(a != b) == 1:
                    self.edges.append((i, j))

        # Initial projection
        projected = [self.project(v) for v in self.verts4]

        # Create 3D visual objects using Dot3D for better OpenGL compatibility
        self.spheres = [Dot3D(point=p, color=BLUE, radius=0.08) for p in projected]
        self.lines = [Line3D(start=projected[i], end=projected[j], color=WHITE)
                      for (i, j) in self.edges]

        self.group = VGroup(*self.spheres, *self.lines)
        self.add(self.group)

        # ValueTrackers to control 4D rotations and projection distance
        self.rot_xw = ValueTracker(0.0)  # rotation in X-W plane
        self.rot_yz = ValueTracker(0.0)  # rotation in Y-Z plane
        self.eye = ValueTracker(4.0)     # projection distance along W

        # Updater rotates vertices in 4D then projects to 3D
        def updater(mob):
            theta = self.rot_xw.get_value()
            phi = self.rot_yz.get_value()
            E = self.eye.get_value()

            # Rotation in X-W plane
            R_xw = np.array([
                [np.cos(theta), 0, 0, -np.sin(theta)],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [np.sin(theta), 0, 0, np.cos(theta)]
            ])

            # Rotation in Y-Z plane
            R_yz = np.array([
                [1, 0, 0, 0],
                [0, np.cos(phi), -np.sin(phi), 0],
                [0, np.sin(phi), np.cos(phi), 0],
                [0, 0, 0, 1]
            ])

            R = R_xw @ R_yz
            pts3 = [self.project(R @ v, eye=E) for v in self.verts4]

            # update spheres
            for i, s in enumerate(self.spheres):
                s.move_to(pts3[i])

            # update lines
            for k, (i, j) in enumerate(self.edges):
                self.lines[k].put_start_and_end_on(pts3[i], pts3[j])

            return mob

        self.group.add_updater(updater)

        # Basic animation to demonstrate
        self.play(
            self.rot_xw.animate.set_value(PI / 6),
            self.rot_yz.animate.set_value(PI / 8),
            run_time=2
        )
        self.wait(0.5)

        # Interactive shell: use self.rot_xw.set_value(...), self.rot_yz.set_value(...), etc.
        self.interactive_embed()

    def project(self, v4, eye=4.0):
        """Perspective project from 4D -> 3D using 'eye' on the w-axis."""
        w = v4[3]
        denom = eye - w
        if abs(denom) < 1e-6:
            denom = np.sign(denom) * 1e-6 if denom != 0 else 1e-6
        factor = eye / denom
        return np.array([v4[0] * factor, v4[1] * factor, v4[2] * factor])


class FluidSimulation3D(ThreeDScene):
    """Interactive 3D fluid simulation with particles.

    RUN WITH:  manim -p --renderer=opengl custom.py FluidSimulation3D

    Features:
    - Particle-based fluid with gravity, damping, and collision
    - Interactive controls: self.gravity, self.damping, self.source_rate
    - Add particles with self.add_particles(n) in interactive mode
    """

    def construct(self):
        # Setup camera
        self.set_camera_orientation(phi=70 * DEGREES, theta=45 * DEGREES)

        # Container box
        box_size = 3.0
        self.box_size = box_size
        box = Cube(side_length=box_size, fill_opacity=0.05, stroke_width=1, stroke_color=WHITE)
        self.add(box)

        # Axes for reference
        axes = ThreeDAxes(
            x_range=[-2, 2, 1], y_range=[-2, 2, 1], z_range=[-2, 2, 1],
            x_length=4, y_length=4, z_length=4
        )
        self.add(axes)

        # Physics parameters as ValueTrackers
        self.gravity = ValueTracker(-9.8)
        self.damping = ValueTracker(0.98)
        self.source_rate = ValueTracker(5)  # particles per second
        self.dt = 0.02  # time step

        # Particle storage
        self.positions = []  # list of np.array [x, y, z]
        self.velocities = []  # list of np.array [vx, vy, vz]
        self.particles = VGroup()  # visual Dot3D objects
        self.add(self.particles)

        # Initialize with some particles at top
        self.spawn_particles(40)

        # Time tracker for spawning
        self.time_acc = 0.0
        self.last_spawn = 0.0

        # Main updater for physics
        def physics_updater(mob, dt):
            if dt == 0:
                return

            g = self.gravity.get_value()
            damp = self.damping.get_value()
            half_box = self.box_size / 2 - 0.1
            restitution = 0.6

            for i in range(len(self.positions)):
                # Apply gravity (in z direction)
                self.velocities[i][2] += g * self.dt

                # Update position
                self.positions[i] += self.velocities[i] * self.dt

                # Collision with box walls
                for axis in range(3):
                    if self.positions[i][axis] < -half_box:
                        self.positions[i][axis] = -half_box
                        self.velocities[i][axis] *= -restitution
                    elif self.positions[i][axis] > half_box:
                        self.positions[i][axis] = half_box
                        self.velocities[i][axis] *= -restitution

                # Apply damping
                self.velocities[i] *= damp

                # Update visual
                if i < len(self.particles):
                    self.particles[i].move_to(self.positions[i])

            # Spawn new particles based on rate
            self.time_acc += dt
            rate = self.source_rate.get_value()
            if rate > 0:
                spawn_interval = 1.0 / rate
                while self.time_acc - self.last_spawn > spawn_interval and len(self.positions) < 200:
                    self.spawn_particles(1)
                    self.last_spawn = self.time_acc

        self.particles.add_updater(physics_updater)

        # Initial animation - let it run
        self.wait(3)

        # Interactive embed for live control
        self.interactive_embed()

    def spawn_particles(self, n):
        """Spawn n particles at the top of the container."""
        half = self.box_size / 2 - 0.2
        for _ in range(n):
            # Random position at top
            x = np.random.uniform(-half * 0.5, half * 0.5)
            y = np.random.uniform(-half * 0.5, half * 0.5)
            z = half - 0.1

            pos = np.array([x, y, z])
            vel = np.array([
                np.random.uniform(-0.5, 0.5),
                np.random.uniform(-0.5, 0.5),
                np.random.uniform(-1, 0)
            ])

            self.positions.append(pos)
            self.velocities.append(vel)

            # Color based on velocity magnitude (blue = slow, red = fast)
            speed = np.linalg.norm(vel)
            color = interpolate_color(BLUE, RED, min(speed / 5, 1))
            particle = Dot3D(point=pos, radius=0.08, color=color)
            self.particles.add(particle)

    def add_particles(self, n=10):
        """Add n particles - call this in interactive mode."""
        self.spawn_particles(n)

    def reset_particles(self):
        """Clear all particles and start fresh."""
        self.positions.clear()
        self.velocities.clear()
        self.particles.submobjects.clear()
        self.spawn_particles(40)

    def set_gravity(self, g):
        """Set gravity value (negative = down)."""
        self.gravity.set_value(g)

    def set_damping(self, d):
        """Set damping (0-1, lower = more energy loss)."""
        self.damping.set_value(d)
