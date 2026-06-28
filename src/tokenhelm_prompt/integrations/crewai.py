"""CrewAI integration — attribute LLM calls made by a CrewAI agent/task.

``prompt_scope`` needs no SDK; :func:`make_hook` imports ``crewai`` lazily.
"""

from __future__ import annotations

from contextlib import contextmanager

from tokenhelm_prompt.tracking import tracker as _default_tracker


@contextmanager
def prompt_scope(name: str, version: str | None = None, tracker=None):
    """Open a prompt scope around a CrewAI invocation (no CrewAI import needed)."""
    trk = tracker or _default_tracker
    with trk.prompt(name, version) as meta:
        yield meta


def make_hook(name: str, version: str | None = None, tracker=None):
    """Return a CrewAI step callback that attributes steps to ``name``."""
    import crewai  # noqa: F401  (validates CrewAI is installed)

    trk = tracker or _default_tracker

    def step_callback(*_args, **_kwargs):
        trk.set_prompt(name, version)

    return step_callback
