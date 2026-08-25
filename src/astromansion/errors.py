"""Exceptions raised by the AstroMansion client.

The API answers every failure with one envelope::

    {"error": {"code": "...", "message": "...", "detail": "..."}}

Each status maps to the class that names its cause, so a caller catches the
case it can act on instead of matching strings. ``AstroMansionError`` is the
single base for "anything the API refused".
"""

from __future__ import annotations

from typing import Any, Final

from .constants import Retry


class AstroMansionError(Exception):
    """Base for every failure the API or the transport reports.

    :ivar message: Human-readable summary.
    :ivar status_code: HTTP status, or None when no response arrived.
    :ivar error_code: Stable machine code from the error envelope.
    :ivar details: Field-level explanation, when the API supplies one.
    :ivar request_id: Server request identifier, useful in support requests.
    :ivar retry_after: Seconds to wait, when the server asked for a pause.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_code: str | None = None,
        details: Any = None,
        request_id: str | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        self.request_id = request_id
        self.retry_after = retry_after

    def __str__(self) -> str:
        parts = [self.message]
        if self.details:
            parts.append(str(self.details))
        if self.request_id:
            parts.append(f"request_id={self.request_id}")
        return " | ".join(parts)


class AstroMansionConnectionError(AstroMansionError):
    """The request never reached the API, or no answer came back.

    Named with the package prefix so it cannot be confused with the built-in
    ``ConnectionError``, which means something narrower.
    """


class AuthenticationError(AstroMansionError):
    """The API key is missing, malformed, or not recognised (401)."""


class QuotaExceededError(AstroMansionError):
    """The plan's allowance for the period is spent (402, or a 429 whose
    code names a quota rather than a rate)."""


class PermissionDeniedError(AstroMansionError):
    """The key is valid but the plan does not include this feature (403)."""


class NotFoundError(AstroMansionError):
    """No such endpoint or resource (404)."""


class ConflictError(AstroMansionError):
    """The request contradicts the current state (409)."""


class ValidationError(AstroMansionError):
    """The request was rejected (422). ``details`` names the field."""


class RateLimitError(AstroMansionError):
    """Too many requests inside the window (429).

    Separate from :class:`QuotaExceededError`: a rate limit clears on its own
    after ``retry_after`` seconds, while a spent quota needs a new period or a
    larger plan. Waiting fixes one and never fixes the other.
    """


class ServerError(AstroMansionError):
    """The API failed to answer (5xx)."""


class ErrorPolicy:
    """Which exception a failed response becomes.

    The taxonomy and the mapping onto it belong together: a class added above
    without a status here would never be raised, and a status added here
    without a class would not compile. Keeping them apart is what lets the two
    drift.
    """

    #: Statuses the API uses with a meaning narrower than "request failed".
    BY_STATUS: Final[dict[int, type[AstroMansionError]]] = {
        401: AuthenticationError,
        402: QuotaExceededError,
        403: PermissionDeniedError,
        404: NotFoundError,
        409: ConflictError,
        422: ValidationError,
        429: RateLimitError,
    }

    #: Codes that mean a spent allowance even when the status says 429.
    QUOTA_CODES: Final[frozenset[str]] = frozenset(
        {
            "quota_exceeded",
            "quota",
            "monthly_quota_exceeded",
        }
    )

    #: Lowest status that means the server, not the caller, is at fault.
    SERVER_FLOOR: Final[int] = 500

    @classmethod
    def is_retryable(cls, status: int, code: str | None) -> bool:
        """Return whether repeating a refused request could ever help.

        A spent quota is not a busy moment. It answers 429 like a rate limit
        does and clears only with a new period or a larger plan, so asking
        again spends two more round trips to be told the same thing.

        :param status: HTTP status code.
        :param code: Machine code from the error envelope, when present.
        :returns: True when another attempt is worth making.
        """
        if status not in Retry.STATUSES:
            return False
        return not (status == 429 and code and code.lower() in cls.QUOTA_CODES)

    @classmethod
    def for_response(cls, status: int, code: str | None) -> type[AstroMansionError]:
        """Return the exception naming why a response failed.

        :param status: HTTP status code.
        :param code: Machine code from the error envelope, when present.
        :returns: The exception class to raise.
        """
        # A spent allowance and a momentary rate limit share status 429 but
        # need opposite responses from the caller, so the code decides.
        if status == 429 and code and code.lower() in cls.QUOTA_CODES:
            return QuotaExceededError
        chosen = cls.BY_STATUS.get(status)
        if chosen is not None:
            return chosen
        return ServerError if status >= cls.SERVER_FLOOR else AstroMansionError
