# Phase 1 Data Model: Prompt Intelligence

All entities are metadata-only. No entity stores rendered prompt text, variable
values, API keys, credentials, or PII (Constitution VII, FR-016).

## Entity: Prompt

The registered identity of a prompt. Keyed by metadata, never by text
(Constitution IV).

| Field | Type | Notes |
|-------|------|-------|
| `id` | string (stable slug/UUID) | Primary key; immutable for the life of the prompt |
| `name` | string | Human-facing unique name within the registry |
| `version` | string | Current/latest version identifier (see Version) |
| `owner` | string | Responsible person/team |
| `application` | string | Owning application |
| `environment` | string | e.g. `dev` / `staging` / `prod` |
| `description` | string (optional) | Free text; no secrets |
| `tags` | list[string] | Free-form labels for grouping/filtering |
| `created_at` | datetime (UTC, ISO-8601) | Creation timestamp |

**Validation rules**
- `id`, `name`, `owner`, `application`, `environment` are required and non-empty.
- `name` is unique within a registry.
- `description` must not contain rendered template content (enforced by
  convention + privacy test; never auto-populated from a template).

**Relationships**
- One Prompt has one or more **Version**s (1..*).
- A Prompt's `version` field references its current active Version.

## Entity: Version

An immutable revision of a prompt (Constitution VIII, FR-002).

| Field | Type | Notes |
|-------|------|-------|
| `version` | string | Version identifier (e.g. semver or incrementing); unique per prompt |
| `hash` | string (SHA-256 hex) | `template_hash` — one-way hash of the template string |
| `created_by` | string | Author of this version |
| `created_at` | datetime (UTC, ISO-8601) | Creation timestamp |
| `status` | enum | `active` \| `deprecated` \| `archived` |

**Validation rules**
- A Version is **append-only**: once written it is never mutated. A template
  change creates a new Version.
- `(prompt_id, version)` is unique.
- `hash` is derived from the template string only; the template string itself is
  not persisted.

**State transitions**
- `active → deprecated → archived` (status only; the immutable content never
  changes). A prompt may have exactly one `active` version at a time; the resolver
  defaults to it.

## Entity: PromptEvent

A TokenHelm `LLMEvent` enriched with prompt attribution before dispatch
(Constitution VI). This feature reads/derives these; it does not own the core
event store.

| Field | Type | Notes |
|-------|------|-------|
| `event_id` | string | Correlates to the underlying TokenHelm event |
| `prompt_id` | string (nullable) | Active prompt at call time; null when no scope active |
| `provider` | string | LLM provider (from core event) |
| `model` | string | Model name (from core event) |
| `tokens` | int / struct | Token usage (from core event) |
| `latency` | float (milliseconds) | Call latency (from core event), normalized to milliseconds for analytics aggregation |
| `cost` | float | Cost from TokenHelm's existing pricing data (not recomputed) |
| `status` | enum | `success` \| `error` — call outcome, taken from the underlying TokenHelm event; the sole source for the analytics `failures` metric |
| `timestamp` | datetime (UTC, ISO-8601) | Event time |

Derived attribution attached at enrichment time also carries the resolved
`prompt_name` and `prompt_version` (from the active Prompt/Version) so analytics
can group without a registry round-trip.

**Validation rules**
- When a prompt scope is active, `prompt_id` (and resolved name/version) MUST be
  present (SC-001).
- When no scope is active, `prompt_id` is null and the event is otherwise
  identical to the pre-feature event (SC-002).
- `status` is read directly from the underlying TokenHelm event (a call that
  raises or is reported as errored is `error`; otherwise `success`). The analytics
  `failures` metric is defined as the count of events with `status == error`
  attributed to a given prompt/version (SC-007, Edge Cases).

**Relationships**
- Many PromptEvents reference one Prompt (via `prompt_id`) and one Version (via
  the resolved `prompt_version`). Unregistered names are recorded with an
  `unregistered` indicator rather than failing the call (Edge Cases).

## Derived/auxiliary structures (not persisted as entities)

- **PromptMetadata**: the immutable bundle attached to an event at enrichment
  time — `prompt_id`, `prompt_name`, `prompt_version`, `owner`, `application`,
  `environment`, `template_hash`, `variable_hash`. `variable_hash` is a one-way
  hash over sorted variable **names** only (never values).
- **Active-prompt stack**: in-memory only, held in a `contextvars.ContextVar`;
  never persisted.

## Aggregates (analytics, computed not stored)

- **By-prompt aggregate**: `{ prompt_id, calls, total_latency, tokens, cost,
  failures }`.
- **By-version aggregate**: same metrics keyed by `(prompt_id, version)`.

These reconcile exactly with the underlying PromptEvents (SC-007).
