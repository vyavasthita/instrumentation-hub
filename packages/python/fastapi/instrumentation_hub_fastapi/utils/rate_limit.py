"""Reusable decorator for rate-limited logging.

The OAAS stack treats logs as a first-class signal, so it is easy for noisy
endpoints (for example `/health`) to flood OpenSearch or Loki. Wrapping a route
handler with `@rate_limited_log` preserves visibility while ensuring the export
pipeline stays within reasonable volume limits.
"""
from __future__ import annotations

import functools
import time
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable)


def rate_limited_log(interval_seconds: int = 60) -> Callable[[F], F]:
    """Decorator that flips `wrapper._can_log` when the interval has elapsed.

    Example:
        ```python
        @rate_limited_log(interval_seconds=5)
        async def handler():
            if handler._can_log:
                logger.info("expensive log")
        ```
    """

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
