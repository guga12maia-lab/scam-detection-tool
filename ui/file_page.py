import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QFileDialog,
)
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from ui.widgets.report_display import ReportDisplayWidget
from utils.worker import AnalysisWorker
from agents.file_agent import FileCheckerAgent
from utils.logger import get_logger
import config

logger = get_logger(__name__)


class DropZone(QFrame):
    """File drop target with click-to-browse."""
    file_chosen = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(110)
        self.setCursor(__import__('PyQt6.QtCore', fromlist=['Qt']).Qt.CursorShape.PointingHandCursor)
        self._path = ""

        layout = QVBoxLayout(self)
        layout.setAlignment(__import__('PyQt6.QtCore', fromlist=['Qt']).Qt.AlignmentFlag.AlignCenter)

        self._icon_lbl = QLabel("📁")
        self._icon_lbl.setStyleSheet("font-size: 28px; background: transparent; border: none;")
        self._icon_lbl.setAlignment(__import__('PyQt6.QtCore', fromlist=['Qt']).Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._icon_lbl)

        self._hint_lbl = QLabel("Drop a file here, or click to browse")
        self._hint_lbl.setObjectName("hintLabel")
        self._hint_lbl.setAlignment(__import__('PyQt6.QtCore', fromlist=['Qt']).Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._hint_lbl)

    def set_file(self, path: str):
        self._path = path
        name = os.path.basename(path)
        size = os.path.getsize(path)
        size_str = f"{size/1024:.1f} KB" if size < 1024*1024 else f"{size/(1024*1024):.1f} MB"
        self._icon_lbl.setText("📄")
        self._hint_lbl.setText(f"{name}  ({size_str})")

    def clear(self):
        self._path = ""
        self._icon_lbl.setText("📁")
        self._hint_lbl.setText("Drop a file here, or click to browse")

    def get_path(self) -> str:
        return self._path

    def mousePressEvent(self, event):
        path, _ = QFileDialog.getOpenFileName(self, "Select file")
        if path:
            self.set_file(path)
            self.file_chosen.emit(path)
        super().mousePressEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isfile(path):
                self.set_file(path)
                self.file_chosen.emit(path)
        super().dropEvent(event)


class FilePage(QWidget):
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

        title = QLabel("File Detector")
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

        lv.addWidget(self._section_label("FILE TO SCAN"))

        vt_status = "VirusTotal enabled" if config.VT_API_KEY else "No VT key — static analysis only (add key in Settings)"
        hint = QLabel(vt_status)
        hint.setObjectName("hintLabel")
        hint.setWordWrap(True)
        self._vt_hint = hint
        lv.addWidget(hint)

        self.drop_zone = DropZone()
        lv.addWidget(self.drop_zone)

        btn_row = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("secondaryBtn")
        clear_btn.setFixedHeight(34)
        clear_btn.clicked.connect(self._clear)
        btn_row.addWidget(clear_btn)
        lv.addLayout(btn_row)

        self.scan_btn = QPushButton("Scan File")
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

    def refresh_vt_hint(self):
        vt_status = "VirusTotal enabled" if config.VT_API_KEY else "No VT key — static analysis only (add key in Settings)"
        self._vt_hint.setText(vt_status)

    def _clear(self):
        self.drop_zone.clear()
        self.report.report_text.clear()
        self.status_lbl.setText("Ready")

    def _run(self):
        path = self.drop_zone.get_path()
        if not path:
            self.report.report_text.setPlainText("Select a file first, then click Scan.")
            return

        self.scan_btn.setEnabled(False)
        self._dot_count = 0
        self._dot_timer.start()
        self.status_lbl.setText("Scanning…")
        self.report.report_text.setPlainText("Scanning file…")

        self.worker = AnalysisWorker(FileCheckerAgent, path)
        self.worker.finished.connect(self._on_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _pulse_btn(self):
        self._dot_count = (self._dot_count + 1) % 4
        self.scan_btn.setText(f"Scanning{'.' * self._dot_count}")

    def _on_done(self, result: dict):
        self._dot_timer.stop()
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("Scan File")
        self.status_lbl.setText("Scan complete")
        self.report.display_report(result)

    def _on_error(self, msg: str):
        self._dot_timer.stop()
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("Scan File")
        self.status_lbl.setText("Scan failed")
        self.report.report_text.setPlainText(f"Error: {msg}")
        logger.error(msg)
