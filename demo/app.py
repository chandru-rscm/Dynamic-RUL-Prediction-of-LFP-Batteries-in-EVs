import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import os

PROCESSED_DIR = r"d:\chandru project\RUL prediction\data\processed"
MODEL_DIR = r"d:\chandru project\RUL prediction\src\models"

st.set_page_config(page_title="Dynamic RUL Prediction", layout="wide")

@st.cache_resource
def load_model_and_data():
    in_path = os.path.join(PROCESSED_DIR, "features.parquet")
    model_path = os.path.join(MODEL_DIR, "lightgbm_rul.pkl")
    
    if not os.path.exists(in_path) or not os.path.exists(model_path):
        return None, None
        
    df = pd.read_parquet(in_path)
    model = joblib.load(model_path)
    
    # Clean NaNs exactly as we did in training to prevent app crashes on broken cells
    features = ['cycle', 'SOH', 'capacity_fade_window', 'IR', 'Tavg', 'dQ_log_var', 'dQ_min', 'dQ_mean']
    df = df.dropna(subset=features + ['RUL'])
    
    return df, model

df, model = load_model_and_data()

st.title("🔋 Dynamic RUL Prediction for LFP Batteries")
st.markdown("This dashboard demonstrates real-time Remaining Useful Life (RUL) prediction for commercial LFP cells under fast-charging conditions.")

if df is None:
    st.error("Data or model not found. Please run the pipeline first.")
    st.stop()

# Load data and recreate the EXACT 80/20 split used during training
# to guarantee we only show STRICTLY UNSEEN test cells in the dropdown
from sklearn.model_selection import GroupShuffleSplit
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(gss.split(df, groups=df['cell_id']))
test_df = df.iloc[test_idx].copy()

# UI Layout: Tabs for Dataset Simulation vs Custom Upload
tab1, tab2 = st.tabs(["🧪 Simulate Unseen Test Cells", "📁 Upload Custom Battery Data"])

with tab1:
    # Select a cell from the purely unseen TEST set
    cell_ids = test_df['cell_id'].unique()
    selected_cell = st.selectbox("Select a strictly unseen test cell to simulate:", cell_ids)

    cell_data = test_df[test_df['cell_id'] == selected_cell].sort_values('cycle')
    actual_cycle_life = cell_data['cycle_life'].iloc[0]

    st.markdown(f"**True Cycle Life (End-of-Life) for {selected_cell}:** {actual_cycle_life} cycles")

    # Simulation slider
    max_cycle = int(cell_data['cycle'].max())
    sim_cycle = st.slider("Simulate driving (Current Cycle Checkpoint):", 
                          min_value=int(cell_data['cycle'].min()), 
                          max_value=max_cycle, 
                          step=5)

    # Filter data up to sim_cycle
    historical_data = cell_data[cell_data['cycle'] <= sim_cycle]
    if historical_data.empty:
        st.warning("Not enough data at this cycle checkpoint.")
    else:
        current_row = historical_data.iloc[-1:]

        features = ['cycle', 'SOH', 'capacity_fade_window', 'IR', 'Tavg', 'dQ_log_var', 'dQ_min', 'dQ_mean']
        X_pred = current_row[features]

        pred_rul = model.predict(X_pred)[0]
        # Use the calibrated conformal interval (122 cycles based on 90% calibration)
        q_hat = 122.0 

        lower_bound = max(0, pred_rul - q_hat)
        upper_bound = pred_rul + q_hat

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Health (SOH)", f"{current_row['SOH'].iloc[0]*100:.2f}%")
        col2.metric("Predicted RUL (Remaining Cycles)", f"{int(pred_rul)} cycles")
        col3.metric("90% Confidence Interval", f"[{int(lower_bound)}, {int(upper_bound)}]")
        col4.metric("True RUL at this point", f"{int(current_row['RUL'].iloc[0])} cycles")

        from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score
        all_true_t1 = cell_data['RUL']
        all_preds_t1 = model.predict(cell_data[features])
        mae_t1 = mean_absolute_error(all_true_t1, all_preds_t1)
        mape_t1 = mean_absolute_percentage_error(np.clip(all_true_t1, 1, None), np.maximum(0, all_preds_t1))
        r2_t1 = r2_score(all_true_t1, all_preds_t1)
        st.info(f"**Overall Trajectory Metrics on this cell:** MAE = {mae_t1:.1f} cycles | MAPE = {mape_t1*100:.1f}% | **R² Accuracy Score = {r2_t1*100:.1f}%**")

        # Plotting
        fig = go.Figure()

        # Plot True RUL trajectory
        fig.add_trace(go.Scatter(
            x=cell_data['cycle'], 
            y=cell_data['RUL'],
            mode='lines',
            name='True RUL Trajectory',
            line=dict(color='white', dash='dash')
        ))

        # Plot predictions up to current point
        all_preds = model.predict(historical_data[features])
        fig.add_trace(go.Scatter(
            x=historical_data['cycle'], 
            y=all_preds,
            mode='lines+markers',
            name='Model Prediction',
            line=dict(color='blue')
        ))

        # Uncertainty bounds
        fig.add_trace(go.Scatter(
            x=historical_data['cycle'].tolist() + historical_data['cycle'].tolist()[::-1],
            y=np.maximum(0, all_preds - q_hat).tolist() + (all_preds + q_hat).tolist()[::-1],
            fill='toself',
            fillcolor='rgba(0,0,255,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            name='90% Confidence Interval'
        ))

        fig.update_layout(
            title="Dynamic RUL Prediction Over Time",
            xaxis_title="Current Cycle",
            yaxis_title="Remaining Useful Life (Cycles)",
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### Upload Custom LFP Data")
    st.markdown("Upload a CSV file containing your battery's feature trajectory. The required columns are: `cycle`, `SOH`, `capacity_fade_window`, `IR`, `Tavg`, `dQ_log_var`, `dQ_min`, `dQ_mean`.")
    
    uploaded_file = st.file_uploader("Upload CSV feature data", type=["csv"])
    
    if uploaded_file is not None:
        custom_df = pd.read_csv(uploaded_file)
        features = ['cycle', 'SOH', 'capacity_fade_window', 'IR', 'Tavg', 'dQ_log_var', 'dQ_min', 'dQ_mean']
        
        if not all(col in custom_df.columns for col in features):
            st.error(f"Missing required columns! Ensure your CSV has: {features}")
        else:
            custom_df = custom_df.sort_values('cycle')
            
            # Interactive Slider for Uploaded Data
            max_cycle_up = int(custom_df['cycle'].max())
            sim_cycle_up = st.slider("Simulate driving (Uploaded Data Checkpoint):", 
                                  min_value=int(custom_df['cycle'].min()), 
                                  max_value=max_cycle_up, 
                                  step=5)

            # Filter data up to sim_cycle
            hist_custom = custom_df[custom_df['cycle'] <= sim_cycle_up]
            if hist_custom.empty:
                st.warning("Not enough data at this cycle checkpoint.")
            else:
                current_row_up = hist_custom.iloc[-1:]
                X_pred_up = current_row_up[features]

                pred_rul_up = model.predict(X_pred_up)[0]
                q_hat = 122.0 

                lower_bound_up = max(0, pred_rul_up - q_hat)
                upper_bound_up = pred_rul_up + q_hat

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Current Health (SOH)", f"{current_row_up['SOH'].iloc[0]*100:.2f}%")
                col2.metric("Predicted RUL (Remaining Cycles)", f"{int(pred_rul_up)} cycles")
                col3.metric("90% Confidence Interval", f"[{int(lower_bound_up)}, {int(upper_bound_up)}]")
                
                has_true_rul = 'RUL' in custom_df.columns
                if has_true_rul:
                    true_rul_val = current_row_up['RUL'].iloc[0]
                    col4.metric("True RUL at this point", f"{int(true_rul_val)} cycles")
                    
                    # Calculate errors over the entire trajectory
                    all_true = custom_df['RUL']
                    all_preds_full = model.predict(custom_df[features])
                    from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score
                    mae = mean_absolute_error(all_true, all_preds_full)
                    mape = mean_absolute_percentage_error(np.clip(all_true, 1, None), np.maximum(0, all_preds_full))
                    r2 = r2_score(all_true, all_preds_full)
                    st.info(f"**Overall Trajectory Metrics on this battery:** MAE = {mae:.1f} cycles | MAPE = {mape*100:.1f}% | **R² Accuracy Score = {r2*100:.1f}%**")

                # Plotting
                fig2 = go.Figure()

                if has_true_rul:
                    # Plot True RUL trajectory
                    fig2.add_trace(go.Scatter(
                        x=custom_df['cycle'], 
                        y=custom_df['RUL'],
                        mode='lines',
                        name='True RUL Trajectory',
                        line=dict(color='white', dash='dash')
                    ))

                # Plot predictions up to current point
                all_preds_up = model.predict(hist_custom[features])
                fig2.add_trace(go.Scatter(
                    x=hist_custom['cycle'], 
                    y=all_preds_up,
                    mode='lines+markers',
                    name='Model Prediction',
                    line=dict(color='green')
                ))

                # Uncertainty bounds
                fig2.add_trace(go.Scatter(
                    x=hist_custom['cycle'].tolist() + hist_custom['cycle'].tolist()[::-1],
                    y=np.maximum(0, all_preds_up - q_hat).tolist() + (all_preds_up + q_hat).tolist()[::-1],
                    fill='toself',
                    fillcolor='rgba(0,255,0,0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    hoverinfo="skip",
                    name='90% Confidence Interval'
                ))

                fig2.update_layout(
                    title="Interactive RUL Prediction on Uploaded Data",
                    xaxis_title="Current Cycle",
                    yaxis_title="Predicted Remaining Useful Life (Cycles)",
                    template="plotly_white"
                )

                st.plotly_chart(fig2, use_container_width=True)
