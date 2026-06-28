# Implementation Plan: Prompt Intelligence

**Branch**: `001-prompt-intelligence` | **Date**: 2026-06-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-prompt-intelligence/spec.md`

## Summary

Prompt Intelligence is an **additive** companion package (`tokenhelm-prompt`)
that gives every TokenHelm-tracked LLM request a versioned prompt identity,
automatic context-based attribution, privacy-safe metadata capture, and
per-prompt analytics — without changing a single line of the TokenHelm v0.1 core
API. The technical approach: a local-first prompt **registry** (YAML and SQLite
backends behind one interface), a `contextvars`-based **PromptContext** that
propagates the active prompt across sync/async/streaming code, a **PromptTracker**
that enriches `LLMEvent`s at the existing `EventDispatcher` seam *before*
dispatch, an **analytics** layer that aggregates the resulting `PromptEvent`s, and
a thin **CLI**. Optional framework integrations (LangChain, LlamaIndex, CrewAI,
Google ADK, OpenAI Agents, Haystack) ship as lazily-imported extras.

## Technical Context

**Language/Version**: Python 3.11+ (matches TokenHelm core; required for robust
`contextvars` + `asyncio` task-local propagation)

**Primary Dependencies**: TokenHelm core (peer dependency, unmodified); standard
library only for the core path (`contextvars`, `hashlib`, `sqlite3`, `csv`,
`json`, `dataclasses`); `PyYAML` for the YAML registry; `click` (or stdlib
`argparse`) for the CLI. Framework integrations are **optional extras**, never
imported at top level.

**Storage**: Local prompt registry — YAML file(s) for human-editable use; SQLite
for indexed/larger registries. Both offline by default. `PromptEvent` analytics
are derived from TokenHelm's existing event stream/storage; this feature adds no
mandatory new event store.

**Testing**: `pytest` with `pytest-asyncio` (async attribution), `pytest-cov`
(≥95% gate), and `pytest-benchmark` (the <1 ms attribution-overhead assertion).

**Target Platform**: Any platform running CPython 3.11+ (Linux/macOS/Windows);
library, not a service.

**Project Type**: Single Python library + CLI (installable as `tokenhelm-prompt`).

**Performance Goals**: Prompt attribution adds ≤1 ms overhead per tracked call
(SC-004); enabling the feature adds ≤2 MB resident memory (SC-005).

**Constraints**: Offline-capable by default; thread-safe, async-safe, and
streaming-safe attribution with no cross-task leakage; zero changes to the
TokenHelm public API; no rendered prompt text / secrets / PII ever persisted.

**Scale/Scope**: Registry sized for thousands of prompts × tens of versions;
analytics over the host application's event volume. Single-process attribution
(multi-process/distributed is out of scope for this version).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Confirm the plan complies with each principle (see `.specify/memory/constitution.md`):

- [x] **I. Core API Stability**: Plan adds a separate package; `TokenHelm`, `track()`, `trace()`, `track_stream()`, `configure()`, `LLMEvent` are untouched and not monkey-patched. Enrichment happens at the dispatcher seam, not by rewriting core.
- [x] **II. Plugin Architecture**: Integration is solely through `EventDispatcher` (enrichment hook) and, where persistence is needed, `StorageBackend`. New `PromptRegistry`/`PromptContext`/`PromptProvider`/`PromptTracker` compose with the core; none modify it.
- [x] **III. Framework Agnostic**: Core path is stdlib + PyYAML only. LangChain/LlamaIndex/CrewAI/ADK/OpenAI-Agents live under `integrations/` as optional extras with lazy imports; importing the core never imports them.
- [x] **IV. Prompt Identity**: `Prompt` is keyed by metadata (id, name, version, owner, application, environment, tags). No identity derives from prompt text.
- [x] **V. Prompt Context**: `PromptContext` is built on `contextvars.ContextVar` with token-based restore; verified for sync, async, and streaming in the test plan.
- [x] **VI. Immutable Events**: The tracker attaches prompt metadata to the event *before* `EventDispatcher` dispatch; after dispatch events are treated as read-only.
- [x] **VII. Privacy**: Only metadata + `template_hash`/`variable_hash` are stored. Hashing is one-way; rendered prompts, keys, credentials, and PII are never written. Enforced by a stored-record privacy test (SC-006).
- [x] **VIII. Versioning**: A `Version` is immutable; any template change creates a new version. The registry never mutates an existing version in place.
- [x] **IX. Offline First**: Default registry (YAML/SQLite) is local and needs no network. Cloud registries are explicitly out of scope / future optional plugins.
- [x] **X. Zero Breaking Changes**: Everything is additive in a separate distribution; with no active scope, tracked events are byte-for-byte equivalent to pre-feature behavior (SC-002).

**Result**: PASS — no violations. Complexity Tracking table intentionally left empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-prompt-intelligence/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   ├── registry.md
│   ├── tracker.md
│   ├── analytics.md
│   └── cli.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/tokenhelm_prompt/
├── __init__.py              # Public exports; no heavy/optional imports
├── models/                  # Prompt, Version, PromptEvent, PromptMetadata (dataclasses)
├── lib/
│   └── hashing.py           # template_hash + variable_hash (one-way)
├── registry/
│   ├── base.py              # PromptRegistry interface (CRUD + version resolve)
│   ├── yaml_registry.py     # Offline YAML backend (default)
│   ├── sqlite_registry.py   # Local SQLite backend
│   └── resolver.py          # Version resolution (latest/pinned/status)
├── context/
│   └── prompt_context.py    # contextvars-based active-prompt stack + restore
├── tracking/
│   ├── tracker.py           # PromptTracker: prompt()/set_prompt()/clear_prompt()/current_prompt()
│   ├── decorators.py        # @prompt(...) decorator form
│   └── enrichment.py        # EventDispatcher hook: attach metadata pre-dispatch
├── analytics/
│   ├── aggregate.py         # by_prompt(), by_version(), cost(), calls()
│   └── export.py            # CSV + JSON export
├── integrations/            # ALL optional, lazy-imported
│   ├── langchain.py
│   ├── llamaindex.py
│   ├── crewai.py
│   ├── google_adk.py
│   ├── openai_agents.py
│   └── haystack.py
└── cli/
    └── main.py              # tokenhelm prompt {init,list,versions,export,diff}

tests/
├── unit/                    # models, registry, context, hashing, analytics
├── integration/             # end-to-end attribution through TokenHelm dispatcher
├── concurrency/             # threads + async task isolation
├── streaming/               # streaming attribution correctness
└── benchmark/               # <1 ms overhead, <2 MB memory assertions
```

**Structure Decision**: Single installable Python library (`src/` layout) plus a
CLI entry point, distributed as `tokenhelm-prompt`. This matches Constitution
Principles I–III: a separate distribution that depends on TokenHelm as an
unmodified peer, keeps the core import path free of optional framework SDKs, and
isolates each integration in its own lazily-imported module.

## Complexity Tracking

> No constitution violations. Table intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
