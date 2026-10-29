"""Theme configuration and styling injection for BhujalDrishti."""
import os
import streamlit as st

THEME_PALETTES = {
    "dark": {
        "bg_primary": "#07141B",
        "bg_secondary": "#0B2029",
        "bg_surface": "#102A35",
        "bg_surface_hover": "#163745",
        "border": "#23414B",
        "text_primary": "#EAF6F7",
        "text_secondary": "#A5BEC5",
        "text_muted": "#7E9FA7",
        "teal_accent": "#35D0C1",
        "blue_accent": "#58B9E8",
        "callout_bg": "#0B2029",
        "callout_border": "#23414B",
        "callout_text": "#EAF6F7",
        "callout_text_secondary": "#A5BEC5",
        "alert_info_bg": "rgba(36, 125, 168, 0.18)",
        "alert_info_border": "rgba(88, 185, 232, 0.35)",
        "alert_info_text": "#BAE6FD",
        "alert_warning_bg": "rgba(245, 158, 11, 0.15)",
        "alert_warning_border": "rgba(245, 158, 11, 0.35)",
        "alert_warning_text": "#FDE68A",
        "alert_error_bg": "rgba(239, 68, 68, 0.18)",
        "alert_error_border": "rgba(239, 68, 68, 0.35)",
        "alert_error_text": "#FECACA",
        "alert_success_bg": "rgba(16, 185, 129, 0.18)",
        "alert_success_border": "rgba(16, 185, 129, 0.35)",
        "alert_success_text": "#A7F3D0",
        "sidebar_bg": "#0B2029",
        "sidebar_border": "#23414B",
        "chart_bg": "#102A35",
        "chart_grid": "#23414B",
    },
    "light": {
        "bg_primary": "#F4F8F8",
        "bg_secondary": "#EBF2F3",
        "bg_surface": "#FFFFFF",
        "bg_surface_hover": "#F8FAFA",
        "border": "#D9E5E7",
        "text_primary": "#17313B",
        "text_secondary": "#617780",
        "text_muted": "#82969E",
        "teal_accent": "#087F80",
        "blue_accent": "#247DA8",
        "callout_bg": "#F8FAFC",
        "callout_border": "#CBD5E1",
        "callout_text": "#1E293B",
        "callout_text_secondary": "#475569",
        "alert_info_bg": "#EFF6FF",
        "alert_info_border": "#BFDBFE",
        "alert_info_text": "#1E40AF",
        "alert_warning_bg": "#FEFCE8",
        "alert_warning_border": "#FDE047",
        "alert_warning_text": "#854D0E",
        "alert_error_bg": "#FEF2F2",
        "alert_error_border": "#FECACA",
        "alert_error_text": "#991B1B",
        "alert_success_bg": "#F0FDFA",
        "alert_success_border": "#99F6E4",
        "alert_success_text": "#087F80",
        "sidebar_bg": "#F8FAFC",
        "sidebar_border": "#E2E8F0",
        "chart_bg": "#FAFAFA",
        "chart_grid": "#E2E8F0",
    }
}


def init_theme(default_theme: str = "light") -> str:
    """Initialize theme in session state if not already present."""
    if "app_theme" not in st.session_state:
        st.session_state["app_theme"] = default_theme
    return st.session_state["app_theme"]


def get_current_theme() -> str:
    """Retrieve the currently active theme identifier ('dark' or 'light')."""
    return st.session_state.get("app_theme", "light")


def toggle_theme() -> str:
    """Toggle between light and dark themes and return new theme."""
    current = get_current_theme()
    new_theme = "dark" if current == "light" else "light"
    st.session_state["app_theme"] = new_theme
    return new_theme


def get_theme_palette(theme: str = None) -> dict:
    """Retrieve color palette dictionary for chart rendering."""
    if theme is None:
        theme = get_current_theme()
    return THEME_PALETTES.get(theme, THEME_PALETTES["light"])


def apply_theme(theme: str = None) -> None:
    """Inject centralized CSS and apply theme-specific tokens."""
    if theme is None:
        theme = get_current_theme()
    
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            
    palette = get_theme_palette(theme)
    
    # Generate dynamic override styles for the active theme
    theme_css = f"""
    <style>
        {css_content}
        
        :root {{
            --bg-primary: {palette['bg_primary']};
            --bg-secondary: {palette['bg_secondary']};
            --bg-surface: {palette['bg_surface']};
            --border-color: {palette['border']};
            --text-primary: {palette['text_primary']};
            --text-secondary: {palette['text_secondary']};
            --text-muted: {palette['text_muted']};
            --teal-accent: {palette['teal_accent']};
            --blue-accent: {palette['blue_accent']};
            --callout-bg: {palette['callout_bg']};
            --callout-border: {palette['callout_border']};
            --callout-text: {palette['callout_text']};
            --callout-text-secondary: {palette['callout_text_secondary']};
            --alert-info-bg: {palette['alert_info_bg']};
            --alert-info-border: {palette['alert_info_border']};
            --alert-info-text: {palette['alert_info_text']};
            --alert-warning-bg: {palette['alert_warning_bg']};
            --alert-warning-border: {palette['alert_warning_border']};
            --alert-warning-text: {palette['alert_warning_text']};
            --alert-error-bg: {palette['alert_error_bg']};
            --alert-error-border: {palette['alert_error_border']};
            --alert-error-text: {palette['alert_error_text']};
            --alert-success-bg: {palette['alert_success_bg']};
            --alert-success-border: {palette['alert_success_border']};
            --alert-success-text: {palette['alert_success_text']};
            --sidebar-bg: {palette['sidebar_bg']};
            --sidebar-border: {palette['sidebar_border']};
        }}
        
        /* Direct container backgrounds based on active theme */
        .stApp {{
            background-color: {palette['bg_primary']} !important;
            color: {palette['text_primary']} !important;
        }}

        /* Sidebar Complete Theme Integration */
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div,
        div[data-testid="stSidebarContent"],
        div[data-testid="stSidebarUserContent"] {{
            background-color: {palette['sidebar_bg']} !important;
            border-right: 1px solid {palette['sidebar_border']} !important;
        }}
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] span {{
            color: {palette['text_primary']} !important;
        }}
        section[data-testid="stSidebar"] hr {{
            border-color: {palette['sidebar_border']} !important;
        }}
        section[data-testid="stSidebar"] .sidebar-brand-name {{
            color: {palette['text_primary']} !important;
        }}
        section[data-testid="stSidebar"] .sidebar-brand-tagline {{
            color: {palette['teal_accent']} !important;
        }}
        section[data-testid="stSidebar"] .telemetry-box {{
            background-color: {palette['bg_surface']} !important;
            border: 1px solid {palette['border']} !important;
            color: {palette['text_secondary']} !important;
        }}
        section[data-testid="stSidebar"] .telemetry-box b {{
            color: {palette['text_primary']} !important;
        }}

        /* Native Streamlit Metric Contrast & Responsive Typography */
        div[data-testid="stMetric"] {{
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-start !important;
        }}
        [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] *,
        [data-testid="stMetricLabel"] p,
        [data-testid="stMetricLabel"] span,
        [data-testid="stMetricLabel"] label,
        [data-testid="stMetricLabel"] div,
        .stMarkdownEllipsis {{
            color: {palette['text_secondary']} !important;
            white-space: normal !important;
            word-wrap: break-word !important;
            overflow: visible !important;
            text-overflow: unset !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            line-height: 1.35 !important;
        }}
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] *,
        div[data-testid="stMetricValue"] > div,
        div[data-testid="stMetricValue"] span,
        div[data-testid="stMetricValue"] p {{
            color: {palette['text_primary']} !important;
            font-size: clamp(1.15rem, 1.8vw, 1.55rem) !important;
            font-weight: 700 !important;
            line-height: 1.25 !important;
            white-space: normal !important;
            word-break: normal !important;
            overflow-wrap: break-word !important;
        }}
        div[data-testid="stMetricDelta"],
        div[data-testid="stMetricDelta"] > div,
        div[data-testid="stMetricDelta"] span {{
            white-space: normal !important;
            word-wrap: break-word !important;
            font-size: 0.8rem !important;
            line-height: 1.3 !important;
        }}

        /* Column Stretching & Equal-Height Alignment in Dynamic Theme */
        div[data-testid="stHorizontalBlock"] {{
            align-items: stretch !important;
        }}
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{
            display: flex !important;
            flex-direction: column !important;
        }}
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {{
            display: flex !important;
            flex-direction: column !important;
            flex: 1 1 auto !important;
            height: 100% !important;
        }}
        div[data-testid="stHorizontalBlock"]:has(.metric-card) > div[data-testid="stColumn"],
        div[data-testid="stHorizontalBlock"]:has(.kpi-card) > div[data-testid="stColumn"] {{
            display: flex !important;
            flex-direction: column !important;
        }}
        div[data-testid="stHorizontalBlock"]:has(.metric-card) div[data-testid="stVerticalBlock"],
        div[data-testid="stHorizontalBlock"]:has(.kpi-card) div[data-testid="stVerticalBlock"],
        div[data-testid="stHorizontalBlock"]:has(.metric-card) div[data-testid="stElementContainer"],
        div[data-testid="stHorizontalBlock"]:has(.kpi-card) div[data-testid="stElementContainer"],
        div[data-testid="stHorizontalBlock"]:has(.metric-card) div[data-testid="stMarkdown"],
        div[data-testid="stHorizontalBlock"]:has(.kpi-card) div[data-testid="stMarkdown"],
        div[data-testid="stHorizontalBlock"]:has(.metric-card) div[data-testid="stMarkdown"] > div,
        div[data-testid="stHorizontalBlock"]:has(.kpi-card) div[data-testid="stMarkdown"] > div,
        div[data-testid="stHorizontalBlock"]:has(.metric-card) div[data-testid="stMarkdownContainer"],
        div[data-testid="stHorizontalBlock"]:has(.kpi-card) div[data-testid="stMarkdownContainer"] {{
            display: flex !important;
            flex-direction: column !important;
            flex: 1 1 auto !important;
            height: 100% !important;
        }}

        /* Dropdowns & Select Components */
        div[data-baseweb="select"] > div {{
            background-color: {palette['bg_surface']} !important;
            border-color: {palette['border']} !important;
            color: {palette['text_primary']} !important;
        }}

        /* Targeted Streamlit Alert Theming & Contrast Protection */
        div[data-testid="stAlert"] {{
            background-color: transparent !important;
            border: none !important;
            padding: 0 !important;
        }}
        div[data-testid="stAlert"] > div[data-testid="stAlertContainer"] {{
            border-radius: 8px !important;
            padding: 12px 16px !important;
            background-color: {palette['callout_bg']} !important;
            border: 1px solid {palette['callout_border']} !important;
            color: {palette['callout_text']} !important;
        }}

        /* Specific Semantic Alert Types */
        div[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) > div[data-testid="stAlertContainer"],
        div[data-testid="stAlert"] > div[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) {{
            background-color: {palette['alert_info_bg']} !important;
            border: 1px solid {palette['alert_info_border']} !important;
        }}
        div[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) p,
        div[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) span,
        div[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) strong,
        [data-testid="stAlertContentInfo"] p,
        [data-testid="stAlertContentInfo"] span {{
            color: {palette['alert_info_text']} !important;
        }}
        div[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) svg,
        [data-testid="stAlertContentInfo"] svg {{
            fill: {palette['alert_info_text']} !important;
            color: {palette['alert_info_text']} !important;
        }}

        div[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) > div[data-testid="stAlertContainer"],
        div[data-testid="stAlert"] > div[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) {{
            background-color: {palette['alert_warning_bg']} !important;
            border: 1px solid {palette['alert_warning_border']} !important;
        }}
        div[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) p,
        div[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) span,
        div[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) strong,
        [data-testid="stAlertContentWarning"] p,
        [data-testid="stAlertContentWarning"] span {{
            color: {palette['alert_warning_text']} !important;
        }}
        div[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) svg,
        [data-testid="stAlertContentWarning"] svg {{
            fill: {palette['alert_warning_text']} !important;
            color: {palette['alert_warning_text']} !important;
        }}

        div[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) > div[data-testid="stAlertContainer"],
        div[data-testid="stAlert"] > div[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) {{
            background-color: {palette['alert_error_bg']} !important;
            border: 1px solid {palette['alert_error_border']} !important;
        }}
        div[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) p,
        div[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) span,
        div[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) strong,
        [data-testid="stAlertContentError"] p,
        [data-testid="stAlertContentError"] span {{
            color: {palette['alert_error_text']} !important;
        }}
        div[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) svg,
        [data-testid="stAlertContentError"] svg {{
            fill: {palette['alert_error_text']} !important;
            color: {palette['alert_error_text']} !important;
        }}

        div[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) > div[data-testid="stAlertContainer"],
        div[data-testid="stAlert"] > div[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) {{
            background-color: {palette['alert_success_bg']} !important;
            border: 1px solid {palette['alert_success_border']} !important;
        }}
        div[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) p,
        div[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) span,
        div[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) strong,
        [data-testid="stAlertContentSuccess"] p,
        [data-testid="stAlertContentSuccess"] span {{
            color: {palette['alert_success_text']} !important;
        }}
        div[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) svg,
        [data-testid="stAlertContentSuccess"] svg {{
            fill: {palette['alert_success_text']} !important;
            color: {palette['alert_success_text']} !important;
        }}

        /* Streamlit Expander Theming */
        details[data-testid="stExpander"] {{
            background-color: {palette['bg_surface']} !important;
            border: 1px solid {palette['border']} !important;
            border-radius: 8px !important;
        }}
        details[data-testid="stExpander"] summary {{
            color: {palette['text_primary']} !important;
        }}
        details[data-testid="stExpander"] summary:hover {{
            color: {palette['teal_accent']} !important;
        }}
        details[data-testid="stExpander"] summary svg {{
            fill: {palette['text_secondary']} !important;
        }}
    </style>
    """
    st.markdown(theme_css, unsafe_allow_html=True)
