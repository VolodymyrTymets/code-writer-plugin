#!/usr/bin/env python3
"""Support hook for the definition-of-done gate: records what happened this session.

Verification commands are recognised from the command map in CLAUDE.md - this hook knows no tool names.
PostToolUse and PostToolUseFailure: Edit|Write|MultiEdit|Bash|mcp__.*
"""
import re

from lib.util import (read_payload, project_dir, rel_from_root, load_state, save_state, verifiable_segments,
                      command_tokens, command_rows, verification_needles, is_code_file, write_targets, now_iso, allow)

p = read_payload()
root = project_dir(p)
s = load_state(root, p.get('session_id'))
now = now_iso()

# Whether the command worked is the harness's verdict, not this hook's guess. Claude Code delivers a
# successful tool call to PostToolUse and a failed one to PostToolUseFailure, so a non-zero exit code
# never arrives here as a success. Reading pass/fail out of the output text instead was both unnecessary
# and wrong: `Found 0 errors.`, `0 problems (0 errors, 0 warnings)` and `40 passed, 0 failed` are what a
# clean type checker, a clean linter and a green suite actually print (review A2).
failed = p.get('hook_event_name') == 'PostToolUseFailure'

# Commands that read, print or move bytes around. Their arguments routinely carry the words below, and
# nothing they do is a verification: a session was recorded as tested, built and executed off `sed`,
# `echo` and `curl` alone (review A11).
READS_ONLY = re.compile(
    r'(cat|less|more|head|tail|sed|awk|grep|rg|ag|ls|find|fd|wc|echo|printf|tree|stat|file|which|pwd|cd|mv|cp|rm|mkdir|touch|'
    r'chmod|chown|ln|export|date|sleep|true|false|jq|yq|curl|wget|http|httpie|open|code|git|gh|diff|tee|xargs|sort|uniq|cut|env)')

# Generic fallbacks, used only when the command map does not resolve the command. Matched against the
# head of the command, never the whole line: `sed -n '1,60p' tests/some_file` runs no tests.
GENERIC = [
    (re.compile(r'\btypecheck\b|\btype-check\b'), 'typecheck'),
    (re.compile(r'\blint\b|\bformat\b'), 'lint'),
    (re.compile(r'\be2e\b|\bend-to-end\b'), 'e2e'),
    (re.compile(r'\btest\b|\bspec\b'), 'test'),
    (re.compile(r'\bbuild\b|\bcompile\b'), 'build'),
]
# Executing the change: an HTTP call, or driving a browser/device through an MCP tool. Matched on the
# program being run, not on the line: `cat docs/curl-recipes.md` calls nothing.
EXECUTES = re.compile(r'(curl|wget|httpie|http|xh|hurl)')


def runs_command(seg_tokens, cmd_tokens):
    """Does this segment run the mapped command? Same program, and every word of the mapped command
    present as a token - so a workspace-scoped invocation still counts as the map's own command, while
    a search for that command's text in a file does not.
    """
    return (len(seg_tokens) > 0 and len(cmd_tokens) > 0 and seg_tokens[0] == cmd_tokens[0]
            and all(t in seg_tokens for t in cmd_tokens[1:]))


def rows_run(tokens, rows):
    """The command-map rows this segment runs. A row whose words are all part of another matched row's is
    dropped: running the longer command says nothing about the shorter one's own run.
    """
    hits = [(r, set(command_tokens(r['needle']))) for r in rows if runs_command(tokens, command_tokens(r['needle']))]
    return [r for r, words in hits if not any(words < other for _, other in hits)]


tool_name = p.get('tool_name') or ''
if tool_name == 'Bash':
    needles = verification_needles(root)
    rows = command_rows(root)
    for item in verifiable_segments((p.get('tool_input') or {}).get('command') or ''):
        seg, covered = item['seg'], item['covered']
        tokens = command_tokens(seg)
        buckets = set()
        ran = []
        head = tokens[0] if tokens else ''

        if not READS_ONLY.fullmatch(head):
            ran = rows_run(tokens, rows)
            for n in needles:
                if runs_command(tokens, command_tokens(n['needle'])):
                    buckets.add(n['bucket'])
            if not buckets:
                head3 = ' '.join(tokens[:3])
                g = next((b for rx, b in GENERIC if rx.search(head3)), None)
                if g:
                    buckets.add(g)
        if EXECUTES.fullmatch(head):
            buckets.add('executed')

        # which row ran, not only which kind: a repo may require one row per part of the tree (verify-dod)
        if failed:
            # a failure no row claims could be any row of its kind, so it retires them all
            for r in ran or [r for r in rows if r['bucket'] in buckets]:
                s['rows'].pop(r['task'], None)
        elif covered:
            for r in ran:
                s['rows'][r['task']] = {'at': now, 'cmd': seg}

        for b in buckets:
            # A failure retires the claim rather than merely failing to add one: a typecheck that passed
            # before the last edit and fails now must leave the session with nothing verified.
            if failed:
                s['verified'].pop(b, None)
            elif covered:
                s['verified'][b] = {'at': now, 'cmd': seg}
elif tool_name.startswith('mcp__') and re.search(r'screenshot|snapshot|navigate|tap|click|automation|evaluate', tool_name, re.I):
    if failed:
        s['verified'].pop('executed', None)
    else:
        s['verified']['executed'] = {'at': now, 'cmd': tool_name}

# Code is code whoever wrote it. Recording this only for Edit/Write meant a session that edited through
# an MCP server ended with `codeEdits: []`, and the definition-of-done gate returned on its first line
# without a word (review A5). A write that failed changed no file, so it records nothing.
if not failed:
    for t in write_targets(p):
        rel = rel_from_root(root, t)
        if not rel:
            continue
        bucket = 'codeEdits' if is_code_file(rel) else 'docEdits'
        if rel not in s[bucket]:
            s[bucket].append(rel)
save_state(root, p.get('session_id'), s)
allow()
