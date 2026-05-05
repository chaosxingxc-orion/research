# Architecture: Research Intelligence Application (RIA) — v2

**Document maturity:** M1 — internally reviewed
**Last updated:** 2026-05-05 (v2.0.1 minor erratum — §0.7 W34 closure consumption, §11 Risks W34 row downgrade, §5.6 schema field rename)
**Repository:** `D:\chao_workspace\research\`
**Supersedes:** `ria-architecture-v1.md` for the structural shape of `ria/`. v1 remains live for ≥ 2 RIA waves per `ria-quality-requirements-v1.md` §10.

> **Document hierarchy**
> - L0 system boundary: this file (v2) + `ria-architecture-v1.md` (v1; live until 2026-05-18)
> - L1 domain detail: `ria-domain-model-v1.md` → revised to v1.1 this wave
> - L1 platform-mapping detail: `ria-platform-contract-mapping-v1.md` → revised to v1.1 this wave
> - L1 quality detail: `ria-quality-requirements-v1.md` → revised to v1.1 this wave
> - Architecture-discussion archive (decision provenance for v1): `docs/superpowers/specs/2026-04-29-ria-agent-server-integration-architecture.md`
> - Architecture-discussion archive (decision provenance for v2): this document's §0 + the 2026-05-04 brainstorming transcript

---

## 0. Diff Against v1 (Mandatory per `ria-quality-requirements-v1.md` §10)

This v2 supersedes v1 on five concrete shape decisions. Everything else carries unchanged from v1; consult v1 for unchanged sections (the section numbering below mirrors v1's so cross-references survive).

### 0.1 Two seams instead of one

**v1.** `ria/platform_client/` is the single outward-facing seam. All non-stdlib outbound traffic from RIA passes through it.

**v2.** RIA has **two** outward seams:
- `ria/platform_client/` — outbound traffic to hi-agent's `agent_server` v1 contract (HTTP /v1/*, SSE).
- `ria/external_services/` (new top-level subpackage) — outbound traffic to non-platform external services: arxiv, semantic-scholar, DOI resolvers, GitHub paper / dataset hosts, Lean local executable, Zenodo, HuggingFace datasets.

This mirrors hi-agent's W32–W33 two-seam pattern (`agent_server/bootstrap.py` + `agent_server/runtime/**`). RIA endorsed that pattern in W32 acceptance §4.1 and W33 acceptance; we now adopt the same shape.

### 0.2 Phase 3 going real (A.3.α)

**v1.** `global_layer/` is "Phase 3+" with stub status. Implementation deferred until W31 BLOCKERs close, then deferred again "until we know our exact shape".

**v2.** `global_layer/{paper_archive, lean_library, dataset_registry, evolution_engine}` is **implemented in real form** in this wave. Tests run against the real `agent-server serve` subprocess, not against a stub `agent_server`. Failures driven by upstream platform gaps (F.2 / F.3 / F.4 per the W34 expectations directive) surface as **red CI** that we publish as a forcing function — see §5.5 below.

### 0.3 New binding rule R-RIA-9

**v1.** R-RIA-1..R-RIA-8 (eight binding boundary rules).

**v2.** Adds **R-RIA-9** (single statement; full text in §13):

> Files under `ria/global_layer/**`, `ria/orchestration/**`, `ria/api/**`, `ria/observability/**`, `ria/user/**`, `ria/domain/**`, and `ria/config/**` MUST NOT directly import outbound-network or outbound-process libraries (`httpx`, `requests`, `urllib`, `urllib3`, `mcp`, `subprocess`, `asyncio.create_subprocess_exec`). All such calls MUST route through either `ria/platform_client/**` (for hi-agent platform calls) or `ria/external_services/**` (for non-platform external calls). The two seams are the only files allowed to perform outbound I/O.

Enforcement: `scripts/check_external_services_seam.py` (new). Companion gate G-RIA-19 (see `ria-quality-requirements-v1.md` v1.1).

### 0.4 Test discipline: integration uses real local `agent_server`

**v1.** L2 integration tests run against a stub `agent_server` (`tests/integration/_stubs/agent_server_stub.py` per `ria-platform-contract-mapping-v1.md` §9). Real platform integration was deferred behind hi-agent W31 BLOCKERs.

**v2.** L2 integration tests run against a real `agent-server serve` subprocess via a session-scope pytest fixture (`tests/integration/conftest.py::real_agent_server`). The stub is retained as a **historical artifact** and as a **fast-feedback loop for early TDD red phase** in `tests/_stubs/` but is no longer the basis for any PASS claim under the `integration` marker. The pytest marker `integration` is updated in `pyproject.toml` from "real RIA wiring against a stub agent_server" to "real RIA wiring against a real local agent-server subprocess".

Enforcement: gate G-RIA-20 (new) — `scripts/check_integration_uses_real_server.py`.

### 0.5 Forcing-function red-status artifact

**v1.** No structured RIA → hi-agent feedback artifact at the CI layer.

**v2.** RIA publishes `docs/ria/red-status/<head>.json` on every commit to RIA `main`. The JSON enumerates: tests blocked by platform gaps (with `blocked_by_wave_id` cross-references — wave-agnostic since v2.0.1 schema rev 1.1; `blocked_by_w34_id` retained as compat field through R-Wave-5), tests broken internally to RIA, and tests green at HEAD. This is the operational link between RIA's red CI and hi-agent's wave-cycle closure work. See §5.6 and the wave-cycle directives (§0.8 cross-references the active directives).

### 0.6 Two new architecture decisions

| ID | Decision | This doc |
|---|---|---|
| ADR-RIA-11 | Mirror hi-agent's two-seam pattern: introduce `ria/external_services/` as the second seam | §0.1, §5 |
| ADR-RIA-12 | A.3.α policy — Phase 3 implementation against real `agent-server serve`; red CI as forcing function; no defense-in-depth shims | §0.2, §0.5, §5.5–5.6 |

ADR-RIA-1..10 from v1 carry forward unchanged.

### 0.7 Migration plan

§14 (new section in this v2) states the v1 → v2 migration plan: which packages get scaffolded when, which v1 conventions become deprecated when, and the deprecation window for `tests/integration/_stubs/`.

### 0.8 W34 closure consumption (v2.0.1, 2026-05-05)

The seven hi-agent W34 BLOCKERs from `hi-agent-wave34-engineering-expectations-2026-05-04.md` §3 are **CLOSED at hi-agent HEAD `77222f8b`** (per `D:\chao_workspace\hi-agent\docs\downstream-responses\2026-05-05-w34-delivery-notice.md` and acknowledged in `hi-agent-wave35-acceptance-and-wave36-expectations-2026-05-05.md` §0.1). Consequence for this v2 architecture:

| What v2 designed against | Pre-W34 state | Post-W34 state | v2 design impact |
|---|---|---|---|
| `evolution_engine/postmortem.py` lineage chain reconstruction | F.2 hardcoded empty | populated correctly (commit `8978f0eb`) | No design change. The integration test that v2 §6.4 illustrates as "red until W34 closes" is now expected GREEN. |
| `paper_archive/` cross-tenant query 404 expectation | F.4 KG partition open | per-tenant directory layout (commits `68fc5ed7` + `5809e422`) | No design change. Tests now expected GREEN. |
| R-RIA-6 startup compatibility check (manifest posture) | manifest field unspec'd | `agent_server/contracts/manifest.py::ManifestResponse` frozen with `posture: PostureLiteral` (digest `cc55145f`) | v2 §13 "permitted exceptions" section continues to permit RIA's parse of `/v1/manifest` via `platform_client/`. |
| Cross-process idempotency replay correctness | untested | spec'd + tested at `agent_server/contracts/idempotency.py` (TTL=86400s, scope=tenant) | v2 §8.5 idempotency rationale now grounded on a frozen platform contract; `platform_client/idempotency.py` implements against this contract. |
| Concurrency baseline for sizing `ria/api/http/` burst handling | no baseline | P50=77.5ms / P95=200.4ms @ N=50/M=5 (`provenance:real`); P50=28.0ms / P95=51.8ms @ N=10/M=1 | v2 §11 Risks "concurrency unverified" downgraded; sizing in `ria/user/budget.py` defaults can use these numbers as floor. |
| B-5 four-registry follow-through | unknown | published audit (`docs/governance/registry-tenant-scoping-audit-2026-05-04.md`); KG / KnowledgeWiki / RunQueue CLOSED, Skill API-layer closed schema-layer W35, Tool / Capability TENANT-AGNOSTIC by design | v2 §11 Risks "B-5 cross-tenant data partition... awaiting W34 status" replaced by "SkillRegistry schema-layer pending W35; otherwise complete". |

**No structural change to v2.** The two-seam pattern (S2), A.3.α forcing function, R-RIA-9 boundary rule, and the eight Phase 3 external-service clients (§5.2) all carry forward unchanged. The v2 design was correct under the W33 + W34-pending state; W34 closure validates the design rather than requiring revision.

**Forcing function continues operating against the W35 plan.** Per §5.6 below, `docs/ria/red-status/<head>.json` is renamed-key compatible (`blocked_by_wave_id` instead of `blocked_by_w34_id`). The W35 plan publishes 8 carryover items at `D:\chao_workspace\hi-agent\docs\superpowers\plans\2026-05-05-wave-35-systematic-audit-followups.md`; three of those (W35-T1 frozen-contract spine, W35-T3 INVERTED posture, W35-T4 idempotency TTL purge) carry RIA-HIGH priority signals (per the W35 acceptance directive §3). The red-status mapping yaml `tests/_blocked_by_platform.yaml` is updated to reference these W35-T IDs; the W34 entries are retired (kept as comments for traceability).

---

## 1. Introduction and Goals

(Unchanged from v1 §1, with the following adjustments to acknowledge v2 shape.)

RIA is the research-domain application layer that drives long-running PI Agent research projects on the hi-agent platform. RIA is the only system above hi-agent that:

- Knows research-domain concepts (Project, Phase, Hypothesis, Claim, AC, Paper, Theorem, Experiment, Dataset, Review, PI Agent role, SkillDelta).
- Owns user-level identity, ACL, and per-user budget envelopes.
- Drives entry protocols for human use (CLI, MCP for Codex / Claude Code, HTTP / SSE for a web front-end).
- **(v2 addition)** Curates cross-project assets (Paper Archive, Lean Library, Dataset Registry, Evolution Engine) implemented in real form — not stubs.

RIA does **not** execute agent runs, manage agent memory at the L0/L1/L2/L3 tier, route LLM calls, or persist run state. Those are platform concerns owned by hi-agent's `agent_server` v1 northbound contract.

### 1.1 Primary goals (revised)

1. Compile a `ResearchProjectSpec` into a platform `RunRequest` + `SkillSpec` set that hi-agent's `agent_server` can execute deterministically. *(unchanged from v1)*
2. Maintain user-level identity, ACL, and per-user budget *above* the platform's per-tenant envelope. *(unchanged)*
3. Provide three entry protocols (CLI, MCP, HTTP/SSE) that speak research-domain vocabulary, not platform vocabulary. *(unchanged)*
4. Curate cross-project assets via `global_layer/` implemented in real form against real platform calls. **(v2: was Phase 3+ stub; now real)**
5. Stay strictly above the platform boundary — never import `hi_agent.*` or `agent_kernel.*`, never reach LLM providers directly. *(unchanged)*
6. **(v2 new)** Reach non-platform external services (arxiv, semantic scholar, DOI, GitHub, Lean local executable, Zenodo, HuggingFace) only through `external_services/`; isolate every outbound boundary at the seam.

### 1.2 Quality requirements (binding) (revised)

See `ria-quality-requirements-v1.md` (v1.1 this wave). Headlines:

- 0 imports of `hi_agent.*` or `agent_kernel.*` from any RIA module (R-RIA-1, CI gate).
- All RIA write operations to the platform carry an `Idempotency-Key` (R-RIA-5).
- TDD red-sha annotation on every new route handler / facade method (R-RIA-7).
- RIA's own posture system (dev / research / prod) coupled to platform posture: RIA `prod` requires platform ≥ `research` (R-RIA-6).
- **(v2 new)** No outbound I/O outside `platform_client/` or `external_services/` seams (R-RIA-9, CI gate).
- **(v2 new)** Integration tests run against real local `agent-server serve` subprocess; stub usage explicitly forbidden under `integration` marker (G-RIA-20).

---

## 2. Constraints

(Carried forward from v1 §2 with two additions.)

| Constraint | Source |
|---|---|
| Python 3.12+ | Match hi-agent runtime; `pyproject.toml` |
| FastAPI/Starlette for HTTP entry | Same stack as platform; reduces operator skill duplication |
| `httpx` for `platform_client/` and `external_services/` async transports | Async-first; matches hi-agent's HTTP gateway pattern |
| `mcp` Python SDK for MCP server | Codex / Claude Code MCP integration |
| SQLite for RIA-owned persistence (user ACL, budget, project metadata, paper/dataset cache) | No second database operator; RIA's persistence is independent of platform persistence |
| RIA's domain layer (`ria/domain/`) is pure stdlib | R-RIA-2 |
| RIA never imports `hi_agent.*` or `agent_kernel.*` | R-RIA-1 |
| Only `ria/platform_client/` may import `agent_server.contracts.*` | R-RIA-3 |
| All entry-protocol surfaces (CLI / MCP / HTTP) speak research-domain vocabulary | R-RIA-4 |
| All platform write operations carry `Idempotency-Key` | R-RIA-5 |
| **(v2)** All outbound I/O confined to two seams: `platform_client/` (platform) and `external_services/` (non-platform) | R-RIA-9 |
| **(v2)** Integration tests use a real `agent-server serve` subprocess fixture | G-RIA-20 |

---

## 3. System Context (v2)

```
┌───────────────────────────────────────────────────────────────────────────────┐
│  Researchers / Operators / Front-end                                           │
│    ┌──────────────────┐    ┌────────────────┐    ┌──────────────────┐         │
│    │ Codex / CC (MCP) │    │ Web front-end  │    │ Operator CLI     │         │
│    └────────┬─────────┘    └───────┬────────┘    └────────┬─────────┘         │
└─────────────┼────────────────────┼─────────────────────┼──────────────────────┘
              │ MCP                │ HTTP / SSE          │ stdin/stdout
              ▼                    ▼                     ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│  RIA process (this repo)                                                       │
│    ria/api/{mcp,http,cli}                                                      │
│    ria/{domain, orchestration, global_layer, user, observability, config}      │
│    ┌─────────────────────┐                ┌─────────────────────┐             │
│    │ ria/platform_client │                │ ria/external_services│            │
│    │  (hi-agent seam)    │                │  (non-platform seam) │            │
│    └──────────┬──────────┘                └──────────┬──────────┘             │
└───────────────┼──────────────────────────────────────┼────────────────────────┘
                │ HTTP /v1/* + SSE                     │ HTTPS (per-service)
                ▼                                      ▼
┌───────────────────────────────────────┐    ┌─────────────────────────────────┐
│  hi-agent platform (separate repo,    │    │  External services              │
│  separate process, separate ops)      │    │  ─────────────────              │
│    agent_server/  (northbound facade) │    │  - arxiv.org API                │
│    hi_agent/      (runtime kernel;    │    │  - semanticscholar.org API      │
│                    RIA never sees)    │    │  - doi.org / crossref           │
│    agent_kernel/  (execution          │    │  - github.com (papers + data)   │
│                    substrate; RIA     │    │  - Lean local executable        │
│                    never sees)        │    │  - zenodo.org                   │
└───────────────────┬───────────────────┘    │  - huggingface.co/datasets      │
                    │ HTTPS (sole egress)    └─────────────────────────────────┘
                    ▼
                LLM Providers (Anthropic / OpenAI / Volces Ark)
```

**Key change vs v1.** The `external_services/` second seam is structurally separate from `platform_client/`. They share no transport configuration: each seam has its own per-target client, its own retry policy, and its own observability counter family. This separation is the structural enforcement that "the platform is one of N outbound boundaries, not the only one" — and it surfaces violations (e.g., `paper_archive` accidentally calling arxiv via the platform, or `evolution_engine` accidentally calling the platform via the external_services seam) at CI time.

**Downstream consumers of RIA:** researchers using Codex / Claude Code; researchers using a web front-end; operators using the CLI.

**Upstream dependencies of RIA (now two):**
1. hi-agent's `agent_server` v1 northbound contract over HTTP — sole upstream for everything platform-shaped.
2. The set of public external services listed in §5.2 below — sole upstream for everything not platform-shaped.

No other upstream dependency is permitted from any RIA subpackage outside the two seams.

---

## 4. Solution Strategy (v2)

| Decision | Rationale | Source |
|---|---|---|
| Three-layer architecture (entry-protocol → RIA domain → platform) | UI is not RIA, RIA is not platform | v1 ADR-RIA-1 |
| `agent_server` is southbound-delivered by hi-agent, not implemented by RIA | Multi-tenancy / quota / audit / streaming written once and shared across consumers | v1 ADR-RIA-2 |
| Model providers reachable only through hi-agent's LLMGateway | Determinism, cost optimisation, evolution-engine telemetry | v1 ADR-RIA-3 |
| Entry protocols connect to RIA, not directly to `agent_server` | User-facing protocols are research-shaped, not generic-agent-shaped | v1 ADR-RIA-4 |
| RIA domain layer is pure stdlib (no platform imports) | Lets us swap platforms without rewriting domain logic | v1 ADR-RIA-5 |
| RIA owns user-level ACL and budget; platform owns tenant-level quota | Layering: RIA maps user → project → platform tenant; platform never sees user_id | v1 ADR-RIA-6 |
| TDD red-sha discipline mirrored from hi-agent's R-AS-5 | Consistent test-first discipline across both teams | v1 ADR-RIA-7 |
| RIA's own dev/research/prod posture, coupled to platform posture | RIA can be in `dev` while platform is in `research`; RIA in `prod` requires platform ≥ `research` | v1 ADR-RIA-8 |
| **(v2)** Mirror hi-agent's two-seam pattern: `platform_client/` + `external_services/` | Structural separation of outbound boundaries; auditable single-point-of-failure-per-target | **ADR-RIA-11** |
| **(v2)** Phase 3 going real (A.3.α): build real, no mocks, red CI is honest | Mock-based filtering of real problems was the dominant rework cause in 2026-04 / 2026-05 | **ADR-RIA-12** |
| **(v2)** Integration tests run against real local `agent-server serve` subprocess | Operationalises ADR-RIA-12 at the test boundary | **ADR-RIA-12** |
| **(v2)** RIA publishes `docs/ria/red-status/<head>.json` on every commit | Operational forcing function for the W34+ wave-cycle conversation with hi-agent | **ADR-RIA-12** |
| **(v2)** No RIA-side defense-in-depth shims that mask platform gaps | Such shims become permanent debt; cf. W31 §B-6 "naming accretion is a defect" | **ADR-RIA-12** |

---

## 5. Building Block View (v2)

```
┌──────────────────────────────── ria ─────────────────────────────────────────┐
│                                                                              │
│  ┌─── api ────────────────────────────────────────────────────────────────┐  │
│  │   cli/      (research project new / status / approve / paper add ...)  │  │
│  │   mcp/      (MCP tools for Codex / CC)                                 │  │
│  │   http/     (HTTP / SSE for front-end)                                 │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                              │                                               │
│                              ▼                                               │
│  ┌─── orchestration ──────────────────────────────────────────────────────┐  │
│  │   pi_agent.py        — PI Agent role spec → SkillSpec compiler          │  │
│  │   phase_pipeline.py  — 6-step writing-team / phase machine              │  │
│  │   backtrack.py       — Backtrack policy when AC fails                   │  │
│  │   replanner.py       — StageDirective wiring (calls /signal)            │  │
│  │   compiler.py        — ResearchProjectSpec → RunRequest+SkillSpec       │  │
│  │   project_state.py   — Project lifecycle state machine                  │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                              │                                               │
│  ┌── global_layer (v2: REAL, not stub) ───────────┐  ┌─── domain ────────┐   │
│  │ paper_archive/                                  │  │  project          │   │
│  │   ingest.py    — fetch + normalise              │  │  phase            │   │
│  │   curate.py    — promote candidate→archived     │  │  hypothesis       │   │
│  │   citation_graph.py                             │  │  claim            │   │
│  │ lean_library/                                   │  │  acceptance       │   │
│  │   verify.py    — invoke local Lean              │  │  role             │   │
│  │   index.py     — verified-theorem index         │  │  gate             │   │
│  │ dataset_registry/                               │  │  paper            │   │
│  │   ingest.py    — zenodo / huggingface fetch     │  │  theorem          │   │
│  │   versioning.py                                 │  │  experiment       │   │
│  │ evolution_engine/                               │  │  dataset          │   │
│  │   postmortem.py — read run records, attribute   │  │  review           │   │
│  │   skill_delta.py — cross-project delta index    │  │  artifact         │   │
│  │   champion_challenger.py                        │  │  skill_delta      │   │
│  └─────────────────────────────────────────────────┘  │                   │   │
│                              │                       │  pure stdlib      │   │
│                              ▼                       │  no platform      │   │
│  ┌───────────────────────────────────────┐           │  no httpx         │   │
│  │ ria/platform_client (seam 1)          │           └───────────────────┘   │
│  │   transport_http.py  — async HTTP /v1/* │                                  │
│  │   transport_mcp.py   — alt transport    │                                  │
│  │   tenant_resolver.py                    │                                  │
│  │   budget_enforcer.py — pre-call check   │                                  │
│  │   run_lifecycle.py   — long-run resumer │                                  │
│  │   streaming.py       — SSE consumer     │                                  │
│  │   idempotency.py     — key gen + retry  │                                  │
│  │   errors.py          — translate ContractError → RIA domain error          │
│  └───────────────────────────────────────┘                                    │
│                                                                              │
│  ┌───────────────────────────────────────┐                                    │
│  │ ria/external_services (seam 2; v2)    │                                    │
│  │   arxiv_client.py                       │                                  │
│  │   semantic_scholar_client.py            │                                  │
│  │   doi_client.py                         │                                  │
│  │   github_paper_client.py                │                                  │
│  │   github_dataset_client.py              │                                  │
│  │   lean_runner.py     — subprocess       │                                  │
│  │   zenodo_client.py                      │                                  │
│  │   huggingface_client.py                 │                                  │
│  │   cassette.py        — record/replay HTTP for unit/integration tests       │
│  │   errors.py          — typed external-service errors                       │
│  │   retry.py           — per-target retry / backoff policy                   │
│  │   ARCHITECTURE.md    — per-seam README                                     │
│  └───────────────────────────────────────┘                                    │
│                                                                              │
│  ┌─── user ─────────────────────────────┐  ┌─── observability ────────────┐  │
│  │ identity.py — user↔profile resolution │  │ counters.py                  │  │
│  │ acl.py      — project-level ACL       │  │ tracing.py                   │  │
│  │ budget.py   — per-user envelope       │  │ audit.py — RIA audit trail   │  │
│  │ store.py    — SQLite persistence      │  │ red_status.py — emit JSON    │  │
│  └──────────────────────────────────────┘  └──────────────────────────────┘  │
│                                                                              │
│  ┌─── config ─────────┐                                                      │
│  │ settings.py         │                                                     │
│  │ posture.py          │                                                     │
│  └─────────────────────┘                                                     │
└──────────────────────────────────────────────────────────────────────────────┘
                                   │                              │
                                   ▼  HTTP /v1/* + SSE            ▼  HTTPS / subprocess
                          (seam 1: platform)              (seam 2: external services)
```

### 5.1 Subpackage responsibilities (v2)

| Subpackage | Responsibility | Allowed imports | Forbidden imports |
|---|---|---|---|
| `ria/domain/` | Pure domain dataclasses + invariants | stdlib only | `agent_server.*`, `hi_agent.*`, httpx, starlette, fastapi, mcp |
| `ria/orchestration/` | Compile spec into platform calls; phase pipeline; backtrack | `ria.domain.*`, `ria.platform_client.*`, `ria.user.*`, `ria.observability.*`, `ria.config.*` | `hi_agent.*`, `agent_kernel.*`, **httpx, requests, urllib, mcp, subprocess (R-RIA-9)** |
| `ria/global_layer/` | Cross-project assets (paper_archive, lean_library, dataset_registry, evolution_engine) | `ria.domain.*`, `ria.platform_client.*`, `ria.external_services.*`, `ria.user.*`, `ria.observability.*`, `ria.config.*` | `hi_agent.*`, `agent_kernel.*`, **httpx, requests, urllib, mcp, subprocess (R-RIA-9)** |
| `ria/platform_client/` | **Seam 1**: single seam to hi-agent's `agent_server` v1 | `agent_server.contracts.*` (as type shape only); httpx | `hi_agent.*`, `agent_kernel.*`; non-platform external services |
| `ria/external_services/` (v2) | **Seam 2**: outbound to non-platform external services (arxiv, semantic-scholar, DOI, github, lean, zenodo, huggingface) | httpx; `subprocess` for `lean_runner.py` only; `ria.domain.*`; `ria.observability.*`; `ria.config.*` | `agent_server.*`, `hi_agent.*`, `agent_kernel.*`; the platform |
| `ria/user/` | Application-level identity / ACL / per-user budget | stdlib + sqlite3; `ria.domain.*`; `ria.config.*` | platform types; `httpx`; `subprocess` |
| `ria/api/cli/` | Operator + researcher CLI | `ria.*` (other than `external_services` and `platform_client` direct) | platform types (except `errors`); direct httpx |
| `ria/api/mcp/` | MCP server for Codex / Claude Code | `ria.*` + `mcp` lib | platform types (except `errors`); direct httpx |
| `ria/api/http/` | HTTP / SSE for front-end | `ria.*` + starlette / fastapi | platform types (except `errors`); direct httpx |
| `ria/observability/` | RIA-owned counters / tracing / audit / red_status emission | `ria.*` (read-only); stdlib; pydantic for JSON ser | platform types; `httpx`; `subprocess` |
| `ria/config/` | Settings + posture | stdlib | platform types; `httpx` |

CI enforcement of this matrix is in `scripts/check_layering.py` (v1.1; checks R-RIA-1..3) and `scripts/check_external_services_seam.py` (new; checks R-RIA-9). See `ria-quality-requirements-v1.md` v1.1 §3.

### 5.2 External services: per-target inventory and intent

Each external-service client lives in `ria/external_services/`. Each has a documented contract (per-file docstring) describing: purpose, target URL pattern, auth model, rate-limit policy, cassette presence for tests.

| Client | Target | Used by | Auth | Rate limit | Cassette dir |
|---|---|---|---|---|---|
| `arxiv_client.py` | `export.arxiv.org` API | `paper_archive/ingest.py` | none | 1 req / 3 s (per arxiv ToS) | `tests/_cassettes/arxiv/` |
| `semantic_scholar_client.py` | `api.semanticscholar.org` | `paper_archive/ingest.py`, `paper_archive/citation_graph.py` | API key (env `SEMANTIC_SCHOLAR_API_KEY`); none if unset (degraded) | 100 req / 5 min (free) or 1k req / 5 min (keyed) | `tests/_cassettes/semantic_scholar/` |
| `doi_client.py` | `doi.org`, `api.crossref.org` | `paper_archive/ingest.py` | none | 50 req / s (crossref polite pool) | `tests/_cassettes/doi/` |
| `github_paper_client.py` | `api.github.com` (papers in repos / releases) | `paper_archive/ingest.py` | `GITHUB_TOKEN` env | 5k / hr (auth) or 60 / hr (anon) | `tests/_cassettes/github_paper/` |
| `github_dataset_client.py` | `api.github.com` (dataset releases) | `dataset_registry/ingest.py` | same as above | same | `tests/_cassettes/github_dataset/` |
| `lean_runner.py` | local `lean` executable | `lean_library/verify.py` | none (local) | n/a | n/a (real exec in tests) |
| `zenodo_client.py` | `zenodo.org` API | `dataset_registry/ingest.py` | optional `ZENODO_TOKEN` | 60 req / min | `tests/_cassettes/zenodo/` |
| `huggingface_client.py` | `huggingface.co` datasets API | `dataset_registry/ingest.py` | optional `HF_TOKEN` | 1k req / hr | `tests/_cassettes/huggingface/` |

**Cassette policy.** All non-local external services use record-and-replay cassettes for unit tests. Real HTTP traffic is permitted in `tests/integration/` (where the cassette would mask real-world variability) and in `tests/conformance/` only when explicitly testing the external service's contract itself; otherwise integration tests use cassettes too. `lean_runner.py` does not have a cassette — Lean's local execution is part of the test loop.

**Degradation.** Each client supports a degraded mode when its auth token is absent: arxiv works without auth at lower rate; semantic-scholar works without auth at lower rate; doi works without auth; github works at 60 req / hr without token; zenodo + huggingface work at lower rate without tokens. Degradation is logged at `WARNING`; tests mark expectations accordingly.

**Cross-cutting error envelope.** `ria/external_services/errors.py` defines `ExternalServiceError`, `ExternalServiceTimeout`, `ExternalServiceRateLimited`, `ExternalServiceAuthFailure`, `ExternalServiceUnavailable`. `ria/global_layer/` callers handle these typed errors; raw `httpx.HTTPError` never surfaces past the seam.

### 5.3 `ria/global_layer/` real implementation surface

The four global-layer modules now have committed shape:

#### 5.3.1 `paper_archive/`

| File | Role | Key dependencies |
|---|---|---|
| `__init__.py` | Public surface: `ingest_paper(...)`, `curate_promote(...)`, `search_archive(...)` | — |
| `ingest.py` | Fetch paper from {arxiv, semantic_scholar, doi, github_paper}; normalise; canonical id | `ria.external_services.{arxiv,semantic_scholar,doi,github_paper}_client`; `ria.domain.paper.Paper` |
| `curate.py` | Promote candidate → ARCHIVED with curator user_id + ACL gate | `ria.user.acl`; `ria.domain.paper`; `ria.platform_client.write_artifact` (cold-write-once) |
| `citation_graph.py` | Build / query Paper × CitationEdge graph | `ria.domain.paper.CitationEdge`; SQLite via `ria.user.store` |
| `search.py` | BM25-over-archived; tag filter; author filter | `ria.domain.paper`; SQLite FTS5 |
| `ARCHITECTURE.md` | Per-module README | — |

#### 5.3.2 `lean_library/`

| File | Role | Key dependencies |
|---|---|---|
| `__init__.py` | Public surface: `verify_proof(...)`, `index_theorem(...)`, `query_dependencies(...)` | — |
| `verify.py` | Invoke `lean` binary on a proof file; capture stdout/stderr; classify VERIFIED / REFUTED / TIMEOUT | `ria.external_services.lean_runner` |
| `index.py` | Maintain verified-theorem index; theorem dependency closure | `ria.domain.theorem.Theorem`; SQLite |
| `cas_store.py` | Content-addressed storage for proof files (sha256 → bytes) | `$RIA_DATA_DIR/lean_cache/` |
| `ARCHITECTURE.md` | Per-module README | — |

#### 5.3.3 `dataset_registry/`

| File | Role | Key dependencies |
|---|---|---|
| `__init__.py` | Public surface: `ingest_dataset(...)`, `register_version(...)`, `query_registry(...)` | — |
| `ingest.py` | Fetch from {zenodo, huggingface, github_dataset}; normalise; sha256 | `ria.external_services.{zenodo,huggingface,github_dataset}_client`; `ria.domain.dataset.Dataset` |
| `versioning.py` | Per-dataset version chain; immutability of registered versions | `ria.domain.dataset` |
| `provenance.py` | Provenance tag (per CLAUDE.md provenance ladder) handling | `ria.domain.dataset.ProvenanceTag` |
| `ARCHITECTURE.md` | Per-module README | — |

#### 5.3.4 `evolution_engine/`

| File | Role | Key dependencies |
|---|---|---|
| `__init__.py` | Public surface: `ingest_postmortem(...)`, `index_skill_delta(...)`, `compare_versions(...)` | — |
| `postmortem.py` | Read platform run records via `platform_client`; reconstruct attempt tree; produce `Postmortem` artifacts | `ria.platform_client.run_lifecycle`; `ria.domain.{run_record_view, postmortem}` (v1.1 additions) |
| `skill_delta.py` | Cross-project skill version diff; index by `(skill_id, project_id, wave)` | `ria.domain.skill_delta.SkillDelta` (v1.1 addition); SQLite |
| `champion_challenger.py` | Read champion vs challenger signals from platform; surface comparison | `ria.platform_client.transport_http`; `ria.domain.skill_delta` |
| `ARCHITECTURE.md` | Per-module README | — |

**Critical dependency on hi-agent W34 closures:**
- `postmortem.py` requires F.2 closure (`RunExecutionContext` lineage populated). Without F.2, `attempt_id` chain reconstruction returns disconnected nodes; postmortem grouping is incorrect.
- `skill_delta.py` requires F.3 closure (spine validation). Without F.3, a single missing-spine `ReasoningTrace` corrupts the delta index.
- All four modules (paper / lean / dataset / evolution) require F.4 closure (KG tenant partition) to avoid cross-tenant leakage in cached reads.

These dependencies are made operationally visible via the red-status JSON (§5.6).

---

### 5.4 `ria/api/{cli,mcp,http}/` v2 expansion

The entry-protocol layer expands to host MCP and HTTP in addition to CLI. Each entry surface speaks research-domain vocabulary (R-RIA-4); none expose platform verbs.

```
ria/api/
  cli/
    __init__.py
    __main__.py
    project_commands.py    # research project new / status / cancel / list
    gate_commands.py       # research gate D|E|F approve / reject / show
    paper_commands.py      # research paper add / curate / search
    dataset_commands.py    # research dataset register / list / show
    theorem_commands.py    # research theorem verify / index / query
    diagnostics.py         # research diagnostics
  mcp/
    __init__.py
    server.py              # MCP stdio server entry
    tools.py               # @mcp_tool definitions; one per CLI command
    resources.py           # MCP resource handlers (project state, papers)
  http/
    __init__.py
    app.py                 # FastAPI app factory
    routes/
      projects.py          # POST/GET /research/projects
      gates.py             # POST /research/projects/{id}/gates/{kind}/decide
      papers.py            # GET /research/papers; POST /research/papers/curate
      datasets.py          # GET /research/datasets
      theorems.py          # POST /research/theorems/verify
      health.py            # GET /ria/health, /ria/diagnostics, /ria/metrics
    middleware/
      jwt_auth.py          # mirrors hi-agent W33-C.4 pattern; outermost
      ria_context.py       # builds RIAContext from auth + headers
      audit.py             # audit-log every write under prod posture
      sse.py               # SSE consumer wrapper
```

**Vocabulary check (R-RIA-4).** Every CLI command, MCP tool, and HTTP route name uses research-domain vocabulary. Forbidden vocabulary in user-visible names: `run`, `skill`, `memory`, `artifact`, `signal`, `capability`. The deny list is enforced by `scripts/check_no_generic_verbs.py`. Internal helper functions may use any naming.

---

### 5.5 A.3.α — Forcing-Function Test Discipline (v2)

**Statement.** All RIA `tests/integration/**` tests run against a real `agent-server serve` subprocess. No stub / mock / fake of `agent_server` is used in any test marked `integration`. Failures driven by hi-agent platform gaps (F.2, F.3, F.4, B-5 follow-through, manifest posture, idempotency cross-process, concurrency baseline) surface as red CI; we do not patch around them.

**Rationale.** Per `engineering-readiness-scorecard-2026-04-26-wave10.md` lineage and the W31 directive: mock-based filtering of real platform problems was the dominant rework cause in 2026-04 / 2026-05. We apply CLAUDE.md's "Using mocks to bypass real failures is strictly forbidden" rule at our integration-test boundary. Red CI is the operational signal that something real is broken.

**Test fixture.** `tests/integration/conftest.py::real_agent_server` (session-scope):

```python
@pytest.fixture(scope="session")
def real_agent_server():
    """Spawn a real agent-server serve subprocess for the test session.

    Requires:
      - hi-agent installed and on PATH (or AGENT_SERVER_BIN env var)
      - Port AGENT_SERVER_TEST_PORT (default 18000) available
      - Posture configured via AGENT_SERVER_TEST_POSTURE (default 'research')

    Yields the base URL; tears down on session end.
    """
    ... (subprocess.Popen + wait-for-/ready + yield + terminate)
```

**Stub retention as historical artifact.** The v1 stub at `tests/integration/_stubs/agent_server_stub.py` is moved to `tests/_stubs/agent_server_stub_v1.py` and explicitly tagged "historical — do not extend". A new `tests/_stubs/README.md` documents the move and the policy: stubs are permitted in `tests/unit/` for fast TDD red phase, never in `tests/integration/`.

**Enforcement.** `scripts/check_integration_uses_real_server.py` (gate G-RIA-20):
- AST-walk every file under `tests/integration/**`.
- Fail if any module under `tests/integration/**` imports `tests._stubs.*` or pattern-matches stub usage.
- Fail if any test function under `tests/integration/**` does not depend (transitively via fixture) on `real_agent_server` for any test that touches `ria.platform_client`.

**Cassette policy for `external_services/`.** `tests/integration/` against `external_services/` may use cassettes (per §5.2) to keep the test loop deterministic. Cassettes are recorded once against the live external service and replayed thereafter. Cassette age is monitored by `scripts/check_cassette_freshness.py` (warning if cassette is > 30 days old; failure if > 90 days old).

---

### 5.6 Red-status forcing-function artifact (v2; schema v1.1 in v2.0.1 erratum)

**Statement.** RIA publishes `docs/ria/red-status/<sha>.json` on every commit to RIA `main`. The JSON is the authoritative machine-readable cross-team status: which RIA tests are currently red, why, and which platform-side wave-ID closure would unblock each.

**Schema (v1.1, 2026-05-05):**

```json
{
  "schema_version": "1.1",
  "ria_head": "<git sha>",
  "ria_head_committed_at": "<iso8601>",
  "platform_head_under_test": "<git sha or '77222f8b-or-newer'>",
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
      "blocked_by_wave_id": "W35-T1",         // v1.1 — wave-agnostic field
      "blocked_by_w34_id": null,              // v1.0 compat field; emitted as null for non-W34 entries; retired in R-Wave-5
      "blocked_by_short": "13 frozen-contract dataclasses missing __post_init__",
      "first_observed_ria_head": "<sha>",
      "consecutive_red_commits": <int>,
      "last_traceback_excerpt": "<truncated, redacted>"
    },
    ...
  ],
  "internal_red": [
    {
      "test": "tests/unit/test_zzz.py::test_qqq",
      "owner": "ria-team",
      "first_observed_ria_head": "<sha>",
      "consecutive_red_commits": <int>
    },
    ...
  ],
  "green_test_count_by_dir": { "tests/unit/": <int>, "tests/integration/": <int>, "tests/conformance/": <int> }
}
```

**Producer.** `ria/observability/red_status.py::emit_red_status_json(...)` is invoked by the RIA CI pipeline after pytest completes. It reads pytest's `--json-report` output, classifies failures (platform-blocked vs internal) using a curated mapping `tests/_blocked_by_platform.yaml`, and writes the JSON to `docs/ria/red-status/<sha>.json`.

**Consumer.** hi-agent's W34+ wave-cycle conversation references this JSON. The W34 expectations directive §5.3 commits to publishing it.

**Privacy / leakage check.** Test tracebacks may contain user data or path information. The producer redacts: file paths under `$HOME`, env var values, anything matching `[A-Za-z0-9_-]{32,}` (potential token shape).

---

## 6. Runtime View (v2)

### 6.1 Happy-path: research project new (mostly unchanged from v1 §6)

(Carried forward from v1; refer to v1 §6 sequence diagram. The only v2 change is that `ria/api/cli` may now be `ria/api/mcp` or `ria/api/http`; the orchestration → platform_client path is identical.)

### 6.2 (v2 new) Phase 3: paper archive ingest

```
Researcher        ria/api/cli       ria/global_layer       ria/external_services      arxiv.org / s2 / doi
    │                │              /paper_archive/ingest          /arxiv_client            │
    │                │                    │                              │                  │
    │ research paper │                    │                              │                  │
    │  add arxiv:NNNN│                    │                              │                  │
    │───────────────▶│                    │                              │                  │
    │                │ ingest_paper(      │                              │                  │
    │                │  source='arxiv',   │                              │                  │
    │                │  id='NNNN')        │                              │                  │
    │                │───────────────────▶│                              │                  │
    │                │                    │ arxiv_client.fetch('NNNN')   │                  │
    │                │                    │─────────────────────────────▶│                  │
    │                │                    │                              │ GET arxiv API    │
    │                │                    │                              │─────────────────▶│
    │                │                    │                              │ ◀ XML metadata  │
    │                │                    │                              │ + PDF URL       │
    │                │                    │ ◀ ParsedPaper(...)           │                  │
    │                │                    │                              │                  │
    │                │                    │ to_domain.Paper(...)         │                  │
    │                │                    │ + content_hash               │                  │
    │                │                    │                              │                  │
    │                │                    │ platform_client.write_artifact(             │
    │                │                    │   tenant_id, content_hash,                  │
    │                │                    │   metadata={"kind":"paper","arxiv_id":"NNNN"})  │
    │                │                    │                              │                  │
    │                │                    │ Idempotency-Key: idem(       │                  │
    │                │                    │   "write_artifact",          │                  │
    │                │                    │   user_id, content_hash)     │                  │
    │                │                    │ ─────────────────────────────────────▶          │
    │                │                    │                              │  to platform     │
    │                │                    │ ◀ artifact_id                │                  │
    │                │                    │                              │                  │
    │                │                    │ store.papers.insert(...)     │                  │
    │                │                    │ (SQLite local cache)         │                  │
    │                │ ◀ Paper(paper_id=  │                              │                  │
    │                │   "arxiv:NNNN",    │                              │                  │
    │                │   archive_status=  │                              │                  │
    │                │   "candidate")     │                              │                  │
    │ ◀ {paper_id,   │                    │                              │                  │
    │   "candidate", │                    │                              │                  │
    │   needs_curate}│                    │                              │                  │
```

### 6.3 (v2 new) Phase 3: lean theorem verify

Similar shape; key difference is `ria/external_services/lean_runner.py` invokes a local subprocess (no HTTP). The `verify.py` returns `VERIFIED` / `REFUTED` / `TIMEOUT` based on Lean's exit code and timing.

### 6.4 (v2 new) Phase 3: evolution-engine postmortem (red until W34-F.2/F.3 close)

```
RIA scheduled job   ria/global_layer            ria/platform_client          agent_server
                    /evolution_engine                                       (real local)
                    /postmortem
        │                  │                          │                          │
        │ run weekly job   │                          │                          │
        │─────────────────▶│                          │                          │
        │                  │ list_recent_runs(        │                          │
        │                  │   tenant_id,             │                          │
        │                  │   since=7d)              │                          │
        │                  │─────────────────────────▶│                          │
        │                  │                          │ GET /v1/runs?since=...   │
        │                  │                          │─────────────────────────▶│
        │                  │                          │ ◀ run_id list           │
        │                  │ for each run_id:         │                          │
        │                  │   fetch_run_records(...) │                          │
        │                  │─────────────────────────▶│                          │
        │                  │                          │ GET /v1/runs/{id}        │
        │                  │                          │ + GET /v1/runs/{id}/events│
        │                  │                          │─────────────────────────▶│
        │                  │                          │ ◀ records w/ lineage    │
        │                  │                          │   *** F.2 IF UNCLOSED:  │
        │                  │                          │   parent_run_id=""      │
        │                  │                          │   attempt_id=""         │
        │                  │ reconstruct_attempt_tree(│                          │
        │                  │   records)               │                          │
        │                  │ *** assertion fails:     │                          │
        │                  │ rows[1].parent_run_id    │                          │
        │                  │   != rows[0].run_id      │                          │
        │                  │                          │                          │
        │                  │ TEST FAILS → red CI →    │                          │
        │                  │ red-status.json updated  │                          │
        │                  │ → W34 expectations §5.3  │                          │
```

This is the canonical illustration of the red-as-honest forcing function. The test is correctly written; the assertion fails because of an upstream gap. The platform fix closes the test.

---

## 7. Deployment View (v2)

```
┌── Host (Linux / Windows) ─────────────────────────────────────────────────┐
│                                                                           │
│  ┌── PM2 / systemd ──────────────────────────────────────────────────┐   │
│  │                                                                    │   │
│  │  ria process                                                       │   │
│  │  ───────────                                                       │   │
│  │   - python -m ria serve         (CLI entry; hosts MCP + HTTP)     │   │
│  │   - posture: research                                             │   │
│  │   - depends-on: agent_server (HTTP base URL via env)              │   │
│  │   - depends-on: lean (local executable, optional per project)     │   │
│  │                                                                    │   │
│  │  agent_server process (separately deployed by hi-agent team)      │   │
│  │  ─────────────────────                                             │   │
│  │   - python -m agent_server serve                                  │   │
│  │   - posture: research                                             │   │
│  │   - depends-on: hi_agent runtime in-process                       │   │
│  │                                                                    │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌── Data directories (RIA-owned) — v2 expansion ────────────────────┐   │
│  │   $RIA_DATA_DIR/ria.sqlite       (user, ACL, budget, project meta)│   │
│  │   $RIA_DATA_DIR/audit.jsonl      (RIA audit trail)                │   │
│  │   $RIA_DATA_DIR/checkpoints/     (project-level checkpoints)      │   │
│  │   $RIA_DATA_DIR/papers/          (v2: paper PDF + metadata cache) │   │
│  │   $RIA_DATA_DIR/lean_cache/      (v2: proof CAS + index)          │   │
│  │   $RIA_DATA_DIR/datasets/        (v2: dataset version chain)      │   │
│  │   $RIA_DATA_DIR/evolution/       (v2: postmortem + skill_delta)   │   │
│  │   $RIA_DATA_DIR/cassettes/       (v2: external_services replay)   │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌── Data directories (platform-owned) ─────────────────────────────┐    │
│  │   (managed by agent_server / hi_agent — RIA does not touch)      │    │
│  └───────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────┘
```

**Standard startup (v2):**

```bash
# 1. Install
pip install -e ".[http,mcp]"   # v2: http + mcp + base

# 2. Configure (RIA core)
export RIA_POSTURE=research
export RIA_DATA_DIR=/var/lib/ria
export AGENT_SERVER_BASE_URL=http://localhost:8000
export AGENT_SERVER_AUTH_TOKEN=<token-issued-by-hi-agent-ops>

# 3. Configure external services (v2)
export SEMANTIC_SCHOLAR_API_KEY=<key>     # optional; degraded without
export GITHUB_TOKEN=<personal-access-token> # optional; degraded without
export ZENODO_TOKEN=<token>                 # optional
export HF_TOKEN=<huggingface-token>         # optional
export LEAN_BINARY_PATH=/usr/local/bin/lean # required for lean_library

# 4. Serve (foreground)
python -m ria serve --host 0.0.0.0 --port 8100

# 5. Serve under PM2 (production)
pm2 start "python -m ria serve --host 0.0.0.0 --port 8100" --name ria
```

**Posture matrix (unchanged from v1):**

| `RIA_POSTURE` | Min platform posture | Tenant context | Idempotency-Key | Per-user budget |
|---|---|---|---|---|
| `dev` | any | optional (defaults to `tenant_dev`) | optional | optional |
| `research` | `research` or `prod` | required | required for write routes | required |
| `prod` | `prod` | required + JWT validation | required for write routes | required + audit log |

**Readiness endpoints (v2 expansion):**
- `GET /ria/health` — 200 ready, 503 otherwise.
- `GET /ria/diagnostics` — compact fingerprint of resolved env / config / external-service auth status.
- `GET /ria/metrics` — Prometheus.
- `GET /ria/red-status` *(new in v2)* — returns the latest `red-status.json` content for ops visibility.

---

## 8. Cross-Cutting Concepts (v2 expansion)

### 8.1 Logging
(Unchanged from v1 §8.1.) Structured JSON; every cross-system call carries `(trace_id, project_id, run_id, user_id, tenant_id)`.

### 8.2 Error handling
(Unchanged from v1 §8.2 for `platform_client/`.) v2 adds `ria/external_services/errors.py` which exposes `ExternalServiceError` and subclasses; `ria/global_layer/` catches typed external-service errors and converts them to RIA domain errors (`RIA.PaperFetchFailed`, `RIA.LeanVerificationTimeout`, etc.). Raw `httpx.HTTPError` / `subprocess.SubprocessError` never crosses out of the seam.

### 8.3 Posture
(Unchanged from v1 §8.3.) RIA's `Posture.from_env()` + `assert_compatible_with_platform()` semantics carry forward.

### 8.4 Security
(Carried from v1 §8.4 with v2 addition.) v2 adds: external-service tokens (SEMANTIC_SCHOLAR_API_KEY, GITHUB_TOKEN, ZENODO_TOKEN, HF_TOKEN) live in env only; never logged; redacted in `red-status.json` producer per §5.6.

### 8.5 Idempotency
(Unchanged from v1 §8.5.) RIA → platform writes carry `Idempotency-Key`. v2 note: RIA depends on hi-agent W34 closure of B-W34-6 (cross-process replay semantics) for correctness under restart.

### 8.6 Long-run resumption
(Unchanged from v1 §8.6.) RIA persists `(project_id, run_id, last_seen_event_cursor)`; resumes on startup.

### 8.7 Tenant resolution
(Unchanged from v1 §8.7.)

### 8.8 (v2 new) External-service rate limiting and back-pressure

Each external-service client owns its own per-target rate limiter (token-bucket; configured per §5.2). Back-pressure surfaces to callers as `ExternalServiceRateLimited`. `ria/global_layer/` modules respect the back-pressure: `paper_archive/ingest.py` queues incoming ingestion requests when arxiv is rate-limited and resumes when token bucket refills. The CLI surfaces "queued — N items pending" status to the user.

Cross-target back-pressure is not coordinated at the seam (each target has its own bucket). Coordination across targets would require a global rate-limit budget; this is **out of scope for v2** and is a candidate for v3 if multi-source ingestion proves to oversaturate.

### 8.9 (v2 new) Cassette discipline

External-service tests use cassettes to record-and-replay HTTP traffic. The cassette format is compatible with `pytest-httpx` (or `vcr.py`; choice deferred to implementation). Cassettes are committed to git under `tests/_cassettes/<service>/`. Refresh policy:

- **Cassette age ≤ 30 days:** OK for any test layer.
- **Cassette age > 30 days, ≤ 90 days:** WARNING in CI; flagged for review.
- **Cassette age > 90 days:** test fails until cassette is refreshed (rerecord against live service).

This is enforced by `scripts/check_cassette_freshness.py` (advisory in v2; promoted to blocking in a future wave once the cassette set stabilises).

### 8.10 (v2 new) Forcing-function red-status

(See §5.6.)

---

## 9. Architecture Decisions (v2)

| ID | Decision | Source |
|---|---|---|
| ADR-RIA-1..10 | Carried forward unchanged from v1 §9 | v1 |
| **ADR-RIA-11** | Mirror hi-agent's two-seam pattern: `platform_client/` + `external_services/` | v2 §0.1, §5 |
| **ADR-RIA-12** | A.3.α — Phase 3 implementation against real `agent-server serve`; red CI as forcing function; no defense-in-depth shims that mask platform gaps | v2 §0.2, §0.5, §5.5–5.6 |
| **ADR-RIA-13** | Cassette-based testing for `external_services/` with 30/90-day age policy | v2 §8.9 |
| **ADR-RIA-14** | Per-target rate limiting at each external-service client; no cross-target coordination in v2 | v2 §8.8 |

---

## 10. Quality Requirements

See `ria-quality-requirements-v1.md` v1.1 for the full bar. Headlines (binding):

| Quality attribute | Target | Enforcement |
|---|---|---|
| Layering integrity | 0 imports of `hi_agent.*` / `agent_kernel.*` from any RIA module | `scripts/check_layering.py` (G-RIA-1) |
| Domain purity | `ria/domain/*` imports only stdlib | `scripts/check_no_platform_types.py` (G-RIA-2) |
| Idempotency coverage | Every platform-write call carries a key | `scripts/check_idempotency_keys.py` (G-RIA-5) |
| TDD evidence | Every route handler / facade method has `# tdd-red-sha:` | `scripts/check_tdd_evidence.py` (G-RIA-7) |
| Test pass rate | All unit + integration + conformance tests pass at HEAD | CI |
| Long-run resume | RIA process kill mid-run; restart; project resumes against same platform run_id | `tests/integration/test_run_lifecycle_restart.py` |
| Soak | RIA-side ≥ 4h soak driving real research workloads | `tests/soak/` |
| Posture coverage | All write paths posture-aware (dev=warn, research=fail-closed, prod=fail-closed + audit) | posture matrix tests |
| **(v2)** Two-seam outbound boundary | No outbound I/O outside `platform_client/` or `external_services/` | `scripts/check_external_services_seam.py` (G-RIA-19) |
| **(v2)** Integration uses real local agent-server | No stubs under `tests/integration/` | `scripts/check_integration_uses_real_server.py` (G-RIA-20) |
| **(v2)** Cassette age | All cassettes < 90 days; warning at 30 | `scripts/check_cassette_freshness.py` (G-RIA-21, advisory) |
| **(v2)** Red-status published | `docs/ria/red-status/<head>.json` exists at every commit | CI artifact upload step |

---

## 11. Risks and Technical Debt (v2)

| Item | Status | Mitigation |
|---|---|---|
| ~~hi-agent W34 BLOCKERs (F.2, F.3, F.4 + 4 new) not closed~~ → **CLOSED at hi-agent HEAD `77222f8b` (2026-05-05); see §0.8** | Closed | RIA red CI now sees the related tests GREEN; mapping yaml retires the W34 entries with comment-trail |
| ~~Cross-tenant data partition at platform KG / skill / tool registry not closed (B-5 follow-through)~~ → **Audited and substantially closed at W34**; SkillRegistry schema-layer pending hi-agent W35 (carryover with existing xfail `expiry_wave="Wave 35"`); other 5 stores closed-or-tenant-agnostic-by-design | Mostly closed; SkillRegistry schema-layer pending W35 | RIA `tests/conformance/test_cross_tenant_isolation_full_surface.py` will probe each scoped read route; `tests/integration/test_skill_registry_schema_partition*` is mapped to `blocked_by_wave_id: W35-T1` until W35 closes |
| Three RIA-HIGH-priority W35 plan items: T1 (frozen-contract spine validation × 13 dataclasses), T3 (INVERTED posture in run_manager), T4 (idempotency TTL purge — feasibility-blocking on Lens 7) | Open as of 2026-05-05; tracked in W35 hi-agent plan | RIA red CI surfaces each blocked test; W35 acceptance directive §3 carries the priority signals; no RIA-side defense-in-depth (per AP-9) |
| `external_services/` external-service variability (arxiv rate limits, GitHub API changes) | Inherent to consuming public APIs | Cassettes for unit/integration; `tests/conformance/` against live API runs only on demand |
| Lean local executable absence on user machines | Inherent | `lean_library/verify.py` returns `LeanNotInstalled` typed error; degraded mode skips Lean-dependent operations |
| `ria/platform_client/` is the single point of failure for platform compatibility | By design | Layering rule + conformance suite + frozen v1 contract minimise blast radius |
| **(v2 new)** Red-status JSON privacy leak via traceback contents | Mitigated | Producer redacts $HOME paths, env values, token-shaped strings |
| **(v2 new)** Cassette drift from live external-service contracts | Active concern | 30/90-day age policy; `tests/conformance/` runs against live periodically |
| **(v2 new)** Subprocess cost of `real_agent_server` fixture | Manageable | Session-scope; one spawn per test run; PostgreSQL backend untested in v2 (deferred) |

---

## 12. Glossary (v2 additions)

(v1 glossary carried forward unchanged.) v2 additions:

| Term | Definition |
|---|---|
| External Service | Any non-platform outbound target (arxiv, semantic scholar, DOI, GitHub, Lean local executable, Zenodo, HuggingFace) |
| Seam (in RIA) | A subpackage that mediates outbound I/O between RIA's domain code and an external system. v2 has two: `platform_client/` (seam 1) and `external_services/` (seam 2) |
| Cassette | Recorded HTTP request/response pair for replay during test, located under `tests/_cassettes/<service>/` |
| Red-status JSON | `docs/ria/red-status/<head>.json` — machine-readable enumeration of red tests at HEAD with platform-blocker attribution |
| A.3.α | The policy decision to build Phase 3 against real local `agent-server serve`, with red CI as forcing function and no RIA-side defense-in-depth shims |
| SkillDelta | A diff between two versions of the same skill across runs / projects, used by `evolution_engine/skill_delta.py` |
| Postmortem (RIA-side) | A reconstructed attempt tree + outcome attribution for a single PI Agent run, produced by `evolution_engine/postmortem.py` |
| Forcing function (in this context) | An operational signal — the red-status JSON — that turns RIA's CI state into a real-time blocker map for hi-agent's W34 closure work |

---

## 13. Boundary Rules (CI-Enforced) — v2

These rules are CI gates; each is binding and bypass requires architecture-discussion-archive entry.

| ID | Rule | Gate script | Status |
|---|---|---|---|
| **R-RIA-1** | `ria/*` MUST NEVER import from `hi_agent.*` or `agent_kernel.*` | `scripts/check_layering.py` | Live (Phase 1) |
| **R-RIA-2** | `ria/domain/*` MUST NOT import `agent_server.contracts.*` (domain decoupled from protocol) | `scripts/check_no_platform_types.py` | Live (Phase 1) |
| **R-RIA-3** | `ria/platform_client/*` is the only subpackage allowed to import `agent_server.contracts.*` | `scripts/check_layering.py` (pass 2) | Live (Phase 1) |
| **R-RIA-4** | `ria/api/{cli,mcp,http}/*` route handlers / tools / commands MUST use research-domain vocabulary | `scripts/check_no_generic_verbs.py` | Live (Phase 1) |
| **R-RIA-5** | All write methods in `ria/platform_client/transport_*.py` MUST generate an `Idempotency-Key` | `scripts/check_idempotency_keys.py` | Live (Phase 1) |
| **R-RIA-6** | RIA `prod` posture requires platform posture ≥ `research`; checked at startup | `ria/config/posture.py` startup assertion | Live (Phase 1) |
| **R-RIA-7** | Every new route handler / facade method has a `# tdd-red-sha: <sha>` annotation | `scripts/check_tdd_evidence.py` | Phase 2 |
| **R-RIA-8** | Persistent dataclasses in `ria/{user,orchestration,global_layer}/` declare `tenant_id` or `project_id` (or both) as required fields | `scripts/check_contract_spine_completeness.py` | Phase 2 |
| **R-RIA-9** *(v2)* | Files outside `ria/platform_client/**` and `ria/external_services/**` MUST NOT directly import `httpx`, `requests`, `urllib`, `urllib3`, `mcp`, `subprocess`, `asyncio.create_subprocess_exec` | `scripts/check_external_services_seam.py` | **Phase 2 (this wave)** |

**R-RIA-9 full statement.**

> **Statement.** Outbound I/O — any call that sends bytes outside the RIA process — MUST be issued by code physically located in `ria/platform_client/**` (for hi-agent platform calls) or `ria/external_services/**` (for non-platform external service calls). All other RIA subpackages (`ria/domain/`, `ria/orchestration/`, `ria/global_layer/`, `ria/api/{cli,mcp,http}/`, `ria/observability/`, `ria/user/`, `ria/config/`) MUST route their outbound needs through one of the two seams.
>
> **Forbidden imports outside the two seams:**
> - `httpx`, `requests`, `urllib`, `urllib3`, `aiohttp`
> - `mcp.client.*`
> - `subprocess`, `asyncio.create_subprocess_exec`, `asyncio.create_subprocess_shell`
> - `socket` (raw), `ssl` (raw)
>
> **Permitted exceptions** (with `# r-ria-9-exception: <reason>` annotation):
> - `ria/api/http/` may import `starlette`, `fastapi`, `uvicorn` for the *inbound* HTTP server (these are not outbound I/O).
> - `ria/api/mcp/` may import `mcp.server.*` for the *inbound* MCP stdio server (not outbound).
> - `ria/observability/` may import `prometheus_client` or equivalent metrics-emission libraries.
>
> **Rationale.** Two reasons. (1) Outbound I/O is the most consequential point of platform-vs-not-platform separation; conflating them at the import level leaks platform concerns into application code (`global_layer` accidentally importing `agent_server.contracts.*` to call platform), or leaks external-service concerns into platform-aware code (`platform_client` accidentally calling arxiv). Either failure mode is structural debt that scales with codebase size. (2) A single auditable "what does RIA call out to" surface is critical for tenant isolation, security review, and cost attribution.
>
> **Gate.** `scripts/check_external_services_seam.py` AST-walks every `ria/**/*.py`. For each `Import` / `ImportFrom`, it checks the imported module against the forbidden list and the importing module's path. Fails on any unannotated violation.

---

## 14. Migration Plan v1 → v2

This plan operationalises the v1 → v2 transition. v1 stays live for ≥ 2 RIA waves (per `ria-quality-requirements-v1.md` §10) which means v1 documentation remains in the repo and v1's structural conventions remain valid in any code that has not yet been touched. v2 conventions apply to any new file or any meaningfully edited file.

### 14.1 Sequencing

| Step | Action | Wave / when | Owner |
|---|---|---|---|
| 1 | Publish v2 architecture document (this file) | 2026-05-04 (R-Wave-2) | RIA architecture |
| 2 | Publish v1.1 of three L1 docs (quality / domain / platform-contract-mapping) | 2026-05-04 (R-Wave-2) | RIA architecture |
| 3 | Publish W34 expectations directive to hi-agent | 2026-05-04 (R-Wave-2) | RIA architecture |
| 4 | Scaffold `ria/external_services/` with all clients (real implementations + cassettes) | R-Wave-2 → R-Wave-3 | RIA platform team |
| 5 | Scaffold `ria/global_layer/{paper_archive,lean_library,dataset_registry,evolution_engine}/` | R-Wave-2 → R-Wave-3 | RIA global-layer team |
| 6 | Expand `ria/orchestration/` (phase_pipeline, backtrack, replanner, project_state) | R-Wave-2 → R-Wave-3 | RIA orchestration |
| 7 | Expand `ria/user/` (acl, budget) | R-Wave-2 | RIA application |
| 8 | Expand `ria/api/` (mcp, http) | R-Wave-2 → R-Wave-3 | RIA application |
| 9 | Expand `ria/domain/` (hypothesis, claim, acceptance, gate, paper, theorem, experiment, dataset, review, artifact, skill_delta) | R-Wave-2 | RIA domain |
| 10 | Expand `ria/observability/` (tracing, audit, red_status) | R-Wave-2 | RIA observability |
| 11 | Expand `ria/platform_client/` (streaming, budget_enforcer, run_lifecycle) | R-Wave-2 | RIA platform team |
| 12 | Implement five new CI gates: G-RIA-7, G-RIA-9, G-RIA-10, G-RIA-11, G-RIA-12 (the Phase 2 quality gates from `ria-quality-requirements-v1.md` §3) | R-Wave-2 | RIA platform team |
| 13 | Implement two new v2 CI gates: G-RIA-19 (R-RIA-9 seam), G-RIA-20 (real-agent-server) | R-Wave-2 | RIA platform team |
| 14 | Move `tests/integration/_stubs/agent_server_stub.py` → `tests/_stubs/agent_server_stub_v1.py` (deprecation move) | R-Wave-2 | RIA test team |
| 15 | Implement `tests/integration/conftest.py::real_agent_server` fixture | R-Wave-2 | RIA test team |
| 16 | Backfill all existing `tests/integration/` to use `real_agent_server` fixture | R-Wave-2 → R-Wave-3 | RIA test team |
| 17 | Implement `ria/observability/red_status.py` + CI step to emit `docs/ria/red-status/<sha>.json` | R-Wave-2 | RIA observability |
| 18 | Retire v1 architecture document (move to `docs/ria/historical/`) | R-Wave-4 (≥ 2 waves after R-Wave-2) | RIA architecture |

**R-Wave-2** corresponds to the work this directive triggers and is expected to span 2026-05-04 → 2026-05-18 (two calendar weeks; pace dictated by team capacity).

### 14.2 Backwards compatibility

- **v1.1 of the three L1 docs is in-place edit (not new file)** per `ria-quality-requirements-v1.md` §10. Header bumps to "v1.1" and "Last updated: 2026-05-04". Backwards-compatible additions only.
- **v1's `ria-architecture-v1.md` stays live in the repo** until R-Wave-4. Cross-references in unchanged code may continue to point to v1 sections; new code references this v2 document.
- **`tests/_stubs/agent_server_stub_v1.py` retained**, tagged "do not extend; use `real_agent_server` fixture for new tests".
- **No code-level breaking changes** are introduced in this wave: existing `ria/` modules continue to function. New work conforms to v2 patterns; touched-but-not-rewritten code may continue to use v1 patterns until the next time it is meaningfully edited.

### 14.3 Deprecation timeline

| Item | Deprecated in | Removed in |
|---|---|---|
| `tests/integration/_stubs/agent_server_stub.py` (original location) | R-Wave-2 (move to `tests/_stubs/`) | R-Wave-4 |
| Stub usage under `tests/integration/` marker | R-Wave-2 | R-Wave-3 (CI gate G-RIA-20 enforces) |
| v1 architecture document as "current" reference | R-Wave-2 | R-Wave-4 |
| Direct `httpx` import outside two seams | R-Wave-2 | R-Wave-3 (CI gate G-RIA-19 enforces) |

### 14.4 Risk-managed rollback

If R-RIA-9 enforcement uncovers untenable existing dependencies (e.g., `ria/observability/` already directly imports `prometheus_client.push_to_gateway`), the path is:

1. Add the import to the permitted-exception list in §13 with `# r-ria-9-exception: <reason>` annotation.
2. Document the exception in this v2's §13 "Permitted exceptions" subsection.
3. Update `scripts/check_external_services_seam.py`'s exception table.

R-RIA-9 is **not** rolled back by removing the rule; it is refined by adding precisely-specified exceptions.

---

## 15. Open Questions (v2)

| Question | Tentative resolution | When to revisit |
|---|---|---|
| Does `external_services/` need a `RealKernelBackend`-style separation internally (clients × adapters)? | No for v2 — each client is small enough; a uniform-cassette policy is sufficient. Revisit if any single client exceeds 500 LOC. | R-Wave-3 retrospective |
| Should `red_status.json` be served over HTTP (`GET /ria/red-status`) for ops monitoring, in addition to file emission? | Yes (added to §7 readiness endpoints). Implementation in observability. | R-Wave-2 |
| What is the cassette-refresh cadence for `tests/conformance/` against live external services? | Weekly for arxiv / semantic scholar; monthly for low-churn (DOI, Lean). Implemented as a scheduled CI job; not part of every commit. | R-Wave-3 |
| How does `lean_library/` handle the `lean` binary version drift? | `lean_runner.py` records `lean --version` at every invocation; verifications are pinned to a Lean major.minor; mismatched binary fails with `LeanVersionMismatch` typed error. | R-Wave-3 |
| Should evolution-engine's cross-project skill delta be persisted in RIA's SQLite or in platform's KG? | RIA's SQLite for v2 — independence from platform KG availability. Migrate to platform KG if and when F.4 closes and KG cross-project query is exposed. | R-Wave-3 |
| Should `ria/api/http/` mirror hi-agent's `agent_server/runtime/` second-seam pattern internally (route handlers vs runtime binding)? | No for v2 — RIA `ria/api/http/` directly invokes `ria/orchestration/` without an internal seam; the structural complexity is not justified at RIA's current scale. Revisit if `api/http/` exceeds 1000 LOC. | R-Wave-3 retrospective |

---

**End of L0 Architecture v2.**
