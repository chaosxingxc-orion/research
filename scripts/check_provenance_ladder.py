"""G-RIA-12 (R-W1): provenance ladder gate.

Every JSON file emitted by RIA that contains a ``provenance`` field must
use one of the canonical CLAUDE.md ladder values:

    measured, derived, simulated, illustrative, unverified

Scope is limited to RIA-emitted JSON under ``docs/ria/`` (red-status
artifacts, RIA verification snapshots). Hi-agent JSON imported into
``docs/`` for inter-team correspondence uses hi-agent's own vocabulary
(``real``, ``shape_verified``, etc.) per CLAUDE.md "Stakeholder vocabulary"
- those are not policed here.

This gate walks ``docs/ria/`` recursively, parses each .json file, and
validates any ``provenance`` field at any nesting depth. Files that fail
to parse as JSON are flagged (corruption / wrong extension).

Exits 0 on PASS, 1 on FAIL.

References:
- CLAUDE.md "Evidence Integrity" + "Stakeholder vocabulary"
- ria-architecture-v2.md §5.6 schema v1.1
- ria-engineering-plan-r-w1-2026-05-05.md §3
"""

from __future__ import annotations

import json
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
RIA_DOCS_ROOT = REPO_ROOT / "docs" / "ria"

CANONICAL: frozenset[str] = frozenset(
    {"measured", "derived", "simulated", "illustrative", "unverified"},
)


def _walk_provenance(obj: Any, path: str) -> Iterator[str]:
    """Yield findings for each invalid ``provenance`` value found in obj."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "provenance" and isinstance(value, str):
                if value not in CANONICAL:
                    yield (
                        f"{path}: provenance={value!r} not in canonical "
                        f"ladder {sorted(CANONICAL)}"
                    )
            yield from _walk_provenance(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            yield from _walk_provenance(item, f"{path}[{index}]")


def main() -> int:
    if not RIA_DOCS_ROOT.exists():
        print("PASS G-RIA-12 provenance-ladder (docs/ria/ absent — vacuous)")
        return 0
    findings: list[str] = []
    for json_file in sorted(RIA_DOCS_ROOT.rglob("*.json")):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            findings.append(
                f"{json_file.relative_to(REPO_ROOT)}: malformed JSON ({exc})",
            )
            continue
        findings.extend(
            _walk_provenance(data, str(json_file.relative_to(REPO_ROOT))),
        )
    if findings:
        print("FAIL G-RIA-12 provenance-ladder:")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("PASS G-RIA-12 provenance-ladder")
    return 0


if __name__ == "__main__":
    sys.exit(main())
