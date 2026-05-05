# RIA Quality Requirements — v1.1

**Document maturity:** M1 — internally reviewed
**Last updated:** 2026-05-04 (v1.1 minor revision per §10)
**Position:** L1 detail under `ria-architecture-v1.md` (and v2 from 2026-05-04); binding standard for every RIA module

> **v1.1 changes vs v1.0** (additive; backwards-compatible per §10):
> - §1 — adds **R-RIA-9** (two-seam outbound boundary) introduced by `ria-architecture-v2.md`.
> - §2.1 — L2 integration tests are now defined as "real RIA wiring against a real local `agent-server serve` subprocess" (was "stub `agent_server`"); the historical stub becomes `tests/_stubs/agent_server_stub_v1.py` retained but not used under the `integration` marker.
> - §3 — adds **G-RIA-19** (R-RIA-9 enforcement), **G-RIA-20** (integration-uses-real-server), **G-RIA-21** (cassette age, advisory).
> - §2.2 — adds anti-pattern **AP-9** (defense-in-depth shim that masks a known platform gap).
> - §9, §12 — cross-reference rows extended to include `ria-architecture-v2.md` and `hi-agent-wave34-engineering-expectations-2026-05-04.md`.
> - **New §13** "Forcing-Function Red-Status Discipline" describing the `docs/ria/red-status/<head>.json` artifact and its CI emission contract.

This document specifies RIA's quality bar. It is the single authoritative source of (a) the binding boundary rules R-RIA-1..**9**, (b) the test discipline, (c) the CI gates that enforce both, (d) the posture coupling rules with the platform, (e) the soak / chaos / observability requirements, (f) the maturity ladder for RIA-produced documents and software, and (g) **the forcing-function red-status discipline that operationalises RIA → hi-agent feedback at the CI layer**.

If a downstream rule conflicts with this document, this document wins for RIA. If this document conflicts with `CLAUDE.md` (the workspace-level rules), `CLAUDE.md` wins; bring the conflict back to update this document.

---

## 1. Boundary Rules (Binding, CI-Enforced)

Each rule below has (a) a one-line statement, (b) the rationale, (c) the exact CI gate script that enforces it, (d) the failure mode if the gate is bypassed.

### R-RIA-1 — No platform-internal imports

**Rule:** No file under `ria/**` may import from `hi_agent.*` or `agent_kernel.*`.

**Rationale:** RIA is the application layer; the platform is the platform layer. Direct imports across the layer boundary defeat hi-agent's freedom to refactor internals and tie RIA to specific platform versions.

**Gate:** `scripts/check_layering.py` — AST-walk every `ria/**/*.py`; fail on any matching `Import` or `ImportFrom` node.

**Bypass cost:** RIA Phase 2 onwards becomes coupled to hi-agent's internal module names. A platform-side rename breaks RIA without crossing a contract gate.

### R-RIA-2 — Domain layer is platform-pure

**Rule:** No file under `ria/domain/**` may import `agent_server.contracts.*` or anything platform-shaped (httpx, starlette, fastapi, mcp).

**Rationale:** The domain layer must be portable across platforms. If RIA ever wants to swap the underlying agent platform, only `platform_client/` rewrites; `domain/` is stable.

**Gate:** `scripts/check_no_platform_types.py` — same AST walk, scoped to `ria/domain/**`.

### R-RIA-3 — Single seam to platform

**Rule:** Only `ria/platform_client/**` may import `agent_server.contracts.*`. No other RIA subpackage may.

**Rationale:** Every byte of the platform's response must be translated into RIA-domain types at the seam, not leaked deeper. Layering invariant.

**Gate:** `scripts/check_layering.py` — second pass: check that `agent_server.contracts.*` imports outside `platform_client/` are zero.

### R-RIA-4 — Entry-protocol layer speaks research vocabulary

**Rule:** Files under `ria/api/{cli,mcp,http}/**` MUST NOT use platform-generic verbs (`run`, `skill`, `memory`, `artifact`) as user-visible names. They MUST use research-domain vocabulary (`research project`, `gate D`, `paper`, `theorem`).

**Rationale:** User-facing protocols must speak the user's language, not the platform's.

**Gate:** `scripts/check_no_generic_verbs.py` — grep CLI command names, MCP tool names, HTTP route paths under `ria/api/**` against a forbidden vocabulary set: `{run, skill, memory, artifact, signal, capability}`. Deny list. (Internal helper functions may use these names; only user-visible identifiers are checked.)

### R-RIA-5 — All platform writes are idempotent

**Rule:** Every method in `ria/platform_client/transport_*.py` that issues a `POST` or `PUT` MUST call `idem(...)` from `ria/platform_client/idempotency.py` to generate the `Idempotency-Key` header. The operation name + parts MUST match the table in `ria-platform-contract-mapping-v1.md` §4.4.

**Rationale:** RIA process restarts and user retries must not double-create state.

**Gate:** `scripts/check_idempotency_keys.py` — AST walk: for every `httpx.AsyncClient.post`, `httpx.AsyncClient.put`, etc. call inside `ria/platform_client/`, verify the `headers` argument resolves to a dict containing `"Idempotency-Key"`, and that the value flows through `idem(...)`.

### R-RIA-6 — Posture coupling

**Rule:** RIA `prod` requires platform posture ≥ `research`. RIA startup checks the platform posture via `GET /v1/manifest` (or equivalent) and refuses to start if the platform is in `dev` while RIA is in `prod`.

**Rationale:** Production RIA must not run on a permissive (`dev`) platform — fail-closed semantics need to be honoured end-to-end.

**Gate:** `ria/config/posture.py::Posture.assert_compatible_with_platform(platform_posture)` — called from `ria/__main__.py` startup; raises `PostureMismatch` if violated. Integration test `tests/integration/test_posture_coupling.py` verifies the assertion in all 9 (RIA × platform) posture pairs.

### R-RIA-7 — TDD evidence on new handlers / facades

**Rule:** Every new function in `ria/api/{cli,mcp,http}/**` (a route handler, MCP tool, or CLI command) and every new method in `ria/platform_client/transport_*.py` carries a `# tdd-red-sha: <sha>` annotation pointing to the commit SHA where the failing-CI red test for that function was first committed.

**Rationale:** Evidence-based test discipline; mirrors hi-agent R-AS-5. Without this annotation, "test pass" claims are unverifiable.

**Gate:** `scripts/check_tdd_evidence.py` — AST walk: for every `def` or `async def` in the listed paths, locate the preceding line(s); fail unless one is `# tdd-red-sha:` followed by 7+ hex chars. The annotation's SHA must resolve in `git log` (referenced commit must exist).

### R-RIA-8 — Persistent records carry scope

**Rule:** Every dataclass under `ria/{user,orchestration,global_layer}/**` that is persisted (saved to SQLite, written to disk, sent over the network) MUST declare `tenant_id` and/or `project_id` as required (non-Optional) fields.

**Rationale:** Mirrors hi-agent's contract spine completeness. Multi-tenant safety must be structurally enforced, not just behaviourally.

**Gate:** `scripts/check_contract_spine_completeness.py` (RIA-side) — AST walk: for every `@dataclass` whose module path matches the listed prefixes and which appears as a field type in `ria/user/store.py` schema or as a request/response body in `ria/api/**`, verify it has a `tenant_id: str` or `project_id: str` field (or both).

### R-RIA-9 — Two-seam outbound boundary (v1.1; introduced by ria-architecture-v2)

**Rule:** Files outside `ria/platform_client/**` and `ria/external_services/**` MUST NOT directly import `httpx`, `requests`, `urllib`, `urllib3`, `aiohttp`, `mcp.client.*`, `subprocess`, `asyncio.create_subprocess_exec`, `asyncio.create_subprocess_shell`, or raw `socket` / `ssl`. Outbound I/O is confined to the two seams: `platform_client/` (hi-agent platform calls) and `external_services/` (non-platform external service calls).

**Rationale:** Two reasons. (1) Outbound I/O is the most consequential point of platform-vs-not-platform separation; conflating them at the import level leaks platform concerns into application code or external-service concerns into platform-aware code. Either failure mode is structural debt that scales with codebase size. (2) A single auditable "what does RIA call out to" surface is critical for tenant isolation, security review, and cost attribution. Mirrors hi-agent's W32–W33 two-seam pattern (`agent_server/bootstrap.py` + `agent_server/runtime/**`); RIA endorsed that pattern in W32 acceptance §4.1 and W33 acceptance.

**Permitted exceptions** (with `# r-ria-9-exception: <reason>` annotation):
- `ria/api/http/` may import `starlette`, `fastapi`, `uvicorn` for the *inbound* HTTP server — these are not outbound I/O.
- `ria/api/mcp/` may import `mcp.server.*` for the *inbound* MCP stdio server — not outbound.
- `ria/observability/` may import `prometheus_client` or equivalent metrics-emission libraries.

**Gate:** `scripts/check_external_services_seam.py` — AST-walk every `ria/**/*.py`. For each `Import` / `ImportFrom`, check the imported module against the forbidden list and the importing module's path. Fail on any unannotated violation.

**Bypass cost:** Outbound I/O scattered across the codebase becomes invisible in audits, undiscoverable in security review, and structurally couples `global_layer/` to specific external-service shapes. The R-RIA-9 boundary is the single point at which RIA can replace, mock, or disable an outbound dependency.

---

## 2. Test Discipline

### 2.1 Three test layers (per CLAUDE.md Rule 4)

| Layer | Path | Description | Mock policy |
|---|---|---|---|
| **L1 Unit** | `tests/unit/` | Per-function, function-purity testing | Mocks allowed for stdlib I/O (file system, time, network); mocks of RIA collaborators allowed; cassettes allowed for `external_services/` clients |
| **L2 Integration** *(v1.1: real local agent-server)* | `tests/integration/` | Real RIA wiring against a real local `agent-server serve` subprocess (session-scope fixture `real_agent_server`) | NO mocks of RIA modules. **NO stub of `agent_server`.** Real `agent-server serve` subprocess is required. For `external_services/`, cassettes are permitted to keep the test loop deterministic. Mocks of LLM providers explicitly denied at this layer (the real platform handles them). |
| **L3 E2E** | `tests/e2e/` | Full system: HTTP entry → RIA → real platform → real LLM provider | NO mocks. NO cassettes. Requires a running `agent_server` and real LLM credentials. |
| **L4 Conformance** | `tests/conformance/` | Black-box conformance: RIA's contract obligations to the platform; periodic conformance against live external services | For platform: replays a fixed cassette of platform responses; validates RIA's request shapes and idempotency-key generation. For external services: scheduled CI job runs against live; not part of every commit. |
| **L5 Soak** | `tests/soak/` | Long-running tests under realistic load | Real platform required; ≥ 4 hour duration |

**v1.1 stub deprecation note.** The v1 stub `tests/integration/_stubs/agent_server_stub.py` is moved to `tests/_stubs/agent_server_stub_v1.py` and tagged "historical — do not extend". Stubs are permitted in `tests/unit/` for fast TDD red phase only; no test under the `integration` marker may use them. This is enforced by **G-RIA-20** (see §3).

### 2.2 Anti-patterns explicitly forbidden

| AP | Description | Detection |
|---|---|---|
| **AP-1** | `MagicMock` of a RIA module imported as `from ria.xxx import yyy; yyy = MagicMock()` in `tests/integration/` | `scripts/check_test_honesty.py` |
| **AP-2** | Test that asserts only `state in {...}` instead of a specific terminal state | code review checklist |
| **AP-3** | `try / except: pass` around the test body | `scripts/check_test_honesty.py` |
| **AP-4** | `time.sleep(N>5)` to sync with async events (use `asyncio.wait_for` or event-driven primitives) | code review checklist |
| **AP-5** | Mock that conceals missing wiring (e.g., a stubbed `tenant_resolver` that always returns `tenant_dev` even in research-posture tests) | `scripts/check_test_honesty.py` |
| **AP-6** | `pytest.mark.skip` without `expiry_wave: <name>` annotation | `scripts/check_pytest_skip_discipline.py` |
| **AP-7** | `pytest.mark.xfail` without a reason and a tracked issue | `scripts/check_pytest_xfail_discipline.py` |
| **AP-8** | A `# noqa` annotation added in the same commit as the line it suppresses | `scripts/check_noqa_discipline.py` |
| **AP-9** *(v1.1)* | A defense-in-depth shim in RIA that masks a known platform gap (e.g., a lineage-proxy in `ria/platform_client/` that fills empty `parent_run_id` from RIA's own tracking when hi-agent's F.2 is unclosed) | code review checklist; `scripts/check_no_platform_gap_shims.py` (Phase 3) |

**AP-9 rationale.** Defense-in-depth shims that are planned to retire when the platform closes a gap are the same shape as the "naming accretion is a defect" pattern from W31 §B-6 — debt that lives forever because each wave optimises for not adding it. The correct response to a known platform gap is to surface it via the red-status forcing function (§12), not to mask it.

### 2.3 Per-PR checklist (mirrored from `agent-server-tdd-outline-2026-04-30.md`)

Every PR description must include:

```
- [ ] RED test committed first; SHA: <sha>
- [ ] Each new handler/facade has `# tdd-red-sha: <sha>` annotation
- [ ] Posture validated: <dev|research|prod>
- [ ] Layer 1 (unit) tests added or updated
- [ ] Layer 2 (integration) tests added or updated for new platform calls
- [ ] No `MagicMock` of `ria.*` in `tests/integration/`
- [ ] All `# noqa` annotations carry `expiry_wave:` or `scope:` reason
- [ ] No new platform call types added without updating `ria-platform-contract-mapping-v1.md`
```

CI fails on missing checklist or missing required annotations.

### 2.4 Test honesty audit cadence

A quarterly audit (`docs/ria/audits/<date>-test-honesty.md`) reviews:

- Total `MagicMock` count by directory.
- Drift from "real-component" baseline at each integration boundary.
- Top 10 longest `pytest.mark.skip` reasons by age.
- Top 10 oldest `expiry_wave:` annotations.

Audit is published; cap on score (similar to hi-agent's `cap_factors`) until any P0 finding is closed.

---

## 3. CI Gate Inventory

The full set of CI gates RIA enforces. Each is a script under `scripts/` and a step in `release-gate.yml` (mirrored pattern from hi-agent).

| ID | Gate | Script | Blocking? |
|---|---|---|---|
| G-RIA-1 | Layering: no `hi_agent.*` / `agent_kernel.*` in `ria/**` | `scripts/check_layering.py` | yes |
| G-RIA-2 | Domain purity: `ria/domain/**` is platform-pure | `scripts/check_no_platform_types.py` | yes |
| G-RIA-3 | Single seam: `agent_server.contracts.*` only in `ria/platform_client/` | `scripts/check_layering.py` (pass 2) | yes |
| G-RIA-4 | Vocabulary: entry-protocol layer uses research-domain names | `scripts/check_no_generic_verbs.py` | yes |
| G-RIA-5 | Idempotency keys on writes | `scripts/check_idempotency_keys.py` | yes |
| G-RIA-6 | Posture coupling | `tests/integration/test_posture_coupling.py` | yes |
| G-RIA-7 | TDD evidence | `scripts/check_tdd_evidence.py` | yes |
| G-RIA-8 | Contract spine completeness | `scripts/check_contract_spine_completeness.py` | yes |
| G-RIA-9 | Test honesty: no MagicMock of `ria.*` in `tests/integration/` | `scripts/check_test_honesty.py` | yes |
| G-RIA-10 | Skip discipline: every `pytest.mark.skip` has `expiry_wave` | `scripts/check_pytest_skip_discipline.py` | yes |
| G-RIA-11 | Noqa discipline: every `# noqa` carries `expiry_wave:` or `scope:` | `scripts/check_noqa_discipline.py` | yes |
| G-RIA-12 | Provenance honesty: no `simulated`/`illustrative`/`unverified` evidence in headline claims | `scripts/check_evidence_provenance.py` | yes |
| G-RIA-13 | No hardcoded wave strings in source (besides governance configs) | `scripts/check_no_hardcoded_wave.py` | yes |
| G-RIA-14 | Doc truth: capability/status fields byte-equal across canonical docs | `scripts/check_doc_truth.py` | yes |
| G-RIA-15 | Soak evidence at release: `provenance: real`, ≥ 4h | `scripts/check_soak_evidence.py` | yes (release only) |
| G-RIA-16 | Conformance suite passes against current platform v1 contract | `tests/conformance/` | yes |
| G-RIA-17 | Default-offline clean-env reproducibility | `scripts/verify_clean_env.py` | yes |
| G-RIA-18 | No shell packages: every subpackage has either real content or `# stub-reason:` | `scripts/check_no_shell_packages.py` | yes |
| **G-RIA-19** *(v1.1)* | R-RIA-9 two-seam outbound boundary: no `httpx`/`requests`/`urllib`/`mcp.client`/`subprocess` outside `ria/platform_client/**` and `ria/external_services/**` | `scripts/check_external_services_seam.py` | yes |
| **G-RIA-20** *(v1.1)* | Integration tests use `real_agent_server` fixture; no stub usage under `tests/integration/` | `scripts/check_integration_uses_real_server.py` | yes |
| **G-RIA-21** *(v1.1, advisory)* | Cassette age: warning if any `tests/_cassettes/<service>/*` is > 30 days old; failure if > 90 days | `scripts/check_cassette_freshness.py` | advisory in v1.1; promoted to blocking once cassette set stabilises |

Initial scope: G-RIA-1 through G-RIA-9 ship in RIA Phase 1 (foundational discipline). G-RIA-10..14 ship in Phase 2 (governance maturity). G-RIA-15..18 ship in Phase 3+ (release-grade discipline). **G-RIA-19, G-RIA-20 ship with v1.1 (R-Wave-2, 2026-05-04). G-RIA-21 is advisory in R-Wave-2; promoted to blocking in R-Wave-4.**

---

## 4. Posture Coupling

### 4.1 RIA × Platform posture matrix

Acceptable combinations:

| RIA | Platform | Status |
|---|---|---|
| dev | dev | OK |
| dev | research | OK (RIA permissive over fail-closed) |
| dev | prod | OK (RIA permissive over fail-closed) |
| research | dev | **REJECTED at startup** (research RIA must not run on dev platform) |
| research | research | OK |
| research | prod | OK |
| prod | dev | **REJECTED at startup** |
| prod | research | OK (RIA `prod` allows platform `research` if research is fail-closed-on-write, which it is) |
| prod | prod | OK |

This is enforced by `ria/config/posture.py::Posture.assert_compatible_with_platform()`. The check runs at process startup; failure exits the process with a clear error message (`exit code 78 — config error`).

### 4.2 Posture-driven behaviour summary

| Behaviour | dev | research | prod |
|---|---|---|---|
| `user_id` required on all write operations | warn | required | required |
| `project_id` required on `submit_project` | optional | required | required |
| `Idempotency-Key` required on platform writes | optional | required | required |
| Per-user budget enforced before platform call | log only | enforced | enforced + audit |
| JWT validation on user identity | skipped | skipped | required |
| `RIA_DATA_DIR` durability | tmpfs OK | sqlite required | sqlite + WAL |
| ACL enforcement | warn | enforced | enforced + audit |
| Posture compatibility check at startup | optional | required | required |
| Soak / chaos in release gate | skipped | required | required |

---

## 5. Soak, Chaos, Observability

### 5.1 Soak requirement (RIA-side)

Before any RIA release tagged ≥ M2 (preprint-grade), RIA runs its own ≥ 4 hour soak driving real research workloads against a real platform:

- **Duration:** ≥ 14400 s (4 h); 24 h preferred for promotion to M3.
- **Workload:** ≥ 3 concurrent users (synthetic accounts), ≥ 2 active projects per user, ≥ 1 PI Agent run per project.
- **Operations:** mid-soak SIGTERM of the RIA process (not the platform); resumption verified.
- **Provenance:** `real` (sampler binds RIA process PID; platform PID instrumentation is platform-side).
- **Acceptance:** 0 lost projects, 0 duplicate-terminal events, RIA process RSS < `RIA_RSS_BUDGET_MB` cap.

Output: `docs/ria/verification/<head>-soak-<duration>m.json` consumed by `scripts/check_soak_evidence.py`.

### 5.2 Chaos requirement

Phase 3+ adds RIA-side chaos scenarios:

| Scenario | Expected behaviour |
|---|---|
| Kill RIA process mid-project | Active projects resume on restart; no duplicate platform calls |
| Platform 5xx for 60 s | RIA retries with backoff; user-facing API returns 503 with `Retry-After`; project state unchanged |
| Platform 401 (token rotation) | RIA refreshes token via configured issuer; project state unchanged |
| Network partition between RIA and platform for 5 min | RIA pauses outbound calls; resumes on reconnect; SSE resubscribes from cursor |
| RIA SQLite locked / WAL contention | Reads succeed; writes retry up to 3 times then fail with typed error |
| User submits 100 projects in 60 s | Per-user budget rate-limit triggers; platform never receives more than budget allows |

Each scenario has an integration test under `tests/integration/test_chaos_*.py` and an e2e test under `tests/e2e/test_chaos_*.py`. Results in `docs/ria/verification/<head>-chaos.json`.

### 5.3 Observability spine (RIA-side)

RIA emits the following structured events; each carries `(trace_id, project_id, run_id, user_id_hash, tenant_id)`:

| Event | When emitted | Counter |
|---|---|---|
| `ria_project_submitted` | After `submit_project` 200 | `ria_project_submitted_total` |
| `ria_project_state_changed` | On state transition | `ria_project_state_changed_total{from, to}` |
| `ria_gate_pending` | When platform emits `gate_pending` | `ria_gate_pending_total{kind}` |
| `ria_gate_decided` | After `signal_resume` 200 | `ria_gate_decided_total{kind, decision}` |
| `ria_platform_call` | Around every `platform_client` call | `ria_platform_call_total{operation, status}` |
| `ria_idempotency_replay` | When platform returns cached response | `ria_idempotency_replay_total{operation}` |
| `ria_budget_breach_attempted` | When per-user budget would be exceeded | `ria_budget_breach_total{kind}` |
| `ria_acl_denial` | When ACL denies a user action | `ria_acl_denial_total{action}` |
| `ria_run_resumed_on_startup` | On RIA startup, per active project resumed | `ria_run_resumed_total` |

A real run produces all of these in a joinable trace, end to end. `tests/integration/test_observability_spine.py` (Phase 2) verifies the trace-id chain.

---

## 6. Provenance Honesty (Inheriting CLAUDE.md)

| Provenance | Allowed in | Notes |
|---|---|---|
| `measured` | All RIA artefacts | Generated by an actual run / actual reading of the cited source |
| `derived` | All RIA artefacts | Computed from `measured` evidence by a documented transformation |
| `simulated` | Internal reasoning only | Never headline claims |
| `illustrative` | Tutorial / docs only | Never an empirical claim |
| `unverified` | Quarantine | Treat as `illustrative` until verified |

**Forbidden:**
- Headline claims backed by `simulated` / `illustrative` / `unverified` evidence.
- Citations to papers not actually read.
- Numbers transcribed from a figure without referencing the table or computation.
- "I'll verify it later" — `unverified` claims stay `unverified` until they don't.

`scripts/check_evidence_provenance.py` walks RIA-published artefacts and fails on headline claims that lack a `provenance: <measured|derived>` field.

---

## 7. Maturity Ladder (RIA-Specific)

Inherits CLAUDE.md's M0..M4 ladder. Per-artefact criteria:

| Level | RIA software (a release) | RIA documents (a spec) |
|---|---|---|
| **M0** | Dev branch; tests pass on author's machine | Drafted; no reviewer |
| **M1** | Internal review (≥ 1 RIA team member sign-off); CI green | Co-author / advisor read; sign-off |
| **M2** | Preprint-grade: methods reproducible from doc alone; soak `provenance: real`; observability spine real-trace; conformance suite green; can be deployed at a partner site | Methods reproducible; `measured`/`derived` evidence; ready for arXiv-equivalent posting |
| **M3** | Peer-reviewed: external user (one) successfully runs full PI Agent project end to end; integration verified at partner site | Accepted at venue with external review; revisions integrated |
| **M4** | Replicated: an independent user (not RIA team) reproduces the central PI Agent capability without RIA team support | Independent party reproduced central result |

`verified_readiness` (RIA-internal score) maps to maturity ladder via the cap factors:

- M0..M1: `verified_readiness ≤ 60` (capability incomplete)
- M2: `verified_readiness ≤ 80` (no external validation)
- M3: `verified_readiness ≤ 90` (external validation but not replicated)
- M4: `verified_readiness ≤ 100`

Without measured soak or measured chaos at the current HEAD, score caps at 65 (matches hi-agent's pre-W28 honest cap).

---

## 8. Defect-vs-Limitation Discipline (Inheriting CLAUDE.md)

When a defect is found in a RIA artefact, closure requires three parts:

(a) Fix in the artefact.
(b) A check that prevents recurrence (CI gate, checklist line, citation-verifier rule, figure-caption template, audit row).
(c) The process change recorded in this document or the relevant spec file.

Missing any one part = defect remains OPEN. This is identical to hi-agent's three-part closure discipline; we share the rule because we share the rule's value.

**Forbidden moves** (mirroring CLAUDE.md):

- Reclassify an open defect as "design intent" or "future work."
- Inflate a score by retiring a cap without producing the missing evidence.
- Mark a closure "complete" because the test was added to the codebase but is `pytest.mark.skip`-ed.

These are blocking findings in any RIA audit. They cannot be waived.

---

## 9. Documentation Hierarchy (Single Authoritative Document)

Per CLAUDE.md, exactly one document is canonical for each fact. The RIA-side mapping:

| Fact | Canonical document | Derived documents |
|---|---|---|
| RIA architecture (L0) | `ria-architecture-v2.md` (current; from 2026-05-04) + `ria-architecture-v1.md` (live until R-Wave-4) | README, ARCHITECTURE.md (top-level, brief) |
| Domain entities and invariants | `ria-domain-model-v1.md` (v1.1) | `ria/domain/__init__.py` docstring |
| RIA → platform call shape | `ria-platform-contract-mapping-v1.md` (v1.1) | `ria/platform_client/transport_*.py` docstrings |
| RIA → external services call shape (v2) | `ria-architecture-v2.md` §5.2 + per-client `# r-ria-9-exception:` docstrings | `ria/external_services/<client>.py` |
| Quality bar / CI gates | this document (v1.1) | `release-gate.yml`, `scripts/check_*.py` doc strings |
| Open BLOCKERs / engineering expectations to hi-agent (current wave) | `hi-agent-wave34-engineering-expectations-2026-05-04.md` | (none — single source per wave) |
| Open BLOCKERs to hi-agent (W31 baseline; historical) | `hi-agent-wave31-blocker-closure-requirements-2026-05-02.md` | (none — single source) |
| Forcing-function red-status (v1.1) | `docs/ria/red-status/<head>.json` (machine-readable) | §13 of this document explains the schema |
| Backlog / open issues | `docs/ria/TODO.md` (when created) | (none — single source) |

When two documents disagree on a canonical fact, the canonical document wins. The other is fixed to match. `scripts/check_doc_truth.py` enforces byte-equality at the field level once Phase 2 ships.

---

## 10. Released-Artifact Immutability (Inheriting CLAUDE.md)

A submitted preprint, accepted paper, or DOI'd dataset is append-only. Corrections become errata or v2 with an explicit diff against v1, never silent overwrites.

For RIA-internal docs (this document and its peers), the convention is:

- v1 is the published baseline. Backwards-compatible additions are minor revisions (`v1.1`, `v1.2`) committed to the same file with a "Last updated" header bump.
- Breaking changes (renamed / removed sections, changed binding rules) require a `v2/` document with an explicit diff against v1 in the v2 introduction.
- Both v1 and v2 coexist for ≥ 2 RIA waves to allow downstream consumers to migrate.

---

## 11. Open Questions and Resolved Defaults

| Question | Resolution |
|---|---|
| Should RIA have its own wave system mirroring hi-agent? | **Yes**, but RIA waves are independent of hi-agent waves. RIA waves track RIA-side feature delivery. Use prefix `R-Wave-N`. |
| Should RIA score itself with `verified_readiness`? | **Yes**, but the score's cap factors include unmet hi-agent BLOCKERs (RIA can never exceed its platform's capability). |
| What is the policy for hi-agent posture changes mid-deployment? | RIA detects via periodic `/v1/manifest` poll; emits a `ria_platform_posture_changed` event; if platform downgrades from research → dev, RIA stops accepting new write requests at the entry-protocol layer. |
| What is the SLA for resolving a CI gate failure? | Same-day for any blocker; 1 wave for any high; tracked in TODO.md per CLAUDE.md staleness rule. |
| What happens if hi-agent ships a v2 before RIA is ready? | RIA pins `agent_server v1`. Platform is required to support v1 for ≥ 2 waves after v2 ships (we wrote this into the original architecture-improvement directive A-01). |

---

## 12. Cross-Reference

| If you are looking for... | Read |
|---|---|
| What RIA *is* (current) | `ria-architecture-v2.md` |
| What RIA *is* (v1 baseline; live until R-Wave-4) | `ria-architecture-v1.md` |
| What RIA's domain entities are | `ria-domain-model-v1.md` (v1.1) |
| How RIA talks to the platform | `ria-platform-contract-mapping-v1.md` (v1.1) |
| How RIA talks to external services (v1.1) | `ria-architecture-v2.md` §5.2 + `ria/external_services/ARCHITECTURE.md` |
| RIA's quality bar | this document (v1.1) |
| What RIA expects from hi-agent (current wave) | `hi-agent-wave34-engineering-expectations-2026-05-04.md` |
| What RIA expected from hi-agent (W31; historical) | `hi-agent-wave31-blocker-closure-requirements-2026-05-02.md` |
| Workspace-level rules | `CLAUDE.md` |
| Architecture decision provenance (v1) | `docs/superpowers/specs/2026-04-29-ria-agent-server-integration-architecture.md` |
| Architecture decision provenance (v2) | `ria-architecture-v2.md` §0 + 2026-05-04 brainstorming transcript |
| Forcing-function red-status JSON | `docs/ria/red-status/<head>.json` |

---

## 13. Forcing-Function Red-Status Discipline (v1.1)

This section operationalises the link between RIA's CI state and hi-agent's wave-cycle work. It is binding for RIA's release pipeline and informational for hi-agent's W34+ planning.

### 13.1 What the artifact is

For every commit to RIA's `main` branch, RIA emits `docs/ria/red-status/<sha>.json` — a machine-readable enumeration of:

- Tests passing at HEAD.
- Tests failing because of a known platform gap (annotated with the W34 BLOCKER ID that would unblock them).
- Tests failing internally to RIA (RIA-team owned).
- Tests skipped (with reason).
- Cassette-staleness notices (advisory).

### 13.2 Schema (proposed; see `ria-architecture-v2.md` §5.6 for the canonical reference)

```json
{
  "schema_version": "1",
  "ria_head": "<git sha>",
  "ria_head_committed_at": "<iso8601>",
  "platform_head_under_test": "<git sha or 'ce9330fa-or-newer'>",
  "platform_manifest_id": "<manifest id read from /v1/manifest>",
  "test_summary": {
    "passed": <int>,
    "failed_blocked_by_platform": <int>,
    "failed_internal": <int>,
    "skipped": <int>
  },
  "blocked_by_platform": [
    {
      "test": "tests/integration/test_xxx.py::test_yyy",
      "blocked_by_w34_id": "B-W34-1",
      "blocked_by_short": "F.2 lineage population",
      "first_observed_ria_head": "<sha>",
      "consecutive_red_commits": <int>,
      "last_traceback_excerpt": "<truncated, redacted>"
    }
  ],
  "internal_red": [
    {
      "test": "tests/unit/test_zzz.py::test_qqq",
      "owner": "ria-team",
      "first_observed_ria_head": "<sha>",
      "consecutive_red_commits": <int>
    }
  ],
  "green_test_count_by_dir": {
    "tests/unit/": <int>,
    "tests/integration/": <int>,
    "tests/conformance/": <int>
  },
  "cassette_warnings": [
    {"cassette": "tests/_cassettes/arxiv/fetch_2403.12345.yaml",
     "age_days": <int>}
  ]
}
```

### 13.3 Producer

`ria/observability/red_status.py::emit_red_status_json(...)` is invoked by the RIA CI pipeline after pytest completes. It reads pytest's `--json-report` output, classifies failures (platform-blocked vs internal) using a curated mapping `tests/_blocked_by_platform.yaml`, and writes the JSON to `docs/ria/red-status/<sha>.json`.

The mapping file `tests/_blocked_by_platform.yaml` (current state, post-W34 close 2026-05-05):

```yaml
# Active mappings — W35 plan carryover items intersecting RIA 8-lens positioning
- test_glob: "tests/conformance/test_contract_dataclass_spine_validation.py"
  blocked_by_wave_id: "W35-T1"
  blocked_by_short: "13 frozen-contract dataclasses missing __post_init__ spine validation"
- test_glob: "tests/posture/test_run_manager_body_tenant_id_fallback*"
  blocked_by_wave_id: "W35-T3"
  blocked_by_short: "INVERTED posture: strict more permissive than dev for body→middleware tenant_id fallback"
- test_glob: "tests/integration/test_idempotency_ttl_purge*"
  blocked_by_wave_id: "W35-T4"
  blocked_by_short: "idempotency TTL records accumulate indefinitely; DB grows unbounded"
- test_glob: "tests/integration/test_skill_registry_schema_partition*"
  blocked_by_wave_id: "W35-T1"   # SkillRegistry schema-layer carryover via existing hi-agent xfail expiry_wave="Wave 35"
  blocked_by_short: "SkillRegistry schema-layer tenant_id enforcement (W34-T-FOLLOWUP carryover)"

# RETIRED 2026-05-05 — closed at hi-agent W34 HEAD 77222f8b (kept as comment for traceability)
# - test_glob: "tests/integration/test_evolution_engine_*"
#   blocked_by_w34_id: "B-W34-1"   # W34-F.2 lineage population — closed
# - test_glob: "tests/integration/test_*_spine_validation.py"
#   blocked_by_w34_id: "B-W34-2"   # W34-F.3 ReasoningTrace spine validation — closed
# - test_glob: "tests/integration/test_knowledge_*_tenant_partition.py"
#   blocked_by_w34_id: "B-W34-3"   # W34-F.4 KG tenant partition — closed
# - test_glob: "tests/conformance/test_cross_tenant_isolation_*"
#   blocked_by_w34_id: "B-W34-4"   # W34-T-FOLLOWUP — audit closed; SkillRegistry schema-layer re-mapped to W35-T1
# - test_glob: "tests/integration/test_manifest_*"
#   blocked_by_w34_id: "B-W34-5"   # W34-MANIFEST — closed (frozen contract digest cc55145f)
# - test_glob: "tests/integration/test_idempotency_cross_process_*"
#   blocked_by_w34_id: "B-W34-6"   # W34-IDEMPOTENCY — closed
# - test_glob: "tests/integration/test_concurrency_*"
#   blocked_by_w34_id: "B-W34-7"   # W34-CONCURRENCY-* — closed
```

**Schema field rename (v1.1 erratum, 2026-05-05).** The mapping yaml now uses `blocked_by_wave_id` (wave-agnostic) instead of the W34-specific `blocked_by_w34_id`. The producer (`ria/observability/red_status.py::emit_red_status_json`) emits both fields in the output JSON for at least 2 RIA waves (R-Wave-3 and R-Wave-4) for backwards compatibility; R-Wave-5 retires `blocked_by_w34_id`. The JSON `schema_version` bumps from `"1"` to `"1.1"` to signal the rename. Schema details in §13.2 above and `ria-architecture-v2.md` §5.6.

The mapping file is updated as new W35+ items land. Tests that fail without a mapping entry are classified `internal_red`.

### 13.4 Consumer

The artifact is consumed by:

- **hi-agent W34+ wave-cycle planning.** The W34 expectations directive §5.3 commits to publishing this artifact; hi-agent ingests it as a CI signal. The directive does not request hi-agent to act on the artifact directly — it commits RIA to publish so the wave-cycle conversation between teams becomes evidence-grounded.
- **RIA's own backlog grooming.** Tests that have been red for > N consecutive RIA commits (parameter; default N=10) are flagged for triage.
- **RIA ops dashboard** (R-Wave-3+). Optional `GET /ria/red-status` endpoint on the running RIA process surfaces the latest JSON for live monitoring.

### 13.5 Privacy / leakage check

Test tracebacks may contain user data, file paths under `$HOME`, env-var values, or token-shape strings. The producer redacts:

- File paths under `$HOME` → replaced with `~`.
- Env-var values that match `[A-Z_][A-Z0-9_]+=...` → value replaced with `<redacted>`.
- Token-shaped strings: any contiguous run of `[A-Za-z0-9_-]{32,}` → replaced with `<redacted-token>`.
- Trailing context after the first 50 lines of traceback truncated.

### 13.6 Discipline rules

- **Do not patch a test red to make the artifact green.** A red test under `blocked_by_platform` is the desired state; "fixing" it by adjusting the assertion is AP-9 (defense-in-depth shim) and is forbidden.
- **Do not silence a test red by `pytest.mark.skip`.** Skipped tests appear in the `skipped` count; they do not get to disappear from the platform-blocker map. AP-6 still applies.
- **Do update `tests/_blocked_by_platform.yaml` when a new platform-blocker test is added.** Otherwise the test is mis-classified as `internal_red`, which dilutes the forcing-function signal.

### 13.7 Promotion path

R-Wave-2 (2026-05-04): producer implemented; mapping file populated for B-W34-1..7; CI step uploads JSON; `GET /ria/red-status` endpoint added.

**R-Wave-2 (erratum 2026-05-05; v1.1 erratum):** hi-agent W34 closed all 7 BLOCKERs at HEAD `77222f8b`; mapping yaml retires the W34 entries and adds W35-T1 / W35-T3 / W35-T4 entries; JSON schema bumps to v1.1 (`blocked_by_wave_id` field added; `blocked_by_w34_id` retained for backwards compatibility).

R-Wave-3: consecutive-red triage threshold (N=10); ops dashboard. Producer continues to emit both `blocked_by_wave_id` and `blocked_by_w34_id`.

R-Wave-4: cassette age `G-RIA-21` promoted from advisory to blocking. Producer continues backwards-compat emission.

R-Wave-5: `blocked_by_w34_id` field retired from JSON output; mapping yaml comments retiring the W34 entries are removed.

---

**End of Quality Requirements v1.1.**
