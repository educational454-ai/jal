"""Unit tests for Gemini API configuration, secure credential handling, and client initialization."""
import os
import unittest.mock as mock
import pytest
from services.gemini_service import (
    get_gemini_api_key,
    is_gemini_configured,
    get_configured_model_id,
    get_gemini_client,
    DEFAULT_GEMINI_MODEL,
)


@pytest.fixture(autouse=True)
def clean_gemini_env():
    """Ensure GEMINI_API_KEY and GEMINI_MODEL_ID are not set in the test environment by default."""
    old_key = os.environ.pop("GEMINI_API_KEY", None)
    old_model = os.environ.pop("GEMINI_MODEL_ID", None)
    yield
    if old_key is not None:
        os.environ["GEMINI_API_KEY"] = old_key
    if old_model is not None:
        os.environ["GEMINI_MODEL_ID"] = old_model


def test_missing_key_detection():
    """Verify that when no API key is set, functions return None/False safely."""
    with mock.patch("streamlit.secrets", {}):
        assert get_gemini_api_key() is None
        assert is_gemini_configured() is False
        assert get_gemini_client() is None


def test_placeholder_key_ignored():
    """Verify that template placeholder values are treated as unconfigured."""
    with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "your-gemini-api-key-here"}):
        assert get_gemini_api_key() is None
        assert is_gemini_configured() is False
        assert get_gemini_client() is None


def test_empty_whitespace_key_ignored():
    """Verify that empty or whitespace-only keys are treated as unconfigured."""
    with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "   "}):
        assert get_gemini_api_key() is None
        assert is_gemini_configured() is False
        assert get_gemini_client() is None


def test_env_var_key_detection():
    """Verify fallback detection of GEMINI_API_KEY from environment variables."""
    mock_key = "AIzaSyFakeMockTestKeyForValidationOnly123"
    with mock.patch.dict(os.environ, {"GEMINI_API_KEY": mock_key}):
        with mock.patch("streamlit.secrets", {}):
            assert is_gemini_configured() is True
            assert get_gemini_api_key() == mock_key


def test_streamlit_secrets_priority_over_env():
    """Verify that Streamlit Secrets takes precedence over environment variable."""
    secrets_key = "AIzaSyFromStreamlitSecrets999"
    env_key = "AIzaSyFromEnvironmentVariable888"
    mock_secrets = {"GEMINI_API_KEY": secrets_key}
    with mock.patch.dict(os.environ, {"GEMINI_API_KEY": env_key}):
        with mock.patch("streamlit.secrets", mock_secrets):
            assert get_gemini_api_key() == secrets_key
            assert is_gemini_configured() is True


def test_client_initialization_with_key():
    """Verify that google.genai.Client is initialized with the configured key without network calls."""
    mock_key = "AIzaSyFakeKeyForClientInitValidation"
    with mock.patch.dict(os.environ, {"GEMINI_API_KEY": mock_key}):
        client = get_gemini_client()
        assert client is not None
        # Verify it is an instance of google.genai.Client
        from google import genai
        assert isinstance(client, genai.Client)


def test_centralized_model_id_configuration():
    """Verify centralized model ID handling without hardcoded model strings."""
    # When unconfigured, returns default constant (currently empty string in Stage 1)
    with mock.patch("streamlit.secrets", {}):
        assert get_configured_model_id() == DEFAULT_GEMINI_MODEL

    # From environment
    with mock.patch.dict(os.environ, {"GEMINI_MODEL_ID": "gemini-2.5-flash-test"}):
        with mock.patch("streamlit.secrets", {}):
            assert get_configured_model_id() == "gemini-2.5-flash-test"

    # From Streamlit secrets
    mock_secrets = {"GEMINI_MODEL_ID": "gemini-2.5-flash-secrets"}
    with mock.patch("streamlit.secrets", mock_secrets):
        assert get_configured_model_id() == "gemini-2.5-flash-secrets"
