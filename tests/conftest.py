import os
import sys


def pytest_sessionstart(session):
    # Ensure src is importable when running tests from repo root
    root = os.path.dirname(os.path.dirname(__file__))
    src = os.path.join(root, "src")
    if src not in sys.path:
        sys.path.insert(0, src)


