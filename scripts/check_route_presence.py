"""G-RIA-13 (R-W1): route-presence probe in real_agent_server fixture.

Mirrors hi-agent W36-A5 B13 silent-route-omission defence on the consumer
side. The fixture at ``tests/integration/conftest.py::real_agent_server``
must:

1. Define a non-empty module-level ``REQUIRED_ROUTES`` tuple.
2. Within the fixture body (before yield), call a function whose name
   contains "probe_route" (e.g., ``_probe_route_presence``).

If either is missing, the consumer-side defence is broken and the fixture
could yield against a partially-served platform without the integration
test suite noticing.

Exits 0 on PASS, 1 on FAIL.

References:
- hi-agent ``docs/governance/boot-time-assertions-roadmap.md`` (B13)
- ria-engineering-plan-r-w1-2026-05-05.md §3 + §7.2 Guard rail 2
- tests/integration/conftest.py::real_agent_server
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFTEST = REPO_ROOT / "tests" / "integration" / "conftest.py"


def _has_required_routes(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id == "REQUIRED_ROUTES"
                    and isinstance(node.value, ast.Tuple)
                    and node.value.elts
                ):
                    return True
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "REQUIRED_ROUTES"
            and isinstance(node.value, ast.Tuple)
            and node.value.elts
        ):
            return True
    return False


def _fixture_calls_probe_route(tree: ast.Module) -> tuple[bool, bool]:
    """Return (fixture_found, probe_called)."""
    fixture_func: ast.FunctionDef | ast.AsyncFunctionDef | None = None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "real_agent_server":
                fixture_func = node
                break
    if fixture_func is None:
        return False, False
    for sub in ast.walk(fixture_func):
        if isinstance(sub, ast.Call):
            func_name = ""
            if isinstance(sub.func, ast.Name):
                func_name = sub.func.id
            elif isinstance(sub.func, ast.Attribute):
                func_name = sub.func.attr
            if "probe_route" in func_name.lower():
                return True, True
    return True, False


def main() -> int:
    if not CONFTEST.exists():
        print(f"FAIL G-RIA-13 route-presence: {CONFTEST.relative_to(REPO_ROOT)} does not exist")
        return 1
    text = CONFTEST.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        print(f"FAIL G-RIA-13 route-presence: cannot parse conftest.py ({exc})")
        return 1
    findings: list[str] = []
    if not _has_required_routes(tree):
        findings.append(
            "REQUIRED_ROUTES module-level tuple is missing or empty in "
            "tests/integration/conftest.py",
        )
    fixture_found, probe_called = _fixture_calls_probe_route(tree)
    if not fixture_found:
        findings.append(
            "real_agent_server fixture function not found at module top level",
        )
    elif not probe_called:
        findings.append(
            "real_agent_server fixture does not call a *probe_route* function "
            "before yield (silent-route-omission defence missing)",
        )
    if findings:
        print("FAIL G-RIA-13 route-presence:")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("PASS G-RIA-13 route-presence")
    return 0


if __name__ == "__main__":
    sys.exit(main())
