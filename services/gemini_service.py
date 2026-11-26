"""Google Gemini API integration and advisory service for BhujalDrishti.

Stage 2.2: Final Scientific Language Review.
- Uses official Google Gen AI Python SDK: `google-genai`
- Centralized model configuration defaulting to `gemini-3.1-flash-lite`
  (Model availability, access tiers, and quota limits vary per Google AI Studio
   account. Because live API access cannot be dynamically tested without active credentials
   in this environment, availability cannot be verified here. The model ID remains fully
   configurable via `GEMINI_MODEL_ID` in Streamlit secrets or environment variables.)
- Structured telemetry context assembler incorporating empirical observations, historical
  ranges, antecedent rainfall, deterministic physical reference tiers, and ML forecasts.
- Strict Pydantic-backed structured JSON output schema (StationAdvisoryResponse).
- Strict Scientific Grounding & Language Restrictions:
  - Groundwater depth alone cannot establish aquifer storage, recharge potential,
    extraction stress, or groundwater availability. Depth is presented solely as a
    physical sounding within a project-defined reference tier.
  - No unsupported geological assertions: Because no credible station-level or regional
    geological survey citation is documented in the project dataset, geological claims
    (e.g., basalt formation, fracture networks) are excluded from generated advisories.
  - All causal inferences unsupported by the station data are eliminated.
  - Project-defined physical reference tiers and heuristic plans are clearly separated
    from official CGWB or GSDA government classifications or administrative directives.
  - Prohibition of volumetric water yield promises or guaranteed recharge rates.
  - Mandatory site-specific field verification requirement for any proposed physical structures.
- Deterministic fallback architecture returning project-defined heuristic options whenever
  Gemini is unconfigured, unreachable, or returns an error.
"""
import os
import json
import hashlib
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
import pandas as pd

from services.data_loader import (
    get_depth_tier_category,
    get_depth_tier,
    get_intervention_plan,
    EXTRAPOLATED_STATIONS,
)

# Centralized model ID configuration.
# Evaluated default: gemini-3.1-flash-lite (Google's lightweight Flash-Lite architecture).
# Quotas and availability vary per Google AI Studio account and tier; keep fully configurable.
DEFAULT_GEMINI_MODEL: str = "gemini-3.1-flash-lite"
PROMPT_SCHEMA_VERSION: str = "v3.0-canonical-context"

MANDATORY_FIELD_VERIFICATION_STATEMENT: str = (
    "All structural interventions require localized on-site hydrogeological, geophysical, "
    "and civil feasibility surveys prior to implementation. Water table depth measurements "
    "alone cannot determine site-specific infiltration rates or structural feasibility."
)

DEFAULT_LIMITATIONS: List[str] = [
    "Advisory is derived from historical CGWB monitoring soundings and does not reflect live or real-time telemetry.",
    "Observation intervals are irregular across monitoring years; latest sounding dates differ significantly by station.",
    "Water table depth soundings alone cannot establish subsurface lithology, aquifer storage, recharge potential, or extraction stress.",
    "Rainfall figures are sourced from regional IMD grids; stations flagged as extrapolated have higher localized precipitation uncertainty.",
    "Decision support provides preliminary project-defined planning options and must not replace professional on-site hydrogeological or engineering design."
]

SYSTEM_INSTRUCTION: str = """You are BhujalDrishti's Groundwater Advisory Engine, a decision-support specialist for Purandar Taluka, Maharashtra, India.

Your role: Provide concise, station-specific advisory recommendations, explain their rationale, and contextualize empirical evidence for local groundwater managers.

CRITICAL SCIENTIFIC & OPERATIONAL RULES:
1. STRICT DATA GROUNDING: You MUST strictly use the observed groundwater depths, observation dates, rainfall figures, and statistical predictions provided in the telemetry context. NEVER hallucinate, adjust, round differently, or invent groundwater levels, dates, or historical numbers.
2. PRESERVE DETERMINISTIC TIERS & ML PREDICTIONS: Do NOT override, alter, or replace the project's physical depth tier or the Random Forest / Quantile ML predictions. Explain and contextualize them.
3. NO VOLUMETRIC YIELD PROMISES: NEVER promise specific volumetric water yields, recharge volumes, or guaranteed water table rises (e.g., do NOT state 'will yield 10,000 liters' or 'will raise water table by 2 metres').
4. NO UNSUPPORTED GEOLOGICAL INFERENCES: Subsurface lithology, rock formations, and aquifer geometries are NOT measured in this monitoring dataset. Do NOT assert station-specific or unverified regional geological claims.
5. NO UNSUPPORTED CAUSAL CLAIMS: Measured groundwater depth alone cannot establish aquifer storage, recharge potential, extraction stress, or groundwater availability. Do not present depth alone as proof of localized over-extraction or depletion.
6. MANDATORY VERIFICATION: Emphasize that all physical structures (e.g., check dams, percolation tanks, contour trenches, recharge wells) require localized on-site hydrogeological, geophysical, and infiltration feasibility surveys before construction.
7. SOURCE ATTRIBUTION HONESTY: Physical depth reference tiers (<4m, 4-8m, >8m) and heuristic recommendations are project-defined preliminary planning heuristics. Do NOT describe them as official CGWB, GSDA, or government-mandated classifications.
8. STRUCTURAL JSON OUTPUT: Output ONLY a valid JSON object strictly matching the provided StationAdvisoryResponse schema.
"""


# =====================================================================
# Pydantic Response Schemas
# =====================================================================

class HydrogeologicalAction(BaseModel):
    """Specific recommended watershed management or conservation action."""
    title: str = Field(description="Action title matching watershed conservation taxonomy")
    action_category: Literal["Recharge", "Demand_Management", "Monitoring", "Soil_Water_Conservation"] = Field(
        description="Category: Recharge, Demand_Management, Monitoring, or Soil_Water_Conservation"
    )
    description: str = Field(description="Detailed operational description of the intervention")
    hydrogeological_rationale: str = Field(
        description="Scientific rationale based on measured water depth and project-defined reference tier; must not infer unmeasured subsurface geology, aquifer storage, recharge potential, or extraction stress"
    )
    preconditions_and_feasibility: str = Field(
        description="Site-specific prerequisites, infiltration testing, and feasibility requirements"
    )
    priority: Literal["High", "Medium", "Low"] = Field(description="Priority: High, Medium, or Low")


class SupportingEvidence(BaseModel):
    """Verified empirical evidence and contextual indicators for the station."""
    observed_depth_mbgl: float = Field(description="Latest measured groundwater depth in metres below ground level")
    observation_date: str = Field(description="Date of latest historical observation (YYYY-MM-DD)")
    physical_depth_tier: str = Field(description="Physical reference depth tier: Shallow (<4m), Moderate (4-8m), or Deep (>8m)")
    historical_context: str = Field(description="Historical trend, sounding range, and previous observation comparison")
    rainfall_context: str = Field(description="Antecedent rainfall lookbacks and spatial extrapolation caveat if applicable")
    forecast_context: Optional[str] = Field(
        default=None,
        description="Statistical ML next-observation forecast and quantile uncertainty bounds, if available"
    )


class StationAdvisoryResponse(BaseModel):
    """Complete structured hydrogeological advisory response schema."""
    station_name: str = Field(description="Name of the CGWB monitoring station")
    advisory_summary: str = Field(description="Concise advisory summary (2-3 sentences)")
    observed_depth_mbgl: float = Field(description="Observed water table depth in m MBGL")
    physical_depth_tier: str = Field(description="Project-defined physical reference depth tier")
    supporting_evidence: SupportingEvidence = Field(description="Verified empirical evidence and contextual indicators")
    recommended_actions: List[HydrogeologicalAction] = Field(description="Specific, prioritized watershed conservation actions")
    explanation_of_relevance: str = Field(
        description="Explanation of why these actions are relevant to this specific station's observed water levels and project-defined tier"
    )
    limitations_and_uncertainty: List[str] = Field(
        description="Key scientific limitations, observation irregularities, and uncertainties"
    )
    field_verification_statement: str = Field(
        description="Mandatory disclaimer requiring on-site hydrogeological and infiltration feasibility surveys"
    )


# =====================================================================
# Configuration & Client Initialization
# =====================================================================

def get_gemini_api_key() -> Optional[str]:
    """Retrieve the Gemini API key securely from Streamlit Secrets or Environment Variables.

    Priority:
    1. Streamlit Secrets: `st.secrets["GEMINI_API_KEY"]`
    2. Environment Variable: `os.environ["GEMINI_API_KEY"]`

    Returns:
        The sanitized API key string if present and non-placeholder, else None.
        Never logs or prints the key.
    """
    key: Optional[str] = None
    try:
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    if not key or not str(key).strip():
        key = os.environ.get("GEMINI_API_KEY")

    if key:
        clean_key = str(key).strip()
        # Defensive check against template placeholders
        if clean_key and clean_key != "your-gemini-api-key-here":
            return clean_key

    return None


def is_gemini_configured() -> bool:
    """Return True if a valid Gemini API key is configured in secrets or environment."""
    return get_gemini_api_key() is not None


def get_configured_model_id() -> str:
    """Return the centralized Gemini model ID from secrets, environment, or default.

    Priority:
    1. Streamlit Secrets: `st.secrets["GEMINI_MODEL_ID"]`
    2. Environment Variable: `os.environ["GEMINI_MODEL_ID"]`
    3. DEFAULT_GEMINI_MODEL constant
    """
    model_id: Optional[str] = None
    try:
        import streamlit as st
        if "GEMINI_MODEL_ID" in st.secrets:
            model_id = st.secrets["GEMINI_MODEL_ID"]
    except Exception:
        pass

    if not model_id or not str(model_id).strip():
        model_id = os.environ.get("GEMINI_MODEL_ID")

    if model_id and str(model_id).strip():
        return str(model_id).strip()

    return DEFAULT_GEMINI_MODEL


def get_gemini_client():
    """Initialize and return the official Google Gen AI Client when credentials exist.

    Uses `google.genai.Client(api_key=...)`.
    Does NOT execute any API requests.

    Returns:
        genai.Client instance if key is available, else None.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return None

    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception:
        return None


# =====================================================================
# Telemetry Context Assembler
# =====================================================================

def build_station_telemetry_context(
    station_name: str,
    df: pd.DataFrame,
    models: Optional[dict] = None
) -> dict:
    """Assemble a structured, strictly verified telemetry and historical context for a station.

    Args:
        station_name: Name of the station to assemble context for.
        df: Processed groundwater DataFrame.
        models: Optional dictionary of loaded ML models (RF forecast, Q10, Q90, metadata).

    Returns:
        Dictionary containing verified telemetry, trend statistics, rainfall indicators,
        deterministic baseline tier, and ML predictions (when eligible).

    Raises:
        ValueError: If station_name is not present in df.
    """
    if df is None or df.empty or 'station' not in df.columns:
        raise ValueError("Invalid or empty dataset provided to context assembler.")

    sub = df[df['station'] == station_name].copy()
    if sub.empty:
        raise ValueError(f"Station '{station_name}' not found in groundwater dataset.")

    sub['date'] = pd.to_datetime(sub['date'])
    sub = sub.sort_values('date').reset_index(drop=True)
    total_records = len(sub)

    latest_row = sub.iloc[-1]
    latest_date_str = latest_row['date'].strftime('%Y-%m-%d')
    latest_depth = float(latest_row['gw_level_mbgl'])

    # Previous observation dynamics
    if total_records > 1:
        prev_row = sub.iloc[-2]
        prev_date_str = prev_row['date'].strftime('%Y-%m-%d')
        prev_depth = float(prev_row['gw_level_mbgl'])
        depth_change_m = round(latest_depth - prev_depth, 2)
        days_elapsed = int((latest_row['date'] - prev_row['date']).days)
    else:
        prev_date_str = None
        prev_depth = None
        depth_change_m = None
        days_elapsed = None

    # Historical trend & sounding distribution
    min_depth = round(float(sub['gw_level_mbgl'].min()), 2)
    max_depth = round(float(sub['gw_level_mbgl'].max()), 2)
    mean_depth = round(float(sub['gw_level_mbgl'].mean()), 2)
    median_depth = round(float(sub['gw_level_mbgl'].median()), 2)
    first_obs_date = sub['date'].min().strftime('%Y-%m-%d')

    # Rainfall indicators & spatial extrapolation caveat
    is_extrapolated = bool(latest_row.get('is_rainfall_extrapolated', station_name in EXTRAPOLATED_STATIONS))
    rain_indicators = {
        "rain_30d_mm": round(float(latest_row['rain_30d']), 1) if 'rain_30d' in latest_row and pd.notnull(latest_row['rain_30d']) else None,
        "rain_60d_mm": round(float(latest_row['rain_60d']), 1) if 'rain_60d' in latest_row and pd.notnull(latest_row['rain_60d']) else None,
        "rain_90d_mm": round(float(latest_row['rain_90d']), 1) if 'rain_90d' in latest_row and pd.notnull(latest_row['rain_90d']) else None,
        "rain_180d_mm": round(float(latest_row['rain_180d']), 1) if 'rain_180d' in latest_row and pd.notnull(latest_row['rain_180d']) else None,
        "rain_365d_mm": round(float(latest_row['rain_365d']), 1) if 'rain_365d' in latest_row and pd.notnull(latest_row['rain_365d']) else None,
        "is_rainfall_extrapolated": is_extrapolated,
        "extrapolation_caveat": (
            "Station is located in an extrapolated zone (>10 km from nearest IMD grid centroid); "
            "localized rainfall may deviate significantly from regional grid estimates."
            if is_extrapolated else
            "Rainfall interpolated from nearest IMD grid centroid within 10 km."
        )
    }

    # Deterministic physical depth tier & heuristic plan
    tier_category = get_depth_tier_category(latest_depth)
    tier_label, _, _ = get_depth_tier(latest_depth)
    deterministic_plan = get_intervention_plan(latest_depth)

    # Machine Learning Next-Observation Forecast (only for stations with >= 10 records)
    ml_forecast: Dict[str, Any]
    if total_records >= 10 and models is not None and 'forecast' in models:
        try:
            from services.model_service import predict_next_observation
            pred_res = predict_next_observation(models, latest_row, rain_factor=0.0)
            pred_val = round(pred_res["pred_val"], 2)
            pred_q10 = round(pred_res["pred_q10"], 2)
            pred_q90 = round(pred_res["pred_q90"], 2)
            
            # Direction of change
            if pred_val < latest_depth - 0.2:
                direction = "Shallower (Projected Recharge)"
            elif pred_val > latest_depth + 0.2:
                direction = "Deeper (Projected Depletion)"
            else:
                direction = "Approximately Stable"

            ml_forecast = {
                "is_available": True,
                "data_type": "statistical_machine_learning_forecast",
                "model_description": "Random Forest Regressor (point estimate) + Gradient Boosting (q10–q90 interval)",
                "predicted_next_depth_mbgl": pred_val,
                "uncertainty_interval_q10_mbgl": pred_q10,
                "uncertainty_interval_q90_mbgl": pred_q90,
                "lower_bound_mbgl": round(pred_res["lower_b"], 2),
                "upper_bound_mbgl": round(pred_res["upper_b"], 2),
                "predicted_direction": direction,
                "forecast_nature_note": (
                    "Event-based forecast for the next irregular historical survey sounding. "
                    "Not a continuous sensor feed or calendar schedule."
                )
            }
        except Exception as e:
            ml_forecast = {
                "is_available": False,
                "reason": f"Prediction generation error: {str(e)}"
            }
    else:
        reason_msg = (
            f"Insufficient historical records ({total_records} < 10 soundings) to generate reliable statistical forecast."
            if total_records < 10 else "Forecasting model artifacts not provided."
        )
        ml_forecast = {
            "is_available": False,
            "reason": reason_msg
        }

    return {
        "station_name": station_name,
        "telemetry": {
            "data_type": "measured_historical_observation",
            "observed_depth_mbgl": round(latest_depth, 2),
            "observation_date": latest_date_str,
            "previous_observation_date": prev_date_str,
            "previous_depth_mbgl": round(prev_depth, 2) if prev_depth is not None else None,
            "depth_change_m": depth_change_m,
            "days_elapsed": days_elapsed,
            "total_station_records": total_records,
        },
        "historical_stats": {
            "data_type": "historical_station_statistics",
            "first_observation_date": first_obs_date,
            "min_depth_mbgl": min_depth,
            "max_depth_mbgl": max_depth,
            "mean_depth_mbgl": mean_depth,
            "median_depth_mbgl": median_depth,
        },
        "rainfall_indicators": rain_indicators,
        "deterministic_tier": {
            "data_type": "project_defined_heuristic_reference_tier",
            "category": tier_category,
            "tier_label": tier_label,
            "priority": deterministic_plan.get("priority"),
            "heuristic_actions": deterministic_plan.get("actions", []),
            "attribution_note": (
                "Project-defined physical reference tier and preliminary heuristic options; "
                "not official CGWB or GSDA government directives."
            ),
        },
        "ml_forecast": ml_forecast,
    }


# =====================================================================
# Canonical Station Cache Key Generator
# =====================================================================

def compute_station_cache_key(
    station_name: str,
    df: pd.DataFrame,
    models: Optional[dict] = None,
    model_id: Optional[str] = None,
    version: str = PROMPT_SCHEMA_VERSION,
) -> str:
    """Compute a deterministic SHA-256 cache key derived from the complete canonical
    station context payload supplied to Gemini, configured model ID, and prompt/schema version.

    Ensures that changes to any supplied telemetry, rainfall indicator, historical context,
    forecast parameter, configured model ID, or prompt/schema version invalidate the cached response.

    Args:
        station_name: Name of the monitoring station.
        df: Groundwater DataFrame.
        models: Optional dictionary of loaded ML models.
        model_id: Optional override model ID.
        version: Prompt and schema version string.

    Returns:
        Deterministic cache key string formatted as `<station_name>:<model_id>:<sha256_hash>`.
    """
    effective_model = (model_id or get_configured_model_id() or DEFAULT_GEMINI_MODEL).strip()
    try:
        context_payload = build_station_telemetry_context(station_name, df, models=models)
    except Exception:
        return f"{station_name}:{effective_model}:empty:{version}"

    # Canonical sorted JSON representation of the complete context dictionary supplied to Gemini
    canonical_repr = json.dumps(context_payload, sort_keys=True, default=str)
    raw_hash_input = f"{version}|{effective_model}|{canonical_repr}"
    digest = hashlib.sha256(raw_hash_input.encode("utf-8")).hexdigest()
    return f"{station_name}:{effective_model}:{digest}"


# =====================================================================
# Deterministic Fallback Advisory Generator
# =====================================================================

def get_fallback_advisory(
    station_name: str,
    df: pd.DataFrame,
    reason: str,
    models: Optional[dict] = None
) -> Dict[str, Any]:
    """Generate a fully populated deterministic fallback advisory conforming to the JSON schema.

    Uses project-defined heuristic options from `services.data_loader` when Gemini API
    is unconfigured, unreachable, or returns an error. These are preliminary screening options,
    not official CGWB or GSDA government directives.

    Args:
        station_name: CGWB station name.
        df: Processed groundwater DataFrame.
        reason: Explanation of why the fallback was triggered.
        models: Optional ML models dictionary.

    Returns:
        Dictionary strictly adhering to the StationAdvisoryResponse schema, flagged with
        `is_fallback=True` and `fallback_reason`.
    """
    # Safe telemetry extraction
    latest_depth: float = 0.0
    latest_date_str: str = "Unknown"
    is_extrapolated: bool = station_name in EXTRAPOLATED_STATIONS
    hist_ctx = "Historical records unavailable."
    rain_ctx = "Rainfall data unavailable."
    fc_ctx = None

    try:
        ctx = build_station_telemetry_context(station_name, df, models=models)
        t = ctx["telemetry"]
        latest_depth = t["observed_depth_mbgl"]
        latest_date_str = t["observation_date"]
        s = ctx["historical_stats"]
        r = ctx["rainfall_indicators"]
        is_extrapolated = r["is_rainfall_extrapolated"]

        hist_ctx = (
            f"Station {station_name} has {t['total_station_records']} historical observations "
            f"spanning {s['first_observation_date']} to {t['observation_date']}. Observed range: "
            f"{s['min_depth_mbgl']:.2f} m to {s['max_depth_mbgl']:.2f} m MBGL (mean {s['mean_depth_mbgl']:.2f} m). "
        )
        if t["previous_depth_mbgl"] is not None:
            direction_word = "fell" if (t["depth_change_m"] or 0) > 0 else "rose"
            hist_ctx += (
                f"Most recent sounding changed by {abs(t['depth_change_m']):.2f} m ({direction_word}) "
                f"over {t['days_elapsed']} days compared to {t['previous_observation_date']}."
            )

        rain_parts = []
        if r["rain_90d_mm"] is not None:
            rain_parts.append(f"90-day rainfall: {r['rain_90d_mm']} mm")
        if r["rain_365d_mm"] is not None:
            rain_parts.append(f"365-day rainfall: {r['rain_365d_mm']} mm")
        rain_ctx = ", ".join(rain_parts) if rain_parts else "Antecedent rainfall not recorded."
        if is_extrapolated:
            rain_ctx += " (Extrapolated IMD grid; >10 km from centroid)."

        if ctx["ml_forecast"].get("is_available"):
            fc = ctx["ml_forecast"]
            fc_ctx = (
                f"Random Forest statistical next-observation forecast predicts {fc['predicted_next_depth_mbgl']} m MBGL "
                f"({fc['predicted_direction']}), with a 10th–90th percentile quantile range of "
                f"{fc['uncertainty_interval_q10_mbgl']} m to {fc['uncertainty_interval_q90_mbgl']} m MBGL."
            )
        else:
            fc_ctx = ctx["ml_forecast"].get("reason", "Forecast unavailable.")
    except Exception:
        # Extreme fallback if dataframe lookup fails
        pass

    tier_cat = get_depth_tier_category(latest_depth)
    tier_label, _, _ = get_depth_tier(latest_depth)
    plan = get_intervention_plan(latest_depth)

    # Convert deterministic heuristic tuples into structured HydrogeologicalAction objects
    actions: List[Dict[str, Any]] = []
    raw_actions = plan.get("actions", [])

    for title, desc in raw_actions:
        title_lower = title.lower()
        if "recharge" in title_lower or "percolation" in title_lower or "rooftop" in title_lower:
            cat = "Recharge"
        elif "extraction" in title_lower or "crop" in title_lower or "irrigation" in title_lower or "budgeting" in title_lower:
            cat = "Demand_Management"
        elif "bunding" in title_lower or "trench" in title_lower or "storage" in title_lower or "shet-tale" in title_lower:
            cat = "Soil_Water_Conservation"
        else:
            cat = "Monitoring"

        if tier_cat == "Deep":
            prio = "High"
            rationale = (
                f"Observed groundwater level ({latest_depth:.2f} m MBGL) falls within the project-defined Deep reference tier (> 8.0 m MBGL). "
                "Water table depth alone cannot establish aquifer storage, recharge potential, extraction stress, or groundwater availability."
            )
        elif tier_cat == "Moderate":
            prio = "Medium"
            rationale = (
                f"Observed groundwater level ({latest_depth:.2f} m MBGL) falls within the project-defined Moderate reference tier (4.0–8.0 m MBGL). "
                "Water table depth alone cannot establish aquifer storage, recharge potential, extraction stress, or groundwater availability."
            )
        elif tier_cat == "Shallow":
            prio = "Low"
            rationale = (
                f"Observed groundwater level ({latest_depth:.2f} m MBGL) falls within the project-defined Shallow reference tier (< 4.0 m MBGL). "
                "Water table depth alone cannot establish aquifer storage, recharge potential, extraction stress, or groundwater availability."
            )
        else:
            prio = "High"
            rationale = (
                "Observation depth is unrecorded, missing, or invalid. In-situ physical measurement "
                "is required before water table depth or reference tier can be determined."
            )

        actions.append({
            "title": title,
            "action_category": cat,
            "description": desc,
            "hydrogeological_rationale": rationale,
            "preconditions_and_feasibility": "Site-specific geological, hydrogeological, and infiltration feasibility survey required.",
            "priority": prio,
        })

    advisory_summary = (
        f"Project-defined heuristic baseline advisory for {station_name}. "
        f"Observed groundwater level is {latest_depth:.2f} m MBGL, categorized within the "
        f"{tier_label} project-defined physical reference tier. Recommended actions provide "
        f"preliminary planning options for local water stewardship."
    )

    relevance = (
        f"Recommendations reflect project-defined conservation heuristics mapped to the {tier_label} "
        f"physical reference tier. These options provide a structured preliminary planning framework for "
        f"surface water management and local monitoring; they do not establish aquifer storage or recharge potential, "
        f"nor do they represent official CGWB or GSDA administrative directives or engineering designs."
    )

    return {
        "is_fallback": True,
        "fallback_reason": reason,
        "model_id": "project-heuristic-baseline",
        "station_name": station_name,
        "advisory_summary": advisory_summary,
        "observed_depth_mbgl": latest_depth,
        "physical_depth_tier": tier_label,
        "supporting_evidence": {
            "observed_depth_mbgl": latest_depth,
            "observation_date": latest_date_str,
            "physical_depth_tier": tier_label,
            "historical_context": hist_ctx,
            "rainfall_context": rain_ctx,
            "forecast_context": fc_ctx,
        },
        "recommended_actions": actions,
        "explanation_of_relevance": relevance,
        "limitations_and_uncertainty": DEFAULT_LIMITATIONS,
        "field_verification_statement": MANDATORY_FIELD_VERIFICATION_STATEMENT,
    }


# =====================================================================
# Main Advisory Generator
# =====================================================================

def generate_station_advisory(
    station_name: str,
    df: pd.DataFrame,
    models: Optional[dict] = None,
    client: Optional[Any] = None,
    model_id: Optional[str] = None
) -> Dict[str, Any]:
    """Generate a Gemini-powered hydrogeological advisory with strict fallback guarantees.

    Args:
        station_name: Name of the monitoring station.
        df: Processed groundwater DataFrame.
        models: Optional dictionary of ML models and evaluation metadata.
        client: Optional pre-configured google.genai.Client (used for mocking in tests).
        model_id: Optional override model string.

    Returns:
        Structured dictionary matching StationAdvisoryResponse plus `is_fallback` and `fallback_reason`.
    """
    # 1. Verify API Key availability
    api_key = get_gemini_api_key()
    if not api_key and client is None:
        return get_fallback_advisory(
            station_name=station_name,
            df=df,
            reason="Gemini API key is not configured in Streamlit Secrets or environment variables.",
            models=models
        )

    # 2. Resolve client and model ID
    effective_model_id = (model_id or get_configured_model_id() or DEFAULT_GEMINI_MODEL).strip()
    if not effective_model_id:
        return get_fallback_advisory(
            station_name=station_name,
            df=df,
            reason="Gemini model ID is not configured.",
            models=models
        )

    active_client = client or get_gemini_client()
    if active_client is None:
        return get_fallback_advisory(
            station_name=station_name,
            df=df,
            reason="Failed to initialize Google Gen AI Client.",
            models=models
        )

    # 3. Assemble verified telemetry context
    try:
        context = build_station_telemetry_context(station_name, df, models=models)
    except Exception as e:
        return get_fallback_advisory(
            station_name=station_name,
            df=df,
            reason=f"Failed to assemble station telemetry context: {str(e)}",
            models=models
        )

    # 4. Construct grounded user prompt
    user_prompt = f"""Generate a station-specific groundwater decision-support advisory for CGWB Station '{station_name}' in Purandar Taluka, Maharashtra.

STATION TELEMETRY CONTEXT (VERIFIED EMPIRICAL DATA ONLY):
{json.dumps(context, indent=2)}

INSTRUCTIONS:
- You MUST anchor all observations, depths, dates, and predictions strictly to the telemetry context above.
- Never state or imply that predictions are live sensor measurements.
- Never state specific volumetric yield increases (e.g. no 'will add 5,000 liters').
- Do not assert unverified geological characteristics or causal claims: groundwater depth alone cannot establish aquifer storage, recharge potential, extraction stress, or groundwater availability.
- Clearly distinguish project-defined heuristic rules from official CGWB or GSDA government classifications.
- Recommend between 2 and 4 targeted watershed and demand-management actions.
- Formulate each action with title, category, description, hydrogeological rationale, feasibility preconditions, and priority.
- Explicitly include the requirement for localized on-site hydrogeological and infiltration feasibility surveys prior to any physical construction.
- Adhere strictly to the requested JSON response schema.
"""

    # 5. Execute API request with structured JSON schema
    try:
        from google.genai import types

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=StationAdvisoryResponse,
            temperature=0.2,
        )

        response = active_client.models.generate_content(
            model=effective_model_id,
            contents=user_prompt,
            config=config,
        )

        if not response or not getattr(response, "text", None):
            return get_fallback_advisory(
                station_name=station_name,
                df=df,
                reason="Gemini API returned an empty or null response.",
                models=models
            )

        # 6. Parse and validate against Pydantic schema
        validated_advisory = StationAdvisoryResponse.model_validate_json(response.text)
        result = validated_advisory.model_dump()

        # 7. Scientific integrity safeguards (enforce zero hallucination on anchor telemetry)
        telemetry = context["telemetry"]
        result["is_fallback"] = False
        result["fallback_reason"] = None
        result["model_id"] = effective_model_id

        # Re-anchor critical empirical metrics to prevent any LLM hallucination drift
        result["station_name"] = station_name
        result["observed_depth_mbgl"] = telemetry["observed_depth_mbgl"]
        result["physical_depth_tier"] = context["deterministic_tier"]["tier_label"]
        result["field_verification_statement"] = MANDATORY_FIELD_VERIFICATION_STATEMENT

        return result

    except Exception as err:
        safe_reason = str(err)
        # Redact API key if present in error message
        if api_key and api_key in safe_reason:
            safe_reason = safe_reason.replace(api_key, "[REDACTED_API_KEY]")

        return get_fallback_advisory(
            station_name=station_name,
            df=df,
            reason=f"Gemini API generation error: {safe_reason}",
            models=models
        )
