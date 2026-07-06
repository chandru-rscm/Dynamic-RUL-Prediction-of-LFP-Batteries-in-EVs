import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score

PROCESSED_DIR = r"d:\chandru project\RUL prediction\data\processed"
MODEL_DIR = r"d:\chandru project\RUL prediction\src\models"
RESULTS_DIR = r"d:\chandru project\RUL prediction\results\figures"

def generate_static_plots():
    in_path = os.path.join(PROCESSED_DIR, "features.parquet")
    model_path = os.path.join(MODEL_DIR, "lightgbm_rul.pkl")
    
    if not os.path.exists(in_path) or not os.path.exists(model_path):
        print("Run train.py first to generate model and features.")
        return
        
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    df = pd.read_parquet(in_path)
    model = joblib.load(model_path)
    
    features = ['cycle', 'SOH', 'capacity_fade_window', 'IR', 'Tavg', 'dQ_log_var', 'dQ_min', 'dQ_mean']
    target = 'RUL'
    
    df = df.dropna(subset=features + [target])
    
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(df, groups=df['cell_id']))
    
    test_df = df.iloc[test_idx].copy()
    X_test = test_df[features]
    y_test = test_df[target]
    
    preds = model.predict(X_test)
    preds = np.clip(preds, 0, None)
    test_df['Predicted_RUL'] = preds
    
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    print(f"Generating plots... Test MAE: {mae:.2f}, R2: {r2:.4f}")
    
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, preds, alpha=0.3, color='blue', edgecolors='none', s=15)
    max_val = max(y_test.max(), preds.max())
    plt.plot([0, max_val], [0, max_val], 'r--', lw=2, label="Perfect Prediction")
    plt.xlabel('Observed Cycle Life (True RUL)', fontsize=12)
    plt.ylabel('Predicted Cycle Life', fontsize=12)
    plt.title(f'True vs Predicted RUL\n(Test Set - MAE: {mae:.1f} cycles)', fontsize=14)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig(os.path.join(RESULTS_DIR, "01_true_vs_predicted_rul.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    importances = model.feature_importances_
    indices = np.argsort(importances)
    sorted_features = [features[i] for i in indices]
    sorted_importances = importances[indices]
    
    plt.figure(figsize=(10, 6))
    plt.barh(range(len(indices)), sorted_importances, color='teal', align='center')
    plt.yticks(range(len(indices)), sorted_features, fontsize=11)
    plt.xlabel('LightGBM Feature Importance (Split count)', fontsize=12)
    plt.title('Feature Importance for RUL Prediction', fontsize=14)
    plt.grid(axis='x', linestyle='--', alpha=0.6)
    plt.savefig(os.path.join(RESULTS_DIR, "02_feature_importance.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    residuals = y_test - preds
    plt.figure(figsize=(8, 6))
    plt.hist(residuals, bins=30, color='purple', alpha=0.7, edgecolor='black')
    plt.axvline(x=0, color='r', linestyle='--', lw=2)
    plt.xlabel('Prediction Error (True - Predicted Cycles)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title('Distribution of Prediction Errors', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig(os.path.join(RESULTS_DIR, "03_prediction_errors_histogram.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    plt.figure(figsize=(10, 6))
    cells = test_df['cell_id'].unique()
    
    min_life = test_df['cycle_life'].min()
    max_life = test_df['cycle_life'].max()
    norm = plt.Normalize(min_life, max_life)
    cmap = cm.viridis
    
    for cell in cells:
        cell_data = test_df[test_df['cell_id'] == cell].sort_values('cycle')
        c_life = cell_data['cycle_life'].iloc[0]
        color = cmap(norm(c_life))
        plt.plot(cell_data['cycle'], cell_data['SOH'], alpha=0.7, color=color, lw=1.5)
        
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=plt.gca())
    cbar.set_label('Cycle Life', rotation=270, labelpad=15)
    
    plt.xlabel('Cycle Number', fontsize=12)
    plt.ylabel('State of Health (Normalized Capacity)', fontsize=12)
    plt.title('Capacity Fade Curves for Test Set Batteries', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig(os.path.join(RESULTS_DIR, "04_capacity_fade_curves.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    long_cells = test_df[test_df['cycle_life'] > 800]['cell_id'].unique()
    if len(long_cells) > 0:
        sample_cell = long_cells[0]
        cell_data = test_df[test_df['cell_id'] == sample_cell].sort_values('cycle')
        
        plt.figure(figsize=(10, 6))
        plt.plot(cell_data['cycle'], cell_data['RUL'], 'k--', label='True RUL', lw=2)
        plt.plot(cell_data['cycle'], cell_data['Predicted_RUL'], 'b-', label='Predicted RUL', marker='o', markersize=4)
        
        q_hat = 122.0
        plt.fill_between(cell_data['cycle'], 
                         np.maximum(0, cell_data['Predicted_RUL'] - q_hat), 
                         cell_data['Predicted_RUL'] + q_hat, 
                         color='blue', alpha=0.2, label='90% Confidence Interval')
                         
        plt.xlabel('Current Cycle', fontsize=12)
        plt.ylabel('Remaining Useful Life (Cycles)', fontsize=12)
        plt.title(f'Dynamic RUL Prediction Trajectory\n(Cell: {sample_cell})', fontsize=14)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.savefig(os.path.join(RESULTS_DIR, "05_dynamic_trajectory_example.png"), dpi=300, bbox_inches='tight')
        plt.close()

    print("All 5 plots generated successfully!")

if __name__ == "__main__":
    generate_static_plots()
