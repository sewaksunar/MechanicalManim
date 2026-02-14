from manim import *
import numpy as np
from scipy.spatial import Delaunay

def closed_bezier(control_points):
    """Return a simple closed, smooth Bezier-like VMobject from anchor points."""
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


class DelaunayMesh(VGroup):
    """Custom Delaunay triangulation mesh generator for 2D domains."""
    
    def __init__(
        self,
        base_domain,
        target_element_size=0.35,
        mesh_color=GREEN,
        mesh_stroke_width=1.5,
        show_domain=True,
        boundary_samples=200,
        interior_density=1.0,
        seed=42,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.base_domain = base_domain
        self.target_element_size = target_element_size
        self.mesh_color = mesh_color
        self.mesh_stroke_width = mesh_stroke_width
        self.show_domain = show_domain
        self.boundary_samples = boundary_samples
        self.interior_density = interior_density
        self.seed = seed
        
        self._generate_mesh()
    
    def _sample_boundary_points(self):
        """Extract points along the domain boundary."""
        # Get points from the VMobject
        boundary_pts = []
        
        # Sample points uniformly along the curve
        n_samples = self.boundary_samples
        for i in range(n_samples):
            alpha = i / n_samples
            point = self.base_domain.point_from_proportion(alpha)
            boundary_pts.append(point[:2])  # Only x, y coordinates
        
        return np.array(boundary_pts)
    
    def _point_in_polygon(self, point, polygon_points):
        """Check if a point is inside a polygon using ray casting."""
        x, y = point
        n = len(polygon_points)
        inside = False
        
        p1x, p1y = polygon_points[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon_points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def _generate_interior_points(self, boundary_pts):
        """Generate random points inside the domain."""
        # Get bounding box
        min_x, min_y = boundary_pts.min(axis=0)
        max_x, max_y = boundary_pts.max(axis=0)
        
        # Estimate number of interior points based on area and target element size
        width = max_x - min_x
        height = max_y - min_y
        area = width * height * 0.7  # Rough estimate
        n_interior = int(area / (self.target_element_size ** 2) * self.interior_density)
        
        # Generate random points and filter those inside the domain
        rng = np.random.default_rng(self.seed)
        interior_pts = []
        attempts = 0
        max_attempts = n_interior * 10
        
        while len(interior_pts) < n_interior and attempts < max_attempts:
            x = rng.uniform(min_x, max_x)
            y = rng.uniform(min_y, max_y)
            
            if self._point_in_polygon([x, y], boundary_pts):
                interior_pts.append([x, y])
            
            attempts += 1
        
        return np.array(interior_pts) if interior_pts else np.empty((0, 2))
    
    def _generate_mesh(self):
        """Generate the Delaunay triangulation mesh."""
        # Sample boundary points
        boundary_pts = self._sample_boundary_points()
        
        # Generate interior points
        interior_pts = self._generate_interior_points(boundary_pts)
        
        # Combine all points
        if len(interior_pts) > 0:
            all_points = np.vstack([boundary_pts, interior_pts])
        else:
            all_points = boundary_pts
        
        # Perform Delaunay triangulation
        tri = Delaunay(all_points)
        
        # Filter triangles to keep only those inside the domain
        valid_triangles = []
        for simplex in tri.simplices:
            # Check if triangle centroid is inside domain
            triangle_pts = all_points[simplex]
            centroid = triangle_pts.mean(axis=0)
            
            if self._point_in_polygon(centroid, boundary_pts):
                valid_triangles.append(simplex)
        
        # Create mesh VMobjects
        if self.show_domain:
            domain_copy = self.base_domain.copy()
            domain_copy.set_fill(opacity=0).set_stroke(self.mesh_color, width=3)
            self.add(domain_copy)
        
        # Create triangle edges
        for simplex in valid_triangles:
            triangle_pts = all_points[simplex]
            
            # Create triangle polygon
            triangle = Polygon(
                *[np.append(pt, 0) for pt in triangle_pts],
                stroke_width=self.mesh_stroke_width,
                stroke_color=self.mesh_color,
                fill_opacity=0
            )
            self.add(triangle)


class CommplexElement(VMobject):
    def __init__(self, width=0.5, height=2, control_points=None, control_smoothness=24, 
                 irregularity=0.28, seed=42, **kwargs):
        super().__init__(**kwargs)
        
        def irregular_circle(radius=2, irregularity=0.25, n_points=80, seed=None):
            """Return a VMobject shaped like an irregular circle (smooth closed blob)."""
            rng = np.random.default_rng(seed)
            thetas = np.linspace(0, TAU, n_points, endpoint=False)
            
            raw = rng.uniform(-1.0, 1.0, size=n_points)
            kernel_size = max(3, n_points // 12)
            kernel = np.ones(kernel_size) / kernel_size
            smooth_noise = np.convolve(raw, kernel, mode="same")
            
            if np.max(np.abs(smooth_noise)) != 0:
                smooth_noise = smooth_noise / np.max(np.abs(smooth_noise))
            
            radii = radius * (1 + irregularity * smooth_noise)
            pts = np.column_stack([
                radii * np.cos(thetas),
                radii * np.sin(thetas),
                np.zeros_like(thetas)
            ])
            pts = np.vstack([pts, pts[0]])
            
            blob = VMobject()
            blob.set_points_smoothly(pts)
            return blob
        
        def _catmull_rom_point(p0, p1, p2, p3, t):
            """Single-point Catmull–Rom interpolation."""
            t2 = t * t
            t3 = t2 * t
            return 0.5 * (
                (2 * p1) +
                (-p0 + p2) * t +
                (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                (-p0 + 3 * p1 - 3 * p2 + p3) * t3
            )
        
        def smooth_blob_from_control_points(control_points, n_points_per_segment=24):
            """Build a smooth, closed VMobject from control points."""
            pts = np.asarray(control_points, dtype=float)
            if pts.ndim != 2 or pts.shape[1] != 2:
                raise ValueError("control_points must be an iterable of (x, y) pairs")
            if pts.shape[0] < 3:
                raise ValueError("Need at least 3 control points")
            
            n = pts.shape[0]
            samples = []
            
            for i in range(n):
                p0 = pts[(i - 1) % n]
                p1 = pts[i]
                p2 = pts[(i + 1) % n]
                p3 = pts[(i + 2) % n]
                
                for k in range(n_points_per_segment):
                    t = k / n_points_per_segment
                    samples.append(_catmull_rom_point(p0, p1, p2, p3, t))
            
            samples = np.asarray(samples)
            samples = np.vstack([samples, samples[0]])
            pts3 = np.column_stack([samples[:, 0], samples[:, 1], np.zeros(samples.shape[0])])
            
            blob = VMobject()
            blob.set_points_smoothly(pts3)
            return blob
        
        # Choose generator
        if control_points is not None:
            self.complex_domain = smooth_blob_from_control_points(
                control_points, 
                n_points_per_segment=control_smoothness
            )
        else:
            self.complex_domain = irregular_circle(
                radius=2, 
                irregularity=irregularity, 
                n_points=120, 
                seed=seed
            )
        
        self.complex_domain.set_fill(RED, opacity=0.35)
        self.complex_domain.set_stroke(RED, width=3)
        self.add(self.complex_domain)


class Domain2D(MovingCameraScene):
    def construct(self):
        # Build a smooth blob from user-defined control points
        control_pts = [
            (2.0, 0.0),
            (1.0, 1.6),
            (-1.2, 1.4),
            (-2.0, 0.1),
            (-1.0, -1.2),
            (1.4, -1.6),
        ]
        
        complex_domain = CommplexElement(control_points=control_pts, control_smoothness=32)
        complex_domain.set_stroke(BLUE, width=3).move_to(ORIGIN)
        
        complex_domain_stroke = complex_domain.complex_domain.copy().set_fill(
            opacity=0
        ).set_stroke(BLUE, width=3)
        
        self.add(complex_domain, complex_domain_stroke)
        
        # Label with updater
        tex = Tex("Complex Domain", color=BLUE).next_to(complex_domain, UP)
        
        def _update_tex(mobj):
            mobj.next_to(complex_domain, UP)
        
        tex.add_updater(_update_tex)
        self.add(tex)
        
        self.play(Write(tex), run_time=2)
        
        # Animate movement
        self.play(
            complex_domain_stroke.animate.move_to(RIGHT * 3),
            complex_domain.animate.move_to(LEFT * 3),
            run_time=3,
        )
        
        # Stop updater
        tex.remove_updater(_update_tex)
        tex.next_to(complex_domain, UP)
        
        # Camera zoom
        self.camera.frame.save_state()
        
        aspect = self.camera.frame.get_width() / self.camera.frame.get_height()
        target_width = max(
            complex_domain_stroke.get_width(),
            complex_domain_stroke.get_height() * aspect,
        ) * 1.2
        
        self.play(
            self.camera.frame.animate.move_to(
                complex_domain_stroke.get_center()
            ).set(width=target_width),
            run_time=3,
        )
        
        # Create custom Delaunay mesh
        delaunay_mesh = DelaunayMesh(
            base_domain=complex_domain_stroke,
            target_element_size=0.35,
            mesh_color=GREEN,
            show_domain=True,
        )
        
        self.play(Create(delaunay_mesh),complex_domain_stroke.animate.set_stroke(width=0), run_time=4)
        self.wait(2)