"""
Retry logic for external API calls using the tenacity library.

Retries on:
  - Network errors (connection timeouts, DNS failures)
  - HTTP 429 (rate limit) and 5xx (server errors)

Does NOT retry on:
  - 4xx client errors (bad request, auth failure, not found)
"""

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    before_sleep_log,
)
import logging

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Max 3 attempts with exponential backoff: 1s, 2s, 4s
_DEFAULT_STOP = stop_after_attempt(3)
_DEFAULT_WAIT = wait_exponential(multiplier=1, min=1, max=8)


def _should_retry(exc: BaseException) -> bool:
    """Return True if this exception warrants a retry."""
    if isinstance(exc, httpx.TimeoutException):
        return True
    if isinstance(exc, httpx.NetworkError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 500, 502, 503, 504)
    return False


def with_retry(func):
    """
    Decorator that adds retry logic to an async or sync function making
    HTTP calls.  Wraps with tenacity using the standard policy above.
    """
    return retry(
        retry=retry_if_exception(_should_retry),
        stop=_DEFAULT_STOP,
        wait=_DEFAULT_WAIT,
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )(func)
