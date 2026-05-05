# hi-agent Wave 34 Acceptance + Wave 35 Endorsement + Wave 36 Forward Expectations

**Date:** 2026-05-05
**From:** Research Intelligence Application (RIA) team — downstream platform consumer
**To:** hi-agent upstream engineering team
**Status:** Acceptance directive (M1 — internally reviewed; W34 acceptance is binding; W35 endorsement is informational; W36 forward expectations are pre-binding for the W36 entry directive RIA will issue at W35 close)
**Position:** Successor to `hi-agent-wave34-engineering-expectations-2026-05-04.md`. Closes W34 acceptance and stages our position on the W35 plan and W36 forward work.

**Companion documents on the RIA side (informational, not binding on you):**
- `docs/ria/ria-architecture-v2.md` (refreshed to v2.0.1 this wave)
- `docs/ria/ria-domain-model-v1.md` (v1.1)
- `docs/ria/ria-platform-contract-mapping-v1.md` (v1.1; §2 status rows updated this wave)
- `docs/ria/ria-quality-requirements-v1.md` (v1.1; §13 red-status mapping updated this wave)

---

## 0. Standing on Wave 34

We have read your Wave 34 delivery notice (`docs/downstream-responses/2026-05-05-w34-delivery-notice.md`, manifest `2026-05-05-77222f8b`, HEAD `77222f8b`) and your Wave 35 plan (`docs/superpowers/plans/2026-05-05-wave-35-systematic-audit-followups.md`).

### 0.1 Wave 34 — full acceptance

All twelve W34 acceptance IDs from `hi-agent-wave34-engineering-expectations-2026-05-04.md` §6 are **CLOSED** at HEAD `77222f8b` against measured / real / derived evidence. Per RIA §8 reporting format, we cross-checked each row of your closure-evidence table:

| Acceptance ID | Status | Evidence we cross-checked | Provenance |
|---|---|---|---|
| W34-F.2 (B-W34-1: lineage population) | **ACCEPTED** | `tests/unit/test_run_execution_context_lineage_population.py` (9 tests) + `scripts/check_lineage_population.py` exit 0 + `from_managed_run` populated at `hi_agent/context/run_execution_context.py:71-104` + `create_run` mints `attempt_id` at `hi_agent/server/run_manager.py:496-540` | measured |
| W34-F.3 (B-W34-2: ReasoningTrace spine validation) | **ACCEPTED** | `tests/unit/test_reasoning_trace_spine_validation.py` (10 tests) + `scripts/check_dataclass_spine_validation.py` exit 0 + `SpineCompletenessError` raised research/prod at `hi_agent/contracts/reasoning.py:55-110` | measured |
| W34-F.4 (B-W34-3: KnowledgeWiki tenant partition) | **ACCEPTED** | `tests/integration/test_knowledge_wiki_tenant_partition.py` (30 tests; 6 cross-tenant cases × 3 postures + 6 posture-behaviour + 2 persistence) + `scripts/check_no_unscoped_knowledge_reads.py` exit 0 + per-tenant directory layout at `hi_agent/knowledge/wiki.py:55-90` | measured |
| W34-T-FOLLOWUP (B-W34-4: 4-registry status) | **ACCEPTED** | `docs/governance/registry-tenant-scoping-audit-2026-05-04.md` per-registry status table; SkillRegistry schema-layer carry to W35 acknowledged with existing xfail `expiry_wave="Wave 35"` | derived |
| W34-MANIFEST (B-W34-5: posture field) | **ACCEPTED** | `agent_server/contracts/manifest.py::ManifestResponse` frozen `posture: PostureLiteral` + 4-test integration + contract digest re-snapshot to `cc55145f` (V1_FROZEN_HEAD) — RIA R-RIA-6 binding | measured |
| W34-IDEMPOTENCY (B-W34-6: cross-process replay) | **ACCEPTED** | `agent_server/contracts/idempotency.py` documents Cache Scope / Cross-Process Replay / TTL / Body-Mismatch + cross-process replay test (POSIX-only; Windows skip with documented reason) + `DEFAULT_TTL_SECONDS=86400.0`, `SCOPE='tenant'` | measured |
| W34-CONCURRENCY-METHOD (B-W34-7: methodology) | **ACCEPTED** | `docs/perf/concurrency-methodology-v1.md` (workload, measurements, hardware target, output schema, equivalence scope, limitations, W35 regression budget proposal) | derived |
| W34-CONCURRENCY-BASELINE (B-W34-7: baseline) | **ACCEPTED** | `docs/verification/c7d1054e-concurrency-N50M5.json` `provenance:real` (P50=77.5ms, P95=200.4ms, P99=216.2ms, 50/50, fairness=1.44) + `docs/verification/c7d1054e-concurrency-N10M1.json` (P50=28.0ms, P95=51.8ms, 10/10, fairness=1.00) + `scripts/check_concurrency_evidence.py` exit 0 | real |
| W34-CONCURRENCY-EQUIV (B-W34-7: persistence equivalence) | **ACCEPTED** | `tests/integration/test_concurrency_persistence_swap.py` SQLite leg PASS (deterministic terminal-state distribution at N=10 M=1) + PostgreSQL leg gated on `HI_AGENT_TEST_POSTGRES_DSN` SKIP — acceptable per RIA §10.1 N/M flexibility | measured |
| W34-NAMING-CLOSE (H-3' / H-13' / H-14') | **ACCEPTED** | `docs/governance/package-consolidation-2026-05-04.md`: H-3' close (deletion of `hi_agent/experiment/`) + H-13' formal decline with import-site asymmetry rationale + H-14' close-as-no-op | measured / derived |
| W34-CONFIG-ENV-AUDIT | **ACCEPTED** | `docs/governance/env-var-audit-2026-05-04.md` (35 unique vars × 64 read sites classified) + `scripts/check_env_var_routing.py` enforces 4 most-policy-sensitive vars | measured |
| W34-LINUX-SOAK-ROADMAP | **ACCEPTED (advisory)** | one paragraph naming W36 6h Linux soak (`ubuntu-latest` 4 vCPU/16GB) at N=50/M=5 with 30s chaos cadence, paired with proposed `soak_evidence_not_real` cap retirement | advisory |

The Real T3 (Volces) at HEAD `8d75aff5` is `provenance:real`, 3/3 PASS, `llm_fallback_count=0` (Rule 8 step 3); arch-7×24 fresh evidence at HEAD `8556243` 5/5 PASS; clean-env evidence 9275 passed / 8 skipped / 0 failed. We accept these as the binding ship-gate evidence at W34 close.

**Three-part defect closure (Rule 15) was honoured for every BLOCKER.** We confirm the `verified_at_release_head` closure level on B-W34-1 / B-W34-2 / B-W34-3 / B-W34-5 / B-W34-6 / B-W34-7 and `documented` level on the decline portion of B-W34-T-FOLLOWUP.

### 0.2 Quality of the W34 work

Wave 34 is the strongest single-wave delivery we have audited. Three particular qualities deserve naming:

1. **Three-part closure was applied uniformly.** Each of the seven BLOCKER closures lists (a) the code fix with file:line, (b) the recurrence-prevention check with gate-script name, (c) the process change with the document section that records it. No closure was claimed without all three parts present. This is the discipline our W34 directive Engineering Discipline 1.3 asked for, and it lands.

2. **The W34 plan accepted all seven BLOCKERs as binding without rebadging.** The W34 plan at `docs/superpowers/plans/2026-05-04-wave-34-ria-engineering-expectations.md` §0 explicitly states "ACCEPT ALL seven BLOCKERs + four governance items + advisory item (twelve total acceptance IDs). No pushback proposed; RIA's §10 positions are accepted as stated." This is the right disposition shape — disagreement with our framing should have surfaced in the plan, not in delivery; absence of pushback there means the delivery was scoped correctly from the start.

3. **The W34-close systematic audit dispatched 6 parallel audit agents.** Per the W35 plan's preamble: "6 parallel audit agents dispatched at W34 close (tenant isolation beyond 4 registries; spine completeness across all dataclasses; lineage population at construction sites; idempotency middleware coverage + TTL; posture coverage; R-AS-1 layering)". This is the systematic-audit discipline we asked for in W31 and that has now matured to "self-applied at every wave close". It surfaced 30 hidden findings beyond the W34 BLOCKERs — a third closed in W34+ patch, two-thirds tracked in the W35 plan. This is exactly the "look for failures while shipping" discipline a mature platform team practices.

### 0.3 Cap factors — unchanged, correctly held

`verified_readiness=75.0` is held by `soak_evidence_not_real` (waived per RIA's W32 acceptance §2 architectural-feasibility 7×24 criterion) and `evidence_provenance` (3 historical W27 artifacts; W28 erratum). We accept both cap factors as correctly measured at the W34 HEAD `77222f8b`.

**RIA's positioning on the soak cap — reaffirmed at W35 close.** Our positioning of the platform's 7×24 capability is "**architectural feasibility**, not measured capacity". The user's exact framing on 2026-05-05:

> 长程工作（如架构约束下具备进行7\*24小时工作的能力，**而不是单独的工程实现**，**我们只关注是否具备可行性而不关注具体能力**）

Translation: "long-running work (such as the capability to do 7×24 work under architectural constraints, **not a standalone engineering implementation**; **we only care about whether it is feasible, not specific capability**)".

This is the position. The architectural 5-assertion check (`scripts/run_arch_7x24.py`) at 5/5 PASS satisfies it. The `soak_evidence_not_real` cap **correctly** persists because measured soak is *not* what we are asking for — and the cap's persistence makes that visible. We are not requesting cap retirement in W36 either; we are requesting the W36 6h Linux soak so that *if* the soak measurement happens to confirm architectural feasibility, the cap *can* be retired. The retirement is downstream of measurement, not a goal in itself.

This means W36 acceptance does not turn on whether the 6h soak succeeds. W36 acceptance turns on whether the soak runs as planned and whether its outcome is reported with provenance. A soak that surfaces a real architectural defect is a successful W36 deliverable; a soak that runs cleanly is also a successful W36 deliverable. We do **not** want the soak to be tuned for cap retirement — that would invert the discipline.

### 0.4 The two-seam pattern is now matured

We endorsed the W32–W33 two-seam pattern in our W34 directive §0. As of this directive, RIA has implemented the structurally analogous pattern on our side: `ria/external_services/` is the second seam parallel to `ria/platform_client/`, enforced by the new R-RIA-9 boundary rule (per `ria-architecture-v2.md` §13). The pattern, which originated in your W32 work, has now propagated into our codebase. This is the kind of cross-team architectural mirroring that makes downstream / upstream teams cooperatively legible to each other, and we are grateful for the design lead.

---

## 1. Engineering Discipline (Standing Reminder — Carried Forward)

These three rules are not negotiable. Each is a CLAUDE.md-level invariant. We carry them forward unchanged from the W34 directive §1.

### 1.1 No mock-based filtering as stub limitation

> When a test passes against a stub but breaks against the real component, that is a defect in the production component, not a stub limitation. The defect is fixed in the production component; the stub may then be tightened to match.

W34 honoured this rule. RIA's Phase 3 going-real (A.3.α) is now operationally viable: the W34 closures of F.2 / F.3 / F.4 / manifest / idempotency mean RIA's `tests/integration/` against `agent-server serve` will not surface tests blocked by these gaps. We commit to maintaining the same rule against W35 work.

### 1.2 Naming / structure accretion is a defect

Carried forward from W31 §B-6 and W34 §1.2. W34-NAMING-CLOSE shows the pattern is now operational: H-3' closed by deletion (commit `d694541e`), H-13' closed by formal decline with concrete asymmetry rationale, H-14' closed as no-op. The W34 delivery notice §"W34-NAMING-CLOSE" closure block formally retires the "RIA discretion deferral" pattern: every naming-hygiene item must close-or-formally-decline within the receiving wave per RIA §4. We accept that retirement and treat any future W35+ naming concerns under the same rule.

### 1.3 Defect-vs-limitation discipline (three-part closure)

Honoured uniformly in W34 (per §0.2 above). Carried forward; binding for W35.

---

## 2. Cross-Layer Positioning Refresh — Eight Lenses, Post-W34

For each of the eight lenses (per W34 directive §2), we restate (a) what W34 closed, (b) what the W35 plan addresses, (c) what we expect in W36.

---

### 2.1 Tenant Isolation (Lens 1)

**W34 closed.**
- F.4 KnowledgeWiki tenant partition (W34-F.4): per-tenant directory layout + posture-aware `__post_init__` on `WikiPage.tenant_id` + 30 integration tests + recurrence gate.
- B-5 follow-through audit (W34-T-FOLLOWUP): the four W31-named registries (KG, Skill, Tool, Capability) + RunQueue + KnowledgeWiki are each in a documented disposition (CLOSED at HEAD, or TENANT-AGNOSTIC by design with rationale, or W35 carryover with `expiry_wave`). RIA accepts this as a complete answer.

**W35 addresses.**
- W35-T1 (frozen-contract spine validation): 13 contract dataclasses across `agent_server/contracts/{run,tenancy,skill,memory,streaming,llm_proxy}.py` carry `tenant_id` but lack `__post_init__`. **RIA priority signal: HIGH** (see §3 below) — these dataclasses are the surface RIA's `platform_client/` constructs from platform responses; without spine validation, malformed responses pass silently. The W34-F.3 closure was `ReasoningTrace` only; W35-T1 extends the same pattern across the contract surface. We endorse the W35 plan's "single batched commit + one re-snapshot" approach to minimise digest churn.
- SkillRegistry schema-layer (W34 carryover, tracked via existing xfail `expiry_wave="Wave 35"`): API-layer is closed; schema-layer closure in W35 completes the structural defense.

**W36 forward expectations (pre-binding).**
- All 13 contract dataclasses from W35-T1 closed against measured evidence.
- SkillRegistry schema-layer xfail flips to PASS.
- New CI gate `scripts/check_dataclass_spine_validation.py::REQUIRED_VALIDATION_TARGETS` extended to cover all 13 + ReasoningTrace + WikiPage + the spine-bearing kernel dataclasses.

---

### 2.2 Functional Idempotency (Lens 2)

**W34 closed.**
- W34-IDEMPOTENCY: `agent_server/contracts/idempotency.py` documents Cache Scope (per-tenant) / Cross-Process Replay / TTL (`DEFAULT_TTL_SECONDS=86400.0`) / Body-Mismatch (409). Cross-process replay test exists (POSIX-only; documented Windows skip). Recurrence gate `scripts/check_idempotency_contract_documented.py` enforces docstring sub-headers.

**W35 addresses.**
- W35-T4 (Idempotency TTL purge): records accumulate indefinitely without a purge task; SQLite database grows unbounded. **RIA priority signal: HIGH — this is feasibility-blocking for Lens 7 (7×24)**, see §3 below.
- W35-T5 (Idempotency body hash hardening — Float canonicalization): deferred with a documented plan; we accept the deferral disposition because the fix is a breaking change requiring tenant-coordinated migration. The W35 plan's "document the float-canonicalization plan in `agent_server/contracts/idempotency.py` Limitations section" is the right shape.
- W35-T6 (Idempotency observability): 4 Prometheus metrics on cache age / replay rate / conflict rate / purged count. RIA endorses; these are necessary for ops visibility on the long-running system.
- W35-T8 (MCP route idempotency coverage): boot-time assertion that `include_mcp_tools=True` implies `idempotency_facade is not None`. RIA endorses.

**W36 forward expectations.**
- W35-T4 closed (background purge task in `agent_server/runtime/lifespan.py` + `IdempotencyStore.purge_expired` + tenant-scoped purge counter + disk-growth regression test).
- W35-T6 metrics live and emitting.
- W35-T8 boot-time assertion live; MCP route idempotency test PASS.
- W35-T5 float-canonicalization plan published with migration window date.

---

### 2.3 High Reliability (Lens 3)

**W34 closed.**
- W34-F.2 (RunExecutionContext lineage population): `from_managed_run` reads lineage from `ManagedRun` spine; `create_run` mints `attempt_id` (uuid4) and threads through `ManagedRun` + `RunExecutionContext` + `RunRecord`. Recurrence gate `scripts/check_lineage_population.py` AST-walks construction sites; root-runs annotated `# scope: root-run` are exempt for `parent_run_id` only.
- W34-F.3 (ReasoningTrace.__post_init__): `SpineCompletenessError` raised under research/prod on missing spine fields; warning under dev posture.

**W35 addresses.**
- W35-T1 (frozen-contract spine validation): extends the F.3 pattern to the 13 contract dataclasses. **RIA priority signal: HIGH**, §3.
- W35-T2 (WEAK_PARITY posture sites × 8): research/prod raises; dev branch missing or identical. **RIA priority signal: MEDIUM** (RIA depends on posture parity being symmetric — dev-permissive vs research-strict — for the R-RIA-6 startup compatibility check to be reliable).

**W36 forward expectations.**
- W35-T1 + W35-T2 closed.
- New ARCHITECTURE.md §"Spine completeness" extended (currently W34-only) to cover the contract surface, posture parity, and audit cadence.

---

### 2.4 High Concurrency (Lens 4)

**W34 closed.**
- Methodology document (`docs/perf/concurrency-methodology-v1.md`): workload, measurements, hardware target (GitHub Actions `ubuntu-latest`: 4 vCPU, 16 GB RAM, SSD), output schema, equivalence scope, limitations, W35 regression budget proposal.
- Baselines: N=50/M=5 → P50=77.5ms, P95=200.4ms, P99=216.2ms, 50/50 success, fairness=1.44; N=10/M=1 → P50=28.0ms, P95=51.8ms, fairness=1.00. Both `provenance:real`.
- Persistence equivalence: SQLite leg PASS at N=10/M=1; PostgreSQL leg gated on `HI_AGENT_TEST_POSTGRES_DSN` SKIP (accepted per W34 §10.1 N/M flexibility).

**RIA's read on the baselines.** P50=77.5ms / P95=200.4ms at N=50/M=5 is a usable baseline for sizing RIA's `ria/api/http/` burst handling and `ria/user/budget.py` per-user rate-limit defaults. The fairness coefficient 1.44 is the metric we will track wave-over-wave; values approaching 1.00 (full fairness) are the regression target. We commit to citing your baselines in our `ria-platform-contract-mapping-v1.md` v1.2 §3 (forthcoming) so that consumers of RIA know the platform's measured concurrency floor.

**W35 plan / W36 forward expectations.**
- W35: regression-budget enforcement (per the methodology document §9). When W35 ships, the wave's concurrency JSON must be within +X% of W34's; the budget multiplier `X` is set by your team.
- W36: PostgreSQL leg PASS (with `HI_AGENT_TEST_POSTGRES_DSN` configured in CI) — closes the persistence-equivalence gap.
- W36: target N raised toward N=100/M=10 if CI runner stability allows; this is the "raise to N=100/M=10 once CI runner stability confirmed" item the methodology document already names. Not a new request.

---

### 2.5 Configurable Development (Lens 5)

**W34 closed.**
- W34-CONFIG-ENV-AUDIT: 35 unique env vars × 64 read sites classified in `docs/governance/env-var-audit-2026-05-04.md`. `scripts/check_env_var_routing.py` enforces per-variable allowlist for the 4 most policy-sensitive vars (`HI_AGENT_POSTURE`, `HI_AGENT_LLM_MODE`, `HI_AGENT_JWT_SECRET`, `AGENT_SERVER_BACKEND`). Zero direct-read defects at HEAD.
- The W33-E.1 closure (`HI_AGENT_ENV` unification through `Posture.resolve_runtime_mode()`) remains intact at W34 HEAD; the audit confirms no regression.

**W35 plan.**
- W35-T7 (agent_server CONFIG layer expansion): tracked as W35 only if v2 contract work is approved; otherwise W36. RIA does not request v2 contract work in W35 (per W34 §7 out-of-scope), so we accept the W35-T7 deferral disposition.

**W36 forward expectations.**
- W35-T7 disposition resolved (deferred to W37+ if v2 not yet planned; addressed in W36 if v2 work is staged).
- The 4-variable allowlist in `scripts/check_env_var_routing.py` reviewed for completeness — if any new policy-sensitive var lands in W35, it is added to the allowlist within the wave that introduces it.

---

### 2.6 Continuous Intelligence Evolution (Lens 6)

**W34 closed transitively.**
- W34-F.2 + W34-F.3 close the postmortem-reconstruction gap: lineage chains are now populated and validated; cross-attempt reconstruction is correct.
- RIA's `evolution_engine/postmortem.py` (Phase 3, going real per A.3.α) can now produce `Postmortem` records (`ria-domain-model-v1.md` v1.1 §3.14) with non-empty `parent_run_id` / `attempt_id` / `phase_id`.

**W35 addresses (via L1 + L3 transitively).**
- W35-T1 (contract spine validation) extends the spine-completeness property to the contract surface, which means RIA's reads of run/event/skill records via `platform_client/` now have structural validation at construction time.

**W36 forward expectations.**
- Champion-Challenger versioning observability through `/v1/skills/{id}/versions` (the route shape was named in our W34 directive §2.6 as a future need; we are not asking for it in W35 — we ask now to track it for W36+ scoping).
- Cross-project skill-delta read shape (RIA's `evolution_engine/skill_delta.py` consumes this via `platform_client.list_skill_versions`, currently EXPECTED in our `ria-platform-contract-mapping-v1.md` v1.1 §2). Track for W36+.

---

### 2.7 Long-Running 7×24 (Lens 7) — Reaffirmed Position

**Position (verbatim from RIA at 2026-05-05):**

> "我们只关注是否具备可行性而不关注具体能力" — "we only care about whether it is feasible, not specific capability".

**What this means operationally.**

| What RIA wants | What RIA does NOT want |
|---|---|
| Architectural feasibility — primitives wired into default path (lifespan reforms, SIGTERM drain, RunQueue.reenqueue, lease semantics, idempotency replay across restart, lineage chain reconstructible across recovery) | A specific measured soak duration as a capability claim |
| `arch-7x24` 5/5 PASS as the structural indicator | A specific RSS/CPU envelope as a SLA |
| `soak_evidence_not_real` cap **persisting correctly** to make the architectural-feasibility-only stance visible | The cap retired without measured soak |
| W36 6h Linux soak as a *measurement* opportunity (not a *capability claim*) | The W36 soak tuned for cap retirement |

**W34 closure relevant to this lens.**
- Five W34 closures directly improve architectural feasibility under the "feasibility-only" frame:
  - W33-C.1 lifespan reforms reaching production (continuity across deployment shapes)
  - W33-C.2 SIGTERM graceful drain (continuity across operator-initiated restart)
  - W33-C.3 RunQueue.reenqueue clears `adoption_token` (continuity across recovery cycles)
  - W34-F.2 lineage population (continuity of attribution across recovery)
  - W34-IDEMPOTENCY cross-process replay (continuity of in-flight requests across kernel restart)
- All five are **architectural-feasibility primitives wired into the default path**, which is exactly what "feasibility, not capacity" asks for.

**W35-T4 — feasibility-blocking on this lens.**

The idempotency-store TTL is `DEFAULT_TTL_SECONDS=86400.0` (24 hours), but W35-T4 names that the store does not actually purge expired records. The records accumulate indefinitely; SQLite grows unbounded. **This is a feasibility defect by RIA's standard** — under the "feasibility-only" frame, an unbounded-growth store is exactly the failure mode that says "this system architecturally cannot run continuously". We do not need a 4-hour soak to confirm it; the architectural inspection of the storage path confirms it. **W35-T4 is therefore RIA priority HIGH**, see §3 below.

**W34-LINUX-SOAK-ROADMAP — accepted as advisory.**

The W36 plan: 6h soak on `ubuntu-latest` (4 vCPU / 16 GB RAM) at N=50/M=5 with 30s chaos cadence, paired with proposed `soak_evidence_not_real` cap retirement. We accept the roadmap. We also reaffirm:

- The cap retirement is **not** a goal of the soak. The soak measures feasibility; the cap reflects what the soak measured.
- A 6h soak that finishes cleanly and a 6h soak that surfaces an architectural defect are **both** successful W36 deliverables — they each return information to the architectural-feasibility ledger. Cap disposition is whatever the measured outcome justifies.
- We do not request a duration extension, a workload increase, or a chaos-cadence increase. The W36 plan as stated is the right plan.

---

### 2.8 Agent Service to Upper Systems (Lens 8)

**W34 closed.**
- W34-MANIFEST: `agent_server/contracts/manifest.py::ManifestResponse` is a frozen dataclass with `posture: PostureLiteral`. Contract digest re-snapshot to `cc55145f` (V1_FROZEN_HEAD). RIA's R-RIA-6 startup compatibility check has its frozen contract surface.

**W35 addresses.**
- W35-T1 (frozen-contract spine validation across 13 dataclasses) extends the contract surface's structural integrity. RIA's `platform_client/` constructs objects from these contract shapes; spine validation makes silent-empty-field acceptance impossible.

**W36 forward expectations.**
- W35-T1 closed across all 13 dataclasses; CI gate updated.
- Phase 3 read routes (`list_recent_runs`, `get_run_history_by_skill`, `list_skill_versions`, `query_kg_cross_project`) — currently `EXPECTED` in `ria-platform-contract-mapping-v1.md` v1.1 §2 — staged for W36 or later. RIA will issue a separate routes-extension directive at W35 close to scope this work; the routes are not part of W35 acceptance.

---

## 3. RIA Priority Signals on the W35 Plan

The W35 plan publishes 8 carryover items (T1 through T8) with acceptance criteria. We endorse all 8. Three deserve **explicit RIA priority signal** because they intersect our 8-lens positioning at structural points:

### 3.1 W35-T1 — Frozen-Contract Spine Validation (RIA priority: HIGH)

**Why HIGH.** The 13 contract dataclasses are RIA's **primary contract surface** to the platform. RIA's `platform_client/transport_http.py` parses platform responses into these dataclass shapes. Without `__post_init__` raising on empty spine fields under research/prod posture, the construction of a malformed object passes silently in our process, and the resulting bug surfaces only at the point of *use* — typically in `ria/global_layer/evolution_engine/postmortem.py` or `ria/global_layer/paper_archive/curate.py` — where the empty `tenant_id` or empty `parent_run_id` produces an incorrect cross-tenant query or an incorrect attempt-tree edge. The construction-site validation is the structural safety net that catches the malformation at the seam.

The W34-F.3 closure validated `ReasoningTrace` only; W35-T1 extends to the full contract surface. RIA's `tests/integration/` expects this property; until W35 closes T1, RIA tests against contract dataclasses lacking spine validation must use defensive checks at the call site. We do **not** add those defensive checks (per AP-9 — defense-in-depth shims that mask platform gaps are forbidden); we let the bug surface and treat it as a W35-T1 closure dependency. Red-status JSON's `blocked_by_wave_id: "W35-T1"` mapping is in place (per `ria-quality-requirements-v1.md` v1.1 §13.3, updated this wave).

**RIA-side test that surfaces the gap:** `tests/conformance/test_contract_dataclass_spine_validation.py` (RIA-side; will probe each of the 13 dataclasses by constructing instances from platform responses and asserting that empty-spine inputs raise under research/prod). This test is currently RED at `ce9330fa` and unchanged at `77222f8b` (W34 head), since W34-F.3 covered ReasoningTrace only.

**RIA's expectation for W35 closure:**
- All 13 dataclasses acquire posture-aware `__post_init__`.
- `scripts/check_dataclass_spine_validation.py::REQUIRED_VALIDATION_TARGETS` extended to cover all 13.
- Contract digest re-snapshot recorded in W35 delivery notice.
- RIA's `tests/conformance/test_contract_dataclass_spine_validation.py` flips to GREEN.

### 3.2 W35-T3 — INVERTED Posture in `run_manager.py:418-432` (RIA priority: HIGH)

**Why HIGH.** Per the W35 plan §"W35-T3": "strict posture issues `DeprecationWarning` and accepts middleware tenant_id when body tenant_id is missing; dev posture has no equivalent fallback. Strict is *more permissive* than dev." This is a **Rule 11 reversal** — strict posture is supposed to be the fail-closed posture. Inversion makes RIA's R-RIA-6 startup compatibility check unsound: RIA expects platform `research` / `prod` to be fail-closed; if strict is more permissive than dev for some sites, the compatibility-check guarantee leaks.

This is not a new bug — the W35 plan flags it as found in audit E (audit of posture coverage). It has likely existed for several waves. The fix is small (restructure to behaviour symmetry, OR remove the strict-only fallback) but the implication is large: any other INVERTED site (audited or not) carries the same kind of risk.

**RIA's expectation for W35 closure:**
- W35-T3 closed: behaviour symmetry (same fallback under both postures, OR strict raises and dev raises).
- `tests/posture/test_run_manager_body_tenant_id_fallback.py` covering both directions (research and dev) — symmetrical assertion.
- Audit of any other INVERTED site: explicit confirmation in W35 delivery notice that the audit-E run found *only* this site (or, if more found, each is included in W35-T3 closure scope).
- Three-part closure (Rule 15).

### 3.3 W35-T4 — Idempotency TTL Purge (RIA priority: HIGH)

**Why HIGH — feasibility-blocking on Lens 7.** Per the W35 plan §"W35-T4": "`IdempotencyStore.expires_at` is stored but never queried for cleanup. Records accumulate indefinitely; SQLite database grows unbounded."

**Per RIA's reaffirmed 7×24 framing (§2.7 above):** an unbounded-growth store is exactly the architectural defect that "feasibility, not capacity" is meant to surface. We do **not** need a 4-hour soak to confirm that an unbounded store eventually exhausts disk; the architectural inspection confirms it. This means **W35-T4 is feasibility-blocking on Lens 7** — without it, the platform's 7×24 architectural feasibility claim has a structural counter-example.

The W35 plan's architecture proposal is the right shape:
1. Background asyncio task in `agent_server/runtime/lifespan.py` running every N minutes.
2. `IdempotencyStore.purge_expired(now=...) -> int` returns count of deleted rows.
3. New Prometheus counter `hi_agent_idempotency_purged_total{tenant_id}`.
4. Lazy-purge fallback in `reserve_or_replay` (delete-then-insert if expired record found).

We endorse all four bullets. Particular care on bullet 1 — the background task must respect SIGTERM graceful drain (W33-C.2) and must not race with `IdempotencyMiddleware` reads.

**RIA's expectation for W35 closure:**
- All four bullets implemented.
- `tests/integration/test_idempotency_ttl_purge.py` exercising both lazy and proactive purge.
- Disk-growth regression test: insert 10,000 records, run purge, assert byte size shrinks (per the W35 plan acceptance criteria).
- Three-part closure (Rule 15).

### 3.4 W35 plan items not flagged as priority

T2 (WEAK_PARITY × 8 sites) — RIA priority MEDIUM. Important but per-site; the W35 plan's per-site closure is the right shape.

T5 (Float canonicalization) — RIA priority LOW for W35; the deferral with documented plan is correct given the breaking-change implication. RIA expects the plan to name a concrete deprecation window in W36.

T6 (Idempotency observability) — RIA priority MEDIUM. Important for ops visibility on the long-running platform. We endorse the 4-metric proposal.

T7 (CONFIG layer expansion) — RIA priority LOW; correctly deferred unless v2 work is staged.

T8 (MCP route idempotency coverage) — RIA priority MEDIUM. Boot-time assertion is the correct mechanism. We do not currently use the MCP route via `platform_client/transport_mcp.py`, but we expect to in a future Phase.

---

## 4. Wave 36 Forward Expectations (Pre-Binding)

These are RIA's pre-binding W36 forward expectations. We will issue a binding W36 directive at W35 close. The list below is the input to that directive, *not* the directive itself — it gives the hi-agent team advance notice of likely W36 entry items so planning can begin.

### 4.1 Carryover from W35 plan

| Pre-binding item | W35 plan reference | Binding form expected at W36 entry |
|---|---|---|
| All 8 W35-T items closed | W35 plan §0 disposition | "W35 closure verified" entry in W36 directive |
| W35-T5 float-canonicalization plan named with concrete deprecation window | W35-T5 acceptance criterion | W36 directive will require the deprecation window be specified |

### 4.2 6h Linux soak (W34-LINUX-SOAK-ROADMAP delivery)

| Pre-binding item | Source | Binding form |
|---|---|---|
| 6h Linux soak runs on `ubuntu-latest` 4 vCPU / 16 GB RAM at N=50/M=5 with 30s chaos cadence | W34 delivery §"Linux-runner soak roadmap" | W36 directive will require: soak run with `provenance: real`; outcome reported regardless of cap-disposition implication; `arch-7x24` re-run at the soak HEAD |
| `soak_evidence_not_real` cap disposition reflects the soak's measured outcome | RIA §2.7 reaffirmation; W34-LINUX-SOAK-ROADMAP | The cap stays, retires, or reframes — driven by the soak data, not by a cap-target |
| 2 OS-limited chaos scenarios (`signal_storm`, `fd_exhaustion_recovery`) participate in the soak | W34 delivery §"Linux-runner soak roadmap" | Both scenarios provenance moves from `runtime_partial` to `real` |

### 4.3 SkillRegistry schema-layer closure

| Pre-binding item | Source | Binding form |
|---|---|---|
| SkillRegistry schema-layer `tenant_id NOT NULL` enforcement at HEAD | W34 §"W31 §B-5 follow-through" + existing xfail `expiry_wave="Wave 35"` | W36 directive will require the xfail flip to PASS (W35 work) or, if delayed past W35, will escalate to BLOCKER |

### 4.4 Phase 3 read routes (RIA's evolution-engine + global-layer needs)

| Pre-binding item | Source | Binding form |
|---|---|---|
| `GET /v1/skills/{skill_id}/versions` (Champion-Challenger surfacing) | W34 directive §2.6 + RIA `ria-platform-contract-mapping-v1.md` §2 | W36 directive *may* require depending on RIA Phase 3 progress; not committed at this directive |
| `GET /v1/runs?since=...&limit=N` (cross-time-range listing) | W34 directive §2.6 + same §2 | same |
| `GET /v1/skills/{skill_id}/runs?since=...` (run history by skill) | same | same |
| `GET /v1/kg/query?tenant_id=...&q=...` (cross-project KG read; depends on F.4 closure ✓) | same | same |

We are **not** asking for these routes in W35 or W36. We are surfacing them as known future requirements; RIA will issue a separate routes-extension directive when our `external_services/` and `global_layer/` implementations are far enough along to know the exact shape we need.

---

## 5. RIA-Side Forcing Function Update (red-status mapping refresh)

Per `ria-quality-requirements-v1.md` v1.1 §13 and `ria-architecture-v2.md` §5.6, RIA emits `docs/ria/red-status/<head>.json` on every commit. The mapping yaml at `tests/_blocked_by_platform.yaml` is **updated this wave** to reflect the W34 → W35 transition:

### 5.1 Retired entries (W34 closures)

The following entries are **removed** from `tests/_blocked_by_platform.yaml` because the underlying platform gaps are closed at HEAD `77222f8b`:

```yaml
# RETIRED 2026-05-05 — closed at hi-agent W34 HEAD 77222f8b
# - test_glob: "tests/integration/test_evolution_engine_*"
#   blocked_by_w34_id: "B-W34-1"   (W34-F.2; closed)
# - test_glob: "tests/integration/test_*_spine_validation.py"
#   blocked_by_w34_id: "B-W34-2"   (W34-F.3; closed)
# - test_glob: "tests/integration/test_knowledge_*_tenant_partition.py"
#   blocked_by_w34_id: "B-W34-3"   (W34-F.4; closed)
# - test_glob: "tests/conformance/test_cross_tenant_isolation_*"
#   blocked_by_w34_id: "B-W34-4"   (W34-T-FOLLOWUP; closed)
# - test_glob: "tests/integration/test_manifest_*"
#   blocked_by_w34_id: "B-W34-5"   (W34-MANIFEST; closed)
# - test_glob: "tests/integration/test_idempotency_cross_process_*"
#   blocked_by_w34_id: "B-W34-6"   (W34-IDEMPOTENCY; closed)
# - test_glob: "tests/integration/test_concurrency_*"
#   blocked_by_w34_id: "B-W34-7"   (W34-CONCURRENCY-*; closed)
```

The retired entries remain as comments for historical traceability; the JSON schema's `blocked_by_wave_id` (renamed from `blocked_by_w34_id`) replaces `blocked_by_w34_id` going forward.

### 5.2 Added entries (W35 carryovers)

```yaml
# ADDED 2026-05-05 — W35 plan items intersecting RIA 8-lens positioning
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
  blocked_by_wave_id: "W35-T1"   # via SkillRegistry schema-layer carryover
  blocked_by_short: "SkillRegistry schema-layer tenant_id enforcement (W34 carryover via xfail expiry_wave=Wave 35)"
```

### 5.3 Schema field rename

The red-status JSON field `blocked_by_w34_id` is renamed to `blocked_by_wave_id` (W34-agnostic). Backwards compatibility: the producer emits both fields for at least 2 RIA waves (R-Wave-3 and R-Wave-4); R-Wave-5 retires `blocked_by_w34_id`. This is documented in `ria-quality-requirements-v1.md` v1.1 §13.7 promotion path and `ria-architecture-v2.md` §5.6.

### 5.4 Forcing-function continues operating

The red-status JSON is now operational for the W35 cycle. RIA's CI emits the JSON at every commit; consumers (hi-agent W35+ planning, RIA backlog grooming, ops dashboard) can ingest it as a CI signal. We continue to commit to this artifact per the W34 directive §5.3.

---

## 6. Wave 35 Acceptance Criteria (CI-Verifiable, Endorsed)

The W35 plan §0 names eight carryover items with acceptance criteria. RIA endorses the W35 plan's own acceptance criteria as binding. We **do not** introduce additional acceptance criteria beyond what the W35 plan already specifies, *except* the three RIA priority signals (W35-T1, W35-T3, W35-T4) which carry **HIGH** designation in the W35 delivery notice.

The endorsed acceptance set:

| W35 ID | Acceptance criterion (per W35 plan) | RIA designation |
|---|---|---|
| W35-T1 | All 13 contract dataclasses acquire posture-aware `__post_init__`; `scripts/check_dataclass_spine_validation.py::REQUIRED_VALIDATION_TARGETS` extended; contract digest re-snapshot in W35 delivery notice | **HIGH (RIA priority signal §3.1)** |
| W35-T2 | Per-site: dev branch logs WARNING + falls back gracefully; research/prod branch raises with structured envelope; new test in `tests/posture/test_*.py` covering both postures | MEDIUM |
| W35-T3 | Behaviour symmetry: same fallback under both postures, OR strict raises and dev raises; `tests/posture/test_run_manager_body_tenant_id_fallback.py` covering both directions; three-part closure (Rule 15) | **HIGH (RIA priority signal §3.2)** |
| W35-T4 | Background task scheduled in lifespan startup; cancelled on shutdown; `tests/integration/test_idempotency_ttl_purge.py` exercises lazy + proactive purge; disk-growth regression test (10,000 records → purge → byte size shrinks) | **HIGH (RIA priority signal §3.3; feasibility-blocking on Lens 7)** |
| W35-T5 | Float-canonicalization plan documented in `agent_server/contracts/idempotency.py` Limitations; CI gate reports any new mutating route accepting non-string-keyed bodies | LOW |
| W35-T6 | 4 Prometheus metrics emitted by `IdempotencyMiddleware` and `IdempotencyStore`; `docs/observability/idempotency-metrics.md` documents each metric | MEDIUM |
| W35-T7 | Disposition resolved (deferred to W37+ if v2 not staged; addressed in W36 if v2 work is approved) | LOW |
| W35-T8 | Boot-time assertion in `build_app` that `include_mcp_tools=True` implies `idempotency_facade is not None`; `tests/integration/test_mcp_tools_idempotency.py` covering replay + conflict on the MCP route | MEDIUM |

**Score implications:** RIA does not request a score-cap change in W35. The 75.0 cap continues to be governed by `soak_evidence_not_real` (waived per RIA's W32 acceptance §2; reaffirmed §2.7 above) + `evidence_provenance` (W27 historicals; W28 erratum). Closing the 8 W35-T items improves the underlying readiness; whether and how that surfaces in the scorecard is hi-agent's call.

---

## 7. Out of Scope for Wave 35 (Explicitly Not Asking)

Per RIA's continuing positioning:

- **No score-cap change in W35.** The two cap factors continue to hold for the right reasons.
- **No new v1 contract routes in W35.** The four Phase 3 read routes (per §4.4 above) are tracked for a future routes-extension directive once RIA's `external_services/` and `global_layer/` implementations are far enough along to know exact shapes.
- **No platform v2 contract work in W35.** RIA pins `agent_server v1`; v2 is hi-agent planning, not RIA request.
- **No new Linux-runner chaos scenario extension beyond the 2 OS-limited.** The W36 6h Linux soak per W34-LINUX-SOAK-ROADMAP is the only Linux-runner expansion; not blocking.
- **No defense-in-depth shims on the RIA side** (per AP-9 in `ria-quality-requirements-v1.md` v1.1 §2.2). RIA does not mask W35-T1/T3/T4 with workarounds; we let them surface in red-status and close in W35.

---

## 8. Reporting Format (For Wave 35 Closure Notice)

When you close W35, the delivery notice should include the following structured section so we can verify mechanically:

```
## Wave 35 Closure Evidence

| Acceptance ID | Status | Evidence path | Provenance | RIA designation |
|---|---|---|---|---|
| W35-T1 | PASS | <path to spine-validation tests + check script + digest re-snapshot> | measured | HIGH |
| W35-T2 | PASS | <path to per-site posture tests> | measured | MEDIUM |
| W35-T3 | PASS | <path to symmetry test + three-part closure section> | measured | HIGH |
| W35-T4 | PASS | <path to ttl_purge tests + disk-growth test + lifespan task> | measured | HIGH |
| W35-T5 | PASS | <path to Limitations docstring + CI gate output> | derived | LOW |
| W35-T6 | PASS | <path to metrics emission + observability doc> | measured | MEDIUM |
| W35-T7 | NOTED or PASS | (deferral disposition or implementation evidence) | derived | LOW |
| W35-T8 | PASS | <path to boot-time assertion + MCP idempotency test> | measured | MEDIUM |
```

**Three-part defect closure documentation.** For each W35 closure designated **HIGH**, include the three-part closure summary (per Engineering Discipline 1.3):

```
### W35-T<N> closure (three-part)

(a) Code fix: <commit SHA + file:line>
(b) Recurrence-prevention check: <gate script + CI integration commit>
(c) Process change: <CLAUDE.md or ARCHITECTURE.md section + line>
```

Status `PARTIAL` is **not** an accepted W35 outcome for any T-item designated HIGH. For MEDIUM items, partial closure with named carryover is acceptable. For LOW items, deferral with rationale is acceptable.

---

## 9. Process Note — How This Directive Composes With W34

This directive is the **acceptance closure** for the W34 directive (`hi-agent-wave34-engineering-expectations-2026-05-04.md`). The W34 directive's items are now in one of three states at HEAD `77222f8b`:

- **Closed** (12 of 12 acceptance IDs): tracked in §0.1 above.
- **Continuing forward** (the eight W35-T plan items): tracked in §3 + §6 above.
- **Forward-only** (Phase 3 read routes; soak cap retirement preconditions; SkillRegistry schema-layer): tracked in §4 above.

There is no W34 item in any other state. No W34 item is rebadged, deferred without acceptance, or carried silently. The W34 directive is fully discharged as of this directive's signing.

The next directive RIA will issue is either:
- **W36 entry directive at W35 close**, if the W35 plan delivers as scoped, or
- **W35 corrective directive**, if any of the three RIA-priority-HIGH items (W35-T1, W35-T3, W35-T4) does not close at the W35 maturity bar stated in §6.

The default trajectory is the W36 entry directive.

---

## 10. Cross-References

| Document | Purpose | Status |
|---|---|---|
| `D:\chao_workspace\hi-agent\docs\downstream-responses\2026-05-05-w34-delivery-notice.md` | hi-agent W34 delivery notice (the basis we work from) | live |
| `D:\chao_workspace\hi-agent\docs\superpowers\plans\2026-05-05-wave-35-systematic-audit-followups.md` | hi-agent W35 plan | live |
| `D:\chao_workspace\hi-agent\docs\superpowers\plans\2026-05-04-wave-34-ria-engineering-expectations.md` | hi-agent's plan for W34 (their disposition response to our directive) | historical reference |
| `D:\chao_workspace\hi-agent\ARCHITECTURE.md` | hi-agent platform architecture | refreshed at W34 |
| `D:\chao_workspace\hi-agent\docs\governance\registry-tenant-scoping-audit-2026-05-04.md` | B-5 follow-through audit (W34-T-FOLLOWUP) | live |
| `D:\chao_workspace\hi-agent\docs\governance\env-var-audit-2026-05-04.md` | env-var audit (W34-CONFIG-ENV-AUDIT) | live |
| `D:\chao_workspace\hi-agent\docs\governance\package-consolidation-2026-05-04.md` | naming closure (W34-NAMING-CLOSE) | live |
| `D:\chao_workspace\hi-agent\docs\perf\concurrency-methodology-v1.md` | concurrency methodology (W34-CONCURRENCY-METHOD) | live |
| `D:\chao_workspace\research\docs\hi-agent-wave31-blocker-closure-requirements-2026-05-02.md` | W31 directive (precedent) | historical |
| `D:\chao_workspace\research\docs\hi-agent-wave34-engineering-expectations-2026-05-04.md` | W34 directive (this directive's predecessor) | now fully discharged |
| `D:\chao_workspace\research\docs\ria\ria-architecture-v2.md` | RIA L0 architecture v2 | refreshed to v2.0.1 this wave |
| `D:\chao_workspace\research\docs\ria\ria-quality-requirements-v1.md` (v1.1) | RIA quality bar | §13 mapping refreshed this wave |
| `D:\chao_workspace\research\docs\ria\ria-platform-contract-mapping-v1.md` (v1.1) | RIA → platform contract mapping | §2 status rows refreshed this wave |
| `D:\chao_workspace\research\docs\ria\ria-domain-model-v1.md` (v1.1) | RIA domain entities | unchanged this wave |
| `D:\chao_workspace\research\docs\ria\red-status\<sha>.json` | RIA's red-status forcing-function artifact | producer operational; mapping refreshed this wave |

---

## 11. Acknowledgement

The W34 delivery is exemplary work. The three-part closure discipline you applied uniformly, the systematic audit dispatching 6 parallel agents at W34 close, and the proactive publication of an 8-item W35 plan (rather than waiting for our directive to surface them) are the signals of a mature platform team. RIA's positioning of the platform — eight lenses, "feasibility not capacity" on long-running, two-seam structural mirroring — is now operationally legible to both teams, and we appreciate the design lead.

The escalations and forward expectations in this directive are **not** a comment on the quality of W34. They are the natural shape of the work that follows from W34's closures and the W35 plan's self-identified carryovers. Three of the W35 carryovers (T1, T3, T4) intersect our 8-lens positioning at structural points; we signal them HIGH because the structural intersection makes them load-bearing.

We expect renegotiation on specific acceptance criteria. We do not expect rebadging of any RIA-HIGH item as advisory; per Engineering Discipline 1.3, that is not a closure path.

---

**Signed:** RIA team
**Audit head (RIA side):** docs match RIA `main` at 2026-05-05
**Platform head under audit:** `77222f8b` (hi-agent W34, manifest `2026-05-05-77222f8b`)
**Document maturity:** M1 — internally reviewed; promotes to M2 (preprint-grade) when mirrored into hi-agent's `docs/upstream-directives/` per the conduct spec.

---

**End of Wave 34 Acceptance + Wave 35 Endorsement + Wave 36 Forward Expectations.**
