"""G-RIA-10 (R-W1): naming hygiene checks for ria/.

Detects:
- Suffix-versioned directories (-v2, -new, -final, _v2, _new, _final)
- Sibling doublets (X.py and Xs.py at the same dir level; X/ and Xs/ at the
  same dir level) - "naming accretion is a defect" rule
- Empty-shell __init__.py files whose body is non-trivial but contains no
  re-exports or actual public surface

Exits 0 on PASS, 1 on FAIL. Print findings on FAIL.

References:
- CLAUDE.md "Naming / structure accretion is a defect"
- ria-quality-requirements-v1.md (v1.2 G-RIA-10)
- ria-engineering-plan-r-w1-2026-05-05.md §3
"""

from __future__ import annotations

import ast
import sys
from collections.abc import Iterable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RIA_ROOT = REPO_ROOT / "ria"

FORBIDDEN_SUFFIXES: tuple[str, ...] = (
    "-v2",
    "-new",
    "-final",
    "_v2",
    "_new",
    "_final",
)

# Allowed plural file/dir names where the singular co-existing is intentional
# (e.g. domain/role.py for the dataclass + a hypothetical roles/ package).
ALLOWED_DOUBLET_PAIRS: frozenset[tuple[str, str]] = frozenset()


def _check_suffix_versioned(root: Path) -> Iterable[str]:
    for path in root.rglob("*"):
        if path.is_dir() and any(path.name.endswith(s) for s in FORBIDDEN_SUFFIXES):
            yield f"suffix-versioned directory: {path.relative_to(REPO_ROOT)}"


def _doublet_violation(parent: Path, name: str, plural: str) -> bool:
    return (parent.name, name) not in ALLOWED_DOUBLET_PAIRS and (parent.name, plural) not in ALLOWED_DOUBLET_PAIRS


def _check_doublets(root: Path) -> Iterable[str]:
    parents_with_py = {p.parent for p in root.rglob("*.py")}
    for parent in parents_with_py:
        names = {p.stem for p in parent.glob("*.py") if p.stem != "__init__"}
        for name in names:
            if name + "s" in names and _doublet_violation(parent, name, name + "s"):
                yield (
                    f"doublet pair: {parent.relative_to(REPO_ROOT)}/{name}.py "
                    f"+ {name}s.py"
                )

    parents_with_dirs = {p.parent for p in root.rglob("*") if p.is_dir()}
    for parent in parents_with_dirs:
        sub_names = {d.name for d in parent.iterdir() if d.is_dir()}
        for name in sub_names:
            if name + "s" in sub_names and _doublet_violation(parent, name, name + "s"):
                yield (
                    f"doublet dir pair: {parent.relative_to(REPO_ROOT)}/{name} "
                    f"+ {name}s/"
                )


def _is_trivial_init_body(node: ast.stmt) -> bool:
    """Return True for body items that are OK in __init__.py."""
    if isinstance(node, (ast.Pass, ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign)):
        return True
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
        return True  # docstring or constant expression
    return False


def _check_empty_init(root: Path) -> Iterable[str]:
    for init in root.rglob("__init__.py"):
        text = init.read_text(encoding="utf-8").strip()
        if not text:
            continue  # truly empty is OK
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue  # syntax errors are caught by other tooling
        for node in tree.body:
            if not _is_trivial_init_body(node):
                yield (
                    f"non-trivial __init__.py body at "
                    f"{init.relative_to(REPO_ROOT)} "
                    f"line {node.lineno}: {type(node).__name__}"
                )


def main() -> int:
    if not RIA_ROOT.exists():
        print(f"FAIL G-RIA-10 naming-hygiene: ria/ not at {RIA_ROOT}")
        return 1
    findings: list[str] = []
    findings.extend(_check_suffix_versioned(RIA_ROOT))
    findings.extend(_check_doublets(RIA_ROOT))
    findings.extend(_check_empty_init(RIA_ROOT))
    if findings:
        print("FAIL G-RIA-10 naming-hygiene:")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("PASS G-RIA-10 naming-hygiene")
    return 0


if __name__ == "__main__":
    sys.exit(main())
