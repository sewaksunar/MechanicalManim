"""
Root Locus Construction Drawing
G(s)H(s) = K / [s(s+1)(s^2+4s+5)]

Construction elements:
  - Root locus branches
  - Real-axis locus segment  [-1, 0]
  - 4 Asymptotes: 45°, 135°, 225°(−135°), 315°(−45°)
  - Asymptote centroid  σₐ = −5/4
  - Departure angles from complex poles  p₃,₄ = −2 ± j
  - Break-away point on real axis
  - Travel-direction arrows
  - Angle-condition helper lines
  - Construction summary box
"""

import matplotlib
matplotlib.use('Agg')           # remove / change to 'TkAgg' for interactive window
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import control as ct
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ── System definition ────────────────────────────────────────────────────────
# Denominator: s(s+1)(s^2+4s+5) = s^4 + 5s^3 + 9s^2 + 5s
num = [1]
den = [1, 5, 9, 5, 0]
sys = ct.TransferFunction(num, den)

poles = np.array([0+0j, -1+0j, -2+1j, -2-1j])
zeros = np.array([])          # no finite zeros

# ── Pre-computed construction values ─────────────────────────────────────────
# Asymptote centroid: (Σpoles − Σzeros) / (n − m)
centroid = -5 / 4    # exact: (0−1−2−2) / 4

# Asymptote angles: (2k+1)×180° / (n−m),  k = 0,1,2,3
asym_angles_deg = [45, 135, 225, 315]

# Breakaway: no zeros → K = −D(s)/N(s) = −D(s)
#   dK/ds = 0  →  D'(s) = 0
#   D = s^4+5s^3+9s^2+5s  →  D' = 4s^3+15s^2+18s+5 = 0
bp_poly  = [4, 15, 18, 5]
bp_roots = np.roots(bp_poly)
real_bp  = bp_roots[np.abs(bp_roots.imag) < 1e-6].real   # ≈ [−0.393]

# Departure angles from complex poles  p₃ = −2+j,  p₄ = −2−j
def compute_departure(pole, all_poles, all_zeros):
    """Angle condition: φ_dep = 180° + Σ∠zeros − Σ∠other_poles  (mod 360°)"""
    angle_zeros = sum(np.degrees(np.angle(pole - z)) for z in all_zeros) if len(all_zeros) else 0
    angle_poles = sum(np.degrees(np.angle(pole - p))
                      for p in all_poles if not np.isclose(p, pole))
    return (180 + angle_zeros - angle_poles) % 360

p3 = poles[2]   # −2+j
p4 = poles[3]   # −2−j
dep_upper = compute_departure(p3, poles, zeros)   # ≈ 161.57°
dep_lower = compute_departure(p4, poles, zeros)   # ≈ 198.43°

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
POLE_C   = '#CC0000'

# ── Figure setup ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 11))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ax.axhline(0, color=GRID, lw=1.2, zorder=1)
ax.axvline(0, color=GRID, lw=1.2, zorder=1)
for v in np.arange(-10, 4, 1):
    ax.axvline(v, color=GRID, lw=0.4, alpha=0.4, zorder=1)
for v in np.arange(-8, 9, 1):
    ax.axhline(v, color=GRID, lw=0.4, alpha=0.4, zorder=1)

# ── 1. Root locus branches ───────────────────────────────────────────────────
for branch in range(rlist_arr.shape[1]):
    ax.plot(rlist_arr[:, branch].real, rlist_arr[:, branch].imag,
            color=LOCUS, lw=2.0, zorder=4, alpha=0.9)

# ── 2. Real-axis locus segment: [−1, 0] ──────────────────────────────────────
ax.plot([-1, 0], [0, 0], color=REAL_SEG, lw=6, alpha=0.3,
        solid_capstyle='round', zorder=3)
ax.annotate('Real-axis locus\n[−1 , 0]',
            xy=(-0.5, 0), xytext=(-0.5, 1.2),
            fontsize=9, color=REAL_SEG, ha='center', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=REAL_SEG, lw=1.2),
            bbox=dict(boxstyle='round,pad=0.3', fc='#F5F5F5', ec=REAL_SEG, alpha=0.95))

# ── 3. Asymptotes ─────────────────────────────────────────────────────────────
asym_len = 9
for ang_deg in asym_angles_deg:
    ang = np.radians(ang_deg)
    ex  = centroid + asym_len * np.cos(ang)
    ey  =            asym_len * np.sin(ang)
    ax.plot([centroid, ex], [0, ey],
            color=ASYM, lw=1.4, linestyle='--', alpha=0.85, zorder=3)
    ax.annotate('', xy=(ex, ey), xytext=(centroid, 0),
                arrowprops=dict(arrowstyle='->', color=ASYM, lw=1.5))
    # Angle label
    lbl_r = 2.2
    lx = centroid + lbl_r * np.cos(ang)
    ly =            lbl_r * np.sin(ang)
    display = ang_deg if ang_deg <= 180 else ang_deg - 360
    ax.text(lx, ly, f'{display}°', color=ASYM, fontsize=9, fontweight='bold',
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.2', fc='#F5F5F5', ec=ASYM, alpha=0.95))

# Angle arcs at centroid
for ang_deg in [45, 135]:
    arc = mpatches.Arc((centroid, 0), 1.2, 1.2,
                        angle=0, theta1=0, theta2=ang_deg,
                        color=ASYM, lw=1.0, linestyle='--', alpha=0.7)
    ax.add_patch(arc)

# Centroid marker
ax.axvline(centroid, color=ASYM, lw=0.8, linestyle=':', alpha=0.6, zorder=2)
ax.plot(centroid, 0, 's', color=ASYM, ms=9, zorder=6)
ax.annotate(f'Centroid\nσₐ = −5/4 = {centroid:.2f}',
            xy=(centroid, 0), xytext=(centroid + 1.0, -2.2),
            fontsize=9, color=ASYM, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=ASYM, lw=1.2),
            bbox=dict(boxstyle='round,pad=0.3', fc='#F5F5F5', ec=ASYM, alpha=0.95))

# ── 4. Departure angles ───────────────────────────────────────────────────────
for pole, dep_ang_deg, lbl_off in [
        (p3, dep_upper, (-2.5, +1.2)),
        (p4, dep_lower, (-2.5, -1.6))]:
    ang_rad = np.radians(dep_ang_deg)
    dep_len = 1.8
    ex = pole.real + dep_len * np.cos(ang_rad)
    ey = pole.imag + dep_len * np.sin(ang_rad)
    ax.annotate('', xy=(ex, ey), xytext=(pole.real, pole.imag),
                arrowprops=dict(arrowstyle='->', color=DEPART, lw=2.2))
    # Arc
    arc = mpatches.Arc((pole.real, pole.imag), 1.8, 1.8,
                        angle=0, theta1=0, theta2=dep_ang_deg % 360,
                        color=DEPART, lw=1.1, linestyle='--')
    ax.add_patch(arc)
    # Label
    actual = dep_ang_deg if dep_ang_deg <= 180 else dep_ang_deg - 360
    ax.text(pole.real + lbl_off[0], pole.imag + lbl_off[1],
            f'φ_dep = {actual:.1f}°',
            color=DEPART, fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', fc='#F5F5F5', ec=DEPART, alpha=0.95))

# ── 5. Angle-condition helper lines (to upper complex pole p3) ────────────────
for src in poles:
    if not np.isclose(src, p3):
        ax.plot([src.real, p3.real], [src.imag, p3.imag],
                color=DIM, lw=0.8, linestyle=':', alpha=0.35, zorder=2)

# ── 6. Break-away point ───────────────────────────────────────────────────────
bp = real_bp[0]
ax.plot(bp, 0, 'D', color=BRKPNT, ms=10, zorder=7,
        markeredgecolor='white', markeredgewidth=0.8)
ax.annotate(f'Break-away\ns₁ ≈ {bp:.3f}',
            xy=(bp, 0), xytext=(bp + 0.15, -1.5),
            fontsize=9, color=BRKPNT, ha='center', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=BRKPNT, lw=1.2),
            bbox=dict(boxstyle='round,pad=0.3', fc='#F5F5F5', ec=BRKPNT, alpha=0.95))

# ── 7. Travel-direction arrows on branches ────────────────────────────────────
mid_idx = len(klist) // 5
for branch in range(rlist_arr.shape[1]):
    x0 = rlist_arr[mid_idx - 1, branch].real
    y0 = rlist_arr[mid_idx - 1, branch].imag
    x1 = rlist_arr[mid_idx + 1, branch].real
    y1 = rlist_arr[mid_idx + 1, branch].imag
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle='->', color=LOCUS,
                                lw=1.5, mutation_scale=14))

# ── 8. Poles (×) ─────────────────────────────────────────────────────────────
pole_labels  = ['p₁ = 0', 'p₂ = −1', 'p₃ = −2+j', 'p₄ = −2−j']
pole_offsets = [(0.15, 0.3), (0.15, 0.3), (0.2, 0.35), (0.2, -0.55)]
for p, lbl, off in zip(poles, pole_labels, pole_offsets):
    ax.plot(p.real, p.imag, 'x', color=POLE_C, ms=14, mew=2.5, zorder=8)
    ax.text(p.real + off[0], p.imag + off[1], lbl,
            color=POLE_C, fontsize=9, fontweight='bold')

# ── Summary box ───────────────────────────────────────────────────────────────
summary = (
    "Construction Summary\n"
    "────────────────────────\n"
    "Poles: 0, −1, −2±j\n"
    "Zeros: none  (m = 0)\n"
    "Branches → ∞: 4\n"
    "Centroid σₐ = −1.25\n"
    "Asymptote angles:\n"
    "  45°, 135°, −135°, −45°\n"
    "Real-axis locus: [−1, 0]\n"
    "Break-away: s ≈ −0.393\n"
    "φ_dep (p₃) = +161.6°\n"
    "φ_dep (p₄) = −161.6°"
)
ax.text(0.765, 0.97, summary, transform=ax.transAxes,
        fontsize=8.5, color=TEXT, va='top', ha='left', family='monospace',
        bbox=dict(boxstyle='round,pad=0.6', fc='#F5F5F5', ec=GRID, alpha=0.95))

# ── Axes cosmetics ────────────────────────────────────────────────────────────
ax.set_xlim(-9, 3)
ax.set_ylim(-7, 7)
ax.set_xlabel('Real Axis  (σ)',        fontsize=12, color=TEXT)
ax.set_ylabel('Imaginary Axis  (jω)', fontsize=12, color=TEXT)
ax.tick_params(colors=DIM, labelsize=10)
for spine in ax.spines.values():
    spine.set_edgecolor(GRID)

ax.set_title(
    'Root Locus Construction Drawing\n'
    r'$G(s)H(s) = \dfrac{K}{s(s+1)(s^2+4s+5)}$',
    fontsize=15, fontweight='bold', color=TEXT, pad=14
)

# ── Legend ────────────────────────────────────────────────────────────────────
handles = [
    mpatches.Patch(color=LOCUS,               label='Root locus branch'),
    mpatches.Patch(color=REAL_SEG, alpha=0.5, label='Real-axis locus [−1, 0]'),
    mpatches.Patch(color=ASYM,                label='Asymptotes (45°,135°,−135°,−45°)'),
    mpatches.Patch(color=DEPART,              label='Departure angles (φ_dep)'),
    plt.Line2D([0],[0], marker='D', color=BRKPNT, ms=8, lw=0, label='Break-away point'),
    plt.Line2D([0],[0], marker='x', color=POLE_C, ms=10, mew=2, lw=0, label='Open-loop poles'),
]
ax.legend(handles=handles, loc='lower right', fontsize=9,
          facecolor='#F5F5F5', edgecolor=GRID, labelcolor=TEXT)

plt.tight_layout()
plt.savefig('root_locus_construction_2.jpg', dpi=200,
            bbox_inches='tight', facecolor=BG)
print("Saved → root_locus_construction_2.jpg")
plt.show()    # uncomment for interactive window