# Feature Specification: Prompt Intelligence

**Feature Branch**: `001-prompt-intelligence`

**Created**: 2026-06-28

**Status**: Draft

**Input**: User description: "Provide prompt attribution, versioning, analytics, and governance for every LLM request tracked by TokenHelm."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register and Version Prompt Templates (Priority: P1)

As a developer, I want to register prompt templates and evolve them over time so
that every LLM request can be attributed to a known, versioned prompt.

**Why this priority**: Identity is the foundation of the whole feature. Without a
registry of versioned prompts, there is nothing to attribute events to. This is
the smallest slice that delivers standalone value (a managed catalog of prompts).

**Independent Test**: Register a prompt, list it, retrieve it, update it to
produce a new version, and delete it — all without making any LLM call.

**Acceptance Scenarios**:

1. **Given** an empty registry, **When** a developer registers a prompt with a
   name and metadata, **Then** the prompt is stored with an initial version and
   can be retrieved by name.
2. **Given** an existing prompt, **When** the developer changes its template,
   **Then** a new immutable version is created and the prior version remains
   retrievable.
3. **Given** a populated registry, **When** the developer lists prompts, **Then**
   all registered prompts and their current versions are returned.
4. **Given** an existing prompt, **When** the developer deletes it, **Then** it no
   longer appears in listings.

---

### User Story 2 - Automatic Attribution via Prompt Scopes (Priority: P1)

As a developer, I want to open a prompt scope so that every LLM call made inside
that scope is automatically attributed to the prompt, with no per-call wiring.

**Why this priority**: This is the headline value — zero-effort attribution. It
turns the registry from a passive catalog into live telemetry on real traffic.

**Independent Test**: Enter a prompt scope, make a tracked LLM call inside it, and
confirm the emitted event carries the prompt name and version; confirm a call
made outside any scope carries no prompt attribution.

**Acceptance Scenarios**:

1. **Given** an active prompt scope, **When** a tracked LLM call completes,
   **Then** the resulting event includes the prompt name and prompt version.
2. **Given** no active scope, **When** a tracked LLM call completes, **Then** the
   event contains no prompt attribution and behaves exactly as before this
   feature existed.
3. **Given** an active prompt scope, **When** the scope exits, **Then** subsequent
   calls are no longer attributed to that prompt.

---

### User Story 3 - Nested Prompt Contexts (Priority: P2)

As a developer, I want to nest prompt scopes so that composing prompt-driven
steps attributes each call to the innermost active prompt and restores the outer
prompt automatically when the inner step ends.

**Why this priority**: Real workflows compose prompts (e.g. summarize → translate).
Correct nesting prevents misattribution, but the feature is still valuable with
only single scopes, so this builds on P1 rather than blocking it.

**Independent Test**: Enter an outer scope, then an inner scope, make a call in
each, and confirm each event is attributed to the correct prompt and that the
outer attribution is restored after the inner scope exits.

**Acceptance Scenarios**:

1. **Given** an outer scope is active, **When** an inner scope is entered and a
   call is made, **Then** the event is attributed to the inner prompt.
2. **Given** an inner scope has exited, **When** a further call is made, **Then**
   it is attributed to the outer prompt that was previously active.
3. **Given** attribution is active, **When** calls run across asynchronous and
   streaming execution, **Then** each call is attributed to the prompt that was
   active where the call originated, with no leakage between concurrent tasks.

---

### User Story 4 - Privacy-Safe Prompt Metadata (Priority: P2)

As a security-conscious developer, I want attribution to capture only prompt
metadata and hashes — never the rendered prompt or sensitive values — so that
observability never becomes a data-leak liability.

**Why this priority**: Privacy is non-negotiable per the project constitution, but
it constrains how attribution data is stored rather than being a standalone user
journey; it rides on P1/P2.

**Independent Test**: Trigger attribution for a prompt whose template contains a
placeholder for a secret, then inspect every stored record and confirm it
contains metadata and hashes only — no rendered text, keys, credentials, or PII.

**Acceptance Scenarios**:

1. **Given** a prompt is attributed to an event, **When** the record is stored,
   **Then** it contains the prompt name, version, owner, application, environment,
   template hash, and variable hash.
2. **Given** a prompt template containing variables, **When** the record is
   stored, **Then** no rendered prompt text, API keys, credentials, or PII are
   present anywhere in the stored data.

---

### User Story 5 - Per-Prompt Analytics (Priority: P3)

As a developer or operator, I want analytics aggregated per prompt and per
version so I can see call volume, latency, token usage, cost, and failures for
each prompt and export the results.

**Why this priority**: Analytics are the payoff of attribution, but they depend on
attributed events already flowing, so they come after P1/P2 are in place.

**Independent Test**: With a set of attributed events present, request analytics
grouped by prompt and by version, verify the aggregates match the underlying
events, and export the results to a file.

**Acceptance Scenarios**:

1. **Given** attributed events exist, **When** analytics are requested by prompt,
   **Then** call count, total/aggregate latency, token usage, cost, and failure
   count are returned per prompt.
2. **Given** attributed events exist, **When** analytics are requested by version,
   **Then** the same metrics are returned broken down per prompt version.
3. **Given** an analytics result, **When** the developer exports it, **Then** the
   data is produced in a portable tabular format and a structured format suitable
   for downstream tooling.

---

### Edge Cases

- What happens when a prompt scope references a prompt name that is not in the
  registry? Attribution records the name with an "unregistered" indicator rather
  than failing the LLM call.
- How does the system handle an LLM call that fails or raises inside an active
  scope? The failure is attributed to the active prompt and counted in its
  failure metric; the scope still restores correctly on exit.
- What happens when scopes are entered and exited out of order, or a scope is
  abandoned due to an exception? Context restoration must still return to the
  exact prior state.
- How does attribution behave across concurrent asynchronous tasks sharing the
  same process? Each task sees only its own active prompt; no cross-task leakage.
- What happens when analytics are requested but no attributed events exist yet?
  An empty but well-formed result is returned, not an error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow registering a prompt template with identifying
  metadata.
- **FR-002**: System MUST create a new immutable version when a registered prompt
  is changed, preserving all prior versions.
- **FR-003**: System MUST support a local, file-based registry format that works
  without network access.
- **FR-004**: System MUST support a local embedded-database registry as an
  alternative backend.
- **FR-005**: System MUST allow custom registry backends to be supplied without
  changes to the core.
- **FR-006**: System MUST propagate the active prompt across the execution flow,
  including asynchronous and streaming calls, without per-call wiring.
- **FR-007**: System MUST support nested prompt scopes, restoring the previously
  active prompt when an inner scope exits.
- **FR-008**: System MUST provide a decorator form of prompt attribution in
  addition to scope/context-manager form.
- **FR-009**: System MUST automatically attach the active prompt's name and
  version to every tracked LLM event produced inside a scope.
- **FR-010**: System MUST provide an analytics capability that aggregates metrics
  per prompt and per version.
- **FR-011**: System MUST export analytics in a portable tabular format.
- **FR-012**: System MUST export analytics in a structured machine-readable
  format.
- **FR-013**: System MUST provide a command-line interface to initialize a
  registry and to list prompts, list versions, export analytics, and compare
  (diff) prompt versions.
- **FR-014**: System MUST offer optional integrations with common LLM frameworks
  and agent toolkits, none of which are required for core operation.
- **FR-015**: System MUST remain fully backward compatible with the existing
  TokenHelm public API; no existing API may change.
- **FR-016**: System MUST store only prompt metadata and hashes — never the
  rendered prompt, API keys, credentials, or PII.
- **FR-017**: Attribution MUST be additive: when no prompt scope is active,
  tracked events behave identically to TokenHelm without this feature.

### Key Entities *(include if feature involves data)*

- **Prompt**: A named, owned, versioned prompt template. Attributes: id, name,
  version, owner, application, environment, description, tags, created_at. Holds
  no rendered text.
- **Version**: An immutable revision of a prompt. Attributes: version, hash,
  created_by, created_at, status.
- **PromptEvent**: A tracked LLM event enriched with prompt attribution.
  Attributes: event_id, prompt_id, provider, model, tokens, latency, cost,
  timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of tracked LLM calls made inside an active prompt scope carry
  the correct prompt name and version.
- **SC-002**: 100% of tracked LLM calls made with no active scope carry no prompt
  attribution and are byte-for-byte equivalent to pre-feature behavior.
- **SC-003**: Nested and concurrent scopes restore the prior prompt correctly in
  100% of cases across synchronous, asynchronous, and streaming execution.
- **SC-004**: Adding prompt attribution to a call adds no more than 1 millisecond
  of overhead per call.
- **SC-005**: Enabling the feature adds no more than 2 MB of additional memory
  footprint.
- **SC-006**: 0% of stored attribution records contain rendered prompt text, API
  keys, credentials, or PII (verified by inspection of stored data).
- **SC-007**: Per-prompt and per-version analytics aggregates match the
  underlying attributed events exactly (call count, latency, token usage, cost,
  and failures reconcile with no discrepancy).
- **SC-008**: A developer can register a prompt and confirm attribution on a real
  call within 5 minutes of first use, with no changes to existing TokenHelm
  setup.
- **SC-009**: Automated test coverage of the feature is at least 95%.

## Assumptions

- "Governance" in the goal is satisfied by ownership/application/environment
  metadata plus immutable versioning; no separate approval-workflow system is in
  scope for this version.
- The runtime target is Python 3.11+ (the existing TokenHelm requirement);
  attribution relies on the standard context-propagation mechanism for that
  runtime.
- The default registry is local and offline; cloud-backed registries are out of
  scope for this version and are expected to arrive later as optional plugins.
- Cost figures come from TokenHelm's existing pricing/cost machinery; this feature
  aggregates them rather than computing prices itself.
- "Failures" are calls that raise or are reported as errored by TokenHelm's
  existing event pipeline.
- Concurrency safety covers in-process threads, async tasks, and streaming
  generators; multi-process or distributed attribution is out of scope.
