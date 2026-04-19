from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QComboBox, QPushButton, QLineEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath
import config


class ColorSwatch(QWidget):
    """Animated circular color swatch button."""
    selected = pyqtSignal(str)  # emits accent key name

    def __init__(self, key: str, color: str, parent=None):
        super().__init__(parent)
        self._key = key
        self._color = color
        self._active = False
        self._hover_t = 0.0
        self.setFixedSize(28, 28)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._anim = QPropertyAnimation(self, b"hover_t")
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def get_hover_t(self): return self._hover_t
    def set_hover_t(self, v):
        self._hover_t = max(0.0, min(1.0, v))
        self.update()
    hover_t = pyqtProperty(float, fget=get_hover_t, fset=set_hover_t)

    def set_active(self, active: bool):
        self._active = active
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = self.rect().center()
        r = 10

        if self._active:
            ring = QColor(self._color)
            ring.setAlpha(180)
            p.setPen(QPen(ring, 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(c, 13, 13)

        scale = 1.0 + 0.15 * self._hover_t
        scaled_r = int(r * scale)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(self._color)))
        p.drawEllipse(c, scaled_r, scaled_r)

    def enterEvent(self, e):
        self._anim.stop()
        self._anim.setStartValue(self._hover_t)
        self._anim.setEndValue(1.0)
        self._anim.start()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._anim.stop()
        self._anim.setStartValue(self._hover_t)
        self._anim.setEndValue(0.0)
        self._anim.start()
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.selected.emit(self._key)
        super().mousePressEvent(e)


class ToggleSwitch(QWidget):
    """Animated toggle switch."""
    toggled = pyqtSignal(bool)

    def __init__(self, checked: bool = False, parent=None):
        super().__init__(parent)
        self._on = checked
        self._t = 1.0 if checked else 0.0
        self.setFixedSize(44, 24)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._anim = QPropertyAnimation(self, b"toggle_t")
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def get_toggle_t(self): return self._t
    def set_toggle_t(self, v):
        self._t = max(0.0, min(1.0, v))
        self.update()
    toggle_t = pyqtProperty(float, fget=get_toggle_t, fset=set_toggle_t)

    def is_checked(self): return self._on

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        t = self._t
        accent = config.ACCENT_COLORS.get(config.ACCENT, "#4a78ff")
        track_off = "#263248" if config.THEME == "dark" else "#c8d0e0"

        def lerp_c(c1, c2, t):
            def h(s): return [int(s.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
            r1,g1,b1 = h(c1); r2,g2,b2 = h(c2)
            return QColor(int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))

        track_color = lerp_c(track_off, accent, t)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(track_color))
        p.drawRoundedRect(0, 4, 44, 16, 8, 8)

        thumb_x = int(4 + (44 - 24) * t)
        p.setBrush(QBrush(QColor("white")))
        p.drawEllipse(thumb_x, 2, 20, 20)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._on = not self._on
            self._anim.stop()
            self._anim.setStartValue(self._t)
            self._anim.setEndValue(1.0 if self._on else 0.0)
            self._anim.start()
            self.toggled.emit(self._on)
        super().mousePressEvent(e)


def _divider() -> QFrame:
    f = QFrame()
    f.setObjectName("divider")
    f.setFixedHeight(1)
    return f


def _row(label: str, hint: str, widget: QWidget) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(16)
    left = QVBoxLayout()
    left.setSpacing(2)
    lbl = QLabel(label)
    lbl.setObjectName("settingName")
    left.addWidget(lbl)
    if hint:
        h = QLabel(hint)
        h.setObjectName("settingHint")
        left.addWidget(h)
    row.addLayout(left)
    row.addStretch()
    row.addWidget(widget)
    return row


class SettingsPage(QWidget):
    theme_changed = pyqtSignal(str)
    accent_changed = pyqtSignal(str)
    animations_changed = pyqtSignal(bool)
    vt_key_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsPage")
        self._swatches: dict[str, ColorSwatch] = {}
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 40)
        root.setSpacing(0)

        title = QLabel("Settings")
        title.setObjectName("pageTitle")
        root.addWidget(title)
        sub = QLabel("Customize the app to your liking")
        sub.setObjectName("pageSubtitle")
        sub.setContentsMargins(0, 6, 0, 32)
        root.addWidget(sub)

        # ── Appearance card ────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("panel")
        cv = QVBoxLayout(card)
        cv.setContentsMargins(24, 20, 24, 20)
        cv.setSpacing(18)

        section_lbl = QLabel("APPEARANCE")
        section_lbl.setObjectName("sectionLabel")
        cv.addWidget(section_lbl)
        cv.addWidget(_divider())

        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light", "system"])
        current = config.get_setting("theme_choice", "system")
        self.theme_combo.setCurrentText(current)
        self.theme_combo.currentTextChanged.connect(self._on_theme)
        cv.addLayout(_row("Theme", "Light or dark interface", self.theme_combo))

        cv.addWidget(_divider())

        # Accent color
        swatch_row = QHBoxLayout()
        swatch_row.setSpacing(10)
        current_accent = config.ACCENT
        for key, color in config.ACCENT_COLORS.items():
            sw = ColorSwatch(key, color)
            sw.set_active(key == current_accent)
            sw.selected.connect(self._on_accent)
            swatch_row.addWidget(sw)
            self._swatches[key] = sw
        swatch_row.addStretch()

        swatch_widget = QWidget()
        swatch_widget.setStyleSheet("background: transparent;")
        swatch_widget.setLayout(swatch_row)
        cv.addLayout(_row("Accent color", "Color used for buttons and highlights", swatch_widget))

        cv.addWidget(_divider())

        # Animations
        self.anim_toggle = ToggleSwitch(checked=config.ANIMATIONS)
        self.anim_toggle.toggled.connect(self._on_animations)
        cv.addLayout(_row("Animations", "Smooth page transitions and hover effects", self.anim_toggle))

        root.addWidget(card)
        root.addSpacing(16)

        # ── Analysis card ──────────────────────────────────────────────
        card2 = QFrame()
        card2.setObjectName("panel")
        cv2 = QVBoxLayout(card2)
        cv2.setContentsMargins(24, 20, 24, 20)
        cv2.setSpacing(18)

        s2 = QLabel("ANALYSIS")
        s2.setObjectName("sectionLabel")
        cv2.addWidget(s2)
        cv2.addWidget(_divider())

        model_combo = QComboBox()
        model_combo.addItems(["gpt-3.5-turbo", "gpt-4", "gpt-4o"])
        model_combo.setCurrentText(config.MODEL_NAME)
        cv2.addLayout(_row("Model", "OpenAI model used for analysis", model_combo))

        cv2.addWidget(_divider())

        demo_toggle = ToggleSwitch(checked=config.DEMO_MODE)
        cv2.addLayout(_row("Demo mode", "Run without an API key (simulated results)", demo_toggle))

        root.addWidget(card2)
        root.addSpacing(16)

        # ── API Keys card ──────────────────────────────────────────────
        card3 = QFrame()
        card3.setObjectName("panel")
        cv3 = QVBoxLayout(card3)
        cv3.setContentsMargins(24, 20, 24, 20)
        cv3.setSpacing(18)

        s3 = QLabel("API KEYS")
        s3.setObjectName("sectionLabel")
        cv3.addWidget(s3)
        cv3.addWidget(_divider())

        vt_row = QHBoxLayout()
        vt_row.setSpacing(8)
        vt_left = QVBoxLayout()
        vt_left.setSpacing(2)
        vt_lbl = QLabel("VirusTotal API Key")
        vt_lbl.setObjectName("settingName")
        vt_left.addWidget(vt_lbl)
        vt_hint = QLabel("Used by File Detector and URL Scanner — free key at virustotal.com")
        vt_hint.setObjectName("settingHint")
        vt_left.addWidget(vt_hint)
        vt_row.addLayout(vt_left)
        vt_row.addSpacing(16)

        self._vt_input = QLineEdit()
        self._vt_input.setObjectName("apiKeyInput")
        self._vt_input.setPlaceholderText("Paste your VT API key here")
        self._vt_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._vt_input.setFixedWidth(240)
        self._vt_input.setFixedHeight(34)
        stored = config.get_setting("vt_api_key", config.VT_API_KEY)
        if stored:
            self._vt_input.setText(stored)
        vt_row.addWidget(self._vt_input)

        save_vt = QPushButton("Save")
        save_vt.setObjectName("secondaryBtn")
        save_vt.setFixedHeight(34)
        save_vt.clicked.connect(self._save_vt_key)
        vt_row.addWidget(save_vt)

        cv3.addLayout(vt_row)
        root.addWidget(card3)
        root.addStretch()

    def _on_theme(self, choice: str):
        if choice == "system":
            theme = config.SYSTEM_THEME
        else:
            theme = choice
        config.THEME = theme
        config.set_setting("theme", theme)
        config.set_setting("theme_choice", choice)
        self.theme_changed.emit(theme)

    def _on_accent(self, key: str):
        for k, sw in self._swatches.items():
            sw.set_active(k == key)
        config.ACCENT = key
        config.set_setting("accent", key)
        self.accent_changed.emit(key)

    def _on_animations(self, enabled: bool):
        config.ANIMATIONS = enabled
        config.set_setting("animations", enabled)
        self.animations_changed.emit(enabled)

    def _save_vt_key(self):
        key = self._vt_input.text().strip()
        config.set_setting("vt_api_key", key)
        config.VT_API_KEY = key
        self.vt_key_changed.emit(key)
