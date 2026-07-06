import pandas as pd
import os
import glob

PROCESSED_DIR = r"d:\chandru project\RUL prediction\data\processed"
TEST_SAMPLES_DIR = r"d:\chandru project\RUL prediction\data\test_samples"

def export_all_anonymous_samples():
    os.makedirs(TEST_SAMPLES_DIR, exist_ok=True)
    
    old_files = glob.glob(os.path.join(TEST_SAMPLES_DIR, "*.csv"))
    for f in old_files:
        os.remove(f)
        
    df = pd.read_parquet(os.path.join(PROCESSED_DIR, "features.parquet"))
    
    features = ['cycle', 'SOH', 'capacity_fade_window', 'IR', 'Tavg', 'dQ_log_var', 'dQ_min', 'dQ_mean']
    df = df.dropna(subset=features + ['RUL'])
    
    from sklearn.model_selection import GroupShuffleSplit
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(df, groups=df['cell_id']))
    test_df = df.iloc[test_idx].copy()
    
    if test_df.empty:
        print("No test data found.")
        return
        
    test_cells = test_df['cell_id'].unique()
    
    for i, cell_id in enumerate(test_cells):
        sample_data = test_df[test_df['cell_id'] == cell_id].copy()
        out_path = os.path.join(TEST_SAMPLES_DIR, f"EV_Battery_Prototype_{i+1:02d}.csv")
        
        upload_cols = features + ['RUL']
        sample_data[upload_cols].to_csv(out_path, index=False)
        print(f"Exported {cell_id} as Prototype {i+1:02d} -> {out_path}")

if __name__ == "__main__":
    export_all_anonymous_samples()
