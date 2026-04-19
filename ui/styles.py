import config

# ── Dark palette ──────────────────────────────────────────────────────────────
_DARK = {
    "bg":          "#0f1218",
    "surface":     "#151d2e",
    "surface2":    "#1a2438",
    "border":      "#1f2d45",
    "border2":     "#263550",
    "text":        "#dde4f0",
    "text2":       "#7a8fad",
    "text3":       "#3d5070",
    "input_bg":    "#0d1420",
}

# ── Light palette ─────────────────────────────────────────────────────────────
_LIGHT = {
    "bg":          "#f0f3f9",
    "surface":     "#ffffff",
    "surface2":    "#f5f7fc",
    "border":      "#d5dce8",
    "border2":     "#c0cad8",
    "text":        "#1a2035",
    "text2":       "#6070a0",
    "text3":       "#a0afc8",
    "input_bg":    "#f8fafd",
}


def _accent_hex(accent_name: str = None) -> str:
    name = accent_name or config.ACCENT
    return config.ACCENT_COLORS.get(name, config.ACCENT_COLORS["blue"])


def get_stylesheet(theme: str = None, accent: str = None) -> str:
    theme = theme or config.THEME
    p = _DARK if theme == "dark" else _LIGHT
    a = _accent_hex(accent)

    # Derive a subtle tinted surface from accent for active states
    return f"""
/* ── Base ──────────────────────────────────────────────────────────── */
QMainWindow, QDialog {{
    background: {p['bg']};
    color: {p['text']};
}}

QWidget {{
    background: {p['bg']};
    color: {p['text']};
    font-family: "Segoe UI Variable", "Segoe UI", system-ui, sans-serif;
    font-size: 13px;
}}

/* ── Nav bar ──────────────────────────────────────────────────────── */
QWidget#navBar {{
    background: {p['surface']};
    border-bottom: 1px solid {p['border']};
}}

QLabel#appName {{
    font-size: 14px;
    font-weight: 700;
    color: {p['text']};
    letter-spacing: -0.3px;
}}

QPushButton#navBtn {{
    background: transparent;
    color: {p['text2']};
    border: none;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 500;
}}

QPushButton#navBtn:hover {{
    background: {p['surface2']};
    color: {p['text']};
}}

QPushButton#navBtn[active="true"] {{
    background: transparent;
    color: {a};
    font-weight: 600;
}}

/* ── Pages ────────────────────────────────────────────────────────── */
QWidget#homePage, QWidget#phishingPage, QWidget#settingsPage {{
    background: {p['bg']};
}}

/* ── Section labels ───────────────────────────────────────────────── */
QLabel#pageTitle {{
    font-size: 22px;
    font-weight: 700;
    color: {p['text']};
    letter-spacing: -0.5px;
}}

QLabel#pageSubtitle {{
    font-size: 13px;
    color: {p['text2']};
}}

QLabel#sectionLabel {{
    font-size: 11px;
    font-weight: 600;
    color: {p['text3']};
    letter-spacing: 0.6px;
    text-transform: uppercase;
}}

/* ── Cards ────────────────────────────────────────────────────────── */
QFrame#panel {{
    background: {p['surface']};
    border: 1px solid {p['border']};
    border-radius: 12px;
}}

/* ── Text input ───────────────────────────────────────────────────── */
QTextEdit#inputField, QTextEdit#reportBox,
QPlainTextEdit#emailInput {{
    background: {p['input_bg']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 8px;
    padding: 12px;
    font-size: 12px;
    selection-background-color: {a};
    selection-color: white;
}}

QTextEdit#inputField:focus, QTextEdit#reportBox:focus,
QPlainTextEdit#emailInput:focus {{
    border-color: {a};
}}

QLineEdit#apiKeyInput {{
    background: {p['input_bg']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 7px;
    padding: 0 10px;
    font-size: 12px;
}}

QLineEdit#apiKeyInput:focus {{
    border-color: {a};
}}

/* ── Drop zone ────────────────────────────────────────────────────── */
QFrame#dropZone {{
    background: {p['input_bg']};
    border: 1.5px dashed {p['border2']};
    border-radius: 10px;
}}

QFrame#dropZone:hover {{
    border-color: {a};
}}

/* ── Hint label ───────────────────────────────────────────────────── */
QLabel#hintLabel {{
    font-size: 11px;
    color: {p['text2']};
}}

/* ── Primary button ───────────────────────────────────────────────── */
QPushButton#primaryBtn {{
    background: {a};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 11px 20px;
    font-size: 13px;
    font-weight: 600;
}}

QPushButton#primaryBtn:hover {{
    background: {a}dd;
}}

QPushButton#primaryBtn:pressed {{
    background: {a}bb;
}}

QPushButton#primaryBtn:disabled {{
    background: {p['border']};
    color: {p['text3']};
}}

/* ── Secondary button ─────────────────────────────────────────────── */
QPushButton#secondaryBtn {{
    background: {p['surface2']};
    color: {p['text2']};
    border: 1px solid {p['border']};
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 500;
}}

QPushButton#secondaryBtn:hover {{
    background: {p['surface']};
    color: {p['text']};
    border-color: {p['border2']};
}}

/* ── Back button ──────────────────────────────────────────────────── */
QPushButton#backBtn {{
    background: transparent;
    color: {p['text2']};
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
}}

QPushButton#backBtn:hover {{
    background: {p['surface2']};
    color: {p['text']};
}}

/* ── Status label ─────────────────────────────────────────────────── */
QLabel#statusLabel {{
    font-size: 11px;
    color: {p['text3']};
}}

/* ── Settings ─────────────────────────────────────────────────────── */
QLabel#settingName {{
    font-size: 13px;
    color: {p['text']};
    font-weight: 500;
}}

QLabel#settingHint {{
    font-size: 11px;
    color: {p['text2']};
}}

QComboBox {{
    background: {p['surface2']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 7px;
    padding: 6px 10px;
    font-size: 12px;
    min-width: 110px;
}}

QComboBox:focus {{
    border-color: {a};
}}

QComboBox QAbstractItemView {{
    background: {p['surface']};
    color: {p['text']};
    border: 1px solid {p['border']};
    selection-background-color: {a};
    selection-color: white;
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

/* ── Scrollbar ────────────────────────────────────────────────────── */
QScrollBar:vertical {{
    width: 6px;
    background: transparent;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {p['border']};
    border-radius: 3px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {p['border2']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{ height: 0; }}

/* ── Threat badge ─────────────────────────────────────────────────── */
QLabel#threatHigh {{
    color: {config.COLOR_DANGER};
    font-weight: 700;
    font-size: 13px;
}}

QLabel#threatMed {{
    color: {config.COLOR_WARNING};
    font-weight: 700;
    font-size: 13px;
}}

QLabel#threatLow {{
    color: {config.COLOR_SAFE};
    font-weight: 700;
    font-size: 13px;
}}

/* ── Divider ──────────────────────────────────────────────────────── */
QFrame#divider {{
    background: {p['border']};
    max-height: 1px;
    border: none;
}}
"""


def get_threat_color(level: str) -> str:
    u = level.upper()
    if "CRITICAL" in u or "HIGH" in u:
        return config.COLOR_DANGER
    if "MEDIUM" in u:
        return config.COLOR_WARNING
    return config.COLOR_SAFE


def palette(theme: str = None) -> dict:
    theme = theme or config.THEME
    return _DARK if theme == "dark" else _LIGHT
