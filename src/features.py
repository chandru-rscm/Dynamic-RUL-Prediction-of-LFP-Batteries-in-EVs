import pandas as pd
import numpy as np
import os

PROCESSED_DIR = r"d:\chandru project\RUL prediction\data\processed"
WINDOW_SIZE = 10
STEP_SIZE = 5

def extract_features(df):
    feature_rows = []
    grouped = df.groupby('cell_id')
    
    for cell_id, group in grouped:
        group = group.sort_values('cycle').reset_index(drop=True)
        cycle_life = group['cycle_life'].iloc[0]
        batch = group['batch'].iloc[0]
        
        nominal_QD = group['QD'].iloc[:10].max() if len(group) > 10 else group['QD'].max()
        if nominal_QD == 0 or np.isnan(nominal_QD):
            continue
            
        for idx in range(WINDOW_SIZE, len(group), STEP_SIZE):
            current_row = group.iloc[idx]
            past_row = group.iloc[idx - WINDOW_SIZE]
            
            k = current_row['cycle']
            rul = cycle_life - k
            if rul < 0:
                continue
                
            qd_current = current_row['QD']
            qd_past = past_row['QD']
            
            SOH = qd_current / nominal_QD
            capacity_fade = (qd_past - qd_current) / nominal_QD
            
            ir_current = current_row['IR']
            tavg_current = current_row['Tavg']
            
            q_var = np.nan
            q_min = np.nan
            q_mean = np.nan
            
            try:
                qdlin_curr = current_row['Qdlin']
                qdlin_past = past_row['Qdlin']
                
                if qdlin_curr is not None and qdlin_past is not None:
                    qdlin_curr = np.array(qdlin_curr)
                    qdlin_past = np.array(qdlin_past)
                    
                    if len(qdlin_curr) > 0 and len(qdlin_curr) == len(qdlin_past):
                        delta_q = qdlin_curr - qdlin_past
                        
                        var_val = np.var(delta_q)
                        q_var = np.log10(np.abs(var_val)) if var_val > 1e-10 else -10
                        
                        q_min = np.min(delta_q)
                        q_mean = np.mean(delta_q)
            except Exception:
                pass
                
            feature_rows.append({
                'cell_id': cell_id,
                'batch': batch,
                'cycle': k,
                'cycle_life': cycle_life,
                'RUL': rul,
                'SOH': SOH,
                'capacity_fade_window': capacity_fade,
                'IR': ir_current,
                'Tavg': tavg_current,
                'dQ_log_var': q_var,
                'dQ_min': q_min,
                'dQ_mean': q_mean
            })
            
    return pd.DataFrame(feature_rows)

def main():
    in_path = os.path.join(PROCESSED_DIR, "cycles.parquet")
    print(f"Loading {in_path}...")
    df = pd.read_parquet(in_path)
    
    print("Extracting dynamic features...")
    feat_df = extract_features(df)
    feat_df = feat_df.dropna(subset=['dQ_log_var'])
    
    out_path = os.path.join(PROCESSED_DIR, "features.parquet")
    feat_df.to_parquet(out_path, index=False)
    
    print(f"Extracted {len(feat_df)} dynamic checkpoints.")
    print(f"Saved features to {out_path}")

if __name__ == "__main__":
    main()
