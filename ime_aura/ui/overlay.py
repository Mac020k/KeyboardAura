"""Fullscreen edge-gradient overlay driven by IME state."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import QApplication, QWidget

from ime_aura.platform.base import PlatformBackend
from ime_aura.settings import default_colors, load_colors, save_colors


class ImeOverlay(QWidget):
    def __init__(self, backend: PlatformBackend):
        super().__init__()
        self._backend = backend

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowTransparentForInput
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        colors = load_colors()
        self.color_jp = colors.color_jp
        self.color_en = colors.color_en

        self.is_japanese = self._backend.is_japanese_input()

        app = QApplication.instance()
        geo = self._backend.get_active_screen_geometry(app) if app else None
        if geo:
            self.setGeometry(geo)
        elif app and app.primaryScreen():
            self.setGeometry(app.primaryScreen().geometry())

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_state)
        self.timer.start(100)

    def set_color_jp(self, color: QColor) -> None:
        self.color_jp = color
        self._persist_colors()
        self.update()

    def set_color_en(self, color: QColor) -> None:
        self.color_en = color
        self._persist_colors()
        self.update()

    def reset_colors_to_default(self) -> None:
        colors = default_colors()
        self.color_jp = colors.color_jp
        self.color_en = colors.color_en
        self._persist_colors()
        self.update()

    def _persist_colors(self) -> None:
        save_colors(self.color_jp, self.color_en)

    def check_state(self) -> None:
        app = QApplication.instance()
        if app is None:
            return

        new_state = self._backend.is_japanese_input()
        state_changed = new_state != self.is_japanese
        if state_changed:
            self.is_japanese = new_state

        target_geo = self._backend.get_active_screen_geometry(app)
        geo_changed = False
        if target_geo and target_geo != self.geometry():
            self.setGeometry(target_geo)
            geo_changed = True

        if state_changed or geo_changed:
            self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        base_color = self.color_jp if self.is_japanese else self.color_en
        transparent = QColor(0, 0, 0, 0)

        width = self.width()
        height = self.height()
        thickness = 15

        grad_top = QLinearGradient(0, 0, 0, thickness)
        grad_top.setColorAt(0, base_color)
        grad_top.setColorAt(1, transparent)
        painter.fillRect(0, 0, width, thickness, grad_top)

        grad_bottom = QLinearGradient(0, height, 0, height - thickness)
        grad_bottom.setColorAt(0, base_color)
        grad_bottom.setColorAt(1, transparent)
        painter.fillRect(0, height - thickness, width, thickness, grad_bottom)

        grad_left = QLinearGradient(0, 0, thickness, 0)
        grad_left.setColorAt(0, base_color)
        grad_left.setColorAt(1, transparent)
        painter.fillRect(0, 0, thickness, height, grad_left)

        grad_right = QLinearGradient(width, 0, width - thickness, 0)
        grad_right.setColorAt(0, base_color)
        grad_right.setColorAt(1, transparent)
        painter.fillRect(width - thickness, 0, thickness, height, grad_right)
