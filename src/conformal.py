import pandas as pd
import numpy as np
import os
import joblib

PROCESSED_DIR = r"d:\chandru project\RUL prediction\data\processed"
MODEL_DIR = r"d:\chandru project\RUL prediction\src\models"

def main():
    in_path = os.path.join(PROCESSED_DIR, "features.parquet")
    model_path = os.path.join(MODEL_DIR, "lightgbm_rul.pkl")
    
    if not os.path.exists(in_path) or not os.path.exists(model_path):
        print("Run train.py first to generate model and features.")
        return
        
    df = pd.read_parquet(in_path)
    model = joblib.load(model_path)
    features = ['cycle', 'SOH', 'capacity_fade_window', 'IR', 'Tavg', 'dQ_log_var', 'dQ_min', 'dQ_mean']
    target = 'RUL'
    
    # Drop any NaNs
    df = df.dropna(subset=features + [target])
    
    # Use the same split as training
    from sklearn.model_selection import GroupShuffleSplit
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(df, groups=df['cell_id']))
    
    train_df = df.iloc[train_idx].copy()
    test_df = df.iloc[test_idx].copy()
    
    X_cal = train_df[features]
    y_cal = train_df[target]
    
    # Compute residuals on calibration set
    # Note: For a true split-conformal approach, we would hold out a dedicated calibration set.
    # To maximize data in this POC, we calibrate on the train set residuals (approximate conformal).
    cal_preds = model.predict(X_cal)
    residuals = np.abs(y_cal - cal_preds)
    
    # 90% confidence interval
    alpha = 0.10
    n = len(residuals)
    q_level = np.ceil((n + 1) * (1 - alpha)) / n
    q_level = min(q_level, 1.0)
    
    q_hat = np.quantile(residuals, q_level)
    print(f"Calibrated 90% Uncertainty Bound: ±{q_hat:.2f} cycles")
    
    # Evaluate coverage on test set
    X_test = test_df[features]
    y_test = test_df[target]
    
    test_preds = model.predict(X_test)
    lower_bound = np.maximum(0, test_preds - q_hat) # RUL cannot be < 0
    upper_bound = test_preds + q_hat
    
    # Coverage probability
    coverage = np.mean((y_test >= lower_bound) & (y_test <= upper_bound))
    print(f"Test Set Empirical Coverage: {coverage*100:.2f}% (Target: { (1-alpha)*100 }%)")
    
if __name__ == "__main__":
    main()
