# tests/_stubs/

**Status:** archive directory for historical stub modules.

Per RIA architecture v2 §5.5 and Wave R-W1 Guard rail 1, **stubs are forbidden
in `tests/integration/**`**. Integration tests run against a real
`agent-server serve` subprocess via the
`tests/integration/conftest.py::real_agent_server` fixture.

This directory exists as the documented archive location for any historical
stub that needs to be retained for unit-test purposes only. As of R-W1
sub-wave 1 launch (2026-05-07), no stub module is on disk; the directory is
reserved for future need.

## Policy

- **Permitted:** unit-test-only stubs that mock a clearly-named external
  boundary (e.g., a third-party API client) for a `tests/unit/` test that
  cannot meaningfully exercise the real boundary.
- **Forbidden:** any stub used by a test under `tests/integration/**` or
  `tests/conformance/**`. G-RIA-20 (`scripts/check_integration_uses_real_server.py`)
  enforces this at CI time by AST-walking the integration tree.

## See also

- `D:\chao_workspace\research\docs\ria\ria-architecture-v2.md` §5.5
- `D:\chao_workspace\research\docs\ria\ria-engineering-plan-r-w1-2026-05-05.md` §7.1
- `tests/integration/conftest.py` — the real-server fixture replacing stub usage
