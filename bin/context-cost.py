#!/usr/bin/env python3
"""Context cost report: the lines a repository adds to every session. Not a hook; /setup and the tests use it.

Always loaded: CLAUDE.md and .claude/CLAUDE.md, what they import with @path (four hops at most), and every
.claude/rules/**/*.md without a `paths:` key in its frontmatter. Lines are raw lines, as `wc -l` counts them,
comments and frontmatter included. Report only: it never fails a repository.
"""
import re
import sys
from pathlib import Path

MAX_HOPS = 4
FENCED = re.compile(r'^[ \t]*(```|~~~).*?(?:^[ \t]*\1[^\n]*$|\Z)', re.M | re.S)
CODE_SPAN = re.compile(r'(`+)(?:(?!\1).)+?\1', re.S)
# only at a line start or after whitespace, so an address such as name@host is not an import
IMPORT = re.compile(r'(?<!\S)@(\S+)')


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8-sig', errors='replace')


def imports(path: Path) -> list:
    """The existing files `path` imports. A relative import is relative to the importing file."""
    out = []
    for name in IMPORT.findall(CODE_SPAN.sub(' ', FENCED.sub(' ', read(path)))):
        for candidate in (name, name.rstrip('.,;:!?)')):    # "see @notes.md." ends a sentence
            target = path.parent / Path(candidate).expanduser()
            if target.is_file():
                out.append(target)
                break
    return out


def is_path_scoped(path: Path) -> bool:
    m = re.match(r'---\n(.*?)\n---\n', read(path), re.S)
    return bool(m and re.search(r'^paths:', m.group(1), re.M))


def always_loaded(root) -> list:
    """(file, lines) for each file every session loads, each file once."""
    root = Path(root)
    found = {}

    def add(path: Path) -> bool:
        key = path.resolve()
        if key in found:
            return False
        found[key] = (path, len(read(path).splitlines()))
        return True

    level = [p for p in (root / 'CLAUDE.md', root / '.claude' / 'CLAUDE.md') if p.is_file() and add(p)]
    for _ in range(MAX_HOPS):
        level = [t for p in level for t in imports(p) if add(t)]
    for rule in sorted((root / '.claude' / 'rules').rglob('*.md')):
        if rule.is_file() and not is_path_scoped(rule):
            add(rule)
    return list(found.values())


def label(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def main(argv: list) -> int:
    root = Path(argv[1] if len(argv) > 1 else '.')
    rows = sorted(((n, label(p, root)) for p, n in always_loaded(root)), key=lambda r: (-r[0], r[1]))
    print('Lines loaded in every session:')
    for n, name in rows:
        print(f'{n:6}  {name}')
    print(f'{sum(n for n, _ in rows):6}  total')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
