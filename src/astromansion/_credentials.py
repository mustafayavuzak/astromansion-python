"""src/astromansion/_credentials.py: Where the key comes from and where it may go.

The process-wide key that ``set_api_key`` stores is the package's one piece of
mutable state, so it has one owner here that names it and one place that
changes it. A key is looked up in this order, and the first one found wins::

    api_key argument ──► set_api_key(...) ──► ASTROMANSION_API_KEY ──► no key

The key travels only in ``X-API-Key``, never in a query string where it would
reach server logs and browser history, and only to a published API path.
"""

from __future__ import annotations

from typing import ClassVar

from .errors import AuthenticationError, ValidationError
from .models.constants.api import ApiConstants, KeyMaskConstants
from .models.constants.errors import ErrorConstants
from .models.constants.package import PackageConstants
from .settings import Settings


class Credentials:
    """Resolve, require, mask, and attach the API key, and keep it on the API.

    ``_shared`` holds the key ``set_api_key`` stored for the module-level
    shortcuts, or ``None``. Only :meth:`share` changes it. A client's own
    ``api_key`` argument always wins over it, so one client can differ from
    the process default.
    """

    _shared: ClassVar[str | None] = None

    @classmethod
    def share(cls, api_key: str | None) -> None:
        """Store or clear the process-wide key.

        Args:
            api_key: The key the shortcuts should use. ``None`` or blank text
                clears it, so the environment is read again.
        """
        cls._shared = (api_key or "").strip() or None

    @classmethod
    def resolve(cls, api_key: str | None) -> str | None:
        """Return the key to send, in the documented order of precedence.

        Args:
            api_key: Key passed to the client's constructor, if any. Blank
                text counts as no key.

        Returns:
            The argument, else the shared key, else ``ASTROMANSION_API_KEY``,
            each stripped; ``None`` when no source supplies one.
        """
        if api_key and api_key.strip():
            return api_key.strip()
        if cls._shared:
            return cls._shared
        return Settings.api_key()

    @staticmethod
    def require(api_key: str | None) -> None:
        """Refuse before the network when no key is available.

        A local failure names the missing configuration. Sending the request
        instead spends a round trip to be told the same thing less clearly.
        The message also names ``require_key=False``, the explicit way to try
        the endpoints the API serves to visitors before creating an account.

        Args:
            api_key: The resolved key, or ``None``.

        Raises:
            AuthenticationError: No key from any source.
        """
        if not api_key:
            raise AuthenticationError(
                "No API key. Pass AstroMansion(api_key=...), call "
                f"astromansion.set_api_key(...), or set {ApiConstants.KEY_ENV}. "
                "To try the visitor endpoints without an account, pass "
                "AstroMansion(require_key=False).",
                error_code=ErrorConstants.MISSING_API_KEY,
            )

    @staticmethod
    def base_url(base_url: str | None) -> str:
        """Return the API root without a trailing slash.

        Trimming here keeps a configured ``.../`` from building ``//v1/natal``.

        Args:
            base_url: Root passed to the constructor, if any.

        Returns:
            The argument, else ``ASTROMANSION_BASE_URL``, else production.

        Examples:
            >>> Credentials.base_url("https://api.example.test/")
            'https://api.example.test'
        """
        chosen = base_url or Settings.base_url() or ApiConstants.BASE_URL
        return chosen.rstrip("/")

    @staticmethod
    def headers(api_key: str | None) -> dict[str, str]:
        """Build the headers every request of a client carries.

        Args:
            api_key: The resolved key; ``None`` sends no key header, which the
                API answers as a visitor.

        Returns:
            JSON content negotiation, the package's User-Agent, and the key
            header when there is a key.

        Examples:
            >>> sorted(Credentials.headers(None))
            ['Accept', 'Content-Type', 'User-Agent']
            >>> Credentials.headers("am_live_key")["X-API-Key"]
            'am_live_key'
        """
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": PackageConstants.USER_AGENT,
        }
        if api_key:
            headers[ApiConstants.KEY_HEADER] = api_key
        return headers

    @staticmethod
    def mask(api_key: str | None) -> str:
        """Return a key that is safe to print.

        Args:
            api_key: The key, or ``None``.

        Returns:
            Its first eight characters, an ellipsis, and its last four. A key
            of at most twelve characters becomes an ellipsis alone, since its
            two ends would be all of it. No key becomes ``none``.

        Examples:
            >>> Credentials.mask("am_live_0123456789abcdef")
            'am_live_…cdef'
            >>> Credentials.mask("am_live_0123")
            '…'
            >>> Credentials.mask(None)
            'none'
        """
        if not api_key:
            return KeyMaskConstants.ABSENT
        if len(api_key) <= KeyMaskConstants.SHORT_KEY_MAX_CHARS:
            return KeyMaskConstants.ELLIPSIS
        return (
            f"{api_key[: KeyMaskConstants.VISIBLE_PREFIX_CHARS]}"
            f"{KeyMaskConstants.ELLIPSIS}"
            f"{api_key[-KeyMaskConstants.VISIBLE_SUFFIX_CHARS :]}"
        )

    @staticmethod
    def check_path(path: object) -> None:
        """Refuse a target that is not a published API path.

        ``request`` exists so a caller can reach a path this release does not
        name. A path is all it may reach: the client attaches the key to every
        call, so an absolute URL would hand that key to whichever host the
        string named.

        Args:
            path: The path a caller passed to ``request``.

        Raises:
            ValidationError: The target is not text, is absolute, or lies
                outside the API's published paths.

        Examples:
            >>> Credentials.check_path("/v1/natal")
            >>> Credentials.check_path("https://elsewhere.example/v1/natal")
            ... # doctest: +ELLIPSIS
            Traceback (most recent call last):
                ...
            astromansion.errors.ValidationError: path must be a relative API path...
        """
        if not isinstance(path, str):
            raise ValidationError(
                f"path must be a string, got {type(path).__name__}",
                error_code=ErrorConstants.VALIDATION,
            )
        text = path.strip()
        if text.startswith("//") or "://" in text:
            raise ValidationError(
                'path must be a relative API path such as "/v1/natal"; '
                f"refusing to send the API key to {text!r}",
                error_code=ErrorConstants.VALIDATION,
            )
        if not text.startswith(ApiConstants.PATH_PREFIX):
            raise ValidationError(
                f"path must begin with {ApiConstants.PATH_PREFIX!r}, got {path!r}",
                error_code=ErrorConstants.VALIDATION,
            )
