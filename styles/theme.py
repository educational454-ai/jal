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
        "bg_primary": "#F5F7F4",
        "bg_secondary": "#EAEFEA",
        "bg_surface": "#FFFFFF",
        "bg_surface_hover": "#F0F5F2",
        "border": "#DCE6E2",
        "text_primary": "#24343A",
        "text_secondary": "#647579",
        "text_muted": "#88989C",
        "teal_accent": "#168C83",
        "blue_accent": "#123B46",
        "callout_bg": "#D8EEE8",
        "callout_border": "#B6DCD3",
        "callout_text": "#24343A",
        "callout_text_secondary": "#647579",
        "alert_info_bg": "#D8EEE8",
        "alert_info_border": "#B6DCD3",
        "alert_info_text": "#123B46",
        "alert_warning_bg": "#FDF6ED",
        "alert_warning_border": "#F5D6A8",
        "alert_warning_text": "#8C5B17",
        "alert_error_bg": "#FEF2F2",
        "alert_error_border": "#FECACA",
        "alert_error_text": "#991B1B",
        "alert_success_bg": "#D8EEE8",
        "alert_success_border": "#B6DCD3",
        "alert_success_text": "#168C83",
        "sidebar_bg": "#FFFFFF",
        "sidebar_border": "#DCE6E2",
        "chart_bg": "#FFFFFF",
        "chart_grid": "#E2EBE7",
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
            --bg-surface-hover: {palette.get('bg_surface_hover', palette['bg_surface'])};
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
        section[data-testid="stSidebar"] hr,
        section[data-testid="stSidebar"] .sidebar-divider {{
            background-color: {palette['sidebar_border']} !important;
            border-color: {palette['sidebar_border']} !important;
        }}
        section[data-testid="stSidebar"] .sidebar-brand-name {{
            color: {palette['text_primary']} !important;
        }}
        section[data-testid="stSidebar"] .sidebar-brand-tagline {{
            color: {palette['teal_accent']} !important;
        }}
        section[data-testid="stSidebar"] .sidebar-footer-sub {{
            color: {palette['text_muted']} !important;
        }}
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {{
            background-color: {palette['bg_surface_hover']} !important;
        }}
        .telemetry-card {{
            background-color: {palette['bg_surface']} !important;
            border: 1px solid {palette['border']} !important;
        }}
        .telemetry-card-label {{
            color: {palette['text_muted']} !important;
        }}
        .telemetry-card-value {{
            color: {palette['text_primary']} !important;
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

        /* Filter & Selectbox Labels - High Contrast Protection */
        div[data-testid="stSelectbox"] label,
        div[data-testid="stSelectbox"] label p,
        div[data-testid="stSelectbox"] label span,
        div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"],
        div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] p,
        div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] span {{
            color: {palette['text_primary']} !important;
            font-weight: 550 !important;
        }}

        /* Dropdowns & Select Components (Theme-aware borders, no red outlines, accessible focus) */
        div[data-testid="stSelectbox"] div[data-rac][role="group"],
        div[data-testid="stSelectbox"] .react-aria-ComboBox div[role="group"],
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        div[data-baseweb="select"] > div {{
            background-color: {palette['bg_surface']} !important;
            border: 1px solid {palette['border']} !important;
            border-color: {palette['border']} !important;
            border-radius: 8px !important;
            color: {palette['text_primary']} !important;
            box-shadow: none !important;
            outline: none !important;
            transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
        }}

        div[data-testid="stSelectbox"] div[data-rac][role="group"]:hover,
        div[data-testid="stSelectbox"] .react-aria-ComboBox div[role="group"]:hover,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover,
        div[data-baseweb="select"] > div:hover {{
            border-color: {palette['teal_accent']} !important;
        }}

        /* Accessible Keyboard and Active Focus State */
        div[data-testid="stSelectbox"] div[data-rac][role="group"]:focus-within,
        div[data-testid="stSelectbox"] .react-aria-ComboBox div[role="group"]:focus-within,
        div[data-testid="stSelectbox"] div[data-rac][role="group"][data-focused="true"],
        div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within > div,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="select"]:focus-within > div,
        div[data-baseweb="select"] > div:focus-within {{
            border-color: {palette['teal_accent']} !important;
            box-shadow: 0 0 0 2px rgba(var(--teal-accent-rgb), 0.28) !important;
            outline: none !important;
        }}

        /* Inputs, buttons and text inside selectbox */
        div[data-testid="stSelectbox"] input,
        div[data-testid="stSelectbox"] input[data-rac] {{
            color: {palette['text_primary']} !important;
            outline: none !important;
            border: none !important;
            box-shadow: none !important;
        }}

        div[data-testid="stSelectbox"] button[data-rac] {{
            color: {palette['text_secondary']} !important;
            border: none !important;
            outline: none !important;
        }}

        /* Suppress unwanted red outline from normal and internal elements */
        div[data-baseweb="select"] *,
        div[data-testid="stSelectbox"] * {{
            outline-color: transparent !important;
        }}

        div[data-testid="stSelectbox"] div[data-rac][role="group"]:focus-visible,
        div[data-testid="stSelectbox"] input:focus-visible,
        div[data-baseweb="select"]:focus-visible,
        div[data-testid="stSelectbox"]:focus-visible,
        div[data-baseweb="select"] input:focus-visible {{
            outline: 2px solid {palette['teal_accent']} !important;
            outline-offset: 1px !important;
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

        /* Buttons - Primary and Secondary Hydro-Tech Styling */
        button[kind="primary"],
        .stButton > button[kind="primary"],
        button[data-testid="baseButton-primary"] {{
            background-color: {palette['blue_accent']} !important;
            color: #FFFFFF !important;
            border: 1px solid {palette['blue_accent']} !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.5rem 1.1rem !important;
            transition: all 0.15s ease !important;
            box-shadow: 0 1px 2px rgba(18, 59, 70, 0.08) !important;
        }}
        button[kind="primary"]:hover,
        .stButton > button[kind="primary"]:hover,
        button[data-testid="baseButton-primary"]:hover {{
            background-color: {palette['teal_accent']} !important;
            border-color: {palette['teal_accent']} !important;
            color: #FFFFFF !important;
        }}
        button[kind="secondary"],
        .stButton > button[kind="secondary"],
        .stButton > button:not([kind="primary"]) {{
            background-color: {palette['bg_surface']} !important;
            color: {palette['text_primary']} !important;
            border: 1px solid {palette['border']} !important;
            border-radius: 8px !important;
            font-weight: 550 !important;
            transition: all 0.15s ease !important;
        }}
        button[kind="secondary"]:hover,
        .stButton > button[kind="secondary"]:hover,
        .stButton > button:not([kind="primary"]):hover {{
            border-color: {palette['teal_accent']} !important;
            color: {palette['teal_accent']} !important;
            background-color: {palette['bg_surface_hover']} !important;
        }}

        /* Tabs Styling - Aqua Teal Highlight */
        div[data-testid="stTabs"] button[role="tab"] {{
            color: {palette['text_secondary']} !important;
            font-weight: 550 !important;
            font-size: 0.90rem !important;
            border-bottom: 2px solid transparent !important;
            padding: 8px 16px !important;
            background-color: transparent !important;
            transition: all 0.15s ease !important;
        }}
        div[data-testid="stTabs"] button[role="tab"]:hover {{
            color: {palette['blue_accent']} !important;
        }}
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
            color: {palette['teal_accent']} !important;
            border-bottom: 2px solid {palette['teal_accent']} !important;
            font-weight: 650 !important;
        }}
        div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {{
            background-color: {palette['teal_accent']} !important;
        }}
        div[data-testid="stTabs"] div[data-baseweb="tab-border"] {{
            background-color: {palette['border']} !important;
        }}

        /* DataFrames & Tables */
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {{
            border: 1px solid {palette['border']} !important;
            border-radius: 8px !important;
            overflow: hidden !important;
            background-color: {palette['bg_surface']} !important;
        }}

        /* Prominent Titles in Deep Teal */
        .main-header,
        .welcome-title,
        .overview-welcome-title,
        .map-welcome-title,
        .forecast-welcome-title,
        .ds-welcome-title,
        h1, h2, h3 {{
            color: {palette['blue_accent']} !important;
        }}
    </style>
    """
    st.markdown(theme_css, unsafe_allow_html=True)
