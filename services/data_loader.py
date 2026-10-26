"""Data loading, feature preparation, and physical depth classification services for BhujalDrishti."""
import pandas as pd
import streamlit as st

EXTRAPOLATED_STATIONS = {
    'Pimpri (Kh) Malvasti',
    'Kamatwadi-Walha',
    'Walha',
    'Narayanpur'
}


@st.cache_data
def load_data(filepath: str = "data/processed/purandar_groundwater_features.csv") -> pd.DataFrame:
    """Load processed groundwater dataset with calendar lookbacks and extrapolation flags."""
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    
    # Defensive verification of rainfall extrapolation flag
    if 'is_rainfall_extrapolated' not in df.columns:
        df['is_rainfall_extrapolated'] = df['station'].apply(
            lambda s: 1 if s in EXTRAPOLATED_STATIONS else 0
        )
    return df


def get_latest_per_station(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the latest observed telemetry snapshot per monitoring station."""
    latest = df.sort_values('date').groupby('station').last().reset_index()
    if 'is_rainfall_extrapolated' not in latest.columns:
        latest['is_rainfall_extrapolated'] = latest['station'].apply(
            lambda s: 1 if s in EXTRAPOLATED_STATIONS else 0
        )
    return latest


def get_depth_tier(mbgl: float) -> tuple[str, str, str]:
    """Classify water table depth into project-defined physical reference tiers.
    
    Boundary definitions:
    - Shallow: mbgl < 4.0 m
    - Moderate: 4.0 <= mbgl <= 8.0 m (inclusive of boundary values 4.0 m and 8.0 m)
    - Deep: mbgl > 8.0 m
    
    Note: These tiers are project-defined physical reference bands for instantaneous
    telemetry visualization. They do not constitute official Central Ground Water Board
    (CGWB) or Groundwater Estimation Committee (GEC) administrative exploitation categories.
    
    Returns:
        (tier_label, hex_color, badge_css_class)
    """
    if mbgl < 4.0:
        return "Shallow (< 4.0 m)", "#0F766E", "badge-shallow"
    elif mbgl <= 8.0:
        return "Moderate (4.0–8.0 m)", "#854D0E", "badge-moderate"
    else:
        return "Deep (> 8.0 m)", "#991B1B", "badge-deep"


def get_depth_tier_category(mbgl: float) -> str:
    """Return canonical tier category string: 'Shallow', 'Moderate', or 'Deep'."""
    if mbgl < 4.0:
        return "Shallow"
    elif mbgl <= 8.0:
        return "Moderate"
    else:
        return "Deep"


def get_status(mbgl: float) -> tuple[str, str, str]:
    """Backward-compatible alias for get_depth_tier."""
    return get_depth_tier(mbgl)


def get_intervention_plan(mbgl: float) -> dict:
    """Return rule-based conservation advisories corresponding to physical depth tiers.
    
    Advisory notes:
    Recommendations are synthesized heuristics from CGWB and GSDA watershed guidelines,
    intended for preliminary decision support. Water table depth alone does not establish
    the complex localized cause of groundwater conditions (e.g. lithological variation,
    fracture connectivity, localized pumping, or topographic recharge dynamics).
    """
    cat = get_depth_tier_category(mbgl)
    if cat == "Deep":
        return {
            "category": "Deep",
            "tier_label": "Deep (> 8.0 m)",
            "icon": "🔴",
            "color": "#991B1B",
            "badge": "badge-deep",
            "priority": "High Priority Intervention Advisory",
            "priority_level": "Deep / Stress Tier (> 8.0 m MBGL)",
            "actions": [
                ("Artificial Recharge Structures", "Prioritize expedited site surveys for percolation tanks and cement check dams across regional nalas to capture monsoon runoff in fractured basalt."),
                ("Extraction Monitoring & Borewell Review", "Review high-capacity commercial extraction permits and recommend voluntary seasonal pumping moderation until post-monsoon water table recovery."),
                ("Crop Shift Advisory", "Promote transition of water-intensive summer crops (e.g., sugarcane) toward drought-hardy pulses, millets, and drip-irrigated horticulture (custard apple, pomegranate)."),
                ("Lined Farm Ponds (Shet-Tale)", "Encourage plastic lining for farm ponds to eliminate excessive percolation loss from surface storage in porous soils.")
            ]
        }
    elif cat == "Moderate":
        return {
            "category": "Moderate",
            "tier_label": "Moderate (4.0–8.0 m)",
            "icon": "🟡",
            "color": "#854D0E",
            "badge": "badge-moderate",
            "priority": "Moderate Depletion Precaution",
            "priority_level": "Moderate Dynamic Tier (4.0–8.0 m MBGL)",
            "actions": [
                ("Continuous Contour Trenches (CCT)", "Implement ridge-to-valley soil moisture conservation and contour bunding on upper slope wasteland and barren lands to enhance recharge lag time."),
                ("Micro-Irrigation Incentives", "Promote expanded drip and micro-sprinkler irrigation systems for fig, vegetable, and orchard farming to reduce consumptive demand."),
                ("Rooftop Rainwater Harvesting", "Incentivize injection well recharge and direct rooftop harvesting for institutional, gram panchayat, and residential structures.")
            ]
        }
    else:  # Shallow (< 4.0 m)
        return {
            "category": "Shallow",
            "tier_label": "Shallow (< 4.0 m)",
            "icon": "🟢",
            "color": "#0F766E",
            "badge": "badge-shallow",
            "priority": "Sustainable Level Maintained",
            "priority_level": "Shallow Phreatic Tier (< 4.0 m MBGL)",
            "actions": [
                ("Aquifer Maintenance & Monitoring", "Continue systematic quarterly water level observation; avoid concentrated deep extraction that could induce localized drawdown cones."),
                ("Community Water Budgeting", "Conduct bi-annual village participatory water audits at Gram Sabha meetings prior to rabi cropping season to maintain safe yields.")
            ]
        }
