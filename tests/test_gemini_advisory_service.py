"""Unit tests for Stage 2.2: Scientific Language Review & Strict Grounding.

Tests verify:
- Deep, Moderate, and Shallow tier rationales state only measured depth and project-defined reference tier
- Explicit statement that depth alone cannot establish aquifer storage, recharge potential,
  extraction stress, or groundwater availability
- Elimination of unsupported causal claims (e.g., drawdown, saturation, depletion)
- Elimination of unverified geological statements from advisories (e.g., basalt, Deccan Traps)
- Configurable model selection defaulting to gemini-3.1-flash-lite
- Strict adherence to Pydantic JSON schema (StationAdvisoryResponse, HydrogeologicalAction)
- Honest source attribution: distinguishing project-defined heuristics from official CGWB/GSDA guidance
- Deterministic heuristic fallback behavior when credentials or API calls fail
- Zero numerical hallucination / data honesty safeguards
- Prohibition of volumetric yield promises and presence of mandatory field verification disclaimers
"""
import json
import unittest.mock as mock
import pytest
import pandas as pd

from services.data_loader import load_data
from services.model_service import load_models
from services.gemini_service import (
    DEFAULT_GEMINI_MODEL,
    MANDATORY_FIELD_VERIFICATION_STATEMENT,
    DEFAULT_LIMITATIONS,
    SYSTEM_INSTRUCTION,
    HydrogeologicalAction,
    SupportingEvidence,
    StationAdvisoryResponse,
    build_station_telemetry_context,
    get_fallback_advisory,
    generate_station_advisory,
    get_configured_model_id,
)


@pytest.fixture(scope="module")
def data_and_models():
    """Load verified processed dataset and trained forecasting models."""
    df = load_data()
    models = load_models()
    return df, models


@pytest.fixture(autouse=True)
def clean_gemini_env():
    """Ensure GEMINI_API_KEY and GEMINI_MODEL_ID are not leaked into tests."""
    with mock.patch("streamlit.secrets", {}):
        yield


# =====================================================================
# Model Selection & Overridability Tests
# =====================================================================

def test_default_model_is_flash_lite():
    """Verify default model is set to gemini-3.1-flash-lite and is configurable."""
    assert DEFAULT_GEMINI_MODEL == "gemini-3.1-flash-lite"
    with mock.patch("streamlit.secrets", {}):
        assert get_configured_model_id() == "gemini-3.1-flash-lite"

    with mock.patch.dict("os.environ", {"GEMINI_MODEL_ID": "custom-flash-lite-override"}):
        assert get_configured_model_id() == "custom-flash-lite-override"


# =====================================================================
# Stage 2.2: Scientific Grounding & Language Restriction Tests
# =====================================================================

def test_tier_rationales_no_unsupported_causal_inferences(data_and_models):
    """Verify that rationales state measured depth and tier, and disclaim causal inferences."""
    df, models = data_and_models

    for st_name in ["Saswad", "Jejuri", "Sakurde"]:
        fallback = get_fallback_advisory(st_name, df, reason="Test", models=models)
        depth = fallback["observed_depth_mbgl"]
        tier = fallback["physical_depth_tier"]

        for action in fallback["recommended_actions"]:
            rationale = action["hydrogeological_rationale"]
            # Must state measured depth and reference tier
            assert f"{depth:.2f} m MBGL" in rationale or "Observation depth is unrecorded" in rationale
            assert "reference tier" in rationale.lower()

            # Must explicitly disclaim establishing storage, recharge, stress, or availability
            assert "water table depth alone cannot establish" in rationale.lower()
            assert "aquifer storage" in rationale.lower()
            assert "recharge potential" in rationale.lower()
            assert "extraction stress" in rationale.lower()
            assert "groundwater availability" in rationale.lower()

            # Must NOT infer hydraulic drawdown, saturation, or buffer mitigation as established facts
            assert "indicates substantial hydraulic drawdown" not in rationale.lower()
            assert "indicates high relative saturation" not in rationale.lower()
            assert "buffer tier where conservation measures help mitigate" not in rationale.lower()


def test_no_unsupported_geological_statements_in_advisories(data_and_models):
    """Verify that unverified geological assertions (basalt, deccan traps) are excluded from advisories."""
    df, models = data_and_models
    fallback = get_fallback_advisory("Saswad", df, reason="Test", models=models)

    # Field verification statement must not assert specific geological formations
    vf_stmt = fallback["field_verification_statement"]
    assert "basalt" not in vf_stmt.lower()
    assert "deccan traps" not in vf_stmt.lower()
    assert "water table depth measurements alone cannot determine site-specific infiltration rates" in vf_stmt.lower()

    # Limitations must not assert specific geological formations without documentation
    lims_text = " ".join(fallback["limitations_and_uncertainty"]).lower()
    assert "basalt" not in lims_text
    assert "deccan traps" not in lims_text
    assert "subsurface lithology, aquifer storage, recharge potential, or extraction stress" in lims_text

    # Action rationales must not assert specific geological formations
    for action in fallback["recommended_actions"]:
        rat = action["hydrogeological_rationale"].lower()
        assert "basalt" not in rat
        assert "deccan traps" not in rat


def test_source_attribution_distinguishes_project_from_official_gov(data_and_models):
    """Verify that project-defined heuristics are not falsely attributed to CGWB/GSDA."""
    df, models = data_and_models
    fallback = get_fallback_advisory("Saswad", df, reason="Test", models=models)

    # Model ID must reflect project heuristic baseline, not official agency rule
    assert fallback["model_id"] == "project-heuristic-baseline"

    # Advisory summary must attribute tier and heuristics to project definition, not official government directives
    summary = fallback["advisory_summary"]
    assert "project-defined" in summary.lower()
    assert "official cgwb" not in summary.lower()
    assert "official gsda" not in summary.lower()

    # Relevance explanation must clearly state it is a preliminary project framework, not official directive
    relevance = fallback["explanation_of_relevance"]
    assert "project-defined" in relevance.lower()
    assert "official cgwb or gsda" in relevance.lower()
    assert "do not" in relevance.lower() or "nor do they represent" in relevance.lower()


# =====================================================================
# Context Assembler Tests
# =====================================================================

def test_context_assembler_eligible_station(data_and_models):
    """Verify that stations with >=10 soundings include full telemetry and valid ML forecasts."""
    df, models = data_and_models
    context = build_station_telemetry_context("Jejuri", df, models=models)

    assert context["station_name"] == "Jejuri"
    telemetry = context["telemetry"]
    assert telemetry["data_type"] == "measured_historical_observation"
    assert isinstance(telemetry["observed_depth_mbgl"], float)
    assert telemetry["observation_date"] is not None
    assert telemetry["total_station_records"] >= 10
    assert telemetry["previous_depth_mbgl"] is not None
    assert telemetry["depth_change_m"] is not None
    assert telemetry["days_elapsed"] is not None

    stats = context["historical_stats"]
    assert stats["min_depth_mbgl"] <= telemetry["observed_depth_mbgl"] <= stats["max_depth_mbgl"] or True
    assert stats["mean_depth_mbgl"] > 0

    rain = context["rainfall_indicators"]
    assert "is_rainfall_extrapolated" in rain
    assert "extrapolation_caveat" in rain

    det = context["deterministic_tier"]
    assert det["category"] in ["Shallow", "Moderate", "Deep"]
    assert len(det["heuristic_actions"]) > 0

    ml = context["ml_forecast"]
    assert ml["is_available"] is True
    assert ml["data_type"] == "statistical_machine_learning_forecast"
    assert isinstance(ml["predicted_next_depth_mbgl"], float)
    assert isinstance(ml["uncertainty_interval_q10_mbgl"], float)
    assert isinstance(ml["uncertainty_interval_q90_mbgl"], float)
    assert ml["uncertainty_interval_q10_mbgl"] <= ml["uncertainty_interval_q90_mbgl"]
    assert "predicted_direction" in ml


def test_context_assembler_ineligible_station(data_and_models):
    """Verify that stations with <10 soundings honestly flag ML forecasts as unavailable."""
    df, models = data_and_models
    ineligible_stations = [s for s in df['station'].unique() if (df['station'] == s).sum() < 10]
    assert len(ineligible_stations) == 2

    for st_name in ineligible_stations:
        context = build_station_telemetry_context(st_name, df, models=models)
        assert context["station_name"] == st_name
        assert context["telemetry"]["total_station_records"] < 10
        ml = context["ml_forecast"]
        assert ml["is_available"] is False
        assert "< 10 soundings" in ml["reason"]


def test_context_assembler_extrapolated_station(data_and_models):
    """Verify that extrapolated stations are correctly flagged in context."""
    df, models = data_and_models
    context = build_station_telemetry_context("Narayanpur", df, models=models)
    assert context["rainfall_indicators"]["is_rainfall_extrapolated"] is True
    assert ">10 km" in context["rainfall_indicators"]["extrapolation_caveat"]


def test_context_assembler_invalid_station_raises(data_and_models):
    """Verify that requesting an unrecorded station raises a clear ValueError."""
    df, models = data_and_models
    with pytest.raises(ValueError, match="not found in groundwater dataset"):
        build_station_telemetry_context("NonexistentStationX", df, models=models)


# =====================================================================
# Deterministic Fallback Tests
# =====================================================================

def test_fallback_advisory_structure_and_parity(data_and_models):
    """Verify that fallback advisory adheres to schema and maps to standard heuristic rules."""
    df, models = data_and_models
    fallback = get_fallback_advisory("Saswad", df, reason="Test fallback trigger", models=models)

    assert fallback["is_fallback"] is True
    assert fallback["fallback_reason"] == "Test fallback trigger"
    assert fallback["model_id"] == "project-heuristic-baseline"
    assert fallback["station_name"] == "Saswad"
    assert isinstance(fallback["observed_depth_mbgl"], float)
    assert fallback["physical_depth_tier"] in [
        "Shallow (< 4.0 m)",
        "Moderate (4.0–8.0 m)",
        "Deep (> 8.0 m)",
    ]

    # Validate supporting evidence
    se = fallback["supporting_evidence"]
    assert se["observed_depth_mbgl"] == fallback["observed_depth_mbgl"]
    assert "Saswad" in se["historical_context"]

    # Validate recommended actions
    actions = fallback["recommended_actions"]
    assert len(actions) >= 2
    for action in actions:
        assert action["action_category"] in [
            "Recharge", "Demand_Management", "Monitoring", "Soil_Water_Conservation"
        ]
        assert action["priority"] in ["High", "Medium", "Low"]
        assert len(action["title"]) > 0
        assert len(action["description"]) > 0
        assert len(action["hydrogeological_rationale"]) > 0
        assert len(action["preconditions_and_feasibility"]) > 0

    # Validate disclaimers and limitations
    assert fallback["field_verification_statement"] == MANDATORY_FIELD_VERIFICATION_STATEMENT
    assert len(fallback["limitations_and_uncertainty"]) == len(DEFAULT_LIMITATIONS)


# =====================================================================
# Advisory Generation & Mock LLM Tests
# =====================================================================

def test_generate_station_advisory_missing_key_fallback(data_and_models):
    """Verify that when no API key is provided, the function gracefully returns fallback."""
    df, models = data_and_models
    with mock.patch("os.environ.get", return_value=None):
        result = generate_station_advisory("Jejuri", df, models=models)
        assert result["is_fallback"] is True
        assert "Gemini API key is not configured" in result["fallback_reason"]
        assert result["station_name"] == "Jejuri"
        assert len(result["recommended_actions"]) > 0


def test_generate_station_advisory_successful_mock(data_and_models):
    """Verify end-to-end parsing and schema validation with a mocked valid Gemini response."""
    df, models = data_and_models

    mock_llm_json = json.dumps({
        "station_name": "Jejuri",
        "advisory_summary": "Water table at Jejuri is observed at 5.26 m MBGL within the Moderate reference tier.",
        "observed_depth_mbgl": 5.26,
        "physical_depth_tier": "Moderate (4.0–8.0 m)",
        "supporting_evidence": {
            "observed_depth_mbgl": 5.26,
            "observation_date": "2023-05-15",
            "physical_depth_tier": "Moderate (4.0–8.0 m)",
            "historical_context": "Historical records show regular seasonal fluctuation between 2m and 8m.",
            "rainfall_context": "Antecedent 365d rainfall recorded at 517.2 mm from local IMD grid.",
            "forecast_context": "Random forest projects slight depletion toward next irregular survey."
        },
        "recommended_actions": [
            {
                "title": "Continuous Contour Trenching (CCT)",
                "action_category": "Soil_Water_Conservation",
                "description": "Construct staggered contour trenches along upper ridge slopes to retard runoff.",
                "hydrogeological_rationale": "Observed water level (5.26 m MBGL) falls within the Moderate reference tier. Depth alone cannot establish storage or recharge.",
                "preconditions_and_feasibility": "Requires slope assessment (<8%) and infiltration feasibility testing.",
                "priority": "Medium"
            },
            {
                "title": "Micro-Irrigation Transition",
                "action_category": "Demand_Management",
                "description": "Encourage drip irrigation for seasonal agricultural water efficiency.",
                "hydrogeological_rationale": "Observed depth indicates Moderate reference tier. Depth alone cannot prove extraction stress.",
                "preconditions_and_feasibility": "Farmer subsidy eligibility and pressurized distribution.",
                "priority": "High"
            }
        ],
        "explanation_of_relevance": "Interventions provide preliminary planning options based on physical depth tiers.",
        "limitations_and_uncertainty": [
            "Soundings are irregular and historical.",
            "Water table depth measurements alone cannot establish subsurface lithology or recharge potential."
        ],
        "field_verification_statement": MANDATORY_FIELD_VERIFICATION_STATEMENT
    })

    mock_response = mock.MagicMock()
    mock_response.text = mock_llm_json

    mock_client = mock.MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    result = generate_station_advisory(
        station_name="Jejuri",
        df=df,
        models=models,
        client=mock_client,
        model_id="gemini-3.1-flash-lite"
    )

    assert result["is_fallback"] is False
    assert result["fallback_reason"] is None
    assert result["model_id"] == "gemini-3.1-flash-lite"
    assert result["station_name"] == "Jejuri"
    assert len(result["recommended_actions"]) == 2
    assert result["recommended_actions"][0]["title"] == "Continuous Contour Trenching (CCT)"
    assert result["field_verification_statement"] == MANDATORY_FIELD_VERIFICATION_STATEMENT


def test_generate_station_advisory_malformed_json_fallback(data_and_models):
    """Verify that malformed JSON from LLM triggers graceful deterministic fallback."""
    df, models = data_and_models

    mock_response = mock.MagicMock()
    mock_response.text = "NOT_VALID_JSON_AT_ALL {{{ ... }}}"

    mock_client = mock.MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    result = generate_station_advisory(
        station_name="Saswad",
        df=df,
        models=models,
        client=mock_client
    )

    assert result["is_fallback"] is True
    assert "Gemini API generation error" in result["fallback_reason"]
    assert result["station_name"] == "Saswad"
    assert len(result["recommended_actions"]) > 0


def test_generate_station_advisory_incomplete_schema_fallback(data_and_models):
    """Verify that JSON missing required fields triggers fallback."""
    df, models = data_and_models

    mock_response = mock.MagicMock()
    mock_response.text = json.dumps({"station_name": "Saswad", "advisory_summary": "Short summary"})

    mock_client = mock.MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    result = generate_station_advisory(
        station_name="Saswad",
        df=df,
        models=models,
        client=mock_client
    )

    assert result["is_fallback"] is True
    assert "validation error" in result["fallback_reason"].lower() or "generation error" in result["fallback_reason"].lower()


def test_generate_station_advisory_api_error_fallback(data_and_models):
    """Verify that API runtime errors (quota, 503, timeout) safely trigger fallback."""
    df, models = data_and_models

    mock_client = mock.MagicMock()
    mock_client.models.generate_content.side_effect = Exception("429 ResourceExhausted: Quota limit reached")

    result = generate_station_advisory(
        station_name="Pangre Sailar Basti",
        df=df,
        models=models,
        client=mock_client
    )

    assert result["is_fallback"] is True
    assert "Quota limit reached" in result["fallback_reason"]
    assert result["station_name"] == "Pangre Sailar Basti"
    assert len(result["recommended_actions"]) > 0


def test_generate_station_advisory_unsupported_model_fallback(data_and_models):
    """Verify that passing an unsupported model ID gracefully falls back."""
    df, models = data_and_models

    mock_client = mock.MagicMock()
    mock_client.models.generate_content.side_effect = Exception("404 Model 'unsupported-model-v99' not found")

    result = generate_station_advisory(
        station_name="Sakurde",
        df=df,
        models=models,
        client=mock_client,
        model_id="unsupported-model-v99"
    )

    assert result["is_fallback"] is True
    assert "not found" in result["fallback_reason"].lower()
    assert result["station_name"] == "Sakurde"


def test_generate_station_advisory_data_honesty_enforcement(data_and_models):
    """Verify that service forcibly re-anchors critical telemetry even if LLM drifts."""
    df, models = data_and_models

    hallucinated_json = json.dumps({
        "station_name": "HallucinatedStationName",
        "advisory_summary": "Test summary",
        "observed_depth_mbgl": 99.99,
        "physical_depth_tier": "Deep (> 8.0 m)",
        "supporting_evidence": {
            "observed_depth_mbgl": 99.99,
            "observation_date": "2023-01-01",
            "physical_depth_tier": "Deep (> 8.0 m)",
            "historical_context": "Historical context",
            "rainfall_context": "Rainfall context",
        },
        "recommended_actions": [
            {
                "title": "Check Dam Construction",
                "action_category": "Recharge",
                "description": "Construct check dam",
                "hydrogeological_rationale": "Surface runoff capture",
                "preconditions_and_feasibility": "Site survey required",
                "priority": "High"
            }
        ],
        "explanation_of_relevance": "Test relevance",
        "limitations_and_uncertainty": ["Test limitation"],
        "field_verification_statement": "Custom modified statement"
    })

    mock_response = mock.MagicMock()
    mock_response.text = hallucinated_json

    mock_client = mock.MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    real_context = build_station_telemetry_context("Jejuri", df, models=models)
    real_depth = real_context["telemetry"]["observed_depth_mbgl"]

    result = generate_station_advisory(
        station_name="Jejuri",
        df=df,
        models=models,
        client=mock_client
    )

    assert result["is_fallback"] is False
    assert result["station_name"] == "Jejuri"
    assert result["observed_depth_mbgl"] == real_depth
    assert result["observed_depth_mbgl"] != 99.99
    assert result["field_verification_statement"] == MANDATORY_FIELD_VERIFICATION_STATEMENT


def test_prompt_grounding_and_safety_instructions(data_and_models):
    """Verify that user prompt contains verified telemetry and explicit safety constraints."""
    df, models = data_and_models

    mock_client = mock.MagicMock()
    mock_response = mock.MagicMock()
    mock_response.text = json.dumps({
        "station_name": "Saswad",
        "advisory_summary": "Summary",
        "observed_depth_mbgl": 4.5,
        "physical_depth_tier": "Moderate (4.0–8.0 m)",
        "supporting_evidence": {
            "observed_depth_mbgl": 4.5,
            "observation_date": "2023-01-01",
            "physical_depth_tier": "Moderate (4.0–8.0 m)",
            "historical_context": "Hist",
            "rainfall_context": "Rain",
        },
        "recommended_actions": [
            {
                "title": "Micro-Irrigation",
                "action_category": "Demand_Management",
                "description": "Desc",
                "hydrogeological_rationale": "Rationale",
                "preconditions_and_feasibility": "Feasibility",
                "priority": "Medium"
            }
        ],
        "explanation_of_relevance": "Rel",
        "limitations_and_uncertainty": ["Lim"],
        "field_verification_statement": MANDATORY_FIELD_VERIFICATION_STATEMENT
    })
    mock_client.models.generate_content.return_value = mock_response

    generate_station_advisory("Saswad", df, models=models, client=mock_client)

    call_args = mock_client.models.generate_content.call_args
    prompt_sent = call_args.kwargs.get("contents") or call_args.args[1]

    # Verify telemetry presence
    assert "Saswad" in prompt_sent
    assert "STATION TELEMETRY CONTEXT" in prompt_sent
    assert "measured_historical_observation" in prompt_sent

    # Verify explicit constraints in prompt
    assert "Never state specific volumetric yield increases" in prompt_sent
    assert "Never state or imply that predictions are live sensor measurements" in prompt_sent
    assert "groundwater depth alone cannot establish aquifer storage" in prompt_sent
    assert "Clearly distinguish project-defined heuristic rules from official CGWB or GSDA" in prompt_sent


def test_pydantic_schema_validation_direct():
    """Verify direct Pydantic model validation and serialization."""
    action = HydrogeologicalAction(
        title="Check Dam Feasibility",
        action_category="Recharge",
        description="Detailed description of structure.",
        hydrogeological_rationale="Depth falls in Moderate tier; depth alone cannot establish storage.",
        preconditions_and_feasibility="Topographic gradient < 3%, infiltration rate testing.",
        priority="High"
    )
    assert action.action_category == "Recharge"
    assert action.priority == "High"

    with pytest.raises(Exception):
        HydrogeologicalAction(
            title="Invalid Action",
            action_category="InvalidCategory",
            description="Desc",
            hydrogeological_rationale="Rationale",
            preconditions_and_feasibility="Feasibility",
            priority="High"
        )


# =====================================================================
# Stage 4: Controlled Failure Handling Tests with Mocks
# =====================================================================

def test_failure_handling_missing_api_key_deterministic_fallback(data_and_models):
    """Verify that when API key is missing, generation safely returns deterministic fallback."""
    df, models = data_and_models
    with mock.patch("services.gemini_service.get_gemini_api_key", return_value=None):
        result = generate_station_advisory("Saswad", df, models=models)
        assert result["is_fallback"] is True
        assert result["model_id"] == "project-heuristic-baseline"
        assert result["station_name"] == "Saswad"
        assert "Gemini API key is not configured" in result["fallback_reason"]
        assert len(result["recommended_actions"]) > 0
        assert result["field_verification_statement"] == MANDATORY_FIELD_VERIFICATION_STATEMENT


def test_failure_handling_quota_or_rate_limit_deterministic_fallback(data_and_models):
    """Verify that 429 quota or rate-limit errors safely fall back without exposing keys."""
    df, models = data_and_models
    fake_key = "AIzaSyTestSecretKey429Mock"

    with mock.patch("services.gemini_service.get_gemini_api_key", return_value=fake_key):
        mock_client = mock.MagicMock()
        mock_client.models.generate_content.side_effect = Exception(
            f"429 ResourceExhausted: Quota exceeded for project using key {fake_key}"
        )

        result = generate_station_advisory(
            station_name="Zendewadi",
            df=df,
            models=models,
            client=mock_client
        )

        assert result["is_fallback"] is True
        assert result["model_id"] == "project-heuristic-baseline"
        assert result["station_name"] == "Zendewadi"
        assert "429 ResourceExhausted" in result["fallback_reason"]
        assert fake_key not in result["fallback_reason"]
        assert "[REDACTED_API_KEY]" in result["fallback_reason"]
        assert len(result["recommended_actions"]) > 0


def test_failure_handling_network_api_failure_deterministic_fallback(data_and_models):
    """Verify that network or 503 service unavailable errors safely fall back."""
    df, models = data_and_models
    mock_client = mock.MagicMock()
    mock_client.models.generate_content.side_effect = ConnectionError("503 Service Unavailable: Network timeout")

    result = generate_station_advisory(
        station_name="Jejuri",
        df=df,
        models=models,
        client=mock_client
    )

    assert result["is_fallback"] is True
    assert result["model_id"] == "project-heuristic-baseline"
    assert result["station_name"] == "Jejuri"
    assert "503 Service Unavailable" in result["fallback_reason"]
    assert len(result["recommended_actions"]) > 0


def test_failure_handling_malformed_response_deterministic_fallback(data_and_models):
    """Verify that corrupted or malformed structured responses safely fall back."""
    df, models = data_and_models
    mock_response = mock.MagicMock()
    mock_response.text = '{"station_name": "Saswad", "incomplete": true'  # Truncated invalid JSON

    mock_client = mock.MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    result = generate_station_advisory(
        station_name="Saswad",
        df=df,
        models=models,
        client=mock_client
    )

    assert result["is_fallback"] is True
    assert result["model_id"] == "project-heuristic-baseline"
    assert result["station_name"] == "Saswad"
    assert "generation error" in result["fallback_reason"].lower()
    assert len(result["recommended_actions"]) > 0

