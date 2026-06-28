"""Per-prompt and per-version analytics over attributed events (US5).

Aggregates reconcile exactly with the underlying :class:`PromptEvent` records
(SC-007). ``failures`` is the count of events with ``status == EventStatus.ERROR``.
Cost comes from TokenHelm's pricing data carried on each event (not recomputed).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from tokenhelm_prompt.analytics.store import PromptEventStore, default_store
from tokenhelm_prompt.models import EventStatus, PromptEvent


@dataclass(frozen=True)
class Aggregate:
    """One analytics row."""

    key: str
    prompt_name: str | None
    prompt_version: str | None
    calls: int
    latency: float  # total latency in milliseconds
    tokens: int
    cost: float
    failures: int

    def as_dict(self) -> dict:
        return asdict(self)


def _summarize(
    key: str, name: str | None, version: str | None, events: list[PromptEvent]
) -> Aggregate:
    return Aggregate(
        key=key,
        prompt_name=name,
        prompt_version=version,
        calls=len(events),
        latency=sum(e.latency or 0.0 for e in events),
        tokens=sum(e.tokens or 0 for e in events),
        cost=sum(e.cost or 0.0 for e in events),
        failures=sum(1 for e in events if e.status is EventStatus.ERROR),
    )


class Analytics:
    """Aggregation facade over a :class:`PromptEventStore`."""

    def __init__(self, store: PromptEventStore | None = None) -> None:
        self._store = store or default_store

    def by_prompt(self) -> list[Aggregate]:
        buckets: dict[str, list[PromptEvent]] = {}
        for event in self._store.all():
            buckets.setdefault(event.prompt_name or "<unattributed>", []).append(event)
        return [_summarize(name, name, None, events) for name, events in sorted(buckets.items())]

    def by_version(self) -> list[Aggregate]:
        buckets: dict[tuple[str, str], list[PromptEvent]] = {}
        for event in self._store.all():
            key = (event.prompt_name or "<unattributed>", event.prompt_version or "<none>")
            buckets.setdefault(key, []).append(event)
        return [
            _summarize(f"{name}@{version}", name, version, events)
            for (name, version), events in sorted(buckets.items())
        ]

    def cost(self) -> float:
        return sum(e.cost or 0.0 for e in self._store.all())

    def calls(self) -> int:
        return len(self._store.all())

    def export(self, fmt: str, path: str) -> None:
        from tokenhelm_prompt.analytics.export import export_aggregates

        export_aggregates(self.by_version(), fmt, path)
