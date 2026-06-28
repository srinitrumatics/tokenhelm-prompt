"""US2: automatic attribution via the enriching dispatcher (T020).

Exercises the real ``EventDispatcher`` seam: ``PromptEnrichingDispatcher``
implements ``dispatch(event)`` and TokenHelm accepts it via ``dispatcher=``.
"""

from __future__ import annotations

from tokenhelm_prompt import analytics, make_dispatcher, tracker
from tokenhelm_prompt.analytics.store import default_store
from tokenhelm_prompt.models import EventStatus


def test_in_scope_event_carries_name_and_version(registry, make_event):
    registry.register(
        "invoice", owner="o", application="a", environment="prod", template="Summarize {x}"
    )
    tracker.use_registry(registry)
    disp = make_dispatcher()

    with tracker.prompt("invoice"):
        disp.dispatch(make_event())

    events = default_store.all()
    assert len(events) == 1
    assert events[0].prompt_name == "invoice"
    assert events[0].prompt_version == "v1"
    assert events[0].status is EventStatus.SUCCESS


def test_out_of_scope_event_has_no_attribution(make_event):
    disp = make_dispatcher()
    disp.dispatch(make_event())
    event = default_store.all()[0]
    assert event.prompt_name is None
    assert event.prompt_id is None
    assert event.prompt_version is None


def test_scope_exit_stops_attribution(registry, make_event):
    registry.register("invoice", owner="o", application="a", environment="prod", template="t")
    tracker.use_registry(registry)
    disp = make_dispatcher()

    with tracker.prompt("invoice"):
        disp.dispatch(make_event())
    disp.dispatch(make_event())  # after scope

    names = [e.prompt_name for e in default_store.all()]
    assert names == ["invoice", None]


def test_original_event_forwarded_unchanged(make_event):
    forwarded = []

    class Inner:
        def dispatch(self, event):
            forwarded.append(event)

    disp = make_dispatcher(Inner())
    ev = make_event()
    disp.dispatch(ev)
    assert forwarded == [ev]  # same object, not mutated/replaced


def test_tokenhelm_accepts_our_dispatcher():
    import tokenhelm as th

    # Constitution II: our dispatcher satisfies the EventDispatcher protocol.
    helm = th.TokenHelm(dispatcher=make_dispatcher())
    assert helm is not None


def test_analytics_reflect_attribution(registry, make_event):
    registry.register("invoice", owner="o", application="a", environment="prod", template="t")
    tracker.use_registry(registry)
    disp = make_dispatcher()
    with tracker.prompt("invoice"):
        disp.dispatch(make_event())
        disp.dispatch(make_event())
    rows = {a.prompt_name: a for a in analytics.by_prompt()}
    assert rows["invoice"].calls == 2
