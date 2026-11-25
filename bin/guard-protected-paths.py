#!/usr/bin/env python3
"""Protected paths (rule C3). PreToolUse: Edit|Write|MultiEdit|NotebookEdit|Bash|mcp__.*

The gate is keyed to the action, not to a list of tool names: writing a file through an MCP server or
through a shell redirection is the same act as writing it through Write, and used to pass untouched
(review A5). `write_targets` finds the paths whatever the tool calls them, and reads nothing for a call
that only reads.
"""
import re

from lib.util import (read_payload, project_dir, protected_path_lists, rel_from_root, matches_any,
                      write_targets, block, ask, allow)

p = read_payload()
root = project_dir(p)

# a path outside the repository is outside this repo's rules
targets = [r for r in (rel_from_root(root, t) for t in write_targets(p)) if r]
if not targets:
    allow()

lists = protected_path_lists(root)
never, ask_list = lists['never'], lists['ask']

for rel in targets:
    if not matches_any(rel, never):
        continue
    if re.search(r'(^|/)(generated|__generated__)/|\.generated\.|\.gen\.', rel, re.I):
        why = 'change the source that generates this file, then re-run the generator from the command map'
    elif re.search(r'lock', rel, re.I):
        why = 'change the dependency declaration and let the tool regenerate the lockfile'
    else:
        why = 'edit the source of truth for this file, or ask a human'
    block('C3', f'"{rel}" is a protected path (generated, vendored, secret, or immutable).', why)

sensitive = [rel for rel in targets if matches_any(rel, ask_list)]
if sensitive:
    ask('"' + '", "'.join(sensitive) + '" is a sensitive project file (rule C3). Confirm the change and say why it is needed.')
allow()
