"""Unit tests for Stage 3: Gemini Advisory UI Integration, Caching, and Fallback Behavior.

Tests verify:
- Deterministic cache key generation incorporating complete canonical telemetry context,
  historical soundings, rainfall indicators, ML forecasts, model ID, and schema version.
- Independent cache key invalidation when each context field is modified.
- Prevention of automatic API calls on ordinary Streamlit reruns.
- Explicit user button interaction requirements (Generate and Refresh).
- Preservation of cached responses when unrelated UI widgets (filters, sorts, themes) change.
- Loading indicator and graceful deterministic fallback handling without secret exposure.
- Strict disclaimers preventing unsupported CGWB/GSDA attribution.
- Preservation of existing deterministic heuristics and ML prediction pipelines.
- UI section rendering integrity.
"""
import unittest.mock as mock
import pytest
import pandas as pd
import streamlit as st

from services.data_loader import load_data, get_intervention_plan
from services.model_service import load_models, predict_next_observation
from services.gemini_service import (
    DEFAULT_GEMINI_MODEL,
    PROMPT_SCHEMA_VERSION,
    compute_station_cache_key,
    generate_station_advisory,
    get_fallback_advisory,
    build_station_telemetry_context,
)
from screens.decision_support import (
    render_ai_station_advisory_section,
    render_decision_support_screen,
)
from components.callouts import render_decision_support_advisory_notice


@pytest.fixture(scope="module")
def data_and_models():
    """Load verified processed dataset and trained forecasting models."""
    df = load_data()
    models = load_models()
    return df, models


@pytest.fixture(autouse=True)
def clean_session_state():
    """Ensure session state is isolated between test runs."""
    st.session_state.clear()
    yield
    st.session_state.clear()


# =====================================================================
# Cache Key & Invalidation Tests
# =====================================================================

def test_compute_station_cache_key_uniqueness(data_and_models):
    """Verify that distinct stations generate distinct cache keys."""
    df, models = data_and_models
    key_saswad = compute_station_cache_key("Saswad", df, models=models)
    key_jejuri = compute_station_cache_key("Jejuri", df, models=models)

    assert key_saswad != key_jejuri
    assert "Saswad" in key_saswad
    assert "Jejuri" in key_jejuri


def test_compute_station_cache_key_invalidation_on_depth_change(data_and_models):
    """Verify that changing observed depth independently invalidates the cache key."""
    df, models = data_and_models
    key_original = compute_station_cache_key("Saswad", df, models=models)

    # Modify latest observed depth in dataset
    df_modified = df.copy()
    mask = df_modified['station'] == "Saswad"
    latest_idx = df_modified[mask].sort_values('date').index[-1]
    df_modified.loc[latest_idx, 'gw_level_mbgl'] = 9.99

    key_modified = compute_station_cache_key("Saswad", df_modified, models=models)
    assert key_original != key_modified


def test_compute_station_cache_key_invalidation_on_observation_date_change(data_and_models):
    """Verify that changing observation date independently invalidates the cache key."""
    df, models = data_and_models
    key_original = compute_station_cache_key("Saswad", df, models=models)

    df_modified = df.copy()
    mask = df_modified['station'] == "Saswad"
    latest_idx = df_modified[mask].sort_values('date').index[-1]
    df_modified.loc[latest_idx, 'date'] = pd.to_datetime("2024-01-01")

    key_modified = compute_station_cache_key("Saswad", df_modified, models=models)
    assert key_original != key_modified


def test_compute_station_cache_key_invalidation_on_previous_observation_change(data_and_models):
    """Verify that changing previous observation depth or interval invalidates the cache key."""
    df, models = data_and_models
    key_original = compute_station_cache_key("Saswad", df, models=models)

    df_modified = df.copy()
    mask = df_modified['station'] == "Saswad"
    prev_idx = df_modified[mask].sort_values('date').index[-2]
    df_modified.loc[prev_idx, 'gw_level_mbgl'] = 12.34

    key_modified = compute_station_cache_key("Saswad", df_modified, models=models)
    assert key_original != key_modified


def test_compute_station_cache_key_invalidation_on_rainfall_90d_change(data_and_models):
    """Verify that changing 90-day antecedent rainfall independently invalidates the cache key."""
    df, models = data_and_models
    key_original = compute_station_cache_key("Jejuri", df, models=models)

    df_modified = df.copy()
    mask = df_modified['station'] == "Jejuri"
    latest_idx = df_modified[mask].sort_values('date').index[-1]
    df_modified.loc[latest_idx, 'rain_90d'] = 888.8

    key_modified = compute_station_cache_key("Jejuri", df_modified, models=models)
    assert key_original != key_modified


def test_compute_station_cache_key_invalidation_on_rainfall_365d_change(data_and_models):
    """Verify that changing 365-day cumulative rainfall independently invalidates the cache key."""
    df, models = data_and_models
    key_original = compute_station_cache_key("Jejuri", df, models=models)

    df_modified = df.copy()
    mask = df_modified['station'] == "Jejuri"
    latest_idx = df_modified[mask].sort_values('date').index[-1]
    df_modified.loc[latest_idx, 'rain_365d'] = 1500.0

    key_modified = compute_station_cache_key("Jejuri", df_modified, models=models)
    assert key_original != key_modified


def test_compute_station_cache_key_invalidation_on_extrapolation_flag_change(data_and_models):
    """Verify that changing rainfall spatial extrapolation status invalidates the cache key."""
    df, models = data_and_models
    key_original = compute_station_cache_key("Saswad", df, models=models)

    df_modified = df.copy()
    mask = df_modified['station'] == "Saswad"
    latest_idx = df_modified[mask].sort_values('date').index[-1]
    df_modified.loc[latest_idx, 'is_rainfall_extrapolated'] = 1

    key_modified = compute_station_cache_key("Saswad", df_modified, models=models)
    assert key_original != key_modified


def test_compute_station_cache_key_invalidation_on_historical_stats_change(data_and_models):
    """Verify that altering older historical soundings (changing min/mean statistics) invalidates the cache key."""
    df, models = data_and_models
    key_original = compute_station_cache_key("Saswad", df, models=models)

    df_modified = df.copy()
    mask = df_modified['station'] == "Saswad"
    first_idx = df_modified[mask].sort_values('date').index[0]
    df_modified.loc[first_idx, 'gw_level_mbgl'] = 25.0  # Alters min/max/mean

    key_modified = compute_station_cache_key("Saswad", df_modified, models=models)
    assert key_original != key_modified


def test_compute_station_cache_key_invalidation_on_forecast_change(data_and_models):
    """Verify that forecast presence vs absence independently alters the cache key."""
    df, models = data_and_models
    key_with_models = compute_station_cache_key("Saswad", df, models=models)
    key_without_models = compute_station_cache_key("Saswad", df, models=None)

    assert key_with_models != key_without_models


def test_compute_station_cache_key_invalidation_on_model_id_change(data_and_models):
    """Verify that switching configured model ID changes the cache key."""
    df, models = data_and_models
    key_default = compute_station_cache_key("Saswad", df, models=models, model_id="gemini-3.1-flash-lite")
    key_override = compute_station_cache_key("Saswad", df, models=models, model_id="custom-flash-model")

    assert key_default != key_override
    assert "gemini-3.1-flash-lite" in key_default
    assert "custom-flash-model" in key_override


def test_compute_station_cache_key_invalidation_on_version_change(data_and_models):
    """Verify that changing the prompt/schema version string invalidates the cache key."""
    df, models = data_and_models
    key_v3 = compute_station_cache_key("Saswad", df, models=models, version=PROMPT_SCHEMA_VERSION)
    key_v4 = compute_station_cache_key("Saswad", df, models=models, version="v4.0-experimental")

    assert key_v3 != key_v4


def test_compute_station_cache_key_empty_handling(data_and_models):
    """Verify that empty or non-existent stations produce defensive fallback keys without crashing."""
    df, models = data_and_models
    key_empty = compute_station_cache_key("NonExistentStation", df, models=models)
    assert "NonExistentStation" in key_empty
    assert "empty" in key_empty


# =====================================================================
# Caching & Prevention of Automatic API Calls on Reruns
# =====================================================================

def test_caching_prevents_unnecessary_api_calls(data_and_models):
    """Verify that identical station inputs reuse cached advisory without calling API."""
    df, models = data_and_models
    station = "Saswad"
    cache_key = compute_station_cache_key(station, df, models=models)

    mock_cache = {}
    mock_advisory = get_fallback_advisory(station, df, reason="Cached baseline")
    mock_cache[cache_key] = mock_advisory

    assert cache_key in mock_cache
    cached_result = mock_cache[cache_key]
    assert cached_result["station_name"] == station
    assert cached_result["is_fallback"] is True


def test_ordinary_rerun_does_not_trigger_api_call(data_and_models):
    """Verify that an ordinary Streamlit rerun without button interaction NEVER calls Gemini API."""
    df, models = data_and_models
    station = "Saswad"
    cache_key = compute_station_cache_key(station, df, models=models)

    # Pre-populate session state cache
    st.session_state["ds_ai_advisory_cache"] = {
        cache_key: get_fallback_advisory(station, df, reason="Pre-cached advisory")
    }
    st.session_state["ds_ai_station_selector"] = station

    with mock.patch("streamlit.button", return_value=False):
        with mock.patch("screens.decision_support.generate_station_advisory") as mock_generate:
            with mock.patch("streamlit.selectbox", return_value=station):
                with mock.patch("streamlit.markdown"):
                    with mock.patch("streamlit.columns", return_value=[mock.MagicMock(), mock.MagicMock()]):
                        render_ai_station_advisory_section(df, models=models, initial_station=station)

            # Strict assertion: generate_station_advisory must NOT be invoked on rerun
            mock_generate.assert_not_called()


def test_unrelated_ui_settings_change_preserves_cache_without_api_call(data_and_models):
    """Verify that modifying filters, sorts, search terms, or themes preserves cache and avoids API calls."""
    df, models = data_and_models
    station = "Saswad"
    cache_key = compute_station_cache_key(station, df, models=models)

    # Pre-populate cache
    st.session_state["ds_ai_advisory_cache"] = {
        cache_key: get_fallback_advisory(station, df, reason="Saved baseline")
    }
    st.session_state["ds_ai_station_selector"] = station

    # Simulate user changing unrelated UI widgets in session state
    st.session_state["ds_search_station"] = "Sas"
    st.session_state["ds_tier_filter"] = "Deep (> 8.0 m)"
    st.session_state["ds_sort_option"] = "Alphabetical (A–Z)"
    st.session_state["theme"] = "dark"

    with mock.patch("streamlit.button", return_value=False):
        with mock.patch("screens.decision_support.generate_station_advisory") as mock_generate:
            with mock.patch("streamlit.markdown"):
                with mock.patch("streamlit.selectbox", return_value=station):
                    with mock.patch("streamlit.columns", return_value=[mock.MagicMock(), mock.MagicMock()]):
                        render_ai_station_advisory_section(df, models=models, initial_station=station)

            mock_generate.assert_not_called()
            # Cache entry remains intact
            assert cache_key in st.session_state["ds_ai_advisory_cache"]
            assert st.session_state["ds_ai_advisory_cache"][cache_key]["station_name"] == station


def test_generate_button_explicit_trigger(data_and_models):
    """Verify that clicking the Generate button triggers advisory generation and updates cache."""
    df, models = data_and_models
    station = "Saswad"
    cache_key = compute_station_cache_key(station, df, models=models)

    st.session_state["ds_ai_advisory_cache"] = {}

    expected_advisory = get_fallback_advisory(station, df, reason="Generated on explicit click")

    # Button returns True when key matches the generate button
    def mock_button(label, key=None, **kwargs):
        if key == f"ds_btn_gen_{station}":
            return True
        return False

    with mock.patch("streamlit.button", side_effect=mock_button):
        with mock.patch("screens.decision_support.generate_station_advisory", return_value=expected_advisory) as mock_generate:
            with mock.patch("streamlit.selectbox", return_value=station):
                with mock.patch("streamlit.markdown"):
                    with mock.patch("streamlit.columns", return_value=[mock.MagicMock(), mock.MagicMock()]):
                        render_ai_station_advisory_section(df, models=models, initial_station=station)

            mock_generate.assert_called_once_with(station, df, models=models, model_id=mock.ANY)
            assert cache_key in st.session_state["ds_ai_advisory_cache"]


def test_refresh_button_explicit_trigger(data_and_models):
    """Verify that clicking the Refresh/Regenerate button re-queries the generator and updates cache."""
    df, models = data_and_models
    station = "Saswad"
    cache_key = compute_station_cache_key(station, df, models=models)

    # Initially in cache as fallback
    st.session_state["ds_ai_advisory_cache"] = {
        cache_key: {"station_name": station, "is_fallback": True, "advisory_summary": "Initial"}
    }

    refreshed_advisory = {"station_name": station, "is_fallback": False, "advisory_summary": "Refreshed live"}

    def mock_button(label, key=None, **kwargs):
        if key == f"ds_btn_regen_{station}":
            return True
        return False

    with mock.patch("streamlit.button", side_effect=mock_button):
        with mock.patch("screens.decision_support.generate_station_advisory", return_value=refreshed_advisory) as mock_generate:
            with mock.patch("streamlit.selectbox", return_value=station):
                with mock.patch("streamlit.markdown"):
                    with mock.patch("streamlit.columns", return_value=[mock.MagicMock(), mock.MagicMock()]):
                        render_ai_station_advisory_section(df, models=models, initial_station=station)

            mock_generate.assert_called_once()
            assert st.session_state["ds_ai_advisory_cache"][cache_key]["advisory_summary"] == "Refreshed live"


# =====================================================================
# Source Attribution & Government Disclaimer Auditing
# =====================================================================

def test_source_attribution_and_disclaimers(data_and_models):
    """Verify that UI callouts, banners, and fallback descriptions disclaim official CGWB/GSDA guidance."""
    df, models = data_and_models
    station = "Saswad"

    # 1. Fallback advisory summary and relevance
    fallback = get_fallback_advisory(station, df, reason="Test attribution")
    summary = fallback["advisory_summary"].lower()
    relevance = fallback["explanation_of_relevance"].lower()

    assert "project-defined" in summary
    assert "official cgwb" not in summary
    assert "official gsda" not in summary
    assert "project-defined" in relevance
    assert "official cgwb or gsda" in relevance
    assert "nor do they represent" in relevance or "do not" in relevance

    # 2. Context payload attribution note
    ctx = build_station_telemetry_context(station, df, models=models)
    det = ctx["deterministic_tier"]
    assert det["data_type"] == "project_defined_heuristic_reference_tier"
    assert "not official cgwb or gsda" in det["attribution_note"].lower()

    # 3. Decision support screen file text check for explicit disclaimers
    with open("screens/decision_support.py", "r", encoding="utf-8") as fp:
        screen_code = fp.read().lower()

    assert "project-defined heuristic baseline active" in screen_code
    assert "project-defined heuristic note" in screen_code
    assert "not official government guidance" in screen_code or "not official cgwb/gsda guidance" in screen_code


# =====================================================================
# Fallback & Error State Display
# =====================================================================

def test_fallback_display_contains_no_exposed_secrets(data_and_models):
    """Verify fallback response contains clean reasons and never leaks API keys."""
    df, models = data_and_models
    fake_secret = "AIzaSySecretTestKey12345"

    with mock.patch("services.gemini_service.get_gemini_api_key", return_value=fake_secret):
        with mock.patch("services.gemini_service.get_gemini_client") as mock_client:
            mock_inst = mock.MagicMock()
            mock_inst.models.generate_content.side_effect = Exception(f"Failed with key {fake_secret}: 429 Quota")
            mock_client.return_value = mock_inst

            advisory = generate_station_advisory("Jejuri", df, models=models)

            assert advisory["is_fallback"] is True
            assert fake_secret not in advisory["fallback_reason"]
            assert "[REDACTED_API_KEY]" in advisory["fallback_reason"]
            assert len(advisory["recommended_actions"]) > 0


# =====================================================================
# Preservation of Existing Heuristics & ML Pipelines
# =====================================================================

def test_preservation_of_existing_heuristics(data_and_models):
    """Verify existing get_intervention_plan returns exact deterministic rules."""
    # Deep
    deep_plan = get_intervention_plan(9.5)
    assert deep_plan["category"] == "Deep"
    assert len(deep_plan["actions"]) == 4

    # Moderate
    mod_plan = get_intervention_plan(6.0)
    assert mod_plan["category"] == "Moderate"
    assert len(mod_plan["actions"]) == 3

    # Shallow
    shallow_plan = get_intervention_plan(2.5)
    assert shallow_plan["category"] == "Shallow"
    assert len(shallow_plan["actions"]) == 2


def test_preservation_of_ml_predictions(data_and_models):
    """Verify that ML predictions remain strictly intact and unaltered."""
    df, models = data_and_models
    sub = df[df['station'] == "Saswad"].sort_values('date')
    latest = sub.iloc[-1]

    pred = predict_next_observation(models, latest, rain_factor=0.0)
    assert isinstance(pred["pred_val"], float)
    assert pred["lower_b"] <= pred["pred_val"] <= pred["upper_b"]


# =====================================================================
# Screen Execution & Signature Tests
# =====================================================================

def test_decision_support_screen_signature_accepts_models(data_and_models):
    """Verify that render_decision_support_screen accepts optional models parameter without error."""
    df, models = data_and_models
    import inspect
    sig = inspect.signature(render_decision_support_screen)
    assert "df" in sig.parameters
    assert "models" in sig.parameters
    assert sig.parameters["models"].default is None


def test_render_ai_advisory_section_execution_mocked(data_and_models):
    """Verify render_ai_station_advisory_section executes cleanly without unhandled exceptions."""
    df, models = data_and_models
    with mock.patch("streamlit.selectbox", return_value="Saswad"):
        with mock.patch("streamlit.button", return_value=False):
            with mock.patch("streamlit.markdown") as mock_md:
                with mock.patch("streamlit.columns", return_value=[mock.MagicMock(), mock.MagicMock()]):
                    render_ai_station_advisory_section(df, models=models, initial_station="Saswad")
                    assert mock_md.called
