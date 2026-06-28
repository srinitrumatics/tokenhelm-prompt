"""Google ADK integration — attribute model calls within an ADK agent run.

``prompt_scope`` needs no SDK; :func:`make_before_model_callback` imports
``google.adk`` lazily.
"""

from __future__ import annotations

from contextlib import contextmanager

from tokenhelm_prompt.tracking import tracker as _default_tracker


@contextmanager
def prompt_scope(name: str, version: str | None = None, tracker=None):
    """Open a prompt scope around an ADK invocation (no ADK import needed)."""
    trk = tracker or _default_tracker
    with trk.prompt(name, version) as meta:
        yield meta


def make_before_model_callback(name: str, version: str | None = None, tracker=None):
    """Return an ADK ``before_model_callback`` that sets the active prompt."""
    import google.adk  # noqa: F401  (validates ADK is installed)

    trk = tracker or _default_tracker

    def before_model_callback(*_args, **_kwargs):
        trk.set_prompt(name, version)
        return None

    return before_model_callback
