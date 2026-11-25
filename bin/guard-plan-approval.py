#!/usr/bin/env python3
"""Makes the plan-approval gate mechanical instead of advisory (rule B4 / the /plan go-ahead).
PreToolUse: Edit|Write|MultiEdit|NotebookEdit|Bash|mcp__.*

Keyed to the action rather than to a list of tool names: code written through an MCP server or through
a shell redirection is code, and used to walk past this gate untouched (review A5).

Scope, deliberately narrow: it only speaks when a plan for the current ticket EXISTS and carries
no approval signature. No ticket in the branch name, or no plan file, means no opinion - this hook
enforces "approved before code", not "a plan must exist" (that is /implement's precondition and
the definition-of-done gate's job).

The escape is visible rather than hidden: there is no env bypass. A human writes the signature line
into the plan itself, which is durable, reviewable in the PR diff, and can say what it is
(`Approved-by: spike, no review - APK-142`) instead of silently disabling a check.
"""
import os
import re

from lib.util import read_payload, project_dir, rel_from_root, is_code_file, current_branch, write_targets, block, allow

# `[^\S\n]*` on purpose: `\s*` matches newlines, so an empty `Approved-by:` line would have
# swallowed the blank line and read the NEXT line as the signature. An empty signature is not approval.
APPROVAL = re.compile(r'^[^\S\n]*Approved-by:[^\S\n]*\S+', re.M | re.I)

p = read_payload()
root = project_dir(p)

# writing prose, the plan, the spec or the agent config is always allowed - that is how you get approved
code = [rel for rel in (rel_from_root(root, t) for t in write_targets(p))
        # also by location, so docs/x.json is not caught by extension
        if rel and is_code_file(rel) and not re.match(r'(docs|\.claude)/', rel)]
if not code:
    allow()
rel = code[0]

branch = current_branch(root) or ''
m = re.search(r'([A-Za-z][A-Za-z0-9]+-\d+)', branch)
if not m:
    allow()
ticket = m.group(1).upper()


def find_plan():
    for base in ('docs/features', 'docs/feature', 'docs'):
        d = os.path.join(root, base)
        if not os.path.exists(d):
            continue
        try:
            entries = os.listdir(d)
        except OSError:
            continue
        hit = next((e for e in entries if e.upper() == ticket), None)
        if not hit:
            continue
        for name in ('plan.md', 'PLAN.md'):
            f = os.path.join(d, hit, name)
            if os.path.exists(f):
                with open(f, encoding='utf-8') as fh:
                    return {'path': f'{base}/{hit}/{name}', 'text': fh.read()}
    return None


plan = find_plan()
if not plan:
    allow()                      # no plan for this ticket - not this hook's business
if APPROVAL.search(plan['text']):
    allow()                      # signed off

block(
    'B4',
    f'the plan for {ticket} is not approved yet, so "{rel}" must not be written.\n'
    f'Plan: {plan["path"]} - no "Approved-by:" line.',
    'present the plan (scope, requirements, risks) and get a human decision. When they approve, add the '
    'signature to the plan itself:\n  Approved-by: <name> · <YYYY-MM-DD>\n'
    'Documentation, the spec and the plan can be written meanwhile. A deliberate exception is written the '
    f'same way, with its reason: "Approved-by: spike, no review - {ticket}".'
)
