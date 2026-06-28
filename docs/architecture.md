# Architecture

`tokenhelm-prompt` is an **additive** companion to TokenHelm. It never modifies
the core; it composes with it at one seam.

## The seam

TokenHelm's `EventDispatcher` is a `Protocol` with a single method,
`dispatch(event) -> None`. `PromptEnrichingDispatcher` implements that protocol,
wraps an inner dispatcher, and:

1. reads the **active prompt** from the context stack,
2. builds an attributed `PromptEvent` (a *separate* record — the core `LLMEvent`
   is frozen and is never mutated),
3. appends it to the shared `PromptEventStore`, then
4. forwards the **original, unchanged** event to the inner dispatcher.

```
tracker.prompt("x")  ──pushes──►  contextvars stack
                                        │ current()
TokenHelm.track() ─► EventDispatcher ───┴─► PromptEnrichingDispatcher
                                              ├─ build PromptEvent ─► PromptEventStore ─► analytics
                                              └─ inner.dispatch(event)   # unchanged
```

## Components

| Component | Responsibility | Constitution |
|-----------|----------------|--------------|
| `context.PromptContext` | `contextvars` stack; nested + async/streaming safe | V |
| `tracking.PromptTracker` | `prompt()` scopes, decorator, set/clear/current, failure capture | V, VI |
| `tracking.PromptEnrichingDispatcher` | attribution at the dispatcher seam | II, VI, X |
| `registry.*` | versioned metadata store (YAML default, SQLite, custom) | VIII, IX |
| `lib.hashing` | `template_hash` + `variable_hash` (one-way) | VII |
| `analytics.*` | per-prompt/version aggregation + CSV/JSON export | — |
| `integrations.*` | optional, lazily-imported framework adapters | III |

## Why a separate `PromptEvent`

The core `LLMEvent` is a frozen dataclass with no attribution or status slot.
Rather than fight that (which would violate immutability), attribution is recorded
as a derived `PromptEvent`. Two consequences:

- **Success** events are recorded by the dispatcher.
- **Failure** events are recorded by `tracker.prompt()` when the scoped block
  raises (the core emits no event for a call that raises). `status` is the source
  of the analytics `failures` metric.

## State & lifetime

The active-prompt stack lives only in a `ContextVar` (never persisted). The
`PromptEventStore` is process-local (the design adds no mandatory new event
store). The registry is the only durable artifact, and it stores metadata +
hashes only.
