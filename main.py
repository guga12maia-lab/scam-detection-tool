import sys
from PyQt6.QtWidgets import QApplication
from ui.app_window import AppWindow
import config


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Scam Detection")
    if not config.DEMO_MODE and not config.OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY not set — running in demo mode")

    window = AppWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
