# Research Intelligence Application — Architecture Design

**Date:** 2026-04-15  
**Status:** Draft — pending user approval  
**Scope:** Overall architecture spec (sub-specs per phase follow separately)

---

## 1. Product Positioning

**Research Intelligence Application** — a research AI application that manages the full lifecycle of academic research, from literature survey through experiment execution to publishable paper.

It is not:
- A single research agent (one agent cannot hold all tools and context without interference)
- A pure skill package (skills alone cannot carry durable state, storage infrastructure, or orchestration)

It is:
- An **application** with project management, human gate console, and data infrastructure
- Whose execution model is a **research team** of specialized agents coordinated by a PI Agent
- Whose domain expertise is encoded as **skills** loaded per agent and per project

---

## 2. Foundational Principles

| Principle | Statement | Architectural Implication |
|-----------|-----------|--------------------------|
| **P1** | Intelligence continuously evolves | Every project must produce learnable artifacts. PI Agent's cross-project memory is the primary evolution asset. Skills improve via A/B versioning after each project. |
| **P2** | Cost continuously decreases | Global shared assets (papers, datasets, Lean proofs) are written once and reused across projects. PI Agent's precise instructions reduce wasteful re-runs. Model tier routing improves based on historical cost/quality data. |
| **P3** | No mock implementations in production | All agent outputs must reflect real execution. Unimplemented tool calls → `skip`/`xfail`, never faked. |

---

## 3. Three-Layer Context Architecture

```
┌─────────────────────────────────────────────────────┐
│  Layer 0 · Global Layer (cross-project)             │
│  Global Paper Archive · Dataset Registry            │
│  Global Lean Proof Library · Evolution Engine       │
│  PI Agent Cross-Project Memory                      │
└────────────────┬────────────────────────────────────┘
                 │ project start: inherit · project end: deposit
┌────────────────▼────────────────────────────────────┐
│  Layer 1 · Agent Team Space (per research project)  │
│                                                     │
│  PI Agent (end-to-end accountability)               │
│  ┌──────────────────────────────────────────────┐   │
│  │ Team Shared Context                          │   │
│  │ memory · knowledge · specs · skills · logs  │   │
│  └──────────────────────────────────────────────┘   │
│  ┌────────┐ ┌──────────┐ ┌────────────┐ ┌───────┐  │
│  │Survey  │ │Analysis  │ │Experiment  │ │Writing│  │
│  │Agent   │ │Agent     │ │Agent       │ │Team   │  │
│  │private │ │private   │ │private     │ │private│  │
│  └────────┘ └──────────┘ └────────────┘ └───────┘  │
└────────────────┬────────────────────────────────────┘
                 │ runtime
┌────────────────▼────────────────────────────────────┐
│  Layer 2 · hi-agent TRACE Runtime                   │
│  RunExecutor · TierRouter · MemoryManager           │
│  SkillLoader · KnowledgeBase · LLMGateway           │
└─────────────────────────────────────────────────────┘
```

---

## 4. PI Agent — Principal Investigator

The PI Agent is the **single point of accountability** for end-to-end research quality. It is a long-running TRACE Run using a strong model with persistent L0→L3 memory across the entire project lifecycle.

### What PI Agent holds

| Asset | Description |
|-------|-------------|
| Research hypothesis H | Stable throughout the project; never delegated |
| Technical claim C | The specific improvement being argued |
| Acceptance criteria AC | What constitutes a publishable result |
| Full project memory | L0 raw logs → L3 long-term knowledge graph |
| Complete phase output history | Can review any prior stage output in context |

### How PI Agent differs from a scheduler

| Dimension | Scheduler (old) | PI Agent (new) |
|-----------|----------------|----------------|
| Instruction style | "Enter Survey phase" | "Focus on efficient transformer works 2018–2024, prioritize papers with >100 citations" |
| Backtrack instruction | "Return to Experiment" | "Add ablation for hypothesis H₂: re-run with lr ∈ {1e-3, 5e-4, 1e-4}, report statistical significance" |
| Phase review | Completion check | Content judgment against H and AC |
| Human Gate presentation | "Phase complete, please approve" | Synthesized diagnosis + specific remediation draft for human to confirm |
| Post-project | Nothing | Leads Postmortem, deposits learnings to Global Layer |

### PI Agent's cross-project memory is P1's primary evolution asset

As projects accumulate, the PI Agent develops research intuition:
- Which research directions yield publishable results
- How to constrain Analysis Agent's proof scope for faster Lean verification
- Which experiment designs most efficiently prove a hypothesis
- How to reduce back-and-forth with Writing Team reviewers

---

## 5. Research Phase Pipeline

### 5.1 Phase Overview

```
PI Agent
  │
  ├─→ [Survey Agent] ──────────────────────────────────┐
  │     ↓ output: papers/ + knowledge graph            │
  │   Human Gate D (PI presents: coverage sufficient?) │
  │                                                    │
  ├─→ [Analysis Agent] ────────────────────────────────┤
  │     ↓ output: lean/ + specs/improvement.md         │
  │   Human Gate D (PI presents: contribution valid?)  │
  │                                                    │
  ├─→ [Experiment Agent] ──────────────────────────────┤
  │     ↓ output: experiments/{exp_id}/                │
  │   Human Gate D (PI presents: hypothesis proven?)   │
  │                                                    │
  └─→ [Writing Team] ──────────────────────────────────┤
        ↓ output: paper/final.tex                      │
      Human Gate D (PI presents: publishable?)         │
        │                                              │
        └─ Backtrack decision ────────────────────────►┘
```

### 5.2 Backtrack Decision Criteria

PI Agent diagnoses Writing review failures and issues precise remediation instructions:

| Failure Type | Backtrack Target | PI Instruction Style |
|---|---|---|
| Insufficient experiments / missing controls | Experiment Agent | "Add ablation X with parameters Y, prove statistical significance at p<0.05" |
| Lean proof defect / contribution unclear | Analysis Agent | "Re-derive theorem T with constraint C, verify via Lean before returning" |
| Related work missing / citation gap | Survey Agent | "Search keyword K in venues V, focus on years Y" |

### 5.3 Human Gate Model

Gate Type **D (final_approval)** is used at every phase transition. The PI Agent:
1. Synthesizes the phase output against H and AC
2. Produces a recommendation: proceed / backtrack
3. If backtrack: includes a specific remediation plan
4. Human confirms or overrides

### 5.4 Agent TRACE Configuration

| Agent | Model Tier | Strategy | Restart Policy |
|---|---|---|---|
| PI Agent | strong | sequential | reflect(3) |
| Survey Agent | light→medium | parallel_dag | retry(3) |
| Analysis Agent | strong | sequential | reflect(2) |
| Experiment Agent | medium | sequential | retry + escalate |
| Writing Team (×5 sub-runs) | strong | sequential | reflect(2) |

---

## 6. Writing Team Composition

The Writing Team runs as sequential sub-Runs under PI Agent coordination. Distinct role agents: Author, Reviewer (×2), Editor, Journal Reviewer. Author runs twice (initial draft + revision), giving 6 total invocations:

1. **Author Agent** (run 1) — drafts full IMRaD structure in LaTeX
2. **Reviewer ×2** (parallel) — independent methodology and experiment review → written opinions
3. **Editor Agent** — logical consistency and narrative flow → revision directives
4. **Author Agent** (run 2) — incorporates internal feedback → second draft
5. **Journal Reviewer Agent** — simulates target venue reviewer style → external review
6. **PI Agent** — publishability judgment against H and AC → Human Gate D

---

## 7. Workspace Structure

Each research project has an isolated workspace bound to a `profile_id`:

```
projects/{project-name}/
│
├── ❄️ Cold (immutable after write)
│   ├── papers/{paper_id}/
│   │   ├── source.tex        ← preferred (arxiv)
│   │   ├── paper.pdf         ← archival + fallback
│   │   ├── extracted.txt     ← PDF text fallback (quality-flagged)
│   │   └── meta.json         ← title, DOI, source, quality level
│   ├── lean/
│   │   └── {theorem}.lean    ← Lean 4 verified proofs
│   ├── skills/               ← domain SKILL.md files
│   └── specs/
│       ├── hypothesis.md     ← H + C + AC (PI-authored)
│       └── constraints.yaml  ← research constraints
│
├── ❄️ Cold (dataset — content-addressed)
│   └── dataset/{name}/
│       ├── registry.json     ← hash, source, license, splits
│       └── data/             ← read-only, immutable
│
├── 🌡️ Warm (versioned, on-demand analysis)
│   ├── experiments/{exp_id}/
│   │   ├── config.yaml       ← full experiment configuration
│   │   ├── results.json      ← quantitative results
│   │   ├── analysis.md       ← PI + agent analysis report
│   │   └── repro/
│   │       ├── requirements.txt
│   │       └── run.sh
│   ├── knowledge/            ← Neo4j snapshot + wiki pages
│   ├── memory/               ← L1 STM + L2 Dream + L3 graph
│   ├── paper/
│   │   ├── draft_v{n}.tex
│   │   ├── reviews/
│   │   └── final.tex
│   └── checkpoints/          ← TRACE Run checkpoints
│
└── 🔥 Hot (append-only, stream-analyzed)
    ├── logs/                 ← all agent run logs (JSONL)
    └── memory/L0/            ← raw experience stream (JSONL)
```

### Paper Storage Convention

Models read LaTeX significantly better than extracted PDF text (formulas, structure, citations all degrade in PDF extraction). Therefore:
- arxiv papers: download LaTeX source via `arxiv.org/e-print/{id}` as primary
- Non-arxiv papers: PDF as archival, `extracted.txt` as model-readable fallback, quality level flagged in `meta.json`
- `paper.pdf` is for human reading only; agents read `source.tex` or `extracted.txt`

### Data Temperature Rules

| Tier | Write Rule | Read Rule |
|---|---|---|
| ❄️ Cold | Written once, content-hash verified, then read-only | Any agent, any time |
| 🌡️ Warm | Each write generates a new versioned ID | Loaded on demand, compared across versions |
| 🔥 Hot | Append-only, never overwritten | Stream analysis only (grep/jq), not random-access |

---

## 8. Global Layer (Cross-Project)

| Asset | Purpose | P1/P2 |
|---|---|---|
| Global Paper Archive | Papers downloaded once, shared across all projects | P2 |
| Global Dataset Registry | Datasets registered once, all projects reuse | P2 |
| Global Lean Proof Library | Verified theorems indexed by signature, directly citable | P2 |
| Evolution Engine | PostmortemAnalyzer + SkillEvolver + ChampionChallenger | P1 |
| PI Agent Cross-Project Memory | Research intuition accumulates across projects | P1 |

### Evolution Engine Flow (per project completion)

```
Project ends
  → PI Agent leads Postmortem
  → PostmortemAnalyzer: what worked, what cost most, what caused backtracks
  → SkillExtractor: encode effective strategies as new skill versions
  → ChampionChallenger: A/B validate new skills against prior versions
  → Winning skills promoted to Global Skill Library
  → TierRouter updated with new cost/quality calibration data
```

---

## 9. Infrastructure Stack

| Component | Role | Scope |
|---|---|---|
| **hi-agent TRACE** | Agent runtime: RunExecutor, MemoryManager, SkillLoader, LLMGateway, TierRouter | All layers |
| **Neo4j** | Citation network + knowledge graph, Cypher queries, browser visualization | Per-project (warm) |
| **SQLite** | Paper metadata index, deduplication, download status tracking | Per-project (hot→warm) |
| **Lean 4** | Formal mathematical proof generation and verification (hard requirement) | Per-proof → global archive |
| **File System** | Cold/warm/hot workspace isolation, content-addressed storage | Per-project + global |

### Anti-Hallucination Guarantee

Every paper reference must have a corresponding entry in `papers/{id}/meta.json` before the agent can cite it. The PI Agent enforces this during phase reviews: any citation without a local archive entry is flagged as a hallucination risk and rejected.

---

## 10. Multi-Project Isolation

Each research project is bound to:
- A unique `profile_id` in hi-agent's TaskContract
- A dedicated `workspace_dir` under `projects/`

All Phase Runs within a project share the same `profile_id`, giving them access to the team's shared context (memory, knowledge, skills, specs) without explicit state passing. Different projects have different `profile_id` values and entirely separate workspace directories.

Multiple projects can run in parallel; hi-agent's `RunContextManager` handles concurrent run isolation.

---

## 11. User Interface

| Interface | Purpose |
|---|---|
| **CLI** | `research new <topic>`, `research status`, `research approve`, `research viz` |
| **Human Gate Console** | Phase output review, backtrack decision confirmation |
| **Neo4j Browser** | Citation network visualization, knowledge graph exploration |
| **Experiment Dashboard** | Multi-version experiment comparison, metric visualization, repro-pack export |

---

## 12. What This Spec Does Not Cover

The following are intentionally deferred to phase-level sub-specs:

- Survey Agent: arxiv/Scholar API integration details, crawling rate limits, deduplication algorithm
- Analysis Agent: Lean 4 code generation prompt design, gap analysis algorithm
- Experiment Agent: environment locking mechanism, local execution harness, result schema
- Writing Team: role prompt design, review scoring rubric, journal style simulation
- Neo4j schema: node/edge types, index design, Cypher query patterns
- Evolution Engine: SkillEvolver algorithm, ChampionChallenger evaluation protocol
