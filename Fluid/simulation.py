"""
Standalone Navier-Stokes Fluid Simulation for Manim
All dependencies included in one file.

Run with: manim -ql fluid_simulation_standalone.py FluidSimulation
"""

from manim import *
import numpy as np


class NavierStokesSolver:
    """2D Incompressible Navier-Stokes Fluid Solver"""
    
    def __init__(self, size=128, viscosity=0.0001, dt=0.1):
        self.size = size
        self.viscosity = viscosity
        self.dt = dt
        
        # Velocity fields
        self.u = np.zeros((size, size))
        self.v = np.zeros((size, size))
        self.u_prev = np.zeros((size, size))
        self.v_prev = np.zeros((size, size))
        
        # Density field for visualization
        self.density = np.zeros((size, size))
        self.density_prev = np.zeros((size, size))
        
    def add_velocity(self, x, y, vx, vy, radius=5):
        """Add velocity at a specific location"""
        x_idx = int(x * self.size)
        y_idx = int(y * self.size)
        
        for i in range(max(0, x_idx-radius), min(self.size, x_idx+radius)):
            for j in range(max(0, y_idx-radius), min(self.size, y_idx+radius)):
                self.u[i, j] += vx
                self.v[i, j] += vy
    
    def add_density(self, x, y, amount, radius=5):
        """Add density at a specific location"""
        x_idx = int(x * self.size)
        y_idx = int(y * self.size)
        
        for i in range(max(0, x_idx-radius), min(self.size, x_idx+radius)):
            for j in range(max(0, y_idx-radius), min(self.size, y_idx+radius)):
                self.density[i, j] += amount
    
    def diffuse(self, b, x, x0, diff):
        """Diffusion step using Gauss-Seidel relaxation"""
        a = self.dt * diff * (self.size - 2) ** 2
        
        for _ in range(20):
            x[1:-1, 1:-1] = (x0[1:-1, 1:-1] + a * (
                x[2:, 1:-1] + x[:-2, 1:-1] + 
                x[1:-1, 2:] + x[1:-1, :-2]
            )) / (1 + 4 * a)
            self.set_boundary(b, x)
    
    def advect(self, b, d, d0, u, v):
        """Advection step using backward particle trace"""
        dt0 = self.dt * (self.size - 2)
        
        for i in range(1, self.size - 1):
            for j in range(1, self.size - 1):
                x = i - dt0 * u[i, j]
                y = j - dt0 * v[i, j]
                
                x = np.clip(x, 0.5, self.size - 2.5)
                y = np.clip(y, 0.5, self.size - 2.5)
                
                i0, j0 = int(x), int(y)
                i1, j1 = i0 + 1, j0 + 1
                
                s1 = x - i0
                s0 = 1 - s1
                t1 = y - j0
                t0 = 1 - t1
                
                d[i, j] = (s0 * (t0 * d0[i0, j0] + t1 * d0[i0, j1]) +
                          s1 * (t0 * d0[i1, j0] + t1 * d0[i1, j1]))
        
        self.set_boundary(b, d)
    
    def project(self, u, v, p, div):
        """Projection step to enforce incompressibility"""
        h = 1.0 / (self.size - 2)
        
        div[1:-1, 1:-1] = -0.5 * h * (
            u[2:, 1:-1] - u[:-2, 1:-1] +
            v[1:-1, 2:] - v[1:-1, :-2]
        )
        p[:] = 0
        
        self.set_boundary(0, div)
        self.set_boundary(0, p)
        
        for _ in range(20):
            p[1:-1, 1:-1] = (div[1:-1, 1:-1] + 
                            p[2:, 1:-1] + p[:-2, 1:-1] +
                            p[1:-1, 2:] + p[1:-1, :-2]) / 4
            self.set_boundary(0, p)
        
        u[1:-1, 1:-1] -= 0.5 * (p[2:, 1:-1] - p[:-2, 1:-1]) / h
        v[1:-1, 1:-1] -= 0.5 * (p[1:-1, 2:] - p[1:-1, :-2]) / h
        
        self.set_boundary(1, u)
        self.set_boundary(2, v)
    
    def set_boundary(self, b, x):
        """Set boundary conditions"""
        if b == 2:
            x[0, :] = -x[1, :]
            x[-1, :] = -x[-2, :]
        else:
            x[0, :] = x[1, :]
            x[-1, :] = x[-2, :]
        
        if b == 1:
            x[:, 0] = -x[:, 1]
            x[:, -1] = -x[:, -2]
        else:
            x[:, 0] = x[:, 1]
            x[:, -1] = x[:, -2]
        
        x[0, 0] = 0.5 * (x[1, 0] + x[0, 1])
        x[0, -1] = 0.5 * (x[1, -1] + x[0, -2])
        x[-1, 0] = 0.5 * (x[-2, 0] + x[-1, 1])
        x[-1, -1] = 0.5 * (x[-2, -1] + x[-1, -2])
    
    def velocity_step(self):
        """Update velocity field for one time step"""
        self.u_prev, self.u = self.u, self.u_prev
        self.v_prev, self.v = self.v, self.v_prev
        
        self.diffuse(1, self.u, self.u_prev, self.viscosity)
        self.diffuse(2, self.v, self.v_prev, self.viscosity)
        
        p = np.zeros_like(self.u)
        div = np.zeros_like(self.u)
        self.project(self.u, self.v, p, div)
        
        self.u_prev, self.u = self.u, self.u_prev
        self.v_prev, self.v = self.v, self.v_prev
        
        self.advect(1, self.u, self.u_prev, self.u_prev, self.v_prev)
        self.advect(2, self.v, self.v_prev, self.u_prev, self.v_prev)
        
        self.project(self.u, self.v, p, div)
    
    def density_step(self):
        """Update density field for one time step"""
        self.density_prev, self.density = self.density, self.density_prev
        self.diffuse(0, self.density, self.density_prev, 0.0001)
        self.density_prev, self.density = self.density, self.density_prev
        self.advect(0, self.density, self.density_prev, self.u, self.v)
        self.density *= 0.99
    
    def step(self):
        """Perform one complete simulation step"""
        self.velocity_step()
        self.density_step()
    
    def get_vorticity(self):
        """Calculate vorticity field (curl of velocity)"""
        vorticity = np.zeros_like(self.u)
        vorticity[1:-1, 1:-1] = (
            (self.v[2:, 1:-1] - self.v[:-2, 1:-1]) -
            (self.u[1:-1, 2:] - self.u[1:-1, :-2])
        ) / 2.0
        return vorticity


class FluidSimulation(Scene):
    def construct(self):
        # Initialize solver with smaller grid for faster rendering
        solver = NavierStokesSolver(size=64, viscosity=0.0001, dt=0.1)
        
        # Add title
        title = Text("Navier-Stokes Fluid Simulation", font_size=36)
        title.to_edge(UP)
        self.add(title)
        
        # Equation
        equation = MathTex(
            r"\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u} = -\frac{\nabla p}{\rho} + \nu \nabla^2 \mathbf{u}",
            font_size=28
        )
        equation.next_to(title, DOWN, buff=0.3)
        self.add(equation)
        
        # Create initial vortex
        for angle in np.linspace(0, 2*np.pi, 16):
            x = 0.5 + 0.2 * np.cos(angle)
            y = 0.5 + 0.2 * np.sin(angle)
            vx = -np.sin(angle) * 50
            vy = np.cos(angle) * 50
            solver.add_velocity(x, y, vx, vy, radius=3)
            solver.add_density(x, y, 100, radius=3)
        
        # Visualization parameters
        resolution = 32
        step = solver.size // resolution
        
        # Create initial visualization
        density_group = VGroup()
        vector_group = VGroup()
        
        # Initial density field
        cell_size = 4.0 / resolution
        for i in range(0, solver.size, step):
            for j in range(0, solver.size, step):
                density_val = solver.density[i, j]
                if density_val > 1:
                    x = (i / solver.size - 0.5) * 4 + cell_size / 2
                    y = (j / solver.size - 0.5) * 4 + cell_size / 2 - 0.8
                    
                    opacity = min(density_val / 100, 1)
                    square = Square(
                        side_length=cell_size,
                        fill_color=BLUE,
                        fill_opacity=opacity * 0.7,
                        stroke_width=0
                    )
                    square.move_to([x, y, 0])
                    density_group.add(square)
        
        # Initial vector field
        for i in range(0, solver.size, step):
            for j in range(0, solver.size, step):
                vx = solver.u[i, j]
                vy = solver.v[i, j]
                
                mag = np.sqrt(vx**2 + vy**2)
                if mag > 0.5:
                    start_x = (i / solver.size - 0.5) * 4
                    start_y = (j / solver.size - 0.5) * 4 - 0.8
                    
                    scale = 0.08
                    end_x = start_x + vx * scale
                    end_y = start_y + vy * scale
                    
                    color = interpolate_color(BLUE, RED, min(mag / 10, 1))
                    
                    arrow = Arrow(
                        start=[start_x, start_y, 0],
                        end=[end_x, end_y, 0],
                        buff=0,
                        color=color,
                        stroke_width=2,
                        max_tip_length_to_length_ratio=0.25
                    )
                    vector_group.add(arrow)
        
        self.add(density_group, vector_group)
        
        # Animation loop
        num_frames = 100
        
        for frame in range(num_frames):
            # Update simulation (multiple substeps for smoother animation)
            for _ in range(2):
                solver.step()
            
            # Add continuous forcing
            if frame < 60:
                angle = frame * 0.1
                x = 0.5 + 0.15 * np.cos(angle)
                y = 0.5 + 0.15 * np.sin(angle)
                vx = -np.sin(angle) * 30
                vy = np.cos(angle) * 30
                solver.add_velocity(x, y, vx, vy, radius=2)
                solver.add_density(x, y, 50, radius=2)
            
            # Create new density field
            new_density = VGroup()
            for i in range(0, solver.size, step):
                for j in range(0, solver.size, step):
                    density_val = solver.density[i, j]
                    if density_val > 1:
                        x = (i / solver.size - 0.5) * 4 + cell_size / 2
                        y = (j / solver.size - 0.5) * 4 + cell_size / 2 - 0.8
                        
                        opacity = min(density_val / 100, 1)
                        square = Square(
                            side_length=cell_size,
                            fill_color=BLUE,
                            fill_opacity=opacity * 0.7,
                            stroke_width=0
                        )
                        square.move_to([x, y, 0])
                        new_density.add(square)
            
            # Create new vector field
            new_vectors = VGroup()
            for i in range(0, solver.size, step):
                for j in range(0, solver.size, step):
                    vx = solver.u[i, j]
                    vy = solver.v[i, j]
                    
                    mag = np.sqrt(vx**2 + vy**2)
                    if mag > 0.5:
                        start_x = (i / solver.size - 0.5) * 4
                        start_y = (j / solver.size - 0.5) * 4 - 0.8
                        
                        scale = 0.08
                        end_x = start_x + vx * scale
                        end_y = start_y + vy * scale
                        
                        color = interpolate_color(BLUE, RED, min(mag / 10, 1))
                        
                        arrow = Arrow(
                            start=[start_x, start_y, 0],
                            end=[end_x, end_y, 0],
                            buff=0,
                            color=color,
                            stroke_width=2,
                            max_tip_length_to_length_ratio=0.25
                        )
                        new_vectors.add(arrow)
            
            # Animate transition
            self.play(
                Transform(density_group, new_density),
                Transform(vector_group, new_vectors),
                run_time=0.1,
                rate_func=linear
            )
        
        self.wait(1)


class VorticityVisualization(Scene):
    def construct(self):
        # Initialize solver
        solver = NavierStokesSolver(size=64, viscosity=0.00005, dt=0.1)
        
        # Add title
        title = Text("Vorticity Field Visualization", font_size=36)
        title.to_edge(UP)
        self.add(title)
        
        subtitle = Text("(Curl of velocity field)", font_size=24, color=GRAY)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.add(subtitle)
        
        # Create vortex
        for angle in np.linspace(0, 2*np.pi, 20):
            x = 0.5 + 0.25 * np.cos(angle)
            y = 0.5 + 0.25 * np.sin(angle)
            vx = -np.sin(angle) * 60
            vy = np.cos(angle) * 60
            solver.add_velocity(x, y, vx, vy, radius=4)
        
        resolution = 48
        step = solver.size // resolution
        cell_size = 4.5 / resolution
        
        # Initial vorticity field
        vorticity = solver.get_vorticity()
        vort_group = VGroup()
        
        for i in range(0, solver.size, step):
            for j in range(0, solver.size, step):
                vort_val = vorticity[i, j]
                
                if abs(vort_val) > 0.1:
                    x = (i / solver.size - 0.5) * 4.5 + cell_size / 2
                    y = (j / solver.size - 0.5) * 4.5 + cell_size / 2 - 0.5
                    
                    if vort_val > 0:
                        color = RED
                        opacity = min(vort_val / 5, 1)
                    else:
                        color = BLUE
                        opacity = min(-vort_val / 5, 1)
                    
                    square = Square(
                        side_length=cell_size,
                        fill_color=color,
                        fill_opacity=opacity * 0.8,
                        stroke_width=0
                    )
                    square.move_to([x, y, 0])
                    vort_group.add(square)
        
        self.add(vort_group)
        
        # Animation
        for frame in range(80):
            for _ in range(2):
                solver.step()
            
            vorticity = solver.get_vorticity()
            new_vort = VGroup()
            
            for i in range(0, solver.size, step):
                for j in range(0, solver.size, step):
                    vort_val = vorticity[i, j]
                    
                    if abs(vort_val) > 0.1:
                        x = (i / solver.size - 0.5) * 4.5 + cell_size / 2
                        y = (j / solver.size - 0.5) * 4.5 + cell_size / 2 - 0.5
                        
                        if vort_val > 0:
                            color = RED
                            opacity = min(vort_val / 5, 1)
                        else:
                            color = BLUE
                            opacity = min(-vort_val / 5, 1)
                        
                        square = Square(
                            side_length=cell_size,
                            fill_color=color,
                            fill_opacity=opacity * 0.8,
                            stroke_width=0
                        )
                        square.move_to([x, y, 0])
                        new_vort.add(square)
            
            self.play(
                Transform(vort_group, new_vort),
                run_time=0.1,
                rate_func=linear
            )
        
        self.wait(1)