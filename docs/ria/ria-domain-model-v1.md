# RIA Domain Model — v1.1

**Document maturity:** M1 — internally reviewed
**Last updated:** 2026-05-04 (v1.1 minor revision per `ria-quality-requirements-v1.md` §10)
**Position:** L1 detail under `ria-architecture-v1.md` §5 and `ria-architecture-v2.md` §5

> **v1.1 changes vs v1.0** (additive; backwards-compatible per `ria-quality-requirements-v1.md` §10):
> - §1 overview — adds SkillDelta, Postmortem, Author entities to the schema diagram footer.
> - §3.13 (new) — `SkillDelta` dataclass for cross-project skill version diff (consumed by `evolution_engine/skill_delta.py`).
> - §3.14 (new) — `Postmortem` dataclass for RIA-side reconstructed attempt-tree summary (consumed by `evolution_engine/postmortem.py`).
> - §3.15 (new) — `Author` dataclass replacing the v1 `authors: tuple[str, ...]` flat-string field on `Paper` with a structured author entity (used by Paper Archive's citation graph).
> - §5 cross-reference map — adds rows for SkillDelta, Postmortem, Author.
> - §6 invariants — adds invariant 7 for SkillDelta tenant scoping.
> - **Note on Phase 3 going-real (per `ria-architecture-v2.md` §0.2):** the dataclasses below are now consumed by **real** `global_layer/` modules, not by stubs. Backwards-compatibility is preserved: every v1 dataclass shape carries forward unchanged. Only the three new entities (SkillDelta, Postmortem, Author) are additions.

This document specifies the research-domain entities that live in `ria/domain/`. The dataclasses below are **pure stdlib** — no platform imports, no I/O, no behaviour beyond invariant enforcement. They are the canonical shape of every research-domain concept; anything that needs a different shape for a different layer (HTTP request, platform RunRequest, persistence row) is a derived adapter, not a redefinition.

---

## 1. Domain Model Overview

```
┌── User (ria/user) ─────────────────────────────────────────────────────────┐
│  user_id  ── owns ──▶  profile_id  ── owns ──▶  Project*                   │
└────────────────────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
┌── Project ─────────────────────────────────────────────────────────────────┐
│  project_id, owner_user_id, profile_id, title, posture                    │
│  phases:           Phase × N                                              │
│  hypotheses:       Hypothesis × N                                         │
│  claims:           Claim × N        (each linked to ≥ 1 Hypothesis)       │
│  acceptance:       AcceptanceCriterion × N (each linked to a Claim)      │
│  artifacts:        ProjectArtifact × N                                    │
│  gates:            GateState × N                                          │
│  pi_agent:         PIAgentRoleSpec                                        │
│  budget:           ProjectBudgetEnvelope                                  │
│  status:           ProjectStatus                                          │
│  platform_run_id:  Optional[str]   (resolved after platform start)       │
└────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌── Phase ───────────────────────────────────────────────────────────────────┐
│  phase_id, project_id, name (e.g. "literature_review"), order             │
│  pipeline_step:  PipelineStep                                             │
│  status:         PhaseStatus                                              │
│  current_skill:  Optional[SkillRef]                                       │
│  produced:       List[ProjectArtifact]                                    │
└────────────────────────────────────────────────────────────────────────────┘

┌── Hypothesis ──────┐  ┌── Claim ───────────────┐  ┌── AcceptanceCriterion ┐
│ hypothesis_id      │  │ claim_id               │  │ ac_id                  │
│ project_id         │  │ project_id             │  │ project_id             │
│ statement          │  │ hypothesis_id          │  │ claim_id               │
│ confidence_prior   │  │ statement              │  │ predicate              │
│ status             │  │ supporting_artifacts:  │  │ verifier:              │
│  (open/refuted/    │  │   List[ArtifactRef]    │  │   VerifierKind          │
│   confirmed)       │  │ confidence:            │  │ status:                │
└────────────────────┘  │   ConfidenceScore       │  │  (open/passed/failed)  │
                        └────────────────────────┘  │ on_fail_action:        │
                                                    │   BacktrackPolicy      │
                                                    └────────────────────────┘

┌── ProjectArtifact ──────────────────────────────┐
│ artifact_id, project_id, phase_id, kind          │
│ content_hash (sha256 of the bytes)               │
│ provenance:    ProvenanceTag                     │
│ produced_by:   SkillRef + run_id + stage_id     │
│ confidence:    ConfidenceScore                   │
│ evidence_count: int                              │
│ tenant_id, user_id (for cross-system join)       │
└──────────────────────────────────────────────────┘

┌── Paper ─────────────────┐  ┌── Theorem ───────────────┐  ┌── Experiment ─┐
│ paper_id, doi/arxiv      │  │ theorem_id, statement     │  │ experiment_id │
│ title, authors, year      │  │ project_id (optional)     │  │ project_id    │
│ archive_status            │  │ proof: LeanProofRef       │  │ design        │
│ citation_graph_node_id    │  │ depends_on: List[theorem] │  │ datasets      │
│ tags                      │  │ status: verified/draft    │  │ result        │
└──────────────────────────┘  └──────────────────────────┘  └───────────────┘

┌── Dataset ───────────────────────────────────────────────────────────────┐
│ dataset_id, name, version, content_hash, provenance, registry_status     │
└───────────────────────────────────────────────────────────────────────────┘

┌── Review ────────────────────────────────────────────────────────────────┐
│ review_id, project_id, reviewer_role (Author/Reviewer/Editor)             │
│ targets: List[ArtifactRef]                                                │
│ verdict: ReviewVerdict, comments                                          │
└───────────────────────────────────────────────────────────────────────────┘
```

The lines above are intentionally schematic — the precise dataclass definitions follow in §3.

---

## 2. Identifier and Hash Conventions

| ID | Format | Source of truth |
|---|---|---|
| `user_id` | UUID v4 | RIA `ria/user/store.py` |
| `profile_id` | UUID v4 | RIA `ria/user/store.py`, scoped under user_id |
| `project_id` | UUID v4 | RIA `ria/orchestration/compiler.py` at project creation |
| `phase_id` | `<project_id>:phase:<order>:<name>` | Derived from Project |
| `hypothesis_id`, `claim_id`, `ac_id` | UUID v4 | Allocated by RIA when accepted |
| `artifact_id` | `sha256:<content_hash>` | Derived from content (content-addressed) |
| `paper_id` | DOI if present, else `arxiv:<id>`, else `sha256:<content_hash>` | First-write resolves canonical id |
| `theorem_id`, `dataset_id`, `experiment_id`, `review_id` | UUID v4 | Allocated at first write |
| `tenant_id` | resolved by `ria/platform_client/tenant_resolver.py` | Platform-side scope |
| `run_id`, `stage_id` | platform-allocated; opaque to RIA domain | Platform-side scope |

`content_hash` = sha256 hex digest of the canonical-byte form of the artifact. For text artifacts, canonical-byte form is UTF-8 normalized (NFC); for code, raw bytes; for structured records (JSON), `json.dumps(sort_keys=True, ensure_ascii=False).encode("utf-8")`.

---

## 3. Dataclass Specifications

These are illustrative dataclass sketches — the actual `ria/domain/*.py` files implement them with `@dataclass(frozen=True, slots=True)` where the entity is immutable, and explicit `__post_init__` invariant checks. All fields below are required unless marked `Optional[...]` or with a default.

### 3.1 `ria/domain/project.py`

```python
class Posture(StrEnum):
    DEV = "dev"
    RESEARCH = "research"
    PROD = "prod"

class ProjectStatus(StrEnum):
    DRAFT = "draft"
    PROPOSED = "proposed"
    ACTIVE = "active"
    PAUSED = "paused"            # waiting on a human gate or external dep
    SUCCEEDED = "succeeded"
    ABANDONED = "abandoned"
    ARCHIVED = "archived"

@dataclass(frozen=True, slots=True)
class ProjectBudgetEnvelope:
    max_total_usd: float
    max_per_phase_usd: float
    max_llm_calls: int
    max_wall_clock_hours: int

@dataclass(frozen=True, slots=True)
class Project:
    project_id: str
    owner_user_id: str           # links to ria/user/identity.User
    profile_id: str              # platform profile scope
    tenant_id: str               # resolved at create time
    title: str
    posture: Posture
    pi_agent: PIAgentRoleSpec
    budget: ProjectBudgetEnvelope
    phases: tuple[Phase, ...]
    hypotheses: tuple[Hypothesis, ...]
    claims: tuple[Claim, ...]
    acceptance: tuple[AcceptanceCriterion, ...]
    gates: tuple[GateState, ...]
    status: ProjectStatus
    created_at: datetime
    platform_run_id: str | None  # resolved by orchestration after platform start
```

**Invariants (enforced in `__post_init__`):**
- `project_id` is non-empty UUID v4.
- `owner_user_id` is non-empty.
- `tenant_id` is non-empty (under research/prod posture this is fail-closed; under dev posture defaults to `tenant_dev`).
- `phases` ordered by `phase.order`; `phase.order` strictly increasing from 0.
- Every `Claim` references a Hypothesis present in `hypotheses`.
- Every `AcceptanceCriterion` references a Claim present in `claims`.
- `status == ACTIVE` implies `platform_run_id is not None`.
- `status == SUCCEEDED` implies all `acceptance` items have `status in {PASSED, WAIVED}`.

### 3.2 `ria/domain/phase.py`

```python
class PipelineStep(StrEnum):
    LITERATURE_REVIEW = "literature_review"
    HYPOTHESIS_DRAFT  = "hypothesis_draft"
    CLAIM_AND_AC      = "claim_and_ac"
    EXPERIMENT_OR_PROOF = "experiment_or_proof"
    WRITING           = "writing"
    REVIEW_AND_SUBMIT = "review_and_submit"

class PhaseStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED  = "paused"
    DONE    = "done"
    ABANDONED = "abandoned"

@dataclass(frozen=True, slots=True)
class Phase:
    phase_id: str
    project_id: str
    name: str
    order: int
    pipeline_step: PipelineStep
    status: PhaseStatus
    current_skill: SkillRef | None
    produced: tuple[ArtifactRef, ...]
    started_at: datetime | None
    finished_at: datetime | None
```

**Invariants:**
- Phases are ordered by `order` (0..N).
- `status == DONE` implies `finished_at is not None`.
- `status == RUNNING` implies `started_at is not None and current_skill is not None`.
- The 6-step writing-team pipeline is the canonical default; other pipelines are valid only if the PI Agent role spec declares them.

### 3.3 `ria/domain/hypothesis.py`

```python
class HypothesisStatus(StrEnum):
    OPEN = "open"
    REFUTED = "refuted"
    CONFIRMED = "confirmed"
    WITHDRAWN = "withdrawn"

@dataclass(frozen=True, slots=True)
class Hypothesis:
    hypothesis_id: str
    project_id: str
    statement: str
    confidence_prior: ConfidenceScore   # 0.0 .. 1.0
    status: HypothesisStatus
    created_at: datetime
    last_updated: datetime
```

**Invariants:**
- `0.0 <= confidence_prior <= 1.0`.
- `statement` non-empty, ≤ 2000 chars.
- `status == REFUTED` requires at least one linked `Claim` with `status == REFUTED` and at least one `AcceptanceCriterion` with `status == FAILED`.

### 3.4 `ria/domain/claim.py`

```python
@dataclass(frozen=True, slots=True)
class ConfidenceScore:
    value: float
    method: Literal["prior", "bayes_update", "direct_assertion"]
    last_updated: datetime

@dataclass(frozen=True, slots=True)
class ArtifactRef:
    artifact_id: str
    content_hash: str

class ClaimStatus(StrEnum):
    OPEN = "open"
    SUPPORTED = "supported"
    REFUTED = "refuted"

@dataclass(frozen=True, slots=True)
class Claim:
    claim_id: str
    project_id: str
    hypothesis_id: str
    statement: str
    supporting_artifacts: tuple[ArtifactRef, ...]
    confidence: ConfidenceScore
    status: ClaimStatus
    created_at: datetime
```

### 3.5 `ria/domain/acceptance.py`

```python
class VerifierKind(StrEnum):
    UNIT_TEST = "unit_test"
    INTEGRATION_TEST = "integration_test"
    LEAN_PROOF = "lean_proof"
    EXPERIMENT_RESULT = "experiment_result"
    HUMAN_REVIEW = "human_review"
    STATISTICAL = "statistical"

class ACStatus(StrEnum):
    OPEN = "open"
    PASSED = "passed"
    FAILED = "failed"
    WAIVED = "waived"  # explicit human waiver via Gate D

class BacktrackPolicy(StrEnum):
    RETRY_SAME_CLAIM_NEW_EVIDENCE = "retry_same_claim_new_evidence"
    REVISE_CLAIM = "revise_claim"
    WITHDRAW_CLAIM = "withdraw_claim"
    REFUTE_HYPOTHESIS = "refute_hypothesis"
    HUMAN_GATE_D = "human_gate_d"

@dataclass(frozen=True, slots=True)
class AcceptanceCriterion:
    ac_id: str
    project_id: str
    claim_id: str
    predicate: str          # natural-language statement
    verifier: VerifierKind
    status: ACStatus
    on_fail_action: BacktrackPolicy
    last_evaluated_at: datetime | None
    last_result_artifact: ArtifactRef | None
```

**Invariants:**
- `status == PASSED` implies `last_result_artifact is not None` and `last_evaluated_at is not None`.
- `status == WAIVED` requires a corresponding `GateState` with kind `GATE_D` and decision `APPROVE` referencing this `ac_id`.
- `on_fail_action == HUMAN_GATE_D` and `status == FAILED` triggers the platform pause-on-token via `ria/orchestration/replanner.py`.

### 3.6 `ria/domain/role.py`

```python
class RoleKind(StrEnum):
    PI_AGENT = "pi_agent"
    AUTHOR = "author"
    REVIEWER = "reviewer"
    EDITOR = "editor"

@dataclass(frozen=True, slots=True)
class PIAgentRoleSpec:
    role_id: str
    skill_refs: tuple[SkillRef, ...]   # which skills this role can invoke
    backtrack_policy: BacktrackPolicy
    replan_policy: ReplanPolicy
    research_domain: str               # e.g. "biology/cancer-genomics"
    constraints: tuple[str, ...]       # e.g. ("must use peer-reviewed sources",)
    default_pipeline: PipelineStep     # entry phase
    budget_share: float                # 0.0 .. 1.0 of project budget allotted

class ReplanPolicy(StrEnum):
    NEVER = "never"
    ON_AC_FAIL = "on_ac_fail"
    ON_GATE_REJECT = "on_gate_reject"
    ANYTIME = "anytime"
```

**Invariants:** `0.0 < budget_share <= 1.0`; `skill_refs` non-empty.

### 3.7 `ria/domain/gate.py`

```python
class GateKind(StrEnum):
    GATE_D = "gate_d"   # PI diagnosis + remediation draft
    GATE_E = "gate_e"   # Ethics / IRB review
    GATE_F = "gate_f"   # Publication readiness / final approval

class GateDecision(StrEnum):
    PENDING = "pending"
    APPROVE = "approve"
    REJECT = "reject"
    DEFER = "defer"

@dataclass(frozen=True, slots=True)
class GateState:
    gate_id: str
    project_id: str
    kind: GateKind
    triggered_by_ac: str | None      # ac_id if Gate D triggered by AC failure
    pending_payload: dict            # context for the human reviewer
    decision: GateDecision
    decided_by_user_id: str | None
    decided_at: datetime | None
    decision_payload: dict | None    # human's resume input (e.g., revised claim)
    platform_pause_token: str | None # opaque token from agent_server
```

**Invariants:**
- `decision == PENDING` implies `decided_by_user_id is None and decided_at is None`.
- `decision in {APPROVE, REJECT, DEFER}` implies `decided_by_user_id is not None and decided_at is not None`.
- `kind == GATE_D` implies `triggered_by_ac is not None`.
- `platform_pause_token` is set by `ria/orchestration/replanner.py` when the platform run pauses.

### 3.8 `ria/domain/paper.py`

```python
@dataclass(frozen=True, slots=True)
class CitationEdge:
    src_paper_id: str
    dst_paper_id: str
    section_in_src: str | None

class PaperArchiveStatus(StrEnum):
    UNCURATED = "uncurated"
    CANDIDATE = "candidate"
    ARCHIVED = "archived"
    REJECTED = "rejected"

@dataclass(frozen=True, slots=True)
class Paper:
    paper_id: str
    title: str
    authors: tuple[str, ...]
    year: int
    doi: str | None
    arxiv_id: str | None
    content_hash: str
    archive_status: PaperArchiveStatus
    citation_graph_node_id: str | None
    tags: tuple[str, ...]
    added_at: datetime
```

### 3.9 `ria/domain/theorem.py`

```python
class TheoremStatus(StrEnum):
    DRAFT = "draft"
    VERIFIED = "verified"
    REFUTED = "refuted"
    DEPRECATED = "deprecated"

@dataclass(frozen=True, slots=True)
class LeanProofRef:
    proof_id: str
    file_path: str          # within Lean Library
    revision_hash: str

@dataclass(frozen=True, slots=True)
class Theorem:
    theorem_id: str
    statement: str
    project_id: str | None  # null = library theorem (cross-project)
    proof: LeanProofRef | None
    depends_on: tuple[str, ...]   # theorem_ids
    status: TheoremStatus
    added_at: datetime
```

### 3.10 `ria/domain/experiment.py`

```python
@dataclass(frozen=True, slots=True)
class ExperimentDesign:
    description: str
    independent_variables: tuple[str, ...]
    dependent_variables: tuple[str, ...]
    control_setup: str
    sample_size_plan: int
    pre_registered: bool

@dataclass(frozen=True, slots=True)
class ExperimentResult:
    summary: str
    p_value: float | None
    effect_size: float | None
    raw_artifact: ArtifactRef
    confidence: ConfidenceScore

class ExperimentStatus(StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    INVALID = "invalid"

@dataclass(frozen=True, slots=True)
class Experiment:
    experiment_id: str
    project_id: str
    design: ExperimentDesign
    datasets: tuple[str, ...]   # dataset_ids
    result: ExperimentResult | None
    status: ExperimentStatus
    started_at: datetime | None
    finished_at: datetime | None
```

### 3.11 `ria/domain/dataset.py`

```python
class ProvenanceTag(StrEnum):
    MEASURED = "measured"
    DERIVED = "derived"
    SIMULATED = "simulated"
    ILLUSTRATIVE = "illustrative"
    UNVERIFIED = "unverified"

class DatasetRegistryStatus(StrEnum):
    DRAFT = "draft"
    REGISTERED = "registered"
    DEPRECATED = "deprecated"

@dataclass(frozen=True, slots=True)
class Dataset:
    dataset_id: str
    name: str
    version: str
    content_hash: str
    provenance: ProvenanceTag
    registry_status: DatasetRegistryStatus
    description: str
    license: str | None
    added_at: datetime
```

### 3.12 `ria/domain/review.py`

```python
class ReviewerRole(StrEnum):
    AUTHOR = "author"
    INTERNAL_REVIEWER = "internal_reviewer"
    EXTERNAL_REVIEWER = "external_reviewer"
    EDITOR = "editor"

class ReviewVerdict(StrEnum):
    ACCEPT = "accept"
    MINOR_REVISION = "minor_revision"
    MAJOR_REVISION = "major_revision"
    REJECT = "reject"

@dataclass(frozen=True, slots=True)
class Review:
    review_id: str
    project_id: str
    reviewer_role: ReviewerRole
    reviewer_user_id: str
    targets: tuple[ArtifactRef, ...]
    verdict: ReviewVerdict
    comments: str
    submitted_at: datetime
```

### 3.13 `ria/domain/skill_delta.py` *(v1.1)*

```python
class SkillDeltaKind(StrEnum):
    ROUTE_CHANGE = "route_change"           # changed StageDirective routing
    PROMPT_CHANGE = "prompt_change"         # changed system / user prompt template
    TIER_CHANGE = "tier_change"             # changed model tier preference
    BUDGET_CHANGE = "budget_change"         # changed per-call budget envelope
    REGRESSION = "regression"               # measured worse on signal X
    IMPROVEMENT = "improvement"             # measured better on signal X
    NO_OP = "no_op"                         # no measurable difference

class SkillDeltaSignal(StrEnum):
    SUCCESS_RATE = "success_rate"
    LATENCY_P95 = "latency_p95"
    COST_PER_RUN = "cost_per_run"
    USER_SATISFACTION = "user_satisfaction"
    AC_PASS_RATE = "ac_pass_rate"

@dataclass(frozen=True, slots=True)
class SkillDelta:
    delta_id: str               # UUID v4
    skill_id: str               # platform-side skill_id; opaque to RIA
    from_version: str           # platform skill version (champion)
    to_version: str             # platform skill version (challenger)
    project_id: str             # which project surfaced this delta (R-RIA-8)
    tenant_id: str              # required (R-RIA-8)
    kind: SkillDeltaKind
    signal: SkillDeltaSignal | None     # null if kind=NO_OP
    delta_value: float | None           # signed; +ve = improvement, -ve = regression
    measured_n_runs: int                # sample size used to measure
    confidence: ConfidenceScore         # statistical confidence in the delta
    detected_at: datetime
    last_evaluated_at: datetime
```

**Invariants (in `__post_init__`):**
- `tenant_id` is non-empty (R-RIA-8).
- `project_id` is non-empty (R-RIA-8).
- `from_version != to_version`.
- `kind in {IMPROVEMENT, REGRESSION}` implies `signal is not None and delta_value is not None and measured_n_runs > 0`.
- `kind == NO_OP` implies `delta_value is None or abs(delta_value) < epsilon` (epsilon = 0.01 by default).
- `0.0 <= confidence.value <= 1.0`.

**Consumed by:** `ria/global_layer/evolution_engine/skill_delta.py::index_delta(...)`. The `SkillDelta` is constructed from platform run records (read via `ria/platform_client/run_lifecycle.py`); construction at the seam means dataclass invariants are validated at the RIA-side boundary.

**Note on hi-agent W34 dependency:** Correct attribution of `from_version` / `to_version` requires hi-agent's F.2 (executor-side lineage population) closure. Without F.2, `from_version` / `to_version` may be empty strings, failing the invariant. The construction site catches this; the failed test is logged in `red-status.json` as `blocked_by_w34_id: B-W34-1`.

### 3.14 `ria/domain/postmortem.py` *(v1.1)*

```python
class PostmortemOutcome(StrEnum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"  # some AC passed, some failed
    FAILURE = "failure"
    ABANDONED = "abandoned"
    INVALID = "invalid"                  # malformed run; cannot reconstruct

class PostmortemFailureClass(StrEnum):
    AC_FAILURE = "ac_failure"
    BUDGET_EXHAUSTED = "budget_exhausted"
    GATE_REJECT = "gate_reject"
    PLATFORM_FAULT = "platform_fault"
    LLM_FAULT = "llm_fault"
    SKILL_FAULT = "skill_fault"
    USER_CANCEL = "user_cancel"
    UNKNOWN = "unknown"

@dataclass(frozen=True, slots=True)
class AttemptTreeNode:
    run_id: str
    parent_run_id: str | None     # None = root attempt
    attempt_id: str               # "1", "2", ... (recovery cycles)
    phase_id: str                 # which phase was active
    started_at: datetime
    finished_at: datetime | None  # None = still running
    terminal_state: str | None    # "done"|"cancelled"|"failed"|None
    last_known_stage: str | None  # last TRACE stage observed

@dataclass(frozen=True, slots=True)
class Postmortem:
    postmortem_id: str            # UUID v4
    project_id: str               # required (R-RIA-8)
    tenant_id: str                # required (R-RIA-8)
    root_run_id: str              # the original run_id (attempt 1)
    attempt_tree: tuple[AttemptTreeNode, ...]  # full reconstructed tree
    outcome: PostmortemOutcome
    failure_class: PostmortemFailureClass | None  # None if outcome=SUCCESS
    total_wall_clock_seconds: int
    total_llm_calls: int
    total_cost_usd: float
    ac_passed: int
    ac_failed: int
    ac_waived: int
    notes: str                    # human-or-LLM-generated narrative
    constructed_at: datetime
```

**Invariants:**
- `tenant_id`, `project_id`, `root_run_id` non-empty.
- `attempt_tree` non-empty; first node has `parent_run_id is None and attempt_id == "1"`.
- For each non-root node, `parent_run_id` references some earlier node's `run_id`.
- `outcome == SUCCESS` implies `failure_class is None`.
- `outcome != SUCCESS` implies `failure_class is not None`.
- `total_*` fields are non-negative.
- `ac_passed + ac_failed + ac_waived == project's total AC count` (cross-validated by construction site).

**Consumed by:** `ria/global_layer/evolution_engine/postmortem.py::build_postmortem(project_id, ...)`. Reads platform run records; reconstructs the attempt tree; classifies the outcome; produces the `Postmortem` dataclass; persists in RIA's SQLite under `$RIA_DATA_DIR/evolution/postmortems.db`.

**Note on hi-agent W34 dependencies:**
- F.2 closure required for correct `parent_run_id` chain (without it, every `parent_run_id` is empty string and `attempt_tree` collapses to a list of disconnected single-attempt entries).
- F.3 closure required for guaranteed non-empty `phase_id` on each node (without it, `phase_id == ""` is silently accepted at construction).
- Both surfaced in red-status as `blocked_by_w34_id: B-W34-1` and `B-W34-2` respectively.

### 3.15 `ria/domain/author.py` *(v1.1)*

```python
@dataclass(frozen=True, slots=True)
class Author:
    author_id: str                # canonical id; ORCID if available, else sha256(name + first-paper-doi)
    name: str                     # canonical display name
    orcid: str | None             # https://orcid.org/0000-...
    affiliations: tuple[str, ...] # current + past, time-ordered
    aliases: tuple[str, ...]      # alternative spellings encountered
    added_at: datetime
```

**Invariants:**
- `name` non-empty.
- If `orcid is not None`, matches ORCID format `\d{4}-\d{4}-\d{4}-\d{3}[\dX]`.
- `author_id` is `sha256:<digest>` if no ORCID, else `orcid:<orcid>`.

**Migration from v1's `Paper.authors: tuple[str, ...]`:**

The v1 `Paper.authors` field is a flat tuple of strings. v1.1 adds **`Author`** as a structured entity but **does not break the v1 `Paper.authors` field**. New `Paper` instances should populate `Paper.authors` with each author's `name` (preserving v1 shape) AND additionally maintain a side-table of `Author` records keyed by `author_id`. Citation graph queries (paper → author → other papers) traverse the side-table.

A future v2 of this document may consolidate the two; v1.1 keeps both for backwards compatibility per `ria-quality-requirements-v1.md` §10.

---

## 4. Lifecycle State Machine (Project)

```
            ┌────────┐  user submits      ┌──────────┐  PI Agent ack    ┌────────┐
            │ DRAFT  │ ─────────────────▶ │ PROPOSED │ ───────────────▶ │ ACTIVE │
            └────────┘                    └──────────┘                  └───┬────┘
                                                                            │
                  ┌────────────── Gate D / E pending ─────────────┐         │
                  │                                               │         │
                  ▼                                               │         ▼
              ┌──────────┐  human approves                     ┌──────────┐
              │  PAUSED  │ ─────────────────────────────────▶  │ ACTIVE   │
              └──────────┘                                     └────┬─────┘
                  │                                                 │
                  │ human rejects + reason                          │ AC for Hypothesis
                  ▼                                                 │ all PASSED + Gate F approve
              ┌──────────┐                                          ▼
              │ABANDONED │                                   ┌────────────┐
              └──────────┘                                   │ SUCCEEDED  │
                                                             └─────┬──────┘
                                                                   │ archive policy
                                                                   ▼
                                                             ┌────────────┐
                                                             │  ARCHIVED  │
                                                             └────────────┘
```

**Transition rules** (in `ria/orchestration/project_state.py`):

- `DRAFT → PROPOSED`: user accepts the auto-built ProjectSpec (CLI: `research project new …`).
- `PROPOSED → ACTIVE`: platform returns a `run_id` from `POST /v1/runs` (skill registered, run queued).
- `ACTIVE → PAUSED`: platform emits `gate_pending` event over SSE, RIA records `GateState`.
- `PAUSED → ACTIVE`: human approves via `research gate {D,E,F} approve`, RIA calls `POST /v1/runs/{id}/signal` with the resume payload.
- `PAUSED → ABANDONED`: human rejects with `reason=abandon`, RIA cancels the platform run.
- `ACTIVE → SUCCEEDED`: all `AcceptanceCriterion` of every `Hypothesis` resolved (`PASSED` or `WAIVED`), and Gate F is `APPROVE`.
- `ACTIVE → ABANDONED`: any of (user cancel, budget exhausted, platform run irrecoverable failure).
- `* → ARCHIVED`: archive policy after 90 days idle, or explicit `research project archive`.

The state machine is the single mutator of `Project.status`. Direct field assignment outside this module fails the layering CI gate (mirrors hi-agent's R-AS-9 `transition()` discipline).

---

## 5. Cross-Reference Map (Domain → Platform)

This table summarises which domain concepts map to which platform concepts. Full call mappings live in `ria-platform-contract-mapping-v1.md`.

| RIA domain concept | Platform concept | Notes |
|---|---|---|
| Project | Run + persistent project_id | one Project = one platform Run (long-lived) |
| Phase | Stage within the Run's TRACE pipeline | Phase.order roughly maps to Stage transitions |
| PIAgentRoleSpec | SkillSpec (registered via `POST /v1/skills`) | role compiles to one parent skill that orchestrates phase skills |
| Hypothesis / Claim / AC | RIA-only — platform does not know these | persisted in `ria/user/store.py` |
| GateState | Platform pause-token + resume-input pattern | Gate kind/decision is RIA-only semantic |
| ProjectArtifact | Platform Artifact (workspace) | content-addressed; `Idempotency-Key` for cold-write-once |
| Paper / Theorem / Dataset | Platform Artifact (typed via metadata) | `global_layer/` materialises these as cross-project artifacts; reaches arxiv / lean / zenodo via `external_services/` (v1.1) |
| Review | RIA-only | persisted in `ria/user/store.py` |
| **SkillDelta** *(v1.1)* | Platform skill version pair (`from_version`, `to_version`) — opaque to RIA | RIA reads via `platform_client/run_lifecycle.py`; constructs the delta in `evolution_engine/skill_delta.py`; persists in `$RIA_DATA_DIR/evolution/skill_deltas.db` |
| **Postmortem** *(v1.1)* | Reconstructed from platform Run records (lineage chain) | requires hi-agent F.2/F.3 closures (B-W34-1/2) for correctness; persists in `$RIA_DATA_DIR/evolution/postmortems.db` |
| **Author** *(v1.1)* | RIA-only | persists in RIA's SQLite as a side-table to `Paper`; never sent to platform |

---

## 6. Domain Invariants Cross-Cut

The following invariants are checked at multiple layers (domain `__post_init__`, orchestration compiler, platform-side validation):

1. **Tenant scope is always populated.** Under research/prod posture, every domain object that crosses into platform_client carries a non-empty `tenant_id`. This is a defence-in-depth restatement of platform R12 (contract spine completeness) at the RIA boundary.
2. **Project budget is non-negotiable.** A platform call that would exceed `ProjectBudgetEnvelope.max_total_usd` is refused at `ria/platform_client/budget_enforcer.py` *before* contacting the platform.
3. **Gate decisions are append-only.** Once a `GateState.decision` is set to a non-`PENDING` value, the GateState is immutable.
4. **Acceptance Criterion failure with `on_fail_action == HUMAN_GATE_D`** must produce a `GateState(kind=GATE_D)` before the project transitions to `PAUSED`.
5. **Provenance honesty.** A `Claim.confidence` upgraded from `prior` to `bayes_update` requires at least one supporting artifact with `provenance in {MEASURED, DERIVED}`. `SIMULATED` / `ILLUSTRATIVE` artifacts cannot upgrade a claim's confidence.
6. **Theorem dependency closure.** A `Theorem(status=VERIFIED)` requires every `theorem_id` in `depends_on` also be `VERIFIED` (closed dependency graph). `ria/orchestration/compiler.py` checks this before submitting a Lean proof to the platform.
7. **(v1.1) SkillDelta tenant scoping.** Every `SkillDelta` carries `tenant_id` and `project_id` (R-RIA-8). Cross-tenant SkillDelta queries (e.g., `evolution_engine.compare_versions(skill_id, tenant_id=A)` vs `... tenant_id=B`) are explicitly disallowed at the construction site; an attempt raises `CrossTenantSkillDeltaQueryError`. This is RIA-side defense-in-depth above hi-agent's tenant isolation; it preserves correctness even if hi-agent's KG / skill registry partition (F.4 / B-5 follow-through) is incomplete at HEAD.

   **Note:** This is not the same as AP-9 (defense-in-depth shim that masks a platform gap). The RIA-side construction-site check is **structural enforcement of a domain invariant** — `SkillDelta` is a RIA-domain object and its tenant scoping is a domain property. It is not a workaround for a platform gap; it is a domain rule. Tests against the platform's tenant-scoping behaviour live in `tests/conformance/test_cross_tenant_isolation_*` and remain red until hi-agent closes the gap.

---

## 7. Open Questions (Resolved Defaults)

| Question | Resolution (default for v1) |
|---|---|
| Can a Project span multiple PI Agents? | **No** for v1. One Project = one PIAgentRoleSpec = one parent platform Run. Multi-PI workflows are Phase 3+. |
| Can Hypotheses be shared across Projects? | **No** in domain; **yes** indirectly via Paper Archive citations. Cross-project hypothesis-level dedup is a Phase 3 feature. |
| What is the "definition" of a successful Project? | All Hypotheses' AC trees resolve, Gate F approves, Paper artifact is curated to ARCHIVED. |
| How are Lean theorems verified? | Skill `lean-prove` is invoked as a sub-run; the platform run hosts Lean's verifier as a registered capability. |
| What is the auth model between users? | Phase 1: single-user (CLI / Codex / CC for local researcher). Phase 2+: multi-user with project ACL (owner / collaborators / public-read). |

---

## 8. Versioning and Evolution

The domain model has its own version: `RIA_DOMAIN_VERSION = "v1"` in `ria/domain/__init__.py`. Breaking changes (field rename, type change, removed enum value) require a `v2/` sub-package and a deprecation wave; additive changes (new optional field, new enum value) are minor revisions.

The domain model's version is **independent** of the platform's `agent_server` v1 contract. RIA can ship a domain-model `v1.3` while staying on platform `v1`. Conversely, RIA must support platform `v1` even if RIA is on domain-model `v2`.

---

**End of Domain Model v1.1.**
