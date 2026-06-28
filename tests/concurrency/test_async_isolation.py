"""US3: async task isolation — no cross-task attribution leakage (T027, SC-003)."""

from __future__ import annotations

import asyncio

import pytest

from tokenhelm_prompt import tracker


@pytest.mark.asyncio
async def test_concurrent_tasks_do_not_leak():
    seen: dict[str, str | None] = {}

    async def worker(name: str):
        with tracker.prompt(name):
            # Yield control so tasks interleave; each must keep its own prompt.
            await asyncio.sleep(0)
            await asyncio.sleep(0)
            current = tracker.current_prompt()
            seen[name] = current.prompt_name if current else None

    await asyncio.gather(*(worker(f"p{i}") for i in range(8)))
    assert seen == {f"p{i}": f"p{i}" for i in range(8)}


@pytest.mark.asyncio
async def test_attribution_follows_await_boundary():
    with tracker.prompt("outer"):

        async def inner():
            # Inherits the caller's context at creation time.
            assert tracker.current_prompt().prompt_name == "outer"

        await inner()
        assert tracker.current_prompt().prompt_name == "outer"
