"""Haystack integration — attribute generator calls within a Haystack pipeline.

``prompt_scope`` needs no SDK; :func:`instrument` imports ``haystack`` lazily.
Haystack is enumerated as an optional integration in Constitution III.
"""

from __future__ import annotations

from contextlib import contextmanager

from tokenhelm_prompt.tracking import tracker as _default_tracker


@contextmanager
def prompt_scope(name: str, version: str | None = None, tracker=None):
    """Open a prompt scope around a Haystack pipeline run (no SDK import needed)."""
    trk = tracker or _default_tracker
    with trk.prompt(name, version) as meta:
        yield meta


def instrument(pipeline, name: str, version: str | None = None, tracker=None):
    """Wrap a Haystack ``Pipeline.run`` so each run is attributed to ``name``."""
    import haystack  # noqa: F401  (validates Haystack is installed)

    trk = tracker or _default_tracker
    original_run = pipeline.run

    def run(*args, **kwargs):
        with trk.prompt(name, version):
            return original_run(*args, **kwargs)

    pipeline.run = run
    return pipeline
