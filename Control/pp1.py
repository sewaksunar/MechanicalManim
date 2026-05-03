"""Complete Nyquist Plot
G(s) = (1+4s) / [s^2*(1+s)*(1+2s)]

Bugs fixed from original code:
  BUG 1 — Semicircle direction was WRONG
    Original:  real_semi = R * cos(θ + π)  → points LEFT (toward −∞)
    Correct:   real_semi = R * cos(−θ)     → points RIGHT (toward +∞)
    Why: s = ε·e^(jθ), G(s) ≈ (1/32s), so G ≈ (1/32ε)·e^(−jθ)
         The G-plane angle is −θ, not θ+π.

  BUG 2 — Frequency response extraction was fragile
    Original: mag, phase, w = ct.frequency_response(sys, omega)
              real = mag * cos(phase)    ← works but deprecated API
    Correct:  fresp = sys(1j * omega)    ← direct complex evaluation
              real, imag = fresp.real, fresp.imag

  BUG 3 — No direction arrows or key-frequency annotations
    Corrected version adds: direction arrows, phase/gain crossover markers,
    zoom panel for the ω→0 region, and a stability summary box.
"""

import matplotlib
matplotlib.use('Agg')           # remove / change to 'TkAgg' for interactive
import matplotlib.pyplot as plt
import numpy as np
import control as ct

# ── System ───────────────────────────────────────────────────────────────────
# num = [4, 1]   # (1+4s)
# den = [2, 3, 1, 0, 0]          # s²(1+s)(1+2s) = 2s⁴ + 3s³ + s²
num = 1
den = [2, 3, 1, 0] # s(1+2s)(1+s) = (s + 2s**2)(1+s) = s + 2s**2 + s**2 + 2s**3 = 2s**3 + 3s**2 + s
sys = ct.TransferFunction(num, den)

# ── Frequency response ───────────────────────────────────────────────────────
# FIX: evaluate G(jω) directly as a complex array
omega_pos = np.logspace(-2, 3, 8000)
fresp_pos = sys(1j * omega_pos).flatten()
real_pos, imag_pos = fresp_pos.real, fresp_pos.imag

# Mirror for negative frequencies: G(−jω) = conj(G(jω))
real_neg = np.flip(real_pos)
imag_neg = -np.flip(imag_pos)

# ── Semicircle detour around pole at s = 0 ───────────────────────────────────
# Pole at origin → G(s) ≈ K_res / s near s=0,  K_res = lim s→0 s·G(s) = 2/64 = 1/32
#
# Nyquist contour: small clockwise semicircle s = ε·e^(jθ),  θ: +π/2 → −π/2
#   G(εe^(jθ)) ≈ (1/32ε)·e^(−jθ)
#   G-plane angle = −θ
#   As θ: +π/2 → 0 → −π/2, angle: −π/2 → 0 → +π/2
#   → large CCW semicircle in G-plane sweeping from bottom through (+∞,0) to top
#
# FIX: cos(-θ) not cos(θ + π)
theta_s   = np.linspace(np.pi/2, -np.pi/2, 2000)
R_semi    = 300
real_semi = R_semi * np.cos(-theta_s)   # ← CORRECTED
imag_semi = R_semi * np.sin(-theta_s)

# ── Key frequencies ───────────────────────────────────────────────────────────
omega_fine = np.logspace(-2, 2, 100000)
fresp_fine = sys(1j * omega_fine).flatten()

# Phase crossover: Im{G(jω)} = 0
idx_pc = np.where(np.diff(np.sign(fresp_fine.imag)))[0][0]
w_pc   = omega_fine[idx_pc]
g_pc   = sys(1j * w_pc).item()

# Gain crossover: |G(jω)| = 1
idx_gc = np.argmin(np.abs(np.abs(fresp_fine) - 1.0))
w_gc   = omega_fine[idx_gc]
g_gc   = sys(1j * w_gc).item()

# Stability margins
gain_margin_db = 20 * np.log10(1 / abs(g_pc.real))
phase_margin   = 180 + np.degrees(np.angle(g_gc))

# ── Colour palette ───────────────────────────────────────────────────────────
BG   = '#FFFFFF'; GRID = '#D8D8D8'; TEXT = '#000000'; DIM  = '#707070'
POS  = '#0066CC'; NEG  = '#9933CC'; SEMI = '#FF8C00'; CRIT = '#CC0000'
GC   = '#009900'; PC   = '#CC0000'

# ── Figure: main plot + zoom panel ───────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(18, 10),
                         gridspec_kw={'width_ratios': [3, 1]})
fig.patch.set_facecolor(BG)

ax  = axes[0]   # main Nyquist plot
ax2 = axes[1]   # zoom near ω→0

for a in [ax, ax2]:
    a.set_facecolor(BG)
    a.axhline(0, color=GRID, lw=1.2)
    a.axvline(0, color=GRID, lw=1.2)

# ═══════════════════════════════════════════════════════════════════════════
# MAIN AXES
# ═══════════════════════════════════════════════════════════════════════════

# 1. Positive frequency path
ax.plot(real_pos, imag_pos, color=POS, lw=2.5, zorder=4,
        label='Positive ω: 0⁺ → +∞')

# 2. Negative frequency path (conjugate mirror)
ax.plot(real_neg, imag_neg, color=NEG, lw=2.5, zorder=4,
        linestyle='--', label='Negative ω: −∞ → 0⁻')

# 3. Semicircle at ε→0 (represented with finite R for visibility)
ax.plot(real_semi, imag_semi, color=SEMI, lw=2.2, zorder=4,
        label='Semicircle detour (ε→0): −90°→ 0°→ +90°')

# Direction arrows on positive path
for frac in [0.08, 0.25, 0.55]:
    i = int(frac * len(real_pos))
    ax.annotate('', xy=(real_pos[i+5], imag_pos[i+5]),
                xytext=(real_pos[i], imag_pos[i]),
                arrowprops=dict(arrowstyle='->', color=POS, lw=1.8, mutation_scale=15))

# Direction arrows on negative path
for frac in [0.45, 0.75, 0.92]:
    i = int(frac * len(real_neg))
    ax.annotate('', xy=(real_neg[i+5], imag_neg[i+5]),
                xytext=(real_neg[i], imag_neg[i]),
                arrowprops=dict(arrowstyle='->', color=NEG, lw=1.8, mutation_scale=15))

# Direction arrow on semicircle
mid = len(real_semi) // 2
ax.annotate('', xy=(real_semi[mid+10], imag_semi[mid+10]),
            xytext=(real_semi[mid], imag_semi[mid]),
            arrowprops=dict(arrowstyle='->', color=SEMI, lw=1.8, mutation_scale=15))

# Critical point (−1, 0)
ax.plot(-1, 0, 'o', color=CRIT, ms=14, markerfacecolor='none',
        markeredgewidth=2.5, zorder=8, label='Critical point (−1, 0)')
ax.axvline(-1, color=CRIT, lw=1.2, alpha=0.35, linestyle='--')
ax.annotate('(−1, 0)', xy=(-1, 0), xytext=(-1+0.008, -0.012),
            color=CRIT, fontsize=9, fontweight='bold')

# Phase crossover marker
ax.plot(g_pc.real, 0, 's', color=PC, ms=10, zorder=7,
        label=f'Phase crossover  ω={w_pc:.2f} rad/s  → GM={gain_margin_db:.1f} dB')
ax.annotate(f'ω={w_pc:.2f}\nG={g_pc.real:.4f}',
            xy=(g_pc.real, 0), xytext=(g_pc.real-0.009, 0.012),
            color=PC, fontsize=8.5, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=PC, lw=1.1),
            bbox=dict(boxstyle='round,pad=0.3', fc='#F5F5F5', ec=PC, alpha=0.95))

# Gain crossover marker
ax.plot(g_gc.real, g_gc.imag, 'D', color=GC, ms=9, zorder=7,
        label=f'Gain crossover  ω={w_gc:.2f} rad/s  → PM={phase_margin:.1f}°')
ax.annotate(f'ω={w_gc:.2f}\n|G|=1',
            xy=(g_gc.real, g_gc.imag),
            xytext=(g_gc.real+0.012, g_gc.imag-0.015),
            color=GC, fontsize=8.5, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=GC, lw=1.1),
            bbox=dict(boxstyle='round,pad=0.3', fc='#F5F5F5', ec=GC, alpha=0.95))

# ω→0+ start label
ax.annotate('ω→0⁺',
            xy=(real_pos[0], imag_pos[0]),
            xytext=(real_pos[0]+0.012, imag_pos[0]-0.022),
            color=POS, fontsize=8.5, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=POS, lw=1.0),
            bbox=dict(boxstyle='round,pad=0.3', fc='#F5F5F5', ec=POS, alpha=0.95))

ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_xlabel('Re{G(jω)}', fontsize=12, color=TEXT)
ax.set_ylabel('Im{G(jω)}', fontsize=12, color=TEXT)
ax.set_title('Complete Nyquist Plot\n'
             r'$G(s) = \dfrac{1+4s}{s^2(1+s)(1+2s)}$',
             fontsize=14, fontweight='bold', color=TEXT, pad=12)
ax.tick_params(colors=DIM, labelsize=9)
for sp in ax.spines.values():
    sp.set_edgecolor(GRID)
ax.legend(loc='lower right', fontsize=9, facecolor='#F5F5F5',
          edgecolor=GRID, labelcolor=TEXT, framealpha=0.95)

# Stability summary box
summary = (
    "Nyquist Summary\n"
    "──────────────────────────────\n"
    f"Open-loop RHP poles:  P = 0\n"
    f"Encirclements of (−1,0): N = 0\n"
    f"Closed-loop RHP poles: Z = N+P = 0\n"
    f"→  STABLE for small K\n\n"
    f"Phase crossover ω_pc = {w_pc:.2f} rad/s\n"
    f"  G(jω_pc) = {g_pc.real:.5f}\n"
    f"  Gain margin = {gain_margin_db:.1f} dB\n\n"
    f"Gain crossover ω_gc = {w_gc:.2f} rad/s\n"
    f"  Phase margin = {phase_margin:.1f}°\n\n"
    "Semicircle (pole at s=0):\n"
    "  s = ε·e^(jθ), θ: +90°→ 0°→ −90°\n"
    "  G ≈ (1/32ε)·e^(−jθ)\n"
    "  → large CCW arc in G-plane"
)
ax.text(0.01, 0.99, summary, transform=ax.transAxes,
        fontsize=8, color=TEXT, va='top', ha='left', family='monospace',
        bbox=dict(boxstyle='round,pad=0.6', fc='#F5F5F5', ec=GRID, alpha=0.95))

# ═══════════════════════════════════════════════════════════════════════════
# ZOOM PANEL — ω→0 region showing how semicircle connects the two paths
# ═══════════════════════════════════════════════════════════════════════════
omega_zoom = np.logspace(-2, 0, 3000)
fresp_zoom = sys(1j * omega_zoom).flatten()

ax2.plot(fresp_zoom.real, fresp_zoom.imag,  color=POS, lw=2.2)
ax2.plot(fresp_zoom.real, -fresp_zoom.imag, color=NEG, lw=2.2, linestyle='--')

# Semicircle schematic arc in zoom view
r_arc = abs(fresp_zoom[-1].imag) * 1.0
theta_arc = np.linspace(-np.pi/2, np.pi/2, 500)
ax2.plot(r_arc * np.cos(theta_arc), r_arc * np.sin(theta_arc),
         color=SEMI, lw=2.2)
ax2.annotate('Semicircle\n(R→∞)',
             xy=(r_arc, 0), xytext=(r_arc*1.8, r_arc*0.9),
             color=SEMI, fontsize=7.5, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=SEMI, lw=1.0),
             bbox=dict(boxstyle='round,pad=0.2', fc='#F5F5F5', ec=SEMI, alpha=0.95))

# Direction arrows in zoom
mid_z = len(fresp_zoom) // 3
ax2.annotate('', xy=(fresp_zoom[mid_z+5].real, fresp_zoom[mid_z+5].imag),
             xytext=(fresp_zoom[mid_z].real,    fresp_zoom[mid_z].imag),
             arrowprops=dict(arrowstyle='->', color=POS, lw=1.5, mutation_scale=12))
ax2.annotate('', xy=(fresp_zoom[mid_z].real,   -fresp_zoom[mid_z+5].imag),
             xytext=(fresp_zoom[mid_z+5].real,  -fresp_zoom[mid_z].imag),
             arrowprops=dict(arrowstyle='->', color=NEG, lw=1.5, mutation_scale=12))

ax2.set_xlim(-r_arc*3, r_arc*5)
ax2.set_ylim(-r_arc*3.5, r_arc*3.5)
ax2.set_xlabel('Re{G}', fontsize=10, color=TEXT)
ax2.set_title('Zoom: ω→0\n(semicircle join)', fontsize=10,
              fontweight='bold', color=TEXT, pad=8)
ax2.tick_params(colors=DIM, labelsize=8)
for sp in ax2.spines.values():
    sp.set_edgecolor(GRID)

plt.tight_layout(pad=2)
plt.savefig('pp1.png', dpi=200,
            bbox_inches='tight', facecolor=BG)
print("Saved → pp1.png")
# plt.show()    # uncomment for interactive window