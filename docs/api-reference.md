# API Reference

All names below are importable from the top-level `tokenhelm_prompt` package.

## Tracking

### `tracker` (a `PromptTracker`)
- `tracker.use_registry(registry)` → bind a registry so scopes resolve full
  metadata (id, version, hashes). Returns the tracker.
- `tracker.prompt(name, version=None)` → context manager; attributes every
  tracked call inside it. Restores the prior prompt on exit (even on exception),
  and records a failure event if the block raises.
- `tracker.set_prompt(name, version=None)` → set the active prompt imperatively.
- `tracker.clear_prompt()` → clear the active prompt.
- `tracker.current_prompt()` → `PromptMetadata | None`.

### `prompt(name, version=None)`
Decorator form bound to the default tracker. Works on sync and `async` functions.

### `make_dispatcher(inner=None, store=None)` → `PromptEnrichingDispatcher`
Wrap an inner `EventDispatcher`. Pass to `TokenHelm(dispatcher=...)`.

## Registry

`YamlRegistry(path)` / `SqliteRegistry(path)` (both implement `PromptRegistry`):

- `register(name, *, owner, application, environment, template, description="", tags=None, created_by=None, version=None)` → `Prompt`
- `get(name, version=None)` → `Prompt` (resolves latest active, or a pinned version)
- `list()` → `list[Prompt]`
- `delete(name)` → `None`
- `add_version(name, *, template, created_by=None, version=None, status=VersionStatus.ACTIVE)` → `Version`
- `versions(name)` → `list[Version]`

Custom backends subclass `PromptRegistry` (or reuse the engine in
`registry.base`). Errors: `PromptNotFoundError`, `PromptConflictError`,
`PromptValidationError` (all subclasses of `RegistryError`).

## Analytics

### `analytics` (an `Analytics`)
- `by_prompt()` → `list[Aggregate]`
- `by_version()` → `list[Aggregate]`
- `cost()` → `float`
- `calls()` → `int`
- `export(fmt, path)` → write `"csv"` or `"json"`

`Aggregate` fields: `key`, `prompt_name`, `prompt_version`, `calls`,
`latency` (ms), `tokens`, `cost`, `failures`.

## Models

- `Prompt` — id, name, version, owner, application, environment, description,
  tags, created_at.
- `Version` (frozen) — version, hash, created_by, created_at, status.
- `VersionStatus` — `active` / `deprecated` / `archived`.
- `PromptEvent` (frozen) — event_id, prompt_id, prompt_name, prompt_version,
  provider, model, tokens, latency, cost, `status`, timestamp.
- `EventStatus` — `success` / `error`.
- `PromptMetadata` (frozen) — prompt_name, prompt_id, prompt_version, owner,
  application, environment, template_hash, variable_hash, registered.

## Integrations (optional, lazy)

`tokenhelm_prompt.integrations.<name>` for `langchain`, `llamaindex`, `crewai`,
`google_adk`, `openai_agents`, `haystack`. Each exposes a factory (e.g.
`make_callback`, `make_handler`, `prompt_scope`, `instrument`) that imports its
SDK only when called.
