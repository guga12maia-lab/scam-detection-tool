from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QGraphicsOpacityEffect,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from ui.styles import get_stylesheet
from ui.home_page import HomePage
from ui.phishing_page import PhishingPage
from ui.file_page import FilePage
from ui.url_page import URLPage
from ui.caller_page import CallerPage
from ui.settings_page import SettingsPage
import config

PAGE_HOME     = 0
PAGE_PHISHING = 1
PAGE_FILE     = 2
PAGE_URL      = 3
PAGE_CALLER   = 4
PAGE_SETTINGS = 5

_TOOL_PAGE = {
    "phishing": PAGE_PHISHING,
    "file":     PAGE_FILE,
    "url":      PAGE_URL,
    "caller":   PAGE_CALLER,
}


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setMinimumSize(900, 620)
        self.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self._nav_btns: dict[int, QPushButton] = {}
        self._transition_running = False
        self._build()
        self._apply_style()
        if config.ANIMATIONS:
            self._fade_in_window()

    def _build(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        main.addWidget(self._build_nav())
        main.addWidget(self._build_stack())

    def _build_nav(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("navBar")
        bar.setFixedHeight(52)
        h = QHBoxLayout(bar)
        h.setContentsMargins(24, 0, 24, 0)
        h.setSpacing(4)

        dot = QLabel("●")
        dot.setStyleSheet("color: #f05050; font-size: 10px; background: transparent;")
        h.addWidget(dot)

        name = QLabel("Scam Detection")
        name.setObjectName("appName")
        name.setStyleSheet("background: transparent; margin-left: 4px;")
        h.addWidget(name)
        h.addStretch()

        for idx, label in [(PAGE_HOME, "Tools"), (PAGE_SETTINGS, "Settings")]:
            btn = QPushButton(label)
            btn.setObjectName("navBtn")
            btn.setFixedHeight(32)
            btn.clicked.connect(lambda _, i=idx: self.navigate(i))
            h.addWidget(btn)
            self._nav_btns[idx] = btn

        self._update_nav_highlight(PAGE_HOME)
        return bar

    def _build_stack(self) -> QStackedWidget:
        self.stack = QStackedWidget()

        self.home_page = HomePage()
        self.home_page.open_tool.connect(self._on_tool_selected)

        self.phishing_page = PhishingPage()
        self.phishing_page.go_back.connect(lambda: self.navigate(PAGE_HOME))

        self.file_page = FilePage()
        self.file_page.go_back.connect(lambda: self.navigate(PAGE_HOME))

        self.url_page = URLPage()
        self.url_page.go_back.connect(lambda: self.navigate(PAGE_HOME))

        self.caller_page = CallerPage()
        self.caller_page.go_back.connect(lambda: self.navigate(PAGE_HOME))

        self.settings_page = SettingsPage()
        self.settings_page.theme_changed.connect(self._on_theme_changed)
        self.settings_page.accent_changed.connect(self._on_accent_changed)
        self.settings_page.vt_key_changed.connect(self._on_vt_key_changed)

        self.stack.addWidget(self.home_page)      # 0
        self.stack.addWidget(self.phishing_page)  # 1
        self.stack.addWidget(self.file_page)      # 2
        self.stack.addWidget(self.url_page)       # 3
        self.stack.addWidget(self.caller_page)    # 4
        self.stack.addWidget(self.settings_page)  # 5

        return self.stack

    def _on_tool_selected(self, key: str):
        idx = _TOOL_PAGE.get(key)
        if idx is not None:
            self.navigate(idx)

    def navigate(self, page_idx: int):
        if self.stack.currentIndex() == page_idx:
            return
        if config.ANIMATIONS:
            self._animated_switch(page_idx)
        else:
            self.stack.setCurrentIndex(page_idx)
            self._update_nav_highlight(page_idx)

    def _animated_switch(self, target_idx: int):
        if self._transition_running:
            self.stack.setCurrentIndex(target_idx)
            self._update_nav_highlight(target_idx)
            return

        self._transition_running = True
        current_widget = self.stack.currentWidget()

        self._eff_out = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(self._eff_out)
        self._anim_out = QPropertyAnimation(self._eff_out, b"opacity")
        self._anim_out.setDuration(130)
        self._anim_out.setStartValue(1.0)
        self._anim_out.setEndValue(0.0)
        self._anim_out.setEasingCurve(QEasingCurve.Type.OutCubic)

        def _swap():
            self.stack.setCurrentIndex(target_idx)
            self._update_nav_highlight(target_idx)
            new_widget = self.stack.currentWidget()
            self._eff_in = QGraphicsOpacityEffect(new_widget)
            new_widget.setGraphicsEffect(self._eff_in)
            self._eff_in.setOpacity(0.0)
            self._anim_in = QPropertyAnimation(self._eff_in, b"opacity")
            self._anim_in.setDuration(180)
            self._anim_in.setStartValue(0.0)
            self._anim_in.setEndValue(1.0)
            self._anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._anim_in.finished.connect(lambda: self._finish_transition(new_widget))
            self._anim_in.start()

        self._anim_out.finished.connect(_swap)
        self._anim_out.start()

    def _finish_transition(self, widget: QWidget):
        widget.setGraphicsEffect(None)
        self._transition_running = False

    def _update_nav_highlight(self, active_idx: int):
        for idx, btn in self._nav_btns.items():
            btn.setProperty("active", "true" if idx == active_idx else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _on_theme_changed(self, theme: str):
        self._apply_style()

    def _on_accent_changed(self, key: str):
        self._apply_style()
        self.home_page.refresh_accent()

    def _on_vt_key_changed(self, key: str):
        self.file_page.refresh_vt_hint()

    def _apply_style(self):
        self.setStyleSheet(get_stylesheet())

    def _fade_in_window(self):
        self.setWindowOpacity(0.0)
        self._win_anim = QPropertyAnimation(self, b"windowOpacity")
        self._win_anim.setDuration(280)
        self._win_anim.setStartValue(0.0)
        self._win_anim.setEndValue(1.0)
        self._win_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._win_anim.start()
