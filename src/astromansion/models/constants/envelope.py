"""src/astromansion/models/constants/envelope.py: The API's two body wrappers.

A successful answer is either the data itself or ``{technique, result}``. A
failure is always ``{"error": {"code", "message", "detail"}}``::

    {"technique": "chart", "result": {...}}
    {"error": {"code": "validation", "message": "...", "detail": "..."}}
"""

from __future__ import annotations

from typing import Final


class EnvelopeConstants:
    """The keys of the success wrapper and of the error envelope.

    ``KEYS`` is the whole success wrapper and nothing else. A payload that
    merely owns a ``result`` field has more keys than these and is left
    alone, so real data is never unwrapped by mistake.
    """

    TECHNIQUE_KEY: Final[str] = "technique"
    RESULT_KEY: Final[str] = "result"
    KEYS: Final[frozenset[str]] = frozenset({TECHNIQUE_KEY, RESULT_KEY})

    ERROR_KEY: Final[str] = "error"
    CODE_KEY: Final[str] = "code"
    MESSAGE_KEY: Final[str] = "message"
    DETAIL_KEY: Final[str] = "detail"
