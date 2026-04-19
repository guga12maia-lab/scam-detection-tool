from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QFrame,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import config
from ui.styles import get_stylesheet
from ui.widgets.email_input import EmailInputWidget
from ui.widgets.report_display import ReportDisplayWidget
from agents.phishing_agent import PhishingDetectionAgent
from utils.logger import get_logger

logger = get_logger(__name__)

class AnalysisThread(QThread):
    """Thread for running analysis without blocking UI"""
    analysis_complete = pyqtSignal(dict)
    analysis_error = pyqtSignal(str)

    def __init__(self, email_content: str):
        super().__init__()
        self.email_content = email_content
        self.agent = None

    def run(self):
        try:
            if not self.agent:
                self.agent = PhishingDetectionAgent()

            result = self.agent.analyze_email(self.email_content)
            self.analysis_complete.emit(result['final_verdict'])
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            self.analysis_error.emit(f"Analysis failed: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.setStyleSheet(get_stylesheet())
        self.analysis_thread = None
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        base_layout = QVBoxLayout()
        base_layout.setContentsMargins(24, 24, 24, 24)
        base_layout.setSpacing(18)

        header = QLabel("Scam Alert")
        header.setObjectName("appTitle")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        base_layout.addWidget(header)

        subtitle = QLabel("Modern phishing detection with clean, responsive UI")
        subtitle.setObjectName("appSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        base_layout.addWidget(subtitle)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        left_card = QFrame()
        left_card.setObjectName("cardPanel")
        left_card_layout = QVBoxLayout(left_card)
        left_card_layout.setSpacing(14)
        left_card_layout.addWidget(QLabel("Email Input"))
        self.email_input = EmailInputWidget()
        left_card_layout.addWidget(self.email_input)

        self.analyze_btn = QPushButton("Analyze Email")
        self.analyze_btn.setObjectName("primaryButton")
        self.analyze_btn.setMinimumHeight(52)
        self.analyze_btn.clicked.connect(self.analyze_email)
        left_card_layout.addWidget(self.analyze_btn)

        self.status_bar = QLabel("Ready to scan emails")
        self.status_bar.setObjectName("statusLabel")
        self.status_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_card_layout.addWidget(self.status_bar)

        right_card = QFrame()
        right_card.setObjectName("cardPanel")
        right_card_layout = QVBoxLayout(right_card)
        right_card_layout.setSpacing(12)

        report_title = QLabel("Analysis Report")
        report_title.setObjectName("sectionTitle")
        right_card_layout.addWidget(report_title)
        self.report_display = ReportDisplayWidget()
        right_card_layout.addWidget(self.report_display)

        settings_row = QHBoxLayout()
        settings_row.setSpacing(10)
        settings_row.addWidget(QLabel("Theme"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["system", "dark", "light"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        active_theme = "system" if config.USE_SYSTEM_THEME else config.THEME
        self.theme_combo.setCurrentText(active_theme)
        settings_row.addWidget(self.theme_combo)
        settings_row.addStretch()
        right_card_layout.addLayout(settings_row)

        content_layout.addWidget(left_card, 1)
        content_layout.addWidget(right_card, 1)

        base_layout.addLayout(content_layout)
        main_widget.setLayout(base_layout)

    def analyze_email(self):
        email_content = self.email_input.get_email_content().strip()

        if not email_content:
            self.report_display.report_text.setPlainText("❌ Please enter email content first.")
            self.status_bar.setText("Enter email content to begin analysis")
            return

        if len(email_content) > config.MAX_EMAIL_LENGTH:
            self.report_display.report_text.setPlainText(
                f"❌ Email too long. Max {config.MAX_EMAIL_LENGTH} characters."
            )
            self.status_bar.setText("Email content exceeds the maximum length")
            return

        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("Analyzing…")
        self.status_bar.setText("Scanning email for phishing indicators...")
        self.report_display.report_text.setPlainText("🔄 Analyzing email... Please wait.")

        self.analysis_thread = AnalysisThread(email_content)
        self.analysis_thread.analysis_complete.connect(self.on_analysis_complete)
        self.analysis_thread.analysis_error.connect(self.on_analysis_error)
        self.analysis_thread.start()

    def on_analysis_complete(self, verdict: dict):
        self.report_display.display_report(verdict)
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("Analyze Email")
        self.status_bar.setText("Analysis completed")
        logger.info("Analysis complete")

    def on_analysis_error(self, error_msg: str):
        self.report_display.report_text.setPlainText(f"❌ {error_msg}")
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("Analyze Email")
        self.status_bar.setText("Analysis failed")
        logger.error(error_msg)

    def change_theme(self, theme: str):
        if theme == "system":
            theme = config.SYSTEM_THEME or config.DEFAULT_THEME
        self.setStyleSheet(get_stylesheet(theme))
