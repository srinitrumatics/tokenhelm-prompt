"""The :class:`PromptEvent` — a TokenHelm event enriched with prompt attribution.

TokenHelm's core ``LLMEvent`` is a frozen dataclass with no attribution slot, so
``PromptEvent`` is a *separate derived record*: the enriching dispatcher pairs the
active prompt with the event's metrics and forwards the original ``LLMEvent``
unchanged (Constitution VI immutability, X backward compatibility).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EventStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


@dataclass(frozen=True)
class PromptEvent:
    """An attributed, immutable record derived from a tracked LLM call.

    ``status`` is the sole source for the analytics ``failures`` metric:
    ``failures`` is the count of events with ``status == EventStatus.ERROR``.
    ``latency`` is normalized to milliseconds for aggregation.
    """

    event_id: str
    prompt_id: str | None
    prompt_name: str | None
    prompt_version: str | None
    provider: str | None
    model: str | None
    tokens: int | None
    latency: float | None
    cost: float
    status: EventStatus
    timestamp: datetime
