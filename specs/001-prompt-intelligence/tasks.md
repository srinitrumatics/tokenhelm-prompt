---
description: "Task list for Prompt Intelligence implementation"
---

# Tasks: Prompt Intelligence

**Input**: Design documents from `/specs/001-prompt-intelligence/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: INCLUDED — the spec mandates ≥95% coverage plus concurrency, streaming,
and benchmark suites (NFRs, SC-003/004/005/009), so test tasks are first-class.

**Organization**: Tasks are grouped by user story so each story is an
independently implementable, independently testable increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete tasks)
- **[Story]**: US1–US5 (user-story phases only)
- All paths are repository-relative; package import name is `tokenhelm_prompt`.

## Path Conventions

- Source: `src/tokenhelm_prompt/`
- Tests: `tests/{unit,integration,concurrency,streaming,benchmark}/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project skeleton and tooling (plan Phase 1 — Foundation).

- [X] T001 Create the package and test layout (`src/tokenhelm_prompt/{models,lib,registry,context,tracking,analytics,integrations,cli}/__init__.py` and `tests/{unit,integration,concurrency,streaming,benchmark}/`) per plan.md
- [X] T002 Create `pyproject.toml` for distribution `tokenhelm-prompt` (Python >=3.11, runtime deps `PyYAML` + `click`, TokenHelm as peer dep, optional extras `[langchain]`/`[llamaindex]`/`[crewai]`/`[adk]`/`[openai-agents]`/`[haystack]`, console entry `tokenhelm = tokenhelm_prompt.cli.main:main`)
- [X] T003 [P] Configure test/lint tooling in `pyproject.toml` (`pytest`, `pytest-asyncio`, `pytest-cov` with `--cov-fail-under=95`, `pytest-benchmark`, `ruff`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Metadata-only models, hashing, and the registry interface that every
story depends on (plan Phase 1 deliverables).

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 [P] Implement `Prompt` dataclass + validation in `src/tokenhelm_prompt/models/prompt.py` (fields per data-model.md; metadata-only)
- [X] T005 [P] Implement immutable `Version` dataclass with `status` enum (`active`/`deprecated`/`archived`) in `src/tokenhelm_prompt/models/version.py`
- [X] T006 [P] Implement `PromptEvent` dataclass in `src/tokenhelm_prompt/models/event.py`, including a `status` (`success`/`error`) field sourced from the underlying TokenHelm event (the data source for the analytics `failures` metric, per data-model.md)
- [X] T007 [P] Implement `PromptMetadata` bundle (name, version, owner, application, environment, template_hash, variable_hash) in `src/tokenhelm_prompt/models/metadata.py`
- [X] T008 [P] Implement hashing utilities — `template_hash` (SHA-256 of template string) and `variable_hash` (SHA-256 over sorted variable **names** only) in `src/tokenhelm_prompt/lib/hashing.py`
- [X] T009 Define `PromptRegistry` interface + domain exceptions (NotFound/Conflict/Validation) in `src/tokenhelm_prompt/registry/base.py` (depends on T004–T005)
- [X] T010 [P] Wire public exports in `src/tokenhelm_prompt/__init__.py` (export `tracker`, `analytics`, registry classes; NO optional/framework imports)

**Checkpoint**: Models, hashing, and registry interface ready — stories can begin.

---

## Phase 3: User Story 1 - Register and Version Prompt Templates (Priority: P1) 🎯 MVP

**Goal**: A local, offline registry with CRUD and immutable versioning, drivable
from code and the CLI.

**Independent Test**: Register → list → get → bump version → delete, with no LLM
call; prior versions remain retrievable.

### Tests for User Story 1 ⚠️ (write first, ensure they fail)

- [X] T011 [P] [US1] Contract test for registry CRUD + version resolution per `contracts/registry.md` in `tests/integration/test_registry_contract.py`
- [X] T012 [P] [US1] Unit tests for version immutability and resolver (latest-active vs pinned) in `tests/unit/test_versioning.py`
- [X] T013 [P] [US1] CLI tests for `init`/`list`/`versions`/`diff` in `tests/integration/test_cli_registry.py`

### Implementation for User Story 1

- [X] T014 [P] [US1] Implement version resolver (latest `active`, or pinned) in `src/tokenhelm_prompt/registry/resolver.py`
- [X] T015 [P] [US1] Implement `YamlRegistry` backend (offline default) in `src/tokenhelm_prompt/registry/yaml_registry.py`
- [X] T016 [P] [US1] Implement `SqliteRegistry` backend in `src/tokenhelm_prompt/registry/sqlite_registry.py`
- [X] T017 [US1] Implement CLI `tokenhelm prompt init` in `src/tokenhelm_prompt/cli/main.py`
- [X] T018 [US1] Implement CLI `tokenhelm prompt list` and `tokenhelm prompt versions <name>` in `src/tokenhelm_prompt/cli/main.py` (depends on T017)
- [X] T019 [US1] Implement CLI `tokenhelm prompt diff <name> <vA> <vB>` using stored hashes only (no prompt text) in `src/tokenhelm_prompt/cli/main.py` (depends on T017)

**Checkpoint**: US1 fully functional and independently testable — MVP candidate.

---

## Phase 4: User Story 2 - Automatic Attribution via Prompt Scopes (Priority: P1)

**Goal**: Every tracked LLM call inside a scope is auto-attributed; calls outside
any scope are unchanged.

**Independent Test**: Event inside a scope carries prompt name/version; event
outside carries none and matches pre-feature behavior.

**Dependency**: Foundational (Phase 2); resolves prompts via US1 registry.

### Tests for User Story 2 ⚠️

- [X] T020 [P] [US2] Integration test: in-scope event has `prompt_name`/`prompt_version`, out-of-scope event has none, in `tests/integration/test_attribution.py`
- [X] T021 [P] [US2] Unit tests for unregistered-name indicator and no-scope passthrough in `tests/unit/test_tracker.py`

### Implementation for User Story 2

- [X] T022 [US2] Implement `PromptContext` — `contextvars.ContextVar` active-prompt stack with token-based restore in `src/tokenhelm_prompt/context/prompt_context.py`
- [X] T023 [US2] Implement `PromptTracker` (`prompt()` context manager, `set_prompt()`, `clear_prompt()`, `current_prompt()`) in `src/tokenhelm_prompt/tracking/tracker.py` (depends on T022)
- [X] T024 [P] [US2] Implement `@prompt(...)` decorator form in `src/tokenhelm_prompt/tracking/decorators.py`
- [X] T025 [US2] Implement `EventDispatcher` enrichment hook that attaches active-prompt metadata **before** dispatch in `src/tokenhelm_prompt/tracking/enrichment.py` (depends on T023)
- [X] T026 [US2] Register the enrichment hook via the TokenHelm `EventDispatcher` extension point (no core changes) in `src/tokenhelm_prompt/tracking/__init__.py` (depends on T025)

**Checkpoint**: US1 + US2 both work independently; attribution is live.

---

## Phase 5: User Story 3 - Nested & Concurrent Contexts (Priority: P2)

**Goal**: Correct innermost-wins attribution and exact restore across nesting,
async tasks, and streaming.

**Independent Test**: Inner/outer scopes attribute correctly and restore; async
and streaming calls show no cross-task leakage.

**Dependency**: US2 (`PromptContext`).

### Tests for User Story 3 ⚠️

- [X] T027 [P] [US3] Concurrency tests for async task isolation in `tests/concurrency/test_async_isolation.py`
- [X] T028 [P] [US3] Streaming attribution tests across generators in `tests/streaming/test_streaming.py`
- [X] T029 [P] [US3] Unit tests for nested restore order and exception-safe reset in `tests/unit/test_nested_context.py`

### Implementation for User Story 3

- [X] T030 [US3] Harden `PromptContext` for nested restore + exception-safe `reset(token)` and verify async/streaming propagation in `src/tokenhelm_prompt/context/prompt_context.py`

**Checkpoint**: Attribution correct under nesting, async, and streaming.

---

## Phase 6: User Story 4 - Privacy-Safe Prompt Metadata (Priority: P2)

**Goal**: Attribution captures only metadata + hashes — never rendered text,
secrets, or PII.

**Independent Test**: Inspect every stored record for a secret-bearing template →
metadata and hashes only.

**Dependency**: US2 (enrichment), Foundational hashing (T008).

### Tests for User Story 4 ⚠️

- [X] T031 [P] [US4] Privacy integration test: stored records contain only metadata + `template_hash`/`variable_hash` (no text/keys/PII) in `tests/integration/test_privacy.py`
- [X] T032 [P] [US4] Unit test confirming `variable_hash` hashes variable names, not values, in `tests/unit/test_hashing.py`

### Implementation for User Story 4

- [X] T033 [US4] Populate `PromptMetadata` with `template_hash` + `variable_hash` at enrichment time and assert no rendered text is ever attached, in `src/tokenhelm_prompt/tracking/enrichment.py`

**Checkpoint**: Privacy guarantee (SC-006) enforced by tests.

---

## Phase 7: User Story 5 - Per-Prompt Analytics (Priority: P3)

**Goal**: Aggregate attributed events per prompt and per version; export CSV/JSON.

**Independent Test**: Aggregates reconcile exactly with underlying events; export
produces CSV and JSON.

**Dependency**: US2 (attributed events exist).

### Tests for User Story 5 ⚠️

- [X] T034 [P] [US5] Analytics integration test: `by_prompt`/`by_version` reconcile with events in `tests/integration/test_analytics.py`
- [X] T035 [P] [US5] Unit tests for empty-result and failure-count edge cases in `tests/unit/test_analytics_edge.py`

### Implementation for User Story 5

- [X] T036 [P] [US5] Implement aggregation `by_prompt()`/`by_version()`/`cost()`/`calls()` in `src/tokenhelm_prompt/analytics/aggregate.py`, deriving the `failures` metric as the count of events with `status == error`
- [X] T037 [P] [US5] Implement CSV + JSON export in `src/tokenhelm_prompt/analytics/export.py`
- [X] T038 [US5] Implement CLI `tokenhelm prompt export [--format csv|json] [--output PATH]` in `src/tokenhelm_prompt/cli/main.py` (depends on T036, T037)

**Checkpoint**: All five user stories independently functional.

---

## Phase 8: Optional Framework Integrations (Cross-Cutting)

**Purpose**: Lazily-imported extras that open a prompt scope around framework
calls. Each is independent and must not be imported by the core (Constitution III).

- [X] T039 [P] Implement LangChain callback in `src/tokenhelm_prompt/integrations/langchain.py`
- [X] T040 [P] Implement LlamaIndex callback in `src/tokenhelm_prompt/integrations/llamaindex.py`
- [X] T041 [P] Implement CrewAI hook in `src/tokenhelm_prompt/integrations/crewai.py`
- [X] T042 [P] Implement Google ADK middleware in `src/tokenhelm_prompt/integrations/google_adk.py`
- [X] T043 [P] Implement OpenAI Agents middleware in `src/tokenhelm_prompt/integrations/openai_agents.py`
- [X] T044 [P] Implement Haystack callback in `src/tokenhelm_prompt/integrations/haystack.py` (Constitution III enumerates Haystack as an optional integration)
- [X] T045 [P] Lazy-import guard test: importing `tokenhelm_prompt` core succeeds with no framework SDKs installed, in `tests/unit/test_lazy_imports.py`

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Performance, compatibility, coverage, docs, and release.

- [X] T046 [P] Benchmark asserting ≤1 ms attribution overhead per call (SC-004) in `tests/benchmark/test_overhead.py`
- [X] T047 [P] Memory probe asserting ≤2 MB additional footprint when enabled (SC-005), measured as the peak `tracemalloc` delta between a baseline run and an attribution-enabled run with a small fixed tolerance, in `tests/benchmark/test_memory.py`
- [X] T048 [P] Backward-compatibility test: with the package installed but no scope, events are byte-for-byte equivalent (SC-002) in `tests/integration/test_backcompat.py`
- [X] T049 Verify ≥95% coverage gate and close any gaps (`pytest --cov`) (SC-009)
- [X] T050 [P] Author docs (Quick Start, API Reference, Architecture, Examples, Migration Guide) in `docs/`
- [X] T051 [P] Add GitHub Actions CI + PyPI trusted-publishing release workflow for `tokenhelm-prompt` in `.github/workflows/release.yml`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (P1)** → no dependencies.
- **Foundational (P2)** → depends on Setup; BLOCKS all user stories.
- **US1 (P3)** → depends on Foundational only. Independently shippable (MVP).
- **US2 (P4)** → depends on Foundational; resolves names via US1 registry.
- **US3 (P5)**, **US4 (P6)**, **US5 (P7)** → each depends on US2.
- **Integrations (P8)** → depend on US2.
- **Polish (P9)** → depends on the stories being polished.

### User Story Completion Order

```
Foundational ──> US1 (registry, MVP)
            └──> US2 (attribution) ──> US3 (nesting/concurrency)
                                  ├──> US4 (privacy)
                                  ├──> US5 (analytics)
                                  └──> Integrations
```

US3, US4, US5, and Integrations are mutually independent once US2 is done and can
proceed in parallel.

### Parallel Opportunities

- Setup: T003 in parallel with packaging review.
- Foundational: T004–T008 and T010 are all `[P]` (separate model/util files); T009 waits on the models.
- US1: tests T011–T013 `[P]`; backends/resolver T014–T016 `[P]`; CLI T017→T018/T019 sequential (same file).
- US2: T020/T021 `[P]`; T024 `[P]`; context/tracker/enrichment T022→T023→T025→T026 sequential.
- After US2: entire US3, US4, US5, and Integration phases can run concurrently across developers.
- Integrations: T039–T044 all `[P]` (separate modules); T045 guard test `[P]`.
- Polish: T046–T048, T050, T051 all `[P]`.

---

## Implementation Strategy

### MVP First

1. Phase 1 Setup → Phase 2 Foundational.
2. Phase 3 (US1) → **STOP and validate**: a working offline prompt registry with
   versioning and CLI. Demoable on its own.

### Incremental Delivery

1. Add US2 → automatic attribution on real calls (the headline value). Demo.
2. Add US3 → correctness under nesting/async/streaming.
3. Add US4 → privacy guarantee enforced.
4. Add US5 → analytics + export.
5. Add Integrations → framework auto-attribution.
6. Polish → perf/compat/coverage/docs/release.

### Parallel Team Strategy

After Foundational + US2 land, assign US3, US4, US5, and Integrations to separate
developers; they integrate independently because all attribution flows through the
single `contextvars`-based context.

---

## Notes

- `[P]` = different files, no incomplete-task dependency.
- All CLI subcommands share `src/tokenhelm_prompt/cli/main.py`, so they are
  sequential within a story even though they serve different commands.
- Tests are written before implementation within each story (spec mandates
  coverage and the acceptance scenarios are the test oracle).
- No task changes the TokenHelm core API (Constitution I & X).
