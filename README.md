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

## Release process

Releases are staged through TestPyPI before production PyPI, driven entirely by
git tags. Publishing uses **PyPI Trusted Publishing (OIDC)** — there are no API
tokens anywhere.

```
RC tag  ──►  TestPyPI  ──►  install + smoke test  ──►  GitHub prerelease
final tag ─►  PyPI     ──►  install + smoke test  ──►  GitHub release
```

A tag is classified automatically: `vX.Y.Z` is a production release; anything
with a pre-release/dev suffix (`rc`, `a`, `b`, `.dev` — e.g. `v0.2.0rc1`) goes to
TestPyPI. The tag version must match `project.version` in `pyproject.toml` (the
workflow guards this), so bump the version first.

**1. Pre-release to TestPyPI:**

```bash
# bump pyproject.toml version to 0.2.0rc1 first, then:
git tag v0.2.0rc1
git push origin v0.2.0rc1
```

This builds, publishes to TestPyPI, installs into a clean venv from TestPyPI,
runs `scripts/release_smoke_test.py`, and cuts a GitHub **prerelease**.

**2. Production to PyPI:**

```bash
# bump pyproject.toml version to 0.2.0 first, then:
git tag v0.2.0
git push origin v0.2.0
```

This builds, publishes to PyPI, installs from PyPI into a clean venv, runs the
smoke test, and cuts the GitHub **release** with generated notes and the wheel +
sdist attached.

The workflow (`.github/workflows/release.yml`) also supports `workflow_dispatch`
for a build-and-check dry run (no publish). The `testpypi` and `pypi` GitHub
environments must each have a Trusted Publisher configured on the respective
index.

---

See [`docs/`](./docs/) for the architecture, full API reference, and a migration
guide. The design lives under
[`specs/001-prompt-intelligence/`](./specs/001-prompt-intelligence/).
