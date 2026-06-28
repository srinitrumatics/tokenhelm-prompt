"""``contextvars``-based active-prompt stack (Constitution V).

A single :class:`contextvars.ContextVar` holds an immutable tuple acting as a
stack. ``push`` returns a token; ``reset(token)`` restores the exact prior state
— giving correct nesting, exception-safe restore, and per-task isolation across
``async`` tasks and streaming generators with no cross-task leakage.
"""

from __future__ import annotations

import contextvars

from tokenhelm_prompt.models import PromptMetadata

_active: contextvars.ContextVar[tuple[PromptMetadata, ...]] = contextvars.ContextVar(
    "tokenhelm_prompt_stack", default=()
)


def push(meta: PromptMetadata) -> contextvars.Token:
    """Push ``meta`` as the active prompt; return a token for :func:`reset`."""
    return _active.set(_active.get() + (meta,))


def reset(token: contextvars.Token) -> None:
    """Restore the active-prompt stack to the state captured by ``token``."""
    _active.reset(token)


def current() -> PromptMetadata | None:
    """Return the innermost active prompt, or ``None`` when no scope is active."""
    stack = _active.get()
    return stack[-1] if stack else None


def clear() -> contextvars.Token:
    """Clear all active prompts; return a token that can restore prior state."""
    return _active.set(())


def depth() -> int:
    """Number of nested active scopes (diagnostics/testing)."""
    return len(_active.get())
