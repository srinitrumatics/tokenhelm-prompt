"""US5: analytics aggregates reconcile with events; export works (T034, SC-007)."""

from __future__ import annotations

import csv
import json

from tokenhelm_prompt import analytics, make_dispatcher, tracker
from tokenhelm_prompt.analytics.store import default_store


def _seed(registry, make_event):
    registry.register("invoice", owner="o", application="a", environment="prod", template="t {x}")
    registry.add_version("invoice", template="t2 {x}", created_by="o")
    tracker.use_registry(registry)
    disp = make_dispatcher()
    with tracker.prompt("invoice", version="v1"):
        disp.dispatch(make_event(latency=0.1, cost="0.01", total_tokens=10))
    with tracker.prompt("invoice", version="v2"):
        disp.dispatch(make_event(latency=0.2, cost="0.02", total_tokens=20))
        disp.dispatch(make_event(latency=0.3, cost="0.03", total_tokens=30))
    return disp


def test_by_prompt_reconciles_with_events(registry, make_event):
    _seed(registry, make_event)
    rows = {a.prompt_name: a for a in analytics.by_prompt()}
    inv = rows["invoice"]
    assert inv.calls == 3
    assert inv.tokens == 60
    assert abs(inv.cost - 0.06) < 1e-9
    # latency normalized to ms: (0.1+0.2+0.3)*1000 = 600
    assert abs(inv.latency - 600.0) < 1e-6
    # totals equal the raw store
    assert inv.calls == len(default_store.all())


def test_by_version_breaks_down(registry, make_event):
    _seed(registry, make_event)
    rows = {a.prompt_version: a for a in analytics.by_version()}
    assert rows["v1"].calls == 1
    assert rows["v2"].calls == 2
    assert rows["v2"].tokens == 50


def test_cost_and_calls_helpers(registry, make_event):
    _seed(registry, make_event)
    assert analytics.calls() == 3
    assert abs(analytics.cost() - 0.06) < 1e-9


def test_export_csv_and_json(registry, make_event, tmp_path):
    _seed(registry, make_event)
    csv_path = tmp_path / "a.csv"
    json_path = tmp_path / "a.json"
    analytics.export("csv", str(csv_path))
    analytics.export("json", str(json_path))

    with csv_path.open() as fh:
        rows = list(csv.DictReader(fh))
    assert {r["prompt_version"] for r in rows} == {"v1", "v2"}

    data = json.loads(json_path.read_text())
    assert sum(int(r["calls"]) for r in data) == 3
