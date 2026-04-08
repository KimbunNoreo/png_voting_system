"""Physical lock circuit abstraction."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DeviceLockCircuit:
    engaged: bool = False

    def engage(self) -> None:
        self.engaged = True
