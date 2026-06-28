"""LlamaIndex integration — attribute LLM calls within a LlamaIndex run.

Lazy: ``llama_index`` is imported only inside :func:`make_handler`.
"""

from __future__ import annotations

from tokenhelm_prompt import context
from tokenhelm_prompt.tracking import tracker as _default_tracker


def make_handler(name: str, version: str | None = None, tracker=None):
    """Return a LlamaIndex callback handler that opens a prompt scope per event."""
    from llama_index.core.callbacks.base_handler import BaseCallbackHandler

    trk = tracker or _default_tracker

    class TokenHelmPromptHandler(BaseCallbackHandler):
        def __init__(self) -> None:
            super().__init__(event_starts_to_ignore=[], event_ends_to_ignore=[])
            self._token = None

        def on_event_start(self, *args, **kwargs) -> str:
            self._token = context.push(trk._build_meta(name, version))
            return ""

        def on_event_end(self, *args, **kwargs) -> None:
            if self._token is not None:
                context.reset(self._token)
                self._token = None

        def start_trace(self, *args, **kwargs) -> None:
            return None

        def end_trace(self, *args, **kwargs) -> None:
            return None

    return TokenHelmPromptHandler()
