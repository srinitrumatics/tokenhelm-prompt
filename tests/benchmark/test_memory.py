"""SC-005: enabling attribution adds ≤2 MB, measured via peak tracemalloc delta (T047)."""

from __future__ import annotations

import tracemalloc

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


def test_memory_overhead_under_2mb():
    store = PromptEventStore()
    disp = make_dispatcher(store=store)
    ev = _event()

    tracemalloc.start()
    base = tracemalloc.take_snapshot()
    with tracker.prompt("bench"):
        for _ in range(1000):
            disp.dispatch(ev)
    peak = tracemalloc.take_snapshot()
    tracemalloc.stop()

    diff = sum(s.size_diff for s in peak.compare_to(base, "filename"))
    mb = diff / (1024 * 1024)
    assert mb < 2.0, f"attribution added {mb:.3f} MB (>2 MB)"
