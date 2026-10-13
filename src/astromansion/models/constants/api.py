"""src/astromansion/models/constants/api.py: The API's address and key names."""

from __future__ import annotations

from typing import Final


class ApiConstants:
    """The API's address, the names it reads a key under, and the paths it serves.

    ``KEY_HEADER`` is the header the published security scheme names; the API
    also accepts a bearer token, and this is its primary. ``KEY_ENV`` and
    ``BASE_URL_ENV`` are the environment variables a client falls back to.
    Every published path begins with ``PATH_PREFIX``, and ``request`` refuses
    anything else, so a mistyped or hostile target cannot carry the key off
    the API. ``REQUEST_ID_HEADER`` and ``RETRY_AFTER_HEADER`` are read from
    responses. ``TEXT_MEDIA_TYPE`` is the one content type decoded to text.
    """

    BASE_URL: Final[str] = "https://api.astromansion.com"
    PATH_PREFIX: Final[str] = "/v1/"

    KEY_HEADER: Final[str] = "X-API-Key"
    KEY_ENV: Final[str] = "ASTROMANSION_API_KEY"
    BASE_URL_ENV: Final[str] = "ASTROMANSION_BASE_URL"

    REQUEST_ID_HEADER: Final[str] = "X-Request-ID"
    RETRY_AFTER_HEADER: Final[str] = "Retry-After"
    TEXT_MEDIA_TYPE: Final[str] = "text/plain"


class KeyMaskConstants:
    """How a key is shown wherever it could be printed.

    A repr reaches logs, tracebacks, and notebooks, so a key is shown as its
    first ``VISIBLE_PREFIX_CHARS`` characters, ``ELLIPSIS``, and its last
    ``VISIBLE_SUFFIX_CHARS``. A key no longer than ``SHORT_KEY_MAX_CHARS`` is
    shown as ``ELLIPSIS`` alone, since its two ends would be all of it.
    ``ABSENT`` stands for no key at all.
    """

    VISIBLE_PREFIX_CHARS: Final[int] = 8
    VISIBLE_SUFFIX_CHARS: Final[int] = 4
    SHORT_KEY_MAX_CHARS: Final[int] = 8
    ELLIPSIS: Final[str] = "…"
    ABSENT: Final[str] = "none"
