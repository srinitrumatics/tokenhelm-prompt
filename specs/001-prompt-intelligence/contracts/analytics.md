# Contract: Analytics

Aggregates attributed `PromptEvent`s into per-prompt and per-version metrics and
exports them. Cost values come from TokenHelm's existing pricing data; analytics
aggregates rather than recomputes them (FR-010, SC-007).

## Operations

### `by_prompt() -> list[Aggregate]`
Metrics grouped by prompt: `calls`, `latency` (milliseconds), `tokens`, `cost`,
`failures` (count of events with `status == error`).

### `by_version() -> list[Aggregate]`
Same metrics grouped by `(prompt, version)`.

### `cost(...) -> number`
Total/aggregated cost across the selected scope (prompt, version, or all).

### `calls(...) -> int`
Total call count across the selected scope.

### `export(format, path) -> None`
Write the current analytics result.
- `format="csv"` → portable tabular output (FR-011).
- `format="json"` → structured machine-readable output (FR-012).

## Guarantees
- Aggregates reconcile exactly with the underlying events — call count, latency,
  token usage, cost, and failures match with no discrepancy (SC-007).
- When no attributed events exist, operations return an empty but well-formed
  result, not an error (Edge Cases).
- A failed/errored call inside a scope is counted in that prompt's `failures`
  metric (Edge Cases).
