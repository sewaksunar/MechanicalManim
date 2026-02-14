from manim import *
import numpy as np


def closed_bezier(control_points):
    """Return a simple closed, smooth Bezier-like VMobject from anchor points.

    This helper closes the loop and uses Manim's `set_points_smoothly` so the
    resulting VMobject is created from cubic Bezier segments that interpolate
    the given anchor points. (Simple and easy to use.)
    """
    pts = np.asarray(control_points, dtype=float)
    if pts.ndim != 2 or pts.shape[1] != 2:
        raise ValueError("control_points must be an iterable of (x, y) pairs")
    if pts.shape[0] < 3:
        raise ValueError("Need at least 3 control points to form a closed curve")

    # make closed loop if needed
    if not np.allclose(pts[0], pts[-1]):
        pts = np.vstack([pts, pts[0]])

    pts3 = np.column_stack([pts[:, 0], pts[:, 1], np.zeros(pts.shape[0])])
    bez = VMobject()
    bez.set_points_smoothly(pts3)
    return bez

class PApproxFun(VMobject):
    pass

class CommplexElement(VMobject):
    def __init__(self, width=0.5, height=2, control_points=None, control_smoothness=24, irregularity=0.28, seed=42, **kwargs):
        super().__init__(**kwargs)

        # two ways to build a smooth 'blob':
        # 1) random radial perturbation (kept for compatibility)
        # 2) smooth blob from a few user-defined control points (Catmull–Rom)

        def irregular_circle(radius=2, irregularity=0.25, n_points=80, seed=None):
            """Return a VMobject shaped like an irregular circle (smooth closed blob).

            - irregularity: fraction of radius for radial perturbations (0 = perfect circle)
            - n_points: number of sample points around the circle (higher = smoother)
            - seed: optional RNG seed for deterministic shapes
            """
            rng = np.random.default_rng(seed)
            thetas = np.linspace(0, TAU, n_points, endpoint=False)

            # generate low-frequency radial noise and smooth it to avoid sharp spikes
            raw = rng.uniform(-1.0, 1.0, size=n_points)
            kernel_size = max(3, n_points // 12)
            kernel = np.ones(kernel_size) / kernel_size
            smooth_noise = np.convolve(raw, kernel, mode="same")
            if np.max(np.abs(smooth_noise)) != 0:
                smooth_noise = smooth_noise / np.max(np.abs(smooth_noise))

            radii = radius * (1 + irregularity * smooth_noise)
            pts = np.column_stack([radii * np.cos(thetas), radii * np.sin(thetas), np.zeros_like(thetas)])
            pts = np.vstack([pts, pts[0]])  # close the loop

            blob = VMobject()
            blob.set_points_smoothly(pts)
            return blob

        def _catmull_rom_point(p0, p1, p2, p3, t):
            """Single-point Catmull–Rom (centripetal/standard with tension=0.5)."""
            t2 = t * t
            t3 = t2 * t
            return 0.5 * (
                (2 * p1)
                + (-p0 + p2) * t
                + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                + (-p0 + 3 * p1 - 3 * p2 + p3) * t3
            )

        def smooth_blob_from_control_points(control_points, n_points_per_segment=24):
            """Build a smooth, closed VMobject from a small list of control points.

            - control_points: iterable of (x, y) coordinates (minimum 3 points)
            - n_points_per_segment: interpolation density between control points
            """
            pts = np.asarray(control_points, dtype=float)
            if pts.ndim != 2 or pts.shape[1] != 2:
                raise ValueError("control_points must be an iterable of (x, y) pairs")
            if pts.shape[0] < 3:
                raise ValueError("Need at least 3 control points for a closed smooth blob")

            n = pts.shape[0]
            samples = []
            # closed curve: wrap indices
            for i in range(n):
                p0 = pts[(i - 1) % n]
                p1 = pts[i]
                p2 = pts[(i + 1) % n]
                p3 = pts[(i + 2) % n]
                for k in range(n_points_per_segment):
                    t = k / n_points_per_segment
                    samples.append(_catmull_rom_point(p0, p1, p2, p3, t))

            samples = np.asarray(samples)
            # ensure closed by appending first sample
            samples = np.vstack([samples, samples[0]])
            pts3 = np.column_stack([samples[:, 0], samples[:, 1], np.zeros(samples.shape[0])])

            blob = VMobject()
            blob.set_points_smoothly(pts3)
            return blob

        # `closed_bezier` is now a module-level helper (see top of file).

        # choose which generator to use: explicit control points (few points) OR random radial noise
        control_pts = control_points
        if control_pts is not None:
            # user-provided control points -> smooth curve through those points
            self.complex_domain = smooth_blob_from_control_points(control_pts, n_points_per_segment=control_smoothness)
        else:
            # fallback to the randomized irregular circle
            self.complex_domain = irregular_circle(radius=2, irregularity=irregularity, n_points=120, seed=seed)

        self.complex_domain.set_fill(RED, opacity=0.35)
        self.complex_domain.set_stroke(RED, width=3)
        self.add(self.complex_domain)


class FiniteElement(VGroup):
    """Approximates a complex domain using simple geometric shapes (triangles, quads, hexagons).
    
    This class implements finite element mesh generation, which is essential in numerical
    methods for approximating solutions to PDEs over complex domains.
    """
    
    def __init__(
        self,
        base_domain=None,
        element_type="triangle",  # "triangle", "quad", "hex"
        num_radial=6,
        num_angular=16,
        show_mesh=True,
        show_domain=True,
        mesh_color=YELLOW,
        domain_color=RED,
        mesh_opacity=0.3,
        stroke_width=1.5,
        adaptive=False,  # Adaptive mesh refinement (finer near boundary)
        **kwargs
    ):
        """
        Create a finite element mesh approximation of a complex domain.
        
        Parameters:
        -----------
        base_domain : CommplexElement or VMobject
            The complex domain to approximate. If None, creates a default irregular blob.
        element_type : str
            Type of finite elements: "triangle", "quad", or "hex"
        num_radial : int
            Number of radial divisions from center to boundary
        num_angular : int
            Number of angular divisions around the domain
        show_mesh : bool
            Whether to display the mesh elements
        show_domain : bool
            Whether to display the original domain boundary
        mesh_color : Color
            Color for mesh elements
        domain_color : Color
            Color for domain boundary
        mesh_opacity : float
            Opacity of mesh elements (0-1)
        stroke_width : float
            Width of mesh element edges
        adaptive : bool
            If True, creates finer mesh near the boundary
        """
        super().__init__(**kwargs)
        
        self.element_type = element_type
        self.num_radial = num_radial
        self.num_angular = num_angular
        self.adaptive = adaptive
        
        # If no base domain provided, create a default one
        if base_domain is None:
            base_domain = CommplexElement(irregularity=0.25, seed=42)
        
        self.base_domain = base_domain
        
        # Generate mesh elements
        elements = self._generate_mesh()
        
        # Style the elements
        for elem in elements:
            elem.set_fill(mesh_color, opacity=mesh_opacity)
            elem.set_stroke(mesh_color, width=stroke_width)
        
        # Add elements to the group
        if show_mesh:
            self.add(*elements)
        
        # Add the original domain boundary if requested
        if show_domain:
            domain_boundary = self.base_domain.copy()
            domain_boundary.set_fill(opacity=0)
            domain_boundary.set_stroke(domain_color, width=stroke_width + 1)
            self.add(domain_boundary)
        
        self.mesh_elements = elements
    
    def _generate_mesh(self):
        """Generate mesh elements based on the selected type."""
        if self.element_type == "triangle":
            return self._generate_triangular_mesh()
        elif self.element_type == "quad":
            return self._generate_quad_mesh()
        elif self.element_type == "hex":
            return self._generate_hex_mesh()
        else:
            raise ValueError(f"Unknown element type: {self.element_type}")
    
    def _sample_domain_boundary(self, num_samples=200):
        """Sample points uniformly along the domain boundary."""
        domain_points = self.base_domain.complex_domain.get_all_points()
        
        # Uniformly resample
        if len(domain_points) > num_samples:
            indices = np.linspace(0, len(domain_points) - 1, num_samples, dtype=int)
            sampled = domain_points[indices]
        else:
            sampled = domain_points
        
        return sampled
    
    def _get_domain_center(self):
        """Compute the approximate center (centroid) of the domain."""
        boundary = self._sample_domain_boundary(50)
        return np.mean(boundary, axis=0)
    
    def _point_in_polygon(self, point, polygon_points):
        """Check if a 2D point is inside a polygon using ray casting algorithm."""
        x, y = point[0], point[1]
        n = len(polygon_points)
        inside = False
        
        p1x, p1y = polygon_points[0][0], polygon_points[0][1]
        for i in range(1, n + 1):
            p2x, p2y = polygon_points[i % n][0], polygon_points[i % n][1]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def _get_radial_profile(self, angle, num_samples=200):
        """Get the radius of the domain at a specific angle by ray casting to boundary."""
        center = self._get_domain_center()
        boundary = self._sample_domain_boundary(num_samples)
        
        # Ray direction
        direction = np.array([np.cos(angle), np.sin(angle), 0])
        
        # Cast ray and find intersection with boundary
        max_radius = 0
        
        # Find the furthest boundary point in this direction
        for point in boundary:
            vec = point - center
            # Get angle of this point
            point_angle = np.arctan2(vec[1], vec[0])
            
            # Check if this point is close to our desired angle
            angle_diff = abs((point_angle - angle + np.pi) % (2 * np.pi) - np.pi)
            
            # Accept points in a narrow cone around our direction
            if angle_diff < TAU / (2 * num_samples):
                radius = np.linalg.norm(vec[:2])
                if radius > max_radius:
                    max_radius = radius
        
        # Fallback if no points found: sample along the ray
        if max_radius == 0:
            for r in np.linspace(0.1, 5, 50):
                test_point = center + direction * r
                if not self._point_in_polygon(test_point, boundary):
                    max_radius = r - 0.1
                    break
            if max_radius == 0:
                max_radius = 2.0  # Final fallback
        
        return max_radius
    
    def _clip_point_to_boundary(self, point):
        """Clip a point to be inside the domain boundary."""
        center = self._get_domain_center()
        boundary = self._sample_domain_boundary(200)
        
        # If point is already inside, return it
        if self._point_in_polygon(point, boundary):
            return point
        
        # Find the closest boundary point
        min_dist = float('inf')
        closest_point = point
        
        for boundary_pt in boundary:
            dist = np.linalg.norm(point[:2] - boundary_pt[:2])
            if dist < min_dist:
                min_dist = dist
                closest_point = boundary_pt
        
        return closest_point
    
    def _generate_triangular_mesh(self):
        """Generate triangular finite elements using radial subdivision."""
        elements = []
        center = self._get_domain_center()
        boundary = self._sample_domain_boundary(200)
        
        # Adaptive mesh: use non-uniform radial spacing
        if self.adaptive:
            # More elements near boundary (quadratic spacing)
            radial_fracs = [(r / self.num_radial) ** 0.7 for r in range(self.num_radial + 1)]
        else:
            radial_fracs = [r / self.num_radial for r in range(self.num_radial + 1)]
        
        # Create radial layers
        for r in range(self.num_radial):
            r_inner = radial_fracs[r]
            r_outer = radial_fracs[r + 1]
            
            for a in range(self.num_angular):
                angle1 = a * TAU / self.num_angular
                angle2 = (a + 1) * TAU / self.num_angular
                angle_mid = (angle1 + angle2) / 2
                
                # Get radius at both angles
                radius1 = self._get_radial_profile(angle1)
                radius2 = self._get_radial_profile(angle2)
                
                # Create vertices
                dir1 = np.array([np.cos(angle1), np.sin(angle1), 0])
                dir2 = np.array([np.cos(angle2), np.sin(angle2), 0])
                
                if r == 0:
                    # Inner ring - triangles from center
                    v1 = center
                    v2 = center + dir1 * radius1 * r_outer
                    v3 = center + dir2 * radius2 * r_outer
                    
                    # Clip vertices to boundary
                    v2 = self._clip_point_to_boundary(v2)
                    v3 = self._clip_point_to_boundary(v3)
                    
                    # Check if all vertices are valid
                    if self._point_in_polygon(v1, boundary) and \
                       self._point_in_polygon(v2, boundary) and \
                       self._point_in_polygon(v3, boundary):
                        tri = Polygon(v1, v2, v3)
                        elements.append(tri)
                else:
                    # Outer rings - split each quad into two triangles
                    v1 = center + dir1 * radius1 * r_inner
                    v2 = center + dir1 * radius1 * r_outer
                    v3 = center + dir2 * radius2 * r_outer
                    v4 = center + dir2 * radius2 * r_inner
                    
                    # Clip all vertices to boundary
                    v1 = self._clip_point_to_boundary(v1)
                    v2 = self._clip_point_to_boundary(v2)
                    v3 = self._clip_point_to_boundary(v3)
                    v4 = self._clip_point_to_boundary(v4)
                    
                    # Check if vertices form valid triangles inside boundary
                    # First triangle
                    if self._point_in_polygon(v1, boundary) and \
                       self._point_in_polygon(v2, boundary) and \
                       self._point_in_polygon(v3, boundary):
                        tri1 = Polygon(v1, v2, v3)
                        elements.append(tri1)
                    
                    # Second triangle
                    if self._point_in_polygon(v1, boundary) and \
                       self._point_in_polygon(v3, boundary) and \
                       self._point_in_polygon(v4, boundary):
                        tri2 = Polygon(v1, v3, v4)
                        elements.append(tri2)
        
        return elements
    
    def _generate_quad_mesh(self):
        """Generate quadrilateral finite elements."""
        elements = []
        center = self._get_domain_center()
        boundary = self._sample_domain_boundary(200)
        
        # Adaptive mesh spacing
        if self.adaptive:
            radial_fracs = [(r / self.num_radial) ** 0.7 for r in range(self.num_radial + 1)]
        else:
            radial_fracs = [r / self.num_radial for r in range(self.num_radial + 1)]
        
        for r in range(self.num_radial):
            r_inner = radial_fracs[r]
            r_outer = radial_fracs[r + 1]
            
            for a in range(self.num_angular):
                angle1 = a * TAU / self.num_angular
                angle2 = (a + 1) * TAU / self.num_angular
                
                # Get radii at both angles
                radius1 = self._get_radial_profile(angle1)
                radius2 = self._get_radial_profile(angle2)
                
                # Create quad vertices
                dir1 = np.array([np.cos(angle1), np.sin(angle1), 0])
                dir2 = np.array([np.cos(angle2), np.sin(angle2), 0])
                
                v1 = center + dir1 * radius1 * r_inner
                v2 = center + dir1 * radius1 * r_outer
                v3 = center + dir2 * radius2 * r_outer
                v4 = center + dir2 * radius2 * r_inner
                
                # Clip all vertices to boundary
                v1 = self._clip_point_to_boundary(v1)
                v2 = self._clip_point_to_boundary(v2)
                v3 = self._clip_point_to_boundary(v3)
                v4 = self._clip_point_to_boundary(v4)
                
                # Only add quad if all vertices are inside boundary
                if self._point_in_polygon(v1, boundary) and \
                   self._point_in_polygon(v2, boundary) and \
                   self._point_in_polygon(v3, boundary) and \
                   self._point_in_polygon(v4, boundary):
                    quad = Polygon(v1, v2, v3, v4)
                    elements.append(quad)
        
        return elements
    
    def _generate_hex_mesh(self):
        """Generate hexagonal finite elements (honeycomb pattern)."""
        elements = []
        center = self._get_domain_center()
        boundary = self._sample_domain_boundary(200)
        avg_radius = np.mean([np.linalg.norm(p[:2] - center[:2]) for p in boundary])
        
        # Hexagon size based on desired mesh density
        hex_size = avg_radius / (self.num_radial * 1.8)
        
        # Generate hexagonal grid using axial coordinates
        for q in range(-self.num_radial - 2, self.num_radial + 3):
            for r in range(-self.num_radial - 2, self.num_radial + 3):
                # Axial to Cartesian conversion for hexagonal grid
                x = hex_size * (3/2 * q)
                y = hex_size * (np.sqrt(3)/2 * q + np.sqrt(3) * r)
                hex_center = center + np.array([x, y, 0])
                
                # Check if hexagon center is inside the boundary
                if not self._point_in_polygon(hex_center, boundary):
                    continue
                
                # Create hexagon vertices
                hex_vertices = []
                for i in range(6):
                    angle = TAU / 6 * i + TAU / 12  # Rotate for flat-top orientation
                    vertex = hex_center + np.array([
                        hex_size * np.cos(angle),
                        hex_size * np.sin(angle),
                        0
                    ])
                    hex_vertices.append(vertex)
                
                # Check if at least 4 vertices are inside (majority)
                # This allows partial hexagons near the boundary
                inside_count = sum(1 for v in hex_vertices if self._point_in_polygon(v, boundary))
                
                if inside_count >= 4:
                    hexagon = Polygon(*hex_vertices)
                    elements.append(hexagon)
        
        return elements
    
    def color_by_function(self, func, color_range=[BLUE, RED], opacity=0.7):
        """
        Color mesh elements based on a scalar function (useful for visualizing solutions).
        
        Parameters:
        -----------
        func : callable
            Function that takes (x, y) and returns a scalar value
        color_range : list
            [min_color, max_color] for the gradient
        opacity : float
            Opacity for the colored elements
        
        Returns:
        --------
        self : for method chaining
        
        Example:
        --------
        # Color by distance from origin
        mesh.color_by_function(lambda x, y: np.sqrt(x**2 + y**2))
        """
        values = []
        for elem in self.mesh_elements:
            center = elem.get_center()
            value = func(center[0], center[1])
            values.append(value)
        
        # Normalize values to [0, 1]
        vmin, vmax = min(values), max(values)
        if vmax - vmin > 1e-10:
            norm_values = [(v - vmin) / (vmax - vmin) for v in values]
        else:
            norm_values = [0.5] * len(values)
        
        # Apply gradient colors
        for elem, norm_val in zip(self.mesh_elements, norm_values):
            color = interpolate_color(color_range[0], color_range[1], norm_val)
            elem.set_fill(color, opacity=opacity)
        
        return self
    
    def highlight_boundary_elements(self, color=YELLOW, opacity=0.8):
        """Highlight mesh elements that are on or near the boundary."""
        center = self._get_domain_center()
        boundary = self._sample_domain_boundary(100)
        max_radius = max([np.linalg.norm(p[:2] - center[:2]) for p in boundary])
        
        for elem in self.mesh_elements:
            elem_center = elem.get_center()
            dist = np.linalg.norm(elem_center[:2] - center[:2])
            
            # Elements in outer 20% are considered boundary elements
            if dist > max_radius * 0.8:
                elem.set_fill(color, opacity=opacity)
        
        return self
    
    def get_refinement_animation(self, new_radial=None, new_angular=None, run_time=2):
        """
        Create an animation showing mesh refinement.
        
        Parameters:
        -----------
        new_radial : int
            New number of radial divisions (higher = finer mesh)
        new_angular : int
            New number of angular divisions
        run_time : float
            Animation duration
        
        Returns:
        --------
        AnimationGroup : Manim animation
        """
        if new_radial is None:
            new_radial = self.num_radial * 2
        if new_angular is None:
            new_angular = self.num_angular * 2
        
        # Create refined mesh
        refined_mesh = FiniteElement(
            base_domain=self.base_domain,
            element_type=self.element_type,
            num_radial=new_radial,
            num_angular=new_angular,
            show_domain=False,
            mesh_color=self.mesh_elements[0].get_fill_color(),
            mesh_opacity=self.mesh_elements[0].get_fill_opacity(),
            stroke_width=self.mesh_elements[0].get_stroke_width(),
        )
        
        return Transform(self, refined_mesh, run_time=run_time)


class Domain2D(Scene):
    """Example scene demonstrating the FiniteElement class with various mesh types."""
    
    def construct(self):
        # Create a custom complex domain
        control_pts = [
            (2.0, 0.0),
            (1.0, 1.6),
            (-1.2, 1.4),
            (-2.0, 0.1),
            (-1.0, -1.2),
            (1.4, -1.6),
        ]
        complex_domain = CommplexElement(control_points=control_pts, control_smoothness=32)
        
        # Example 1: Triangular mesh
        tri_mesh = FiniteElement(
            base_domain=complex_domain,
            element_type="triangle",
            num_radial=4,
            num_angular=12,
            mesh_color=YELLOW,
            show_domain=True,
        )
        tri_mesh.scale(0.8).shift(LEFT * 4)
        
        # Example 2: Quadrilateral mesh
        quad_mesh = FiniteElement(
            base_domain=complex_domain,
            element_type="quad",
            num_radial=5,
            num_angular=14,
            mesh_color=BLUE,
            show_domain=True,
        )
        quad_mesh.scale(0.8)
        
        # Example 3: Hexagonal mesh
        hex_mesh = FiniteElement(
            base_domain=complex_domain,
            element_type="hex",
            num_radial=4,
            num_angular=12,
            mesh_color=GREEN,
            show_domain=True,
        )
        hex_mesh.scale(0.8).shift(RIGHT * 4)
        
        # Add labels
        tri_label = Text("Triangular Mesh", font_size=20).next_to(tri_mesh, UP)
        quad_label = Text("Quad Mesh", font_size=20).next_to(quad_mesh, UP)
        hex_label = Text("Hexagonal Mesh", font_size=20).next_to(hex_mesh, UP)
        
        self.add(tri_mesh, quad_mesh, hex_mesh)
        self.add(tri_label, quad_label, hex_label)


class FunctionVisualization(Scene):
    """Example scene showing how to visualize functions on finite element meshes."""
    
    def construct(self):
        # Create domain
        domain = CommplexElement(irregularity=0.3, seed=123)
        
        # Create mesh
        mesh = FiniteElement(
            base_domain=domain,
            element_type="triangle",
            num_radial=6,
            num_angular=18,
            show_domain=True,
            domain_color=WHITE,
        )
        
        # Color by a function (e.g., distance from origin)
        mesh.color_by_function(
            lambda x, y: np.sqrt(x**2 + y**2),
            color_range=[BLUE, RED],
            opacity=0.8
        )
        
        title = Text("Heat Distribution", font_size=32).to_edge(UP)
        
        self.add(mesh, title)


class AdaptiveMesh(Scene):
    """Example showing adaptive mesh refinement."""
    
    def construct(self):
        # Create domain
        domain = CommplexElement(irregularity=0.25, seed=42)
        
        # Coarse mesh
        coarse = FiniteElement(
            base_domain=domain,
            element_type="quad",
            num_radial=3,
            num_angular=10,
            mesh_color=YELLOW,
            adaptive=False,
        )
        coarse.shift(LEFT * 3.5)
        
        # Adaptive mesh (finer near boundary)
        adaptive = FiniteElement(
            base_domain=domain,
            element_type="quad",
            num_radial=5,
            num_angular=16,
            mesh_color=GREEN,
            adaptive=True,
        )
        adaptive.shift(RIGHT * 3.5)
        
        coarse_label = Text("Uniform Mesh", font_size=24).next_to(coarse, UP)
        adaptive_label = Text("Adaptive Mesh", font_size=24).next_to(adaptive, UP)
        
        self.add(coarse, adaptive, coarse_label, adaptive_label)