import pandas as pd
import numpy as np
import os

TEST_SAMPLES_DIR = r"d:\chandru project\RUL prediction\data\test_samples"

def generate_synthetic_lfp():
    os.makedirs(TEST_SAMPLES_DIR, exist_ok=True)
    
    # Remove the MIT ones
    for f in os.listdir(TEST_SAMPLES_DIR):
        os.remove(os.path.join(TEST_SAMPLES_DIR, f))
        
    np.random.seed(42)
    
    # We will generate 5 synthetic LFP batteries based on general empirical models
    # Q(n) = Q0 - A * exp(B * n) - C * n
    # We'll vary the parameters to get different cycle lives
    
    configs = [
        {"name": "Synthetic_LFP_Standard_Discharge", "life": 1200, "noise": 0.001},
        {"name": "Synthetic_LFP_Fast_Charge", "life": 600, "noise": 0.002},
        {"name": "Synthetic_LFP_High_Temp", "life": 800, "noise": 0.0015},
        {"name": "Synthetic_LFP_Low_Temp", "life": 1500, "noise": 0.0008},
        {"name": "Synthetic_LFP_Eco_Mode", "life": 2000, "noise": 0.0005},
    ]
    
    for config in configs:
        max_cycle = config["life"]
        cycles = np.arange(10, max_cycle, 5)
        
        # Empirical SOH degradation
        # Starts at 1.0, degrades to ~0.8 at max_cycle
        soh = 1.0 - 0.2 * (cycles / max_cycle)**1.5 + np.random.normal(0, config["noise"], len(cycles))
        soh = np.clip(soh, 0.8, 1.0)
        
        # SOH fade window (derivative)
        fade = np.gradient(soh) * 10 
        
        # Internal Resistance (increases over time from 0.015 to ~0.025)
        ir = 0.015 + 0.01 * (cycles / max_cycle) + np.random.normal(0, 0.0001, len(cycles))
        
        # Tavg (Temperature average)
        tavg = 32.0 + 3.0 * (cycles / max_cycle) + np.random.normal(0, 0.5, len(cycles))
        
        # dQ features (Voltage curve variance, typical values for LFP)
        dq_log_var = -6.0 - 1.5 * (cycles / max_cycle) + np.random.normal(0, 0.1, len(cycles))
        dq_min = -0.001 - 0.003 * (cycles / max_cycle) + np.random.normal(0, 0.0002, len(cycles))
        dq_mean = -0.0005 - 0.001 * (cycles / max_cycle) + np.random.normal(0, 0.0001, len(cycles))
        
        rul = max_cycle - cycles
        
        df = pd.DataFrame({
            'cycle': cycles,
            'SOH': soh,
            'capacity_fade_window': fade,
            'IR': ir,
            'Tavg': tavg,
            'dQ_log_var': dq_log_var,
            'dQ_min': dq_min,
            'dQ_mean': dq_mean,
            'RUL': rul
        })
        
        out_path = os.path.join(TEST_SAMPLES_DIR, f"{config['name']}.csv")
        df.to_csv(out_path, index=False)
        print(f"Generated independent synthetic data: {out_path}")

if __name__ == "__main__":
    generate_synthetic_lfp()
