"""Control window for color customization and quitting."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QButtonGroup,
    QCheckBox,
    QColorDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ime_aura.settings import (
    DEFAULT_GRADIENT_WIDTH,
    DISPLAY_MODE_ALWAYS,
    DISPLAY_MODE_ON_FOCUS,
    GRADIENT_WIDTH_MAX,
    GRADIENT_WIDTH_MIN,
    UI_FONT_SIZE_LARGE,
    UI_FONT_SIZE_MEDIUM,
    UI_FONT_SIZE_SMALL,
    ui_font_point_size,
)
from ime_aura.ui.overlay import ImeOverlay


class ControlWindow(QWidget):
    def __init__(self, overlay: ImeOverlay):
        super().__init__()
        self.overlay = overlay
        self.setWindowTitle("IME Aura")

        layout = QVBoxLayout()

        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("文字サイズ:"))
        self.radio_font_small = QRadioButton("小")
        self.radio_font_medium = QRadioButton("中")
        self.radio_font_large = QRadioButton("大")
        self.font_group = QButtonGroup(self)
        self.font_group.addButton(self.radio_font_small)
        self.font_group.addButton(self.radio_font_medium)
        self.font_group.addButton(self.radio_font_large)
        font_layout.addWidget(self.radio_font_small)
        font_layout.addWidget(self.radio_font_medium)
        font_layout.addWidget(self.radio_font_large)
        font_layout.addStretch(1)
        layout.addLayout(font_layout)

        jp_layout = QHBoxLayout()
        jp_label = QLabel("日本語入力時の色:")
        self.jp_btn = QPushButton()
        self.update_btn_color(self.jp_btn, self.overlay.color_jp)
        self.jp_btn.clicked.connect(self.choose_jp_color)
        jp_layout.addWidget(jp_label)
        jp_layout.addWidget(self.jp_btn)
        layout.addLayout(jp_layout)

        en_layout = QHBoxLayout()
        en_label = QLabel("英語入力時の色:")
        self.en_btn = QPushButton()
        self.update_btn_color(self.en_btn, self.overlay.color_en)
        self.en_btn.clicked.connect(self.choose_en_color)
        en_layout.addWidget(en_label)
        en_layout.addWidget(self.en_btn)
        layout.addLayout(en_layout)

        reset_btn = QPushButton("デフォルトの色に戻す")
        reset_btn.clicked.connect(self.reset_colors)
        layout.addWidget(reset_btn)

        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("グラデーションの幅:"))
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(GRADIENT_WIDTH_MIN, GRADIENT_WIDTH_MAX)
        self.width_slider.setMinimumWidth(120)
        self.width_slider.setValue(self.overlay.gradient_width)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(GRADIENT_WIDTH_MIN, GRADIENT_WIDTH_MAX)
        self.width_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.width_spin.setSuffix(" px")
        self.width_spin.setValue(self.overlay.gradient_width)
        width_layout.addWidget(self.width_slider, stretch=1)
        width_layout.addWidget(self.width_spin)
        layout.addLayout(width_layout)

        reset_width_btn = QPushButton("デフォルトの幅に戻す")
        reset_width_btn.clicked.connect(self.reset_gradient_width)
        layout.addWidget(reset_width_btn)

        layout.addWidget(QLabel("グラデーション表示:"))

        self.radio_always = QRadioButton("常に表示")
        self.radio_on_focus = QRadioButton("テキスト入力時のみ")
        self.display_group = QButtonGroup(self)
        self.display_group.addButton(self.radio_always)
        self.display_group.addButton(self.radio_on_focus)
        layout.addWidget(self.radio_always)
        layout.addWidget(self.radio_on_focus)

        self.hover_check = QCheckBox("ホバー時も表示")
        hover_layout = QHBoxLayout()
        hover_layout.setContentsMargins(24, 0, 0, 0)
        hover_layout.addWidget(self.hover_check)
        layout.addLayout(hover_layout)

        if self.overlay.display_mode == DISPLAY_MODE_ON_FOCUS:
            self.radio_on_focus.setChecked(True)
        else:
            self.radio_always.setChecked(True)
        self.hover_check.setChecked(self.overlay.show_on_hover)
        self._sync_hover_enabled()

        font_size = self.overlay.ui_font_size
        if font_size == UI_FONT_SIZE_SMALL:
            self.radio_font_small.setChecked(True)
        elif font_size == UI_FONT_SIZE_LARGE:
            self.radio_font_large.setChecked(True)
        else:
            self.radio_font_medium.setChecked(True)

        self.radio_always.toggled.connect(self._on_display_mode_changed)
        self.radio_on_focus.toggled.connect(self._on_display_mode_changed)
        self.hover_check.toggled.connect(self._on_hover_toggled)
        self.radio_font_small.toggled.connect(self._on_font_size_changed)
        self.radio_font_medium.toggled.connect(self._on_font_size_changed)
        self.radio_font_large.toggled.connect(self._on_font_size_changed)
        self.width_slider.valueChanged.connect(self._on_width_slider_changed)
        self.width_spin.valueChanged.connect(self._on_width_spin_changed)

        exit_btn = QPushButton("アプリケーションを終了")
        exit_btn.clicked.connect(QApplication.quit)
        layout.addWidget(exit_btn)

        self.setLayout(layout)
        self._apply_ui_font_size(self.overlay.ui_font_size)

    def _apply_ui_font_size(self, size_key: str) -> None:
        font = QFont(self.font())
        font.setPointSize(ui_font_point_size(size_key))
        self.setFont(font)
        for widget in self.findChildren(QWidget):
            widget.setFont(font)

        # Preview labels: each option always shows the size it would apply.
        for radio, key in (
            (self.radio_font_small, UI_FONT_SIZE_SMALL),
            (self.radio_font_medium, UI_FONT_SIZE_MEDIUM),
            (self.radio_font_large, UI_FONT_SIZE_LARGE),
        ):
            preview = QFont(font)
            preview.setPointSize(ui_font_point_size(key))
            radio.setFont(preview)

        self.adjustSize()

    def _on_font_size_changed(self, checked: bool) -> None:
        if not checked:
            return
        if self.radio_font_small.isChecked():
            size_key = UI_FONT_SIZE_SMALL
        elif self.radio_font_large.isChecked():
            size_key = UI_FONT_SIZE_LARGE
        else:
            size_key = UI_FONT_SIZE_MEDIUM
        self.overlay.set_ui_font_size(size_key)
        self._apply_ui_font_size(size_key)

    def _set_width_controls(self, value: int) -> None:
        self.width_slider.blockSignals(True)
        self.width_spin.blockSignals(True)
        self.width_slider.setValue(value)
        self.width_spin.setValue(value)
        self.width_slider.blockSignals(False)
        self.width_spin.blockSignals(False)

    def _on_width_slider_changed(self, value: int) -> None:
        self.width_spin.blockSignals(True)
        self.width_spin.setValue(value)
        self.width_spin.blockSignals(False)
        self.overlay.set_gradient_width(value)

    def _on_width_spin_changed(self, value: int) -> None:
        self.width_slider.blockSignals(True)
        self.width_slider.setValue(value)
        self.width_slider.blockSignals(False)
        self.overlay.set_gradient_width(value)

    def reset_gradient_width(self) -> None:
        self.overlay.set_gradient_width(DEFAULT_GRADIENT_WIDTH)
        self._set_width_controls(self.overlay.gradient_width)

    def _sync_hover_enabled(self) -> None:
        enabled = self.radio_on_focus.isChecked()
        self.hover_check.setEnabled(enabled)
        if not enabled:
            self.hover_check.blockSignals(True)
            self.hover_check.setChecked(False)
            self.hover_check.blockSignals(False)

    def _on_display_mode_changed(self, checked: bool) -> None:
        if not checked:
            return
        if self.radio_always.isChecked():
            self.overlay.set_display_mode(DISPLAY_MODE_ALWAYS)
        else:
            self.overlay.set_display_mode(DISPLAY_MODE_ON_FOCUS)
        self._sync_hover_enabled()
        if self.radio_on_focus.isChecked():
            self.overlay.set_show_on_hover(self.hover_check.isChecked())

    def _on_hover_toggled(self, checked: bool) -> None:
        self.overlay.set_show_on_hover(checked)

    def update_btn_color(self, btn: QPushButton, color: QColor) -> None:
        btn.setStyleSheet(
            f"background-color: rgba({color.red()}, {color.green()}, "
            f"{color.blue()}, {color.alpha()}); border: 1px solid #ccc;"
        )

    def choose_jp_color(self) -> None:
        color = QColorDialog.getColor(
            self.overlay.color_jp,
            self,
            "日本語入力時の色を選択",
            QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if color.isValid():
            self.overlay.set_color_jp(color)
            self.update_btn_color(self.jp_btn, color)

    def choose_en_color(self) -> None:
        color = QColorDialog.getColor(
            self.overlay.color_en,
            self,
            "英語入力時の色を選択",
            QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if color.isValid():
            self.overlay.set_color_en(color)
            self.update_btn_color(self.en_btn, color)

    def reset_colors(self) -> None:
        self.overlay.reset_colors_to_default()
        self.update_btn_color(self.jp_btn, self.overlay.color_jp)
        self.update_btn_color(self.en_btn, self.overlay.color_en)

    def closeEvent(self, event) -> None:
        QApplication.quit()
        event.accept()
