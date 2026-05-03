"""
Root Locus Construction Drawing
G(s)H(s) = K(s+2) / [s(s+1)(s^2+8s+64)]

Construction elements drawn:
  - Root locus branches (via python-control)
  - Real-axis locus segments
  - Asymptotes with angles (60°, 180°, -60°)
  - Asymptote centroid
  - Departure angles from complex poles
  - Break-away / Break-in points
  - Travel-direction arrows on branches
  - Angle-condition helper lines
"""

import matplotlib
matplotlib.use('Agg')           # change to 'TkAgg' or remove for interactive window
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import control as ct
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ── System definition ────────────────────────────────────────────────────────
# G(s)H(s) = (s+2) / (s^4 + 9s^3 + 72s^2 + 64s)
num = [1, 2]
den = [1, 9, 72, 64, 0]
sys = ct.TransferFunction(num, den)

poles = np.array([0+0j, -1+0j, -4+6.9282j, -4-6.9282j])
zeros = np.array([-2+0j])

# ── Pre-computed construction values ────────────────────────────────────────
# Asymptote centroid: (Σpoles - Σzeros) / (n-m)
centroid = -7 / 3   # exact: (0-1-4-4 - (-2)) / (4-1)

# Breakaway/break-in: roots of  D'(s)·N(s) - D(s)·N'(s) = 0
#   → 3s^4 + 26s^3 + 126s^2 + 288s + 128 = 0
bp_poly  = [3, 26, 126, 288, 128]
bp_roots = np.roots(bp_poly)
# Real roots only (the two real ones lie on real-axis locus segments)
real_bp  = bp_roots[np.abs(bp_roots.imag) < 1e-6].real
# real_bp ≈ [-0.5717, -3.5069]

# Departure angles from complex poles via angle condition:
#   φ_dep = 180° + Σ∠(p-z) - Σ∠(p-pj),  j ≠ k
def compute_departure(pole, all_poles, all_zeros):
    angle_sum_zeros = sum(np.degrees(np.angle(pole - z)) for z in all_zeros)
    angle_sum_poles = sum(np.degrees(np.angle(pole - p))
                          for p in all_poles if not np.isclose(p, pole))
    return (180 + angle_sum_zeros - angle_sum_poles) % 360

dep_upper = compute_departure(poles[2], poles, zeros)  # ≈ 322.69° (-37.31°)
dep_lower = compute_departure(poles[3], poles, zeros)  # ≈  37.31°

# ── Root locus data ──────────────────────────────────────────────────────────
rlist, klist = ct.root_locus(sys, plot=False)
plt.close('all')
rlist_arr = np.array(rlist)

# ── Colour palette ───────────────────────────────────────────────────────────
BG       = "#FFFFFF"
GRID     = '#D8D8D8'
TEXT     = '#000000'
DIM      = '#707070'
LOCUS    = '#0066CC'
ASYM     = '#FF8C00'
DEPART   = '#CC0000'
BRKPNT   = '#009900'
REAL_SEG = '#9933CC'
ZERO_C   = '#00AA88'
POLE_C   = '#CC0000'

# ── Figure setup ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 11))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# Grid lines
ax.axhline(0, color=GRID, lw=1.2, zorder=1)
ax.axvline(0, color=GRID, lw=1.2, zorder=1)
for v in np.arange(-14, 6, 2):
    ax.axvline(v, color=GRID, lw=0.4, alpha=0.5, zorder=1)
for v in np.arange(-12, 13, 2):
    ax.axhline(v, color=GRID, lw=0.4, alpha=0.5, zorder=1)

# ── 1. Root locus branches ───────────────────────────────────────────────────
for branch in range(rlist_arr.shape[1]):
    ax.plot(rlist_arr[:, branch].real, rlist_arr[:, branch].imag,
            color=LOCUS, lw=2.0, zorder=4, alpha=0.9)

# ── 2. Real-axis locus segments ──────────────────────────────────────────────
# Segments: [-inf, -2] and [-1, 0]  (left of odd count of real singularities)
ax.plot([-13, -2], [0, 0], color=REAL_SEG, lw=5, alpha=0.3,
        solid_capstyle='round', zorder=3)
ax.plot([-1,   0], [0, 0], color=REAL_SEG, lw=5, alpha=0.3,
        solid_capstyle='round', zorder=3)

# ── 3. Asymptotes ────────────────────────────────────────────────────────────
asym_angles_deg = [60, 180, 300]
asym_len = 13

for ang_deg in asym_angles_deg:
    ang = np.radians(ang_deg)
    ex  = centroid + asym_len * np.cos(ang)
    ey  =            asym_len * np.sin(ang)
    ax.plot([centroid, ex], [0, ey],
            color=ASYM, lw=1.4, linestyle='--', alpha=0.85, zorder=3)
    ax.annotate('', xy=(ex, ey), xytext=(centroid, 0),
                arrowprops=dict(arrowstyle='->', color=ASYM, lw=1.5,
                                linestyle='dashed'))
    # Angle label
    lbl_r = 2.8
    lx = centroid + lbl_r * np.cos(ang)
    ly =            lbl_r * np.sin(ang)
    display = ang_deg if ang_deg <= 180 else ang_deg - 360
    ax.text(lx, ly, f'{display}°', color=ASYM, fontsize=9, fontweight='bold',
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.2', fc='#F5F5F5', ec=ASYM, alpha=0.95))

# Centroid marker
ax.axvline(centroid, color=ASYM, lw=0.8, linestyle=':', alpha=0.6, zorder=2)
ax.plot(centroid, 0, 's', color=ASYM, ms=8, zorder=6)
ax.annotate(f'Centroid\nσₐ = −7/3 ≈ {centroid:.2f}',
            xy=(centroid, 0), xytext=(centroid + 1.4, -2.8),
            fontsize=9, color=ASYM, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=ASYM, lw=1.2),
            bbox=dict(boxstyle='round,pad=0.3', fc='#F5F5F5', ec=ASYM, alpha=0.95))

# ── 4. Departure angles ───────────────────────────────────────────────────────
departure_info = [
    (poles[2], dep_upper, (+0.4, +1.8)),   # upper complex pole
    (poles[3], dep_lower, (+0.4, -2.2)),   # lower complex pole
]
for pole, dep_ang_deg, lbl_off in departure_info:
    ang_rad = np.radians(dep_ang_deg)
    dep_len = 2.5
    ex = pole.real + dep_len * np.cos(ang_rad)
    ey = pole.imag + dep_len * np.sin(ang_rad)
    ax.annotate('', xy=(ex, ey), xytext=(pole.real, pole.imag),
                arrowprops=dict(arrowstyle='->', color=DEPART, lw=2.0))
    # Arc showing the angle
    arc_r = 1.2
    theta2 = dep_ang_deg % 360
    arc = mpatches.Arc((pole.real, pole.imag), 2*arc_r, 2*arc_r,
                        angle=0, theta1=0, theta2=theta2,
                        color=DEPART, lw=1.2, linestyle='--')
    ax.add_patch(arc)
    # Label
    actual_deg = dep_ang_deg if dep_ang_deg <= 180 else dep_ang_deg - 360
    ax.text(pole.real + lbl_off[0], pole.imag + lbl_off[1],
            f'φ_dep = {actual_deg:.1f}°',
            color=DEPART, fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', fc='#F5F5F5', ec=DEPART, alpha=0.95))

# ── 5. Angle-condition helper lines (to upper complex pole) ──────────────────
for src in [*poles, *zeros]:
    ax.plot([src.real, poles[2].real], [src.imag, poles[2].imag],
            color=DIM, lw=0.7, linestyle=':', alpha=0.3, zorder=2)

# ── 6. Break-away / Break-in points ──────────────────────────────────────────
bp_labels  = ['Break-away\ns₁ ≈ −0.572', 'Break-in\ns₂ ≈ −3.507']
bp_offsets = [(0, -1.8), (0, -1.8)]

for bp, lbl, off in zip(sorted(real_bp, reverse=True), bp_labels, bp_offsets):
    ax.plot(bp, 0, 'D', color=BRKPNT, ms=9, zorder=7,
            markeredgecolor='white', markeredgewidth=0.8)
    ax.annotate(lbl, xy=(bp, 0), xytext=(bp + off[0], off[1]),
                fontsize=9, color=BRKPNT, ha='center', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=BRKPNT, lw=1.2),
                bbox=dict(boxstyle='round,pad=0.3', fc='#F5F5F5', ec=BRKPNT, alpha=0.95))

# ── 7. Travel-direction arrows ────────────────────────────────────────────────
mid_idx = len(klist) // 4
for branch in range(rlist_arr.shape[1]):
    x0 = rlist_arr[mid_idx - 1, branch].real
    y0 = rlist_arr[mid_idx - 1, branch].imag
    x1 = rlist_arr[mid_idx + 1, branch].real
    y1 = rlist_arr[mid_idx + 1, branch].imag
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle='->', color=LOCUS,
                                lw=1.5, mutation_scale=14))

# ── 8. Poles (×) and Zeros (○) ───────────────────────────────────────────────
pole_labels   = ['p₁ = 0', 'p₂ = −1', 'p₃ = −4+j6.93', 'p₄ = −4−j6.93']
pole_offsets  = [(0.3, 0.7), (0.3, 0.7), (0.5, 0.9), (0.5, -1.2)]

for p, lbl, off in zip(poles, pole_labels, pole_offsets):
    ax.plot(p.real, p.imag, 'x', color=POLE_C, ms=14, mew=2.5, zorder=8)
    ax.text(p.real + off[0], p.imag + off[1], lbl,
            color=POLE_C, fontsize=9, fontweight='bold')

for z in zeros:
    ax.plot(z.real, z.imag, 'o', color=ZERO_C, ms=12, mew=2.0,
            markerfacecolor='none', markeredgecolor=ZERO_C, zorder=8)
    ax.text(z.real + 0.3, z.imag + 0.7, 'z₁ = −2',
            color=ZERO_C, fontsize=9, fontweight='bold')

# ── Axes cosmetics ───────────────────────────────────────────────────────────
ax.set_xlim(-14, 5)
ax.set_ylim(-12, 12)
ax.set_xlabel('Real Axis  (σ)',        fontsize=12, color=TEXT)
ax.set_ylabel('Imaginary Axis  (jω)', fontsize=12, color=TEXT)
ax.tick_params(colors=DIM, labelsize=10)
for spine in ax.spines.values():
    spine.set_edgecolor(GRID)

ax.set_title(
    'Root Locus Construction Drawing\n'
    r'$G(s)H(s) = \dfrac{K(s+2)}{s(s+1)(s^2+8s+64)}$',
    fontsize=15, fontweight='bold', color=TEXT, pad=14
)

# ── Legend ───────────────────────────────────────────────────────────────────
handles = [
    mpatches.Patch(color=LOCUS,                         label='Root locus branch'),
    mpatches.Patch(color=REAL_SEG, alpha=0.5,           label='Real-axis locus segment'),
    mpatches.Patch(color=ASYM,                          label='Asymptotes (60°, 180°, −60°)'),
    mpatches.Patch(color=DEPART,                        label='Departure angles (φ_dep)'),
    plt.Line2D([0],[0], marker='D', color=BRKPNT, ms=8, lw=0,
               label='Break-away / Break-in'),
    plt.Line2D([0],[0], marker='x', color=POLE_C, ms=10, mew=2, lw=0,
               label='Open-loop poles'),
    plt.Line2D([0],[0], marker='o', color=ZERO_C, ms=9,  mew=2, lw=0,
               markerfacecolor='none', label='Open-loop zero'),
]
ax.legend(handles=handles, loc='upper right', fontsize=9,
          facecolor='#F5F5F5', edgecolor=GRID, labelcolor=TEXT)

plt.tight_layout()
plt.savefig('root_locus_construction.png', dpi=200,
            bbox_inches='tight', facecolor=BG)
print("Saved → root_locus_construction.png")
# plt.show()   # uncomment for interactive display