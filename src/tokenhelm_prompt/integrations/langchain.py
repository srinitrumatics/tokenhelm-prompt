"""LangChain integration — attribute LLM calls made within a LangChain run.

Lazy: ``langchain_core`` is imported only when :func:`make_callback` is called,
so importing this module never requires LangChain (Constitution III).
"""

from __future__ import annotations

from tokenhelm_prompt import context
from tokenhelm_prompt.tracking import tracker as _default_tracker


def make_callback(name: str, version: str | None = None, tracker=None):
    """Return a LangChain callback handler that opens a prompt scope per LLM run."""
    from langchain_core.callbacks import BaseCallbackHandler

    trk = tracker or _default_tracker

    class TokenHelmPromptCallback(BaseCallbackHandler):
        def __init__(self) -> None:
            self._token = None

        def on_llm_start(self, *args, **kwargs) -> None:
            self._token = context.push(trk._build_meta(name, version))

        def on_llm_end(self, *args, **kwargs) -> None:
            self._reset()

        def on_llm_error(self, *args, **kwargs) -> None:
            self._reset()

        def _reset(self) -> None:
            if self._token is not None:
                context.reset(self._token)
                self._token = None

    return TokenHelmPromptCallback()
