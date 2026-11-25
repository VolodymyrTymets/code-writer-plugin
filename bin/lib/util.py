"""Shared helpers for rln-agent hooks. Needs python3 >= 3.9, standard library only, stack-agnostic.

Nothing in here may name a language, framework or package manager: what the repo uses is read from
the command map in CLAUDE.md and from the optional pattern files under .claude/rules/.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

# Hook payloads and block messages carry non-ASCII text (arrows, dots, typographic quotes); a console
# whose default encoding is not UTF-8 must not turn that into a crash.
for _stream in (sys.stdin, sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass


def read_payload() -> dict:
    try:
        raw = sys.stdin.read().strip()
        data = json.loads(raw) if raw else {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def project_dir(payload: dict | None = None) -> str:
    return os.environ.get('CLAUDE_PROJECT_DIR') or (payload or {}).get('cwd') or os.getcwd()


def block(rule: str, message: str, alternative: str | None = None) -> None:
    """Block the action: stderr becomes the feedback the agent sees."""
    lines = [f'[rln-agent] BLOCKED by rule {rule}: {message}']
    if alternative:
        lines.append(f'Do this instead: {alternative}')
    sys.stderr.write('\n'.join(lines) + '\n')
    sys.stderr.flush()
    sys.exit(2)


def ask(reason: str) -> None:
    """Ask the user instead of blocking outright."""
    sys.stdout.write(json.dumps({
        'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'permissionDecision': 'ask',
            'permissionDecisionReason': f'[rln-agent] {reason}',
        }
    }, ensure_ascii=False, separators=(',', ':')))
    sys.stdout.flush()
    sys.exit(0)


def allow() -> None:
    sys.exit(0)


_SPLIT = r'\n|&&|\|\||;|(?<!\|)\|(?!\|)'
_SEPARATORS = re.compile('(' + _SPLIT + ')')


def segments(command: str = '') -> list:
    """Split a shell command line into individually inspectable segments."""
    return [s.strip() for s in re.split(_SPLIT, str(command or '')) if s and s.strip()]


def verifiable_segments(command: str = '') -> list:
    """The same segments, each flagged with whether the exit code the harness reported is that segment's.

    Only `&&` carries a segment's status to the end of the line: `a && b` succeeds only if both did.
    With `|`, `;` or a newline the tail's code is the line's code, so nothing earlier in the line has
    been verified by it - `make test | tail -20` reports on `tail`. And a `||` anywhere to the left means
    the segment may never have run at all. Used by record-activity: a command whose real result the hook
    cannot see is not evidence, in either direction.
    """
    parts = _SEPARATORS.split(str(command or ''))
    out = []
    for i in range(0, len(parts), 2):
        seg = (parts[i] or '').strip()
        if not seg:
            continue
        before = [parts[k].strip() for k in range(1, len(parts), 2) if k < i]
        after = [parts[k].strip() for k in range(1, len(parts), 2) if k > i]
        out.append({'seg': seg, 'covered': '||' not in before and all(x == '&&' for x in after)})
    return out


_ASSIGN = re.compile(r'[A-Za-z_]\w*=')
_WRAPPER = re.compile(r'(sudo|command|time|nice|exec|env)')


def command_tokens(segment: str = '') -> list:
    """The tokens a segment actually runs: leading `VAR=value` assignments and a `sudo`/`time`-style
    wrapper dropped, the program reduced to its basename, everything lowercased. `CI=1 sudo
    /usr/bin/make test` and `make test` both come back as `['make', 'test']`.
    """
    t = str(segment).strip().split()
    i = 0
    while i < len(t) and _ASSIGN.match(t[i]):
        i += 1
    while i < len(t) and _WRAPPER.fullmatch(t[i]):
        i += 1
    out = [x.lower() for x in t[i:]]
    if out:
        out[0] = out[0].split('/')[-1]
    return out


def git(args: list, cwd: str):
    try:
        r = subprocess.run(['git'] + list(args), cwd=cwd, capture_output=True, text=True, timeout=4)
    except (OSError, subprocess.SubprocessError):
        return None
    return (r.stdout or '').strip() if r.returncode == 0 else None


def current_branch(cwd: str):
    return git(['rev-parse', '--abbrev-ref', 'HEAD'], cwd)


def protected_branches() -> list:
    from_env = os.environ.get('RLN_PROTECTED_BRANCHES')
    if from_env:
        return [s.strip() for s in from_env.split(',') if s.strip()]
    return ['main', 'master', 'develop', 'staging', 'release']


def is_protected_branch(name) -> bool:
    if not name:
        return False
    return name in protected_branches() or bool(re.match(r'(release|hotfix)/', name))


_GLOB_ESCAPE = '.+^$()|[]\\'


def glob_to_regex(glob: str):
    """Minimal glob -> regex (supports **, *, ?, {a,b}). Paths use forward slashes.

    `**/` spans whole path segments or none of them, so `**/dist/**` covers `dist/main` and
    `apps/api/dist/main` but not `src/mydist/main`. Emitting a bare `.*` there instead would make every
    `**/`-prefixed rule match half-words, and a rule that blocks the wrong file gets the hook turned off.
    """
    out = ''
    i = 0
    n = len(glob)
    while i < n:
        c = glob[i]
        if c == '*':
            if i + 1 < n and glob[i + 1] == '*':
                i += 1
                if i + 1 < n and glob[i + 1] == '/':
                    out += '(?:.*/)?'
                    i += 1
                else:
                    out += '.*'
            else:
                out += '[^/]*'
        elif c == '?':
            out += '[^/]'
        elif c == '{':
            end = glob.find('}', i)
            if end == -1:
                out += '\\{'
            else:
                alts = glob[i + 1:end].split(',')
                out += '(' + '|'.join(''.join('\\' + ch if ch in _GLOB_ESCAPE else ch for ch in a) for a in alts) + ')'
                i = end
        elif c in _GLOB_ESCAPE:
            out += '\\' + c
        else:
            out += c
        i += 1
    return re.compile(r'(?:\./)?' + out)


def matches_any(rel_path: str, globs: list) -> bool:
    """A path matches a list when some glob matches it and no `!` exception does.

    The exception wins wherever it sits in the file. That is deliberately *unlike* the `!` entries in a
    project's `.claude/settings.json`, which are gitignore negations and only carve out of the rules listed
    above them - a negation placed first there silently does nothing. This list is parsed here, so there is
    no reason to reproduce a failure mode that reports success either way.
    """
    p = rel_path.replace(os.sep, '/')

    def hit(g: str) -> bool:
        rx = glob_to_regex(g)
        return bool(rx.fullmatch(p) or rx.fullmatch('./' + p))

    if any(g.startswith('!') and hit(g[1:]) for g in globs):
        return False
    return any(not g.startswith('!') and hit(g) for g in globs)


def rule_file(root: str, name: str):
    """Read a rules file from the project first, then fall back to the plugin's own copy."""
    # The project copy wins. The plugin's rules/ is an inert two-layer library (core/ + stack-python/)
    # that /setup copies from, so it is only a fallback for a repo that has not been set up yet.
    plugin = os.environ.get('CLAUDE_PLUGIN_ROOT')
    candidates = [os.path.join(root, '.claude', 'rules', name)]
    if plugin:
        candidates += [os.path.join(plugin, 'rules', 'core', name),
                       os.path.join(plugin, 'rules', 'stack-python', name)]
    for f in candidates:
        if os.path.exists(f):
            with open(f, encoding='utf-8') as fh:
                return fh.read()
    return None


def protected_path_lists(root: str) -> dict:
    """Parse the two fenced glob lists out of rules/protected-paths.md."""
    md = rule_file(root, 'protected-paths.md')
    if not md:
        return {'never': [], 'ask': []}
    blocks = []
    for m in re.finditer(r'```([\s\S]*?)```', md):
        lines = [ln.strip() for ln in m.group(1).split('\n')]
        blocks.append([ln for ln in lines if ln and not ln.startswith('#')])
    return {'never': blocks[0] if len(blocks) > 0 else [], 'ask': blocks[1] if len(blocks) > 1 else []}


def extra_command_patterns(root: str, name: str) -> list:
    """Extra patterns a project or a stack pack drops in, one regex per line, `#` for comments:
    .claude/rules/destructive-commands.txt - ecosystem-specific commands (device copies, publishes)
    that guard-destructive should also treat as destructive.
    """
    f = os.path.join(root, '.claude', 'rules', name)
    if not os.path.exists(f):
        return []
    out = []
    with open(f, encoding='utf-8') as fh:
        for line in fh.read().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                out.append(re.compile(line, re.I))
            except re.error:
                pass
    return out


def rel_from_root(root: str, file_path):
    if not file_path:
        return None
    try:
        absolute = os.path.abspath(os.path.join(root, file_path))
        rel = os.path.relpath(absolute, root)
    except ValueError:  # another drive on Windows
        return None
    # Outside the repository is outside every rule this plugin has: a scratch file in /tmp is not a code
    # edit, and a protected-path glob written for this repo says nothing about another one. Returning the
    # absolute path instead made the definition-of-done gate fire on sessions that never touched the repo.
    if rel.startswith('..'):
        return None
    return rel.replace(os.sep, '/')


# ---------- what a tool call is about to write ----------

# A path can arrive under any key. The built-in tools use `file_path` and `notebook_path`; an MCP server
# uses whatever it likes, and Serena - which this plugin installs into every project - uses
# `relative_path`. Three hardcoded field names is one hole per server (review A5), so the field is found
# rather than listed.
_PATH_KEY = re.compile(r'(.*_)?(file|files|filename|filenames|filepath|path|paths|uri)', re.I)
# ...except the keys that carry a name shaped like a path but addressing something that is not a file.
_NOT_A_FILE_KEY = re.compile(r'(name_path|symbol_path|module_path|class_path|package_path|project_path|repo_path)', re.I)


def tool_input_paths(value, depth: int = 0) -> list:
    """Every path in a tool input, at any depth - `edits: [{ file_path }]` and `paths: [...]` included."""
    if not isinstance(value, (dict, list)) or depth > 4:
        return []
    if isinstance(value, list):
        out = []
        for v in value:
            out.extend(tool_input_paths(v, depth + 1))
        return out
    out = []
    for k, v in value.items():
        is_path_key = bool(_PATH_KEY.fullmatch(k)) and not _NOT_A_FILE_KEY.fullmatch(k)
        if isinstance(v, str):
            if is_path_key and v.strip():
                out.append(v.strip())
        elif isinstance(v, list):
            if is_path_key:
                out.extend(x.strip() for x in v if isinstance(x, str) and x.strip())
            out.extend(tool_input_paths(v, depth + 1))
        elif isinstance(v, dict):
            out.extend(tool_input_paths(v, depth + 1))
    return out


# An MCP call that only reads carries a path too, and a gate that blocks reads is a gate the team turns
# off. Read verbs are listed and everything else counts as a write: an unknown verb that turns out to be
# read-only costs one visible false block, while an unknown verb assumed read-only is a silent bypass.
_MCP_READ_VERB = re.compile(
    r'(^|_)(find|get|read|list|search|query|grep|show|view|inspect|describe|overview|symbols|summary|check|status|diff|log)(_|$)', re.I)
_MCP_NAME = re.compile(r'^mcp__[^_]+(?:_[^_]+)*?__(.+)$')


def is_mcp_write(tool_name: str = '') -> bool:
    """Does this MCP tool call write? Judged on the part of the name after the server prefix."""
    m = _MCP_NAME.match(str(tool_name))
    return (not _MCP_READ_VERB.search(m.group(1))) if m else False


_REDIRECT = re.compile(r'(?<![0-9&])>>?\s*(?!&)(["\']?)([^\s"\'|;&<>]+)\1')
_QUOTE_ENDS = re.compile(r'^["\']|["\']$')
_INPLACE_FLAG = re.compile(r'-[A-Za-z]*i')


def bash_write_targets(command: str = '') -> list:
    """The paths a shell command is about to write. Deliberately not exhaustive, and it cannot be: a script
    can write a file any way it likes. It covers the forms an agent actually reaches for - a redirection,
    `tee`, an in-place editor, a copy or a move - so that the protected-path rule is not simply absent from
    the shell (review A5). `cd x && ...` is followed, because in a monorepo that is how the agent gets to
    the file. Anything subtler stays a matter for review, and the README says so.
    """
    out: list = []
    cwd = ''

    def at(f):
        if not f or f.startswith('/') or not cwd:
            return f
        return re.sub(r'/+$', '', cwd) + '/' + f

    for seg in segments(command):
        # `> file` and `>> file`, but not `2>&1` or `>&2`
        for m in _REDIRECT.finditer(seg):
            out.append(at(m.group(2)))
        raw = [_QUOTE_ENDS.sub('', a) for a in seg.strip().split()]
        i = 0
        while i < len(raw) and _ASSIGN.match(raw[i]):
            i += 1
        if _WRAPPER.fullmatch(raw[i] if i < len(raw) else ''):
            i += 1
        prog = (raw[i] if i < len(raw) else '').split('/')[-1]
        rest = raw[i + 1:]
        operands = [a for a in rest if not a.startswith('-')]
        if prog == 'cd':
            cwd = operands[0] if operands else ''
            continue
        if prog == 'tee':
            out.extend(at(o) for o in operands)
        elif re.fullmatch(r'cp|mv|install|rsync', prog) and len(operands) >= 2:
            out.append(at(operands[-1]))
        elif re.fullmatch(r'sed|perl|ruby|gsed', prog) and any(_INPLACE_FLAG.match(a) for a in rest):
            out.extend(at(o) for o in operands[1:])
    return [x for x in out if x]


# The built-in tools that write a file. Unlike the MCP side this set is finite and known, so it is listed
# rather than guessed - `Read` and `Grep` carry a `file_path` too, and a gate that blocks reading is worse
# than useless. A structure case keeps this in step with the matcher in hooks.json.
BUILTIN_WRITE_TOOLS = ['Edit', 'Write', 'MultiEdit', 'NotebookEdit']


def write_targets(payload: dict | None = None) -> list:
    """Every path THIS tool call is about to write, whatever tool it is."""
    payload = payload or {}
    name = str(payload.get('tool_name') or '')
    tool_input = payload.get('tool_input') or {}
    if name == 'Bash':
        return bash_write_targets((tool_input or {}).get('command') or '')
    if name.startswith('mcp__'):
        return tool_input_paths(tool_input) if is_mcp_write(name) else []
    if name and name not in BUILTIN_WRITE_TOOLS:
        return []
    return tool_input_paths(tool_input)


# ---------- the command map: the only place the hooks learn what this repo runs ----------

_MAP_ROW = re.compile(r'^\|\s*([^|]+?)\s*\|\s*`([^`]+)`[^|]*\|')


def command_map(root: str) -> dict:
    """Parse the `| task | `command` |` table out of the project CLAUDE.md."""
    f = os.path.join(root, 'CLAUDE.md')
    out: dict = {}
    if not os.path.exists(f):
        return out
    try:
        with open(f, encoding='utf-8') as fh:
            text = fh.read()
    except OSError:
        return out
    for line in text.split('\n'):
        # text after the closing backtick (a note such as "report only") is allowed; `none` is a real answer
        m = _MAP_ROW.match(line)
        if m and not m.group(2).startswith('{{') and m.group(2).strip().lower() != 'none':
            out[m.group(1).strip().lower()] = m.group(2).strip()
    return out


_BUCKET_BY_TASK = [
    (re.compile(r'typecheck|type-check|types'), 'typecheck'),
    (re.compile(r'lint|format|static analysis'), 'lint'),
    (re.compile(r'e2e|end-to-end|integration'), 'e2e'),
    (re.compile(r'test'), 'test'),
    (re.compile(r'build|compile|bundle'), 'build'),
    (re.compile(r'dev|serve|run|start'), 'run'),
]


def verification_needles(root: str) -> list:
    """Verification needles derived from the command map: [{ bucket, needle }]."""
    out = []
    for task, cmd in command_map(root).items():
        bucket = next((b for rx, b in _BUCKET_BY_TASK if rx.search(task)), None)
        if not bucket:
            continue
        needle = re.sub(r'\s+', ' ', re.sub(r'\{\{[^}]*\}\}', '', cmd)).strip()
        if len(needle) >= 4:
            out.append({'bucket': bucket, 'needle': needle.lower()})
    return out


# ---------- session state (record-activity -> verify-dod) ----------

def state_file(root: str, session_id) -> str:
    d = os.path.join(root, '.claude', '.state')
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        pass
    return os.path.join(d, 'session-' + re.sub(r'[^\w-]', '', session_id or 'unknown', flags=re.ASCII) + '.json')


def _empty_state() -> dict:
    return {'codeEdits': [], 'docEdits': [], 'verified': {}, 'stopBlocks': 0}


def load_state(root: str, session_id) -> dict:
    f = state_file(root, session_id)
    if not os.path.exists(f):
        return _empty_state()
    try:
        with open(f, encoding='utf-8') as fh:
            state = json.load(fh)
    except (OSError, ValueError):
        return _empty_state()
    if not isinstance(state, dict):
        return _empty_state()
    for key, default in _empty_state().items():
        state.setdefault(key, default)
    return state


def save_state(root: str, session_id, state: dict) -> None:
    try:
        with open(state_file(root, session_id), 'w', encoding='utf-8') as fh:
            json.dump(state, fh, indent=2, ensure_ascii=False)
    except OSError:
        pass


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


# Anything that is not prose or an asset counts as code, whatever the language.
_NON_CODE_EXT = {'.md', '.mdx', '.txt', '.rst', '.adoc', '.csv', '.tsv',
                 '.svg', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.pdf', '.lock'}


def is_code_file(rel_path) -> bool:
    if not rel_path:
        return False
    return os.path.splitext(rel_path)[1].lower() not in _NON_CODE_EXT
