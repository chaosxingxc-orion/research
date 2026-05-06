"""G-RIA-11 (R-W1): doc-truth gate.

Checks that the high-level documentation files describe the actual on-disk
state, not a stale earlier-phase state. Specifically:

1. ARCHITECTURE.md Subpackage Map does NOT carry "Phase 2 - not scaffolded
   yet" wording for subpackages that are actually present on disk.
2. pyproject.toml integration pytest marker description does NOT say
   "stub agent_server" (RIA architecture v2 §0.4 mandates real local
   agent-server subprocess).
3. CLAUDE.md does NOT say "Phase 2 ships R-RIA-7" (stale wording — R-RIA-7
   ships in R-W1 sub-wave 3, not Phase 2).

Exits 0 on PASS, 1 on FAIL.

References:
- ria-architecture-v2.md §0.4
- ria-engineering-plan-r-w1-2026-05-05.md §6
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

ARCHITECTURE_MD = REPO_ROOT / "ARCHITECTURE.md"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
PYPROJECT_TOML = REPO_ROOT / "pyproject.toml"
INTEGRATION_CONFTEST = REPO_ROOT / "tests" / "integration" / "conftest.py"


def _check_pyproject_marker() -> list[str]:
    if not PYPROJECT_TOML.exists():
        return [f"pyproject.toml not at {PYPROJECT_TOML}"]
    text = PYPROJECT_TOML.read_text(encoding="utf-8")
    match = re.search(r'"integration:\s*([^"]*)"', text)
    if not match:
        return ["pyproject.toml: no `integration:` pytest marker found"]
    description = match.group(1)
    findings: list[str] = []
    if "stub agent_server" in description.lower():
        findings.append(
            "pyproject.toml integration marker still says 'stub agent_server' "
            "(stale per ria-architecture-v2.md §0.4)",
        )
    fixture_exists = INTEGRATION_CONFTEST.exists()
    if fixture_exists and "real" not in description.lower():
        findings.append(
            "pyproject.toml integration marker should reference real local "
            "agent-server subprocess (fixture exists at tests/integration/conftest.py)",
        )
    return findings


def _check_claude_md() -> list[str]:
    if not CLAUDE_MD.exists():
        return [f"CLAUDE.md not at {CLAUDE_MD}"]
    text = CLAUDE_MD.read_text(encoding="utf-8")
    findings: list[str] = []
    stale_phrases = [
        "Phase 2 ships R-RIA-7",
        "R-RIA-4, R-RIA-7, R-RIA-8 ship in Phase 2",
    ]
    for phrase in stale_phrases:
        if phrase in text:
            findings.append(f"CLAUDE.md still has stale phrasing: {phrase!r}")
    return findings


def _check_architecture_md() -> list[str]:
    if not ARCHITECTURE_MD.exists():
        return []  # ARCHITECTURE.md is optional in some repo states
    text = ARCHITECTURE_MD.read_text(encoding="utf-8")
    findings: list[str] = []
    orchestration_present = (REPO_ROOT / "ria" / "orchestration" / "compiler.py").exists()
    user_present = (REPO_ROOT / "ria" / "user" / "store.py").exists()
    if orchestration_present and "**Phase 2** — not scaffolded yet" in text:
        # Only flag when the table row for orchestration claims not-scaffolded
        if re.search(
            r"`ria/orchestration/`.*\*\*Phase 2\*\*\s*[—-]\s*not scaffolded yet",
            text,
        ):
            findings.append(
                "ARCHITECTURE.md says 'orchestration/ — Phase 2 not scaffolded' "
                "but ria/orchestration/compiler.py is on disk",
            )
    if user_present and re.search(
        r"`ria/user/`.*\*\*Phase 2\*\*\b",
        text,
    ):
        if "Phase 2 — not scaffolded" in text or "Phase 2** —" in text:
            # Looser check: user/store.py exists, so 'Phase 2' status is stale
            findings.append(
                "ARCHITECTURE.md user/ row claims Phase 2 status but "
                "ria/user/store.py is on disk",
            )
    return findings


def main() -> int:
    findings: list[str] = []
    findings.extend(_check_pyproject_marker())
    findings.extend(_check_claude_md())
    findings.extend(_check_architecture_md())
    if findings:
        print("FAIL G-RIA-11 doc-truth:")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("PASS G-RIA-11 doc-truth")
    return 0


if __name__ == "__main__":
    sys.exit(main())
