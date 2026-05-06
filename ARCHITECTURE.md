# Research Intelligence Application (RIA) — L0 Architecture

**Document maturity:** M1 — internally reviewed
**Last updated:** 2026-05-07 (post hi-agent W35-corrective acceptance; RIA Wave R-W1 sub-wave 1 in flight)
**Type:** Top-level architecture summary

This file is the **brief** L0 view of RIA. The full canonical specs live under `docs/ria/`:

- L0 architecture (full): [`docs/ria/ria-architecture-v1.md`](docs/ria/ria-architecture-v1.md)
- Domain model: [`docs/ria/ria-domain-model-v1.md`](docs/ria/ria-domain-model-v1.md)
- Platform contract mapping: [`docs/ria/ria-platform-contract-mapping-v1.md`](docs/ria/ria-platform-contract-mapping-v1.md)
- Quality requirements: [`docs/ria/ria-quality-requirements-v1.md`](docs/ria/ria-quality-requirements-v1.md)

---

## Three-Layer Stack

```
┌───────────────────────────────────────────────────────┐
│  Entry Protocols   (CLI · MCP · HTTP/SSE)             │
└──────────────────┬────────────────────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────────────────────┐
│  RIA   (this repo, ria/ package)                      │
│   domain · orchestration · global_layer · user        │
│   platform_client (single seam to platform)           │
└──────────────────┬────────────────────────────────────┘
                   │  HTTP /v1/* + SSE  (agent_server v1)
                   ▼
┌───────────────────────────────────────────────────────┐
│  hi-agent platform   (separate repo, separate process)│
│   agent_server  → hi_agent  → agent_kernel            │
└──────────────────┬────────────────────────────────────┘
                   │ HTTPS (sole egress)
                   ▼
                LLM providers
```

## Subpackage Map (R-W1 sub-wave 1 in progress — tri-state PRESENT / IN-PROGRESS / PLANNED)

| Path | Purpose | Status |
|---|---|---|
| `ria/config/` | Settings + RIA posture (`dev`/`research`/`prod`) | PRESENT |
| `ria/platform_client/` | Single seam to `agent_server` v1 (seam 1) | PRESENT (4 of 8 modules; `transport_mcp` / `run_lifecycle` / `streaming` / `budget_enforcer` IN-PROGRESS in R-W1) |
| `ria/domain/` | Pure domain dataclasses | PRESENT (3 of 17; 14 additional modules IN-PROGRESS in R-W1 sub-wave 2) |
| `ria/observability/` | Counters / tracing / audit / red-status | PRESENT (counters); `tracing` / `audit` / `red_status` IN-PROGRESS in R-W1 sub-wave 3 |
| `ria/api/cli/` | Operator + researcher CLI | PRESENT |
| `ria/orchestration/` | PI Agent compiler + phase pipeline | PRESENT (compiler + pi_agent); `phase_pipeline` / `backtrack` / `replanner` / `project_state` IN-PROGRESS in R-W1 |
| `ria/user/` | user_id / ACL / per-user budget | PRESENT (identity + store); `acl` / `budget` IN-PROGRESS in R-W1 |
| `ria/external_services/` | Second outbound seam (arxiv / S2 / DOI / GitHub / Lean / Zenodo / HF) | PLANNED — IN-PROGRESS in R-W1 sub-wave 2 |
| `ria/global_layer/` | Paper Archive / Lean Library / Dataset Registry / Evolution | PLANNED — IN-PROGRESS in R-W1 sub-wave 3 |
| `ria/api/{mcp,http}/` | MCP server + front-end HTTP | PLANNED — IN-PROGRESS in R-W1 sub-wave 3 |

## Eight Boundary Rules

Enforced by `scripts/check_*.py` gates; full text in `CLAUDE.md` §"RIA Boundary Rules".

| ID | Rule (one-liner) |
|---|---|
| R-RIA-1 | No `hi_agent.*` / `agent_kernel.*` imports anywhere under `ria/**` |
| R-RIA-2 | `ria/domain/**` imports only stdlib (no `agent_server.contracts.*` either) |
| R-RIA-3 | Only `ria/platform_client/**` may import `agent_server.contracts.*` |
| R-RIA-4 | Entry-protocol layer uses research-domain vocabulary, not platform verbs |
| R-RIA-5 | Every `ria/platform_client/transport_*.py` write generates `Idempotency-Key` |
| R-RIA-6 | RIA `prod` posture requires platform posture ≥ `research` (startup assertion) |
| R-RIA-7 | New route handlers / facade methods carry `# tdd-red-sha:` annotation |
| R-RIA-8 | Persistent dataclasses declare `tenant_id` and/or `project_id` as required |

## Platform Compatibility

| RIA version | Platform contract | Tested-against HEAD |
|---|---|---|
| RIA 0.1 (R-W1 in flight) | hi-agent `agent_server` v1 | hi-agent W35-corrective-CLOSE (`ad521c07`) |

**Platform status (verified 2026-05-07):** W34 + W35 + W35 corrective all CLOSED at M2; `verified_readiness=72.0` held by `t3_deferred` cap (clears at next manifest cycle with passing real-Volces) + `soak_evidence_not_real` cap (held per RIA's architectural-feasibility-only stance). All 8 RIA dimensions (T, I, R, C, D, E, L, N) satisfy our consumer-side criterion. W36 binding work in flight per `docs/hi-agent-wave36-engineering-expectations-2026-05-05.md` + supplement directive `docs/hi-agent-w35-corrective-acceptance-and-w36-supplement-directive-2026-05-07.md`.

**RIA-side R-W1 wave** (RIA's first explicit engineering wave; ~5 weeks; brings v2 architecture to ~95% on-disk coverage) is in flight. See `docs/ria/ria-engineering-plan-r-w1-2026-05-05.md`.

## Run Local

```bash
# Install (Phase 1 scaffold)
pip install -e ".[test,lint]"

# Lint + tests
ruff check ria/ scripts/
pytest tests/unit

# Smoke against hi-agent (when running)
export AGENT_SERVER_BASE_URL=http://localhost:8000
ria smoke
```

## See Also

- Hi-agent architecture: `D:\chao_workspace\hi-agent\ARCHITECTURE.md` (separate repo)
- Wave 31 acceptance: [`docs/hi-agent-wave31-acceptance-2026-05-03.md`](docs/hi-agent-wave31-acceptance-2026-05-03.md)
- Wave 31 directive (closed): [`docs/hi-agent-wave31-blocker-closure-requirements-2026-05-02.md`](docs/hi-agent-wave31-blocker-closure-requirements-2026-05-02.md)
