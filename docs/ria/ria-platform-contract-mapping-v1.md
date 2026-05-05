# RIA → Platform (agent_server v1) Contract Mapping — v1.1

**Document maturity:** M1 — internally reviewed
**Last updated:** 2026-05-04 (v1.1 minor revision per `ria-quality-requirements-v1.md` §10)
**Position:** L1 detail under `ria-architecture-v1.md` and `ria-architecture-v2.md`; binding contract for `ria/platform_client/`
**Compatible platform contract:** `agent_server` v1 (frozen at SHA `8c6e22f1`) — as documented in `D:\chao_workspace\hi-agent\agent_server\ARCHITECTURE.md` §6 and `docs/platform/agent-server-northbound-contract-v1.md` (when published).

> **v1.1 changes vs v1.0** (additive; backwards-compatible per `ria-quality-requirements-v1.md` §10):
> - §2 — adds Phase 3 read operations (`list_recent_runs`, `get_run_history_by_skill`, `query_kg_cross_project`, `list_skill_versions`) — most are **EXPECTED** routes RIA needs hi-agent to expose; current platform-side status noted per row.
> - §2 — adds `get_manifest_posture` as a strongly-typed call (consumes the W34-MANIFEST closure: `posture: Literal["dev","research","prod"]` field on `/v1/manifest`).
> - §4.5 (new) — RIA's deterministic generation rule for the new write operations.
> - §9 — stub mode is deprecated for `tests/integration/`; replaced by `real_agent_server` subprocess fixture (see `ria-architecture-v2.md` §5.5 and `ria-quality-requirements-v1.md` v1.1 §2.1). The stub is retained as `tests/_stubs/agent_server_stub_v1.py` for `tests/unit/` only.
> - §10 — versioning note refreshed: RIA pins agent_server v1; hi-agent v2 work is parallel; conformance suite is the authoritative compatibility check.
> - §11 — out-of-scope list refreshed: Phase 3 reads moved out of the out-of-scope section since they are now expected per §2.

This document is the **complete specification** of how RIA interacts with the hi-agent platform. Every other RIA module reaches the platform through `ria/platform_client/` and through this mapping. Anything that the platform exposes but is not listed here is **not** a supported RIA → platform integration point.

If a future need requires a platform call not listed here, the procedure is: (1) request the call shape from hi-agent (extend their v1 contract or open v2); (2) update this document; (3) implement in `ria/platform_client/`. RIA modules outside `platform_client/` MUST NOT reach the platform through any other path.

---

## 1. Single-Seam Principle

Only `ria/platform_client/` imports `agent_server.contracts.*`. Every RIA module above (orchestration, global_layer, user, api, observability) reaches the platform through `platform_client`'s typed methods. This is enforced by `scripts/check_layering.py` and is the most important rule in this document.

```
ria/orchestration/*          ria/api/*           ria/global_layer/*
        │                       │                       │
        └───────────┬───────────┴───────────────────────┘
                    ▼
           ┌────────────────────┐
           │  ria/platform_client │  ← only path to the platform
           └─────────┬──────────┘
                     ▼   HTTP /v1/* + SSE
              agent_server v1
```

---

## 2. Operation → Route Mapping

Every RIA operation listed here corresponds to exactly one logical platform interaction. The "Idempotency-Key formula" column states the deterministic key generation rule (see §4 for the formal definition).

| RIA operation (caller) | Platform call | Idempotency-Key formula | Tenant scoping |
|---|---|---|---|
| `submit_project(spec)` (orchestration) | `POST /v1/skills` (register PI Agent role) → `POST /v1/runs` (start) | `idem("submit_project", user_id, project_id)` | header `X-Tenant-ID` from resolver |
| `cancel_project(project_id)` (orchestration) | `POST /v1/runs/{run_id}/cancel` | `idem("cancel_project", user_id, project_id)` | header |
| `signal_resume(project_id, gate_id, payload)` (orchestration) | `POST /v1/runs/{run_id}/signal` | `idem("signal_resume", user_id, project_id, gate_id)` | header |
| `get_project_status(project_id)` (orchestration / api) | `GET /v1/runs/{run_id}` | n/a (read) | header |
| `stream_project_events(project_id)` (orchestration / api) | `GET /v1/runs/{run_id}/events` (SSE) | n/a (read) | header |
| `list_project_artifacts(project_id)` (orchestration / global_layer) | `GET /v1/runs/{run_id}/artifacts` | n/a (read) | header |
| `read_artifact(artifact_id)` (global_layer / api) | `GET /v1/artifacts/{artifact_id}` | n/a (read) | header |
| `write_artifact(payload)` (global_layer) | `POST /v1/artifacts` (cold-write-once via content_hash) | `idem("write_artifact", user_id, content_hash)` | header |
| `register_skill(skill_spec)` (orchestration / global_layer) | `POST /v1/skills` | `idem("register_skill", user_id, skill_id, skill_version)` | header |
| `proxy_llm_call(request)` (rare; default is to embed in run) | `POST /v1/llm/complete` | `idem("llm_proxy", user_id, project_id, content_hash(request))` | header |
| `get_capability_manifest()` (operator CLI / startup) | `GET /v1/manifest` | n/a (read) | header (optional) |
| `get_platform_health()` (operator CLI / startup) | `GET /v1/health`, `/v1/ready` | n/a (read) | unscoped |
| `query_tenant_quota()` (operator CLI) | `GET /v1/tenancy/quota` (when supported by platform) | n/a (read) | header |
| `query_tenant_cost()` (operator CLI / budget audit) | `GET /v1/tenancy/cost` (when supported by platform) | n/a (read) | header |
| **`list_recent_runs(tenant_id, since)`** *(v1.1; Phase 3)* | `GET /v1/runs?since=<iso8601>&limit=N` (paginated) — **EXPECTED in W36+; not yet exposed on v1; tracked in W35 acceptance directive §4.4** | n/a (read) | header |
| **`get_run_history_by_skill(skill_id, tenant_id, since)`** *(v1.1; Phase 3)* | `GET /v1/skills/{skill_id}/runs?since=<iso8601>` — **EXPECTED in W36+; not yet exposed on v1** | n/a (read) | header |
| **`list_skill_versions(skill_id, tenant_id)`** *(v1.1; Phase 3; required for Champion-Challenger surfacing per W34 expectations §2.6)* | `GET /v1/skills/{skill_id}/versions` — **EXPECTED in W36+; not yet exposed on v1** | n/a (read) | header |
| **`query_kg_cross_project(tenant_id, query)`** *(v1.1; Phase 3)* | `GET /v1/kg/query?tenant_id=...&q=...` — **EXPECTED in W36+; F.4 closure prerequisite is COMPLETE at hi-agent W34 HEAD `77222f8b`** | n/a (read) | header |
| **`get_manifest_posture()`** *(v1.1; **AVAILABLE** at hi-agent W34 HEAD `77222f8b`)* | `GET /v1/manifest` — strongly-typed parse of the `posture: PostureLiteral` field on `ManifestResponse` (frozen contract digest `cc55145f`); spec'd at `agent_server/contracts/manifest.py` | n/a (read; cached for process lifetime) | header (optional) |

**Notes:**

- "Cold-write-once" semantics for artifacts: same `content_hash` writes return the existing artifact (200 with the same response). Hash mismatch with a different body returns 409 — this is the platform's `ArtifactConflictError`. RIA treats both consistently as "the artifact is at this content_hash."
- `GET /v1/manifest` is called once at RIA process startup to verify capability availability under the configured posture; result is cached for the process lifetime.
- `LLM proxy` is rarely used by RIA directly — most LLM calls happen inside an active platform Run. Direct proxy is only for one-off tool calls (e.g., a CLI helper that summarises a paper without starting a Run).
- *(v1.1; v1.1 erratum 2026-05-05)* The four **EXPECTED** Phase 3 read operations (`list_recent_runs`, `get_run_history_by_skill`, `list_skill_versions`, `query_kg_cross_project`) are not yet exposed on `agent_server` v1 at hi-agent HEAD `77222f8b`. RIA's Phase 3 modules call them under A.3.α policy; the calls return 404 until hi-agent ships the routes. Each 404 surfaces in `red-status.json` as `blocked_by_wave_id: <future-wave>`. RIA will issue a separate routes-extension directive at W35 close to scope these for W36+ delivery (per `hi-agent-wave35-acceptance-and-wave36-expectations-2026-05-05.md` §4.4).
- *(v1.1; v1.1 erratum 2026-05-05)* `get_manifest_posture()` is **AVAILABLE** at hi-agent W34 HEAD `77222f8b`. It returns a strongly-typed `Posture` enum value (`dev` / `research` / `prod`) parsed from `ManifestResponse.posture: PostureLiteral` (frozen at contract digest `cc55145f`). RIA's `Posture.from_platform_manifest_response()` may now rely on the contract field directly; the W33-era best-effort fallback is retired.
- *(v1.1; v1.1 erratum 2026-05-05)* `Idempotency-Key` cross-process replay semantics are **spec'd** at hi-agent W34 HEAD `77222f8b` in `agent_server/contracts/idempotency.py` with `DEFAULT_TTL_SECONDS=86400.0` and `SCOPE='tenant'`. RIA's `platform_client/idempotency.py` may implement against this frozen contract.
  - *Carryover concern (W35-T4):* the current `IdempotencyStore` does not actually purge expired records; SQLite grows unbounded. RIA-HIGH-priority signal in `hi-agent-wave35-acceptance-and-wave36-expectations-2026-05-05.md` §3.3 (feasibility-blocking on Lens 7). RIA's `tests/integration/test_idempotency_ttl_purge*` is mapped to `blocked_by_wave_id: W35-T4` until W35 closes.

---

## 3. Tenant, User, Project Scoping

### 3.1 Identity propagation

| Identity | Where it lives | How it reaches the platform |
|---|---|---|
| `user_id` | RIA-only; `ria/user/identity.py` | NEVER sent to platform; resolved into `tenant_id` by `ria/platform_client/tenant_resolver.py` |
| `tenant_id` | platform-side scope | sent in `X-Tenant-ID` header on every request |
| `project_id` | RIA-allocated UUID v4 | sent in request body for write routes; sent as query param `?project_id=` for some read routes |
| `profile_id` | platform-side scope | sent in request body for write routes |
| `run_id` | platform-allocated | learned in `POST /v1/runs` response; persisted by RIA in `ria/user/store.py` for resumption |

### 3.2 Tenant resolver semantics (`ria/platform_client/tenant_resolver.py`)

| RIA `RIA_POSTURE` | Resolution rule |
|---|---|
| `dev` | All users → `tenant_dev`. Single-tenant operation. |
| `research` | One tenant per organisational unit. Mapping configured in `RIA_TENANT_MAP_PATH` JSON (e.g. `{"chaos.xing.xc@gmail.com": "tenant_acme_lab"}`). |
| `prod` | One tenant per organisational unit + JWT validates the user belongs to that tenant. JWT issuer set in `RIA_JWT_ISSUER_URL`. |

The resolver is called exactly once per inbound request, before any platform call. The result is attached to the per-request `RIAContext` and read by `platform_client` calls.

### 3.3 ACL boundary

User-level ACL is **RIA-only**. Examples:

- "Alice owns project P1; Bob is a collaborator with read-write."
- "Carol is the editor for project P3; she can approve Gate F."

The platform sees only `tenant_id` and `project_id`. It does not enforce per-user ACL — that is RIA's job. RIA's `ria/user/acl.py` is checked **before** the platform call. If ACL denies, `platform_client` is never invoked.

This is defensive layering: even if RIA's ACL fails-open due to a bug, the platform's tenant isolation still prevents cross-tenant data leakage. But the application-level ACL is the primary enforcement.

---

## 4. Idempotency-Key Generation

### 4.1 Formal definition

```python
def idem(operation: str, *parts: str) -> str:
    """
    Generate a deterministic Idempotency-Key for a RIA → platform write call.

    The key is stable across RIA restarts and across user retries: the same
    inputs produce the same key, so the platform short-circuits to the cached
    response.

    `operation`  — short namespacing literal (e.g., "submit_project")
    `parts`      — domain-meaningful identifying values, in caller-defined order
    """
    canonical = "|".join((operation, *parts)).encode("utf-8")
    return "ria:" + hashlib.sha256(canonical).hexdigest()
```

### 4.2 Required-key operations

The following platform calls **must** carry an `Idempotency-Key` header (per platform `prod` posture and per RIA R-RIA-5):

- `POST /v1/runs`
- `POST /v1/runs/{run_id}/cancel`
- `POST /v1/runs/{run_id}/signal`
- `POST /v1/skills`
- `POST /v1/artifacts`
- `POST /v1/llm/complete`

Read-only calls (`GET /v1/*`) do not carry idempotency keys.

### 4.3 Replay semantics (we expect from the platform)

If RIA sends the same `Idempotency-Key` + same body twice:

- The platform returns the previously cached response (typically 200 / 201) with the same payload.

If RIA sends the same `Idempotency-Key` + a different body:

- The platform returns 409 Conflict with `error_category: idempotency_conflict`. RIA surfaces this as a domain-level `IdempotencyConflict` error.

If RIA sends a different `Idempotency-Key` + the same body (e.g., orchestrator restart with non-deterministic key generation — must not happen in v1):

- The platform treats it as a new request. This is why the key must be deterministic.

### 4.4 RIA's deterministic generation rule (per operation)

| Operation | Key parts (in order) |
|---|---|
| `submit_project` | `user_id`, `project_id` |
| `cancel_project` | `user_id`, `project_id` |
| `signal_resume` | `user_id`, `project_id`, `gate_id` |
| `register_skill` | `user_id`, `skill_id`, `skill_version` |
| `write_artifact` | `user_id`, `content_hash` |
| `proxy_llm_call` | `user_id`, `project_id`, `content_hash(request_body)` |

The script `scripts/check_idempotency_keys.py` verifies that every write method in `ria/platform_client/transport_*.py` calls `idem(...)` and that the operation name + parts match this table.

### 4.5 Phase 3 read operations (v1.1) — no idempotency keys

The four Phase 3 read operations (`list_recent_runs`, `get_run_history_by_skill`, `list_skill_versions`, `query_kg_cross_project`) are read-only and do not carry `Idempotency-Key`. They follow `agent_server` v1's standard read-route conventions: `X-Tenant-ID` header, optional `?since=` / `?limit=` query params, JSON response.

`get_manifest_posture()` is a read-only convenience wrapper around `GET /v1/manifest` that parses the response into a strongly-typed `Posture` enum. It does not carry an Idempotency-Key. The result is cached for the RIA process lifetime; RIA polls `/v1/manifest` periodically (`RIA_MANIFEST_POLL_INTERVAL_SECONDS`, default 300) to detect platform posture changes per `ria-quality-requirements-v1.md` §11 "What is the policy for hi-agent posture changes mid-deployment?".

---

## 5. Long-Run Resumption Protocol

PI Agent Runs live for weeks. RIA must survive its own process restarts without disturbing platform Runs.

### 5.1 Persistence schema (`ria/user/store.py` SQLite)

```
table active_projects (
    project_id        TEXT PRIMARY KEY,
    user_id           TEXT NOT NULL,
    tenant_id         TEXT NOT NULL,
    platform_run_id   TEXT NOT NULL,
    last_event_cursor TEXT,                    -- platform SSE cursor
    last_known_state  TEXT NOT NULL,           -- queued|running|paused|done|cancelled|failed
    last_known_phase  TEXT,
    last_seen_at      TIMESTAMP NOT NULL,
    created_at        TIMESTAMP NOT NULL
)
```

### 5.2 Resumption procedure (RIA process startup)

```
on_startup():
    for row in active_projects where last_known_state in {queued, running, paused}:
        # 1. Refresh state
        status = platform_client.get_project_status(row.project_id)
        ria/user/store.py update_state(row.project_id, status.state, status.current_stage)

        # 2. If still active, resubscribe SSE from cursor
        if status.state in {queued, running, paused}:
            spawn_task(platform_client.stream_project_events(
                row.project_id,
                cursor=row.last_event_cursor,
            ))
        # 3. Sync gates and acceptance criteria from latest events
        ria/orchestration/replanner.py reconcile(row.project_id)
```

Resumption is idempotent — running it twice produces the same end state. RIA's restart does not generate new platform calls beyond `GET /v1/runs/{id}` per active project + SSE resubscribe.

### 5.3 SSE consumer rules (`ria/platform_client/streaming.py`)

- Reconnect on disconnect with exponential backoff (cap 30 s).
- On reconnect, resume from the last seen cursor.
- Each event updates the `last_event_cursor` in `ria/user/store.py` **before** RIA acts on it (write-ahead).
- If an event arrives with a cursor older than `last_event_cursor`, drop it (replay protection).

### 5.4 Cancellation contract

`cancel_project(project_id)` produces:

| Platform response | RIA action |
|---|---|
| 200 with `state: cancelled` | RIA marks project `ABANDONED` in store; closes SSE |
| 404 (run_id unknown to platform) | RIA logs structural drift; marks project `ABANDONED`; raises `RIA.ProjectStateLost` |
| 5xx | RIA retries up to 3 times with exponential backoff; on persistent failure, raises `RIA.PlatformUnavailable` and leaves project state unchanged (cancellation will be re-attempted on next operator action) |

Per platform's documented contract (`agent_server/ARCHITECTURE.md` §6), **404 on cancellation of an unknown run_id is the correct behaviour**, not 200. RIA depends on this for state-drift detection.

---

## 6. Human Gate Protocol (Pause-on-Token / Resume-with-Input)

### 6.1 Pause flow

When the platform Run reaches a pause point (e.g., AC failure with `on_fail_action=HUMAN_GATE_D`):

1. Platform emits SSE event `{"type": "gate_pending", "pause_token": "...", "context": {...}}`.
2. `ria/platform_client/streaming.py` receives the event; updates `last_event_cursor`.
3. `ria/orchestration/replanner.py` translates the platform event into a domain `GateState(kind=GATE_D, decision=PENDING, ..., platform_pause_token=token)`.
4. RIA persists the GateState; project status flips to `PAUSED`.
5. RIA notifies the user (CLI prints, MCP emits notification, HTTP API exposes via `GET /research/projects/{id}/gates/pending`).

### 6.2 Resume flow

When the user resolves the gate (`research gate D approve --remediation '<text>'`):

1. RIA reads the `GateState`, validates user has gate-approval ACL on the project.
2. RIA constructs the resume payload: `{"gate_id": "...", "decision": "approve", "input": {...}}`.
3. RIA calls `POST /v1/runs/{run_id}/signal` with body `{"signal_type": "resume_with_input", "pause_token": <token>, "payload": <resume payload>}` and `Idempotency-Key: idem("signal_resume", user_id, project_id, gate_id)`.
4. Platform returns 200; RIA updates the GateState to `decision=APPROVE`, `decided_at=now`, `decided_by_user_id=...`.
5. Project status flips back to `ACTIVE`. SSE resumes streaming events.

### 6.3 Multi-step gates

Gates D / E / F may produce successive pauses (e.g., Gate D approve → Gate E pause for ethics). Each pause is a new `GateState` with its own `gate_id`. RIA does not collapse them.

---

## 7. Error Envelope Translation

Platform error envelope (per `agent_server/contracts/errors.py`):

```json
{
  "error_category": "<one of: not_found | conflict | rate_limited | invalid_input | unauthorised | unauthorized | unavailable | internal>",
  "message": "<human-readable>",
  "retryable": true | false,
  "next_action": "<optional hint string>"
}
```

RIA mapping (`ria/platform_client/errors.py`):

| Platform `error_category` | HTTP status | RIA domain error | RIA HTTP status (on user-facing API) |
|---|---|---|---|
| `not_found` | 404 | `RIA.ProjectNotFound` / `RIA.ArtifactNotFound` | 404 |
| `conflict` | 409 | `RIA.IdempotencyConflict` / `RIA.ArtifactConflict` | 409 |
| `rate_limited` | 429 | `RIA.PlatformBudgetExceeded` | 429 |
| `invalid_input` | 400 | `RIA.PlatformContractMismatch` | 500 (RIA bug — should not happen with type checks) |
| `unauthorised` / `unauthorized` | 401 | `RIA.PlatformAuthFailure` | 500 (RIA bug — token issue) |
| `unavailable` | 503 | `RIA.PlatformUnavailable` | 503 |
| `internal` | 500 | `RIA.PlatformInternalError` | 503 |

**Retry policy** (`ria/platform_client/transport_http.py`):

- `retryable=true` and HTTP in {5xx, 429}: retry with exponential backoff, capped at 3 attempts. Idempotency-Key carried unchanged.
- `retryable=false`: no retry; surface as RIA domain error.
- Network errors (timeout, connection reset): retry up to 3 attempts (treated as `retryable=true`).

**Never retry on:** 400, 401, 403, 404, 409. These are deterministic outcomes of the request shape; retrying does not change them.

---

## 8. Observability Threading

Every RIA → platform call carries:

- `X-Trace-Id`: a UUID v4 generated by RIA at entry-protocol layer; attached to logs, metrics, and platform calls. Platform reflects it in event log so the chain can be reconstructed.
- `X-Span-Id`: per-call span id; parent of any platform-side spans.
- `X-RIA-User-Id-Hash`: sha256(user_id) — for cross-system join without leaking user identity. Optional; off by default.

Counters (Prometheus, exposed at RIA's `/ria/metrics`):

- `ria_platform_call_total{operation, status}`
- `ria_platform_call_duration_seconds{operation}` (histogram)
- `ria_idempotency_replay_total{operation}` — when platform returns a cached response
- `ria_platform_retry_total{operation, attempt}`
- `ria_platform_unavailable_total{operation}`

These counters are RIA-side; the platform has its own counters. The two are joined via `trace_id`.

---

## 9. Stub Mode — Deprecated for `tests/integration/` (v1.1)

**v1 framing (historical).** Phase 1 development used a stub `agent_server` at `tests/integration/_stubs/agent_server_stub.py` while the hi-agent W31 BLOCKERs were unresolved. The stub was the basis for `tests/integration/` PASS claims.

**v1.1 framing (current; per `ria-architecture-v2.md` §0.4 + §5.5 and `ria-quality-requirements-v1.md` v1.1 §2.1).** The stub is **deprecated** for `tests/integration/` and is **forbidden** under that pytest marker (enforced by G-RIA-20: `scripts/check_integration_uses_real_server.py`). All `tests/integration/` tests now run against a real `agent-server serve` subprocess via the `real_agent_server` session-scope fixture.

**What happens to the stub:**

- The file is moved from `tests/integration/_stubs/agent_server_stub.py` to `tests/_stubs/agent_server_stub_v1.py` (deprecation move; explicit "do not extend" tag).
- Permitted use: `tests/unit/` for fast TDD red phase only.
- Forbidden use: `tests/integration/` (G-RIA-20 fails CI).

**Why deprecated.** Per `ria-architecture-v2.md` §5.5 "A.3.α — Forcing-Function Test Discipline": mock-based / stub-based development was the dominant rework cause in 2026-04 / 2026-05. RIA applies CLAUDE.md's "Using mocks to bypass real failures is strictly forbidden" rule at the `integration` boundary. Red CI driven by real platform gaps is the desired state; the red-status JSON (per `ria-quality-requirements-v1.md` v1.1 §13) operationalises the cross-team forcing function.

**`AGENT_SERVER_BASE_URL` configuration.** `ria/platform_client/transport_http.py` continues to accept `AGENT_SERVER_BASE_URL`. In production it points at hi-agent's deployed `agent-server serve`. In `tests/integration/`, the `real_agent_server` fixture spawns a local `agent-server serve` subprocess and exports the URL into the test environment.

The conformance suite (`tests/conformance/`) remains the single source of truth for "what real platform behaviour does RIA depend on" — and v1.1 strengthens this: conformance runs against the real local `agent-server serve` for platform conformance, plus periodically against live external services for `external_services/` conformance (per `ria-architecture-v2.md` §5.2).

---

## 10. Versioning

This mapping document is versioned alongside `agent_server` v1. When the platform team ships v2 (breaking change), RIA writes `ria-platform-contract-mapping-v2.md` and a parallel `ria/platform_client/v2/` subpackage. Both v1 and v2 mappings coexist for the deprecation window (≥ 2 platform waves), so RIA can support either platform version during a deployment-controlled migration.

The current document explicitly does **not** describe v2 — that is future work.

---

## 11. Out of Scope (Explicit Non-Goals) — refreshed in v1.1

The following platform capabilities are **not** consumed by RIA, even though the platform exposes them:

- Direct LLM proxy for chains of multi-turn tool calls outside a Run — RIA always wraps multi-turn work as a Run.
- Tenant-level quota administration — RIA queries quota for budget reporting; tenant quota provisioning is an operator-side action, not a RIA-side action.
- Direct kernel ports / `hi_agent.*` modules — these are R-RIA-1 forbidden imports.
- Platform v2 contract surface — RIA pins v1; v2 is a future migration when hi-agent ships it (≥ 2 platform waves of overlap required per architecture-improvement directive A-01).

**v1.1 promotion** (moved out of v1 out-of-scope into v1.1 in-scope):

- ~~Platform-level skill A/B versioning — RIA's `global_layer/evolution_engine.py` will use it eventually, but Phase 3+.~~ → **Now in §2 as `list_skill_versions`** (EXPECTED in W34/W35).
- ~~Knowledge-graph backend protocol direct access — RIA reads KG state through Run-produced artifacts only.~~ → **Now in §2 as `query_kg_cross_project`** (EXPECTED in W34/W35; depends on F.4 closure).

Listing these explicitly so future implementers know not to wire them in `platform_client` without revising this document first.

---

**End of Platform Contract Mapping v1.1.**
