#!/usr/bin/env python3
"""Mechanical formatting of the changed file, by extension. PostToolUse: Edit|Write|MultiEdit

Python goes to ruff, TypeScript to prettier or biome. Opt-in on purpose: a formatter runs only when the repo
declares it, because reformatting a file nobody ever formatted turns a one-line fix into a whole-file diff
(rule C1).
"""
import json
import os
import re
import subprocess

from lib.util import read_payload, project_dir, allow

TS_EXTENSIONS = ('.ts', '.tsx', '.mts', '.cts')
PRETTIER_CONFIG = re.compile(r'\.prettierrc(\.(json5?|ya?ml|toml|[cm]?[jt]s))?|prettier\.config\.[cm]?[jt]s')
# a JSONC comment, or a string that merely looks like it holds one
_JSONC = re.compile(r'("(?:\\.|[^"\\])*")|//[^\n]*|/\*.*?\*/', re.S)

p = read_payload()
root = project_dir(p)
file = (p.get('tool_input') or {}).get('file_path')
if not file:
    allow()

rel = os.path.relpath(os.path.abspath(os.path.join(root, file)), root).replace(os.sep, '/')
ext = os.path.splitext(rel)[1]
if rel.startswith('..') or ext not in ('.py',) + TS_EXTENSIONS:
    allow()
if re.search(r'(^|/)(\.venv|venv|env|node_modules|dist|build|\.tox|__pycache__|__generated__)/', rel):
    allow()


def read(*parts):
    try:
        with open(os.path.join(root, *parts), encoding='utf-8-sig') as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return ''


def run(command, cwd):
    try:
        subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        pass


def ruff():
    if not (re.search(r'^\[format\]', read('ruff.toml'), re.M) or re.search(r'^\[format\]', read('.ruff.toml'), re.M)
            or re.search(r'^\[tool\.ruff\.format\]', read('pyproject.toml'), re.M)):
        return
    local = next((f for f in ('.venv/bin/ruff', 'venv/bin/ruff', '.venv/Scripts/ruff.exe') if os.path.exists(os.path.join(root, f))), None)
    run([os.path.join(root, local) if local else 'ruff', 'format', '--quiet', rel], root)


def declares_prettier(folder):
    try:
        if any(PRETTIER_CONFIG.fullmatch(f) for f in os.listdir(os.path.join(root, folder))):
            return True
        return 'prettier' in json.loads(read(folder, 'package.json') or '{}')  # the key, not a dependency
    except (OSError, ValueError, TypeError):
        return False


def declares_biome(folder):
    """A `formatter` block that is not switched off. A config that only lints is not a declaration."""
    for name in ('biome.json', 'biome.jsonc'):
        text = _JSONC.sub(lambda m: m.group(1) or '', read(folder, name))
        try:
            formatter = json.loads(re.sub(r',(\s*[}\]])', r'\1', text) or '{}').get('formatter')
        except (ValueError, AttributeError):
            continue
        if isinstance(formatter, dict) and formatter.get('enabled') is not False:
            return True
    return False


def typescript():
    # from the file's folder up to the root: the nearest declaration decides, the nearest install runs
    folders = [os.path.dirname(rel)]
    while folders[-1]:
        folders.append(os.path.dirname(folders[-1]))
    tools = next((t for t in ([n for n, declared in (('prettier', declares_prettier), ('biome', declares_biome)) if declared(d)]
                              for d in folders) if t), [])
    if len(tools) != 1:
        return  # none declared, or both: do not guess
    names = [tools[0] + '.cmd'] if os.name == 'nt' else [tools[0]]
    # only what the project installed - never a runner that would download it
    binary = next((b for b in (os.path.join(root, d, 'node_modules', '.bin', n) for d in folders for n in names)
                   if os.path.exists(b)), None)
    if not binary:
        return
    target = os.path.join(root, rel)
    # run from the root, where the repo's ignore file and root config are looked up
    run([binary, '--write', target] if tools[0] == 'prettier' else [binary, 'format', '--write', target], root)


ruff() if ext == '.py' else typescript()
allow()  # formatting never blocks, and a missing formatter is not an error
