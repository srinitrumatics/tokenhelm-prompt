# Contract: Prompt Tracker & Context

`PromptTracker` provides scope-based, automatic attribution. It is backed by a
`contextvars`-based active-prompt stack (`PromptContext`) and enriches each
`LLMEvent` at the `EventDispatcher` seam before dispatch (Constitution V, VI).

## Operations

### `prompt(name, version=None) -> context manager`
Open a prompt scope. Every tracked LLM call made while the scope is active is
attributed to this prompt.
```python
with tracker.prompt("invoice_summary"):
    client.responses.create(...)   # event carries prompt_name + prompt_version
```
- **Behavior**: pushes the resolved prompt onto the context stack; on exit
  restores the previously active prompt (token-based reset), even on exception.
- **Nesting**: inner scope wins while active; outer is restored on inner exit
  (US3, SC-003).
- **Unregistered name**: recorded with an `unregistered` indicator; the LLM call
  is **not** failed (Edge Cases).

### `@prompt(name, version=None)` (decorator form — FR-008)
Equivalent to wrapping the decorated function body in `tracker.prompt(...)`.

### `set_prompt(name, version=None) -> None`
Imperatively set the active prompt without a `with` block.

### `clear_prompt() -> None`
Clear the active prompt (restores to no-attribution state).

### `current_prompt() -> PromptMetadata | None`
Return the currently active prompt metadata, or `None` when no scope is active.

## Attribution guarantees
- **Scope active** → event includes `prompt_name` and `prompt_version` (SC-001).
- **No scope** → event has no prompt attribution and is byte-for-byte identical to
  pre-feature behavior (SC-002, Constitution X).
- **Async / streaming** → attribution follows the originating task; no leakage
  between concurrent tasks (SC-003).
- Metadata is attached **before** dispatch; the event is immutable afterward
  (Constitution VI).
- Only metadata + `template_hash`/`variable_hash` are recorded — never rendered
  prompt text or values (Constitution VII).
