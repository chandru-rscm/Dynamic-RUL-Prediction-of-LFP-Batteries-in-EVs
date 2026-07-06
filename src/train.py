import pandas as pd
import numpy as np
import os
import lightgbm as lgb
from sklearn.metrics import mean_absolute_percentage_error, mean_absolute_error, r2_score
import joblib

PROCESSED_DIR = r"d:\chandru project\RUL prediction\data\processed"
MODEL_DIR = r"d:\chandru project\RUL prediction\src\models"

def train_dynamic_model():
    in_path = os.path.join(PROCESSED_DIR, "features.parquet")
    if not os.path.exists(in_path):
        print("Features file not found. Run features.py first.")
        return
        
    df = pd.read_parquet(in_path)
    
    features = ['cycle', 'SOH', 'capacity_fade_window', 'IR', 'Tavg', 'dQ_log_var', 'dQ_min', 'dQ_mean']
    target = 'RUL'
    
    df = df.dropna(subset=features + [target])
    
    from sklearn.model_selection import GroupShuffleSplit
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(df, groups=df['cell_id']))
    
    train_df = df.iloc[train_idx].copy()
    test_df = df.iloc[test_idx].copy()
    
    X_train = train_df[features]
    y_train = train_df[target]
    
    X_test = test_df[features]
    y_test = test_df[target]
    
    print(f"Training on {len(X_train)} checkpoints, Testing on {len(X_test)} checkpoints.")
    
    model = lgb.LGBMRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=7,
        num_leaves=31,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    
    y_test_safe = np.clip(y_test, 1, None)
    preds_safe = np.clip(preds, 0, None)
    
    mape = mean_absolute_percentage_error(y_test_safe, preds_safe)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    
    print("\n--- DYNAMIC TEST SET RESULTS ---")
    print(f"Test R2 Score: {r2:.4f}")
    print(f"Test MAE: {mae:.2f} cycles")
    print(f"Test MAPE: {mape*100:.2f}%\n")
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, "lightgbm_rul.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")
    
    importance = model.feature_importances_
    print("--- Feature Importance ---")
    for f, imp in zip(features, importance):
        print(f"{f}: {imp}")

if __name__ == "__main__":
    train_dynamic_model()
