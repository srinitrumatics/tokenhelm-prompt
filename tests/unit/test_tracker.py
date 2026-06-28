"""US2: tracker behavior — unregistered names, passthrough, imperative API (T021)."""

from __future__ import annotations

from tokenhelm_prompt import make_dispatcher, tracker
from tokenhelm_prompt.analytics.store import default_store


def test_unregistered_name_does_not_fail_call(make_event):
    # No registry bound → name is unregistered, but the call still records.
    disp = make_dispatcher()
    with tracker.prompt("ghost"):
        meta = tracker.current_prompt()
        assert meta.prompt_name == "ghost"
        assert meta.registered is False
        disp.dispatch(make_event())
    assert default_store.all()[0].prompt_name == "ghost"


def test_no_scope_means_no_current_prompt():
    assert tracker.current_prompt() is None


def test_set_and_clear_prompt():
    tracker.set_prompt("manual")
    assert tracker.current_prompt().prompt_name == "manual"
    tracker.clear_prompt()
    assert tracker.current_prompt() is None


def test_decorator_attributes_function(registry, make_event):
    from tokenhelm_prompt import prompt as prompt_decorator

    registry.register("dec", owner="o", application="a", environment="prod", template="t")
    tracker.use_registry(registry)
    disp = make_dispatcher()

    @prompt_decorator("dec")
    def do_work():
        disp.dispatch(make_event())

    do_work()
    assert default_store.all()[0].prompt_name == "dec"


def test_failure_in_scope_recorded_as_error():
    from tokenhelm_prompt.models import EventStatus

    try:
        with tracker.prompt("risky"):
            raise RuntimeError("boom")
    except RuntimeError:
        pass

    events = default_store.all()
    assert len(events) == 1
    assert events[0].status is EventStatus.ERROR
    assert events[0].prompt_name == "risky"
    # context restored even though the block raised
    assert tracker.current_prompt() is None
