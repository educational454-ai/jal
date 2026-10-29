"""Unit tests for BhujalDrishti metric card layout and responsive styling."""
import os
import re
import pytest


def test_styles_css_metric_card_flex_rules():
    """Verify CSS defines flexbox layout and equal height rules for KPI and metric cards."""
    css_path = os.path.join(os.path.dirname(__file__), "..", "styles", "styles.css")
    assert os.path.exists(css_path), "styles.css must exist"
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # Verify .kpi-card flex rules
    assert ".kpi-card" in css
    assert "display: flex" in css
    assert "justify-content: space-between" in css
    assert "min-height: 135px" in css or "min-height:" in css

    # Verify .metric-card flex rules
    assert ".metric-card" in css
    assert ".metric-card-title" in css
    assert ".metric-card-body" in css
    assert ".metric-card-caveat" in css

    # Verify container height stretching
    assert 'div[data-testid="stHorizontalBlock"]' in css
    assert "align-items: stretch" in css


def test_styles_css_responsive_breakpoints():
    """Verify responsive media queries for tablet and narrow desktop viewports exist."""
    css_path = os.path.join(os.path.dirname(__file__), "..", "styles", "styles.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    assert "@media (max-width: 1080px)" in css
    assert "@media (max-width: 640px)" in css
    assert "div[data-testid=\"stHorizontalBlock\"]:has(.kpi-card)" in css
    assert "div[data-testid=\"stHorizontalBlock\"]:has(.metric-card)" in css


def test_styles_theme_responsive_metric_rules():
    """Verify theme.py injects responsive typography without brittle nowrap on stMetricValue."""
    theme_path = os.path.join(os.path.dirname(__file__), "..", "styles", "theme.py")
    assert os.path.exists(theme_path), "theme.py must exist"
    with open(theme_path, "r", encoding="utf-8") as f:
        code = f.read()

    assert '[data-testid="stMetricLabel"]' in code or 'div[data-testid="stMetricLabel"]' in code
    assert 'div[data-testid="stMetricValue"]' in code
    assert 'clamp(' in code, "stMetricValue should use fluid typography clamp()"
    assert 'white-space: normal' in code, "stMetricValue should allow wrapping"
