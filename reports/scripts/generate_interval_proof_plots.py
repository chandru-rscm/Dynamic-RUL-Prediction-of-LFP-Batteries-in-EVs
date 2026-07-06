import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

PROCESSED_DIR = r"d:\chandru project\RUL prediction\data\processed"
OUT_DIR = r"d:\chandru project\RUL prediction\results\figures"
ROOT_DIR = r"d:\chandru project\RUL prediction"

os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_parquet(os.path.join(PROCESSED_DIR, "features.parquet"))

# Select cell 19 which exhibits a textbook rapid non-linear capacity plunge near 80% SOH
cell_df = df[df['cell_id'] == '2017-05-12_cell_19'].sort_values('cycle')

# Zoom into the critical aging window: Cycles 580 to 787
window_df = cell_df[(cell_df['cycle'] >= 580) & (cell_df['cycle'] <= 787)].copy()

# --- DIAGRAM 1: 5-Cycle Polling Interval ---
plt.figure(figsize=(10, 5.5), dpi=300)
plt.plot(window_df['cycle'], window_df['SOH'], color='#95a5a6', lw=2, linestyle='--', label='True Physical Degradation Curve')

# Every row in features.parquet is recorded at 5-cycle intervals
df_5 = window_df.copy()
plt.plot(df_5['cycle'], df_5['SOH'], color='#102C57', lw=2.5, label='AI Polling Trajectory (Every 5 Cycles)')
plt.scatter(df_5['cycle'], df_5['SOH'], color='#28a745', s=65, zorder=5, edgecolors='black', lw=1, label='Diagnostic Checkpoint (5-Cycle Resolution)')

plt.axhline(0.81, color='#e74c3c', linestyle=':', lw=2, label='End-of-Life Replacement Warning Threshold')

# Precise Annotation pointing to dense tracking during the drop
target_row = df_5[df_5['cycle'] == 752].iloc[0]
plt.annotate('High-Resolution Polling:\nCatches capacity drop immediately at every 5-cycle step!', 
             xy=(target_row['cycle'], target_row['SOH']),
             xytext=(595, 0.825),
             arrowprops=dict(facecolor='#28a745', shrink=0.08, width=2, headwidth=8),
             fontsize=11.5, fontweight='bold', color='#145A32',
             bbox=dict(boxstyle="round,pad=0.6", fc="#EAFAF1", ec="#28a745", lw=1.5))

plt.title('5-Cycle Polling Interval (High-Precision Continuous Tracking)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Battery Cycle Number', fontsize=12.5, fontweight='bold')
plt.ylabel('State of Health (Normalized Capacity)', fontsize=12.5, fontweight='bold')
plt.ylim(0.80, 0.93)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper right', framealpha=0.95, fontsize=10.5)

path_5 = os.path.join(OUT_DIR, "proof_interval_5_cycles.png")
plt.savefig(path_5, bbox_inches='tight')
plt.savefig(os.path.join(ROOT_DIR, "proof_interval_5_cycles.png"), bbox_inches='tight')
plt.close()

# --- DIAGRAM 2: 20-Cycle Polling Interval ---
plt.figure(figsize=(10, 5.5), dpi=300)
plt.plot(window_df['cycle'], window_df['SOH'], color='#95a5a6', lw=2, linestyle='--', label='True Physical Degradation Curve')

# Subsample every 4th step = 20 cycles apart
df_20 = window_df.iloc[::4].copy()
plt.plot(df_20['cycle'], df_20['SOH'], color='#c0392b', lw=2.5, label='AI Polling Trajectory (Every 20 Cycles)')
plt.scatter(df_20['cycle'], df_20['SOH'], color='#e74c3c', s=85, zorder=5, marker='s', edgecolors='black', lw=1, label='Diagnostic Checkpoint (20-Cycle Resolution)')

plt.axhline(0.81, color='#e74c3c', linestyle=':', lw=2, label='End-of-Life Replacement Warning Threshold')

# Highlight the 20-cycle gap where steep degradation occurs
target_x = df_20['cycle'].iloc[-3]
target_y = df_20['SOH'].iloc[-3]

plt.annotate('20-Cycle Polling Gap:\nSevere blind spot during non-linear capacity drop!', 
             xy=(target_x, target_y),
             xytext=(595, 0.825),
             arrowprops=dict(facecolor='#c0392b', shrink=0.08, width=2, headwidth=8),
             fontsize=11.5, fontweight='bold', color='#78281F',
             bbox=dict(boxstyle="round,pad=0.6", fc="#FDEDEC", ec="#c0392b", lw=1.5))

plt.title('20-Cycle Polling Interval (Inspection Blind Spot During Plunge)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Battery Cycle Number', fontsize=12.5, fontweight='bold')
plt.ylabel('State of Health (Normalized Capacity)', fontsize=12.5, fontweight='bold')
plt.ylim(0.80, 0.93)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper right', framealpha=0.95, fontsize=10.5)

path_20 = os.path.join(OUT_DIR, "proof_interval_20_cycles.png")
plt.savefig(path_20, bbox_inches='tight')
plt.savefig(os.path.join(ROOT_DIR, "proof_interval_20_cycles.png"), bbox_inches='tight')
plt.close()

print(f"Clean 5-cycle plot saved to: {path_5}")
print(f"Clean 20-cycle plot saved to: {path_20}")
