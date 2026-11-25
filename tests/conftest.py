"""Shared setup for the plugin's own tests.

The hooks are plain scripts run by `python3 bin/<name>.py`, so the tests drive them the same way
(a subprocess fed a JSON payload on stdin). `bin/` goes on sys.path only so a test can import
`lib.util` and call a helper directly.
"""
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN / 'bin'))
