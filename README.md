# 💧 BhujalDrishti (JalRakshak AI)
### Multimodal Hydrological Intelligence & Predictive Groundwater Dashboard for Purandar Taluka, Maharashtra

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/pytest-56%20passed-brightgreen.svg)](tests/)
[![Leaflet.js](https://img.shields.io/badge/leaflet-1.9.4-199900.svg)](https://leafletjs.com/)
[![Research Prototype](https://img.shields.io/badge/status-Research%20Prototype-teal.svg)](#disclaimer--research-use)

**BhujalDrishti (JalRakshak AI)** is an environmental intelligence research prototype designed for regional groundwater monitoring, predictive next-observation forecasting, interactive GIS mapping, and conservation decision support in **Purandar Taluka**, Pune District, Maharashtra, India.

> [!IMPORTANT]
> **Research Prototype Disclaimer**: BhujalDrishti is a historical-data research tool developed for empirical evaluation and methodology demonstration. It is **not a real-time monitoring telemetry system** and **not an official regulatory platform**. All predictions and advisories are statistical estimates derived from discrete historical surveys and gridded precipitation datasets.

---

## 📑 Table of Contents

1. [Project Overview](#-project-overview)
2. [Study Area & Dataset](#-study-area--dataset)
3. [Four Application Screens](#-four-application-screens)
   - [Screen 1: Overview Dashboard](#1--screen-1--overview-dashboard)
   - [Screen 2: Interactive Groundwater Map](#2--screen-2--interactive-groundwater-map)
   - [Screen 3: Next-Observation Forecast](#3--screen-3--next-observation-forecast)
   - [Screen 4: Conservation Decision Support](#4--screen-4--conservation-decision-support)
4. [Scientific Methodology & Limitations](#-scientific-methodology--limitations)
5. [Model Architecture & Evaluation Benchmarks](#-model-architecture--evaluation-benchmarks)
6. [Technology Stack](#-technology-stack)
7. [Repository Structure](#-repository-structure)
8. [Installation & Local Execution](#-installation--local-execution)
9. [Automated Test Suite](#-automated-test-suite)
10. [Disclaimer & Research Use](#-disclaimer--research-use)

---

## 🌍 Project Overview

Purandar Taluka is situated in the semi-arid, rain-shadow agricultural belt of the Western Ghats on the **Deccan Traps Basalt** plateau. The region faces pronounced groundwater volatility driven by low primary porosity in basalt, seasonal monsoon concentration, localized hard-rock fracture connectivity, and intensive agricultural pumping.

BhujalDrishti provides a modular, reproducible research interface to inspect multi-decadal historical water table observations, evaluate next-observation machine learning models, visualize geospatial station telemetry with interactive Leaflet GIS, and formulate rule-based conservation advisories.

---

## 📍 Study Area & Dataset

### Hydrogeological & Geographic Parameters

- **Geographic Scope**: Purandar Taluka, Pune District, Maharashtra, India.
- **Estimated Study Bounding Area**: Approximately **2,936 km²** (approximate geographic extent covering the monitoring network; official taluka administrative GIS shapefiles are not bundled in the repository).
- **Monitoring Network**: **11 Central Ground Water Board (CGWB)** in-situ monitoring stations.
- **Station Density**: Approximately **1 monitoring station per 267 km²** (a coarse spatial average across rugged terrain).
- **Historical Record**: **680 validated groundwater soundings** spanning **1996 through 2023**.
- **Geological Setting**: Deccan Traps layered basaltic lava flows characterized by low primary rock porosity, localized secondary joint/fracture permeability, and highly responsive unconfined-to-semi-confined shallow aquifers.

### Precipitation Dataset & Spatial Extrapolation

- **Rainfall Source**: India Meteorological Department (IMD) high-resolution ($0.25^\circ \times 0.25^\circ$) daily gridded rainfall dataset (1991–2023).
- **Rainfall Grid Structure**: 4 primary IMD grid points cover the central Purandar region.
- **Spatial Extrapolation**: Four peripheral monitoring stations (*Pimpri (Kh) Malvasti, Kamatwadi-Walha, Walha, Narayanpur*) lie outside the four-point grid spatial polygon. Antecedent rainfall features at these locations are computed via spatial inverse-distance weighting (IDW) extrapolation. Grid coverage does not imply uniform or dense rain-gauge coverage across complex micro-topography.

### Observation Irregularity & Temporal Recency

Groundwater observations in the dataset are discrete, manually sounded in-situ records rather than high-frequency telemetry:
- **7 stations** have their latest historical observation recorded in **2023** (*Jejuri, Kamatwadi-Walha, Narayanpur, Pangre Sailar Basti, Pimpri (Kh) Malvasti, Sakurde, Zendewadi-1*).
- **4 stations** reflect earlier historical monitoring rounds (*Zendewadi in 2022, Saswad in 2006, Waghapur in 1997, Walha in 1997*). Older records represent historical survey coverage and must not be misinterpreted as decommissioned or inactive monitoring infrastructure.
- Multi-year observation intervals occur in the historical series (e.g., Zendewadi contains a 2,206-day / 6.0-year observation gap between May 2016 and May 2022).

---

## 🖥️ Four Application Screens

The application is structured into four focused screens accessible via the sidebar navigation:

```
                                  ┌──────────────────────────┐
                                  │    app.py (App Shell)    │
                                  └─────────────┬────────────┘
                                                │
                       ┌────────────────────────┼────────────────────────┐
                       ▼                        ▼                        ▼
             ┌────────────────────┐   ┌────────────────────┐   ┌────────────────────┐
             │ Screen 1:          │   │ Screen 2:          │   │ Screen 3:          │
             │ Overview Dashboard │   │ Groundwater Map    │   │ Next-Observation   │
             │                    │   │ (Leaflet GIS)      │   │ Forecast & What-If │
             └────────────────────┘   └────────────────────┘   └──────────┬─────────┘
                                                                          │
                                            ┌─────────────────────────────┴────────┐
                                            ▼                                      ▼
                                  ┌────────────────────┐                ┌────────────────────┐
                                  │ Screen 4:          │                │ Conformal Quantile │
                                  │ Decision Support   │                │ Regression (CQR)   │
                                  │ (Advisory Heuristics)               │ Calibration Guide  │
                                  └────────────────────┘                └────────────────────┘
```

### 1. 📊 Screen 1 — Overview Dashboard

- **Network-Level Summary KPIs**: Displays dynamic metrics for Mean Water Table Depth (m MBGL), CGWB Monitoring Network size (11 stations), Total Historical Observations (680 records), and Held-Out Model MAE (2.092 m).
- **Physical Depth Tier Badges**: Distribution indicators summarizing the network across project-defined physical reference categories (<4.0 m Shallow, 4.0–8.0 m Moderate, >8.0 m Deep).
- **Latest Station Telemetry & Historical Changes**: A comprehensive table listing every station's latest recorded depth, observation date, immediately prior survey date, elapsed calendar days, observed depth change (m), and direction of change (Shallower / Deeper / Unchanged), with prominent warnings for multi-year observation gaps.
- **Seasonal Groundwater Analysis (Collapsible Expander)**:
  - Compares May (pre-monsoon) and November (post-monsoon) groundwater levels strictly using **matched station-year pairs** ($n=78$ pairs across 1996–2022).
  - Dynamically calculates mean November-minus-May depth change (negative value indicates water-table rise toward the surface) and median water-table rise.
  - Interactive dual-bar comparison chart displaying annual May vs. November mean depths.
  - Transparent methodological note clarifying that paired seasonal differences represent historical historical soundings, not predictive seasonal forecasts.
- **Rainfall & Groundwater Relationship (Collapsible Expander)**:
  - Dual-axis time-series visualization correlating annual cumulative rainfall (mm) against mean groundwater levels (m MBGL, inverted axis).
  - Dynamic scatter plot evaluating 90-day, 180-day, and 365-day antecedent rainfall accumulation windows against observed water table depths.
  - Reports dynamically calculated Pearson ($r$) and Spearman ($\rho$) correlation metrics.
  - Explicit scientific qualifications stating that pooled correlations across 11 stations are exploratory, correlation does not establish causation, infiltration lags vary across fractured basalt, and recharge response is not uniform across stations.

### 2. 🗺️ Screen 2 — Interactive Groundwater Map

- **Interactive Leaflet.js GIS Canvas**: Custom HTML/Leaflet map component centered on Purandar Taluka `(18.28° N, 74.12° E)` with OpenStreetMap basemap tiles and auto-fitted network bounds.
- **Station Coordinate Mapping**: Displays all 11 CGWB monitoring stations at their recorded geographic coordinates with circle markers color-coded by project reference depth tiers:
  - 🟢 **Shallow (< 4.0 m MBGL)**: `#0F766E` (Near-surface water table)
  - 🟡 **Moderate (4.0–8.0 m MBGL)**: `#854D0E` (Intermediate water table)
  - 🔴 **Deep (> 8.0 m MBGL)**: `#991B1B` (Deep water table)
- **Station Telemetry Popups**: Clickable popups detailing station name, latest recorded MBGL depth, project reference tier, observation date, previous survey depth and date, elapsed days, depth change interpretation, geographic coordinates, and rainfall extrapolation status.
- **Dynamic Controls Toolbar**:
  - Filter by Depth Category (*All Depth Tiers*, *Shallow (< 4.0 m)*, *Moderate (4.0–8.0 m)*, *Deep (> 8.0 m)*).
  - Search / Select Monitoring Station with instant map pan, zoom, and popup opening.
  - ⟲ Reset Map View button to restore the full network zoom.
  - Reset Filters button.
- **Dual-Theme Compatibility**: Includes a custom dark tile shader (`brightness(0.7) invert(1) contrast(2.6) hue-rotate(200deg)`) for seamless readability in Dark Mode.
- **Station Telemetry Details Table**: Interactive Streamlit dataframe rendering full station attributes, coordinates, elapsed days, and rainfall grid coverage status.
- **Spatial Prediction Layer Status (Methodological Expander)**: Documents Leave-One-Station-Out Cross-Validation (LOSO-CV) findings ($R^2 < 0$, negative spatial generalizability in fractured basalt), explaining why continuous spatial interpolation surfaces are excluded to preserve scientific integrity.

### 3. 🔮 Screen 3 — Next-Observation Forecast

- **Station Selection & Eligibility**: Interactive station drilldown with an informational note explaining that **9 of the 11 CGWB monitoring stations** are available for forecasting because the other 2 stations have fewer than 10 historical soundings (these 2 stations remain fully included in historical monitoring and map views).
- **Telemetry Snapshot & Direction of Change**:
  - Latest observed water table depth (m MBGL) and observation date.
  - Machine-learning predicted next-observation depth (m MBGL).
  - Categorical direction of change: *Shallower* ($\le -0.25\text{ m}$), *Deeper* ($\ge +0.25\text{ m}$), or *Approximately Stable* ($|\Delta| < 0.25\text{ m}$).
  - Illustrative event horizon note explaining that the displayed horizon is based on the held-out test-set median interval of 92 days (mean 109.4 days), not a fixed calendar schedule or model-predicted date.
- **Historical vs. Predicted Time-Series Chart**: High-resolution Matplotlib visualization showing historical observed groundwater depths alongside the predicted next observation (amber diamond with $q_{10}$–$q_{90}$ error bar) and an inverted y-axis (higher MBGL = deeper water table).
- **Separation of Models & Uncertainty Interval**:
  - Point estimate generated by a **Random Forest Regressor** (MAE: 2.092 m, RMSE: 2.899 m, $R^2$: 0.247).
  - Prediction interval ($q_{10}$–$q_{90}$) generated by separate **Gradient Boosting Quantile Regressors**.
  - Transparent undercoverage warning documenting that the nominal 80% interval achieves **57.26% empirical coverage** on held-out evaluation data (undercoverage miss rate: 42.74%; average width: 4.36 m).
- **Evaluation Benchmark Cards**: Standardized comparison displaying Random Forest performance against a naive Persistence baseline ($y_t = y_{t-1}$, MAE: 2.744 m, RMSE: 3.709 m, $R^2$: -0.233), demonstrating a 23.8% error reduction.
- **Hypothetical Rainfall Sensitivity Slider**: An interactive simulation slider ($\pm 50\%$) that scales antecedent rainfall accumulation features (30d, 60d, 90d, 180d, 365d) to simulate localized aquifer responsiveness under drought or surplus scenarios. Clearly labeled as a hypothetical sensitivity analysis, not a meteorological forecast.
- **Conformalized Quantile Regression (CQR) Methodology Expander**: Outlines the mathematical foundation of split conformal prediction, non-conformity scores, calibration steps, and finite-sample marginal coverage guarantees.

### 4. 🛡️ Screen 4 — Conservation Decision Support

- **Reference Depth Tier Summary Cards**: Overview KPI cards displaying station counts across project-defined physical reference tiers (Deep $>8.0\text{ m}$, Moderate $4.0\text{–}8.0\text{ m}$, Shallow $<4.0\text{ m}$ MBGL), explicitly stating that these are physical depth categories, not official CGWB administrative or safety classifications.
- **Historical Assessment Transparency**: Prominently notes that all station assessments reflect each well's latest recorded historical observation, not current real-time groundwater conditions. Stations with older records (pre-2023) display recency badges (e.g. `🗓️ Historical Survey: 2006`) without labeling stations as decommissioned or inactive.
- **Filtering & Sorting Controls**: Allows filtering by physical depth tier and sorting by *Deepest Observation First*, *Shallowest Observation First*, or *Alphabetical (A–Z)*.
- **Qualitative Hydrogeological Advisory Heuristics**:
  - **Deep Reference Tier (> 8.0 m MBGL)** (*Deep Reference Tier — Enhanced Assessment Advisory*):
    - *Artificial Recharge Feasibility Assessment*: Check dams and percolation structures presented as preliminary options strictly requiring site-specific geological, hydrogeological, and infiltration feasibility assessment in fractured basalt.
    - *Voluntary Extraction Monitoring & Pumping Review*: Voluntary monitoring of extraction rates and seasonal pumping reviews during dry periods.
    - *Crop Water Management Options*: Locally assessed agricultural transitions (drought-resilient crops, drip irrigation) rather than blanket prescriptions.
    - *Farm Storage Pond Lining Assessment (Shet-Tale)*: Lining decisions based on site-specific soil permeability and water-retention testing.
  - **Moderate Reference Tier (4.0–8.0 m MBGL)** (*Moderate Reference Tier — Conservation Advisory*):
    - *Contour Bunding & Continuous Contour Trenches (CCT)*: Preliminary soil and water conservation options subject to terrain slope and soil depth suitability.
    - *Micro-Irrigation Adoption*: Micro-sprinklers and drip systems recommended as water-efficiency options suited to local conditions.
    - *Rooftop Rainwater Harvesting & Managed Recharge*: Rooftop harvesting for storage distinguished from groundwater injection; injection wells strictly require hydrogeological and water-quality testing.
  - **Shallow Reference Tier (< 4.0 m MBGL)** (*Shallow Reference Tier — Monitoring Advisory*):
    - *Aquifer Monitoring & Surveillance*: Proposed quarterly observation schedule; avoidance of concentrated deep pumping to prevent localized cone of depression formation.
    - *Participatory Community Water Budgeting*: Suggested village water budgeting at Gram Sabha meetings for local water-resource planning.
- **Scientific Limitations & Methodological Boundaries Expander**: Full documentation of physical reference tiers vs. official CGWB/GEC taluka-wide budget assessments (Safe, Semi-Critical, Critical, Over-Exploited), historical sounding limitations, site-specific feasibility requirements, and precipitation extrapolation boundaries.

---

## 🔬 Scientific Methodology & Limitations

1. **MBGL Definition & Axis Directionality**:
   - Depth measurements are in **Metres Below Ground Level (MBGL)**.
   - **Higher MBGL values indicate a deeper water table** (water level is further below the land surface).
   - **Lower MBGL values indicate a shallower water table** (water level is closer to the land surface).
   - In seasonal differences, a negative November-minus-May depth change indicates a water-table rise.
2. **Project-Defined Depth Tiers vs. Official Classifications**:
   - The categories (*Shallow < 4.0 m*, *Moderate 4.0–8.0 m*, *Deep > 8.0 m MBGL*) are project-defined physical reference categories designed for localized visualization.
   - They do **not constitute official Central Ground Water Board (CGWB) or Groundwater Estimation Committee (GEC)** administrative categories (*Safe, Semi-Critical, Critical, Over-Exploited*), which evaluate annual recharge vs. extraction ratios at the taluka level.
3. **Forecast Target & Horizon**:
   - The predictive task is **next-recorded-observation forecasting**, not a fixed 30-day, 60-day, or 90-day calendar forecast.
   - The observation interval in the historical dataset is irregular: in the held-out test set, intervals range from 41 to 233 days (mean 109.4 days, median 92.0 days).
4. **Separate Point and Uncertainty Models**:
   - The point forecast is produced by a Random Forest Regressor.
   - The $q_{10}$ and $q_{90}$ interval bounds are produced by separate Gradient Boosting Quantile Regressors.
   - The resulting nominal 80% prediction interval is **uncalibrated** and achieves **57.26% empirical coverage** on held-out test data (miss rate: 42.74%, average width: 4.36 m).
5. **Rainfall Sensitivity Simulation**:
   - The rainfall slider is a **hypothetical sensitivity analysis** scaling historical antecedent rainfall features ($\pm 50\%$). It is not a coupled meteorological forecast or precipitation prediction.
6. **Spatial Generalizability in Hard-Rock Basalt**:
   - Leave-One-Station-Out Cross-Validation (LOSO-CV) demonstrates negative spatial generalizability across unmonitored sites due to Deccan Traps fracture heterogeneity. Continuous spatial interpolation surfaces are excluded to prevent misleading representations.
7. **Advisory Heuristics**:
   - Conservation recommendations are rule-based heuristics synthesized from watershed management handbooks. They do not constitute validated civil engineering designs or guaranteed recharge solutions.

---

## 📈 Model Architecture & Evaluation Benchmarks

Evaluation is conducted using a strict **chronological train/test split** (training: 1996–2017, $n=526$; held-out testing: 2018–2023, $n=124$) with zero target leakage and no future feature contamination:

| Model / Baseline | Task | MAE (m) | RMSE (m) | $R^2$ | Empirical 80% Coverage | Avg Interval Width (m) |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **Random Forest Regressor** | Next Observation Forecast | **2.092** | **2.899** | **0.247** | — | — |
| **HistGradientBoosting** | Next Observation Forecast | 2.094 | 2.914 | 0.239 | — | — |
| **Persistence Baseline ($y_t = y_{t-1}$)** | Naive Benchmark | 2.744 | 3.709 | -0.233 | — | — |
| **Quantile GBDT ($q_{10}, q_{90}$)** | Prediction Interval | — | — | — | **57.26%** (Nominal 80%) | **4.36** |

- **MAE Improvement**: Random Forest reduces Mean Absolute Error by **23.8%** (from 2.744 m to 2.092 m) compared to the persistence baseline.
- **RMSE Improvement**: Random Forest reduces Root Mean Squared Error by **21.8%** (from 3.709 m to 2.899 m).
- Evaluation metadata is stored in [reports/model_evaluation.json](reports/model_evaluation.json).

---

## 🛠️ Technology Stack

- **Core Runtime**: Python 3.10+ (tested on Python 3.10 through 3.14)
- **Frontend Framework**: [Streamlit](https://streamlit.io/) (`>=1.30.0`)
- **Geospatial Mapping**: [Leaflet.js](https://leafletjs.com/) (v1.9.4) embedded via `streamlit.components.v1.html`, OpenStreetMap tile service
- **Data Wrangling**: [Pandas](https://pandas.pydata.org/) (`>=2.0.0`), [NumPy](https://numpy.org/) (`>=1.24.0`)
- **Machine Learning**: [Scikit-Learn](https://scikit-learn.org/) (`>=1.3.0`) — Random Forest Regressor, Gradient Boosting Quantile Regressors, HistGradientBoostingRegressor
- **Model Serialization**: [Joblib](https://joblib.readthedocs.io/) (`>=1.3.0`)
- **Data Visualization**: [Matplotlib](https://matplotlib.org/) (`>=3.8.0`) with custom dual-theme styling
- **Testing & QA**: [Pytest](https://docs.pytest.org/) (`>=7.0.0`)

---

## 📁 Repository Structure

```
BhujalDrishti/
├── .gitignore                          # Git ignore rules
├── README.md                           # Project documentation and source of truth
├── app.py                              # Streamlit main entry point, router & theme state
├── requirements.txt                    # Pinned core dependencies
├── run_dashboard.bat                   # Windows launcher script
│
├── components/                         # Decoupled UI and visualization components
│   ├── __init__.py
│   ├── callouts.py                     # Horizon notices, advisory disclaimers & CQR guide
│   ├── charts.py                       # Theme-adaptive Matplotlib charts (forecast, seasonal, rainfall)
│   ├── header.py                       # Top research header banner & status pill
│   ├── map_view.py                     # Interactive Leaflet.js GIS map component
│   ├── metric_cards.py                 # Responsive equal-height KPI metric cards
│   ├── sidebar.py                      # Theme switcher and screen navigation
│   └── tables.py                       # Formatted station telemetry tables
│
├── screens/                            # Application screen controllers
│   ├── __init__.py
│   ├── overview.py                     # Screen 1: Regional Overview Dashboard
│   ├── groundwater_map.py              # Screen 2: Interactive GIS Groundwater Map
│   ├── forecast.py                     # Screen 3: Next-Observation Forecast & What-If
│   └── decision_support.py             # Screen 4: Conservation Decision Support
│
├── services/                           # Business logic, loading & inference services
│   ├── __init__.py
│   ├── data_loader.py                  # Telemetry caching, paired seasonal comparison, depth tiers
│   ├── metrics_service.py              # Summary statistics and metric aggregations
│   └── model_service.py                # Model artifact loading and inference routines
│
├── src/                                # Offline data processing and training pipelines
│   ├── inspect_data.py                 # Raw dataset inspection and audit utilities
│   ├── preprocess.py                   # Feature engineering and temporal window computation
│   └── train_models.py                 # Model training and chronological evaluation pipeline
│
├── styles/                             # Aqua Intelligence design system
│   ├── __init__.py
│   ├── styles.css                      # CSS custom properties, cards, badges, and responsive queries
│   └── theme.py                        # Light and Dark theme palette injection
│
├── data/                               # Hydrological and meteorological datasets
│   ├── processed/
│   │   └── purandar_groundwater_features.csv    # 680 feature-engineered records (1996–2023)
│   └── raw/
│       ├── purandar_rainfall_1991_2023.csv      # Daily IMD rainfall records
│       └── purandhar_groundwater_level_merged.csv # Raw CGWB in-situ groundwater records
│
├── models/                             # Trained serialized model artifacts
│   ├── rf_forecast_model.joblib        # Primary Random Forest next-observation model
│   ├── forecast_q10.joblib             # 10th percentile quantile regression model
│   ├── forecast_q90.joblib             # 90th percentile quantile regression model
│   └── rf_mapping_model.joblib         # Spatial regression artifact
│
├── reports/                            # Benchmarking reports and evaluation logs
│   └── model_evaluation.json           # Exact held-out metrics, coverage, and horizon statistics
│
└── tests/                              # Comprehensive automated test suite (56 passed)
    ├── test_depth_classification.py    # 9 tests: physical depth tiers and advisory selection
    ├── test_forecast_screen.py         # 7 tests: forecast calculations, bounds, disclaimers
    ├── test_groundwater_map.py         # 9 tests: coordinates, filters, popup attributes, CSS
    ├── test_metric_cards_layout.py     # 3 tests: CSS flexbox rules, fluid typography, breakpoints
    ├── test_pipeline_integrity.py      # 8 tests: zero leakage, raw data integrity, metrics honesty
    ├── test_rainfall_relationship.py   # 4 tests: correlation calculations and edge cases
    ├── test_seasonal_comparison.py     # 6 tests: matched May/Nov pairs, yearly summary, edge cases
    ├── test_station_changes.py         # 5 tests: station changes, math consistency, Zendewadi gap
    └── test_theme_tokens.py            # 5 tests: token presence, theme parity, semantic alert colors
```

---

## 🚀 Installation & Local Execution

### Prerequisites

- Python 3.10, 3.11, 3.12, or 3.14
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/SuchitraKarde/BhujalDrishti.git
cd BhujalDrishti
```

### 2. Create and Activate a Virtual Environment

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the Dashboard

**Option A — Windows One-Click Launcher:**
Double-click `run_dashboard.bat` in the project root directory.

**Option B — Command Line:**
```bash
streamlit run app.py
```

The application will be accessible at **`http://localhost:8501`**.

---

## 🧪 Automated Test Suite

The test suite validates data pipeline integrity, chronological validation splits, mathematical consistency, depth classification boundaries, and UI components.

Execute the complete test suite:

```bash
python -m pytest tests/ -v
```

### Test Suite Summary (56 / 56 Passing)

| Test File | Test Count | Key Functionality Verified |
|---|:---:|---|
| [tests/test_depth_classification.py](tests/test_depth_classification.py) | **9** | Canonical boundary values (3.99m, 4.00m, 8.00m, 8.01m), physical reference tiers, advisory branch selection, invalid value handling. |
| [tests/test_forecast_screen.py](tests/test_forecast_screen.py) | **7** | Station eligibility ($\ge 10$ records), baseline prediction mathematical bounds, direction of change classification, what-if responsiveness, evaluation metrics consistency. |
| [tests/test_groundwater_map.py](tests/test_groundwater_map.py) | **9** | Station coordinate validity, depth tier stratification counts, defensive coordinate filtering, popup attributes, scientific terminology, label contrast CSS. |
| [tests/test_metric_cards_layout.py](tests/test_metric_cards_layout.py) | **3** | CSS flex rules, container height stretching, fluid typography `clamp()`, responsive media query breakpoints. |
| [tests/test_pipeline_integrity.py](tests/test_pipeline_integrity.py) | **8** | Raw data integrity, negative depth value preservation, chronological train/test split zero-leakage, no future features, evaluation metric honesty. |
| [tests/test_rainfall_relationship.py](tests/test_rainfall_relationship.py) | **4** | Dynamic Pearson/Spearman correlations, multi-window lookbacks, annual correlations, NaN/edge-case handling. |
| [tests/test_seasonal_comparison.py](tests/test_seasonal_comparison.py) | **6** | Strict matched May/November station-year pairs, depth change directionality, yearly summary aggregation, empty/unmatched edge cases. |
| [tests/test_station_changes.py](tests/test_station_changes.py) | **5** | Dynamic station-wise depth change, mathematical consistency (positive = deeper), Zendewadi 2,206-day gap detection, observation recency counts. |
| [tests/test_theme_tokens.py](tests/test_theme_tokens.py) | **5** | Token structure, light/dark theme parity, semantic alert tokens, contrast compliance. |
| **Total** | **56** | **All 56 tests passing** |

---

## ⚖️ Disclaimer & Research Use

BhujalDrishti (JalRakshak AI) is an experimental academic prototype developed for computational hydrology research and methodology exploration.

- **Non-Regulatory**: Outputs do not constitute official statutory groundwater assessments under Central Ground Water Board (CGWB), State Groundwater Surveys and Development Agency (GSDA), or Central Ground Water Authority (CGWA) frameworks.
- **Physical Reference Tiers vs. Statutory Categories**: Project depth tiers (<4m, 4–8m, >8m MBGL) reflect physical observation depth and do not equate to taluka-wide extraction stage categories (*Safe, Semi-Critical, Critical, Over-Exploited*).
- **Engineering Feasibility**: Interventions presented in the decision support screen are preliminary planning heuristics. All structural watershed interventions require comprehensive on-site geophysical surveys, lithological logging, infiltration testing, and civil engineering design prior to implementation.
- **Data Recency**: Station assessments reflect the latest available discrete historical surveys and do not depict live or current aquifer conditions.
