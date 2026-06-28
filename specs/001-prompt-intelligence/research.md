# Phase 0 Research: Prompt Intelligence

All Technical Context items were determined from the spec, the constitution, and
the user-supplied phased plan. No `NEEDS CLARIFICATION` markers remained; the
items below record the decisions and the alternatives weighed.

## R1. Active-prompt propagation mechanism

- **Decision**: Use `contextvars.ContextVar` holding an immutable stack of active
  prompts. `prompt()` sets a new value and keeps the returned `Token`;
  `__exit__`/`clear` calls `ContextVar.reset(token)` to restore the prior state.
- **Rationale**: `contextvars` is the only stdlib mechanism that propagates
  per-task state correctly across `asyncio` tasks and generators (streaming)
  without leaking between concurrent tasks — mandated by Constitution Principle V
  and SC-003. Token-based reset gives exact nested restore even on exceptions.
- **Alternatives considered**: `threading.local` (does not follow `await`
  boundaries; breaks async/streaming); explicit per-call arguments (violates the
  "no per-call wiring" goal of US2); a global stack with locks (leaks across
  concurrent async tasks).

## R2. Enrichment seam into TokenHelm

- **Decision**: Attach prompt metadata to the event at the `EventDispatcher`
  extension point, before the event is dispatched. The tracker registers an
  enrichment hook; it reads `current_prompt()` and writes prompt name/version onto
  the event.
- **Rationale**: Principle II requires integration only through existing extension
  points and Principle VI requires metadata be attached before dispatch and never
  after. The dispatcher is the last point where the event is still mutable.
- **Alternatives considered**: Subclassing/replacing `LLMEvent` (violates I);
  monkey-patching `track()` (violates I); a `Logger` post-processor (too late —
  event already dispatched, violates VI).

## R3. Registry backends

- **Decision**: One `PromptRegistry` interface with two bundled backends — YAML
  (default, human-editable, offline) and SQLite (indexed, larger registries).
  Custom backends register by implementing the interface.
- **Rationale**: Principle IX (offline-first local default) and FR-003/004/005.
  YAML is the friendliest default for small hand-curated registries; SQLite scales
  and supports fast version queries; the shared interface keeps both swappable and
  allows cloud backends later as optional plugins.
- **Alternatives considered**: JSON-only (less human-friendly than YAML for
  multi-line metadata); requiring a server/db (violates IX); a single hardcoded
  backend (violates FR-005 extensibility).

## R4. Privacy-safe template/variable capture

- **Decision**: Store `template_hash` and `variable_hash` (SHA-256 over the
  template string and over the sorted set of variable *names*, respectively).
  Never store rendered output or variable values.
- **Rationale**: Principle VII / FR-016 / SC-006. Hashing the template detects
  drift and powers `prompt diff` without retaining text; hashing variable *names*
  (not values) captures shape without capturing secrets/PII.
- **Alternatives considered**: Storing rendered prompts (direct privacy
  violation); storing variable values (may contain secrets/PII); no hash at all
  (loses drift detection and the `diff` capability in FR-013).

## R5. Immutable versioning model

- **Decision**: Each `Version` is append-only with a `status` field
  (e.g. `active`/`deprecated`/`archived`). Editing a prompt's template creates a
  new `Version`; existing versions are never rewritten. The resolver selects
  latest-active by default or a pinned version when specified.
- **Rationale**: Principle VIII and FR-002. Append-only versions make attribution
  reproducible — an event's `prompt_version` always points at the exact prompt
  that produced it.
- **Alternatives considered**: Mutable "current template" field (breaks
  reproducibility); git-style content addressing only (over-engineered for the
  metadata model and would tempt storing full text).

## R6. Optional framework integrations

- **Decision**: Each integration (LangChain callback, LlamaIndex callback, CrewAI
  hook, Google ADK middleware, OpenAI Agents middleware) lives in its own module
  under `integrations/`, imported lazily and gated behind install extras
  (e.g. `tokenhelm-prompt[langchain]`). Each simply opens a `PromptContext` around
  the framework's call so existing attribution applies.
- **Rationale**: Principle III / FR-014. Importing the core must never import a
  framework SDK; integrations are sugar over the same `contextvars` mechanism so
  no per-framework attribution logic diverges.
- **Alternatives considered**: A single integrations module importing all SDKs
  (forces heavy optional deps, violates III); bespoke attribution per framework
  (duplicates logic, risks divergence from the contextvars source of truth).

## R7. Analytics aggregation & export

- **Decision**: Aggregate over `PromptEvent`s grouped by prompt and by version,
  computing calls, latency, token usage, cost, and failures. Export to CSV
  (tabular) and JSON (structured). Cost is taken from TokenHelm's existing
  pricing/cost data, not recomputed.
- **Rationale**: FR-010/011/012, SC-007. Reusing TokenHelm's cost figures keeps a
  single source of truth and avoids drift; CSV+JSON covers spreadsheet and tooling
  consumers.
- **Alternatives considered**: Recomputing cost from a separate pricing table
  (drift risk, duplicates core responsibility); a single export format (fails
  either spreadsheet or programmatic consumers).

## R8. Performance validation approach

- **Decision**: Assert the ≤1 ms attribution overhead (SC-004) and ≤2 MB memory
  (SC-005) with `pytest-benchmark` and a memory probe in `tests/benchmark/`,
  comparing a tracked call with and without an active scope.
- **Rationale**: The constitution's quality gate and SC-004/005 are measurable;
  encoding them as tests makes regressions visible.
- **Alternatives considered**: Manual/ad-hoc timing (not repeatable); skipping the
  memory bound (would let the 2 MB budget regress silently).
