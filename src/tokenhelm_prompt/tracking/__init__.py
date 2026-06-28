"""Tracking: the default tracker, the ``@prompt`` decorator, and the dispatcher.

Wiring (no TokenHelm core changes — Constitution I/II/X)::

    from tokenhelm import TokenHelm, DefaultEventDispatcher
    from tokenhelm_prompt import make_dispatcher, tracker

    th = TokenHelm(dispatcher=make_dispatcher(DefaultEventDispatcher()))
    with tracker.prompt("invoice_summary"):
        th.track(response)   # event recorded with prompt attribution
"""

from __future__ import annotations

from tokenhelm_prompt.tracking.decorators import make_prompt_decorator
from tokenhelm_prompt.tracking.enrichment import PromptEnrichingDispatcher
from tokenhelm_prompt.tracking.tracker import PromptTracker

#: Process-wide default tracker (bind a registry via ``tracker.use_registry``).
tracker = PromptTracker()

#: ``@prompt("name")`` decorator bound to the default tracker.
prompt = make_prompt_decorator(tracker)


def make_dispatcher(inner=None, store=None) -> PromptEnrichingDispatcher:
    """Build a :class:`PromptEnrichingDispatcher` wrapping ``inner``."""
    return PromptEnrichingDispatcher(inner=inner, store=store)


__all__ = [
    "PromptTracker",
    "PromptEnrichingDispatcher",
    "tracker",
    "prompt",
    "make_dispatcher",
]
