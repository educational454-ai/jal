"""Unit tests for BhujalDrishti theme palette tokens and alert styling consistency."""
import pytest
from styles.theme import THEME_PALETTES, get_theme_palette


REQUIRED_CORE_TOKENS = [
    "bg_primary",
    "bg_secondary",
    "bg_surface",
    "border",
    "text_primary",
    "text_secondary",
    "text_muted",
    "teal_accent",
    "blue_accent",
    "callout_bg",
    "callout_border",
    "callout_text",
    "callout_text_secondary",
    "sidebar_bg",
    "sidebar_border",
    "chart_bg",
    "chart_grid",
]

REQUIRED_ALERT_TOKENS = [
    "alert_info_bg",
    "alert_info_border",
    "alert_info_text",
    "alert_warning_bg",
    "alert_warning_border",
    "alert_warning_text",
    "alert_error_bg",
    "alert_error_border",
    "alert_error_text",
    "alert_success_bg",
    "alert_success_border",
    "alert_success_text",
]


def test_theme_palettes_structure():
    """Verify dark and light theme palettes are properly configured."""
    assert "dark" in THEME_PALETTES, "Missing 'dark' palette in THEME_PALETTES"
    assert "light" in THEME_PALETTES, "Missing 'light' palette in THEME_PALETTES"


def test_core_tokens_presence():
    """Verify all required core layout and component tokens exist in both palettes."""
    for theme_name in ["dark", "light"]:
        palette = THEME_PALETTES[theme_name]
        for token in REQUIRED_CORE_TOKENS:
            assert token in palette, f"Token '{token}' missing from '{theme_name}' palette"
            assert isinstance(palette[token], str) and len(palette[token].strip()) > 0, (
                f"Token '{token}' in '{theme_name}' palette must be a non-empty string"
            )


def test_alert_tokens_presence():
    """Verify all semantic alert tokens exist in both palettes."""
    for theme_name in ["dark", "light"]:
        palette = THEME_PALETTES[theme_name]
        for token in REQUIRED_ALERT_TOKENS:
            assert token in palette, f"Alert token '{token}' missing from '{theme_name}' palette"
            assert isinstance(palette[token], str) and len(palette[token].strip()) > 0, (
                f"Alert token '{token}' in '{theme_name}' palette must be a non-empty string"
            )


def test_token_parity_between_themes():
    """Verify both dark and light palettes have identical token keys."""
    dark_keys = set(THEME_PALETTES["dark"].keys())
    light_keys = set(THEME_PALETTES["light"].keys())
    assert dark_keys == light_keys, f"Palette key mismatch: {dark_keys ^ light_keys}"


def test_get_theme_palette_helper():
    """Verify get_theme_palette retrieves the expected palette dictionary."""
    dark_pal = get_theme_palette("dark")
    light_pal = get_theme_palette("light")
    default_pal = get_theme_palette("nonexistent_theme")

    assert dark_pal == THEME_PALETTES["dark"]
    assert light_pal == THEME_PALETTES["light"]
    assert default_pal == THEME_PALETTES["light"]  # fallback default
