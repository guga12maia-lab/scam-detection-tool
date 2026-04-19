from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QApplication
from PyQt6.QtCore import QTimer
from ui.styles import get_threat_color
import config


class ReportDisplayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Threat + confidence row
        badge_row = QHBoxLayout()
        badge_row.setSpacing(12)

        self.threat_lbl = QLabel("—")
        self.threat_lbl.setObjectName("statusLabel")
        badge_row.addWidget(self.threat_lbl)

        self.conf_lbl = QLabel("")
        self.conf_lbl.setObjectName("statusLabel")
        badge_row.addWidget(self.conf_lbl)

        badge_row.addStretch()
        layout.addLayout(badge_row)

        self.report_text = QTextEdit()
        self.report_text.setObjectName("reportBox")
        self.report_text.setReadOnly(True)
        self.report_text.setMinimumHeight(280)
        self.report_text.setPlainText("No analysis yet. Paste an email and click Analyze.")
        layout.addWidget(self.report_text)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.copy_btn = QPushButton("Copy Report")
        self.copy_btn.setObjectName("secondaryBtn")
        self.copy_btn.setFixedHeight(34)
        self.copy_btn.clicked.connect(self._copy)
        btn_row.addWidget(self.copy_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

    def display_report(self, verdict: dict):
        level = verdict.get("threat_level", "UNKNOWN")
        score = verdict.get("confidence_score", 0)
        rec   = verdict.get("recommendation", "")
        summary = verdict.get("summary", "")

        color = get_threat_color(level)
        self.threat_lbl.setText(level)
        self.threat_lbl.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {color}; background: transparent;"
        )
        self.conf_lbl.setText(f"Confidence: {score}%")
        self.conf_lbl.setStyleSheet("color: #54678a; background: transparent; font-size: 12px;")

        self.report_text.setPlainText(
            f"VERDICT: {level}\n"
            f"Confidence: {score}%\n"
            f"\nRECOMMENDATION:\n{rec}\n"
            f"\nDETAILED ANALYSIS:\n{summary}"
        )

    def _copy(self):
        QApplication.clipboard().setText(self.report_text.toPlainText())
        self.copy_btn.setText("Copied!")
        QTimer.singleShot(2000, lambda: self.copy_btn.setText("Copy Report"))
