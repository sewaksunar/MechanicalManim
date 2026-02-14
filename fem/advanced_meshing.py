"""
Advanced Meshing Implementation - Best Practices
Includes: Delaunay triangulation, boundary layers, quality metrics
"""

from manim import *
import numpy as np
from scipy.spatial import Delaunay as ScipyDelaunay
from scipy.spatial import ConvexHull


class AdvancedFiniteElement(VGroup):
    """
    Advanced finite element mesh generator with multiple algorithms.
    
    Implements:
    - Delaunay triangulation (optimal quality)
    - Boundary layer meshing (for CFD/gradient capture)
    - Quality metric calculation and visualization
    - Adaptive mesh refinement
    """
    
    def __init__(
        self,
        base_domain=None,
        mesh_algorithm="delaunay",  # "delaunay", "boundary_layer", "hybrid"
        target_element_size=0.3,
        boundary_layers=None,  # Number of boundary layers
        boundary_layer_growth=1.2,  # Growth rate for boundary layers
        show_domain=True,
        mesh_color=YELLOW,
        domain_color=RED,
        mesh_opacity=0.3,
        stroke_width=1.5,
        **kwargs
    ):
        """
        Create advanced finite element mesh.
        
        Parameters:
        -----------
        mesh_algorithm : str
            "delaunay" - Delaunay triangulation (best quality)
            "boundary_layer" - Structured layers near boundary
            "hybrid" - Boundary layers + Delaunay interior
        target_element_size : float
            Approximate size of mesh elements
        boundary_layers : int or None
            Number of layers near boundary (for boundary_layer/hybrid)
        boundary_layer_growth : float
            Growth rate for boundary layer thickness
        """
        super().__init__(**kwargs)
        
        # Import CommplexElement from domain_2d_enhanced
        from domain_2d_enhanced import CommplexElement
        
        if base_domain is None:
            base_domain = CommplexElement(irregularity=0.25, seed=42)
        
        self.base_domain = base_domain
        self.target_size = target_element_size
        self.mesh_algorithm = mesh_algorithm
        self.boundary_layers = boundary_layers
        self.boundary_layer_growth = boundary_layer_growth
        
        # Generate mesh based on algorithm
        if mesh_algorithm == "delaunay":
            elements, self.nodes = self._generate_delaunay_mesh()
        elif mesh_algorithm == "boundary_layer":
            elements, self.nodes = self._generate_boundary_layer_mesh()
        elif mesh_algorithm == "hybrid":
            elements, self.nodes = self._generate_hybrid_mesh()
        else:
            raise ValueError(f"Unknown algorithm: {mesh_algorithm}")
        
        # Style elements
        for elem in elements:
            elem.set_fill(mesh_color, opacity=mesh_opacity)
            elem.set_stroke(mesh_color, width=stroke_width)
        
        self.add(*elements)
        
        # Add domain boundary
        if show_domain:
            boundary = self.base_domain.copy()
            boundary.set_fill(opacity=0)
            boundary.set_stroke(domain_color, width=stroke_width + 1)
            self.add(boundary)
        
        self.mesh_elements = elements
    
    def _sample_boundary(self, target_spacing=None):
        """Sample points uniformly along the boundary."""
        if target_spacing is None:
            target_spacing = self.target_size
        
        boundary_curve = self.base_domain.complex_domain
        all_points = boundary_curve.get_all_points()
        
        # Calculate total perimeter
        perimeter = 0
        for i in range(len(all_points) - 1):
            perimeter += np.linalg.norm(all_points[i+1] - all_points[i])
        
        # Number of boundary points
        n_boundary = max(int(perimeter / target_spacing), 20)
        
        # Uniformly sample
        indices = np.linspace(0, len(all_points) - 1, n_boundary, dtype=int)
        return all_points[indices]
    
    def _get_domain_center(self):
        """Get centroid of domain."""
        boundary = self._sample_boundary()
        return np.mean(boundary, axis=0)
    
    def _point_in_polygon(self, point, polygon_points):
        """Check if point is inside polygon using ray casting."""
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
    
    def _generate_interior_points(self, boundary_points, spacing):
        """Generate interior points using Poisson disk sampling."""
        center = self._get_domain_center()
        
        # Bounding box
        min_x = np.min(boundary_points[:, 0])
        max_x = np.max(boundary_points[:, 0])
        min_y = np.min(boundary_points[:, 1])
        max_y = np.max(boundary_points[:, 1])
        
        # Grid-based sampling
        points = []
        
        # Add center point
        points.append(center[:2])
        
        # Sample on a grid with some randomization
        n_x = int((max_x - min_x) / spacing) + 1
        n_y = int((max_y - min_y) / spacing) + 1
        
        for i in range(n_x):
            for j in range(n_y):
                x = min_x + i * spacing + np.random.uniform(-0.2, 0.2) * spacing
                y = min_y + j * spacing + np.random.uniform(-0.2, 0.2) * spacing
                point = np.array([x, y, 0])
                
                # Check if inside domain
                if self._point_in_polygon(point, boundary_points):
                    points.append(point[:2])
        
        return np.array(points)
    
    def _generate_delaunay_mesh(self):
        """
        Generate mesh using Delaunay triangulation.
        
        This is the GOLD STANDARD for triangular mesh generation:
        - Maximizes minimum angle (avoids skinny triangles)
        - Unique for a given point set
        - Mathematically optimal quality
        """
        # Sample boundary
        boundary_points = self._sample_boundary(self.target_size)
        
        # Generate interior points
        interior_points = self._generate_interior_points(boundary_points, self.target_size)
        
        # Combine all points
        all_points = np.vstack([boundary_points[:, :2], interior_points])
        
        # Perform Delaunay triangulation
        tri = ScipyDelaunay(all_points)
        
        # Create triangle elements
        elements = []
        valid_triangles = []
        
        for simplex in tri.simplices:
            # Get triangle vertices
            v1 = np.array([all_points[simplex[0], 0], all_points[simplex[0], 1], 0])
            v2 = np.array([all_points[simplex[1], 0], all_points[simplex[1], 1], 0])
            v3 = np.array([all_points[simplex[2], 0], all_points[simplex[2], 1], 0])
            
            # Check if triangle centroid is inside domain
            centroid = (v1 + v2 + v3) / 3
            if self._point_in_polygon(centroid, boundary_points):
                triangle = Polygon(v1, v2, v3)
                elements.append(triangle)
                valid_triangles.append(simplex)
        
        # Store nodes for quality analysis
        nodes = all_points
        
        return elements, nodes
    
    def _generate_boundary_layer_mesh(self):
        """
        Generate structured boundary layer mesh.
        
        Critical for CFD and problems with boundary gradients:
        - Controlled element height near boundary
        - High aspect ratio elements (stretched)
        - Smooth transition to interior
        """
        if self.boundary_layers is None:
            self.boundary_layers = 3
        
        boundary_points = self._sample_boundary(self.target_size)
        n_boundary = len(boundary_points)
        
        elements = []
        all_nodes = []
        
        # Compute inward normals at each boundary point
        normals = []
        for i in range(n_boundary):
            prev_pt = boundary_points[(i - 1) % n_boundary]
            next_pt = boundary_points[(i + 1) % n_boundary]
            
            # Tangent vector
            tangent = next_pt - prev_pt
            tangent = tangent / np.linalg.norm(tangent)
            
            # Inward normal (rotate tangent 90 degrees)
            normal = np.array([-tangent[1], tangent[0], 0])
            
            # Check if normal points inward
            center = self._get_domain_center()
            to_center = center - boundary_points[i]
            if np.dot(normal[:2], to_center[:2]) < 0:
                normal = -normal
            
            normals.append(normal)
        
        # Create layers
        layer_heights = []
        h = self.target_size * 0.3  # Initial layer height
        for layer in range(self.boundary_layers):
            layer_heights.append(h)
            h *= self.boundary_layer_growth
        
        # Generate layer points
        layer_points = [boundary_points]
        for layer_h in layer_heights:
            new_layer = []
            for i, pt in enumerate(layer_points[-1]):
                new_pt = pt + normals[i] * layer_h
                new_layer.append(new_pt)
            layer_points.append(np.array(new_layer))
        
        # Create quad elements in layers
        for layer in range(len(layer_points) - 1):
            for i in range(n_boundary):
                i_next = (i + 1) % n_boundary
                
                v1 = layer_points[layer][i]
                v2 = layer_points[layer][i_next]
                v3 = layer_points[layer + 1][i_next]
                v4 = layer_points[layer + 1][i]
                
                # Create two triangles from quad
                tri1 = Polygon(v1, v2, v3)
                tri2 = Polygon(v1, v3, v4)
                
                elements.append(tri1)
                elements.append(tri2)
        
        # Fill interior with Delaunay
        interior_boundary = layer_points[-1]
        interior_points = self._generate_interior_points(
            interior_boundary, 
            self.target_size * 1.5
        )
        
        if len(interior_points) > 3:
            all_interior = np.vstack([interior_boundary[:, :2], interior_points])
            tri = ScipyDelaunay(all_interior)
            
            for simplex in tri.simplices:
                v1 = np.array([all_interior[simplex[0], 0], all_interior[simplex[0], 1], 0])
                v2 = np.array([all_interior[simplex[1], 0], all_interior[simplex[1], 1], 0])
                v3 = np.array([all_interior[simplex[2], 0], all_interior[simplex[2], 1], 0])
                
                centroid = (v1 + v2 + v3) / 3
                if self._point_in_polygon(centroid, boundary_points):
                    triangle = Polygon(v1, v2, v3)
                    elements.append(triangle)
        
        # Collect all nodes
        for layer in layer_points:
            all_nodes.extend(layer[:, :2])
        if len(interior_points) > 0:
            all_nodes.extend(interior_points)
        
        nodes = np.array(all_nodes)
        
        return elements, nodes
    
    def _generate_hybrid_mesh(self):
        """Boundary layers + Delaunay interior (BEST for CFD)."""
        return self._generate_boundary_layer_mesh()
    
    def calculate_quality_metrics(self):
        """
        Calculate quality metrics for all elements.
        
        Returns dictionary with:
        - aspect_ratios: list of aspect ratios
        - min_angles: list of minimum angles (degrees)
        - areas: list of element areas
        - quality_scores: 0-1 score (1 = perfect)
        """
        metrics = {
            'aspect_ratios': [],
            'min_angles': [],
            'areas': [],
            'quality_scores': []
        }
        
        for elem in self.mesh_elements:
            vertices = elem.get_vertices()
            
            if len(vertices) < 3:
                continue
            
            # Take first 3 vertices for triangle
            v1, v2, v3 = vertices[0], vertices[1], vertices[2]
            
            # Edge lengths
            e1 = np.linalg.norm(v2 - v1)
            e2 = np.linalg.norm(v3 - v2)
            e3 = np.linalg.norm(v1 - v3)
            
            # Aspect ratio
            longest = max(e1, e2, e3)
            shortest = min(e1, e2, e3)
            aspect_ratio = longest / shortest if shortest > 1e-10 else 100
            
            # Angles (using law of cosines)
            def angle(a, b, c):
                """Angle opposite to side a."""
                cos_angle = (b**2 + c**2 - a**2) / (2 * b * c)
                cos_angle = np.clip(cos_angle, -1, 1)
                return np.arccos(cos_angle) * 180 / np.pi
            
            angle1 = angle(e1, e2, e3)
            angle2 = angle(e2, e3, e1)
            angle3 = angle(e3, e1, e2)
            min_angle = min(angle1, angle2, angle3)
            
            # Area
            area = 0.5 * abs(
                (v2[0] - v1[0]) * (v3[1] - v1[1]) - 
                (v3[0] - v1[0]) * (v2[1] - v1[1])
            )
            
            # Quality score (0-1, higher is better)
            # Based on minimum angle (equilateral = 60°)
            angle_quality = min_angle / 60.0
            # Based on aspect ratio (equilateral = 1.0)
            aspect_quality = 1.0 / aspect_ratio
            
            quality = (angle_quality + aspect_quality) / 2
            quality = np.clip(quality, 0, 1)
            
            metrics['aspect_ratios'].append(aspect_ratio)
            metrics['min_angles'].append(min_angle)
            metrics['areas'].append(area)
            metrics['quality_scores'].append(quality)
        
        return metrics
    
    def color_by_quality(self, metric="quality", color_range=[RED, GREEN]):
        """
        Color elements by quality metric.
        
        Parameters:
        -----------
        metric : str
            "quality" - overall quality score (0-1)
            "aspect_ratio" - aspect ratio
            "min_angle" - minimum angle
            "area" - element area
        """
        metrics = self.calculate_quality_metrics()
        
        if metric == "quality":
            values = metrics['quality_scores']
            reverse = False  # Higher is better
        elif metric == "aspect_ratio":
            values = metrics['aspect_ratios']
            reverse = True  # Lower is better
        elif metric == "min_angle":
            values = metrics['min_angles']
            reverse = False  # Higher is better
        elif metric == "area":
            values = metrics['areas']
            reverse = False
        else:
            raise ValueError(f"Unknown metric: {metric}")
        
        # Normalize values
        vmin, vmax = min(values), max(values)
        if vmax - vmin > 1e-10:
            norm_values = [(v - vmin) / (vmax - vmin) for v in values]
        else:
            norm_values = [0.5] * len(values)
        
        # Reverse if lower is better
        if reverse:
            norm_values = [1 - v for v in norm_values]
        
        # Apply colors
        for elem, norm_val in zip(self.mesh_elements, norm_values):
            color = interpolate_color(color_range[0], color_range[1], norm_val)
            elem.set_fill(color, opacity=0.7)
        
        return self
    
    def get_quality_stats(self):
        """Get summary statistics of mesh quality."""
        metrics = self.calculate_quality_metrics()
        
        stats = {
            'num_elements': len(self.mesh_elements),
            'avg_quality': np.mean(metrics['quality_scores']),
            'min_quality': np.min(metrics['quality_scores']),
            'avg_aspect_ratio': np.mean(metrics['aspect_ratios']),
            'max_aspect_ratio': np.max(metrics['aspect_ratios']),
            'avg_min_angle': np.mean(metrics['min_angles']),
            'min_angle_overall': np.min(metrics['min_angles']),
        }
        
        return stats


# Continue in next file...