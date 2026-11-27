#!/usr/bin/env python3
"""Enforces the dependency manager this repo declares. PreToolUse: Bash

Two ecosystems, each judging only its own commands: Python (py-tooling-1..3) and Node (ts-tooling-1..3).
A block in any segment wins; the confirmation questions are collected and asked after every segment was seen.
"""
import json
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


# ---------------- Node: npm, pnpm, yarn, bun ----------------

LOCKFILES = {'package-lock.json': 'npm', 'npm-shrinkwrap.json': 'npm', 'pnpm-lock.yaml': 'pnpm',
             'yarn.lock': 'yarn', 'bun.lock': 'bun', 'bun.lockb': 'bun'}
# subcommands that change what is installed: 'add' may name a new package, 'sync' only installs, then remove/update
NODE_COMMANDS = {
    'npm': {'add': 'install add i in ins inst insta instal isnt isnta isntal isntall install-test it',
            'sync': 'ci clean-install ic install-clean isntall-clean',
            'remove': 'uninstall unlink remove rm r un', 'update': 'update u up upgrade udpate'},
    'pnpm': {'add': 'add install i', 'sync': 'ci', 'remove': 'remove rm uninstall un', 'update': 'update up upgrade'},
    'yarn': {'add': 'add', 'sync': 'install', 'remove': 'remove', 'update': 'up upgrade upgrade-interactive'},
    'bun': {'add': 'add a install i', 'sync': 'ci', 'remove': 'remove rm', 'update': 'update'},
}
# `-P` is a peer dependency for yarn only; npm and pnpm read it as a production one
NOT_RUNTIME = {
    'npm': {'-D', '--save-dev', '-O', '--save-optional', '--save-peer'},
    'pnpm': {'-D', '-d', '--save-dev', '-O', '-o', '--save-optional', '--save-peer'},
    'yarn': {'-D', '--dev', '-O', '--optional', '-P', '--peer'},
    'bun': {'-D', '-d', '--dev', '--development', '--optional', '--peer'},
}
FORCING = {'npm': {'--force', '-f', '--legacy-peer-deps'}, 'pnpm': {'--force'},
           'yarn': {'--force', '--ignore-engines'}, 'bun': {'--force'}}
# flags whose value is the next word, so it is neither the subcommand nor a package name
VALUE_FLAGS = {'--registry', '--filter', '-F', '--workspace', '--prefix', '--cwd', '--dir', '-C', '--tag'}


def words(segment):
    """The words a segment runs: no quotes, subshell parentheses, redirections, comment, `VAR=x` or wrapper."""
    out, skip = [], False
    for w in segment.split():
        if w.startswith('#'):
            break
        if skip:
            skip = False
        elif re.fullmatch(r'\d*[<>]+&?', w):
            skip = True   # `> file`
        elif not re.search(r'[<>]', w) and w != '&':
            w = w.strip('"\'').lstrip('(').rstrip(')')
            if w:
                out.append(w)
    while out and (re.match(r'[A-Za-z_]\w*=', out[0]) or out[0] in ('sudo', 'command', 'time', 'nice', 'exec', 'env', 'corepack')):
        out.pop(0)
    return out


def folders(start):
    """`start` and its parents up to the project root; nothing for a folder outside the project."""
    top = os.path.realpath(root)
    d = os.path.realpath(start)
    while d == top or d.startswith(top + os.sep):
        yield d
        if d == top:
            return
        d = os.path.dirname(d)


def node_project(start):
    """(is there a Node project here, its declared manager or None) - the nearest folder with evidence decides."""
    found = False
    for d in folders(start):
        manifest = os.path.join(d, 'package.json')
        found = found or os.path.exists(manifest)
        try:
            with open(manifest, encoding='utf-8-sig') as fh:
                named = str(json.load(fh).get('packageManager') or '').split('@')[0]
        except (OSError, ValueError, AttributeError):
            named = ''
        if named in NODE_COMMANDS:
            return True, named
        locks = {m for f, m in LOCKFILES.items() if os.path.exists(os.path.join(d, f))}
        if locks:
            return True, locks.pop() if len(locks) == 1 else None  # two managers: do not guess
    return found, None


def node_command(w):
    """(manager, kind, is_global, flags, packages) for an install, remove or update; otherwise None."""
    if not w:
        return None
    tool = re.sub(r'\.(cmd|exe)$', '', w[0].split('/')[-1])
    if tool not in NODE_COMMANDS:
        return None
    flags, args, i = [], [], 1
    while i < len(w):
        if w[i].startswith('-'):
            flags.append(w[i])
            if w[i] in VALUE_FLAGS or (w[i] == '-w' and tool == 'npm'):
                i += 1
        else:
            args.append(w[i])
        i += 1
    if {'--help', '-h', '--version', '-v'} & set(flags):
        return None
    is_global = bool({'-g', '--global', '--location=global'} & set(flags))
    if tool == 'yarn':
        if args[:1] == ['global']:
            is_global, args = True, args[1:]
        elif args[:1] == ['workspace']:
            args = args[2:]
        if not args:
            return None if is_global else (tool, 'sync', False, flags, [])  # bare `yarn` installs
    if not args:
        return None
    kind = next((k for k, names in NODE_COMMANDS[tool].items() if args[0] in names.split()), None)
    return (tool, kind, is_global, flags, args[1:]) if kind else None


def check_node(segment, w, cwd):
    for i, x in enumerate(w):
        if x in ('rm', 'del', 'unlink'):
            for target in w[i + 1:]:
                if os.path.basename(target) in LOCKFILES and node_project(os.path.dirname(os.path.join(cwd, target)))[0]:
                    block('ts-tooling-3', 'deleting a lockfile.', 'never delete it — fix the dependency instead')
    found = node_command(w)
    if not found:
        return
    tool, kind, is_global, flags, packages = found
    here, declared_manager = node_project(cwd)
    if not here:
        return
    installs = kind != 'remove'
    if is_global and installs:
        block('ts-tooling-2', f'"{segment}" installs globally, outside this project.',
              'add it to the project\'s devDependencies, or ask a human')
    if declared_manager and tool != declared_manager and not is_global:
        block('ts-tooling-1', f'"{segment}" uses {tool}, but this repo declares {declared_manager}.',
              f'use {declared_manager} — see the command map in CLAUDE.md')
    if installs and FORCING[tool] & set(flags):
        block('ts-tooling-2', f'"{segment}" forces past the package manager\'s own protection.',
              'fix the conflict it reports, or ask a human')
    if kind == 'add' and not is_global and not NOT_RUNTIME[tool] & set(flags) and any(x != '.' for x in packages):
        asks.append(f'Adding a runtime dependency (rule C2): "{segment}". Confirm it is needed, pin it, and justify size/licence/maintenance in the PR.')


def follow_cd(w, cwd):
    if w[:1] != ['cd'] or len(w) < 2 or w[1].startswith('-') or '$' in w[1]:
        return cwd
    return os.path.normpath(os.path.join(cwd, os.path.expanduser(w[1])))


# ---------------- Python: pip, uv, poetry, pipenv ----------------

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

asks = []
cwd = str(p.get('cwd') or root)
for c in segments(raw):
    w = words(c)
    cwd = follow_cd(w, cwd)
    check_node(c, w, cwd)
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
        asks.append(f'Adding a runtime dependency (rule C2): "{c}". Confirm it is needed, pin it, and justify size/licence/maintenance in the PR.')
if asks:
    ask(' '.join(asks))
allow()
