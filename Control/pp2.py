import numpy as np
import control as ct
import matplotlib.pyplot as plt
# num = [4, 1]   # (1+4s)
# den = [2, 3, 1, 0, 0]          # s²(1+s)(1+2s) = 2s⁴ + 3s³ + s²
# num = 1
# den = [2, 3, 1, 0] # s(1+2s)(1+s) = (s + 2s**2)(1+s) = s + 2s**2 + s**2 + 2s**3 = 2s**3 + 3s**2 + s

num = [1, 2]   # (s + 2)
den = [1, 0, -1] # (s-1)(s+1) = s² - 1
W = ct.TransferFunction(num, den)

print("="*60)
print("Transfer Function:")
print("="*60)
print(W)
print("="*60)

# Get margins using control library
gm, pm, wgc, wpc = ct.margin(W)
gain_margin_db = 20 * np.log10(gm)

print(f"Gain Margin: {gain_margin_db:.3f} dB at ω_pc = {wpc:.3f} rad/s")
print(f"Phase Margin: {pm:.3f}° at ω_gc = {wgc:.3f} rad/s")

plt.figure(figsize=(12, 10))

# Use nyquist_plot() - auto-scales to show entire plot
ct.nyquist_plot(W)

# Find real axis intersections (where Im{G(jω)} = 0)
omega = np.logspace(-3, 2, 5000)
G = W(1j * omega)
real_part = G.real.flatten()
imag_part = G.imag.flatten()
mag_part = np.abs(G).flatten()

# Find zero crossings of imaginary part (phase crossover)
zero_crossings = np.where(np.diff(np.sign(imag_part)))[0]

print("\nReal Axis Intersections:")
for idx in zero_crossings:
    real_val = real_part[idx]
    # Mark intersection point
    plt.plot(real_val, 0, 'ro', markersize=12, markeredgewidth=2.5, 
             markerfacecolor='none', zorder=5, label='Phase crossover (∠G = -180°)' if idx == zero_crossings[0] else '')
    # Add label
    plt.annotate(f'({real_val:.3f}, 0)', xy=(real_val, 0), 
                xytext=(real_val+1, 1.5), fontsize=10, color='red',
                fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
    print(f"  Real = {real_val:.4f}")

# Find gain crossover (|G(jω)| = 1)
idx_gc = np.argmin(np.abs(mag_part - 1.0))
G_gc = G.flatten()[idx_gc]
plt.plot(G_gc.real, G_gc.imag, 'bs', markersize=12, markeredgewidth=2.5, 
         markerfacecolor='none', zorder=5, label='Gain crossover (|G| = 1)')
plt.annotate(f'ω_gc={omega[idx_gc]:.3f} rad/s\n|G|=1', xy=(G_gc.real, G_gc.imag), 
            xytext=(G_gc.real+0.5, G_gc.imag+0.5), fontsize=10, color='blue',
            fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='blue', lw=1.5))

# Mark critical point (-1, 0)
plt.plot(-1, 0, 'k*', markersize=20, zorder=6, label='Critical point (-1, 0)')

# Draw construction line: from origin to (-1,0) showing -180° line
plt.plot([-2, 0], [0, 0], 'k--', linewidth=2, alpha=0.5, zorder=2)
plt.axvline(-1, color='gray', linestyle=':', alpha=0.5, linewidth=1.5)

# Draw unit circle (for reference)
circle = plt.Circle((0, 0), 1, fill=False, linestyle='--', color='green', alpha=0.3, linewidth=2)
plt.gca().add_patch(circle)

plt.xlabel('Real Axis', fontsize=12, fontweight='bold')
plt.ylabel('Imaginary Axis', fontsize=12, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.title(f'Nyquist Plot - G(s) = 1/[s(1+2s)(1+s)]\nGain Margin: {gain_margin_db:.2f} dB | Phase Margin: {pm:.2f}°',
          fontsize=13, fontweight='bold')
plt.legend(fontsize=11, loc='best')
plt.axhline(0, color='k', linewidth=0.5)
plt.axvline(0, color='k', linewidth=0.5)

plt.savefig('pp2.png', dpi=300)
plt.show()



