# Quickstart & Validation: Prompt Intelligence

A run guide that proves the feature works end-to-end. It maps each scenario back
to the spec's success criteria. Implementation details live in `tasks.md` and the
code; this file is for validating behavior.

## Prerequisites

- Python 3.11+
- TokenHelm core installed (unmodified)
- This package installed: `pip install tokenhelm-prompt`
  - Optional integrations: `pip install "tokenhelm-prompt[langchain]"` (etc.)

## Setup

```bash
# Create a local, offline registry
tokenhelm prompt init
# Register a prompt (metadata only; template is hashed, not stored)
tokenhelm prompt list
```

## Scenario 1 — Registry & Versioning (US1)

1. Register a prompt, then list it → it appears with an initial version.
2. Update its template and re-register/bump → a new immutable version is created;
   `tokenhelm prompt versions <name>` shows both, old one still present.
3. Delete it → it no longer appears in `tokenhelm prompt list`.

**Expected**: CRUD works; prior versions remain retrievable (validates FR-001/002,
US1 acceptance).

## Scenario 2 — Automatic Attribution (US2, SC-001/002)

```python
from tokenhelm_prompt import tracker

with tracker.prompt("invoice_summary"):
    client.responses.create(...)        # tracked LLM call
```

**Expected**:
- The emitted event includes `prompt_name` and `prompt_version` (SC-001).
- A call made **outside** any scope has no prompt attribution and is identical to
  pre-feature behavior (SC-002).

## Scenario 3 — Nested & Concurrent Contexts (US3, SC-003)

```python
with tracker.prompt("invoice"):
    # call here → attributed to "invoice"
    with tracker.prompt("translate"):
        # call here → attributed to "translate"
        ...
    # call here → attributed to "invoice" again (restored)
```

**Expected**: inner scope wins; outer restored on exit; correct attribution across
`async` tasks and streaming generators with no cross-task leakage.

## Scenario 4 — Privacy (US4, SC-006)

1. Use a prompt whose template contains a placeholder for a secret.
2. Trigger attribution, then inspect every stored record.

**Expected**: records contain metadata + `template_hash` + `variable_hash` only —
no rendered text, API keys, credentials, or PII (validates FR-016).

## Scenario 5 — Analytics & Export (US5, SC-007)

```python
from tokenhelm_prompt import analytics
analytics.by_prompt()
analytics.by_version()
analytics.export("csv", "prompts.csv")
```

**Expected**: per-prompt and per-version aggregates (calls, latency, tokens, cost,
failures) reconcile exactly with the underlying events; CSV and JSON exports
produced.

## Performance validation (SC-004/005)

- `tests/benchmark/` asserts attribution adds ≤1 ms per call and ≤2 MB memory when
  enabled.

## Backward-compatibility check (Constitution X, SC-002)

- Run an existing TokenHelm program with this package installed but **no** prompt
  scopes → behavior and emitted events are unchanged.

## Reference

- Public API: [contracts/](./contracts/) (`registry.md`, `tracker.md`,
  `analytics.md`, `cli.md`)
- Entities: [data-model.md](./data-model.md)
