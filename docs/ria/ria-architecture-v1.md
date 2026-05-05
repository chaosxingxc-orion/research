# Architecture: Research Intelligence Application (RIA) — v1

**Document maturity:** M1 — internally reviewed
**Last updated:** 2026-05-02
**Repository:** `D:\chao_workspace\research\`

> **Document hierarchy**
> - L0 system boundary: this file
> - L1 domain detail: `ria-domain-model-v1.md`
> - L1 platform-mapping detail: `ria-platform-contract-mapping-v1.md`
> - L1 quality detail: `ria-quality-requirements-v1.md`
> - Architecture-discussion archive (decision provenance): `docs/superpowers/specs/2026-04-29-ria-agent-server-integration-architecture.md`

This is the canonical L0 architecture for the Research Intelligence Application. It supersedes the architecture sections of the 2026-04-29 discussion archive at the points where they differ.

---

## 1. Introduction and Goals

RIA is the **research-domain application layer** that drives long-running PI Agent research projects on the hi-agent platform. RIA is the only system above hi-agent that:

- Knows research-domain concepts (Project, Phase, Hypothesis, Claim, Acceptance Criterion, Paper, Theorem, Experiment, Dataset, Review, PI Agent role).
- Owns user-level identity, ACL, and per-user budget envelopes.
- Drives entry protocols for human use (CLI, MCP for Codex/Claude Code, HTTP/SSE for a web front-end).

RIA does **not** execute agent runs, manage agent memory, route LLM calls, or persist run state. Those are platform concerns owned by hi-agent's `agent_server` v1 northbound contract.

### 1.1 Primary goals

1. Compile a `ResearchProjectSpec` into a platform `RunRequest` + `SkillSpec` set that hi-agent's `agent_server` can execute deterministically.
2. Maintain user-level identity, ACL, and per-user budget *above* the platform's per-tenant envelope.
3. Provide three entry protocols (CLI, MCP, HTTP/SSE) that speak research-domain vocabulary, not platform vocabulary.
4. Curate cross-project assets (Paper Archive, Lean Library, Dataset Registry, Evolution Engine).
5. Stay strictly above the platform boundary — never import `hi_agent.*` or `agent_kernel.*`, never reach LLM providers directly.

### 1.2 Quality requirements (binding)

See `ria-quality-requirements-v1.md`. Headlines:

- 0 imports of `hi_agent.*` or `agent_kernel.*` from any RIA module (CI gate).
- All RIA write operations to the platform carry an `Idempotency-Key`.
- TDD red-sha annotation on every new route handler / facade method.
- RIA's own posture system (dev / research / prod) coupled to platform posture: RIA `prod` requires platform ≥ `research`.

---

## 2. Constraints

| Constraint | Source |
|---|---|
| Python 3.12+ | Match hi-agent runtime; `pyproject.toml` |
| FastAPI/Starlette for HTTP entry | Same stack as platform; reduces operator skill duplication |
| `httpx` for platform_client transport | Async-first; matches hi-agent's HTTP gateway pattern |
| `mcp` Python SDK for MCP server | Codex / Claude Code MCP integration |
| SQLite for RIA-owned persistence (user ACL, budget, project metadata) | No second database operator; RIA's persistence is independent of platform persistence |
| RIA's domain layer (`ria/domain/`) is pure stdlib | `ria-quality-requirements-v1.md` R-RIA-2 |
| RIA never imports `hi_agent.*` or `agent_kernel.*` | R-RIA-1 |
| Only `ria/platform_client/` may import `agent_server.contracts.*` | R-RIA-3 |
| All entry-protocol surfaces (CLI/MCP/HTTP) speak research-domain vocabulary | R-RIA-4 |
| All platform write operations carry `Idempotency-Key` | R-RIA-5 |

---

## 3. System Context

```
┌────────────────────────────────────────────────────────────────────────┐
│  Researchers / Operators / Front-end                                   │
│    ┌──────────────────┐    ┌────────────────┐    ┌──────────────────┐  │
│    │ Codex / CC (MCP) │    │ Web front-end  │    │ Operator CLI     │  │
│    └────────┬─────────┘    └───────┬────────┘    └────────┬─────────┘  │
└─────────────┼─────────────────────┼──────────────────────┼─────────────┘
              │ MCP                 │ HTTP / SSE            │ stdin/stdout
              ▼                     ▼                       ▼
┌────────────────────────────────────────────────────────────────────────┐
│  RIA process (this repo)                                               │
│    ria/api/{mcp,http,cli}                                              │
│    ria/{domain, orchestration, global_layer, user, observability}      │
│    ria/platform_client (single seam to platform)                       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ HTTP /v1/* + SSE  (agent_server v1)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│  hi-agent platform (separate repo, separate process, separate ops)     │
│    agent_server/  (northbound facade)                                  │
│    hi_agent/      (runtime kernel; RIA never sees)                     │
│    agent_kernel/  (execution substrate; RIA never sees)                │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ HTTPS (sole egress to model providers)
                                   ▼
                       LLM Providers (Anthropic / OpenAI / Volces Ark)
```

**Downstream consumers of RIA:** researchers using Codex / Claude Code; researchers using a web front-end; operators using the CLI.

**Upstream dependency of RIA:** exactly one — hi-agent's `agent_server` v1 northbound contract over HTTP. No other upstream dependency is permitted in `ria/platform_client/`.

---

## 4. Solution Strategy

| Decision | Rationale |
|---|---|
| Three-layer architecture (entry-protocol → RIA domain → platform) | Established in the 2026-04-29 discussion archive D1; UI is not RIA, RIA is not platform. |
| `agent_server` is southbound-delivered by hi-agent, not implemented by RIA | Discussion archive D2; multi-tenancy / quota / audit / streaming are written once and shared across consumers. |
| Model providers reachable only through hi-agent's LLMGateway | D3; preserves determinism, cost optimisation, and evolution-engine telemetry. |
| Entry protocols connect to RIA, not directly to `agent_server` | D4; user-facing protocols are research-shaped, not generic-agent-shaped. |
| RIA domain layer is pure stdlib (no platform imports) | Lets us swap platforms without rewriting domain logic. |
| RIA owns user-level ACL and budget; platform owns tenant-level quota | Layering: RIA maps user → project → platform tenant; platform never sees user_id. |
| TDD red-sha discipline mirrored from hi-agent's R-AS-5 | Consistent test-first discipline across both teams. |
| RIA's own dev/research/prod posture, coupled to platform posture | RIA can be in `dev` while platform is in `research`; RIA in `prod` requires platform ≥ `research`. |

---

## 5. Building Block View

```
┌──────────────────────────────── ria ─────────────────────────────────────┐
│                                                                          │
│  ┌─── api ────────────────────────────────────────────────────────────┐  │
│  │   cli/      (research project new / status / approve)              │  │
│  │   mcp/      (MCP tools for Codex / CC)                             │  │
│  │   http/     (HTTP / SSE for front-end)        [Phase 2]            │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                              │                                           │
│                              ▼                                           │
│  ┌─── orchestration ──────────────────────────────────────────────────┐  │
│  │   pi_agent.py        — PI Agent role spec → SkillSpec compiler     │  │
│  │   phase_pipeline.py  — 6-step writing-team / phase machine          │  │
│  │   backtrack.py       — Backtrack policy when AC fails              │  │
│  │   replanner.py       — StageDirective wiring (calls /signal)       │  │
│  │   compiler.py        — ResearchProjectSpec → RunRequest+SkillSpec  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                              │                                           │
│  ┌── global_layer ──────────┐│┌─── domain ────────────────────────────┐  │
│  │ paper_archive.py         │││  project · phase · hypothesis · claim │  │
│  │ lean_library.py          │││  paper · theorem · experiment · ...    │  │
│  │ dataset_registry.py      │││  role · gate semantics                 │  │
│  │ evolution_engine.py      │││                                        │  │
│  │  [Phase 3]               │││  pure stdlib · no platform imports     │  │
│  └──────────────────────────┘│└────────────────────────────────────────┘  │
│                              │                                           │
│                              ▼                                           │
│  ┌─── platform_client ───────────────────────────────────────────────┐   │
│  │   transport_http.py  — async HTTP client for /v1/*                 │   │
│  │   transport_mcp.py   — MCP client (alt transport, same surface)    │   │
│  │   tenant_resolver.py — RIA user_id → platform tenant_id            │   │
│  │   budget_enforcer.py — Per-user budget BEFORE call                 │   │
│  │   run_lifecycle.py   — Long-run resumer + checkpoint discipline    │   │
│  │   streaming.py       — SSE consumer (cooperative backpressure)     │   │
│  │   idempotency.py     — Idempotency-Key generator + retry           │   │
│  │   errors.py          — platform.ContractError → RIA domain error   │   │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─── user ─────────────────────┐  ┌─── observability ───────────────┐   │
│  │ identity (user↔profile)      │  │ counters · tracing · audit       │   │
│  │ acl (project ACL)            │  │ (RIA-owned, separate from        │   │
│  │ budget (per-user envelope)   │  │  platform observability)         │   │
│  │ store (SQLite)               │  │                                  │   │
│  └──────────────────────────────┘  └──────────────────────────────────┘   │
│                                                                          │
│  ┌─── config ─────────┐                                                  │
│  │ settings · posture  │                                                 │
│  └─────────────────────┘                                                 │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼  HTTP /v1/* + SSE
                          (only seam to platform)
```

### 5.1 Subpackage responsibilities

| Subpackage | Responsibility | Allowed imports | Forbidden imports |
|---|---|---|---|
| `ria/domain/` | Pure domain dataclasses + invariants | stdlib only | `agent_server.*`, `hi_agent.*`, httpx, starlette, fastapi |
| `ria/orchestration/` | Compile `ResearchProjectSpec` into platform calls; phase pipeline; backtrack | `ria.domain.*`, `ria.platform_client.*` | `hi_agent.*`, `agent_kernel.*` |
| `ria/global_layer/` | Cross-project assets (Paper Archive, Lean Library, Dataset Registry, Evolution Engine) | `ria.domain.*`, `ria.platform_client.*` | `hi_agent.*`, `agent_kernel.*` |
| `ria/platform_client/` | Single seam to hi-agent's `agent_server` v1 | `agent_server.contracts.*` (as type shape only); httpx | `hi_agent.*`, `agent_kernel.*` |
| `ria/user/` | Application-level identity / ACL / per-user budget | stdlib + sqlite3 | platform types |
| `ria/api/cli/` | Operator + researcher CLI | `ria.*` | platform types (except `errors`) |
| `ria/api/mcp/` | MCP server for Codex / Claude Code | `ria.*` + mcp lib | platform types (except `errors`) |
| `ria/api/http/` | HTTP / SSE for front-end | `ria.*` + starlette / fastapi | platform types (except `errors`) |
| `ria/observability/` | RIA-owned counters / tracing / audit | `ria.*` | platform types |
| `ria/config/` | Settings + posture | stdlib | platform types |

CI enforcement of this matrix is in `scripts/check_layering.py` (see `ria-quality-requirements-v1.md` §3).

---

## 6. Runtime View

The canonical happy-path flow: a researcher submits a new research project.

```
Researcher        ria/api/cli       ria/orchestration       ria/platform_client       agent_server
    │                  │                    │                       │                     │
    │ research project │                    │                       │                     │
    │  new <topic>     │                    │                       │                     │
    │─────────────────▶│                    │                       │                     │
    │                  │  resolve user_id   │                       │                     │
    │                  │  → profile_id      │                       │                     │
    │                  │  build spec        │                       │                     │
    │                  │───────────────────▶│ ResearchProjectSpec   │                     │
    │                  │                    │  compile to platform  │                     │
    │                  │                    │  RunRequest+SkillSpec │                     │
    │                  │                    │─────────────────────▶│                     │
    │                  │                    │                       │ POST /v1/skills     │
    │                  │                    │                       │  (PI Agent role)    │
    │                  │                    │                       │  + Idempotency-Key  │
    │                  │                    │                       │────────────────────▶│
    │                  │                    │                       │ ◀ skill_id          │
    │                  │                    │                       │ POST /v1/runs       │
    │                  │                    │                       │  (project_id, goal, │
    │                  │                    │                       │   skill_id, …)      │
    │                  │                    │                       │  + Idempotency-Key  │
    │                  │                    │                       │────────────────────▶│
    │                  │                    │                       │ ◀ {run_id, queued}  │
    │                  │                    │ ◀ run_id              │                     │
    │                  │ ◀ project_id       │                       │                     │
    │ ◀ {project_id,   │                    │                       │                     │
    │    run_id, queued}                    │                       │                     │
    │                                                                                     │
    │ research project status <project_id>                                                │
    │────────────────▶│                     │                       │                     │
    │                  │ GET status         │                       │                     │
    │                  │───────────────────▶│ get_project_status    │                     │
    │                  │                    │─────────────────────▶│                     │
    │                  │                    │                       │ GET /v1/runs/{id}   │
    │                  │                    │                       │────────────────────▶│
    │                  │                    │                       │ ◀ {state, stage, …} │
    │                  │                    │                       │ + tenant scope      │
    │ ◀ {state, current_phase, last_event}                                               │
```

**Resumption contract:** if the RIA process restarts, `ria/orchestration/run_lifecycle.py` re-resolves every active project's `run_id` from `ria/user/store.py` and resubscribes to SSE; the platform run is unaffected by RIA restarts.

**Cancellation contract:** `research project cancel <project_id>` calls `POST /v1/runs/{run_id}/cancel`. Known live run → 200 + terminal; unknown run id → 404. RIA propagates the platform error to the user as a domain error.

**Human-gate contract:** when a phase reaches Gate D (PI diagnosis + remediation) the platform run pauses with a `gate_pending` event. RIA persists the gate context, exposes it through `research gate D show`, and waits for `research gate D approve|reject` to call `POST /v1/runs/{run_id}/signal` with the resume payload. The platform does not know what "Gate D" is; that semantic lives in `ria/domain/gate.py`.

---

## 7. Deployment View

```
┌── Host (Linux / Windows) ─────────────────────────────────────────────────┐
│                                                                           │
│  ┌── PM2 / systemd ──────────────────────────────────────────────────┐    │
│  │                                                                    │    │
│  │  ria process                                                       │    │
│  │  ───────────                                                       │    │
│  │   - python -m ria serve         (CLI entry; hosts MCP + HTTP)     │    │
│  │   - posture: research                                             │    │
│  │   - depends-on: agent_server (HTTP base URL via env)              │    │
│  │                                                                    │    │
│  │  agent_server process (separately deployed by hi-agent team)      │    │
│  │  ─────────────────────                                             │    │
│  │   - python -m agent_server serve                                  │    │
│  │   - posture: research                                             │    │
│  │   - depends-on: hi_agent runtime in-process                       │    │
│  │                                                                    │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌── Data directories (RIA-owned) ──────────────────────────────────┐    │
│  │   $RIA_DATA_DIR/ria.sqlite     (user, ACL, budget, project meta) │    │
│  │   $RIA_DATA_DIR/audit.jsonl    (RIA audit trail)                 │    │
│  │   $RIA_DATA_DIR/checkpoints/   (project-level checkpoints)       │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌── Data directories (platform-owned) ─────────────────────────────┐    │
│  │   (managed by agent_server / hi_agent — RIA does not touch)      │    │
│  └───────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────┘
```

**Standard startup:**

```bash
# 1. Install
pip install -e ".[ria]"

# 2. Configure
export RIA_POSTURE=research
export RIA_DATA_DIR=/var/lib/ria
export AGENT_SERVER_BASE_URL=http://localhost:8000
export AGENT_SERVER_AUTH_TOKEN=<token-issued-by-hi-agent-ops>

# 3. Serve (foreground)
python -m ria serve --host 0.0.0.0 --port 8100

# 4. Serve under PM2 (production)
pm2 start "python -m ria serve --host 0.0.0.0 --port 8100" --name ria
```

**Posture matrix:**

| `RIA_POSTURE` | Min platform posture | Tenant context | Idempotency-Key | Per-user budget |
|---|---|---|---|---|
| `dev` | any | optional (defaults to `tenant_dev`) | optional | optional |
| `research` | `research` or `prod` | required | required for write routes | required |
| `prod` | `prod` | required + JWT validation | required for write routes | required + audit log |

**Readiness endpoints:** `GET /ria/health` (200 ready, 503 otherwise), `GET /ria/diagnostics` (compact fingerprint of resolved env/config), `GET /ria/metrics` (Prometheus).

---

## 8. Cross-Cutting Concepts

### 8.1 Logging

Structured logging (`logging` + JSON formatter). Every cross-system call (RIA → platform) emits a structured log with `(trace_id, project_id, run_id, user_id, tenant_id)` so the chain can be reconstructed across both processes.

### 8.2 Error handling

- Platform errors are typed: `agent_server.contracts.errors.ContractError` and subclasses.
- `ria/platform_client/errors.py` translates them to RIA domain errors:
  - `NotFoundError(404)` → `RIA.ProjectNotFound`
  - `ConflictError(409)` → `RIA.IdempotencyConflict`
  - `RateLimitedError(429)` → `RIA.PlatformBudgetExceeded`
  - generic 5xx → `RIA.PlatformUnavailable`
- RIA never re-raises raw `httpx` exceptions to its callers; the seam translates everything.

### 8.3 Posture

`RIA_POSTURE = {dev, research, prod}` (default `dev`) is read by `ria/config/posture.py::Posture.from_env()`. It is read at every enforcement call site:

- `dev` is permissive (single-user CLI use; user_id auto-defaulted; budget warnings logged).
- `research` and `prod` are fail-closed: `user_id` required, `project_id` required on every write, idempotency keys required, per-user budget enforced before platform call.

### 8.4 Security

- User identity is JWT-validated under `prod`. The JWT issuer is configured per deployment.
- ACL is resource-level; project ACL governs read / write / approve-gate permissions.
- RIA never trusts the request body for identity — middleware resolves identity from auth header into `RIAContext` injected into request state.
- Per-user budget is enforced *before* the platform call. If the user exhausts their envelope, RIA refuses; the platform call never happens.
- Path traversal in workspace operations is blocked at `ria/platform_client/` before sending to the platform (defence in depth — the platform also checks).

### 8.5 Idempotency

Every RIA → platform write call carries an `Idempotency-Key`. The key is deterministic: `sha256(user_id, project_id, operation_type, content_hash)`. Two consequences:

- Replays are safe across both RIA and platform restarts.
- A retry from the user (e.g., flaky front-end) does not double-create projects or runs.

`scripts/check_idempotency_keys.py` enforces that every write call in `ria/platform_client/transport_*.py` produces a key.

### 8.6 Long-run resumption

PI Agent runs can live weeks. RIA persists `(project_id, run_id, last_seen_event_cursor)` in `ria/user/store.py` after every meaningful state change. On RIA restart, `ria/orchestration/run_lifecycle.py` resumes:

1. Load all active projects from store.
2. For each project, `GET /v1/runs/{run_id}` to refresh state.
3. Resubscribe to `GET /v1/runs/{run_id}/events?cursor=<last_seen>` SSE.

The platform's run is unaffected by RIA restarts. The platform's run is unaffected by RIA process upgrades.

### 8.7 Tenant resolution

RIA maps `user_id` → platform `tenant_id` via `ria/platform_client/tenant_resolver.py`. The mapping is configurable per deployment:

- `dev` posture: 1 tenant for all users (`tenant_dev`).
- Single-org `prod`: 1 tenant for all users in the org.
- Multi-tenant `prod`: 1 tenant per organisational unit; users within the unit share workspace scope.

`project_id` is RIA-owned and unique per RIA installation. Platform sees `project_id` as opaque scope.

---

## 9. Architecture Decisions

| ID | Decision | Source |
|---|---|---|
| ADR-RIA-1 | Three-layer architecture (entry → RIA → platform) | 2026-04-29 archive D1 |
| ADR-RIA-2 | `agent_server` is southbound-delivered by hi-agent | Archive D2 |
| ADR-RIA-3 | LLM provider reachable only via hi-agent | Archive D3 |
| ADR-RIA-4 | Entry protocols connect to RIA, not to `agent_server` | Archive D4 |
| ADR-RIA-5 | RIA domain layer is pure stdlib | This doc §2 |
| ADR-RIA-6 | RIA owns user / ACL / budget; platform owns tenant / quota | This doc §3 |
| ADR-RIA-7 | TDD red-sha annotation on every new route + facade method | Mirrored from hi-agent R-AS-5 |
| ADR-RIA-8 | RIA's posture system independent but coupled to platform posture | This doc §8.3 |
| ADR-RIA-9 | All RIA → platform writes carry Idempotency-Key | This doc §8.5 |
| ADR-RIA-10 | RIA never imports `hi_agent.*` or `agent_kernel.*` | R-RIA-1 |

---

## 10. Quality Requirements

See `ria-quality-requirements-v1.md` for the full bar. Headlines (binding):

| Quality attribute | Target | Enforcement |
|---|---|---|
| Layering integrity | 0 imports of `hi_agent.*`/`agent_kernel.*` from any RIA module | `scripts/check_layering.py` |
| Domain purity | `ria/domain/*` imports only stdlib | `scripts/check_no_platform_types.py` |
| Idempotency coverage | Every platform-write call carries a key | `scripts/check_idempotency_keys.py` |
| TDD evidence | Every route handler / facade method has `# tdd-red-sha:` | `scripts/check_tdd_evidence.py` |
| Test pass rate | All unit + integration tests pass; conformance suite passes against agent_server stub | CI |
| Long-run resume | RIA process kill mid-run; restart; project resumes against same platform run_id | `tests/integration/test_run_lifecycle_restart.py` |
| Soak | RIA-side ≥ 4h soak driving real research workloads | `tests/soak/` |
| Posture coverage | All write paths posture-aware (dev=warn, research=fail-closed, prod=fail-closed + audit) | posture matrix tests |

---

## 11. Risks and Technical Debt

| Item | Status | Mitigation |
|---|---|---|
| hi-agent W31 BLOCKERs (B-1, B-2, B-3 in directive 2026-05-02) not yet closed | Open | RIA Phase 1 uses stub agent_server; Phase 2 integration deferred until W31 acceptance gates green |
| Cross-tenant data partition at platform KG/skill/tool registry not closed (B-5) | Open on platform side | RIA enforces user-level ACL above; defence-in-depth |
| Front-end UI surfaces (Gate Console, KG Browser, Experiment Dashboard) not designed | Phase 3+ | Acceptable; CLI + MCP cover Phase 1-2 |
| Evolution Engine (cross-project skill / route deltas) not implemented | Phase 3 | Acceptable; per-project evolution handled by platform's PostmortemEngine |
| `ria/platform_client/` is the single point of failure for platform compatibility | By design | Layering rule + conformance suite + frozen v1 contract minimise blast radius |

---

## 12. Glossary

| Term | Definition |
|---|---|
| RIA | Research Intelligence Application — this codebase |
| Project | A research investigation; the unit of long-running work; weeks to months in duration |
| Phase | A named stage within a Project; six phases in the writing-team pipeline |
| PI Agent | Principal Investigator Agent — the long-running TRACE Run that drives a Project |
| Hypothesis | A research hypothesis associated with a Project |
| Claim | An assertion the PI Agent commits to in service of a Hypothesis |
| Acceptance Criterion (AC) | A falsifiable test for a Claim; if AC fails, Backtrack policy fires |
| Backtrack | A controlled retraction of Claims when an AC fails; PI Agent re-plans |
| Gate D / E / F | Human-gate decision points (PI diagnosis, ethics review, publication readiness) |
| Paper Archive | Cross-project curated paper library |
| Lean Library | Cross-project verified-theorem library |
| Dataset Registry | Cross-project versioned dataset registry |
| Evolution Engine | Cross-project skill / route improvement loop |
| Tenant | Platform-level scope; many users may share one tenant |
| User | RIA-level identity; one user owns many projects |
| Profile | hi-agent platform concept; a `profile_id` is a configuration bundle |
| Posture | dev / research / prod — fail-closed level |
| platform_client | RIA's only seam to hi-agent; thin async HTTP/MCP client |
| TDD red-sha | Annotation pointing to the commit where the RED test for this code was first written |

---

## 13. Boundary Rules (CI-Enforced)

These rules are not conventions — each is a CI gate.

| ID | Rule | Gate script |
|---|---|---|
| **R-RIA-1** | `ria/*` MUST NEVER import from `hi_agent.*` or `agent_kernel.*` | `scripts/check_layering.py` |
| **R-RIA-2** | `ria/domain/*` MUST NOT import `agent_server.contracts.*` (domain decoupled from protocol) | `scripts/check_no_platform_types.py` |
| **R-RIA-3** | `ria/platform_client/*` is the only subpackage allowed to import `agent_server.contracts.*` | `scripts/check_layering.py` |
| **R-RIA-4** | `ria/api/{cli,mcp,http}/*` route handlers / tools / commands MUST use research-domain vocabulary, not platform vocabulary | `scripts/check_no_generic_verbs.py` |
| **R-RIA-5** | All write methods in `ria/platform_client/transport_*.py` MUST generate an `Idempotency-Key` | `scripts/check_idempotency_keys.py` |
| **R-RIA-6** | RIA `prod` posture requires platform posture ≥ `research`; checked at startup | `ria/config/posture.py` startup assertion |
| **R-RIA-7** | Every new route handler / facade method has a `# tdd-red-sha: <sha>` annotation pointing to the RED-test commit | `scripts/check_tdd_evidence.py` |
| **R-RIA-8** | All persistent dataclasses in `ria/user/`, `ria/orchestration/`, `ria/global_layer/` declare `tenant_id` or `project_id` (or both) as required fields | `scripts/check_contract_spine_completeness.py` |

---

**End of L0 Architecture v1.**
