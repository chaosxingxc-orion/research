# RIA Engineering Plan — Wave R-W1 (2026-05-05)

**Document maturity:** M1 — internally reviewed
**Wave name:** **R-W1** (RIA's first explicit engineering wave; Phase 1 + Phase 2 partial were waveless)
**Owner:** RIA team
**Repository:** `D:\chao_workspace\research\`
**Predecessors:**
- `docs/ria/ria-architecture-v2.md` (v2.0.1 — design baseline this plan operationalises)
- `docs/ria/ria-quality-requirements-v1.md` (v1.1 — gates this plan extends)
- `docs/ria/ria-platform-contract-mapping-v1.md` (v1.1 — platform contract assumptions)
- `docs/ria/ria-domain-model-v1.md` (v1.1 — domain entities this plan instantiates)

**Companion outgoing artifacts (signed today, separate documents):**
- `docs/hi-agent-w35-acceptance-audit-2026-05-05.md` — RIA-internal W35 audit (the basis for this plan's hi-agent dependency assumptions)
- `docs/hi-agent-w35-corrective-directive-2026-05-05.md` — corrective directive to hi-agent
- `docs/hi-agent-wave36-engineering-expectations-2026-05-05.md` — W36 entry directive to hi-agent

---

## 1. Scope, Naming, Definition of Done

### 1.1 Wave naming

This is **R-W1** — RIA's first explicit engineering wave. Numbering is independent of hi-agent's wave count; we expect ~5 weeks of internal work spanning hi-agent's W36 binding window.

### 1.2 Scope

The wave lands the remaining ~75% of `ria-architecture-v2.md` v2.0.1 design surface as a single coherent ship:

- **`ria/external_services/`** — second outbound seam (the R-RIA-9 surface).
- **`ria/global_layer/`** — real implementation of paper_archive, lean_library, dataset_registry, evolution_engine.
- **`ria/api/{http,mcp}/`** — entry-protocol expansion beyond CLI.
- **`ria/orchestration/{phase_pipeline, backtrack, replanner, project_state}.py`** — orchestration completion.
- **`ria/user/{acl, budget}.py`** — user layer completion.
- **`ria/observability/{tracing, audit, red_status}.py`** — observability completion.
- **`ria/platform_client/{transport_mcp, run_lifecycle, streaming, budget_enforcer}.py`** — platform_client surface completion (Phase 2 surface from `transport_http` docstring).
- **`ria/domain/`** — 14 new domain modules (hypothesis, claim, acceptance, gate, paper, theorem, experiment, dataset, review, artifact, skill_delta, postmortem, author, run_record_view).
- **9 new CI gates** under `scripts/`.
- **Test infrastructure** — real `agent-server serve` fixture, `_blocked_by_platform.yaml`, `red-status/` JSON pipeline, integration + conformance test sets.
- **Doc synchronisation** — `ARCHITECTURE.md`, `pyproject.toml`, `CLAUDE.md`, `skills/<all 4>/SKILL.md` brought into truth alignment.

### 1.3 Definition of Done (one-vote-veto)

The wave does not close until all six conditions hold:

1. **9 new CI gates** all green (G-RIA-7, G-RIA-10, G-RIA-11, G-RIA-12, G-RIA-13, G-RIA-19, G-RIA-20, G-RIA-21, plus the R-RIA-7 enforcement). All pre-existing 5 gates remain green.
2. **`tests/integration/`** runs against real `agent-server serve` subprocess fixture and is green; **stub usage in `tests/integration/`** is forbidden by `scripts/check_integration_uses_real_server.py`.
3. **`docs/ria/red-status/<sha>.json`** emitted on every commit to RIA `main`, schema v1.1, with the `blocked_by_wave_id` field active.
4. **All v2 §5 designed modules** are PRESENT (per `ARCHITECTURE.md` Subpackage Map updated to v2.0.1 truth).
5. **Outgoing directives signed** — W35 corrective directive + W36 entry directive both M1.
6. **Doc-truth gate** — `ARCHITECTURE.md`, `pyproject.toml::tool.pytest.ini_options.markers`, `CLAUDE.md` Phase status all aligned with on-disk state.

---

## 2. Fourteen Work Streams

Each work stream has explicit deliverables, falsifiable acceptance criteria, and dependency declarations.

### 2.1 Stream A — outbound seam 2 (`ria/external_services/`)

**Deliverables.**
- `arxiv_client.py`, `semantic_scholar_client.py`, `doi_client.py`, `github_paper_client.py`, `github_dataset_client.py`, `lean_runner.py`, `zenodo_client.py`, `huggingface_client.py`
- `cassette.py` (record/replay HTTP), `errors.py` (typed `ExternalServiceError` family), `retry.py` (per-target backoff)
- `ARCHITECTURE.md` per-seam README (purpose, target URL, auth, rate limit, cassette dir per client)

**Acceptance criteria.**
- G-RIA-19 (`scripts/check_external_services_seam.py`) PASS.
- Each client carries a docstring with the v2 §5.2 fields.
- At least one cassette per HTTP-based client under `tests/_cassettes/<service>/`.
- `ria/external_services/errors.py::ExternalServiceError` family — no raw `httpx.HTTPError` escapes the seam.
- Each client supports the v2 §5.2 degraded mode (anonymous / no auth).
- Unit tests cover error envelope translation; integration tests cover cassette replay.

**Dependencies.** None (foundation track).

### 2.2 Stream B — `global_layer/` real implementation

**Deliverables.**
- `paper_archive/` — `__init__.py`, `ARCHITECTURE.md`, `ingest.py`, `curate.py`, `citation_graph.py`, `search.py`
- `lean_library/` — `__init__.py`, `ARCHITECTURE.md`, `verify.py`, `index.py`, `cas_store.py`
- `dataset_registry/` — `__init__.py`, `ARCHITECTURE.md`, `ingest.py`, `versioning.py`, `provenance.py`
- `evolution_engine/` — `__init__.py`, `ARCHITECTURE.md`, `postmortem.py`, `skill_delta.py`, `champion_challenger.py`

**Acceptance criteria.**
- Each public surface (`ingest_paper`, `verify_proof`, `ingest_dataset`, `ingest_postmortem`, etc.) has at least one `tests/integration/test_*` against the `real_agent_server` fixture green.
- `ria/global_layer/**` imports only allowed paths (no `httpx`/`subprocess`/`mcp`; everything via `external_services/` or `platform_client/`) — enforced by G-RIA-19.
- Postmortem reconstruction works for real platform run records (depends on hi-agent W34 F.2 closure ✓ and W36 A4 schema-shape extension — RED status until W36 closes).
- KG cross-tenant queries respect tenant partitioning (depends on hi-agent W34 F.4 closure ✓).

**Dependencies.** Stream A (external_services); Stream H (real_agent_server fixture); Stream I (platform_client run_lifecycle for postmortem).

### 2.3 Stream C — orchestration expansion

**Deliverables.**
- `phase_pipeline.py` — 6-step writing-team / phase machine.
- `backtrack.py` — backtrack policy when AC fails.
- `replanner.py` — `StageDirective` wiring (calls `/v1/runs/{id}/signal`).
- `project_state.py` — Project lifecycle state machine.

**Acceptance criteria.**
- Each module has ≥5 unit tests.
- Integration test `test_compile_then_phase_pipeline_against_real_server.py` exercises `compile_new_project` → `phase_pipeline.advance` → real `/v1/runs` submission.
- `replanner.py` writes go through `transport_http.signal_run` with `Idempotency-Key` (R-RIA-5).

**Dependencies.** Stream I (platform_client surface completion); Stream H (fixture).

### 2.4 Stream D — user layer expansion

**Deliverables.**
- `acl.py` — project-level ACL (read/write/admin grants per (user_id, project_id)).
- `budget.py` — per-user budget envelope. Defaults sized against hi-agent W34 baselines: P50=77.5ms, P95=200.4ms (N=50/M=5).

**Acceptance criteria.**
- Unit tests for acl.py (grant/revoke/check) and budget.py (envelope, exhaustion, reset).
- Integration test `test_budget_against_real_server.py` exercises pre-call enforcement against real `agent-server serve`.
- `budget.py` documents the W34-baseline derivation in its module docstring.

**Dependencies.** Stream H (fixture); Stream I (budget_enforcer in platform_client).

### 2.5 Stream E — `api/{http,mcp}/` entry-protocol expansion

**Deliverables.**
- `api/mcp/server.py`, `tools.py`, `resources.py` — MCP stdio server with research-domain tool definitions.
- `api/http/app.py` — FastAPI app factory.
- `api/http/routes/` — `projects.py`, `gates.py`, `papers.py`, `datasets.py`, `theorems.py`, `health.py`.
- `api/http/middleware/` — `jwt_auth.py` (mirrors hi-agent W33-C.4 outermost pattern), `ria_context.py`, `audit.py`, `sse.py`.

**Acceptance criteria.**
- G-RIA-8 (`check_no_generic_verbs.py`) PASS — no platform-vocabulary names in user-visible surfaces (no `run`, `skill`, `memory`, `artifact`, `signal`, `capability`).
- HTTP routes integration-tested against `real_agent_server` fixture.
- MCP server passes a stdio smoke test.
- `jwt_auth.py` is outermost in the middleware chain.

**Dependencies.** Stream A (external_services for paper/dataset routes); Stream B (global_layer for paper_archive/dataset_registry/lean_library/evolution_engine routes); Stream C (orchestration phase_pipeline); Stream D (user/acl, budget); Stream G (observability tracing/audit).

### 2.6 Stream F — domain layer expansion (14 modules)

**Deliverables.**
- `hypothesis.py`, `claim.py`, `acceptance.py`, `gate.py`, `paper.py`, `theorem.py`, `experiment.py`, `dataset.py`, `review.py`, `artifact.py`, `skill_delta.py`, `postmortem.py`, `author.py`, `run_record_view.py`

**Acceptance criteria.**
- All 14 modules pure stdlib (G-RIA-2 / `check_no_platform_types.py` PASS).
- R-RIA-8 spine completeness: persistent dataclasses (any module other than `author.py` and `run_record_view.py` which are value-objects) declare `tenant_id` and/or `project_id` as required (non-Optional) fields. Process-internal value-objects carry `# scope: process-internal` annotation.
- G-RIA-9 (`check_contract_spine_completeness.py`) PASS at 14 modules.
- Each module has ≥3 unit tests covering invariant assertions.

**Dependencies.** None (pure-stdlib track; runs in parallel with everything else).

### 2.7 Stream G — observability expansion

**Deliverables.**
- `tracing.py` — W3C Trace-Context propagation through `platform_client` and `external_services`.
- `audit.py` — RIA audit trail (every write under prod posture logs to a SQLite audit table).
- `red_status.py` — emitter for `docs/ria/red-status/<sha>.json` per v2 §5.6 schema v1.1.

**Acceptance criteria.**
- Tracing context survives `platform_client.transport_http` round-trip (verified by integration test against real_agent_server).
- `audit.py` writes 100% of writes under prod posture (verified by counter assertion).
- `red_status.py` emits well-formed JSON on every commit; schema v1.1 validated by G-RIA-12 (`check_provenance_ladder.py`).
- **No dashboard code is added in this stream** that depends on `{tenant_bucket}` or `{tenant_id}` Prometheus labels — observability dashboards await hi-agent's resolution of W35 corrective C-1. RIA emits only label-free counters and trace IDs for now.

**Dependencies.** Stream H (fixture for tracing test); Stream I (transport_http for tracing context).

### 2.8 Stream H — test infrastructure

**Deliverables.**
- `tests/integration/conftest.py::real_agent_server` — session-scope subprocess fixture per v2 §5.5. The fixture **must** include a route-presence probe before yielding (the RIA-side mirror of hi-agent B13).
- `tests/_blocked_by_platform.yaml` — wave-id to test-glob mapping per v2 §5.6.
- `tests/_stubs/` — historical stub_v1 archive with `tests/_stubs/README.md` documenting "do not extend; unit tests only".
- `tests/_cassettes/` — per-service cassette directories.
- `docs/ria/red-status/` — directory created.

**Acceptance criteria.**
- G-RIA-20 (`check_integration_uses_real_server.py`) PASS — no `tests/integration/**` test imports `tests._stubs.*`; every test that imports `ria.platform_client` transitively depends on `real_agent_server`.
- G-RIA-13 (`check_route_presence.py`) PASS — fixture's route-presence probe asserts `/v1/manifest`, `/v1/runs`, `/v1/runs/{id}`, `/v1/runs/{id}/events`, etc., each return a non-404 before fixture yields.
- `_blocked_by_platform.yaml` has entries for all known W35 corrective + W36 binding items.
- First `red-status/<sha>.json` emitted at wave-close commit.

**Dependencies.** None (foundation track); blocking for all integration tests.

### 2.9 Stream I — platform_client surface completion

**Deliverables.**
- `transport_mcp.py` — alternative MCP transport (parallel to `transport_http.py`).
- `run_lifecycle.py` — long-running resumer for postmortem reads.
- `streaming.py` — SSE consumer wrapping `transport_http`.
- `budget_enforcer.py` — pre-call check consuming `user/budget.py` envelope.

**Acceptance criteria.**
- R-RIA-5 (`check_idempotency_keys.py`) PASS — every write fn in `transport_*.py` calls `idem(...)`.
- `streaming.py` consumes SSE events from real `agent-server serve` and emits structured events upward.
- `run_lifecycle.py` reads platform run records via `transport_http.get_run` and reconstructs lineage chain (depends on hi-agent W34 F.2 closure ✓; postmortem reconstruction completeness depends on W36 A4 schema-shape extension — RED until then).
- `budget_enforcer.py` raises `BudgetExhausted` before submitting a run when the per-user envelope is exhausted.

**Dependencies.** Stream H (fixture); Stream D (budget for budget_enforcer).

### 2.10 Stream J — CI gates (9 new)

See §3 below for the gate-by-gate detail. All gates land as `scripts/check_*.py` with their own pytest-runnable selftest.

**Acceptance criteria.**
- 9 gates exist, are exit-0 at wave-close head, and are wired into `pyproject.toml`'s `lint` extra or a wave-acceptance script.
- `scripts/run_r_w1_acceptance.py` orchestrates all gates + tests + red-status emission and is exit-0 at wave-close head.

**Dependencies.** Stream H for G-RIA-13/G-RIA-20 testability.

### 2.11 Stream K — doc synchronisation

**Deliverables.**
- `ARCHITECTURE.md` — Subpackage Map updated to PRESENT/IN-PROGRESS/PLANNED tri-state with current truth.
- `pyproject.toml::tool.pytest.ini_options.markers.integration` — text changed from "real RIA wiring against a stub agent_server" to "real RIA wiring against real local agent-server subprocess (v2 §0.4)".
- `CLAUDE.md` line 198 updated: "R-W1 ships R-RIA-7 + R-RIA-9 + 9 new gates" replaces the Phase 2 wording.
- `CLAUDE.md` Repository Purpose paragraph updated: "R-W1 brings v2 architecture to ~95% on-disk coverage" added.
- `skills/<all 4>/SKILL.md` `description` frontmatter translated from Chinese to English (CLAUDE.md Language Rule).
- `docs/ria/ria-quality-requirements-v1.md` v1.2 — adds G-RIA-13 entry.

**Acceptance criteria.**
- G-RIA-11 (`check_doc_truth.py`) PASS — Subpackage Map matches `ria/` actual contents; CLAUDE.md Phase status matches gate inventory; pyproject marker text matches `tests/integration/conftest.py::real_agent_server` existence.
- Skill frontmatter passes a Latin-character heuristic check.

**Dependencies.** All other streams (K runs at wave-close).

### 2.12 Stream L — outgoing directives

**Deliverables.**
- `docs/hi-agent-w35-corrective-directive-2026-05-05.md` — signed today, separate document.
- `docs/hi-agent-wave36-engineering-expectations-2026-05-05.md` — signed today, separate document.

**Acceptance criteria.**
- Both signed M1.
- Both English (per RIA correspondence rule).
- Both follow the W34/W35 directive format precedent.

**Dependencies.** None (signed concurrent with this plan).

### 2.13 Stream M — Phase 3 conformance test set

**Deliverables.**
- `tests/conformance/test_contract_dataclass_spine_validation.py` — probes each of the 53 hi-agent contract dataclasses by constructing instances from real `/v1/manifest` responses and asserting research/prod posture validation (red-status maps to `W35-T1` — already closed, expected GREEN at hi-agent HEAD `bd4d38d5`).
- `tests/conformance/test_idempotency_replay_against_real.py` — exercises cross-process replay against real `agent-server serve`.
- `tests/conformance/test_manifest_posture_compatibility.py` — verifies `agent_server/contracts/manifest.py::ManifestResponse::posture` field shape per W34-MANIFEST closure.
- ≥7 additional conformance tests across the 8 lenses.

**Acceptance criteria.**
- All conformance tests run against `real_agent_server` fixture.
- Tests RED due to platform W36 carryovers are mapped in `_blocked_by_platform.yaml` with `blocked_by_wave_id`.
- Default-offline + integration + conformance suites all green at wave-close head (modulo `_blocked_by_platform.yaml` entries).

**Dependencies.** Stream H (fixture); Stream I (platform_client).

### 2.14 Stream N — wave acceptance orchestrator

**Deliverable.** `scripts/run_r_w1_acceptance.py` — orchestrates the `Definition of Done` six conditions in §1.3.

**Acceptance criteria.**
- Exit-0 at wave-close head means R-W1 is shippable.
- Per-condition diagnostic output for failures.

**Dependencies.** All streams.

---

## 3. Nine New CI Gates

| Gate | Script | Rule | Check | Blocking |
|---|---|---|---|---|
| **G-RIA-7** | `check_tdd_evidence.py` | R-RIA-7 | Every new route handler / facade method carries `# tdd-red-sha: <sha>`; missing → fail | yes |
| **G-RIA-10** | `check_naming_hygiene.py` | — | Naming-drift detection: no `<X>/<Xs>` doublets, no `-v2`/`-new`/`-final` directory suffixes, no empty-shell `__init__.py` (only `pass` body counts as empty) | yes |
| **G-RIA-11** | `check_doc_truth.py` | — | `ARCHITECTURE.md` Subpackage Map matches `ria/` actual contents; CLAUDE.md Phase status matches gate inventory; `pyproject.toml` pytest marker text matches `tests/integration/conftest.py::real_agent_server` existence | yes |
| **G-RIA-12** | `check_provenance_ladder.py` | — | Any `<head>.json` or `red-status/<sha>.json` containing `provenance` field uses one of {measured, derived, simulated, illustrative, unverified} | yes |
| **G-RIA-13** | `check_route_presence.py` | — | `tests/integration/conftest.py::real_agent_server` includes a route-presence probe before yield; the probe asserts a documented route inventory returns non-404. **Mirrors hi-agent B13 silent-route-omission defence on the consumer side.** | yes |
| **G-RIA-19** | `check_external_services_seam.py` | R-RIA-9 | `ria/{domain,orchestration,global_layer,api,observability,user,config}/**` does not import `httpx`/`requests`/`urllib`/`urllib3`/`mcp`/`subprocess`/`asyncio.create_subprocess_exec`. Only `platform_client/` and `external_services/` may | yes |
| **G-RIA-20** | `check_integration_uses_real_server.py` | — | AST-walk `tests/integration/**`: (i) no import of `tests._stubs.*`; (ii) any test importing `ria.platform_client` transitively depends on `real_agent_server` fixture | yes |
| **G-RIA-21** | `check_cassette_freshness.py` | — | `tests/_cassettes/**` files: warning if mtime > 30d, fail if > 90d | warn → fail |
| **(reuse) G-RIA-8** | `check_no_generic_verbs.py` | R-RIA-4 | Already on disk; R-W1 strengthens enforcement on new `api/{http,mcp}/` paths | yes |

Plus the 5 existing gates (`check_layering.py`, `check_no_platform_types.py`, `check_idempotency_keys.py`, `check_no_generic_verbs.py`, `check_contract_spine_completeness.py`) all remain in CI and continue PASS.

---

## 4. Sub-wave Phasing

R-W1 internally divides into four sub-waves with explicit gates between them. Each sub-wave has its own green door.

### Sub-wave 1 — foundations (~1 week)

**Streams:** K (doc sync), H (fixture + yaml), J subset (G-RIA-10/11/13/19/20/21), L (corrective + W36 entry directives signed and posted).

**Sub-wave 1 green door:**
- 5 doc edits landed.
- 4 new gates green at HEAD.
- `real_agent_server` fixture exits 0 with route-presence probe.
- W35 corrective + W36 entry directives M1 and committed.

**Why first.** The fixture and directives unblock everything else. Doc-truth gate prevents cascading drift while the rest of the wave lands.

### Sub-wave 2 — seams + domain + platform_client (~1.5 weeks)

**Streams:** A (external_services), I (platform_client surface), F (14 domain modules), D (user/acl + user/budget).

**Sub-wave 2 green door:**
- G-RIA-19 PASS (R-RIA-9 enforced).
- R-RIA-5 / R-RIA-8 / R-RIA-9 all PASS at HEAD.
- New modules each have unit tests + (where applicable) cassette tests green.
- 14 domain modules pass G-RIA-2 + G-RIA-9.

**Dependency on Sub-wave 1.** Fixture must exist; doc-truth must hold.

### Sub-wave 3 — consumers + entry + observability (~2 weeks)

**Streams:** B (global_layer), C (orchestration expansion), E (api/{http,mcp}), G (observability).

**Sub-wave 3 green door:**
- M conformance set runs green against real_agent_server.
- G-RIA-7, G-RIA-8, G-RIA-12 PASS.
- HTTP / MCP / CLI three entry-protocol surfaces all pass vocabulary check.
- Tracing context survives platform round-trip.

**Dependency on Sub-wave 2.** External_services + platform_client + domain + user must exist.

### Sub-wave 4 — wave close (~0.5 week)

**Streams:** N (acceptance orchestrator), final K corrections, M conformance final pass.

**Sub-wave 4 green door (and wave Definition of Done):**
- `scripts/run_r_w1_acceptance.py` exit 0.
- `red-status/<sha>.json` emitted at wave-close commit.
- All six §1.3 Definition-of-Done conditions hold.

**Total wave duration:** ~5 weeks of focused work.

---

## 5. Final Directory Tree (R-W1 close)

```
ria/
├── __init__.py
├── config/                       posture.py settings.py
├── domain/                       (3 existing) project.py phase.py role.py
│                                 (14 new) hypothesis.py claim.py acceptance.py gate.py
│                                          paper.py theorem.py experiment.py dataset.py
│                                          review.py artifact.py skill_delta.py
│                                          postmortem.py author.py run_record_view.py
├── platform_client/              (4 existing) errors.py idempotency.py
│                                              tenant_resolver.py transport_http.py
│                                 (4 new) transport_mcp.py run_lifecycle.py
│                                         streaming.py budget_enforcer.py
├── external_services/   ★NEW     arxiv_client.py semantic_scholar_client.py
│                                  doi_client.py github_paper_client.py
│                                  github_dataset_client.py lean_runner.py
│                                  zenodo_client.py huggingface_client.py
│                                  cassette.py errors.py retry.py ARCHITECTURE.md
├── orchestration/                (2 existing) compiler.py pi_agent.py
│                                 (4 new) phase_pipeline.py backtrack.py
│                                          replanner.py project_state.py
├── global_layer/        ★NEW     paper_archive/   ARCHITECTURE.md ingest.py curate.py
│                                                  citation_graph.py search.py
│                                  lean_library/   ARCHITECTURE.md verify.py
│                                                  index.py cas_store.py
│                                  dataset_registry/ ARCHITECTURE.md ingest.py
│                                                    versioning.py provenance.py
│                                  evolution_engine/ ARCHITECTURE.md postmortem.py
│                                                    skill_delta.py champion_challenger.py
├── user/                         (2 existing) identity.py store.py
│                                 (2 new) acl.py budget.py
├── api/
│   ├── cli/                      (existing)
│   ├── mcp/             ★NEW     server.py tools.py resources.py
│   └── http/            ★NEW     app.py
│                                  routes/   projects.py gates.py papers.py
│                                            datasets.py theorems.py health.py
│                                  middleware/ jwt_auth.py ria_context.py
│                                              audit.py sse.py
└── observability/                (1 existing) counters.py
                                  (3 new) tracing.py audit.py red_status.py

scripts/
├── (5 existing)                 check_layering.py check_no_platform_types.py
│                                 check_idempotency_keys.py check_no_generic_verbs.py
│                                 check_contract_spine_completeness.py
└── (9 new)                      check_tdd_evidence.py
                                  check_external_services_seam.py
                                  check_integration_uses_real_server.py
                                  check_cassette_freshness.py
                                  check_naming_hygiene.py
                                  check_doc_truth.py
                                  check_provenance_ladder.py
                                  check_route_presence.py
                                  run_r_w1_acceptance.py

tests/
├── conftest.py
├── unit/                         (7 existing) + per-new-module unit coverage
├── integration/         ★NEW     conftest.py::real_agent_server (with route probe)
│                                  test_external_services_*.py
│                                  test_global_layer_*.py
│                                  test_http_routes_real_server.py
│                                  test_budget_against_real_server.py
│                                  test_compile_then_phase_pipeline_against_real_server.py
├── conformance/         ★NEW     test_contract_dataclass_spine_validation.py
│                                  test_idempotency_replay_against_real.py
│                                  test_manifest_posture_compatibility.py
│                                  (~7 more across 8 lenses)
├── _stubs/                       (historical stub_v1, unit-only)  README.md
├── _cassettes/          ★NEW     arxiv/ semantic_scholar/ doi/ github_paper/
│                                  github_dataset/ zenodo/ huggingface/
└── _blocked_by_platform.yaml ★NEW

docs/ria/
├── ria-architecture-v2.md         (existing v2.0.1)
├── ria-domain-model-v1.md         (v1.2 minor refresh)
├── ria-platform-contract-mapping-v1.md (v1.2 minor refresh)
├── ria-quality-requirements-v1.md (v1.2 — add G-RIA-13)
├── red-status/         ★NEW       <sha>.json
└── ria-engineering-plan-r-w1-2026-05-05.md (this document)

docs/                              (existing inter-team docs)
├── hi-agent-w35-acceptance-audit-2026-05-05.md         ★NEW
├── hi-agent-w35-corrective-directive-2026-05-05.md     ★NEW
└── hi-agent-wave36-engineering-expectations-2026-05-05.md ★NEW
```

---

## 6. Doc Synchronisation Specifics

### 6.1 `ARCHITECTURE.md` Subpackage Map

Tri-state per row: **PRESENT / IN-PROGRESS / PLANNED**. Pre-R-W1 wording "Phase 2 — not scaffolded yet" replaced by current truth.

### 6.2 `pyproject.toml` pytest marker

```toml
[tool.pytest.ini_options]
markers = [
    "integration: real RIA wiring against real local agent-server subprocess (v2 §0.4)",
    "conformance: contract conformance against agent_server v1",
    "soak: long-running soak tests (skipped in default-offline)",
]
```

### 6.3 `CLAUDE.md` Repository Purpose paragraph

Add: "As of 2026-05-05 (post hi-agent W35 acceptance + RIA W35 audit), R-W1 wave is in progress; v2.0.1 architecture is being landed to ~95% on-disk coverage."

### 6.4 `CLAUDE.md` line 198 (`Phase 1 ships ...` paragraph)

Replace with:

```
Phase 1 + early Phase 2 shipped: R-RIA-1, R-RIA-2, R-RIA-3, R-RIA-4, R-RIA-5,
R-RIA-6, R-RIA-8 as enforced gates. R-W1 ships R-RIA-7 + R-RIA-9 plus 9 new gates
(G-RIA-7, G-RIA-10, G-RIA-11, G-RIA-12, G-RIA-13, G-RIA-19, G-RIA-20, G-RIA-21,
plus the run_r_w1_acceptance orchestrator).
```

### 6.5 Skill frontmatter language

`skills/literature-review/SKILL.md`, `skills/paper-reading/SKILL.md`, `skills/paper-writing/SKILL.md`, `skills/experiments/SKILL.md` — `description` frontmatter currently in Chinese; translate to English per CLAUDE.md Language Rule.

### 6.6 `docs/ria/ria-quality-requirements-v1.md` v1.2

Add `G-RIA-13` entry; refresh §13 red-status mapping; add the W35-corrective-derived `_blocked_by_platform.yaml` entries.

---

## 7. Guard Rails (Carry From Audit Recommendations)

### 7.1 Guard rail 1 — R-RIA-9 outbound seam strict

G-RIA-19 enforced in CI from sub-wave 1 onward. **No defence-in-depth shim** in any RIA module masks a hi-agent platform gap. Tests stay red and surface in red-status JSON.

### 7.2 Guard rail 2 — route-presence probe in fixture

`tests/integration/conftest.py::real_agent_server` includes a route-presence probe before yield, asserting documented route inventory returns non-404. This is the consumer-side mirror of hi-agent B13. G-RIA-13 enforces it.

### 7.3 Guard rail 3 — observability label decision pending

Until hi-agent resolves W35 corrective C-1, `ria/observability/` does NOT add any dashboard code dependent on `{tenant_bucket}` or `{tenant_id}` Prometheus label form. Only label-free counters and W3C Trace-Context propagation are added. Once C-1 closes, a follow-up wave R-W2 (or in-wave amendment if C-1 closes early) adds dashboards.

---

## 8. Risk Register

| ID | Risk | Mitigation |
|---|---|---|
| R-1 | external_services cassette dirty-record on first capture due to network instability | Documented record procedure; G-RIA-21 30d/90d freshness gate |
| R-2 | Real `agent-server serve` integration test runtime grows CI cost | Session-scope fixture; PR-only execution; unit coverage maintained ≥80% |
| R-3 | `api/http` middleware/jwt_auth diverges from hi-agent W33-C.4 outermost pattern | Direct mirror of W33-C.4 layer order with single source citation in module docstring |
| R-4 | 5-week wave duration risks personal energy / pace | Sub-wave phasing with independent green doors permits suspension at any boundary |
| R-5 | hi-agent W35 corrective unresolved when R-W1 needs labels | Guard rail 3: defer dashboard work; do label-free observability only |
| R-6 | hi-agent W36 A4 schema-shape extension delayed; postmortem reconstruction incomplete | Red-status JSON makes this visible; no defence-in-depth shim added; postmortem feature blocked publicly |
| R-7 | Skill frontmatter translation introduces meaning drift | Literal English translation; reviewer pass for semantic preservation |

---

## 9. Verification Sequence (At Wave Close)

```bash
# 1. Static checks
cd D:\chao_workspace\research
ruff check ria/ scripts/ tests/
mypy ria/

# 2. All 14 CI gates (5 existing + 9 new)
for g in check_layering check_no_platform_types check_idempotency_keys \
         check_no_generic_verbs check_contract_spine_completeness \
         check_tdd_evidence check_external_services_seam \
         check_integration_uses_real_server check_cassette_freshness \
         check_naming_hygiene check_doc_truth check_provenance_ladder \
         check_route_presence ; do
  python "scripts/${g}.py" || { echo "GATE FAIL: ${g}"; exit 1; }
done

# 3. Test layers
pytest tests/unit
pytest tests/integration -m integration   # spawns real_agent_server
pytest tests/conformance -m conformance

# 4. Red-status emission + wave acceptance
python scripts/run_r_w1_acceptance.py     # writes docs/ria/red-status/<sha>.json
                                           # exit 0 = wave shippable
```

A wave-close run with all-green is the operational definition of "R-W1 done".

---

## 10. Cross-References

| Document | Role |
|---|---|
| `D:\chao_workspace\research\docs\ria\ria-architecture-v2.md` | v2.0.1 design baseline this plan operationalises |
| `D:\chao_workspace\research\docs\ria\ria-quality-requirements-v1.md` | v1.1 — extended to v1.2 in stream K |
| `D:\chao_workspace\research\docs\ria\ria-platform-contract-mapping-v1.md` | v1.1 — refreshed to v1.2 in stream K |
| `D:\chao_workspace\research\docs\ria\ria-domain-model-v1.md` | v1.1 — refreshed to v1.2 in stream K |
| `D:\chao_workspace\research\docs\hi-agent-w35-acceptance-audit-2026-05-05.md` | RIA-internal W35 audit (basis for this plan's hi-agent dependency assumptions) |
| `D:\chao_workspace\research\docs\hi-agent-w35-corrective-directive-2026-05-05.md` | corrective directive (companion outgoing artifact) |
| `D:\chao_workspace\research\docs\hi-agent-wave36-engineering-expectations-2026-05-05.md` | W36 entry directive (companion outgoing artifact) |
| `D:\chao_workspace\research\CLAUDE.md` | RIA workspace rules (refreshed in stream K §6.4) |
| `D:\chao_workspace\research\ARCHITECTURE.md` | top-level brief (refreshed in stream K §6.1) |
| `D:\chao_workspace\research\pyproject.toml` | manifest (marker refreshed in stream K §6.2) |

---

**Signed:** RIA team
**Audit head (RIA side):** `main` at 2026-05-05
**Document maturity:** M1 — internally reviewed; promotes to M2 on wave-close (when all six Definition-of-Done conditions hold).

---

**End of RIA Engineering Plan — Wave R-W1.**
