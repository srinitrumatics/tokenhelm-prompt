"""Analytics aggregation, export, and the shared event store."""

from __future__ import annotations

from tokenhelm_prompt.analytics.aggregate import Aggregate, Analytics
from tokenhelm_prompt.analytics.export import export_aggregates
from tokenhelm_prompt.analytics.store import PromptEventStore, default_store

#: Default analytics facade bound to the shared :data:`default_store`.
analytics = Analytics(default_store)

__all__ = [
    "Analytics",
    "Aggregate",
    "analytics",
    "PromptEventStore",
    "default_store",
    "export_aggregates",
]
