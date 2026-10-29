# 💧 BhujalDrishti (JalRakshak AI)
### Multimodal GIS & Machine Learning Framework for Groundwater Level Mapping and Forecasting in Purandar Taluka, Maharashtra

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/pytest-25%20passed-brightgreen.svg)](tests/)
[![Research Prototype](https://img.shields.io/badge/status-Research%20Prototype-teal.svg)](#)

**BhujalDrishti (JalRakshak AI)** is a scientific hydrological intelligence dashboard and decision-support platform designed for regional groundwater monitoring, predictive next-observation forecasting, spatial GIS mapping, and site-specific conservation planning. The system focuses on **Purandar Taluka (~1,105 km²)** in Pune District, Maharashtra, an arid-to-semi-arid rain-shadow agro-ecological tract situated on the **Deccan Traps Basalt** geological formation.

---

## 📌 Hydrogeological & Regional Context

- **Study Area**: Purandar Taluka, Pune District, Maharashtra, India (~1,105 km²).
- **Aquifer Framework**: Layered basaltic lava flows (Deccan Traps) characterized by low primary porosity, secondary weathering/fracture zones, anisotropic permeability, and shallow dynamic groundwater storage.
- **Monitoring Network**: 11 Central Ground Water Board (CGWB) in-situ observation wells with multi-decadal quarterly telemetry spanning **1996 through 2023** (680 verified historical records).
- **Precipitation Regime**: 4-point India Meteorological Department (IMD) high-resolution ($0.25^\circ \times 0.25^\circ$) daily gridded rainfall dataset. Stations outside the grid polygon are modeled via spatial extrapolation with transparent telemetry flagging.
- **Chronological Split (Zero-Target-Leakage)**: Training data strictly partitioned from **1996 to 2017**; held-out evaluation and uncertainty testing strictly conducted on **2018 through 2023** ($n=124$ events).

---

## 🚀 The 4 Application Screens

The application is refactored into a screen-wise, decoupled modular architecture powered by the custom **Aqua Intelligence UI System**:

```
                                  ┌────────────────────────┐
                                  │   app.py (App Shell)   │
                                  └───────────┬────────────┘
                                              │
                      ┌───────────────────────┼───────────────────────┐
                      ▼                       ▼                       ▼
            ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
            │  Screen 1:        │   │  Screen 2:        │   │  Screen 3:        │
            │  Overview         │   │  Groundwater Map  │   │  Next-Observation │
            │  Dashboard        │   │  (GIS Leaflet)    │   │  Forecast         │
            └───────────────────┘   └───────────────────┘   └─────────┬─────────┘
                                                                      │
                                            ┌─────────────────────────┴─────────┐
                                            ▼                                   ▼
                                  ┌───────────────────┐               ┌───────────────────┐
                                  │  Screen 4:        │               │ Uncertainty / CQR │
                                  │  Decision Support │               │ Calibration Guide │
                                  │  (Advisory)       │               └───────────────────┘
                                  └───────────────────┘
```

### 1. 📊 Screen 1 — Overview Dashboard
- **Responsive KPI Cards**: Real-time summary cards displaying Mean Water Table Depth (`6.88 m MBGL`), Active Monitoring Network (`11 Wells`), Historical Time Series (`680 Records`), and Held-Out Model MAE (`2.092 m`). Built with fluid typography (`clamp()`) and flex-column container height stretching.
- **Depth Tier Distribution Badges**: Summary indicator badges classifying latest water table observations across project-defined reference bands (<4.0 m Shallow, 4.0–8.0 m Moderate, >8.0 m Deep).
- **Dual-Axis Hydrological Dynamics**: Matplotlib visualization correlating 365-day cumulative antecedent precipitation with mean annual water table fluctuations, featuring an inverted groundwater axis (shallower depths pointing upward).
- **Pre- vs. Post-Monsoon Trends**: Historical recharge and post-monsoon depletion trajectories tracing long-term multi-decadal aquifer behavior.

### 2. 🗺️ Screen 2 — Interactive GIS Groundwater Map
- **Interactive Leaflet Cartography**: Native Leaflet.js embedding centered at Purandar Taluka coordinates `(18.28° N, 74.12° E)` with zoom constraints and scale controls.
- **Telemetry Station Pins**: 11 fixed-geometry markers color-coded by current physical depth band:
  - 🟢 **Shallow Depth**: $< 4.0\text{ m}$ MBGL (High water table / near-surface).
  - 🟡 **Moderate Depth**: $4.0\text{–}8.0\text{ m}$ MBGL (Intermediate water table).
  - 🔴 **Deep Depth**: $> 8.0\text{ m}$ MBGL (Stressed / deep water table).
- **Telemetry Popups**: Detailed station inspect cards showing station name, exact recorded depth, observation date, seasonal tag, and data extrapolation status.
- **Dynamic Dark Tile Shader**: Cartographic tile filter adjusting map contrast and luminance to preserve visual ergonomics when toggling between Light and Dark themes.

### 3. 🔮 Screen 3 — Next-Observation Groundwater Forecast
- **Station Drilldown Selector**: Telemetry inspect panel displaying recorded depth, preceding 90-day rain, and preceding 365-day cumulative rainfall for the selected station.
- **Machine Learning Forecast Engine**: Random Forest regression predicting the next scheduled CGWB monitoring observation date (held-out test set horizon: median 92.0 days, mean 109.4 days).
- **Uncalibrated Quantile Intervals ($q_{10}$–$q_{90}$)**: Quantile regression models predicting lower and upper bounds (nominal 80% interval).
- **Empirical Coverage Transparency**: Prominent display of measured test coverage (**57.26%** coverage vs. 80% nominal target; undercoverage miss rate 42.74%) with the explicit scientific caveat: `*Does not guarantee future coverage*`.
- **Benchmark Evaluation Cards**: Equal-height benchmark comparison showing Random Forest performance vs. Persistence Baseline (23.8% lower MAE).
- **Hypothetical Rainfall Sensitivity Slider**: Interactive simulation slider ($\pm 50\%$) scaling antecedent 30-day to 365-day cumulative rainfall features to evaluate aquifer sensitivity under wet and drought scenarios.
- **Historical Station Chart**: High-resolution time-series plot of station-specific water table dynamics with inverted y-axis.
- **Conformalized Quantile Regression (CQR) Guide**: Theoretical methodology expander detailing split conformal prediction, non-conformity scores, calibration steps, and finite-sample marginal coverage guarantees.

### 4. 🛡️ Screen 4 — Conservation & Decision Support
- **Consistent Physical Depth Tiering**: Standardized three-tier classification applied consistently with the Groundwater Map screen.
- **Station Telemetry Matrix**: Tabular overview of all 11 stations showing latest recorded water levels, classification tiers, and primary recommended interventions.
- **Supply-Side Interventions**: Geologically matched structural artificial recharge recommendations for basaltic terrain:
  - *Continuous Contour Trenches (CCT)* & staggered trenching on upper ridge slopes.
  - *Percolation Tanks* and *Cement Nala Bunds / Check Dams* in secondary drainage lines.
  - *Farm Ponds with plastic lining* for runoff harvesting.
  - *Sub-Surface Dykes* in alluvial/valley fills to arrest baseflow drainage.
- **Demand-Side Management**: Recommended micro-irrigation systems (drip/sprinkler), crop water budgeting, and diversification away from water-intensive perennials during prolonged deep water table regimes.
- **Scientific Advisory Disclaimer**: Transparent clarification that project-defined physical depth tiers reflect point telemetry observations and do not substitute for official CGWB/GEC taluka-wide extraction stage assessments (Safe, Semi-Critical, Critical, Over-Exploited).

---

## 📊 Model Benchmarks & Scientific Rigor

All predictive models were evaluated using a strict **chronological validation split** without cross-validation shuffling or future feature leakage:

| Metric / Parameter | Random Forest Model | Persistence Baseline | Relative Improvement |
|---|---|---|---|
| **Mean Absolute Error (MAE)** | **2.092 m** | 2.744 m | **23.8% Error Reduction** |
| **Root Mean Squared Error (RMSE)** | **2.899 m** | 3.709 m | **21.8% Error Reduction** |
| **Coefficient of Determination ($R^2$)** | **0.247** | — | — |
| **Nominal Interval Target** | 80.0% ($q_{10}$–$q_{90}$) | — | — |
| **Empirical Test Coverage ($n=124$)** | **57.26%** (Undercoverage) | — | Miss rate: 42.74% |
| **Average Interval Width** | **4.36 m** | — | — |

*Evaluation metadata is preserved in [reports/model_evaluation.json](file:///c:/Users/SOHAN/Desktop/BhujalDrishti/reports/model_evaluation.json).*

---

## 🎨 Aqua Intelligence UI System & Dual Themes

The interface incorporates a custom scientific UI design system featuring:

- **Dual-Theme Engine**:
  - ☀️ **Light Theme**: Clean, scientific white-and-slate canvas (`#F8FAFC` base, `#FFFFFF` cards, `#007B8A` teal accent, `#1E3A8A` deep navy headings).
  - 🌙 **Dark Theme (Aqua)**: Deep oceanic palette (`#0F1E25` base, `#162E35` cards, `#23414B` borders, `#2DD4BF` aqua accent, `#38BDF8` blue glow).
- **Theme-Aware Tokens & Alert Theming**: Custom styling for `st.info`, `st.warning`, `st.success`, and `st.error` blocks ensuring WCAG-compliant text/background contrast in both light and dark themes.
- **Fluid Typography**: Dynamic sizing using CSS `clamp()` (`clamp(1.15rem, 1.8vw, 1.55rem)`) preventing metric text overflow across laptop, tablet, and narrow desktop viewports.
- **Equal-Height Card Layout**: Multi-level flexbox stretching across Streamlit column hierarchies (`stHorizontalBlock` $\to$ `stColumn` $\to$ `stVerticalBlock` $\to$ `stElementContainer` $\to$ `stMarkdownContainer` $\to$ `.kpi-card` / `.metric-card`).
- **Responsive Breakpoints**:
  - `@media (max-width: 1080px)`: Wraps 4-column KPI rows into a clean 2×2 grid; wraps 3-column evaluation metrics into a balanced 2+1 grid.
  - `@media (max-width: 640px)`: Fluid full-width stacking.

---

## 📂 Project Directory Structure

```
BhujalDrishti/
├── app.py                          # Streamlit entry point, router & theme state manager
├── requirements.txt                # Pinned production dependencies
├── run_dashboard.bat               # Windows one-click launcher
├── README.md                       # Comprehensive project documentation
│
├── components/                     # Reusable presentation components
│   ├── header.py                   # Branded Aqua Intelligence header & badges
│   ├── sidebar.py                  # Theme switcher, navigation & telemetry context
│   ├── metric_cards.py             # Equal-height KPI and evaluation metric cards
│   ├── map_view.py                 # Embedded Leaflet.js interactive map component
│   ├── charts.py                   # Theme-adaptive Matplotlib hydrological charts
│   ├── callouts.py                 # Horizon schedule callouts & CQR expander
│   └── tables.py                   # Station data tables & telemetry matrix
│
├── screens/                        # Modular screen controllers
│   ├── overview.py                 # Screen 1: Regional Overview Dashboard
│   ├── groundwater_map.py          # Screen 2: Interactive GIS Groundwater Map
│   ├── forecast.py                 # Screen 3: Next-Observation Forecast & Uncertainty
│   └── decision_support.py         # Screen 4: Conservation Planning & Decision Support
│
├── services/                       # Business logic and inference services
│   ├── data_loader.py              # Telemetry loading, caching & canonical depth tiering
│   ├── model_service.py            # Next-observation inference & sensitivity calculation
│   └── metrics_service.py          # Summary aggregations & regional health metrics
│
├── styles/                         # Aqua Intelligence styling system
│   ├── styles.css                  # Core CSS design tokens, cards & media queries
│   └── theme.py                    # Dynamic theme palette injection & alert contrast
│
├── data/                           # Hydrological & spatial datasets
│   ├── purandar_groundwater_telemetry.csv  # 11 CGWB stations, 680 records (1996–2023)
│   ├── raw/                        # Original raw rainfall and telemetry records
│   └── processed/                  # Feature-engineered spatio-temporal datasets
│
├── models/                         # Serialized machine learning model artifacts
│   ├── rf_model.joblib             # Primary Random Forest next-observation model
│   ├── q10_model.joblib            # 10th percentile quantile regression model
│   └── q90_model.joblib            # 90th percentile quantile regression model
│
├── reports/                        # Evaluation metrics and experiment logs
│   └── model_evaluation.json       # Exact MAE, RMSE, R² & empirical coverage metrics
│
└── tests/                          # Automated test suite (25/25 passing)
    ├── test_depth_classification.py    # 9 tests: canonical boundaries & advisory branches
    ├── test_pipeline_integrity.py      # 8 tests: zero leakage, data integrity & metrics
    ├── test_theme_tokens.py            # 5 tests: theme palettes, tokens & parity
    └── test_metric_cards_layout.py     # 3 tests: flex rules, fluid clamps & breakpoints
```

---

## 🧪 Automated Testing & Quality Assurance

The codebase includes comprehensive unit and integration testing with **100% pass rate (25/25 tests)**:

```bash
python -m pytest tests/test_depth_classification.py tests/test_pipeline_integrity.py tests/test_theme_tokens.py tests/test_metric_cards_layout.py -v
```

### Test Coverage Highlights
1. **`test_depth_classification.py` (9 tests)**:
   - Validates canonical project boundaries: `<4.0 m` (Shallow), `4.0 <= depth <= 8.0 m` (Moderate), `>8.0 m` (Deep).
   - Verifies exact edge behavior at boundary points ($3.99\text{ m}$, $4.00\text{ m}$, $7.99\text{ m}$, $8.00\text{ m}$, $8.01\text{ m}$).
   - Validates missing/invalid data handling and advisory branch routing for all 11 stations.
2. **`test_pipeline_integrity.py` (8 tests)**:
   - Verifies raw dataset integrity and negative value preservation (artesian/near-surface water table).
   - Confirms zero-target leakage in the chronological train/test split.
   - Enforces that no future features are used in inference.
   - Asserts mathematical consistency between reported and actual evaluation metrics.
3. **`test_theme_tokens.py` (5 tests)**:
   - Verifies color token existence and parity between Light and Dark palettes.
   - Ensures semantic alert tokens and contrast ratios.
4. **`test_metric_cards_layout.py` (3 tests)**:
   - Verifies CSS flexbox equal-height rules and container stretching.
   - Verifies responsive media query breakpoints (`1080px`, `640px`).
   - Ensures fluid typography `clamp()` prevents text truncation without brittle `white-space: nowrap`.

---

## 💻 Installation & Local Setup

### Prerequisites
- Python 3.10, 3.11, or 3.12+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/educational454-ai/jal.git
cd BhujalDrishti
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Dashboard

**Option A — One-Click (Windows):**
Double-click `run_dashboard.bat` in the root folder.

**Option B — Command Line:**
```bash
streamlit run app.py
```
Open your browser at **`http://localhost:8501`**.

---

## 📖 Citation & Research Attribution

If you utilize BhujalDrishti or its analytical methodology in your research, please cite:

```bibtex
@misc{bhujaldrishti2026,
  author = {BhujalDrishti Research Team},
  title = {BhujalDrishti (JalRakshak AI): Multimodal GIS and Machine Learning for Groundwater Level Mapping and Forecasting in Purandar Taluka, Maharashtra},
  year = {2026},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/educational454-ai/jal}}
}
```

---

## ⚖️ License & Research Disclaimer
This software is distributed for academic research, education, and technical evaluation. All predictive outputs are statistical estimates derived from historical telemetry and gridded meteorological inputs, not actual physical future measurements. Site-specific groundwater management decisions should integrate field hydrogeological borewell logging and statutory CGWB/GSDA administrative guidelines.
