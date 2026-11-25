#!/usr/bin/env python3
"""Definition of done, made mechanical (rules B1/B2). Stop hook.

Names no tool: every command it suggests comes from the command map in CLAUDE.md.
"""
import sys

from lib.util import read_payload, project_dir, load_state, save_state, command_map

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


missing = []

typecheck_cmd = pick('typecheck', 'type-check', 'types')
if not v.get('typecheck') and typecheck_cmd:
    missing.append(f'typecheck  →  {typecheck_cmd}')
lint_cmd = pick('lint', 'format')
if not v.get('lint') and lint_cmd:
    missing.append(f'lint  →  {lint_cmd}')
test_cmd = pick('affected tests', 'unit tests', 'tests', 'test')
if not v.get('test') and not v.get('e2e') and test_cmd:
    missing.append(f'tests  →  {test_cmd}')
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
    f'[rln-agent] Rule B1 - not done yet. Code changed this session ({files}) but these are missing:\n'
    + '\n'.join(f'  - {m}' for m in missing)
    + '\nRun them, then report the real output in the evidence block. Run each one on its own: a command behind '
    'a pipe, a "|| true" or a ";" reports someone else\'s exit code, so it does not count as verified. '
    'If something genuinely cannot be verified here (no device, no database, no network), say so explicitly '
    'under "Not verified" and stop again.\n'
)
sys.exit(2)
