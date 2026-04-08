"""Physical tamper sensor abstraction."""

from __future__ import annotations


class TamperSensor:
    def __init__(self, tampered: bool = False) -> None:
        self.tampered = tampered

    def is_tampered(self) -> bool:
        return self.tampered
