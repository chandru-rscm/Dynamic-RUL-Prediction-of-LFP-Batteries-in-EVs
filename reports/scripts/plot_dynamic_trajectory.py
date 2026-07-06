import os
import pandas as pd
import numpy as np
import lightgbm as lgb
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
train_df, test_df = df.iloc[train_idx].copy(), df.iloc[test_idx].copy()

X_train, y_train = train_df[feats], train_df['RUL']
opt_model = lgb.LGBMRegressor(n_estimators=300, num_leaves=31, min_child_samples=7, learning_rate=0.05, random_state=42, verbose=-1)
opt_model.fit(X_train, y_train)

# Pick cell_12 or first test cell
cell_id = test_df['cell_id'].unique()[0]
cell_data = test_df[test_df['cell_id'] == cell_id].sort_values('cycle')

cycles = cell_data['cycle'].values
true_rul = cell_data['RUL'].values
preds = opt_model.predict(cell_data[feats])

# 90% Conformal band (+/- 122 cycles)
q_margin = 122.0
lower = np.maximum(0, preds - q_margin)
upper = preds + q_margin

plt.figure(figsize=(10, 5))
plt.plot(cycles, true_rul, 'k--', lw=2.5, label='True Observed RUL')
plt.plot(cycles, preds, color='#0284C7', lw=2, label='AI Predicted RUL (LightGBM)')
plt.fill_between(cycles, lower, upper, color='#0284C7', alpha=0.25, label='90% Conformal Safety Bracket (±122 cycles)')

plt.xlabel("Current Operating Cycle Age", fontsize=12, fontweight='bold')
plt.ylabel("Remaining Useful Life (Cycles)", fontsize=12, fontweight='bold')
plt.title(f"Dynamic Real-Time RUL Trajectory with Safety Brackets\nUnseen Test Battery ({cell_id})", fontsize=13, fontweight='bold')
plt.legend(loc='upper right', fontsize=11, framealpha=0.9)
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()

out_path = os.path.join(FIG_DIR, "05_dynamic_trajectory_example.png")
plt.savefig(out_path, dpi=300)
plt.close()
print(f"True Dynamic RUL Trajectory plot saved to: {out_path}")
