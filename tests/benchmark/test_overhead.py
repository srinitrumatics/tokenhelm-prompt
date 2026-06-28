"""SC-004: attribution overhead ≤1 ms per call (T046)."""

from __future__ import annotations

import time

from tokenhelm_prompt import make_dispatcher, tracker
from tokenhelm_prompt.analytics.store import PromptEventStore


def _event():
    import tokenhelm as th
    from datetime import datetime, timezone
    from decimal import Decimal

    return th.LLMEvent(
        provider=th.LLMProvider.OPENAI,
        model="gpt-4",
        input_tokens=10,
        output_tokens=5,
        total_tokens=15,
        latency=0.2,
        cost=Decimal("0.01"),
        timestamp=datetime.now(timezone.utc),
    )


def test_attribution_overhead_under_1ms():
    store = PromptEventStore()
    disp = make_dispatcher(store=store)
    ev = _event()
    iterations = 2000

    start = time.perf_counter()
    with tracker.prompt("bench"):
        for _ in range(iterations):
            disp.dispatch(ev)
    elapsed = time.perf_counter() - start

    per_call_ms = (elapsed / iterations) * 1000.0
    assert per_call_ms < 1.0, f"attribution overhead {per_call_ms:.4f} ms/call exceeds 1 ms"
