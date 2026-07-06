import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import GroupShuffleSplit

PROJ_ROOT = r"d:\chandru project\RUL prediction"
FIG_DIR = os.path.join(PROJ_ROOT, "results", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

df = pd.read_parquet(os.path.join(PROJ_ROOT, "data", "processed", "features.parquet"))
feats = ['cycle', 'SOH', 'capacity_fade_window', 'IR', 'Tavg', 'dQ_log_var', 'dQ_min', 'dQ_mean']
df = df.dropna(subset=feats + ['RUL']).sort_values(['cell_id', 'cycle']).reset_index(drop=True)

gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(gss.split(df, groups=df['cell_id']))
test_df = df.iloc[test_idx].copy()

# Pick cell 12 or cell 26 from test set
cell_id = test_df['cell_id'].unique()[0]
cell_data = test_df[test_df['cell_id'] == cell_id].sort_values('cycle')

cycles = cell_data['cycle'].values
soh = cell_data['SOH'].values
r0 = cell_data['IR'].values
r1 = r0 * (1.2 + (1.0 - soh) * 2.0)
c1 = np.maximum(10.0, soh * 400.0)
tau = r1 * c1

poles = -1.0 / tau
zeros = -(r0 + r1) / (r0 * r1 * c1)

plt.figure(figsize=(10, 5))

# Plot full lifecycle migration path colored by cycle
sc = plt.scatter(poles, np.zeros_like(poles), c=cycles, cmap='viridis', s=35, alpha=0.8, label='Pole Migration Path (Lifecycle)')
cbar = plt.colorbar(sc)
cbar.set_label("Operating Cycle Age", fontsize=11, fontweight='bold')

# Highlight Healthy State (Early Cycle ~12)
idx_early = 0
plt.scatter(poles[idx_early], 0, color='green', s=140, marker='x', linewidths=3, label=f'Healthy Pole (Cycle {int(cycles[idx_early])})')
plt.scatter(zeros[idx_early], 0, facecolors='none', edgecolors='green', s=140, linewidths=2.5, label=f'Healthy Zero (Cycle {int(cycles[idx_early])})')

# Highlight Degraded State (Late Cycle ~860)
idx_late = len(cycles) - 1
plt.scatter(poles[idx_late], 0, color='red', s=140, marker='x', linewidths=3, label=f'Aged Pole (Cycle {int(cycles[idx_late])})')
plt.scatter(zeros[idx_late], 0, facecolors='none', edgecolors='blue', s=140, linewidths=2.5, label=f'Aged Zero (Cycle {int(cycles[idx_late])})')

# Dotted arrow showing rightward migration towards zero boundary
plt.annotate("", xy=(poles[idx_late], 0.05), xytext=(poles[idx_early], 0.05),
             arrowprops=dict(arrowstyle="->", color="black", lw=2, ls="--"))
plt.text((poles[idx_early] + poles[idx_late])/2, 0.08, "Impedance Growth Pole Migration ➔", ha='center', fontweight='bold', fontsize=11)

plt.axhline(0, color='gray', linestyle='-', linewidth=1)
plt.axvline(0, color='red', linestyle=':', linewidth=1.5, label='Instability Boundary (s = 0)')

plt.ylim(-0.4, 0.4)
plt.xlabel("Real Axis σ (rad/s) [Stability Degradation Trajectory ➔]", fontsize=12, fontweight='bold')
plt.ylabel("Imaginary Axis jω", fontsize=12, fontweight='bold')
plt.title(f"Complex s-Plane Pole-Zero Migration Map ({cell_id})\nLaplace Transfer Function Tracking Impedance Growth", fontsize=13, fontweight='bold')
plt.legend(loc='upper right', framealpha=0.9, fontsize=10)
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()

# Save to both locations
out1 = os.path.join(FIG_DIR, "07_pole_zero_migration_map.png")
out2 = os.path.join(FIG_DIR, "05_dynamic_trajectory_example.png")
plt.savefig(out1, dpi=300)
plt.savefig(out2, dpi=300)
plt.close()

print(f"Pole-Zero Migration Map successfully generated and saved to:\n1. {out1}\n2. {out2}")
