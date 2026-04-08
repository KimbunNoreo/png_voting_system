"""Printer service settings."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PrinterSettings:
    default_printer_name: str = "securevote-vvpat"
    paper_size: str = "A6"
    secure_qr_required: bool = True
