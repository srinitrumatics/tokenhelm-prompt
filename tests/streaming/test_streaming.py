"""US3: streaming attribution across generators (T028, SC-003)."""

from __future__ import annotations

from tokenhelm_prompt import make_dispatcher, tracker
from tokenhelm_prompt.analytics.store import default_store


def test_generator_steps_attributed_to_active_prompt(make_event):
    disp = make_dispatcher()

    def stream():
        # Each yielded chunk dispatches an event while the scope is active.
        for _ in range(3):
            disp.dispatch(make_event())
            yield

    with tracker.prompt("streamer"):
        list(stream())

    events = default_store.all()
    assert len(events) == 3
    assert all(e.prompt_name == "streamer" for e in events)


def test_generator_created_in_scope_keeps_attribution_when_consumed_outside(make_event):
    disp = make_dispatcher()

    def make_stream():
        with tracker.prompt("lazy"):
            for _ in range(2):
                disp.dispatch(make_event())
                yield

    gen = make_stream()
    # Consume entirely outside any active scope.
    list(gen)
    events = default_store.all()
    assert [e.prompt_name for e in events] == ["lazy", "lazy"]
    assert tracker.current_prompt() is None
