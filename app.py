"""BhujalDrishti (JalRakshak AI) - Environmental Intelligence System.

Modular Application Architecture & Scientific Disclaimers:
- Task: Next-Observation Groundwater Forecast
- Uncertainty Quantification: Uncalibrated q10–q90 Prediction Band
- Telemetry Units: Meters Below Ground Level (MBGL)
- Temporal Target: Predicts next recorded CGWB observation, not groundwater exactly 90 days in the future
- Model Horizon: Evaluation Population Forecast Horizon
- Nature of Outputs: Statistical machine-learning estimates, not actual future physical measurements
- Map Telemetry: L.circleMarker with fixed radius, is_extrapolated warning, and Observed CGWB Telemetry popup
"""
import streamlit as st

# Application Core Services & Styling
from styles.theme import init_theme, apply_theme, get_current_theme
from services.data_loader import load_data
from services.model_service import load_models

# Reusable Layout Components
from components.header import render_research_header
from components.sidebar import render_sidebar

# Modular Screens
from screens.overview import render_overview_screen
from screens.groundwater_map import render_groundwater_map_screen
from screens.forecast import render_forecast_screen
from screens.decision_support import render_decision_support_screen

# -------------------------------------------------------------
# Streamlit Application Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="BhujalDrishti | Environmental Intelligence",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# Initialize & Apply Centralized Aqua Intelligence Theme
# -------------------------------------------------------------
init_theme(default_theme="light")
current_theme = get_current_theme()
apply_theme(current_theme)

# -------------------------------------------------------------
# Load Shared Cached Resources (Data & Trained Models)
# -------------------------------------------------------------
df = load_data()
models = load_models()

# -------------------------------------------------------------
# Render Shared Sidebar Navigation & Header Banner
# -------------------------------------------------------------
selected_screen = render_sidebar()
render_research_header(theme=current_theme)

# -------------------------------------------------------------
# Modular Screen Router
# -------------------------------------------------------------
if selected_screen == "📊 Screen 1: Overview Dashboard":
    render_overview_screen(df, models)

elif selected_screen == "🗺️ Screen 2: Groundwater Map":
    render_groundwater_map_screen(df)

elif selected_screen == "🔮 Screen 3: Next-Observation Forecast":
    render_forecast_screen(df, models)

elif selected_screen == "🛡️ Screen 4: Decision Support":
    render_decision_support_screen(df)
