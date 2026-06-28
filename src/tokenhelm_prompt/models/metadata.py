"""The :class:`PromptMetadata` bundle attached to an event at enrichment time.

Immutable and metadata-only: it carries identity + one-way hashes, never the
rendered prompt, variable values, keys, credentials, or PII (Constitution VII).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptMetadata:
    """The immutable attribution bundle for the active prompt.

    ``registered`` is ``False`` when a scope references a name that is not in the
    registry; attribution is still recorded (with an ``unregistered`` indicator)
    rather than failing the call.
    """

    prompt_name: str
    prompt_id: str | None = None
    prompt_version: str | None = None
    owner: str | None = None
    application: str | None = None
    environment: str | None = None
    template_hash: str | None = None
    variable_hash: str | None = None
    registered: bool = True
