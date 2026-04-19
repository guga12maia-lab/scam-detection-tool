import os
import json
import platform
from dotenv import load_dotenv

load_dotenv()

# API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
_demo_env = os.getenv("DEMO_MODE", "false").lower() == "true"
DEMO_MODE = _demo_env or not OPENAI_API_KEY  # auto-demo when no key
VT_API_KEY = os.getenv("VT_API_KEY", "")  # overridden below from saved settings if present

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_EMAIL_LENGTH = int(os.getenv("MAX_EMAIL_LENGTH", 10000))

# Model
MODEL_NAME = "gpt-3.5-turbo"
TEMPERATURE = 0.3
MAX_TOKENS = 1500

# Window
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 780
WINDOW_TITLE = "Scam Detection"

# Threat colors
COLOR_SAFE = "#3dd68c"
COLOR_WARNING = "#f0a030"
COLOR_DANGER = "#f05050"

# Accent palette
ACCENT_COLORS = {
    "blue":   "#4a78ff",
    "red":    "#f05050",
    "green":  "#3dd68c",
    "purple": "#9f70f0",
    "orange": "#f0a030",
    "teal":   "#20c8b8",
}

# --- User settings (persisted to disk) ---
_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "user_settings.json")

def _load_settings() -> dict:
    if os.path.exists(_SETTINGS_FILE):
        try:
            with open(_SETTINGS_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_settings(data: dict):
    try:
        with open(_SETTINGS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

_settings = _load_settings()

def get_setting(key: str, default):
    return _settings.get(key, default)

def set_setting(key: str, value):
    _settings[key] = value
    _save_settings(_settings)
    # Sync live API key into module-level variable
    if key == "vt_api_key":
        global VT_API_KEY
        VT_API_KEY = value


def detect_system_theme() -> str:
    if platform.system() == "Windows":
        try:
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            ) as key:
                v, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return "light" if v == 1 else "dark"
        except Exception:
            pass
    return "dark"


SYSTEM_THEME = detect_system_theme()

# Runtime-mutable values (updated when settings change)
THEME = get_setting("theme", SYSTEM_THEME)
ACCENT = get_setting("accent", "blue")
ANIMATIONS = get_setting("animations", True)
VT_API_KEY = get_setting("vt_api_key", VT_API_KEY)  # prefer saved key over env
