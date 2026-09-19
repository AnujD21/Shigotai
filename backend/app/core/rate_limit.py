"""Rate limiting for sensitive auth endpoints.

Uses Redis (fixed-window counter via INCR/EXPIRE) when REDIS_URL is set, so
limits are shared correctly across multiple backend instances/workers. Falls
back to an in-process sliding window otherwise -- fine for a single-instance
deployment, but each worker process would enforce its own separate limit if
you ever run more than one without Redis.

A Redis outage fails OPEN (requests are allowed through) rather than taking
down login/registration -- rate limiting is a defense-in-depth measure, not
something that should turn an infra blip into a full outage.
"""

import logging
import time
from collections import defaultdict
from functools import lru_cache

from fastapi import HTTPException, Request, status

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_WINDOW_SECONDS = 60
_hits: dict[str, list[float]] = defaultdict(list)


@lru_cache
def _get_redis_client():
    settings = get_settings()
    if not settings.redis_url:
        return None
    try:
        import redis

        client = redis.from_url(settings.redis_url, socket_connect_timeout=2, socket_timeout=2)
        client.ping()
        return client
    except Exception:
        logger.warning("REDIS_URL is set but unreachable; falling back to in-process rate limiting.")
        return None


def _check_redis(client, key: str, max_requests: int) -> bool:
    try:
        count = client.incr(key)
        if count == 1:
            client.expire(key, _WINDOW_SECONDS)
        return count <= max_requests
    except Exception:
        logger.warning("Redis error during rate-limit check; allowing request through.")
        return True


def _check_in_process(key: str, max_requests: int) -> bool:
    now = time.monotonic()
    window_start = now - _WINDOW_SECONDS
    hits = [t for t in _hits[key] if t > window_start]
    hits.append(now)
    _hits[key] = hits
    return len(hits) <= max_requests


def rate_limit(max_requests: int = 10):
    def dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"ratelimit:{request.url.path}:{client_ip}"

        redis_client = _get_redis_client()
        allowed = _check_redis(redis_client, key, max_requests) if redis_client else _check_in_process(key, max_requests)

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please wait a moment and try again.",
            )

    return dependency
