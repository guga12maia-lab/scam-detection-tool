from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QPlainTextEdit,
)
from PyQt6.QtCore import QTimer, pyqtSignal
from ui.widgets.report_display import ReportDisplayWidget
from utils.worker import AnalysisWorker
from agents.domain_agent import DomainCheckerAgent
from utils.logger import get_logger

logger = get_logger(__name__)


class DomainPage(QWidget):
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

        title = QLabel("Domain Checker")
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

        lv.addWidget(self._section_label("DOMAIN NAME"))

        hint = QLabel("Enter the domain you want to check (e.g. example.com)")
        hint.setObjectName("hintLabel")
        hint.setWordWrap(True)
        lv.addWidget(hint)

        self.domain_input = QPlainTextEdit()
        self.domain_input.setObjectName("emailInput")
        self.domain_input.setPlaceholderText("e.g. suspicious-bank-login.xyz\nor paste a full URL — the domain will be extracted")
        lv.addWidget(self.domain_input)

        btn_row = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("secondaryBtn")
        clear_btn.setFixedHeight(34)
        clear_btn.clicked.connect(self.domain_input.clear)
        btn_row.addWidget(clear_btn)
        lv.addLayout(btn_row)

        self.check_btn = QPushButton("Check Domain")
        self.check_btn.setObjectName("primaryBtn")
        self.check_btn.setMinimumHeight(44)
        self.check_btn.clicked.connect(self._run)
        lv.addWidget(self.check_btn)

        panels.addWidget(left, 1)

        right = QFrame()
        right.setObjectName("panel")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(20, 20, 20, 20)
        rv.setSpacing(12)
        rv.addWidget(self._section_label("DOMAIN REPORT"))

        self.report = ReportDisplayWidget()
        rv.addWidget(self.report)
        panels.addWidget(right, 1)

        root.addLayout(panels)

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("sectionLabel")
        return lbl

    def _run(self):
        content = self.domain_input.toPlainText().strip()
        if not content:
            self.report.report_text.setPlainText("Enter a domain name above, then click Check.")
            return

        self.check_btn.setEnabled(False)
        self._dot_count = 0
        self._dot_timer.start()
        self.status_lbl.setText("Checking…")
        self.report.report_text.setPlainText("Looking up domain…")

        self.worker = AnalysisWorker(DomainCheckerAgent, content)
        self.worker.finished.connect(self._on_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _pulse_btn(self):
        self._dot_count = (self._dot_count + 1) % 4
        self.check_btn.setText(f"Checking{'.' * self._dot_count}")

    def _on_done(self, result: dict):
        self._dot_timer.stop()
        self.check_btn.setEnabled(True)
        self.check_btn.setText("Check Domain")
        self.status_lbl.setText("Check complete")
        self.report.display_report(result)

    def _on_error(self, msg: str):
        self._dot_timer.stop()
        self.check_btn.setEnabled(True)
        self.check_btn.setText("Check Domain")
        self.status_lbl.setText("Check failed")
        self.report.report_text.setPlainText(f"Error: {msg}")
        logger.error(msg)
