# tokenhelm-prompt

**Prompt Intelligence for [TokenHelm](https://pypi.org/project/tokenhelm/)** —
prompt attribution, versioning, analytics, and governance for every LLM request
TokenHelm tracks. Entirely additive: the TokenHelm v0.1 API is never changed.

## Install

```bash
pip install tokenhelm-prompt
# optional framework integrations:
pip install "tokenhelm-prompt[langchain]"   # or llamaindex, crewai, adk, openai-agents, haystack
```

## Quick start

```python
from tokenhelm import TokenHelm, DefaultEventDispatcher
from tokenhelm_prompt import YamlRegistry, tracker, analytics, make_dispatcher

# 1. Register a versioned prompt (metadata + a template HASH — never the text).
registry = YamlRegistry("prompts.yaml")
registry.register(
    "invoice_summary",
    owner="ana", application="billing", environment="prod",
    template="Summarize invoice {invoice_id} for {customer}",
)
tracker.use_registry(registry)

# 2. Wrap TokenHelm's dispatcher so events get attributed (no core changes).
th = TokenHelm(dispatcher=make_dispatcher(DefaultEventDispatcher()))

# 3. Every tracked call inside the scope is attributed automatically.
with tracker.prompt("invoice_summary"):
    th.track(response)            # event recorded as invoice_summary@v1

# 4. Per-prompt / per-version analytics.
for row in analytics.by_version():
    print(row.prompt_name, row.prompt_version, row.calls, row.cost, row.failures)
analytics.export("csv", "prompts.csv")
```

Nested scopes, the `@prompt(...)` decorator, and `async`/streaming all work and
restore correctly:

```python
from tokenhelm_prompt import prompt

@prompt("translate")
async def translate(...): ...

with tracker.prompt("invoice"):
    with tracker.prompt("translate"):   # inner wins; outer restored on exit
        ...
```

## CLI

```bash
tokenhelm-prompt init                       # create a local registry
tokenhelm-prompt list                       # list prompts + current versions
tokenhelm-prompt versions invoice_summary   # immutable version history
tokenhelm-prompt diff invoice_summary v1 v2 # compare by hash (never shows text)
tokenhelm-prompt export --format json -o inventory.json
```

## Guarantees

- **No core changes** — TokenHelm's `track/trace/track_stream/configure/LLMEvent`
  are untouched; integration is purely via the `EventDispatcher` seam.
- **Privacy** — only metadata + one-way hashes are stored; never rendered prompts,
  keys, credentials, or PII.
- **Offline-first** — the default YAML/SQLite registry needs no network.
- **Additive** — with no active scope, behavior is identical to plain TokenHelm.

See [`docs/`](./docs/) for the architecture, full API reference, and a migration
guide. The design lives under
[`specs/001-prompt-intelligence/`](./specs/001-prompt-intelligence/).
