from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QPlainTextEdit,
)
from PyQt6.QtCore import QTimer, pyqtSignal
from ui.widgets.report_display import ReportDisplayWidget
from utils.worker import AnalysisWorker
from agents.report_agent import ReportGeneratorAgent
from utils.logger import get_logger

logger = get_logger(__name__)


class ReportPage(QWidget):
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

        title = QLabel("Report Generator")
        title.setObjectName("pageTitle")
        top.addWidget(title)
        top.addStretch()

        self.status_lbl = QLabel("Ready")
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

        lv.addWidget(self._section_label("INCIDENT DETAILS"))

        hint = QLabel("Paste analysis results, findings, or describe the incident.\nThe generator will structure it into a formal security report.")
        hint.setObjectName("hintLabel")
        hint.setWordWrap(True)
        lv.addWidget(hint)

        self.incident_input = QPlainTextEdit()
        self.incident_input.setObjectName("emailInput")
        self.incident_input.setPlaceholderText(
            "Paste results from other tools here, or describe the incident:\n\n"
            "e.g.\nPhishing email received from noreply@paypa1.support.xyz\n"
            "URL scan: HIGH risk — http://login.paypa1.support.xyz/verify\n"
            "Urgency language detected, credential request, unencrypted link."
        )
        lv.addWidget(self.incident_input)

        btn_row = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("secondaryBtn")
        clear_btn.setFixedHeight(34)
        clear_btn.clicked.connect(self.incident_input.clear)
        btn_row.addWidget(clear_btn)
        lv.addLayout(btn_row)

        self.generate_btn = QPushButton("Generate Report")
        self.generate_btn.setObjectName("primaryBtn")
        self.generate_btn.setMinimumHeight(44)
        self.generate_btn.clicked.connect(self._run)
        lv.addWidget(self.generate_btn)

        panels.addWidget(left, 1)

        right = QFrame()
        right.setObjectName("panel")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(20, 20, 20, 20)
        rv.setSpacing(12)
        rv.addWidget(self._section_label("GENERATED REPORT"))

        self.report = ReportDisplayWidget()
        rv.addWidget(self.report)
        panels.addWidget(right, 1)

        root.addLayout(panels)

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("sectionLabel")
        return lbl

    def _run(self):
        content = self.incident_input.toPlainText().strip()
        if not content:
            self.report.report_text.setPlainText("Add incident details above, then click Generate.")
            return

        self.generate_btn.setEnabled(False)
        self._dot_count = 0
        self._dot_timer.start()
        self.status_lbl.setText("Generating…")
        self.report.report_text.setPlainText("Building report…")

        self.worker = AnalysisWorker(ReportGeneratorAgent, content)
        self.worker.finished.connect(self._on_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _pulse_btn(self):
        self._dot_count = (self._dot_count + 1) % 4
        self.generate_btn.setText(f"Generating{'.' * self._dot_count}")

    def _on_done(self, result: dict):
        self._dot_timer.stop()
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Generate Report")
        self.status_lbl.setText("Report ready")
        self.report.display_report(result)

    def _on_error(self, msg: str):
        self._dot_timer.stop()
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Generate Report")
        self.status_lbl.setText("Generation failed")
        self.report.report_text.setPlainText(f"Error: {msg}")
        logger.error(msg)
