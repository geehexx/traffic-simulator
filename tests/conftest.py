"""Tests for conftest."""

from __future__ import annotations


"""Tests for conftest."""


import pytest

import os
import sys


def pytest_sessionstart(session):
    # Ensure src is importable when running tests from repo root
    root = os.path.dirname(os.path.dirname(__file__))
    src = os.path.join(root, "src")
    if src not in sys.path:
        sys.path.insert(0, src)


if __name__ == "__main__":
    pytest.main([__file__])
