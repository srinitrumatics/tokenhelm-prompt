"""Shared fixtures: isolate the shared store, context, and a fresh registry."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from tokenhelm_prompt import context
from tokenhelm_prompt.analytics.store import default_store
from tokenhelm_prompt.registry import YamlRegistry
from tokenhelm_prompt.tracking import tracker as default_tracker


@pytest.fixture(autouse=True)
def _isolation():
    """Reset shared global state before and after every test."""
    default_store.clear()
    context.clear()
    default_tracker._registry = None
    yield
    default_store.clear()
    context.clear()
    default_tracker._registry = None


@pytest.fixture
def registry(tmp_path) -> YamlRegistry:
    return YamlRegistry(tmp_path / "prompts.yaml")


@pytest.fixture
def make_event():
    """Factory building a realistic TokenHelm ``LLMEvent`` for dispatch tests."""
    import tokenhelm as th

    def _make(latency: float = 0.2, cost: str = "0.01", total_tokens: int = 15):
        return th.LLMEvent(
            provider=th.LLMProvider.OPENAI,
            model="gpt-4",
            input_tokens=10,
            output_tokens=5,
            total_tokens=total_tokens,
            latency=latency,
            cost=Decimal(cost),
            timestamp=datetime.now(timezone.utc),
        )

    return _make
