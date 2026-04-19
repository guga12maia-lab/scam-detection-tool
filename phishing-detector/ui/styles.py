import config

DARK_STYLESHEET = """
QMainWindow {
    background-color: #121721;
    color: #e6ecf5;
}

QWidget {
    background-color: #121721;
    color: #e6ecf5;
}

QFrame#cardPanel {
    background-color: #19212e;
    border: 1px solid #2c3a54;
    border-radius: 18px;
}

QLabel#appTitle {
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
}

QLabel#appSubtitle {
    font-size: 12px;
    color: #99a3b9;
    margin-bottom: 12px;
}

QLabel#sectionTitle {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 8px;
}

QLabel#sectionLabel {
    font-size: 13px;
    font-weight: 600;
    color: #d9e3f5;
}

QLabel#statusLabel {
    font-size: 11px;
    color: #8fa4c8;
}

QTextEdit#inputField, QTextEdit#reportBox {
    background-color: #152033;
    color: #f1f6ff;
    border: 1px solid #2c3a54;
    border-radius: 14px;
    padding: 14px;
    font-family: 'Segoe UI', Arial;
    font-size: 10.5pt;
}

QPushButton#primaryButton {
    background-color: #4f7dff;
    color: white;
    border: none;
    border-radius: 14px;
    padding: 14px;
    font-size: 11pt;
    font-weight: 700;
}

QPushButton#primaryButton:hover {
    background-color: #608dff;
}

QPushButton#secondaryButton {
    background-color: #1d2a42;
    color: #d7e2ff;
    border: 1px solid #2f456e;
    border-radius: 12px;
    padding: 10px 16px;
}

QPushButton#secondaryButton:hover {
    background-color: #263655;
}

QPushButton:disabled {
    background-color: #2f456e;
    color: #7c8dbf;
}

QComboBox {
    background-color: #152033;
    color: #e6ecf5;
    border: 1px solid #2c3a54;
    border-radius: 12px;
    padding: 8px 10px;
}

QComboBox QAbstractItemView {
    background-color: #152033;
    color: #e6ecf5;
    border: 1px solid #2c3a54;
}

QScrollBar:vertical {
    width: 10px;
    background-color: #131b29;
}

QScrollBar::handle:vertical {
    background-color: #3a4c6f;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5b6d93;
}

QLabel {
    color: #e6ecf5;
}

QMessageBox {
    background-color: #19212e;
    color: #e6ecf5;
}

QMessageBox QLabel {
    color: #e6ecf5;
}

QMessageBox QPushButton {
    min-width: 70px;
}

QLabel#secondaryTag {
    color: #a1b3d1;
}
"""

LIGHT_STYLESHEET = """
QMainWindow {
    background-color: #f4f6fb;
    color: #1f2937;
}

QWidget {
    background-color: #f4f6fb;
    color: #1f2937;
}

QFrame#cardPanel {
    background-color: #ffffff;
    border: 1px solid #d8e2f1;
    border-radius: 18px;
}

QLabel#appTitle {
    font-size: 28px;
    font-weight: 800;
}

QLabel#appSubtitle {
    font-size: 12px;
    color: #667085;
    margin-bottom: 12px;
}

QLabel#sectionTitle {
    font-size: 18px;
    font-weight: 700;
}

QLabel#sectionLabel {
    font-size: 13px;
    font-weight: 600;
    color: #344054;
}

QLabel#statusLabel {
    font-size: 11px;
    color: #667085;
}

QTextEdit#inputField, QTextEdit#reportBox {
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #d8e2f1;
    border-radius: 14px;
    padding: 14px;
    font-family: 'Segoe UI', Arial;
    font-size: 10.5pt;
}

QPushButton#primaryButton {
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 14px;
    padding: 14px;
    font-size: 11pt;
    font-weight: 700;
}

QPushButton#primaryButton:hover {
    background-color: #3b82f6;
}

QPushButton#secondaryButton {
    background-color: #eef2ff;
    color: #334155;
    border: 1px solid #c7d2fe;
    border-radius: 12px;
    padding: 10px 16px;
}

QPushButton#secondaryButton:hover {
    background-color: #e0e7ff;
}

QPushButton:disabled {
    background-color: #cbd5e1;
    color: #64748b;
}

QComboBox {
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #d8e2f1;
    border-radius: 12px;
    padding: 8px 10px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #d8e2f1;
}

QScrollBar:vertical {
    width: 10px;
    background-color: #f1f5f9;
}

QScrollBar::handle:vertical {
    background-color: #a6b7d0;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #8192b0;
}

QLabel {
    color: #1f2937;
}

QMessageBox {
    background-color: #ffffff;
    color: #1f2937;
}

QMessageBox QLabel {
    color: #1f2937;
}

QMessageBox QPushButton {
    min-width: 70px;
}

QLabel#secondaryTag {
    color: #475569;
}
"""

def get_stylesheet(theme: str = None) -> str:
    """Get stylesheet based on theme"""
    theme = theme or config.THEME
    return DARK_STYLESHEET if theme == "dark" else LIGHT_STYLESHEET

def get_threat_color(threat_level: str) -> str:
    """Get color for threat level"""
    if "CRITICAL" in threat_level or "HIGH" in threat_level:
        return config.COLOR_DANGER
    elif "MEDIUM" in threat_level:
        return config.COLOR_WARNING
    else:
        return config.COLOR_SAFE
