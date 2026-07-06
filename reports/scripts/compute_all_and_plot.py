import os
import sys
import time
import pandas as pd
import numpy as np
import lightgbm as lgb
import matplotlib.pyplot as plt
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import mean_absolute_error, r2_score, confusion_matrix

# Ensure directories exist
PROJ_ROOT = r"d:\chandru project\RUL prediction"
REPORTS_DIR = os.path.join(PROJ_ROOT, "reports")
FIG_DIR = os.path.join(PROJ_ROOT, "results", "figures")
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

df = pd.read_parquet(os.path.join(PROJ_ROOT, "data", "processed", "features.parquet"))
feats = ['cycle', 'SOH', 'capacity_fade_window', 'IR', 'Tavg', 'dQ_log_var', 'dQ_min', 'dQ_mean']
df = df.dropna(subset=feats + ['RUL']).sort_values(['cell_id', 'cycle']).reset_index(drop=True)

gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(gss.split(df, groups=df['cell_id']))
train_df, test_df = df.iloc[train_idx].copy(), df.iloc[test_idx].copy()

X_train, y_train = train_df[feats], train_df['RUL']
X_test, y_test = test_df[feats], test_df['RUL']

opt_model = lgb.LGBMRegressor(n_estimators=300, num_leaves=31, min_child_samples=7, learning_rate=0.05, random_state=42, verbose=-1)
opt_model.fit(X_train, y_train)

test_preds = opt_model.predict(X_test)
test_mae = mean_absolute_error(y_test, test_preds)
test_r2 = r2_score(y_test, test_preds)
test_std = np.std(np.abs(test_preds - y_test))

print(f"Optimal Model Test MAE: {test_mae:.2f} | R2: {test_r2*100:.2f}% | Std Dev: {test_std:.2f} cycles")

# 1. RE-PLOT 01_true_vs_predicted_rul.png with EXACT MATCHING TITLE
plt.figure(figsize=(8, 6))
plt.scatter(y_test, test_preds, alpha=0.4, color='#0284C7', s=15, label='Test Cell Predictions')
max_val = max(y_test.max(), test_preds.max())
plt.plot([0, max_val], [0, max_val], 'r--', lw=2, label='Perfect Prediction Identity')
plt.xlabel("Observed Cycle Life (True RUL)", fontsize=12, fontweight='bold')
plt.ylabel("Predicted Cycle Life (AI Output)", fontsize=12, fontweight='bold')
plt.title(f"True vs Predicted Remaining Useful Life\nUnseen Test Cohort (MAE: {test_mae:.2f} cycles | R²: {test_r2*100:.2f}%)", fontsize=13, fontweight='bold')
plt.legend(loc='upper left')
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "01_true_vs_predicted_rul.png"), dpi=300)
plt.close()

# 2. COMPUTE CONFUSION MATRIX FOR REPLACEMENT ALERT (Threshold RUL <= 100 cycles)
alert_threshold = 100
true_alert = (y_test <= alert_threshold).astype(int)
pred_alert = (test_preds <= alert_threshold).astype(int)
cm = confusion_matrix(true_alert, pred_alert)

fig, ax = plt.subplots(figsize=(7, 5))
cax = ax.matshow(cm, cmap=plt.cm.Blues)
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(j, i, str(cm[i, j]), va='center', ha='center', size=20, weight='bold',
                color='white' if cm[i, j] > cm.max()/2 else 'black')

ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_xticklabels(['Healthy (>100c)', 'Replace Alert (<=100c)'], fontsize=11, fontweight='bold')
ax.set_yticklabels(['True Healthy (>100c)', 'True Dying (<=100c)'], fontsize=11, fontweight='bold')
ax.xaxis.set_ticks_position('bottom')
plt.xlabel("AI Dashboard Prediction", fontsize=12, fontweight='bold')
plt.ylabel("Actual Battery Condition", fontsize=12, fontweight='bold')
plt.title("Prognostic Maintenance Confusion Matrix\n(Replacement Alert Window: RUL ≤ 100 cycles)", fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "06_confusion_matrix.png"), dpi=300)
plt.close()

tn, fp, fn, tp = cm.ravel()
accuracy = (tp + tn) / (tp + tn + fp + fn) * 100
precision = tp / max(1, tp + fp) * 100
recall = tp / max(1, tp + fn) * 100
print(f"Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp} | Alert Accuracy: {accuracy:.2f}% | Precision: {precision:.2f}% | Recall: {recall:.2f}%")

# 3. BENCHMARK EXECUTION SPEED
start_time = time.perf_counter()
n_runs = 1000
for _ in range(n_runs):
    _ = opt_model.predict(X_test.iloc[:1])
end_time = time.perf_counter()
avg_ms = ((end_time - start_time) / n_runs) * 1000.0
print(f"Execution Speed Benchmark: Single sample inference time = {avg_ms:.4f} ms")

sys.stdout.flush()
