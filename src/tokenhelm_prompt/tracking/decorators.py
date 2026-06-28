"""Decorator form of prompt attribution (FR-008).

``@prompt("name")`` wraps a function body in ``tracker.prompt(...)``. Both sync
and async callables are supported so attribution follows ``await`` boundaries.
"""

from __future__ import annotations

import functools
import inspect
from typing import Callable


def make_prompt_decorator(tracker) -> Callable:
    """Build a ``@prompt(name, version=None)`` decorator bound to ``tracker``."""

    def prompt(name: str, version: str | None = None) -> Callable:
        def decorate(func: Callable) -> Callable:
            if inspect.iscoroutinefunction(func):

                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    with tracker.prompt(name, version):
                        return await func(*args, **kwargs)

                return async_wrapper

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                with tracker.prompt(name, version):
                    return func(*args, **kwargs)

            return sync_wrapper

        return decorate

    return prompt
