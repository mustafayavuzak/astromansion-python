"""src/astromansion/_backoff.py: How long to wait before repeating a request.

The server's ``Retry-After`` wins when it sent one, because it knows when the
window reopens. Otherwise the wait grows exponentially with a random share, so
clients that failed together do not retry together::

    attempt     window (s)      wait (s)
    0           0.5             0.25 .. 0.5
    1           1.0             0.5  .. 1.0
    2           2.0             1.0  .. 2.0
    5           8.0 (ceiling)   4.0  .. 8.0
"""

from __future__ import annotations

import random
from collections.abc import Mapping

from .models.constants.api import ApiConstants
from .models.constants.transport import RetryConstants


class Backoff:
    """Read the server's requested pause and compute the wait before a retry."""

    @staticmethod
    def parse_header(value: str | None) -> float | None:
        """Read a ``Retry-After`` value expressed in seconds.

        The header may also hold an HTTP date. That form is ignored rather
        than parsed for a hint, and the exponential backoff covers it.

        Args:
            value: The header's text, or ``None`` when it was absent.

        Returns:
            Seconds to wait, never negative, or ``None`` when the value is
            missing or not a number.

        Examples:
            >>> Backoff.parse_header("3")
            3.0
            >>> Backoff.parse_header("-1")
            0.0
            >>> Backoff.parse_header("Wed, 21 Oct 2026 07:28:00 GMT") is None
            True
        """
        if not value:
            return None
        try:
            return max(0.0, float(value.strip()))
        except ValueError:
            return None

    @classmethod
    def retry_after(cls, headers: Mapping[str, str]) -> float | None:
        """Read the pause a response asked for.

        Args:
            headers: The response headers.

        Returns:
            Seconds to wait, or ``None`` when the response asked for none.

        Examples:
            >>> Backoff.retry_after({"Retry-After": "2"})
            2.0
            >>> Backoff.retry_after({}) is None
            True
        """
        return cls.parse_header(headers.get(ApiConstants.RETRY_AFTER_HEADER))

    @staticmethod
    def delay(attempt: int, retry_after: float | None) -> float:
        """Return the pause before the next attempt, in seconds.

        Args:
            attempt: Zero-based number of the attempt that just failed.
            retry_after: The server's requested pause, if it gave one.

        Returns:
            The server's pause capped at the ceiling, or the exponential
            window for this attempt reduced by a random share of at most half.

        Examples:
            >>> Backoff.delay(0, 3.0)
            3.0
            >>> Backoff.delay(0, 60.0)
            8.0
            >>> 0.25 <= Backoff.delay(0, None) <= 0.5
            True
        """
        if retry_after is not None and retry_after >= 0:
            return min(retry_after, RetryConstants.BACKOFF_CEILING_SECONDS)
        window = min(
            RetryConstants.BACKOFF_SECONDS * (2**attempt),
            RetryConstants.BACKOFF_CEILING_SECONDS,
        )
        floor = RetryConstants.JITTER_FLOOR_FRACTION
        return float(window * (floor + random.random() * (1.0 - floor)))
