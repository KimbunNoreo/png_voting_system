"""Test package configuration for unittest discovery."""

from __future__ import annotations

import unittest


def load_tests(loader: unittest.TestLoader, standard_tests: unittest.TestSuite, pattern: str) -> unittest.TestSuite:
    """Enable recursive discovery when running ``python -m unittest`` from repo root."""

    return loader.discover("tests", pattern=pattern or "test*.py")
