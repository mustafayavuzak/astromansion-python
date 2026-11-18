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

    A wait the server's answer asked for, such as a rate limit's, is never
    silent. The client writes ``WAIT_WARNING`` to the ``LOGGER_NAME`` logger
    before it sleeps, so a call that pauses for seconds says why. Python
    prints a warning to standard error when the application configured no
    logging, and an application that did can silence the logger by name.
    """

    LOGGER_NAME: Final[str] = "astromansion"
    WAIT_WARNING: Final[str] = (
        "The AstroMansion API answered %d, so the client waits %.1f s "
        "before retry %d of %d. Pass max_retries=0 to get the error at once."
    )
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
