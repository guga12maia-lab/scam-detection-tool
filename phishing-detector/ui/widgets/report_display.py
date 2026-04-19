from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.styles import get_threat_color

class ReportDisplayWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(14)

        self.title_label = QLabel("Analysis Report")
        self.title_label.setObjectName("sectionTitle")
        layout.addWidget(self.title_label)

        info_row = QHBoxLayout()
        self.threat_label = QLabel("Threat Level: --")
        self.threat_label.setObjectName("statusTag")
        info_row.addWidget(self.threat_label)

        self.confidence_label = QLabel("Confidence: --%")
        self.confidence_label.setObjectName("secondaryTag")
        info_row.addWidget(self.confidence_label)
        info_row.addStretch()
        layout.addLayout(info_row)

        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setMinimumHeight(320)
        self.report_text.setObjectName("reportBox")
        layout.addWidget(self.report_text)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.copy_btn = QPushButton("Copy Report")
        self.copy_btn.setObjectName("secondaryButton")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(self.copy_btn)

        self.export_btn = QPushButton("Export Report")
        self.export_btn.setObjectName("secondaryButton")
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.clear_report()

    def display_report(self, verdict: dict):
        threat_level = verdict.get('threat_level', 'UNKNOWN')
        confidence = verdict.get('confidence_score', 0)
        recommendation = verdict.get('recommendation', '')
        summary = verdict.get('summary', '')

        self.threat_label.setText(threat_level)
        threat_color = get_threat_color(threat_level)
        self.threat_label.setStyleSheet(
            f"color: {threat_color}; font-weight: bold; padding: 6px 12px; border: 1px solid {threat_color}; border-radius: 12px;"
        )

        self.confidence_label.setText(f"Confidence: {confidence}%")

        report = f"""
THREAT ASSESSMENT: {threat_level}
Confidence Score: {confidence}%

RECOMMENDATION:
{recommendation}

DETAILED ANALYSIS:
{summary}
"""
        self.report_text.setPlainText(report)

    def clear_report(self):
        self.threat_label.setText("Threat Level: --")
        self.threat_label.setStyleSheet("")
        self.confidence_label.setText("Confidence: --%")
        self.report_text.setPlainText("No analysis yet. Analyze an email to see results here.")

    def copy_to_clipboard(self):
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.report_text.toPlainText())
        self.copy_btn.setText("Copied!")
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.copy_btn.setText("Copy Report"))
