"""US3: nested restore order and exception-safe reset (T029)."""

from __future__ import annotations

from tokenhelm_prompt import context, tracker


def test_inner_scope_wins_then_outer_restored():
    with tracker.prompt("outer"):
        assert tracker.current_prompt().prompt_name == "outer"
        with tracker.prompt("inner"):
            assert tracker.current_prompt().prompt_name == "inner"
        # inner exited → outer restored
        assert tracker.current_prompt().prompt_name == "outer"
    assert tracker.current_prompt() is None


def test_exception_in_inner_restores_outer():
    with tracker.prompt("outer"):
        try:
            with tracker.prompt("inner"):
                raise ValueError("x")
        except ValueError:
            pass
        assert tracker.current_prompt().prompt_name == "outer"
    assert tracker.current_prompt() is None
    assert context.depth() == 0


def test_three_levels_restore_in_order():
    with tracker.prompt("a"):
        with tracker.prompt("b"):
            with tracker.prompt("c"):
                assert tracker.current_prompt().prompt_name == "c"
            assert tracker.current_prompt().prompt_name == "b"
        assert tracker.current_prompt().prompt_name == "a"
    assert context.depth() == 0
