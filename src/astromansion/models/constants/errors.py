"""src/astromansion/models/constants/errors.py: Machine codes of failures."""

from __future__ import annotations

from typing import Final


class ErrorConstants:
    """The API's quota codes and the codes the client raises on its own.

    ``QUOTA_CODES`` are the API codes that mean a spent allowance even when
    the status is 429: a rate limit clears by waiting, a spent quota does
    not. ``MISSING_API_KEY``, ``VALIDATION``, and ``PAGINATION`` are the
    ``error_code`` values of failures the client detects before or after a
    request, in the same vocabulary the API uses.
    """

    QUOTA_CODES: Final[frozenset[str]] = frozenset(
        {
            "quota_exceeded",
            "quota",
            "monthly_quota_exceeded",
        }
    )

    MISSING_API_KEY: Final[str] = "missing_api_key"
    VALIDATION: Final[str] = "validation"
    PAGINATION: Final[str] = "pagination"
