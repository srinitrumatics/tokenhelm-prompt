"""OpenAI Agents SDK integration — attribute model calls within an agent run.

``prompt_scope`` needs no SDK; :func:`make_run_hooks` imports ``agents`` lazily.
"""

from __future__ import annotations

from contextlib import contextmanager

from tokenhelm_prompt.tracking import tracker as _default_tracker


@contextmanager
def prompt_scope(name: str, version: str | None = None, tracker=None):
    """Open a prompt scope around an OpenAI Agents run (no SDK import needed)."""
    trk = tracker or _default_tracker
    with trk.prompt(name, version) as meta:
        yield meta


def make_run_hooks(name: str, version: str | None = None, tracker=None):
    """Return an OpenAI Agents ``RunHooks`` subclass instance attributing runs."""
    from agents import RunHooks

    trk = tracker or _default_tracker

    class TokenHelmPromptHooks(RunHooks):
        async def on_agent_start(self, *args, **kwargs) -> None:
            trk.set_prompt(name, version)

        async def on_agent_end(self, *args, **kwargs) -> None:
            trk.clear_prompt()

    return TokenHelmPromptHooks()
