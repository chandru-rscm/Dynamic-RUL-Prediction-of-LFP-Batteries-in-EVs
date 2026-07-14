# 🧠 Project & Conversation Master Context (For AI Assistant on New Laptop)

> **Instructions for AI Assistant on New Laptop:**  
> Read this document carefully upon your first turn. This is the **Master Context Transfer** summarizing the entire history, mathematical formulations, architectural decisions, file layout, and user preferences for the **Dynamic Remaining Useful Life (RUL) & Electrochemical Stability Prediction of LFP Batteries in EV Applications** project.

---

## 1. Project Overview & Core Philosophy

We have developed a state-of-the-art, human-verified, physics-informed machine learning and control theory framework for predicting the cycle life and electrochemical stability of Lithium Iron Phosphate (LFP) batteries under fast-charging EV protocols.

### Key Breakthrough over Static Early-Cycle RUL:
* Traditional battery prognostic papers (like Severson et al., 2019) only predict total lifetime once from early cycles (e.g., cycle 100).
* **Our Approach**: **Dynamic Multi-Checkpoint Prognostics**. We predict Remaining Useful Life ($\text{RUL} = N_{\text{EOL}} - N_{\text{current}}$) dynamically across the entire life of the battery as it ages (e.g., every 5 to 20 cycles, using sliding/rolling windows).

---

## 2. Core Technical & Mathematical Frameworks

### A. Physics-Informed Feature Engineering (`src/features.py`)
We extract physical domain features from raw MATLAB/HDF5 battery discharge/charge curves (`data/processed/cycles.parquet`):
1. **$\Delta Q(V)$ Log-Variance**: Variance of the capacity difference curve between consecutive cycles across voltage steps. Log-transformed to capture early interfacial SEI growth.
2. **Internal Resistance Growth ($\Delta R_{\text{int}}$)**: Normalized resistance growth relative to early baseline cycles.
3. **Thermal Dissipation ($T_{\text{avg}}, T_{\text{max}}$)**: Mean and peak surface temperature during fast charging.
4. **Normalized State of Health ($\text{SOH}$)**: $\text{SOH}(N) = \frac{Q(N)}{Q_{\text{nominal}}}$.

### B. Machine Learning & Conformal Prediction (`src/train.py`, `src/conformal.py`)
* **Regressor**: LightGBM (`LGBMRegressor`), trained using a **Leave-One-Cell-Out (LOCO) grouped 80/20 cell split** (`GroupKFold` / `GroupShuffleSplit`) to ensure strict evaluation on unseen cells.
* **Performance**: Test $R^2 \approx 0.93$, Mean Absolute Percentage Error (MAPE) $\approx 9.0\%$.
* **Conformal Uncertainty Calibration**: Distribution-free split conformal prediction generating mathematically guaranteed **90% confidence intervals ($\pm \hat{q}$ cycles)** around predicted RUL, enabling risk-aware Battery Management System (BMS) decisions.

### C. 2nd-Order Control Theory & Stability Analysis (`demo/app.py`)
To mathematically prove the transition from gradual degradation to rapid End-of-Life (EOL) capacity drop-off, we model battery transport lag and interfacial impedance as a **2nd-Order Linear Dynamical System (Laplace Transfer Function)**:
$$G(s) = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$
Where the damping ratio $\zeta$ is directly driven by the battery's $\text{SOH}$ threshold:
1. **Healthy Overdamped Regime ($\text{SOH} > 80\%, \zeta \ge 1.0$)**:
   * Roots of the characteristic equation ($s^2 + 2\zeta\omega_n s + \omega_n^2 = 0$) lie entirely on the negative real axis ($\text{Im}(s) = 0$).
   * Represents predictable, linear electrochemical aging.
2. **Critical Damping / Bifurcation Point ($\text{SOH} = 80\%, \zeta = 1.00$)**:
   * The exact threshold where real poles collide and bifurcate/split into the complex plane.
   * Marks the onset of severe electrochemical imbalance and accelerated capacity fade.
3. **Imaginary Axis Strike / EOL Instability ($\text{SOH} < 80\%, \zeta < 1.0 \to 0.00$)**:
   * As $\zeta \to 0$, complex conjugate poles ($s = -\zeta\omega_n \pm j\omega_n\sqrt{1-\zeta^2}$) migrate across the left-half $s$-plane toward the imaginary axis ($\text{Re}(s) = 0$).
   * At $\zeta = 0$, poles strike the imaginary axis, mathematically proving catastrophic electrochemical breakdown / oscillatory instability.

---

## 3. Codebase & Repository Layout

```text
Dynamic-RUL-Prediction-of-LFP-Batteries-in-EVs/
│
├── README.md                 <-- Comprehensive guide with download & setup steps
├── requirements.txt          <-- Python dependencies (numpy, pandas, lightgbm, streamlit, plotly, etc.)
├── .gitignore                <-- Strictly ignores large data, models, reports, docs, ppts (keeps repo code-clean)
│
├── src/
│   ├── ingest_matr.py        <-- Converts raw MIT/Stanford MATLAB (.mat) files -> cycles.parquet
│   ├── features.py           <-- Extracts dynamic physics-informed features -> features.parquet
│   ├── train.py              <-- Trains LightGBM model, evaluates LOCO test metrics, saves lightgbm_rul.pkl
│   ├── conformal.py          <-- Computes 90% conformal prediction bounds
│   ├── evaluate.py           <-- Generates evaluation plots and metrics
│   └── utils/
│       ├── export_sample.py  <-- Exports sample test CSVs for dashboard upload
│       ├── fix_synthetic.py  <-- Cleans/formats sample prototype CSVs
│       └── generate_synthetic.py
│
├── demo/
│   └── app.py                <-- Interactive Streamlit Dashboard (3 Modules: Unseen Test Simulation, Custom CSV Upload, 2nd-Order Root Locus Simulation)
│
├── data/                     <-- (Ignored by git except folder structure)
│   ├── raw/                  <-- Raw downloaded .mat batch files
│   ├── processed/            <-- cycles.parquet & features.parquet
│   └── test_samples/         <-- Sample test CSVs ready for custom UI upload
│
└── results/
    └── figures/              <-- 8 Core result plots (01_true_vs_predicted_rul.png ... 08_proof_interval_20_cycles.png)
```

> **Note on Local Submission Folders**: In our previous session, we also organized a local non-git folder (`ppt, docs, figures`) on your hard drive (`D:\chandru downloads\...` and local workspace) containing all final Word manuscripts (`.docx`), LaTeX source (`.tex`), and sequential paper figures (`01_flow_architecture.png` to `11_paper_figure_9.png`), strictly excluding 2nd-order control theory figures from the paper submission package per your instruction.

---

## 4. Code & Behavioral Preferences (CRITICAL FOR NEW AI)

1. **Clean, Senior-Engineer Code Style**:
   * Do **NOT** add verbose, repetitive, AI-generated bulleted comments inside code files.
   * Keep comments minimal, concise, and focused strictly on non-obvious mathematical rationale or domain physics.
2. **Git Repository Cleanliness**:
   * Do **NOT** commit presentation files (`.pptx`), Word docs (`.docx`), zip archives (`.zip`), or large dataset files (`.parquet`, `.mat`) to Git. Keep the remote repository strictly for project source code (`src/`, `demo/`), documentation (`README.md`), and essential result verification figures (`results/figures/`).
3. **Operational Approach**:
   * When modifying core simulation or prediction logic, always verify behavior locally (or propose verification tests) before staging and pushing.
   * Maintain a warm, proactive, pair-programming tone with Chandru (`the user`). Prioritize direct execution and accuracy over lengthy explanations unless asked.

---

## 5. Current Project Status

* All code in `src/` and `demo/` is clean, refactored, and tested.
* `git status` on branch `main` is completely clean and up to date with `origin/main` (`latest commit: 2e3f240 Update feature extraction notebook`).
* The Streamlit dashboard (`demo/app.py`) runs smoothly locally (`http://localhost:8501`), fully supporting live unseen battery RUL predictions, custom CSV uploads, and real-time interactive 2nd-order root locus pole-zero migration.
* **Ready for immediate continuation on the new laptop!**
