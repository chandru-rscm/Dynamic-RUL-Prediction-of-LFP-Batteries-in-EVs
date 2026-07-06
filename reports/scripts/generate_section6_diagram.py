import os
import matplotlib.pyplot as plt
import numpy as np

os.makedirs(r"reports\figures", exist_ok=True)

def generate_pole_zero_migration():
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

    # Simulate trajectory of poles from healthy cycle 12 to aged cycle 867/897
    cycles = np.linspace(12, 897, 25)
    # R0 increases from 0.0162 to 0.0196
    # R1 increases from 0.0195 to 0.0310
    # C1 adjusts such that tau = R1*C1 increases from 7.78s to 10.02s
    # pole p = -1/tau goes from -1/7.78 = -0.1285 to -1/10.02 = -0.0998
    poles = -1.0 / np.linspace(7.78, 10.02, 25)
    zeros = -1.0 * (1.0 + np.linspace(0.0195, 0.0310, 25)/np.linspace(0.0162, 0.0196, 25)) / np.linspace(7.78, 10.02, 25)

    # Color mapping by cycle age
    sc_p = ax.scatter(poles, np.zeros_like(poles), c=cycles, cmap='viridis', s=80, marker='x', linewidth=2.5, label='Pole Migration Path $p(t)$')
    sc_z = ax.scatter(zeros, np.zeros_like(zeros), c=cycles, cmap='viridis', s=70, marker='o', facecolors='none', edgecolors='C0', linewidth=1.5, alpha=0.6, label='Zero Migration Path $z(t)$')

    # Highlight specific points
    ax.scatter([-0.1285], [0.0], color='#2E7D32', s=130, marker='X', zorder=5, label='Healthy Pole (Cycle 12: $-0.1285$ rad/s)')
    ax.scatter([-0.0998], [0.0], color='#D32F2F', s=130, marker='X', zorder=5, label='Aged Pole (Cycle 897: $-0.0998$ rad/s)')
    ax.scatter([-0.2827], [0.0], color='#1976D2', s=110, marker='o', zorder=5, label='Healthy Zero (Cycle 12: $-0.2827$ rad/s)')

    # Stability Boundary
    ax.axvline(0.0, color='#C62828', linestyle='--', linewidth=1.8, label='Instability Boundary ($\sigma = 0$)')
    ax.axhline(0.0, color='#888888', linestyle=':', linewidth=1.0)

    # Arrow showing migration direction
    ax.annotate('Impedance Growth Pole Migration $\\rightarrow$', xy=(-0.103, 0.08), xytext=(-0.125, 0.08),
                arrowprops=dict(color='#D32F2F', arrowstyle='-|>,head_width=0.3,head_length=0.4', lw=2),
                fontsize=9.5, fontweight='bold', color='#B71C1C', ha='center')

    ax.set_title("Complex s-Plane Pole-Zero Migration Map (Cell '2017-05-12_cell_12')\nLaplace Transfer Function Tracking SEI Film Thickening & Impedance Growth", fontsize=11, fontweight='bold')
    ax.set_xlabel("Real Axis $\sigma$ (rad/s) [Stability Degradation Trajectory $\\rightarrow$]", fontsize=10, fontweight='bold')
    ax.set_ylabel("Imaginary Axis $j\\omega$ (rad/s)", fontsize=10, fontweight='bold')
    ax.set_xlim(-0.31, 0.03)
    ax.set_ylim(-0.25, 0.25)
    ax.grid(True, linestyle='--', alpha=0.4)

    cbar = plt.colorbar(sc_p, ax=ax, pad=0.02)
    cbar.set_label('Operating Cycle Age', fontsize=10, fontweight='bold')

    ax.legend(loc='lower left', fontsize=8.5, framealpha=0.95)

    plt.tight_layout()
    out_path = r"reports\figures\pole_zero_migration.png"
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved pole_zero_migration.png")

if __name__ == "__main__":
    generate_pole_zero_migration()
