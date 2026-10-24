# 💧 BhujalDrishti (JalRakshak AI)
### Multimodal Data Fusion Using GIS and Machine Learning for Groundwater Level Mapping and Forecasting in Purandar Taluka, Maharashtra

BhujalDrishti is an AI-driven decision-support platform designed to monitor, forecast, and spatially map groundwater levels (in Meters Below Ground Level, **MBGL**) across Purandar Taluka, Pune District, Maharashtra.

---

## 🚀 Key Features & The 4 Screens

1. **📊 Screen 1 — Overview Dashboard**:
   - Taluka-wide groundwater depth indicators, station health ratios, and pre-/post-monsoon historical time series.
   - Dual-axis graph highlighting rainfall vs. groundwater recharge dynamics.

2. **🗺️ Screen 2 — Interactive GIS Groundwater Map**:
   - Leaflet.js interactive map featuring all 11 CGWB monitoring stations.
   - Dynamic circle radius and color-coding by risk status (🟢 Safe $<4\text{m}$, 🟡 Semi-Critical $4\text{–}8\text{m}$, 🔴 Critical $>8\text{m}$).
   - Spatial influence zone modeling between stations.

3. **🔮 Screen 3 — AI Forecasting Engine**:
   - Station drilldown selector with historical actual readings.
   - 1–3 month ahead predictive forecasting with Random Forest ensemble.
   - **80% Uncertainty Confidence Intervals** (Quantile Regression: 10th & 90th percentiles).
   - Interactive Rainfall Simulation slider to evaluate drought vs. high-recharge scenarios.

4. **🛡️ Screen 4 — Conservation Decision Support**:
   - Station-wise vulnerability breakdown with Central Ground Water Board (CGWB) & GSDA criteria.
   - Tailored structural interventions (Continuous Contour Trenches, Percolation Tanks, Cement Check Dams, Farm Ponds).
   - Demand-side management recommendations (Micro-irrigation, crop water budgeting).

---

## ⚙️ Project Structure

```
BhujalDrishti/
├── app.py                      # Main Streamlit 4-screen application
├── run_dashboard.bat           # One-click launcher script
├── data/
│   ├── raw/                    # Original raw CSV files
│   │   ├── purandar_rainfall_1991_2023.csv
│   │   └── purandhar_groundwater_level_merged.csv
│   └── processed/              # Fused spatio-temporal dataset
│       └── purandar_groundwater_features.csv
├── models/                     # Trained ML models and uncertainty quantiles
│   ├── rf_mapping_model.joblib
│   ├── rf_forecast_model.joblib
│   ├── forecast_q10.joblib
│   └── forecast_q90.joblib
├── reports/                    # Benchmark metrics & JSON evaluation
│   └── model_evaluation.json
└── src/
    ├── inspect_data.py         # Exploratory data validation
    ├── preprocess.py           # IDW spatial fusion & lag engineering
    └── train_models.py         # Baseline & ML training with chronological split
```

---

## 🏃 Running the Application

### Option 1: Double-Click
Double click `run_dashboard.bat` in the root folder.

### Option 2: Terminal
Run:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.
