# Contract: CLI

Command group `tokenhelm prompt` manages the registry and analytics from the
shell (FR-013). All commands operate on the local registry and work offline
(Constitution IX).

## Commands

### `tokenhelm prompt init`
Initialize a new local prompt registry (creates the YAML or SQLite store).
- **Output**: confirmation + path of the created registry.
- **Errors**: registry already exists → non-zero exit with message (no overwrite).

### `tokenhelm prompt list`
List all registered prompts with their current versions, owners, and
applications.

### `tokenhelm prompt versions <name>`
List all immutable versions of a prompt with `status`, `created_by`, `created_at`,
and `hash`.
- **Errors**: unknown name → non-zero exit.

### `tokenhelm prompt export [--format csv|json] [--output PATH]`
Export per-prompt / per-version analytics (delegates to the analytics contract).
- Default format `csv`; `json` supported.

### `tokenhelm prompt diff <name> <versionA> <versionB>`
Compare two versions of a prompt using their stored `template_hash`/`variable_hash`
(and metadata) — reports whether they differ, **without** revealing prompt text
(Constitution VII).
- **Errors**: unknown name or version → non-zero exit.

## Conventions
- Non-zero exit code on any error; human-readable message to stderr.
- No command prints rendered prompt text, variable values, or secrets.
