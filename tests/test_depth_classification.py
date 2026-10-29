"""Unit tests for physical depth tier classification and intervention planning."""
import math
import numpy as np
import pandas as pd
import pytest
from services.data_loader import (
    get_depth_tier,
    get_depth_tier_category,
    get_status,
    get_intervention_plan,
    load_data,
    get_latest_per_station,
)


def test_canonical_boundary_exact_values():
    """Verify the exact required evaluation boundary points map to canonical categories."""
    assert get_depth_tier_category(3.99) == "Shallow"
    assert get_depth_tier_category(4.00) == "Moderate"
    assert get_depth_tier_category(6.00) == "Moderate"
    assert get_depth_tier_category(8.00) == "Moderate"
    assert get_depth_tier_category(8.01) == "Deep"


def test_depth_below_4m():
    """Verify depths below 4.0 m are classified as Shallow phreatic tier."""
    test_values = [-0.40, 0.0, 1.25, 2.50, 3.99]
    for d in test_values:
        tier_label, color, badge = get_depth_tier(d)
        assert tier_label == "Shallow (< 4.0 m)", f"Failed for depth {d}"
        assert color == "#0F766E"
        assert badge == "badge-shallow"
        assert get_depth_tier_category(d) == "Shallow"
        
        plan = get_intervention_plan(d)
        assert plan["category"] == "Shallow"
        assert plan["icon"] == "🟢"
        assert plan["priority"] == "Equilibrium Maintenance & Monitoring Advisory"
        assert len(plan["actions"]) > 0


def test_depth_exactly_4m():
    """Verify depth of exactly 4.0 m is classified as Moderate boundary tier."""
    d = 4.00
    tier_label, color, badge = get_depth_tier(d)
    assert tier_label == "Moderate (4.0–8.0 m)"
    assert color == "#854D0E"
    assert badge == "badge-moderate"
    assert get_depth_tier_category(d) == "Moderate"
    
    plan = get_intervention_plan(d)
    assert plan["category"] == "Moderate"
    assert plan["icon"] == "🟡"
    assert plan["priority"] == "Precautionary Stewardship & Recharge Advisory"
    assert len(plan["actions"]) > 0


def test_depth_between_4m_and_8m():
    """Verify depths between 4.0 m and 8.0 m are classified as Moderate tier."""
    test_values = [4.01, 5.06, 6.00, 6.20, 7.08, 7.99]
    for d in test_values:
        tier_label, color, badge = get_depth_tier(d)
        assert tier_label == "Moderate (4.0–8.0 m)", f"Failed for depth {d}"
        assert color == "#854D0E"
        assert badge == "badge-moderate"
        assert get_depth_tier_category(d) == "Moderate"
        
        plan = get_intervention_plan(d)
        assert plan["category"] == "Moderate"
        assert plan["icon"] == "🟡"
        assert plan["priority"] == "Precautionary Stewardship & Recharge Advisory"
        assert len(plan["actions"]) > 0


def test_depth_exactly_8m():
    """Verify depth of exactly 8.0 m is classified as Moderate boundary tier."""
    d = 8.00
    tier_label, color, badge = get_depth_tier(d)
    assert tier_label == "Moderate (4.0–8.0 m)"
    assert color == "#854D0E"
    assert badge == "badge-moderate"
    assert get_depth_tier_category(d) == "Moderate"
    
    plan = get_intervention_plan(d)
    assert plan["category"] == "Moderate"
    assert plan["icon"] == "🟡"
    assert plan["priority"] == "Precautionary Stewardship & Recharge Advisory"
    assert len(plan["actions"]) > 0


def test_depth_above_8m():
    """Verify depths above 8.0 m are classified as Deep tier."""
    test_values = [8.01, 8.34, 8.48, 10.50, 16.0]
    for d in test_values:
        tier_label, color, badge = get_depth_tier(d)
        assert tier_label == "Deep (> 8.0 m)", f"Failed for depth {d}"
        assert color == "#991B1B"
        assert badge == "badge-deep"
        assert get_depth_tier_category(d) == "Deep"
        
        plan = get_intervention_plan(d)
        assert plan["category"] == "Deep"
        assert plan["icon"] == "🔴"
        assert plan["priority"] == "High-Vulnerability Monitoring & Conservation Advisory"
        assert len(plan["actions"]) > 0


def test_missing_and_invalid_depth():
    """Verify missing, NaN, and invalid non-numeric depths return safe unclassified results."""
    invalid_values = [None, np.nan, float("nan"), math.nan, "invalid", "", "N/A"]
    for val in invalid_values:
        assert get_depth_tier_category(val) == "Unknown", f"Failed for {val}"
        
        tier_label, color, badge = get_depth_tier(val)
        assert tier_label == "Unknown / Unclassified"
        assert color == "#64748B"
        assert badge == "badge-unknown"
        
        # Test backward-compatible alias get_status
        stat_label, stat_color, stat_badge = get_status(val)
        assert stat_label == "Unknown / Unclassified"
        assert stat_color == "#64748B"
        assert stat_badge == "badge-unknown"
        
        plan = get_intervention_plan(val)
        assert plan["category"] == "Unknown"
        assert plan["icon"] == "⚪"
        assert plan["priority"] == "Telemetry Unavailable / Unclassified"
        assert plan["badge"] == "badge-unknown"
        assert len(plan["actions"]) >= 1


def test_advisory_branch_selection():
    """Verify each canonical category selects its designated distinct advisory branch."""
    # Shallow branch
    shallow_plan = get_intervention_plan(2.5)
    assert shallow_plan["category"] == "Shallow"
    assert shallow_plan["icon"] == "🟢"
    assert "Equilibrium" in shallow_plan["priority"]
    assert any("Participatory Community Water Budgeting" in title for title, _ in shallow_plan["actions"])
    
    # Moderate branch
    mod_plan = get_intervention_plan(5.5)
    assert mod_plan["category"] == "Moderate"
    assert mod_plan["icon"] == "🟡"
    assert "Precautionary" in mod_plan["priority"]
    assert any("Contour Bunding" in title for title, _ in mod_plan["actions"])
    
    # Deep branch
    deep_plan = get_intervention_plan(9.0)
    assert deep_plan["category"] == "Deep"
    assert deep_plan["icon"] == "🔴"
    assert "High-Vulnerability" in deep_plan["priority"]
    assert any("Artificial Recharge Exploration" in title for title, _ in deep_plan["actions"])
    
    # Unknown branch
    unknown_plan = get_intervention_plan(None)
    assert unknown_plan["category"] == "Unknown"
    assert unknown_plan["icon"] == "⚪"
    assert "Telemetry Unavailable" in unknown_plan["priority"]
    assert any("Verify Station Telemetry" in title for title, _ in unknown_plan["actions"])


def test_station_telemetry_intervention_coverage():
    """Verify all 11 stations in Purandar Taluka produce valid plans across physical tiers."""
    df = load_data()
    latest_st = get_latest_per_station(df)
    assert len(latest_st) == 11
    
    categories_found = set()
    for _, row in latest_st.iterrows():
        plan = get_intervention_plan(row["gw_level_mbgl"])
        categories_found.add(plan["category"])
        assert plan["icon"] in ["🔴", "🟡", "🟢"]
        assert len(plan["actions"]) >= 2
        
    # Purandar has stations across all physical depth tiers
    assert "Deep" in categories_found, "Deep stations missing in telemetry"
    assert "Moderate" in categories_found, "Moderate stations missing in telemetry"
    assert "Shallow" in categories_found, "Shallow stations missing in telemetry"
    assert "Unknown" not in categories_found, "Valid station telemetry unexpectedly flagged Unknown"
