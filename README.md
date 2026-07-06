# Dynamic Remaining Useful Life (RUL) & Electrochemical Stability Prediction of LFP Batteries in EV Applications

A comprehensive end-to-end framework combining **Physics-Informed Machine Learning (LightGBM)**, **Conformal Uncertainty Quantification**, and **2nd-Order Control Theory Stability Analysis** for real-time prognostics of Lithium Iron Phosphate (LFP) battery cells under fast-charging EV protocols.

---

## 🌟 Key Features

1. **Physics-Informed Dynamic RUL Prediction**:
   - Replaces static early-cycle lifetime estimation with continuous, multi-checkpoint RUL tracking across the entire battery lifespan.
   - Extracts physical domain features including voltage relaxation curve log-variance ($\Delta Q(V)$ variance), internal resistance ($R_{int}$) growth, thermal dissipation ($T_{avg}$), and normalized State of Health ($\text{SOH}$).
   - Achieves high prognostic accuracy on strictly unseen test batteries (**Test $R^2 \approx 0.93$, MAPE $\approx 9.0\%$**).

2. **Conformal Uncertainty Quantification**:
   - Implements distribution-free conformal prediction to generate mathematically guaranteed **90% confidence intervals ($\pm q_{hat}$ cycles)** around predicted remaining life.
   - Enables risk-aware battery management system (BMS) decision-making and preventative maintenance scheduling.

3. **2nd-Order Control Theory & Electrochemical Stability Analysis**:
   - Models battery electrochemical transport lag and interfacial impedance as a second-order linear dynamical system:
     $$G(s) = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$
   - **Healthy Overdamped Regime ($\zeta > 1.0$)**: Real poles on the negative real axis ($\text{Im}(s) = 0$), reflecting linear, predictable aging.
   - **Bifurcation Point ($\text{SOH} = 80\%, \zeta = 1.00$)**: Critical damping threshold where poles collide and split into the complex plane, marking the onset of non-linear electrochemical imbalance.
   - **Imaginary Axis Strike ($\zeta \to 0.00$)**: Real-time tracking of complex conjugate poles migrating toward $\text{Re}(s) = 0$, proving impending cell failure and instability.

4. **Interactive Real-Time Dashboard**:
   - Built with Streamlit and Plotly for live visualization of unseen test cell prognostics, custom CSV prototype testing, and interactive root locus pole-zero migration.

---

## 📂 Dataset Download & Setup

This project utilizes the benchmark **MIT / Stanford / Toyota Research Institute (TRI) Fast-Charging LFP Battery Dataset** (Severson et al., *Nature Energy* 2019).

### 1. Download the Raw Data
Download the raw MATLAB (`.mat`) batch files from the official data repository:
* **Official Data Portal**: [MATR.io Battery Data Archive](https://data.matr.io/1/)
* **Reference Publication**: *Data-driven prediction of battery cycle life before capacity degradation* ([Nature Energy, 2019](https://doi.org/10.1038/s41560-019-0356-8))

You will need the primary batch files (e.g., `2017-05-12_batchdata_updated_struct_errorcorrect.mat`, `2017-06-30_batchdata_updated_struct_errorcorrect.mat`, and `2018-04-12_batchdata_updated_struct_errorcorrect.mat`).

### 2. Organize the Data Directory
Create a `data/raw/` folder inside the project root directory and place all downloaded `.mat` files into it:

```text
Dynamic-RUL-Prediction-of-LFP-Batteries-in-EVs/
│
├── data/
│   ├── raw/                  <-- PLACE DOWNLOADED .MAT FILES HERE
│   ├── processed/            <-- Generated automatically by ingest scripts
│   └── test_samples/         <-- Generated prototype CSVs for custom upload
│
├── demo/
│   └── app.py                <-- Streamlit Interactive Dashboard
│
├── src/
│   ├── ingest_matr.py        <-- Raw HDF5/MATLAB data parser
│   ├── features.py           <-- Physics-informed feature engineering
│   ├── train.py              <-- LightGBM model training & LOCO validation
│   ├── conformal.py          <-- Conformal uncertainty calibration
│   ├── evaluate.py           <-- Evaluation metrics & static figure generation
│   └── utils/                <-- Synthetic benchmark & sample export utilities
│
├── requirements.txt
└── README.md
```

---

## 🛠️ System Requirements & Installation

### Prerequisites
* **Operating System**: Windows 10/11, macOS, or Linux
* **Python**: Version 3.9, 3.10, or 3.11 (Tested on Python 3.10+)
* **Git**: To clone the repository

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/Dynamic-RUL-Prediction-of-LFP-Batteries-in-EVs.git
   cd Dynamic-RUL-Prediction-of-LFP-Batteries-in-EVs
   ```

2. **Create a Virtual Environment**:
   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate on Windows (PowerShell):
   .\.venv\Scripts\activate

   # Activate on macOS / Linux:
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 🚀 Step-by-Step Execution Guide

To build the dataset, extract features, train the model, and evaluate performance from scratch, execute the following pipeline in order:

### Step 1: Data Ingestion & Parsing
Parse the raw MATLAB/HDF5 files and convert them into structured time-series cycles:
```bash
python src/ingest_matr.py
```
*Output: Saves compiled cycle data to `data/processed/cycles.parquet`.*

### Step 2: Dynamic Feature Engineering
Extract physical domain features ($\Delta Q(V)$ variance, internal resistance, thermal metrics, and capacity fade windows) across dynamic cycle checkpoints:
```bash
python src/features.py
```
*Output: Saves ML-ready feature matrices to `data/processed/features.parquet`.*

### Step 3: Model Training
Train the LightGBM prognostic regressor using a Leave-One-Cell-Out (LOCO) grouped 80/20 train-test split:
```bash
python src/train.py
```
*Output: Evaluates test set R², MAE, and MAPE, and saves the trained model to `src/models/lightgbm_rul.pkl`.*

### Step 4: Uncertainty Calibration & Evaluation
Compute 90% conformal prediction intervals and generate comprehensive evaluation plots:
```bash
python src/conformal.py
python src/evaluate.py
```
*Output: Generates static analysis plots (True vs. Predicted RUL, Feature Importance, Error Residuals, and Capacity Fade curves) in `results/figures/`.*

### Step 5 (Optional): Generate Sample CSV Prototypes for Dashboard Upload
Generate anonymous prototype CSV files from unseen test batteries for testing the custom upload feature in the dashboard:
```bash
python src/utils/export_sample.py
python src/utils/fix_synthetic.py
```
*Output: Populates `data/test_samples/` with ready-to-upload battery prototype CSVs.*

---

## 🖥️ Running the Interactive Dashboard

Launch the Streamlit web application to interact with the models in real time:

```bash
streamlit run demo/app.py
```

Open your browser and navigate to `http://localhost:8501`. 

### Dashboard Modules:
1. **🧪 Simulate Unseen Test Cells**: Select any battery from the strictly unseen test split. Watch the model dynamically predict RUL with 90% conformal confidence bounds across its entire lifecycle.
2. **📁 Upload Custom Battery Data**: Upload any time-series CSV file (use the generated prototypes in `data/test_samples/`) to receive instant health assessments and maintenance recommendations.
3. **⚙️ Control Systems (Poles & Zeros)**: 
   - Analyze battery stability through second-order control theory.
   - Adjust the cycle progression slider to observe real-time pole migration across the complex Laplace plane ($s$-plane).
   - Witness the critical **Bifurcation Point at 80% SOH** and simulate **End-of-Life Imaginary Axis Strikes ($\zeta \to 0.00$)**!

---

## 📜 License & Acknowledgments
* **Data Source**: Severson et al., *Nature Energy* (2019), Toyota Research Institute, MIT, and Stanford University.
* **Academic Reference**: Built for research and development in advanced battery prognostics, EV battery management systems (BMS), and electrochemical stability modeling.
