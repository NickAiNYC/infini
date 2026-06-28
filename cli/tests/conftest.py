"""Pytest configuration — add src/ to path so tests can import infini."""
import sys
from pathlib import Path

src = Path(__file__).parent.parent / "src"
if str(src) not in sys.path:
    sys.path.insert(0, str(src))
