<!--
SYNC IMPACT REPORT
==================
Version change: (none / template) → 1.0.0
Bump rationale: Initial ratification of the project constitution (MAJOR baseline).

Modified principles: N/A (initial adoption)
Added principles (10 total, replacing the 5-slot template):
  - I.    Core API Stability
  - II.   Plugin Architecture
  - III.  Framework Agnostic
  - IV.   Prompt Identity
  - V.    Prompt Context
  - VI.   Immutable Events
  - VII.  Privacy
  - VIII. Versioning
  - IX.   Offline First
  - X.    Zero Breaking Changes
Added sections:
  - Vision
  - Additional Constraints (derived from privacy + offline principles)
  - Development Workflow & Quality Gates
Removed sections: None (template placeholder slots fully replaced)

Templates requiring updates:
  ✅ .specify/templates/plan-template.md  — Constitution Check gate filled with principle gates
  ✅ .specify/templates/spec-template.md  — reviewed; no change needed (tech-agnostic, compatible)
  ✅ .specify/templates/tasks-template.md — reviewed; no change needed (principle-driven task types fit existing phases)
  ✅ CLAUDE.md                            — reviewed; no change needed (workflow guidance unaffected)

Follow-up TODOs: None. Ratification date set to adoption date 2026-06-28.
-->

# TokenHelm Prompt Intelligence Constitution

## Vision

TokenHelm Prompt Intelligence extends TokenHelm by adding prompt awareness,
attribution, versioning, governance, and analytics while preserving the
simplicity and stability of the TokenHelm core SDK.

Prompt Intelligence MUST remain an additive extension. The TokenHelm v0.1 API is
immutable.

## Core Principles

### I. Core API Stability

The following public APIs MUST NOT change in signature, semantics, or behavior:
`TokenHelm`, `track()`, `trace()`, `track_stream()`, `configure()`, and
`LLMEvent`. Prompt Intelligence only enriches events; it MUST NOT replace,
wrap-to-replace, or monkey-patch core functionality.

**Rationale**: Existing TokenHelm users depend on these surfaces. Stability here
is the precondition for every other principle — additive value is worthless if
it breaks the foundation.

### II. Plugin Architecture

Prompt Intelligence MUST integrate exclusively through the existing TokenHelm
extension points: `BaseAdapter`, `PricingProvider`, `StorageBackend`, `Logger`,
and `EventDispatcher`. It introduces `PromptRegistry`, `PromptContext`,
`PromptProvider`, and `PromptTracker` as new components that compose with — and
MUST NOT modify — the existing architecture.

**Rationale**: Extension through defined seams keeps the core closed for
modification but open for extension, so Prompt Intelligence can evolve without
forking or destabilizing TokenHelm.

### III. Framework Agnostic

The library MUST NOT require any framework or provider SDK to function.
Integrations with OpenAI SDK, Anthropic SDK, Gemini SDK, Ollama, LangChain,
LlamaIndex, Haystack, CrewAI, Google ADK, and OpenAI Agents SDK MUST remain
optional extras, importable only when explicitly installed.

**Rationale**: A mandatory dependency on any one ecosystem would exclude users of
the others. Optionality keeps the core installable and testable in isolation.

### IV. Prompt Identity

Prompts MUST be identified by metadata, never by prompt text. Every prompt MUST
carry: Prompt ID, Name, Version, Owner, Application, Environment, and Tags.

**Rationale**: Text is mutable, large, and may contain secrets. Stable metadata
identity enables attribution and analytics without coupling to or exposing
prompt content.

### V. Prompt Context

Prompt attribution MUST use `contextvars`. Nested attribution scopes MUST restore
the previous context on exit. Attribution MUST work correctly across sync, async,
and streaming execution.

**Rationale**: `contextvars` is the only mechanism that propagates attribution
correctly through async and streaming code without leaking state between
concurrent tasks.

### VI. Immutable Events

Prompt metadata MUST be attached to an event before dispatch. After dispatch,
events MUST be treated as immutable.

**Rationale**: Mutating dispatched events creates race conditions and makes
analytics non-reproducible. A clear attach-then-freeze boundary keeps the event
stream a reliable record.

### VII. Privacy

Prompt templates may contain secrets. The system MUST NEVER store rendered
prompts, API keys, credentials, or PII. Only metadata and optional hashes may be
persisted.

**Rationale**: Storing prompt content turns an observability tool into a
liability. Metadata and hashes provide traceability without retaining sensitive
data.

### VIII. Versioning

Prompt versions MUST be immutable. Any change to a prompt MUST create a new
version rather than altering an existing one.

**Rationale**: Immutable versions make attribution and historical analytics
trustworthy — an event tagged with a version always refers to the exact prompt
that produced it.

### IX. Offline First

The default prompt registry MUST be local and function without network access.
Cloud registries MUST be optional plugins layered on top of the local default.

**Rationale**: Offline-first guarantees the library works in any environment and
keeps prompt data under the user's control by default.

### X. Zero Breaking Changes

Every release MUST remain backward compatible with TokenHelm core. Prompt
Intelligence is entirely additive.

**Rationale**: This is the binding promise that makes adoption safe — upgrading
must never force a consumer to change working code.

## Additional Constraints

- **Data minimization**: Persistence layers MUST default to storing only the
  metadata defined in Principle IV plus optional hashes; storing anything more
  requires explicit justification recorded in the relevant plan.
- **Optional dependencies**: Provider/framework integrations MUST be declared as
  optional extras and guarded by lazy imports so the core imports cleanly without
  them (Principle III).
- **Local default**: A working installation MUST behave correctly with no cloud
  configuration present (Principle IX).

## Development Workflow & Quality Gates

- **Constitution Check (planning gate)**: Every `/speckit-plan` MUST pass the
  Constitution Check before Phase 0 research and re-check it after Phase 1
  design. Plans that touch core APIs, persistence, attribution, or dependencies
  MUST demonstrate compliance with Principles I–X.
- **Additive review**: Any change to the public surface listed in Principle I is
  a constitution violation and MUST be rejected or escalated to an amendment.
- **Justification of complexity**: Deviations MUST be recorded in the plan's
  Complexity Tracking table with the simpler alternative that was rejected and
  why.

## Governance

This constitution supersedes other development practices for Prompt Intelligence.
All plans and reviews MUST verify compliance with the principles above.

**Amendment procedure**: Amendments MUST be proposed as a documented change to
this file, including rationale and, where a principle changes meaning, a
migration note. Approval MUST precede merge.

**Versioning policy**: This constitution is versioned with semantic versioning:
- **MAJOR**: Backward-incompatible governance changes, or removal/redefinition of
  a principle.
- **MINOR**: A new principle or section is added, or guidance is materially
  expanded.
- **PATCH**: Clarifications, wording, and non-semantic refinements.

**Compliance review**: Constitution compliance is reviewed at every planning gate
and before every release. A release that breaks backward compatibility with
TokenHelm core (Principle X) MUST NOT ship under this constitution.

**Version**: 1.0.0 | **Ratified**: 2026-06-28 | **Last Amended**: 2026-06-28
