"""About dialog with license and third-party notices."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QTextBrowser,
    QVBoxLayout,
)

from ime_aura import __version__
from ime_aura.resources import resource_path


def _read_text(relative_path: str) -> str:
    path = resource_path(relative_path)
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return f"（{relative_path} を読み込めませんでした）"


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IME Aura について")
        self.setMinimumSize(480, 420)

        layout = QVBoxLayout(self)

        summary = QLabel(
            f"<b>IME Aura</b> {__version__}<br>"
            "Copyright (c) 2026 Mac020k<br><br>"
            "本ソフトウェアは MIT License のもとで提供されています。<br>"
            "GUI には PySide6 / Qt（LGPL-3.0 / GPL-2.0 / GPL-3.0）を利用しています。"
        )
        summary.setTextFormat(Qt.TextFormat.RichText)
        summary.setWordWrap(True)
        layout.addWidget(summary)

        notices = QTextBrowser()
        notices.setOpenExternalLinks(True)
        notices.setPlainText(
            "--- LICENSE ---\n\n"
            + _read_text("LICENSE")
            + "\n\n--- THIRD_PARTY_NOTICES ---\n\n"
            + _read_text("THIRD_PARTY_NOTICES.md")
        )
        layout.addWidget(notices, stretch=1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)
