from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from ui.widgets.email_input import EmailInputWidget
from ui.widgets.report_display import ReportDisplayWidget
from agents.phishing_agent import PhishingDetectionAgent
from utils.logger import get_logger
import config

logger = get_logger(__name__)


class AnalysisThread(QThread):
    analysis_complete = pyqtSignal(dict)
    analysis_error = pyqtSignal(str)

    def __init__(self, email_content: str):
        super().__init__()
        self.email_content = email_content
        self._agent = None

    def run(self):
        try:
            if not self._agent:
                self._agent = PhishingDetectionAgent()
            result = self._agent.analyze_email(self.email_content)
            self.analysis_complete.emit(result["final_verdict"])
        except Exception as e:
            self.analysis_error.emit(f"Analysis failed: {e}")


class PhishingPage(QWidget):
    go_back = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("phishingPage")
        self.analysis_thread = None
        self._dot_timer = QTimer(self)
        self._dot_timer.setInterval(400)
        self._dot_timer.timeout.connect(self._pulse_btn)
        self._dot_count = 0
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 28, 48, 32)
        root.setSpacing(0)

        # ── Top row: back + title ──────────────────────────────────────
        top = QHBoxLayout()
        top.setSpacing(12)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("backBtn")
        back_btn.setFixedHeight(32)
        back_btn.clicked.connect(self.go_back)
        top.addWidget(back_btn)

        title = QLabel("Phishing Detector")
        title.setObjectName("pageTitle")
        top.addWidget(title)
        top.addStretch()

        status_lbl = QLabel("Ready to scan")
        status_lbl.setObjectName("statusLabel")
        self.status_lbl = status_lbl
        top.addWidget(status_lbl)

        root.addLayout(top)
        root.addSpacing(20)

        # ── Two panels side by side ────────────────────────────────────
        panels = QHBoxLayout()
        panels.setSpacing(16)

        # Left panel – email input
        left = QFrame()
        left.setObjectName("panel")
        lv = QVBoxLayout(left)
        lv.setContentsMargins(20, 20, 20, 20)
        lv.setSpacing(12)

        lbl = QLabel("EMAIL CONTENT")
        lbl.setObjectName("sectionLabel")
        lv.addWidget(lbl)

        self.email_input = EmailInputWidget()
        lv.addWidget(self.email_input)

        self.analyze_btn = QPushButton("Analyze Email")
        self.analyze_btn.setObjectName("primaryBtn")
        self.analyze_btn.setMinimumHeight(44)
        self.analyze_btn.clicked.connect(self._run_analysis)
        lv.addWidget(self.analyze_btn)

        panels.addWidget(left, 1)

        # Right panel – report
        right = QFrame()
        right.setObjectName("panel")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(20, 20, 20, 20)
        rv.setSpacing(12)

        lbl2 = QLabel("ANALYSIS REPORT")
        lbl2.setObjectName("sectionLabel")
        rv.addWidget(lbl2)

        self.report = ReportDisplayWidget()
        rv.addWidget(self.report)

        panels.addWidget(right, 1)
        root.addLayout(panels)

    def _run_analysis(self):
        content = self.email_input.get_email_content().strip()
        if not content:
            self.report.report_text.setPlainText("Paste an email above, then click Analyze.")
            return
        if len(content) > config.MAX_EMAIL_LENGTH:
            self.report.report_text.setPlainText(f"Email too long (max {config.MAX_EMAIL_LENGTH} chars).")
            return

        self.analyze_btn.setEnabled(False)
        self._dot_count = 0
        self._dot_timer.start()
        self.status_lbl.setText("Scanning…")
        self.report.report_text.setPlainText("Analyzing email — this takes a few seconds…")

        self.analysis_thread = AnalysisThread(content)
        self.analysis_thread.analysis_complete.connect(self._on_done)
        self.analysis_thread.analysis_error.connect(self._on_error)
        self.analysis_thread.start()

    def _pulse_btn(self):
        self._dot_count = (self._dot_count + 1) % 4
        dots = "." * self._dot_count
        self.analyze_btn.setText(f"Analyzing{dots}")

    def _on_done(self, verdict: dict):
        self._dot_timer.stop()
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("Analyze Email")
        self.status_lbl.setText("Analysis complete")
        self.report.display_report(verdict)

    def _on_error(self, msg: str):
        self._dot_timer.stop()
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("Analyze Email")
        self.status_lbl.setText("Analysis failed")
        self.report.report_text.setPlainText(f"Error: {msg}")
        logger.error(msg)
