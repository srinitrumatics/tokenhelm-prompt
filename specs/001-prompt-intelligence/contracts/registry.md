# Contract: Prompt Registry

`PromptRegistry` is the interface for storing and resolving versioned prompt
metadata. Bundled backends: `YamlRegistry` (default, offline) and
`SqliteRegistry`. Custom backends implement this same interface (FR-005).

## Operations

### `register(prompt) -> Prompt`
Register a new prompt with its metadata. Creates the prompt and its initial
immutable `Version`.
- **Input**: prompt metadata (name, owner, application, environment, optional
  description/tags) + template (used only to compute `template_hash`; not stored).
- **Output**: the stored `Prompt` (with `id`, initial `version`, `created_at`).
- **Errors**: duplicate `name` in the registry → conflict error; missing required
  metadata → validation error.
- **Constitution**: IV (metadata identity), VII (template hashed, not stored).

### `get(name, version=None) -> Prompt`
Retrieve a prompt by name; resolves to the latest `active` version unless a
specific `version` is pinned.
- **Output**: the resolved `Prompt`/`Version`.
- **Errors**: unknown name → not-found; unknown pinned version → not-found.

### `list() -> list[Prompt]`
Return all registered prompts with their current versions.

### `delete(name) -> None`
Remove a prompt from listings.
- **Errors**: unknown name → not-found.
- **Note**: deletion removes the registry entry; it does not rewrite historical
  `PromptEvent`s (those are immutable).

### Version resolution (`resolver`)
- Default: latest version with `status == active`.
- Pinned: exact `version` string.
- A new `register`-with-changed-template or explicit version bump creates a new
  immutable `Version`; existing versions are never mutated (Constitution VIII).

## Invariants
- A `Version` is append-only; `(prompt_id, version)` is unique.
- No backend persists rendered prompt text, variable values, or secrets.
- The default backend operates fully offline (Constitution IX).
