import os
import platform
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
USE_SYSTEM_THEME = os.getenv("USE_SYSTEM_THEME", "true").lower() == "true"

# Application Settings
DEFAULT_THEME = os.getenv("THEME", "dark")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_EMAIL_LENGTH = int(os.getenv("MAX_EMAIL_LENGTH", 10000))


def detect_system_theme():
    """Detect the OS light/dark preference."""
    if platform.system() == "Windows":
        try:
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            ) as key:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return "light" if value == 1 else "dark"
        except Exception:
            return DEFAULT_THEME
    if platform.system() == "Darwin":
        try:
            import subprocess
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
            )
            return "dark" if result.returncode == 0 else "light"
        except Exception:
            return DEFAULT_THEME
    return DEFAULT_THEME

SYSTEM_THEME = detect_system_theme() if USE_SYSTEM_THEME else None
THEME = SYSTEM_THEME if USE_SYSTEM_THEME else DEFAULT_THEME

# Model Configuration
MODEL_NAME = "gpt-3.5-turbo"
TEMPERATURE = 0.3
MAX_TOKENS = 1500

# UI Configuration
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "AI Phishing Email Detector"

# Colors
COLOR_SAFE = "#2ecc71"
COLOR_WARNING = "#f39c12"
COLOR_DANGER = "#e74c3c"
COLOR_DARK_BG = "#1e1e1e"
COLOR_LIGHT_BG = "#f5f5f5"
