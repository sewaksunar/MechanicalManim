"""
Root Locus Plot for the transfer function:
G(s)H(s) = K(s+2) / (s(s+1)(s^2+8s+64))

The root locus shows how the closed-loop poles vary with gain K from 0 to ∞.
"""

import control as ct
import matplotlib.pyplot as plt
import numpy as np
import warnings

# Suppress the deprecation warning for root_locus (using it temporarily)
warnings.filterwarnings('ignore', message='root_locus.*deprecated')


def plot_root_locus():
    """
    Create and display the root locus plot for the given transfer function.
    """
    # Define the numerator and denominator polynomials
    # Numerator: K(s+2), use K=1 as the root locus function handles gain variation
    num = [1, 2]  # (s+2)
    
    # Denominator: s(s+1)(s^2+8s+64)
    # First expand: s(s+1) = s^2 + s
    # Then multiply by (s^2+8s+64): (s^2+s)(s^2+8s+64) = s^4 + 8s^3 + 64s^2 + s^3 + 8s^2 + 64s
    #                                                    = s^4 + 9s^3 + 72s^2 + 64s
    den = [1, 9, 72, 64, 0]  # s^4 + 9s^3 + 72s^2 + 64s
    
    # Create transfer function
    sys = ct.TransferFunction(num, den)
    
    print("Open-Loop Transfer Function:")
    print(sys)
    print("\nPoles of open-loop system:")
    poles = ct.poles(sys)
    print(poles)
    print("\nZeros of open-loop system:")
    zeros = ct.zeros(sys)
    print(zeros)
    
    # Verify root locus properties
    n_poles = len(poles)
    n_zeros = len(zeros)
    n_branches_to_infinity = n_poles - n_zeros
    
    print(f"\n--- Root Locus Properties ---")
    print(f"Number of poles: {n_poles}")
    print(f"Number of zeros: {n_zeros}")
    print(f"Branches to infinity: {n_branches_to_infinity}")
    
    # Asymptote center (centroid)
    centroid = (np.sum(poles) - np.sum(zeros)) / (n_poles - n_zeros)
    print(f"Asymptote center: {centroid:.4f}")
    
    # Asymptote angles
    angles = [(2*k + 1)*180 / (n_poles - n_zeros) for k in range(n_poles - n_zeros)]
    print(f"Asymptote angles (degrees): {angles}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 9))
    
    # Use control's root_locus with built-in plotting to matplotlib axes
    ct.root_locus(sys, plot=True)
    
    # Get current axes
    ax = plt.gca()
    
    # Customize the plot
    ax.set_xlabel('Real Axis (σ)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Imaginary Axis (ω)', fontsize=13, fontweight='bold')
    ax.set_title('Root Locus Plot: G(s)H(s) = K(s+2) / [s(s+1)(s²+8s+64)]', 
                 fontsize=15, fontweight='bold', pad=15)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_aspect('equal', adjustable='box')
    
    # Save the plot
    output_file = 'root_locus_plot.jpg'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n[SAVED] Plot saved to: {output_file}")
    plt.show()


if __name__ == "__main__":
    plot_root_locus()