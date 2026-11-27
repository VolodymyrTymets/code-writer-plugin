"""Structure guard. Run: python -m pytest tests/test_structure.py

The plugin has two layers that live in directories, not in separate repos:
  core         - never names a language, framework or dependency manager
  stack-python - the Python layer, which names them on purpose
Skills are deliberately FLAT (nesting inside a plugin's skills/ is not a documented Claude Code
feature), so the layer of a skill is known from the lists below rather than from its path.
"""
import json
import os
import re
import warnings
from pathlib import Path

from conftest import PLUGIN as ROOT
from lib.util import _BUCKET_BY_TASK, matches_any

CORE_SKILLS = ['setup-project', 'feature', 'plan-feature', 'analyze-plan', 'develop-feature',
               'write-tests', 'write-docs', 'review-pr', 'fix-bug']
STACK_SKILLS = []   # the Python layer is rules and hooks only; every skill is stack-neutral
# A plugin skill takes its command from frontmatter `name:` (unlike a project skill, where the
# directory name wins), so the directory can stay descriptive while the command stays short.
# This map is the single source of truth: the skills must match it, and no document may reference
# a command that is not in it. A mismatch here is what shipped once already - the docs said
# `/setup` and `/plan` while the skills were only reachable as `/setup-project` and `/plan-feature`.
COMMANDS = {
    'setup-project': 'setup',
    'feature': 'feature',
    'plan-feature': 'plan',
    'analyze-plan': 'analyze',
    'develop-feature': 'implement',
    'write-tests': 'write-tests',
    'write-docs': 'write-docs',
    'review-pr': 'review-pr',        # NOT `review`: /review is the bundled code-review alias and would shadow it
    'fix-bug': 'fix-bug',
}
# Claude Code's own commands. Referencing them is fine; naming a skill after one is not.
BUILTINS = ['mcp', 'context', 'plugin', 'compact', 'clear', 'config', 'init', 'help', 'rewind',
            'agents', 'doctor', 'review', 'code-review', 'login', 'feedback', 'loop', 'schedule', 'resume', 'rename']
# Commands we intend to build. Allowed in prose so a roadmap can name them; they must not be
# presented as available - keep them out of the constitution and out of a skill's instructions.
PLANNED = ['garden', 'techdebt', 'promote-rule', 'onboard', 'new-skill', 'handover', 'estimate',
           'release', 'security', 'refactor', 'adr', 'explain', 'verify', 'test', 'docs', 'pr', 'distill',
           'correct', 'trust-report']
PLANNED_OK_IN = ['README.md', 'CHANGELOG.md']

CORE_HOOKS = ['session-context.py', 'guard-git.py', 'guard-destructive.py', 'guard-protected-paths.py',
              'guard-plan-approval.py', 'record-activity.py', 'verify-dod.py', os.path.join('lib', 'util.py')]
STACK_HOOKS = ['guard-dependency-manager.py', 'format-changed.py']
# every stack layer must stay complete or /setup cannot install it
REQUIRED_STACK_RULES = {
    'stack-python': ['python-tooling.md', 'python-core.md', 'testing-python.md', 'CLAUDE.stack-section.md'],
    'stack-typescript': ['ts-tooling.md', 'ts-core.md', 'testing-ts.md', 'CLAUDE.stack-section.md'],
}

SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.pytest_cache', '.venv', '.idea', '.serena'}


def read(path) -> str:
    return Path(path).read_text(encoding='utf-8')


def frontmatter(path):
    t = read(path)
    if not t.startswith('---\n'):
        return None
    end = t.find('\n---\n', 3)
    return None if end < 0 else t[4:end]


def keys(block: str) -> dict:
    return {m.group(1): m.group(2) for m in re.finditer(r'^([a-zA-Z_-]+):\s*(.*)$', block, re.M)}


def walk(directory) -> list:
    out = []
    for name in sorted(os.listdir(directory)):
        p = Path(directory) / name
        if name in SKIP_DIRS:
            continue
        out.extend(walk(p) if p.is_dir() else [p])
    return out


def rel(p) -> str:
    return os.path.relpath(p, ROOT).replace(os.sep, '/')


def report(fails, warns=()):
    for w in warns:
        warnings.warn(w)
    assert not fails, '\n' + '\n'.join(f'FAIL: {f}' for f in fails)


SKILL_DIRS = sorted(os.listdir(ROOT / 'skills'))
PLUGIN_NAME = json.loads(read(ROOT / '.claude-plugin' / 'plugin.json'))['name']
AGENT_FILES = [f[:-3] for f in sorted(os.listdir(ROOT / 'agents')) if f.endswith('.md')]
HOOKS = json.loads(read(ROOT / 'hooks' / 'hooks.json'))


def setup_text() -> str:
    files = [ROOT / 'skills' / 'setup-project' / f for f in ('SKILL.md', 'references/stack-python.md', 'references/stack-typescript.md', 'references/interview.md')]
    return '\n'.join(read(f) for f in files if f.exists())


# ---------------- skills (flat) ----------------

def test_skills_are_flat_named_and_complete():
    fails, warns = [], []
    for d in SKILL_DIRS:
        sd = ROOT / 'skills' / d
        f = sd / 'SKILL.md'
        if not sd.is_dir():
            fails.append(f'skills/{d} is not a directory')
            continue
        if not f.exists():
            fails.append(f'skills/{d} has no SKILL.md')
            continue
        b = frontmatter(f)
        if not b:
            fails.append(f'skills/{d}/SKILL.md has no frontmatter')
            continue
        k = keys(b)
        expected = COMMANDS.get(d)
        if expected is None:
            fails.append(f'skills/{d}: not in the COMMANDS map - declare its command name')
        elif k.get('name') != expected:
            fails.append(f'skills/{d}: frontmatter name "{k.get("name")}" but COMMANDS says the command is "{expected}" - '
                         "a plugin skill's command comes from name:, so the docs and the skill would disagree")
        if k.get('name') in BUILTINS:
            fails.append(f'skills/{d}: name "{k["name"]}" collides with a built-in command - the bare /{k["name"]} would never reach this skill')
        if len(k.get('description') or '') < 40:
            fails.append(f'skills/{d}: description too short to trigger reliably')
        text = read(f)
        if len(text.split('\n')) > 500:
            fails.append(f'skills/{d}/SKILL.md over the 500-line budget - move depth into references/')
        for ref in re.finditer(r'@(references/[\w./-]+\.md)', text):
            if not (sd / ref.group(1)).exists():
                fails.append(f'skills/{d}: missing {ref.group(1)}')
        # nesting would break discovery, so catch a stray subdirectory that looks like a nested skill
        for sub in os.listdir(sd):
            if sub != 'references' and (sd / sub).is_dir() and (sd / sub / 'SKILL.md').exists():
                fails.append(f'skills/{d}/{sub}/SKILL.md is a nested skill - plugin skills must stay flat')
    for s in CORE_SKILLS + STACK_SKILLS:
        if s not in SKILL_DIRS:
            fails.append(f'skill "{s}" is listed in this test\'s layer map but missing from skills/')
    for d in SKILL_DIRS:
        if d not in CORE_SKILLS + STACK_SKILLS:
            warns.append(f"skills/{d} is not in this test's layer map - add it to CORE_SKILLS or STACK_SKILLS")
    report(fails, warns)


# ---------------- forked skills ----------------
# A gate that the caller may or may not run in a fresh context is a request, not a gate: the context that
# wrote the plan is the worst judge of it, and prose cannot stop it from judging itself. `context: fork` is
# the mechanism, so the skills below must carry it rather than ask for it.
# The `agent:` is the part that fails silently: with no agent (or one that does not resolve) a fork runs as
# `general-purpose`, which has Edit and Write - a "read-only" gate that can rewrite the plan it is judging.
MUST_FORK = ['analyze-plan']
BUILTIN_AGENTS = ['Explore', 'Plan', 'general-purpose']


def test_forked_skills_name_a_real_write_free_agent():
    fails = []
    for d in SKILL_DIRS:
        f = ROOT / 'skills' / d / 'SKILL.md'
        b = f.exists() and frontmatter(f)
        if not b:
            continue
        k = keys(b)
        forked = k.get('context') == 'fork'
        if d in MUST_FORK and not forked:
            fails.append(f'skills/{d}: no "context: fork" - it is a read-only gate, and a fork asked for in prose is not a mechanism')
        if not forked:
            if k.get('agent'):
                fails.append(f'skills/{d}: "agent:" without "context: fork" - the field only applies to a forked skill')
            if k.get('background'):
                fails.append(f'skills/{d}: "background:" without "context: fork" - the field only applies to a forked skill')
            continue
        # a plugin agent registers under its scoped id (`<plugin>:<name>`), which is what `agent:` must name
        a = k.get('agent')
        if not a:
            fails.append(f'skills/{d}: "context: fork" with no "agent:" - it would fork into general-purpose, which has write tools')
        elif a not in BUILTIN_AGENTS:
            scoped = a.startswith(f'{PLUGIN_NAME}:')
            bare = a[len(PLUGIN_NAME) + 1:] if scoped else a
            if not scoped:
                fails.append(f'skills/{d}: agent "{a}" is not a built-in and is not scoped - a plugin agent resolves as "{PLUGIN_NAME}:{a}"')
            elif bare not in AGENT_FILES:
                fails.append(f'skills/{d}: agent "{a}" has no agents/{bare}.md - the fork would fall back to general-purpose, silently')
        if d in MUST_FORK and k.get('background') != 'false':
            fails.append(f'skills/{d}: a gate must set "background: false" - a backgrounded fork lets the caller implement while the verdict is still being written')
    report(fails)


# ---------------- agents ----------------

def test_agents_have_frontmatter_a_matching_name_and_a_description():
    fails, warns = [], []
    for a in sorted(os.listdir(ROOT / 'agents')):
        if not a.endswith('.md'):
            continue
        b = frontmatter(ROOT / 'agents' / a)
        if not b:
            fails.append(f'agents/{a} has no frontmatter')
            continue
        k = keys(b)
        if k.get('name') != a[:-3]:
            fails.append(f'agents/{a}: name "{k.get("name")}" !== filename')
        if not k.get('description'):
            fails.append(f'agents/{a}: no description')
        if not k.get('tools'):
            warns.append(f'agents/{a}: no explicit tools allowlist (it will inherit everything)')
    report(fails, warns)


# ---------------- rules: an inert two-layer library ----------------

def test_rules_library_layers_budgets_and_required_stack_rules():
    fails, warns = [], []
    claude_md = ROOT / 'rules' / 'core' / 'CLAUDE.template.md'
    if not claude_md.exists():
        fails.append('rules/core/CLAUDE.template.md is missing')
    else:
        n = len(read(claude_md).split('\n'))
        if n > 200:
            fails.append(f'rules/core/CLAUDE.template.md is {n} lines (budget 200)')
    for layer in ('core', 'stack-python', 'stack-typescript'):
        d = ROOT / 'rules' / layer
        if not d.exists():
            fails.append(f'rules/{layer}/ is missing')
            continue
        for r in sorted(f for f in os.listdir(d) if f.endswith('.md')):
            if r.startswith('CLAUDE.'):
                continue  # templates and fragments, not path-scoped rules
            where = f'rules/{layer}/{r}'
            b = frontmatter(d / r)
            if not b:
                warns.append(f'{where}: no frontmatter')
                continue
            if 'paths:' not in b and (layer, r) != ('core', 'protected-paths.md'):
                # in a stack layer this is context every session pays for, so it fails rather than warns
                (fails if layer.startswith('stack-') else warns).append(f'{where}: no paths: globs - it would load unconditionally, every session')
            lines = len(read(d / r).split('\n'))
            if lines > 130:
                warns.append(f'{where} is {lines} lines (target <=120)')
    for layer, required in REQUIRED_STACK_RULES.items():
        for r in required:
            if not (ROOT / 'rules' / layer / r).exists():
                fails.append(f'rules/{layer}/{r} is missing - the layer is incomplete')
    report(fails, warns)


def rule_globs(path) -> list:
    return re.findall(r'^\s+- "([^"]+)"$', frontmatter(path) or '', re.M)


def test_typescript_rule_paths_reach_typescript_files_and_no_python_file():
    layer = ROOT / 'rules' / 'stack-typescript'
    expected = {'ts-tooling.md': ['package.json', 'apps/web/tsconfig.build.json', 'pnpm-lock.yaml'],
                'ts-core.md': ['a.ts', 'apps/web/src/a.tsx'],
                'testing-ts.md': ['a.test.ts', 'apps/web/src/a.spec.tsx', 'packages/ui/__tests__/a.ts']}
    for name, paths in expected.items():
        globs = rule_globs(layer / name)
        for p in paths:
            assert matches_any(p, globs), f'{name} does not load for {p}'
    for f in sorted(layer.glob('*.md')):
        if f.name.startswith('CLAUDE.'):
            continue
        for p in ('a.py', 'src/pkg/a.py', 'tests/test_a.py'):
            assert not matches_any(p, rule_globs(f)), f'{f.name} loads for {p}'


def test_stack_sections_hold_no_table_rows_and_their_rule_ids_do_not_collide():
    ids = {}
    for layer in REQUIRED_STACK_RULES:
        text = read(ROOT / 'rules' / layer / 'CLAUDE.stack-section.md')
        assert not re.search(r'^\|', text, re.M), f'{layer}: a table row here would replace a command-map row'
        ids[layer] = set(re.findall(r'\*\*([A-Z]+\d+)\*\*', text))
        assert ids[layer], layer
    ids['core'] = set(re.findall(r'\*\*([A-Z]+\d+)\*\*', read(ROOT / 'rules' / 'core' / 'CLAUDE.template.md')))
    every = [i for s in ids.values() for i in s]
    assert len(every) == len(set(every)), ids


# A label that changes which gate a row belongs to fails silently: `typescript` contains `types`.
def test_every_labelled_command_row_setup_names_stays_in_its_plain_rows_bucket():
    def bucket(task):
        return next((b for rx, b in _BUCKET_BY_TASK if rx.search(task)), None)

    labelled = re.findall(r'`([a-z][a-z ]*?) \((?:ts|py)\)`', read(ROOT / 'skills' / 'setup-project' / 'SKILL.md'))
    assert 'lint' in labelled
    for task in labelled:
        for label in ('ts', 'py'):
            assert bucket(f'{task} ({label})') == bucket(task), f'{task} ({label})'


def test_every_placeholder_in_the_rules_library_is_documented_in_setup():
    # every {{PLACEHOLDER}} in the rules library must be documented in /setup, or nothing fills it
    text = setup_text()
    placeholders = set()
    for layer in sorted(p.name for p in (ROOT / 'rules').iterdir() if p.is_dir()):
        d = ROOT / 'rules' / layer
        if d.exists():
            for r in (f for f in os.listdir(d) if f.endswith('.md')):
                placeholders.update(re.findall(r'\{\{([A-Z0-9_]+)\}\}', read(d / r)))
    report([f'placeholder {{{{{ph}}}}} is used in rules/ but not documented in setup-project - nothing would fill it'
            for ph in sorted(placeholders) if ph not in text])


STACKS_LINE = re.compile(r'^Stacks:\s*(.+)$', re.M)   # the contract in CONTRIBUTING.md; hooks and /setup re-runs read it


def known_stacks() -> list:
    """A stack is known to /setup when its reference exists: skills/setup-project/references/stack-<name>.md."""
    return sorted(p.stem[len('stack-'):] for p in (ROOT / 'skills' / 'setup-project' / 'references').glob('stack-*.md'))


def test_stacks_line_in_the_template_matches_the_contract():
    # the line is plain text: bold or backticks would end up inside the captured value
    template = read(ROOT / 'rules' / 'core' / 'CLAUDE.template.md')
    lines = [l for l in template.split('\n') if l.startswith('Stacks:')]
    fails = []
    if lines != ['Stacks: {{STACKS}}']:
        fails.append(f'rules/core/CLAUDE.template.md must hold exactly one line "Stacks: {{{{STACKS}}}}", found {lines}')
    known = known_stacks()
    for sample in ('Stacks: python', 'Stacks: typescript', 'Stacks: python, typescript', 'Stacks: none'):
        for v in (v.strip() for v in STACKS_LINE.search(sample).group(1).split(',')):
            if v != 'none' and v not in known:
                fails.append(f'"{sample}": {v} has no skills/setup-project/references/stack-{v}.md')
    contributing = read(ROOT / 'CONTRIBUTING.md')
    if STACKS_LINE.pattern not in contributing:
        fails.append(f'CONTRIBUTING.md must state the contract regex {STACKS_LINE.pattern} verbatim')
    if 'no bold' not in contributing:
        fails.append('CONTRIBUTING.md must say the Stacks: line is plain text (no bold, no backticks)')
    report(fails)


def test_setup_prose_asks_the_stack_before_copying_and_names_the_rerun_rules():
    text = setup_text()
    skill = read(ROOT / 'skills' / 'setup-project' / 'SKILL.md')
    must = ['AskUserQuestion', 'pyproject.toml', 'requirements', 'package.json', 'tsconfig.json', 'Stacks:', 'Stacks: none',
            'two levels', 'node_modules', 'the user\'s answer wins', 'delete nothing', 'never append', 'no `Stacks:` line', 'already installed', 'Do not create a stub']
    fails = [f'setup-project does not mention "{m}"' for m in must if m.lower() not in text.lower()]
    if re.search(r'not python,? skip', text, re.I):
        fails.append('setup-project still skips the stack step for a non-Python repo - it must branch per stack')
    i_stack, i_write = skill.find('## Step 1.5'), skill.find('## Step 4 ')
    if not 0 <= i_stack < i_write:
        fails.append('setup-project: the stack question (Step 1.5) must come before the config is written (Step 4)')
    report(fails)


def export_manifest(stack: str) -> list:
    """The `## Export manifest` bullet list of skills/setup-project/references/stack-<stack>.md."""
    text = read(ROOT / 'skills' / 'setup-project' / 'references' / f'stack-{stack}.md')
    m = re.search(r'^## Export manifest\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    return re.findall(r'^- `([^`]+)`', m.group(1), re.M) if m else []


def test_export_sets_for_python_typescript_and_both_do_not_overlap():
    fails = []
    stacks = known_stacks()
    sets = {s: export_manifest(s) for s in stacks}
    for s, files in sets.items():
        if not files:
            fails.append(f'references/stack-{s}.md has no "## Export manifest" bullet list')
        if len(files) != len(set(files)):
            fails.append(f'stack-{s} manifest lists a file twice')
        for f in files:
            for o in stacks:
                if o != s and re.search(rf'(?<![a-z]){o}(?![a-z])', f):
                    fails.append(f'stack-{s} manifest names stack-{o}\'s file: {f}')
        # a stack ships once its core rule file exists; its path list can land before that
        shipped = any((ROOT / 'rules' / f'stack-{s}').glob('*-core.md'))
        for f in files:
            if (shipped or f.endswith('/protected-paths.md')) and not (ROOT / f).exists():
                fails.append(f'stack-{s} manifest lists {f}, which does not exist')
        # completeness: a shipped file that is not in the manifest would never be exported
        for d in (ROOT / 'rules' / f'stack-{s}', ROOT / 'templates' / f'stack-{s}'):
            if d.exists():
                for p in sorted(d.iterdir()):
                    if not p.name.startswith('.') and rel(p) not in files:
                        fails.append(f'{rel(p)} exists but is not in the stack-{s} manifest, so /setup would never copy it')
    both = [f for files in sets.values() for f in files]
    if len(both) != len(set(both)):
        fails.append('the Both export set contains a file twice')
    report(fails)


# ---------------- hooks wiring ----------------

def test_hooks_json_is_wired_to_scripts_that_exist():
    fails, warns = [], []
    wired = set(re.findall(r'bin/([\w-]+\.py)', json.dumps(HOOKS)))
    for s in sorted(wired):
        if not (ROOT / 'bin' / s).exists():
            fails.append(f'hooks.json references missing bin/{s}')
    for s in [h for h in CORE_HOOKS + STACK_HOOKS if 'lib' not in h]:
        if s not in wired:
            warns.append(f'bin/{s} exists but is not wired in hooks.json')
    # The definition-of-done gate only sees a failed command if the plugin subscribes to failures at all.
    if not HOOKS.get('hooks', {}).get('PostToolUseFailure'):
        fails.append('hooks.json has no PostToolUseFailure block: a command that exits non-zero never reaches record-activity, '
                     'so nothing can retire a stale verification')
    report(fails, warns)


# A hook that reads a payload field Claude Code does not send fails silently and forever, and a test
# suite that builds its own payloads will never notice - which is exactly how A2 survived a green suite.
# `tool_result` is the field the API uses for a tool-result content block; hooks receive `tool_response`.
PHANTOM_PAYLOAD_FIELDS = ['tool_result', 'toolResult', 'tool_output', 'exit_code', 'exitCode']


def test_no_script_reads_a_payload_field_claude_code_does_not_send():
    fails = []
    files = [p for p in walk(ROOT / 'bin') + walk(ROOT / 'tests')
             if p.suffix == '.py' and p.name != 'test_structure.py']  # this file has to name them
    for p in files:
        text = read(p)
        for f in PHANTOM_PAYLOAD_FIELDS:
            if re.search(rf'\b{f}\b', text):
                fails.append(f'{rel(p)} uses "{f}", which is not a field of any hook payload - the result of a tool call reaches a hook '
                             'as "tool_response" on PostToolUse, and a failure as "error" on PostToolUseFailure')
    report(fails)


# ---------------- write gates: reach every way of writing (rule C3/B4) ----------------
# A gate keyed to a list of tool names has one hole per tool that is not on the list, and MCP servers and
# Bash were both off it. The matcher and the hook's own idea of a write must stay in step, and the two
# write gates must be wired everywhere a write can come from.
WRITE_GATES = ['guard-protected-paths.py', 'guard-plan-approval.py']


def test_write_gates_are_wired_for_every_way_of_writing():
    fails = []
    pre = HOOKS.get('hooks', {}).get('PreToolUse', [])
    m = re.search(r'BUILTIN_WRITE_TOOLS = \[([^\]]*)\]', read(ROOT / 'bin' / 'lib' / 'util.py'))
    builtins = re.findall(r"'([^']+)'", m.group(1)) if m else []
    for gate in WRITE_GATES:
        matchers = [h['matcher'] for h in pre if gate in json.dumps(h['hooks'])]
        for need in ('Bash', 'mcp__.*'):
            if not any(need in mt.split('|') for mt in matchers):
                fails.append(f'hooks.json: {gate} is not wired for "{need}" - a write through it bypasses the gate entirely')
        on_writes = next((mt for mt in matchers if 'Edit' in mt), None)
        for b in builtins:
            if on_writes and b not in on_writes.split('|'):
                fails.append(f'hooks.json: {gate} does not match "{b}", which util.py counts as a built-in write tool')
    report(fails)


# ---------------- permissions: the deny list has to live in the project ----------------
# A plugin's own settings.json applies only `agent` and `subagentStatusLine`. Claude Code reads every other
# key and silently discards it, so a permissions block shipped from here protects nothing and says nothing
# about it - which is how 23 deny rules rode along looking like a security layer while `.env` stayed readable
# and `gh pr merge` stayed available. Permissions exist only in project, user or managed settings.
PLUGIN_SETTINGS_KEYS = ['agent', 'subagentStatusLine']
PROJECT_SETTINGS = json.loads(read(ROOT / 'templates' / 'settings.project.json'))
DENY = PROJECT_SETTINGS.get('permissions', {}).get('deny', [])


def test_the_plugin_root_settings_declare_only_keys_a_plugin_can_apply():
    f = ROOT / 'settings.json'
    fails = []
    if f.exists():
        for k in json.loads(read(f)):
            if k not in PLUGIN_SETTINGS_KEYS:
                fails.append(f'settings.json at the plugin root declares "{k}"; Claude Code applies only {" and ".join(PLUGIN_SETTINGS_KEYS)} '
                             'from a plugin and ignores the rest without a word - move it to templates/settings.project.json so /setup writes it')
    report(fails)


# ...and what the plugin cannot ship, /setup has to write. Each class below is a protection with no second
# home: drop it here and no layer carries it.
DENY_CLASSES = [
    ('environment files at any depth', r'^Read\(\./\*\*/\.env'),
    ('key material at any depth', r'^Read\(\./\*\*/\*\.(pem|key|p8|p12|jks|keystore|mobileprovision)\)$'),
    ('credential files at any depth', r'^Read\(\./\*\*/[^)]*(credentials|service-account|id_rsa)'),
    ('merging, approving or un-drafting a PR from the shell (rule A4)', r'^Bash\(gh pr (merge|review|ready):'),
    ('merging a PR through an MCP server (rule A4 - the guard-git hook only inspects Bash)', r'^mcp__[\w*]*merge'),
    ('publishing or submitting a build (rule C4)', r'^Bash\((twine upload|uv publish|poetry publish|gh release create):'),
    ('force-pushing (rule A1)', r'^Bash\(git push --force'),
]


def test_the_project_settings_template_denies_what_no_other_layer_blocks():
    fails = []
    for label, rx in DENY_CLASSES:
        if not any(re.search(rx, d) for d in DENY):
            fails.append(f'templates/settings.project.json: permissions.deny has no rule for {label} - nothing else in the stack blocks it')

    # Over-blocking is how a rule set gets switched off. `.env.*` also matches `.env.example`, which holds no
    # secrets and is the one file that answers "which variables does this service need". A `!` rule is a
    # gitignore negation that carves paths out of the rules listed ABOVE it, so one placed first carves
    # nothing and does it silently - the failure mode this whole section exists to prevent.
    last_env_deny = max((i for i, d in enumerate(DENY) if re.search(r'^Read\(\./(\*\*/)?\.env', d)), default=-1)
    first_carve = next((i for i, d in enumerate(DENY) if re.search(r'^Read\(!.*\.env', d)), -1)
    if first_carve < 0:
        fails.append('templates/settings.project.json: permissions.deny blocks `.env.*` with no carve-out for `.env.example` - '
                     'that file carries no secrets, and denying it teaches the team the list is wrong')
    elif first_carve < last_env_deny:
        fails.append(f'templates/settings.project.json: "{DENY[first_carve]}" is listed before the .env deny rule it carves from - '
                     'a gitignore negation only applies to rules above it, so this one does nothing and says nothing')
    # The negation must stay a bare basename. Written in the anchored style of the lines above it
    # (`Read(!./**/.env.example)`) it carves out nothing at all, at the root or nested, with no warning -
    # verified in a fixture repo. Anyone tidying these three lines to match their neighbours breaks them.
    for c in (d for d in DENY if d.startswith('Read(!')):
        if re.match(r'^Read\(!(\./|\*\*/)', c) or '/' in c:
            fails.append(f'templates/settings.project.json: "{c}" anchors a gitignore negation with a path - '
                         'only a bare basename such as Read(!.env.example) carves anything out, and the anchored form fails silently')
    # A rule nobody writes is not a rule: /setup is the only thing that puts this block in a client repo.
    if 'permissions.deny' not in setup_text():
        fails.append('setup-project never names permissions.deny - the plugin cannot ship permissions, '
                     'so a block no skill writes does not reach any repo')
    report(fails)


# ---------------- protected paths: monorepo reach (rule C3) ----------------
# A glob with no leading globstar only ever matches at the repository root, and this plugin targets
# monorepos - so an unprefixed entry is a rule that protects nothing in the repo it was written for.
# The exceptions are files that mean something only at a workspace root; each one is listed here on
# purpose, so adding another is a decision rather than an oversight.
ROOT_ONLY = {
    '.github/workflows/**',   # GitHub reads workflows from the root and nowhere else
    '.gitlab-ci.yml',         # same
    '.claude/**',             # the project's own agent config
}


def glob_blocks(path) -> list:
    out = []
    for m in re.finditer(r'```\n([\s\S]*?)```', read(path)):
        out.extend(ln.strip() for ln in m.group(1).split('\n') if ln.strip())
    return out


def test_protected_path_globs_reach_into_every_workspace():
    fails = []
    for f in sorted((ROOT / 'rules').glob('*/protected-paths.md')):
        for g in glob_blocks(f):
            bare = g[1:] if g.startswith('!') else g   # an exception needs the same reach as the rule it carves from
            if not bare.startswith('**/') and bare not in ROOT_ONLY:
                fails.append(f'{rel(f)}: "{g}" is anchored to the repository root - prefix it with "**/" or add it to ROOT_ONLY with a reason')
    # `**/.env.*` also names `.env.example`, which holds no values and is where a service records the variables
    # it needs - a feature that adds config has to write it. Blocking it teaches the team the guard is wrong,
    # and the hook's block carries no in-session override, so there is no way around it in the moment.
    if not any(re.search(r'^!.*\.env\.example$', g) for g in glob_blocks(ROOT / 'rules' / 'core' / 'protected-paths.md')):
        fails.append('rules/core/protected-paths.md: `**/.env.*` blocks `.env.example` with no `!` exception - '
                     'that file carries no secret and cannot be written any other way')
    report(fails)


# The one shared list was split between core and the stacks. Nothing may fall out on the way, and what a
# Python-only repo no longer covers is written down here rather than discovered later.
def test_splitting_the_protected_paths_dropped_no_glob():
    before = set(glob_blocks(ROOT / 'tests' / 'fixtures' / 'legacy' / 'protected-paths.md'))
    core, python, typescript = (set(glob_blocks(ROOT / 'rules' / layer / 'protected-paths.md'))
                                for layer in ('core', 'stack-python', 'stack-typescript'))
    assert before - (core | python | typescript) == set()
    assert before - (core | python) == {'**/out/**', '**/*-lock.json', '**/*-lock.yaml'}


# ---------------- secrets (rules G2/A6) ----------------
FORBIDDEN = re.compile(r'''\b(api[_-]?key\s*[:=]\s*['"][\w-]{16,}|secret\s*[:=]\s*['"][\w-]{16,}|postgres://[^@\s]+@(?!localhost|127\.0\.0\.1)[\w.-]+)''', re.I)


def test_no_secret_or_client_connection_string_is_committed():
    fails = []
    for p in (p for p in walk(ROOT) if re.search(r'\.(md|json|py|ya?ml|txt)$', p.name)):
        for i, line in enumerate(read(p).split('\n'), 1):
            # a deliberate fixture opts out with an inline `scan-ok:` marker, the same way rule B3 needs `WHY:`
            if FORBIDDEN.search(line) and 'scan-ok:' not in line:
                fails.append(f'possible secret or client connection string at ./{rel(p)}:{i} (rule G2/A6)')
    report(fails)


# ---------------- documented commands must exist ----------------
# Two shapes count as a command reference: a whole code span (`/plan`) and a line that starts with
# one, which is how the README's workflow block and the shell examples write them. Glob and path
# fragments never match either shape, because they do not begin with a slash.
KNOWN = set(COMMANDS.values()) | set(BUILTINS)


def code_spans(line: str) -> list:
    # Split on backticks and read only the odd segments, which are the code spans. A regex over the
    # whole line matches across a closing backtick (`paths`/aliases looks like a span starting `/aliases`).
    return [s for i, s in enumerate(line.split('`')) if i % 2 == 1]


def test_every_documented_command_exists():
    fails = []
    for p in (p for p in walk(ROOT) if p.suffix == '.md'):
        where_file = rel(p)
        planned_ok = any(where_file.endswith(f) for f in PLANNED_OK_IN)
        history_ok = where_file.endswith('CHANGELOG.md')   # a changelog must be able to name a deleted command
        for i, line in enumerate(read(p).split('\n'), 1):
            refs = []
            for sp in code_spans(line):
                m = re.match(r'^/([a-z][a-z-]*)(?:\s.*)?$', sp)
                if m:
                    refs.append(m.group(1))
            refs.extend(re.findall(r'^\s{0,4}/([a-z][a-z-]*)(?=\s|$)', line))
            for r in dict.fromkeys(refs):
                if r in KNOWN or history_ok:
                    continue
                where = f'./{where_file}:{i}'
                if r in PLANNED:
                    if not planned_ok:
                        fails.append(f'{where} presents /{r} as available, but it is only planned - say so, or drop it')
                else:
                    fails.append(f'{where} references /{r}, which is not a skill in this plugin and not a built-in')
    report(fails)


# ---------------- layer hygiene ----------------
# The invariant that matters is the command-map contract: the CORE HOOKS must not know any
# ecosystem's tooling, because they read the repo's own commands from CLAUDE.md. That stays a
# hard failure. Everywhere else in the core layer a stack term is a smell, not a defect, so it
# warns - a warning keeps the signal without blocking a rule that legitimately cites an example.
# Unambiguous tokens: matched case-insensitively.
STACK_TERMS = re.compile(
    r'\b(pytest|ruff|mypy|pyright|pip|pipenv|poetry|uv|conda|django|flask|fastapi|kivy|numpy|pnpm|yarn|npm run|jest|vitest|eslint|'
    r'prettier|tsconfig|rspec|gradlew|xcodebuild)\b|\.(tsx?|jsx?|py|rb|kt|swift|php)\b', re.I)
# Words that are also ordinary English or a bare product name: only the capitalised spelling counts.
STACK_TERMS_CASED = re.compile(r'\b(Python|TypeScript|JavaScript|Node\.js|React|Django|Flask)\b')


def scan(path) -> list:
    out = []
    for i, line in enumerate(read(path).split('\n'), 1):
        m = STACK_TERMS.search(line) or STACK_TERMS_CASED.search(line)
        if m:
            out.append(f'stack term "{m.group(0)}" at ./{rel(path)}:{i}')
    return out


def test_core_hooks_name_no_tooling():
    fails = [f"{msg} - core hooks must read the repo's command map, never name tooling"
             for h in CORE_HOOKS for msg in scan(ROOT / 'bin' / h)]
    report(fails)


def test_core_rules_and_workflow_skills_stay_stack_neutral():
    warns = [f'{msg} - rules/core is the stack-agnostic layer'
             for r in sorted(os.listdir(ROOT / 'rules' / 'core')) for msg in scan(ROOT / 'rules' / 'core' / r)]
    # setup-project is exempt: installing the stack layer is its job, so it names the stack on purpose.
    for d in (d for d in CORE_SKILLS if d in SKILL_DIRS and d != 'setup-project'):
        for f in (f for f in walk(ROOT / 'skills' / d) if f.suffix == '.md'):
            warns.extend(f'{msg} - workflow skills should stay stack-neutral' for msg in scan(f))
    report([], warns)
