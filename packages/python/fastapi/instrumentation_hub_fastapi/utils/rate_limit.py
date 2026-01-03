"""Reusable decorator for rate-limited logging."""
from __future__ import annotations

import functools
import time
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable)


def rate_limited_log(interval_seconds: int = 60) -> Callable[[F], F]:
    """Decorator that flips `wrapper._can_log` when the interval has elapsed."""

    def decorator(func: F) -> F:
        last_logged = [0.0]

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            wrapper._can_log = False
            now = time.time()
            if now - last_logged[0] > interval_seconds:
                wrapper._can_log = True
                last_logged[0] = now
            return await func(*args, **kwargs)

        wrapper._can_log = True  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator
