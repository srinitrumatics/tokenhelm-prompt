# Migration Guide

Prompt Intelligence is **additive**. Adopting it requires **no changes** to your
existing TokenHelm code, and removing it leaves behavior identical.

## From plain TokenHelm

Before:

```python
from tokenhelm import TokenHelm
th = TokenHelm()
th.track(response)
```

After (attribution enabled):

```python
from tokenhelm import TokenHelm, DefaultEventDispatcher
from tokenhelm_prompt import make_dispatcher, tracker, YamlRegistry

tracker.use_registry(YamlRegistry("prompts.yaml"))
th = TokenHelm(dispatcher=make_dispatcher(DefaultEventDispatcher()))

with tracker.prompt("my_prompt"):
    th.track(response)
```

The only change is wrapping the dispatcher and opening prompt scopes. Calls made
**outside** any scope behave exactly as before — same events, no attribution.

## Compatibility guarantees

- No TokenHelm public API changes: `TokenHelm`, `track`, `trace`, `track_stream`,
  `configure`, `LLMEvent` are untouched and never monkey-patched.
- Your existing dispatcher/loggers/storage keep working — `make_dispatcher`
  *wraps* them and forwards every event unchanged.
- Versions are immutable: existing registry entries are never rewritten by an
  upgrade.

## Removing the package

Drop the `dispatcher=` wrapper and the `with tracker.prompt(...)` blocks. Nothing
else depends on it; the registry file can be deleted. TokenHelm continues
unchanged.

## Notes

- The CLI ships as `tokenhelm-prompt` (it does not override any `tokenhelm`
  command).
- Live per-call analytics are process-local; export them via
  `analytics.export(...)`. The CLI `export` command exports the registry
  inventory.
