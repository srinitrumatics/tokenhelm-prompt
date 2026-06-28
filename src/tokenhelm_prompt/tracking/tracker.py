"""``PromptTracker`` — scope-based automatic attribution (US2, US3).

The tracker resolves a prompt's metadata (via an optional registry), pushes it
onto the context stack for the duration of a scope, and records a failure
``PromptEvent`` if the scoped block raises. Successful events are recorded by the
enriching dispatcher; failures are captured here because TokenHelm's core emits
no event for a call that raises (its ``LLMEvent`` carries no error status).
"""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator

from tokenhelm_prompt import context
from tokenhelm_prompt.analytics.store import PromptEventStore, default_store
from tokenhelm_prompt.models import EventStatus, PromptEvent, PromptMetadata


class PromptTracker:
    """Provides ``prompt()`` scopes plus imperative set/clear/current helpers."""

    def __init__(self, registry=None, store: PromptEventStore | None = None) -> None:
        self._registry = registry
        self._store = store or default_store

    def use_registry(self, registry) -> "PromptTracker":
        """Bind a registry so scopes resolve full metadata (id, version, hashes)."""
        self._registry = registry
        return self

    # ---- metadata resolution ------------------------------------------------
    def _build_meta(self, name: str, version: str | None) -> PromptMetadata:
        if self._registry is not None:
            try:
                fields = self._registry.metadata_for(name, version)
                return PromptMetadata(prompt_name=name, registered=True, **fields)
            except Exception:
                # Unknown name/version: attribute as unregistered, never fail the call.
                pass
        return PromptMetadata(
            prompt_name=name,
            prompt_version=version,
            registered=False,
        )

    # ---- scope --------------------------------------------------------------
    @contextmanager
    def prompt(self, name: str, version: str | None = None) -> Iterator[PromptMetadata]:
        """Context manager attributing every tracked call inside it to ``name``."""
        meta = self._build_meta(name, version)
        token = context.push(meta)
        try:
            yield meta
        except Exception:
            self._record_failure(meta)
            raise
        finally:
            context.reset(token)

    # ---- imperative helpers -------------------------------------------------
    def set_prompt(self, name: str, version: str | None = None) -> None:
        """Set the active prompt without a ``with`` block."""
        context.push(self._build_meta(name, version))

    def clear_prompt(self) -> None:
        """Clear the active prompt (restore the no-attribution state)."""
        context.clear()

    def current_prompt(self) -> PromptMetadata | None:
        """Return the active prompt metadata, or ``None`` when no scope is active."""
        return context.current()

    # ---- failure capture ----------------------------------------------------
    def _record_failure(self, meta: PromptMetadata) -> None:
        self._store.add(
            PromptEvent(
                event_id=uuid.uuid4().hex,
                prompt_id=meta.prompt_id,
                prompt_name=meta.prompt_name,
                prompt_version=meta.prompt_version,
                provider=None,
                model=None,
                tokens=None,
                latency=None,
                cost=0.0,
                status=EventStatus.ERROR,
                timestamp=datetime.now(timezone.utc),
            )
        )
