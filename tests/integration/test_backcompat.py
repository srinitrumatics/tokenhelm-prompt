"""Constitution X / SC-002: no-scope events are unchanged; core API untouched (T048)."""

from __future__ import annotations


def test_inner_dispatcher_receives_identical_event_with_no_scope(make_event):
    from tokenhelm_prompt import make_dispatcher

    received = []

    class Inner:
        def dispatch(self, event):
            received.append(event)

    disp = make_dispatcher(Inner())
    ev = make_event()
    disp.dispatch(ev)  # no active scope

    assert received == [ev]  # same object, byte-for-byte identical
    assert received[0] is ev


def test_core_public_api_surface_intact():
    import tokenhelm as th

    # Constitution I: these names must still exist and be unchanged in kind.
    for name in ("TokenHelm", "LLMEvent", "EventDispatcher"):
        assert hasattr(th, name)
    for method in ("track", "trace", "track_stream", "configure"):
        assert callable(getattr(th.TokenHelm, method))


def test_importing_prompt_package_does_not_patch_core():
    import tokenhelm as th

    before = th.TokenHelm.track
    import tokenhelm_prompt  # noqa: F401

    assert th.TokenHelm.track is before  # no monkey-patching
