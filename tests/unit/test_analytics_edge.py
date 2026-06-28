"""US5: empty-result and failure-count edge cases (T035)."""

from __future__ import annotations

import pytest

from tokenhelm_prompt import analytics, make_dispatcher, tracker
from tokenhelm_prompt.analytics.export import export_aggregates


def test_empty_store_returns_well_formed_empty_results():
    assert analytics.by_prompt() == []
    assert analytics.by_version() == []
    assert analytics.calls() == 0
    assert analytics.cost() == 0.0


def test_failures_counted_from_error_status():
    # one success, two failures attributed to "risky"
    disp = make_dispatcher()
    import tokenhelm as th
    from datetime import datetime, timezone
    from decimal import Decimal

    ev = th.LLMEvent(
        provider=th.LLMProvider.OPENAI,
        model="m",
        input_tokens=1,
        output_tokens=1,
        total_tokens=2,
        latency=0.01,
        cost=Decimal("0"),
        timestamp=datetime.now(timezone.utc),
    )
    with tracker.prompt("risky"):
        disp.dispatch(ev)
    for _ in range(2):
        try:
            with tracker.prompt("risky"):
                raise RuntimeError("boom")
        except RuntimeError:
            pass

    row = {a.prompt_name: a for a in analytics.by_prompt()}["risky"]
    assert row.calls == 3
    assert row.failures == 2


def test_export_rejects_unknown_format(tmp_path):
    with pytest.raises(ValueError):
        export_aggregates([], "xml", str(tmp_path / "x.xml"))
