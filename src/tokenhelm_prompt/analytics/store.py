"""In-memory store of attributed :class:`PromptEvent` records.

This is the source of truth analytics aggregate over. It is process-local and
holds only metadata + hashes (never prompt text), consistent with Constitution
VII. A module-level :data:`default_store` is shared by the tracker and the
enriching dispatcher.
"""

from __future__ import annotations

import threading

from tokenhelm_prompt.models import PromptEvent


class PromptEventStore:
    """Thread-safe append-only collection of attributed events."""

    def __init__(self) -> None:
        self._events: list[PromptEvent] = []
        self._lock = threading.Lock()

    def add(self, event: PromptEvent) -> None:
        with self._lock:
            self._events.append(event)

    def all(self) -> list[PromptEvent]:
        with self._lock:
            return list(self._events)

    def clear(self) -> None:
        with self._lock:
            self._events.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._events)


default_store = PromptEventStore()
