#!/usr/bin/env python3
"""Definition of done, made mechanical (rules B1/B2). Stop hook.

Names no tool: every command it suggests comes from the command map in CLAUDE.md.
"""
import re
import sys

from lib.util import read_payload, project_dir, load_state, save_state, command_map, gate_paths, matches_any

p = read_payload()
root = project_dir(p)
s = load_state(root, p.get('session_id'))

# never loop forever: after two blocks, hand control back to the human
if p.get('stop_hook_active') or (s.get('stopBlocks') or 0) >= 2:
    sys.exit(0)
if not s.get('codeEdits'):
    sys.exit(0)

v = s.get('verified') or {}
cmd = command_map(root)


def pick(*keys):
    return next((cmd[k] for k in keys if cmd.get(k)), None)


paths = gate_paths(root)
touched = [label for label, globs in paths.items() if any(matches_any(f, globs) for f in s['codeEdits'])]
ran = s.get('rows') or {}


def per_label(keys):
    """The rows still to run when the map splits this kind of check by label, one for each label whose files
    were edited. A label with no row of its own is covered by the plain row. None when the map does not split
    the kind, or no labelled file was edited: the kind as a whole is then what counts.
    """
    labelled = {}
    for key in keys:
        for task in cmd:
            m = re.fullmatch(r'(.*?)\s*\(([^()]+)\)', task)
            if m and m.group(1) == key and m.group(2) in paths:
                labelled.setdefault(m.group(2), []).append(task)
    if not labelled or not touched:
        return None
    plain = [k for k in keys if cmd.get(k)]
    need = []
    for label in touched:
        tasks = labelled.get(label) or plain
        if tasks and not any(t in ran for t in tasks) and tasks[0] not in need:
            need.append(tasks[0])
    return need


missing = []


def check(name, keys, verified):
    need = per_label(keys)
    if need is not None:
        missing.extend(f'{task}  →  {cmd[task]}' for task in need)
    elif not verified and pick(*keys):
        missing.append(f'{name}  →  {pick(*keys)}')
    return pick(*keys)


typecheck_cmd = check('typecheck', ('typecheck', 'type-check', 'types'), v.get('typecheck'))
lint_cmd = check('lint', ('lint', 'format'), v.get('lint'))
# an end-to-end run stands in for the tests as a whole, never for one label's row
test_cmd = check('tests', ('affected tests', 'unit tests', 'tests', 'test'), v.get('test') or v.get('e2e'))
if not v.get('executed') and not v.get('e2e'):
    missing.append('execute the change (rule B1): call the endpoint, open the page, or launch the screen — and capture the evidence')
if not typecheck_cmd and not lint_cmd and not test_cmd and not v:
    missing.append('no verification of any kind was recorded, and CLAUDE.md has no command map — run /setup or state under "Not verified" why this session could not be verified')

if not missing:
    sys.exit(0)

s['stopBlocks'] = (s.get('stopBlocks') or 0) + 1
save_state(root, p.get('session_id'), s)

edits = s['codeEdits']
files = ', '.join(edits[:8]) + (f', +{len(edits) - 8} more' if len(edits) > 8 else '')
sys.stderr.write(
    f'[code-writer] Rule B1 - not done yet. Code changed this session ({files}) but these are missing:\n'
    + '\n'.join(f'  - {m}' for m in missing)
    + '\nRun them, then report the real output in the evidence block. Run each one on its own: a command behind '
    'a pipe, a "|| true" or a ";" reports someone else\'s exit code, so it does not count as verified. '
    'If something genuinely cannot be verified here (no device, no database, no network), say so explicitly '
    'under "Not verified" and stop again.\n'
)
sys.exit(2)
