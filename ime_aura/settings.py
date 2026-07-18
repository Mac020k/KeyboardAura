"""Persistent color settings for IME Aura."""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import dataclass

from PySide6.QtGui import QColor

logger = logging.getLogger(__name__)

DEFAULT_COLOR_JP = QColor(248, 40, 70, 255)
DEFAULT_COLOR_EN = QColor(45, 129, 253, 255)


@dataclass
class ColorSettings:
    color_jp: QColor
    color_en: QColor


def default_colors() -> ColorSettings:
    return ColorSettings(
        color_jp=QColor(DEFAULT_COLOR_JP),
        color_en=QColor(DEFAULT_COLOR_EN),
    )


def config_dir() -> str:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, "IMEAura")
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/IMEAura")
    xdg = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(xdg, "ime_aura")


def settings_path() -> str:
    return os.path.join(config_dir(), "settings.json")


def _color_to_list(color: QColor) -> list[int]:
    return [color.red(), color.green(), color.blue(), color.alpha()]


def _color_from_list(values: object, fallback: QColor) -> QColor:
    if not isinstance(values, (list, tuple)) or len(values) != 4:
        return QColor(fallback)
    try:
        r, g, b, a = (int(v) for v in values)
    except (TypeError, ValueError):
        return QColor(fallback)
    if not all(0 <= v <= 255 for v in (r, g, b, a)):
        return QColor(fallback)
    return QColor(r, g, b, a)


def load_colors() -> ColorSettings:
    path = settings_path()
    defaults = default_colors()
    if not os.path.isfile(path):
        return defaults

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Failed to load settings from %s: %s", path, exc)
        return defaults

    if not isinstance(data, dict):
        return defaults

    return ColorSettings(
        color_jp=_color_from_list(data.get("color_jp"), defaults.color_jp),
        color_en=_color_from_list(data.get("color_en"), defaults.color_en),
    )


def save_colors(color_jp: QColor, color_en: QColor) -> None:
    path = settings_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        payload = {
            "color_jp": _color_to_list(color_jp),
            "color_en": _color_to_list(color_en),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
    except OSError as exc:
        logger.warning("Failed to save settings to %s: %s", path, exc)
