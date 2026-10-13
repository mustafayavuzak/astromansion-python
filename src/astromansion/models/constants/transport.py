"""src/astromansion/models/constants/transport.py: Timeouts and retry policy."""

from __future__ import annotations

from http import HTTPStatus
from typing import Final


class TimeoutConstants:
    """How long a client waits, in seconds.

    A chart is computed on the server, so reading is generous while
    connecting stays short: an unreachable host should fail fast.
    """

    CONNECT_SECONDS: Final[float] = 5.0
    READ_SECONDS: Final[float] = 30.0


class RetryConstants:
    """When repeating a request is safe, and how long to wait before it.

    Only failures that carry no result are repeated. A request that never
    completed cannot have been counted against the caller's allowance, and a
    status in ``STATUSES`` means the server produced nothing, so neither can
    be charged twice. A refusal the caller must fix is never repeated.

    ``MAX_RETRIES`` is the default number of repeats after the first attempt.
    The wait doubles from ``BACKOFF_SECONDS`` per attempt up to
    ``BACKOFF_CEILING_SECONDS``, then takes a random share of itself no
    smaller than ``JITTER_FLOOR_FRACTION``, so clients that failed together
    do not retry together.
    """

    MAX_RETRIES: Final[int] = 2
    BACKOFF_SECONDS: Final[float] = 0.5
    BACKOFF_CEILING_SECONDS: Final[float] = 8.0
    JITTER_FLOOR_FRACTION: Final[float] = 0.5

    STATUSES: Final[frozenset[HTTPStatus]] = frozenset(
        {
            HTTPStatus.TOO_MANY_REQUESTS,
            HTTPStatus.INTERNAL_SERVER_ERROR,
            HTTPStatus.BAD_GATEWAY,
            HTTPStatus.SERVICE_UNAVAILABLE,
            HTTPStatus.GATEWAY_TIMEOUT,
        }
    )
