#!/usr/bin/env python3
"""Mechanical formatting of the changed Python file (python-tooling rule 6). PostToolUse: Edit|Write|MultiEdit

Opt-in on purpose: it runs only when the repo declares ruff as its formatter, because reformatting a
file nobody ever formatted turns a one-line fix into a whole-file diff (rule C1).
"""
import os
import re
import subprocess

from lib.util import read_payload, project_dir, allow

p = read_payload()
root = project_dir(p)
file = (p.get('tool_input') or {}).get('file_path')
if not file:
    allow()

rel = os.path.relpath(os.path.abspath(os.path.join(root, file)), root).replace(os.sep, '/')
if rel.startswith('..') or os.path.splitext(rel)[1] != '.py':
    allow()
if re.search(r'(^|/)(\.venv|venv|env|node_modules|dist|build|\.tox|__pycache__|__generated__)/', rel):
    allow()


def read(f):
    try:
        with open(os.path.join(root, f), encoding='utf-8') as fh:
            return fh.read()
    except OSError:
        return ''


declares_formatter = (re.search(r'^\[format\]', read('ruff.toml'), re.M) or re.search(r'^\[format\]', read('.ruff.toml'), re.M)
                      or re.search(r'^\[tool\.ruff\.format\]', read('pyproject.toml'), re.M))
if not declares_formatter:
    allow()

local = next((f for f in ('.venv/bin/ruff', 'venv/bin/ruff', '.venv/Scripts/ruff.exe') if os.path.exists(os.path.join(root, f))), None)
try:
    subprocess.run([os.path.join(root, local) if local else 'ruff', 'format', '--quiet', rel],
                   cwd=root, capture_output=True, text=True, timeout=20)
except (OSError, subprocess.SubprocessError):
    pass

allow()  # formatting never blocks, and a missing ruff is not an error
