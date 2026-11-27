#!/usr/bin/env python3
"""Destructive and production-touching commands (rules C4, C5). PreToolUse: Bash

Built-ins are ecosystem-neutral. Projects and stack packs add their own one-regex-per-line in
.claude/rules/destructive-commands.txt or destructive-commands.<label>.txt (e.g. a device-copy or publish command).
"""
import re

from lib.util import read_payload, project_dir, segments, extra_command_patterns, block, ask, allow

p = read_payload()
if p.get('tool_name') != 'Bash':
    allow()
root = project_dir(p)

SAFE_RM = re.compile(r'(dist|build|out|target|coverage|tmp|temp|\.cache|\.turbo|\.nx|node_modules|vendor|__pycache__|\.venv|\.pytest_cache|\.gradle)')
extra = extra_command_patterns(root, 'destructive-commands')

# checked on the whole command line, because segments() splits on the pipe that makes this dangerous
raw = str((p.get('tool_input') or {}).get('command') or '')
if re.search(r'(?:curl|wget|iwr|Invoke-WebRequest)[^|]*\|\s*(?:sudo\s+)?(?:sh|bash|zsh|python\d?|node|perl|ruby|iex)\b', raw, re.I):
    block('C4', 'piping a downloaded script straight into an interpreter.',
          'download it, read it, then run it deliberately - or install the tool from the platform package manager')

for c in segments(raw):
    for source, rx in extra:
        if rx.search(c):
            block('C4', f'"{c}" matches a destructive pattern declared for this repo (.claude/rules/{source}).',
                  'hand this command to a human, or use the reversible alternative documented in RUNBOOK.md')

    if re.search(r'\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\b', c) and not SAFE_RM.search(c):
        block('C4', f'"{c}" is a recursive force delete outside the known build directories.',
              'delete the specific path, or name a build/cache directory')
    if re.search(r'\brm\s+-rf\s+(/|~|\$HOME|\*)\s*$', c) or re.search(r':\(\)\s*\{', c):
        block('C4', 'catastrophic command.', 'nothing - do not run this')
    if re.search(r'\bgit\s+clean\s+-[a-zA-Z]*[dfx]', c):
        block('C4', 'git clean removes untracked files irreversibly.', 'delete the specific paths you mean')
    if re.search(r'docker\s+(system\s+prune|volume\s+rm|compose\s+down\s+(-v|--volumes))', c):
        block('C4', 'this destroys local volumes and other projects’ containers.',
              'stop only this project: docker compose down')
    if re.search(r'\b(kubectl|helm|terraform|pulumi|ansible|aws|gcloud|az|flyctl|vercel|heroku|railway)\b', c):
        block('C5', f'"{c}" touches infrastructure.', 'infrastructure changes are human-run; describe what needs to happen')
    # publish / deploy / submit, but only when it is the command or its subcommand - not a filename that
    # happens to contain the word (`cat deploy.md` must stay allowed)
    tokens = c.split()
    verb_at = next((i for i, t in enumerate(tokens) if i <= 2 and re.fullmatch(r'publish|submit|deploy|release|promote', t)), -1)
    if (verb_at >= 0 and not re.fullmatch(r'git|cat|less|head|tail|grep|rg|ls|find|wc|echo|open|code', tokens[0])
            and not re.search(r'--dry-run|--help|-h$', c)):
        block('C4', f'"{c}" looks like a publish, deploy or store submission.',
              'prepare the version bump and changelog, then hand off to the lead')
    if re.search(r'chmod\s+777', c):
        block('C4', 'chmod 777.', 'use the narrowest permission the task needs')

    if re.search(r'\b(prod|production|live)\b', c, re.I) and re.search(r'(deploy|ssh|scp|rsync|restore|dump)', c, re.I):
        block('C5', 'this looks like a production operation.',
              'stop and hand this to a human with the exact command you propose')

    if re.search(r'\bgh\s+(repo|secret|api)\b.*(delete|-X\s*DELETE)', c):
        ask(f'Destructive remote API call (rule C4): "{c}". Confirm explicitly if this is intended.')
allow()
