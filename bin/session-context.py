#!/usr/bin/env python3
"""Session briefing (<=30 lines; stdout is injected into context). SessionStart

Reads only repo-declared facts - no assumption about language, runtime or package manager.
"""
import json
import os
import re
import sys

from lib.util import read_payload, project_dir, git, current_branch, is_protected_branch, command_map

p = read_payload()
root = project_dir(p)
out = ['## Session context (rln-agent)']
branch = current_branch(root)

if branch:
    out.append(f'- branch: **{branch}**' +
               ('  ⚠️ PROTECTED - create a feature branch before committing (rule A1)' if is_protected_branch(branch) else ''))

dirty = git(['status', '--porcelain'], root)
if dirty is not None:
    n = len(dirty.split('\n')) if dirty else 0
    out.append(f'- uncommitted files: {n}' + (' (large working tree - confirm what is yours before editing)' if n > 20 else ''))
ticket = re.search(r'([A-Z][A-Z0-9]+-\d+)', branch or '', re.I)
if ticket:
    out.append(f'- ticket in branch name: {ticket.group(1).upper()}')

# runtime version pinned by the repo, whatever the ecosystem
for f in ['.tool-versions', '.nvmrc', '.python-version', '.ruby-version', '.node-version', 'runtime.txt', '.sdkmanrc']:
    path = os.path.join(root, f)
    if os.path.exists(path):
        with open(path, encoding='utf-8') as fh:
            v = ' / '.join(fh.read().strip().split('\n')[:2])
        out.append(f'- runtime pinned by `{f}`: {v} — if your local version differs, stop and report')
        break

# Claude Code reads project MCP wiring from `.mcp.json` at the repo root only.
# `.claude/.mcp.json` is silently ignored, so report it as broken instead of reading it.
mcp = os.path.join(root, '.mcp.json')
if os.path.exists(mcp):
    try:
        with open(mcp, encoding='utf-8') as fh:
            servers = list((json.load(fh).get('mcpServers') or {}).keys())
        if servers:
            out.append(f'- MCP servers expected: {", ".join(servers)}')
    except (ValueError, AttributeError, OSError):
        out.append('- ⚠️ `.mcp.json` is not valid JSON - no project MCP server is loaded')
if os.path.exists(os.path.join(root, '.claude', '.mcp.json')):
    out.append('- ⚠️ `.claude/.mcp.json` exists but Claude Code never loads it - move it to `.mcp.json` in the repo root')

cmd = command_map(root)
keys = list(cmd.keys())
if keys:
    pick = [k for k in keys if re.search(r'typecheck|lint|test|build', k)][:4]
    if pick:
        out.append('- commands: ' + ' · '.join(f'{k}: `{cmd[k]}`' for k in pick))
elif os.path.exists(os.path.join(root, 'CLAUDE.md')):
    out.append('- ⚠️ CLAUDE.md has no filled command map - the definition-of-done gate cannot suggest commands. Run /setup.')
else:
    out.append('- ⚠️ no CLAUDE.md in this repo - run **/setup** before doing any work')
out.append('- workflow: /feature <TICKET>, or /plan → /analyze → /implement → /review-pr. Nothing is "done" without executed verification (rule B1).')

sys.stdout.write('\n'.join(out[:30]) + '\n')
