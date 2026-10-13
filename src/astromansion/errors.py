"""src/astromansion/errors.py: The client's exceptions, and which one a failure becomes.

The API answers every failure with one envelope::

    {"error": {"code": "...", "message": "...", "detail": "..."}}

Each status maps to the class that names its cause, so a caller catches the
case it can act on instead of matching strings. ``AstroMansionError`` is the
one base for anything the API refused or the transport lost::

    AstroMansionError
    ├── AstroMansionConnectionError   no answer arrived
    ├── AuthenticationError           401
    ├── QuotaExceededError            402, or 429 with a quota code
    ├── PermissionDeniedError         403
    ├── NotFoundError                 404
    ├── ConflictError                 409
    ├── ValidationError               422, or refused before sending
    ├── RateLimitError                429
    └── ServerError                   500 and above
"""

from __future__ import annotations

from http import HTTPStatus
from typing import Any

from .models.constants.errors import ErrorConstants
from .models.constants.transport import RetryConstants


class AstroMansionError(Exception):
    """Base for every failure the API or the transport reports.

    Attributes:
        message: Human-readable summary.
        status_code: HTTP status, or ``None`` when no response arrived.
        error_code: Stable machine code from the error envelope, or one of the
            client's own codes such as ``missing_api_key``.
        details: Field-level explanation, when the API supplies one.
        request_id: Server request identifier, useful in a support request.
        retry_after: Seconds to wait, when the server asked for a pause.

    Examples:
        >>> error = AstroMansionError("refused", details="lat", request_id="r1")
        >>> str(error)
        'refused | lat | request_id=r1'
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
        """Record what failed and what the server said about it.

        Args:
            message: Human-readable summary.
            status_code: HTTP status, or ``None`` when no response arrived.
            error_code: Stable machine code, when there is one.
            details: Field-level explanation, when there is one.
            request_id: Server request identifier, when the server sent one.
            retry_after: Seconds to wait, when the server asked for a pause.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        self.request_id = request_id
        self.retry_after = retry_after

    def __str__(self) -> str:
        """Join the message, the details, and the request id.

        Returns:
            The parts that are present, separated by `` | ``.
        """
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
    """The plan's allowance for the period is spent.

    Raised for 402, and for a 429 whose code names a quota rather than a rate.
    """


class PermissionDeniedError(AstroMansionError):
    """The key is valid but the plan does not include this feature (403)."""


class NotFoundError(AstroMansionError):
    """No such endpoint or resource (404)."""


class ConflictError(AstroMansionError):
    """The request contradicts the current state (409)."""


class ValidationError(AstroMansionError):
    """The request was rejected (422), or refused before it was sent.

    ``details`` names the field when the API supplies one.
    """


class RateLimitError(AstroMansionError):
    """Too many requests inside the window (429).

    Separate from :class:`QuotaExceededError`: a rate limit clears on its own
    after ``retry_after`` seconds, while a spent quota needs a new period or a
    larger plan. Waiting fixes one and never fixes the other.
    """


class ServerError(AstroMansionError):
    """The API failed to answer (5xx), or answered in a way that cannot be used."""


class ErrorPolicy:
    """Decide which exception a failed response becomes, and whether to retry it.

    The taxonomy and the mapping onto it live in one module: a class added
    above without a status here would never be raised.
    """

    @staticmethod
    def is_quota(status: int, code: str | None) -> bool:
        """Return whether a 429 means a spent allowance rather than a busy moment.

        Args:
            status: HTTP status code.
            code: Machine code from the error envelope, when present.

        Returns:
            True for a 429 whose code is one of the API's quota codes.

        Examples:
            >>> ErrorPolicy.is_quota(429, "quota_exceeded")
            True
            >>> ErrorPolicy.is_quota(429, "rate_limited")
            False
        """
        return (
            status == HTTPStatus.TOO_MANY_REQUESTS
            and bool(code)
            and str(code).lower() in ErrorConstants.QUOTA_CODES
        )

    @classmethod
    def is_retryable(cls, status: int, code: str | None) -> bool:
        """Return whether repeating a refused request could ever help.

        A spent quota is not a busy moment. It answers 429 like a rate limit
        does and clears only with a new period or a larger plan, so asking
        again spends two more round trips to be told the same thing.

        Args:
            status: HTTP status code.
            code: Machine code from the error envelope, when present.

        Returns:
            True when another attempt is worth making.

        Examples:
            >>> ErrorPolicy.is_retryable(503, None)
            True
            >>> ErrorPolicy.is_retryable(429, "quota_exceeded")
            False
            >>> ErrorPolicy.is_retryable(422, None)
            False
        """
        return status in RetryConstants.STATUSES and not cls.is_quota(status, code)

    @classmethod
    def for_response(cls, status: int, code: str | None) -> type[AstroMansionError]:
        """Return the exception naming why a response failed.

        A spent allowance and a momentary rate limit share 429 but need
        opposite responses from the caller, so the code decides between them.

        Args:
            status: HTTP status code.
            code: Machine code from the error envelope, when present.

        Returns:
            The exception class to raise.

        Examples:
            >>> ErrorPolicy.for_response(401, None).__name__
            'AuthenticationError'
            >>> ErrorPolicy.for_response(429, "quota").__name__
            'QuotaExceededError'
            >>> ErrorPolicy.for_response(502, None).__name__
            'ServerError'
            >>> ErrorPolicy.for_response(418, None).__name__
            'AstroMansionError'
        """
        if cls.is_quota(status, code):
            return QuotaExceededError
        match status:
            case HTTPStatus.UNAUTHORIZED:
                return AuthenticationError
            case HTTPStatus.PAYMENT_REQUIRED:
                return QuotaExceededError
            case HTTPStatus.FORBIDDEN:
                return PermissionDeniedError
            case HTTPStatus.NOT_FOUND:
                return NotFoundError
            case HTTPStatus.CONFLICT:
                return ConflictError
            case HTTPStatus.UNPROCESSABLE_ENTITY:
                return ValidationError
            case HTTPStatus.TOO_MANY_REQUESTS:
                return RateLimitError
        if status >= HTTPStatus.INTERNAL_SERVER_ERROR:
            return ServerError
        return AstroMansionError
