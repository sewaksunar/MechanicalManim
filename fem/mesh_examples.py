"""
Example scenes demonstrating best meshing practices
"""

from manim import *
import numpy as np
from advanced_meshing import AdvancedFiniteElement
from domain_2d_enhanced import CommplexElement


class DelaunayVsRadial(Scene):
    """
    Compare Delaunay (optimal) vs Radial (simple) meshing.
    
    Key Learning: Delaunay produces higher quality triangles
    """
    
    def construct(self):
        # Create same domain for both
        domain = CommplexElement(irregularity=0.3, seed=100)
        
        # Radial mesh (from previous implementation)
        from domain_2d_enhanced import FiniteElement
        radial_mesh = FiniteElement(
            base_domain=domain.copy(),
            element_type="triangle",
            num_radial=5,
            num_angular=16,
            mesh_color=BLUE,
            show_domain=True,
        )
        radial_mesh.scale(0.9).shift(LEFT * 3.5)
        
        # Delaunay mesh (optimal quality)
        delaunay_mesh = AdvancedFiniteElement(
            base_domain=domain.copy(),
            mesh_algorithm="delaunay",
            target_element_size=0.35,
            mesh_color=GREEN,
            show_domain=True,
        )
        delaunay_mesh.scale(0.9).shift(RIGHT * 3.5)
        
        # Labels
        radial_label = VGroup(
            Text("Radial Mesh", font_size=22, color=BLUE),
            Text("(Simple)", font_size=16, color=GRAY)
        ).arrange(DOWN, buff=0.1).next_to(radial_mesh, UP)
        
        delaunay_label = VGroup(
            Text("Delaunay Mesh", font_size=22, color=GREEN),
            Text("(Optimal Quality)", font_size=16, color=GRAY)
        ).arrange(DOWN, buff=0.1).next_to(delaunay_mesh, UP)
        
        title = Text("Meshing Algorithm Comparison", font_size=28).to_edge(UP)
        
        # Quality comparison
        delaunay_stats = delaunay_mesh.get_quality_stats()
        comparison = VGroup(
            Text(f"Delaunay Quality: {delaunay_stats['avg_quality']:.2f}", 
                 font_size=16, color=GREEN),
            Text(f"Min Angle: {delaunay_stats['min_angle_overall']:.1f}°",
                 font_size=14, color=GRAY),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT).to_edge(DOWN).shift(RIGHT * 2)
        
        self.add(radial_mesh, delaunay_mesh)
        self.add(radial_label, delaunay_label, title, comparison)


class BoundaryLayerMesh(Scene):
    """
    Demonstrate boundary layer meshing for CFD applications.
    
    Key Learning: Critical for capturing gradients near walls
    """
    
    def construct(self):
        # Airfoil-like shape
        control_pts = [
            (2.5, 0.0),
            (1.5, 0.8),
            (0.0, 1.0),
            (-1.5, 0.6),
            (-2.0, 0.0),
            (-1.5, -0.4),
            (0.0, -0.5),
            (1.5, -0.3),
        ]
        domain = CommplexElement(control_points=control_pts, control_smoothness=40)
        
        # Boundary layer mesh
        bl_mesh = AdvancedFiniteElement(
            base_domain=domain,
            mesh_algorithm="boundary_layer",
            target_element_size=0.4,
            boundary_layers=4,
            boundary_layer_growth=1.3,
            mesh_color=BLUE,
            show_domain=True,
            domain_color=RED,
            stroke_width=2,
        )
        
        title = Text("Boundary Layer Mesh", font_size=32).to_edge(UP)
        
        description = VGroup(
            Text("4 structured layers near boundary", font_size=18),
            Text("Growth rate: 1.3x per layer", font_size=16, color=GRAY),
            Text("Critical for CFD and gradient capture", font_size=16, color=YELLOW),
        ).arrange(DOWN, buff=0.15, aligned_edge=LEFT).to_edge(DOWN)
        
        # Highlight first layer
        first_layer_note = Text(
            "First layer: Fine elements\nnear wall", 
            font_size=14, 
            color=BLUE
        ).move_to(RIGHT * 4 + UP * 2)
        
        arrow = Arrow(
            first_layer_note.get_left(),
            bl_mesh.get_right() + LEFT * 0.5,
            color=BLUE,
            stroke_width=2,
        )
        
        self.add(bl_mesh, title, description)
        self.add(first_layer_note, arrow)


class QualityVisualization(Scene):
    """
    Visualize mesh quality metrics.
    
    Key Learning: Always check quality before using mesh
    """
    
    def construct(self):
        domain = CommplexElement(irregularity=0.25, seed=42)
        
        # Create Delaunay mesh
        mesh = AdvancedFiniteElement(
            base_domain=domain,
            mesh_algorithm="delaunay",
            target_element_size=0.35,
            show_domain=True,
            domain_color=WHITE,
        )
        
        # Color by quality
        mesh.color_by_quality(metric="quality", color_range=[RED, GREEN])
        
        title = Text("Mesh Quality Visualization", font_size=28).to_edge(UP)
        
        # Quality stats
        stats = mesh.get_quality_stats()
        
        stats_text = VGroup(
            Text(f"Total Elements: {stats['num_elements']}", font_size=16),
            Text(f"Average Quality: {stats['avg_quality']:.3f}", font_size=16),
            Text(f"Min Quality: {stats['min_quality']:.3f}", font_size=16),
            Text(f"Avg Aspect Ratio: {stats['avg_aspect_ratio']:.2f}", font_size=16),
            Text(f"Min Angle: {stats['min_angle_overall']:.1f}°", font_size=16),
        ).arrange(DOWN, buff=0.15, aligned_edge=LEFT).scale(0.9).to_corner(DL)
        
        # Color legend
        legend = VGroup(
            Text("Quality:", font_size=18, weight=BOLD),
            VGroup(
                Rectangle(width=0.3, height=0.2, fill_color=RED, fill_opacity=0.7, stroke_width=0),
                Text("Poor", font_size=14),
            ).arrange(RIGHT, buff=0.1),
            VGroup(
                Rectangle(width=0.3, height=0.2, fill_color=YELLOW, fill_opacity=0.7, stroke_width=0),
                Text("Fair", font_size=14),
            ).arrange(RIGHT, buff=0.1),
            VGroup(
                Rectangle(width=0.3, height=0.2, fill_color=GREEN, fill_opacity=0.7, stroke_width=0),
                Text("Good", font_size=14),
            ).arrange(RIGHT, buff=0.1),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT).scale(0.8).to_corner(DR)
        
        self.add(mesh, title, stats_text, legend)


class MeshRefinementStudy(Scene):
    """
    Show mesh refinement progression (convergence study).
    
    Key Learning: Always perform convergence study
    """
    
    def construct(self):
        domain = CommplexElement(irregularity=0.3, seed=50)
        
        # Three meshes: coarse, medium, fine
        coarse = AdvancedFiniteElement(
            base_domain=domain.copy(),
            mesh_algorithm="delaunay",
            target_element_size=0.6,
            mesh_color=BLUE,
            show_domain=True,
        )
        coarse.scale(0.6).shift(LEFT * 4.2)
        
        medium = AdvancedFiniteElement(
            base_domain=domain.copy(),
            mesh_algorithm="delaunay",
            target_element_size=0.4,
            mesh_color=YELLOW,
            show_domain=True,
        )
        medium.scale(0.6)
        
        fine = AdvancedFiniteElement(
            base_domain=domain.copy(),
            mesh_algorithm="delaunay",
            target_element_size=0.25,
            mesh_color=GREEN,
            show_domain=True,
        )
        fine.scale(0.6).shift(RIGHT * 4.2)
        
        # Labels with element counts
        coarse_stats = coarse.get_quality_stats()
        medium_stats = medium.get_quality_stats()
        fine_stats = fine.get_quality_stats()
        
        coarse_label = VGroup(
            Text("Coarse", font_size=20, color=BLUE),
            Text(f"{coarse_stats['num_elements']} elements", font_size=14, color=GRAY)
        ).arrange(DOWN, buff=0.1).next_to(coarse, UP)
        
        medium_label = VGroup(
            Text("Medium", font_size=20, color=YELLOW),
            Text(f"{medium_stats['num_elements']} elements", font_size=14, color=GRAY)
        ).arrange(DOWN, buff=0.1).next_to(medium, UP)
        
        fine_label = VGroup(
            Text("Fine", font_size=20, color=GREEN),
            Text(f"{fine_stats['num_elements']} elements", font_size=14, color=GRAY)
        ).arrange(DOWN, buff=0.1).next_to(fine, UP)
        
        title = Text("Mesh Refinement Study", font_size=28).to_edge(UP)
        
        note = Text(
            "Solution should converge as mesh is refined →",
            font_size=16,
            color=YELLOW
        ).to_edge(DOWN)
        
        self.add(coarse, medium, fine)
        self.add(coarse_label, medium_label, fine_label, title, note)


class OptimalElementSize(Scene):
    """
    Demonstrate optimal element sizing strategy.
    
    Key Learning: Smaller near features, larger in uniform regions
    """
    
    def construct(self):
        # Create domain with a feature (indentation)
        control_pts = [
            (2.0, 0.8),
            (0.8, 1.8),
            (-0.2, 1.9),  # Small feature
            (-0.5, 1.6),  # Small feature
            (-0.8, 1.8),  # Small feature
            (-2.0, 1.0),
            (-2.2, -0.5),
            (-1.0, -1.8),
            (1.5, -1.5),
        ]
        domain = CommplexElement(control_points=control_pts, control_smoothness=50)
        
        # Fine mesh to capture features
        mesh = AdvancedFiniteElement(
            base_domain=domain,
            mesh_algorithm="delaunay",
            target_element_size=0.3,
            mesh_color=BLUE,
            show_domain=True,
            domain_color=RED,
        )
        
        title = Text("Element Sizing Strategy", font_size=28).to_edge(UP)
        
        # Annotations
        feature_note = Text(
            "Fine elements\nnear features",
            font_size=14,
            color=YELLOW
        ).move_to(LEFT * 4 + UP * 1)
        
        uniform_note = Text(
            "Coarser in\nuniform regions",
            font_size=14,
            color=YELLOW
        ).move_to(RIGHT * 3.5 + DOWN * 0.5)
        
        arrow1 = Arrow(
            feature_note.get_right(),
            mesh.get_left() + RIGHT * 0.3 + UP * 1,
            color=YELLOW,
            stroke_width=2,
        )
        
        arrow2 = Arrow(
            uniform_note.get_left(),
            mesh.get_right() + LEFT * 1.5 + DOWN * 0.5,
            color=YELLOW,
            stroke_width=2,
        )
        
        principle = Text(
            "Rule: 3-5 elements across smallest feature",
            font_size=16,
            color=GREEN
        ).to_edge(DOWN)
        
        self.add(mesh, title)
        self.add(feature_note, uniform_note, arrow1, arrow2, principle)


class AspectRatioComparison(Scene):
    """
    Show effect of aspect ratio on mesh quality.
    
    Key Learning: Avoid high aspect ratios (except boundary layers)
    """
    
    def construct(self):
        domain = CommplexElement(irregularity=0.3, seed=123)
        
        # Mesh colored by aspect ratio
        mesh = AdvancedFiniteElement(
            base_domain=domain,
            mesh_algorithm="delaunay",
            target_element_size=0.35,
            show_domain=True,
        )
        
        # Color by aspect ratio (red = bad, green = good)
        mesh.color_by_quality(metric="aspect_ratio", color_range=[RED, GREEN])
        
        title = Text("Aspect Ratio Visualization", font_size=28).to_edge(UP)
        
        # Quality guide
        guide = VGroup(
            Text("Aspect Ratio Quality:", font_size=18, weight=BOLD),
            Text("< 3:  Excellent", font_size=14, color=GREEN),
            Text("3-10: Acceptable", font_size=14, color=YELLOW),
            Text("> 10: Poor", font_size=14, color=RED),
        ).arrange(DOWN, buff=0.15, aligned_edge=LEFT).to_corner(DR)
        
        # Stats
        stats = mesh.get_quality_stats()
        stats_text = VGroup(
            Text(f"Average: {stats['avg_aspect_ratio']:.2f}", font_size=16),
            Text(f"Maximum: {stats['max_aspect_ratio']:.2f}", font_size=16),
        ).arrange(DOWN, buff=0.15, aligned_edge=LEFT).to_corner(DL)
        
        # Legend
        legend = VGroup(
            VGroup(
                Rectangle(width=0.3, height=0.2, fill_color=GREEN, fill_opacity=0.7, stroke_width=0),
                Text("Good", font_size=14),
            ).arrange(RIGHT, buff=0.1),
            VGroup(
                Rectangle(width=0.3, height=0.2, fill_color=RED, fill_opacity=0.7, stroke_width=0),
                Text("Poor", font_size=14),
            ).arrange(RIGHT, buff=0.1),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT).next_to(guide, UP, buff=0.3)
        
        self.add(mesh, title, guide, stats_text, legend)


# ==========================================
# Render commands:
# ==========================================
# 
# Compare algorithms:
#   manim -pql mesh_examples.py DelaunayVsRadial
# 
# Boundary layer meshing:
#   manim -pql mesh_examples.py BoundaryLayerMesh
# 
# Quality visualization:
#   manim -pql mesh_examples.py QualityVisualization
# 
# Refinement study:
#   manim -pql mesh_examples.py MeshRefinementStudy
# 
# Element sizing:
#   manim -pql mesh_examples.py OptimalElementSize
# 
# Aspect ratio:
#   manim -pql mesh_examples.py AspectRatioComparison