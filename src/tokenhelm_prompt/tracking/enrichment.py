"""``PromptEnrichingDispatcher`` — attribution at the ``EventDispatcher`` seam.

TokenHelm's ``EventDispatcher`` is a ``Protocol`` with a single ``dispatch``
method. This wrapper reads the active prompt, builds an attributed
:class:`PromptEvent` *before* forwarding, and then delegates to the wrapped
dispatcher with the original event **unchanged** — satisfying Constitution II
(integrate via the extension point), VI (metadata attached before dispatch; core
event never mutated), and X (no behavioral change when no scope is active).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from tokenhelm_prompt import context
from tokenhelm_prompt.analytics.store import PromptEventStore, default_store
from tokenhelm_prompt.models import EventStatus, PromptEvent


def _to_ms(latency) -> float | None:
    """Normalize core latency (seconds) to milliseconds (data-model A1)."""
    if latency is None:
        return None
    return float(latency) * 1000.0


def _provider_str(provider) -> str | None:
    if provider is None:
        return None
    return getattr(provider, "value", None) or getattr(provider, "name", None) or str(provider)


class PromptEnrichingDispatcher:
    """Wraps an inner ``EventDispatcher`` and records attributed events.

    Conforms structurally to TokenHelm's ``EventDispatcher`` protocol (it exposes
    ``dispatch(event) -> None``), so it can be passed straight to
    ``TokenHelm(dispatcher=...)``.
    """

    def __init__(self, inner=None, store: PromptEventStore | None = None) -> None:
        self._inner = inner
        self._store = store or default_store

    def dispatch(self, event) -> None:
        meta = context.current()
        self._store.add(
            PromptEvent(
                event_id=uuid.uuid4().hex,
                prompt_id=getattr(meta, "prompt_id", None),
                prompt_name=getattr(meta, "prompt_name", None),
                prompt_version=getattr(meta, "prompt_version", None),
                provider=_provider_str(getattr(event, "provider", None)),
                model=getattr(event, "model", None),
                tokens=getattr(event, "total_tokens", None),
                latency=_to_ms(getattr(event, "latency", None)),
                cost=float(getattr(event, "cost", 0) or 0),
                status=EventStatus.SUCCESS,
                timestamp=getattr(event, "timestamp", None) or datetime.now(timezone.utc),
            )
        )
        # Forward the original, unmodified event to the wrapped dispatcher.
        if self._inner is not None:
            self._inner.dispatch(event)
