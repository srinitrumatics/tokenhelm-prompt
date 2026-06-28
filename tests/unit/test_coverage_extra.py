"""Targeted tests for remaining branches (push coverage past the 95% gate)."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from tokenhelm_prompt import make_dispatcher, prompt, tracker
from tokenhelm_prompt.analytics.store import default_store
from tokenhelm_prompt.registry.resolver import resolve_version


def test_async_decorator_attributes(registry):
    registry.register("adec", owner="o", application="a", environment="prod", template="t")
    tracker.use_registry(registry)
    disp = make_dispatcher()

    @prompt("adec")
    async def work():
        assert tracker.current_prompt().prompt_name == "adec"
        disp.dispatch(
            SimpleNamespace(
                provider=None, model=None, total_tokens=1, latency=None, cost=None, timestamp=None
            )
        )

    asyncio.run(work())
    assert default_store.all()[0].prompt_name == "adec"


def test_enrichment_handles_none_provider_and_latency():
    disp = make_dispatcher()
    disp.dispatch(
        SimpleNamespace(
            provider=None, model=None, total_tokens=None, latency=None, cost=None, timestamp=None
        )
    )
    event = default_store.all()[0]
    assert event.provider is None
    assert event.latency is None
    assert event.cost == 0.0


def test_registry_bound_unknown_name_falls_back_to_unregistered(registry):
    # Registry IS bound, but the name is absent → except path → unregistered.
    registry.register("known", owner="o", application="a", environment="prod", template="t")
    tracker.use_registry(registry)
    with tracker.prompt("missing"):
        meta = tracker.current_prompt()
    assert meta.registered is False
    assert meta.prompt_id is None


def test_resolver_empty_versions_raises():
    with pytest.raises(LookupError):
        resolve_version([], None)
