"""Hardware tamper detection helpers."""

from __future__ import annotations


def detect_tamper(sensor_triggered: bool, enclosure_open: bool) -> bool:
    return sensor_triggered or enclosure_open
