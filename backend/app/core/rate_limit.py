"""Minimal in-process rate limiting for sensitive auth endpoints.

This is intentionally simple (a per-process sliding window keyed by client
IP) rather than pulling in Redis/slowapi -- appropriate for a single-instance
demo deployment. A production deployment behind multiple workers should
replace this with a shared-store limiter (e.g. Redis) using the same
dependency signature; see README "Security" section.
"""

import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

_WINDOW_SECONDS = 60
_hits: dict[str, list[float]] = defaultdict(list)


def rate_limit(max_requests: int = 10):
    def dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"{request.url.path}:{client_ip}"
        now = time.monotonic()
        window_start = now - _WINDOW_SECONDS

        hits = [t for t in _hits[key] if t > window_start]
        if len(hits) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please wait a moment and try again.",
            )
        hits.append(now)
        _hits[key] = hits

    return dependency
