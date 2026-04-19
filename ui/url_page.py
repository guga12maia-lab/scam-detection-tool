from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QPlainTextEdit,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from ui.widgets.report_display import ReportDisplayWidget
from utils.worker import AnalysisWorker
from agents.url_agent import URLScannerAgent
from utils.logger import get_logger
import config

logger = get_logger(__name__)


class URLPage(QWidget):
    go_back = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("phishingPage")
        self.worker = None
        self._dot_timer = QTimer(self)
        self._dot_timer.setInterval(400)
        self._dot_timer.timeout.connect(self._pulse_btn)
        self._dot_count = 0
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 28, 48, 32)
        root.setSpacing(0)

        top = QHBoxLayout()
        top.setSpacing(12)
        back_btn = QPushButton("← Back")
        back_btn.setObjectName("backBtn")
        back_btn.setFixedHeight(32)
        back_btn.clicked.connect(self.go_back)
        top.addWidget(back_btn)

        title = QLabel("URL Scanner")
        title.setObjectName("pageTitle")
        top.addWidget(title)
        top.addStretch()

        self.status_lbl = QLabel("Ready to scan")
        self.status_lbl.setObjectName("statusLabel")
        top.addWidget(self.status_lbl)
        root.addLayout(top)
        root.addSpacing(20)

        panels = QHBoxLayout()
        panels.setSpacing(16)

        left = QFrame()
        left.setObjectName("panel")
        lv = QVBoxLayout(left)
        lv.setContentsMargins(20, 20, 20, 20)
        lv.setSpacing(12)

        lv.addWidget(self._section_label("URLS TO SCAN"))

        hint = QLabel("Enter one or more URLs (one per line, or comma-separated)")
        hint.setObjectName("hintLabel")
        hint.setWordWrap(True)
        lv.addWidget(hint)

        self.url_input = QPlainTextEdit()
        self.url_input.setObjectName("emailInput")
        self.url_input.setPlaceholderText(
            "https://example.com\nhttp://suspicious-site.xyz/login\nbit.ly/abc123"
        )
        lv.addWidget(self.url_input)

        btn_row = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("secondaryBtn")
        clear_btn.setFixedHeight(34)
        clear_btn.clicked.connect(self.url_input.clear)
        btn_row.addWidget(clear_btn)
        lv.addLayout(btn_row)

        self.scan_btn = QPushButton("Scan URLs")
        self.scan_btn.setObjectName("primaryBtn")
        self.scan_btn.setMinimumHeight(44)
        self.scan_btn.clicked.connect(self._run)
        lv.addWidget(self.scan_btn)

        panels.addWidget(left, 1)

        right = QFrame()
        right.setObjectName("panel")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(20, 20, 20, 20)
        rv.setSpacing(12)
        rv.addWidget(self._section_label("SCAN REPORT"))

        self.report = ReportDisplayWidget()
        rv.addWidget(self.report)
        panels.addWidget(right, 1)

        root.addLayout(panels)

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("sectionLabel")
        return lbl

    def _run(self):
        content = self.url_input.toPlainText().strip()
        if not content:
            self.report.report_text.setPlainText("Enter at least one URL above, then click Scan.")
            return

        self.scan_btn.setEnabled(False)
        self._dot_count = 0
        self._dot_timer.start()
        self.status_lbl.setText("Scanning…")
        self.report.report_text.setPlainText("Scanning URLs…")

        self.worker = AnalysisWorker(URLScannerAgent, content)
        self.worker.finished.connect(self._on_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _pulse_btn(self):
        self._dot_count = (self._dot_count + 1) % 4
        self.scan_btn.setText(f"Scanning{'.' * self._dot_count}")

    def _on_done(self, result: dict):
        self._dot_timer.stop()
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("Scan URLs")
        self.status_lbl.setText("Scan complete")
        self.report.display_report(result)

    def _on_error(self, msg: str):
        self._dot_timer.stop()
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("Scan URLs")
        self.status_lbl.setText("Scan failed")
        self.report.report_text.setPlainText(f"Error: {msg}")
        logger.error(msg)
