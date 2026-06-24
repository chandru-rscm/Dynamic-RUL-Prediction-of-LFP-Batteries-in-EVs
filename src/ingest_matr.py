import os
import glob
import h5py
import pandas as pd
import numpy as np

RAW_DIR = r"d:\chandru project\RUL prediction\data\raw"
PROCESSED_DIR = r"d:\chandru project\RUL prediction\data\processed"

def load_matr_batch(filepath, batch_name):
    print(f"Loading {filepath}...")
    try:
        f = h5py.File(filepath, 'r')
    except Exception as e:
        print(f"Failed to open {filepath}: {e}")
        return []
        
    batch = f['batch']
    num_cells = batch['summary'].shape[0]
    
    rows = []
    
    for i in range(num_cells):
        try:
            summary_ref = batch['summary'][i, 0]
            cycles_ref = batch['cycles'][i, 0]
            policy_ref = batch['policy_readable'][i, 0]
            cycle_life_ref = batch['cycle_life'][i, 0]
            
            summary = f[summary_ref]
            cycles = f[cycles_ref]
            
            # Read policy
            policy = f[policy_ref]
            policy_str = "".join([chr(c[0]) for c in policy])
            
            # Read cycle life
            cycle_life = f[cycle_life_ref][0, 0]
            
            cell_id = f"{batch_name}_cell_{i}"
            
            # Read summary arrays
            IR = summary['IR'][0, :]
            QC = summary['QCharge'][0, :]
            QD = summary['QDischarge'][0, :]
            Tavg = summary['Tavg'][0, :]
            
            num_cycles = cycles['I'].shape[0]
            
            for j in range(num_cycles):
                # Only use valid cycles where summary QD > 0
                if j >= len(QD) or QD[j] < 0.01:
                    continue
                    
                row = {
                    'batch': batch_name,
                    'cell_id': cell_id,
                    'policy': policy_str,
                    'cycle_life': cycle_life,
                    'cycle': j + 1,  # 1-indexed cycles
                    'IR': IR[j],
                    'QC': QC[j],
                    'QD': QD[j],
                    'Tavg': Tavg[j]
                }
                
                # Try to extract Qdlin (interpolated discharge capacity)
                try:
                    Qdlin_ref = cycles['Qdlin'][j, 0]
                    Qdlin = f[Qdlin_ref][:].flatten()
                    # We store it as a list of floats
                    row['Qdlin'] = Qdlin.tolist()
                except Exception:
                    row['Qdlin'] = None
                    
                rows.append(row)
        except Exception as e:
            print(f"Error processing cell {i} in {batch_name}: {e}")
            
    f.close()
    return rows

def main():
    mat_files = glob.glob(os.path.join(RAW_DIR, "*.mat"))
    if not mat_files:
        print("No .mat files found in data/raw/")
        return
        
    all_rows = []
    for filepath in mat_files:
        filename = os.path.basename(filepath)
        # Extract batch name, e.g., "2017-05-12"
        batch_name = filename.split('_')[0]
        batch_rows = load_matr_batch(filepath, batch_name)
        all_rows.extend(batch_rows)
        
    if not all_rows:
        print("No data extracted.")
        return
        
    df = pd.DataFrame(all_rows)
    print(f"Extracted {len(df)} total cycles across all cells.")
    
    # Save to parquet
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    out_path = os.path.join(PROCESSED_DIR, "cycles.parquet")
    
    # Pyarrow can handle list columns natively
    df.to_parquet(out_path, engine='pyarrow', index=False)
    print(f"Saved processed data to {out_path}")

if __name__ == "__main__":
    main()
