"""Reusable UI presentation components for BhujalDrishti."""
from components.header import render_research_header
from components.sidebar import render_sidebar
from components.metric_cards import (
    render_kpi_card,
    render_overview_kpis,
    render_depth_distribution_bar,
    render_evaluation_result_cards,
)
from components.charts import render_rainfall_groundwater_chart, render_station_history_chart
from components.tables import render_latest_stations_table
from components.map_view import render_groundwater_map
from components.callouts import (
    render_depth_tier_note,
    render_forecast_mbgl_info,
    render_horizon_callout,
    render_spatial_model_status_expander,
    render_cqr_calibration_expander,
    render_decision_support_advisory_notice,
)

__all__ = [
    "render_research_header",
    "render_sidebar",
    "render_kpi_card",
    "render_overview_kpis",
    "render_depth_distribution_bar",
    "render_evaluation_result_cards",
    "render_rainfall_groundwater_chart",
    "render_station_history_chart",
    "render_latest_stations_table",
    "render_groundwater_map",
    "render_depth_tier_note",
    "render_forecast_mbgl_info",
    "render_horizon_callout",
    "render_spatial_model_status_expander",
    "render_cqr_calibration_expander",
    "render_decision_support_advisory_notice",
]
