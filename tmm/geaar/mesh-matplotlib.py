#!/usr/bin/env python3
"""
Generate animated gear mesh visualization as MP4 and GIF
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from matplotlib import animation
from PIL import Image
import os

# ============= GEAR MATHEMATICS =============

def involute(alpha_rad):
    return np.tan(alpha_rad) - alpha_rad

def pressure_angle_at_radius(rb, r):
    return np.where(r < rb, 0, np.arccos(rb / r))

def tooth_thickness_at_radius(r, tp, rp, phi_rad, rb):
    psi = pressure_angle_at_radius(rb, r)
    return 2 * r * (tp / (2 * rp) + involute(phi_rad) - involute(psi))

def point_on_circle(center, radius, angle):
    return center + radius * np.array([np.cos(angle), np.sin(angle)])

# ============= GEAR PROFILE GENERATION =============

def generate_gear_profile(center, rb, ra, tp, rp, phi_rad, ptP, ptP1, num_teeth, rd, rotation_angle=0, num_points=35):
    """Generate gear profile path"""
    tooth_angle = 2 * np.pi / num_teeth
    r_end = max(rd, ra) if rb < rd else ra
    
    gear_points = []
    
    for tooth_num in range(num_teeth):
        rotation = tooth_num * tooth_angle + rotation_angle
        rotated_P = np.array([
            np.cos(rotation) * ptP[0] - np.sin(rotation) * ptP[1],
            np.sin(rotation) * ptP[0] + np.cos(rotation) * ptP[1]
        ]) + center
        
        rotated_P1 = np.array([
            np.cos(rotation) * ptP1[0] - np.sin(rotation) * ptP1[1],
            np.sin(rotation) * ptP1[0] + np.cos(rotation) * ptP1[1]
        ]) + center
        
        angle_P1 = np.arctan2(rotated_P1[1] - center[1], rotated_P1[0] - center[0])
        
        half_angle_base = tooth_thickness_at_radius(rb, tp, rp, phi_rad, rb) / (2 * rb)
        angle_left_base = angle_P1 - half_angle_base
        angle_right_base = angle_P1 + half_angle_base
        angle_next_left = angle_P1 + tooth_angle - half_angle_base
        
        # Left involute
        for i in range(num_points + 1):
            r = rb + (r_end - rb) * i / num_points
            half_angle = tooth_thickness_at_radius(r, tp, rp, phi_rad, rb) / (2 * r)
            pt = point_on_circle(center, r, angle_P1 - half_angle)
            gear_points.append(pt)
        
        # Addendum arc (simplified - use points on circle)
        half_angle_end = tooth_thickness_at_radius(r_end, tp, rp, phi_rad, rb) / (2 * r_end)
        for i in range(10):
            angle = angle_P1 - half_angle_end + (2 * half_angle_end) * i / 9
            pt = point_on_circle(center, r_end, angle)
            gear_points.append(pt)
        
        # Right involute
        for i in range(num_points, -1, -1):
            r = rb + (r_end - rb) * i / num_points
            half_angle = tooth_thickness_at_radius(r, tp, rp, phi_rad, rb) / (2 * r)
            pt = point_on_circle(center, r, angle_P1 + half_angle)
            gear_points.append(pt)
        
        # Dedendum arc
        for i in range(10):
            angle = angle_right_base + (angle_next_left - angle_right_base) * i / 9
            pt = point_on_circle(center, rd, angle)
            gear_points.append(pt)
    
    return np.array(gear_points)

# ============= SETUP PARAMETERS =============

num_teeth = 22
phi = np.radians(20)
rp = 132  # mm
m = 2 * rp / num_teeth
rb = rp * np.cos(phi)
ra = rp + 1 * m
rd = rp - 1.25 * m
p = 2 * np.pi * rp / num_teeth
tp = p / 2

center1 = np.array([200, 200])  # mm
angle_initial = 100 * np.pi / 180
ptP = np.array([rp * np.cos(angle_initial + (tp / 2) / rp), rp * np.sin(angle_initial + (tp / 2) / rp)])
ptP1 = np.array([rp * np.cos(angle_initial), rp * np.sin(angle_initial)])

angle_to_P = np.arctan2(ptP[1], ptP[0])
center2 = center1 + 2 * rp * np.array([np.cos(angle_to_P), np.sin(angle_to_P)])
angle_P1_gear2 = angle_to_P - (tp / 2) / rp
ptP1_gear2 = np.array([rp * np.cos(angle_P1_gear2), rp * np.sin(angle_P1_gear2)])

# ============= GENERATE FRAMES =============

num_frames = 24
fps = 12
frames_dir = "frames"

if not os.path.exists(frames_dir):
    os.makedirs(frames_dir)

print(f"Generating {num_frames} animation frames...")

for frame in range(num_frames):
    angle_increment = 2 * np.pi * frame / num_frames
    
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    ax.set_xlim(-10, 410)
    ax.set_ylim(-10, 410)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    # Draw boundary
    ax.plot([0, 400, 400, 0, 0], [0, 0, 400, 400, 0], 'k--', alpha=0.5, linewidth=1)
    
    # Generate and draw gears
    gear1_profile = generate_gear_profile(center1, rb, ra, tp, rp, phi, ptP, ptP1, num_teeth, rd, angle_increment)
    gear2_profile = generate_gear_profile(center2, rb, ra, tp, rp, phi, ptP, ptP1_gear2, num_teeth, rd, -angle_increment)
    
    ax.fill(gear1_profile[:, 0], gear1_profile[:, 1], color='lightgray', alpha=0.7, edgecolor='black', linewidth=2)
    ax.fill(gear2_profile[:, 0], gear2_profile[:, 1], color='lightgray', alpha=0.7, edgecolor='black', linewidth=2)
    
    # Draw centers
    ax.plot(*center1, 'ko', markersize=8)
    ax.plot(*center2, 'ko', markersize=8)
    
    # Draw line between centers
    ax.plot([center1[0], center2[0]], [center1[1], center2[1]], 'k--', alpha=0.3, linewidth=1)
    
    # Draw pitch circles (light)
    circle1_pitch = Circle(center1, rp, fill=False, edgecolor='blue', linestyle='--', alpha=0.3, linewidth=1)
    circle2_pitch = Circle(center2, rp, fill=False, edgecolor='blue', linestyle='--', alpha=0.3, linewidth=1)
    ax.add_patch(circle1_pitch)
    ax.add_patch(circle2_pitch)
    
    # Draw meshing point
    ax.plot(*ptP, 'r.', markersize=10)
    
    # Labels
    ax.set_xlabel('X (mm)', fontsize=10)
    ax.set_ylabel('Y (mm)', fontsize=10)
    ax.set_title(f'Gear Mesh Animation - Frame {frame + 1}/{num_frames}', fontsize=12)
    ax.text(20, 20, f'Frame {frame + 1}/{num_frames}', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Save frame
    frame_path = os.path.join(frames_dir, f'frame_{frame:03d}.png')
    plt.savefig(frame_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    if (frame + 1) % 6 == 0:
        print(f"  Generated {frame + 1}/{num_frames} frames")

print(f"Frames saved to {frames_dir}/")

# ============= CREATE VIDEO AND GIF =============

print("\nCreating MP4 video...")
os.system(f'ffmpeg -framerate {fps} -i {frames_dir}/frame_%03d.png -vf scale=1200:1200 -c:v libx264 -pix_fmt yuv420p gear_mesh_animation.mp4 -y')

print("Creating GIF animation...")
os.system(f'ffmpeg -framerate {fps} -i {frames_dir}/frame_%03d.png -vf scale=800:800 gear_mesh_animation.gif -y')

print("\nAnimation complete!")
print("  - MP4: gear_mesh_animation.mp4")
print("  - GIF: gear_mesh_animation.gif")
