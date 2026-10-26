"""Screens package for BhujalDrishti."""
from screens.overview import render_overview_screen
from screens.groundwater_map import render_groundwater_map_screen
from screens.forecast import render_forecast_screen
from screens.decision_support import render_decision_support_screen

__all__ = [
    "render_overview_screen",
    "render_groundwater_map_screen",
    "render_forecast_screen",
    "render_decision_support_screen",
]
