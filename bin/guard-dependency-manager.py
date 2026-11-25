#!/usr/bin/env python3
"""Enforces the dependency manager this repo declares (python-tooling rules 1-4). PreToolUse: Bash"""
import os
import re

from lib.util import read_payload, project_dir, segments, block, ask, allow

p = read_payload()
if p.get('tool_name') != 'Bash':
    allow()
root = project_dir(p)


def read(f):
    try:
        with open(os.path.join(root, f), encoding='utf-8') as fh:
            return fh.read()
    except OSError:
        return ''


def has(*names):
    return any(os.path.exists(os.path.join(root, f)) for f in names)


def declared():
    """Declared by the repo itself: a lockfile or a tool table wins over a bare requirements file."""
    pyproject = read('pyproject.toml')
    if has('uv.lock') or re.search(r'^\[tool\.uv\]', pyproject, re.M):
        return 'uv'
    if has('poetry.lock') or re.search(r'^\[tool\.poetry\]', pyproject, re.M):
        return 'poetry'
    if has('Pipfile', 'Pipfile.lock'):
        return 'pipenv'
    if has('requirements.txt', 'requirements-dev.txt', 'requirements.in'):
        return 'pip'
    return None


pm = declared()
PIP = re.compile(r'^(?:sudo\s+)?(?:(?:\S*/)?python[\d.]*\s+-m\s+)?(?:\S*/)?pip[\d.]*\s+install\b')
INSTALLERS = {
    'pip': PIP,
    'uv': re.compile(r'^uv\s+(pip\s+(install|sync)|add|sync)\b'),
    'poetry': re.compile(r'^poetry\s+(add|install)\b'),
    'pipenv': re.compile(r'^pipenv\s+(install|sync)\b'),
}

# pip installs into whatever interpreter it belongs to, so it only counts as safe inside a venv:
# an active one in this process, or one the command itself activates or points at.
raw = str((p.get('tool_input') or {}).get('command') or '')
in_venv = (bool(os.environ.get('VIRTUAL_ENV'))
           or bool(re.search(r'(^|[\s/])\.?(venv|env)/(bin|Scripts)/', raw))
           or bool(re.search(r'\bactivate\b', raw)))

for c in segments(raw):
    if pm:
        for other, rx in INSTALLERS.items():
            if other != pm and rx.search(c):
                block('py-tooling-1', f'"{c}" uses {other}, but this repo declares {pm}.',
                      f'use {pm} — see the command map in CLAUDE.md')

    if re.search(r'--break-system-packages|--ignore-requires-python', c) and re.search(r'\b(pip[\d.]*|uv)\b', c):
        block('py-tooling-2', f'"{c}" forces past the interpreter\'s own protection.',
              'install into the project venv, or ask a human')
    if PIP.search(c) and not in_venv:
        block('py-tooling-2', f'"{c}" would install into whichever Python is first on PATH, not the project venv.',
              'use the venv explicitly (.venv/bin/pip install ...) or activate it first; if there is no venv, ask a human')
    if re.search(r'\b(rm|del|unlink)\b.*(requirements[\w.-]*\.(txt|in)|uv\.lock|poetry\.lock|Pipfile(\.lock)?|pdm\.lock)', c):
        block('py-tooling-3', 'deleting a dependency declaration or lockfile.',
              'never delete it — fix the dependency instead')

    # a new runtime dependency is a decision (rule C2), not a side effect
    adds_package = (
        (PIP.search(c) and re.search(r'\binstall\s+(?!-)', c)
         and not re.search(r'\s-(r|e|c)\b|--(requirement|editable|constraint)\b', c)
         and not re.search(r'\binstall\s+(-\S+\s+)*(\.|pip|setuptools|wheel)(\s|$)', c))
        or (re.search(r'^uv\s+add\s+[^-\s]', c) and not re.search(r'(--dev|-d\b|--group\b|--optional)', c))
        or (re.search(r'^poetry\s+add\s+[^-\s]', c) and not re.search(r'(-D\b|--dev|--group\b)', c))
        or (re.search(r'^pipenv\s+install\s+[^-\s]', c) and not re.search(r'--dev\b', c))
    )
    if adds_package:
        ask(f'Adding a runtime dependency (rule C2): "{c}". Confirm it is needed, pin it, and justify size/licence/maintenance in the PR.')
allow()
