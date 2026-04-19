from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath
import config


def _lerp_color(c1: str, c2: str, t: float) -> QColor:
    def h(s): return [int(s.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
    r1, g1, b1 = h(c1)
    r2, g2, b2 = h(c2)
    return QColor(
        max(0, min(255, int(r1 + (r2 - r1) * t))),
        max(0, min(255, int(g1 + (g2 - g1) * t))),
        max(0, min(255, int(b1 + (b2 - b1) * t))),
    )


class ToolCard(QWidget):
    clicked = pyqtSignal()

    def __init__(self, icon: str, title: str, desc: str, accent: str = "#4a78ff", parent=None):
        super().__init__(parent)
        self._hover_t = 0.0
        self._accent = accent

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(260, 155)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._anim = QPropertyAnimation(self, b"hover_t")
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        icon_lbl = QLabel(icon)
        icon_lbl.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        icon_lbl.setStyleSheet("background: transparent; border: none; font-size: 26px;")
        icon_lbl.setFixedHeight(34)
        layout.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        title_lbl.setStyleSheet(
            "background: transparent; border: none; "
            "font-size: 14px; font-weight: 600; color: #dde4f0;"
        )
        layout.addWidget(title_lbl)

        desc_lbl = QLabel(desc)
        desc_lbl.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        desc_lbl.setStyleSheet(
            "background: transparent; border: none; "
            "font-size: 11px; color: #546480; line-height: 1.4;"
        )
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)
        layout.addStretch()

        badge = QLabel("Available")
        badge.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        badge.setStyleSheet(
            f"background: transparent; border: none; "
            f"font-size: 9px; font-weight: 700; color: {accent}; letter-spacing: 0.5px;"
        )
        self._badge = badge
        layout.addWidget(badge)

    def get_hover_t(self) -> float:
        return self._hover_t

    def set_hover_t(self, value: float):
        self._hover_t = max(0.0, min(1.0, value))
        self.update()

    hover_t = pyqtProperty(float, fget=get_hover_t, fset=set_hover_t)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        t = self._hover_t
        theme = config.THEME
        if theme == "dark":
            bg_base, bg_hover = "#151d2e", "#1b2640"
            bd_base = "#1f2d45"
        else:
            bg_base, bg_hover = "#ffffff", "#f4f7ff"
            bd_base = "#d5dce8"

        bg = _lerp_color(bg_base, bg_hover, t)
        border = _lerp_color(bd_base, self._accent, t)

        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(float(rect.x()), float(rect.y()), float(rect.width()), float(rect.height()), 12.0, 12.0)
        p.setPen(QPen(border, 1.5))
        p.setBrush(QBrush(bg))
        p.drawPath(path)

    def enterEvent(self, event):
        self._anim.stop()
        self._anim.setStartValue(self._hover_t)
        self._anim.setEndValue(1.0)
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._anim.stop()
        self._anim.setStartValue(self._hover_t)
        self._anim.setEndValue(0.0)
        self._anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class HomePage(QWidget):
    open_tool = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("homePage")
        self._cards = []
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(48, 40, 48, 40)
        outer.setSpacing(0)

        title = QLabel("Security Tools")
        title.setObjectName("pageTitle")
        outer.addWidget(title)

        sub = QLabel("Choose a tool to get started")
        sub.setObjectName("pageSubtitle")
        sub.setContentsMargins(0, 6, 0, 36)
        outer.addWidget(sub)

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setContentsMargins(0, 0, 0, 0)

        tools = [
            ("🎣", "Phishing Detector", "Analyze suspicious emails for phishing indicators", "phishing"),
            ("📁", "File Detector",     "Scan files with VirusTotal for malware",            "file"),
            ("🔗", "URL Scanner",       "Check links against VirusTotal + heuristics",       "url"),
            ("📞", "Scam Caller ID",    "Identify scam phone numbers and tactics",           "caller"),
        ]

        accent = config.ACCENT_COLORS.get(config.ACCENT, config.ACCENT_COLORS["blue"])

        for i, (icon, name, desc, key) in enumerate(tools):
            card = ToolCard(icon, name, desc, accent=accent)
            card.clicked.connect(lambda k=key: self.open_tool.emit(k))
            grid.addWidget(card, i // 2, i % 2)
            self._cards.append(card)

        outer.addLayout(grid)
        outer.addStretch()

    def refresh_accent(self):
        accent = config.ACCENT_COLORS.get(config.ACCENT, config.ACCENT_COLORS["blue"])
        for card in self._cards:
            card._accent = accent
            card._badge.setStyleSheet(
                f"background: transparent; border: none; "
                f"font-size: 9px; font-weight: 700; color: {accent}; letter-spacing: 0.5px;"
            )
            card.update()
