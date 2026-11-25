#!/usr/bin/env python3
"""H1 - git and PR discipline (rules A1-A4, A6). PreToolUse: Bash"""
import re

from lib.util import (read_payload, project_dir, segments, block, allow, current_branch,
                      is_protected_branch, protected_branches, git)

p = read_payload()
if p.get('tool_name') != 'Bash':
    allow()
root = project_dir(p)
cmds = segments((p.get('tool_input') or {}).get('command') or '')
branch = current_branch(root)
on_protected = is_protected_branch(branch)

for c in cmds:
    is_git = bool(re.match(r'git\s', c))
    is_gh = bool(re.match(r'gh\s', c))

    # A4 - the agent never merges, approves or un-drafts a PR
    if is_gh and re.search(r'\bpr\s+(merge|ready)\b', c):
        block('A4', f'"{c}" - only a human marks a PR ready or merges it.',
              'leave the PR as a draft and report that it is ready for review')
    if is_gh and re.search(r'\bpr\s+review\b', c):
        block('A4', f'"{c}" - the agent never submits a PR review.',
              'post findings with /review or as a plain PR comment')
    if is_gh and re.search(r'\brelease\s+create\b', c):
        block('C4', 'creating a release is a human action.', 'ask the tech lead to cut the release')

    if not is_git:
        continue

    # A2 - force push
    if re.search(r'\bpush\b', c) and re.search(r'--force(?!-with-lease)\b|(?:^|\s)-f(?:\s|$)', c):
        block('A2', 'plain --force push.', 'git push --force-with-lease, and only on your own feature branch')

    # A1 - protected branches
    push_target = re.search(r'\bpush\b[^|]*?\s(?:origin|upstream)\s+(?:HEAD:)?([\w./-]+)', c)
    if re.search(r'\bpush\b', c) and (is_protected_branch(push_target.group(1)) if push_target else on_protected):
        block('A1', f'push to protected branch "{push_target.group(1) if push_target else branch}".',
              f'create a feature branch: git switch -c feat/<TICKET>-<slug>  (protected: {", ".join(protected_branches())})')
    if re.search(r'\bcommit\b', c) and on_protected:
        block('A1', f'commit on protected branch "{branch}".', 'git switch -c feat/<TICKET>-<slug> and commit there')

    # A6 / B3 - never bypass local checks
    if re.search(r'\bcommit\b', c) and re.search(r'--no-verify|(?:^|\s)-n(?:\s|$)', c):
        block('B3', 'commit with --no-verify bypasses the pre-commit checks.', 'fix what the hook reports, then commit normally')

    # A3 - no history rewrite on pushed work
    if re.search(r'\bcommit\b', c) and '--amend' in c:
        pushed = git(['branch', '-r', '--contains', 'HEAD'], root)
        if pushed:
            block('A3', 'amending a commit that is already pushed.', 'make a new commit instead')
    if re.search(r'\brebase\b', c) and on_protected:
        block('A1', f'rebase while on protected branch "{branch}".', 'switch to your feature branch first')
    if re.search(r'\bpush\b', c) and re.search(r'--delete|:\s*$', c):
        block('C4', 'deleting a remote branch.', 'ask a human to delete the remote branch')
    if re.search(r'\bcheckout\s+\.|\brestore\s+\.|\breset\s+--hard', c):
        block('C4', f'"{c}" discards uncommitted work irreversibly.',
              'git stash, or name the specific file you want to restore')

    # A6 - obvious secret commits
    if re.search(r'\badd\b', c) and re.search(
            r'(^|\s)(\.env|[\w./-]*\.env(\.\w+)?|[\w./-]*\.(pem|p8|p12|keystore|jks|mobileprovision))(\s|$)', c):
        block('A6', 'staging a secret or key file.', 'add it to .gitignore; secrets live in the secret manager')
allow()
