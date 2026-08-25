"""Behaviour the two clients share, grouped by what it decides.

Written once so the surfaces cannot drift: credentials, retry timing and
response decoding are settled here, and each client supplies only its own
transport.
"""

from __future__ import annotations

import os
import random
from typing import Any, ClassVar

from .constants import Api, Catalog, Retry
from .errors import (
    AuthenticationError,
    ErrorPolicy,
    ServerError,
    ValidationError,
)
from .response import Result


class Credentials:
    """Where the key comes from and how it is carried.

    The process-wide key lives here rather than as a loose module variable,
    so the one piece of mutable state in the package has an owner that names
    it and a single place that changes it.
    """

    #: Set by ``set_api_key`` for notebook and script use. A client always
    #: prefers its own argument, so this never overrides an explicit key.
    _shared: ClassVar[str | None] = None

    @classmethod
    def share(cls, api_key: str | None) -> None:
        """Store the process-wide key."""
        cls._shared = (api_key or "").strip() or None

    @classmethod
    def shared(cls) -> str | None:
        """Return the process-wide key, if one was set."""
        return cls._shared

    @classmethod
    def resolve(cls, api_key: str | None) -> str | None:
        """Return the key to send, in the documented order of precedence.

        Explicit argument, then :meth:`share`, then the environment. An
        argument always wins, so one client can differ from the default.

        :param api_key: Key passed to the constructor, if any.
        :returns: The key, or None when no source supplies one.
        """
        if api_key and api_key.strip():
            return api_key.strip()
        if cls._shared:
            return cls._shared
        return (os.environ.get(Api.KEY_ENV) or "").strip() or None

    @staticmethod
    def base_url(base_url: str | None) -> str:
        """Return the API root without a trailing slash.

        Trimming here is what keeps a configured ``.../`` from building
        ``//v1/natal``.
        """
        chosen = base_url or os.environ.get(Api.BASE_URL_ENV) or Api.BASE_URL
        return chosen.rstrip("/")

    @staticmethod
    def mask(api_key: str | None) -> str:
        """Return a key safe to print: prefix, ellipsis, last four."""
        if not api_key:
            return "none"
        if len(api_key) <= 8:
            return "…"
        return f"{api_key[:8]}…{api_key[-4:]}"

    @staticmethod
    def headers(api_key: str | None, user_agent: str) -> dict[str, str]:
        """Build request headers.

        The key travels in the header the API documents, never in the query
        string, where it would reach server logs and browser history.
        """
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": user_agent,
        }
        if api_key:
            headers[Api.KEY_HEADER] = api_key
        return headers

    @staticmethod
    def require(api_key: str | None) -> None:
        """Refuse before the network when no key is available.

        A local failure names the missing configuration. Sending the request
        instead spends a round trip to be told the same thing less clearly.

        :raises AuthenticationError: No key from any source.
        """
        if not api_key:
            raise AuthenticationError(
                "No API key. Pass AstroMansion(api_key=...), call "
                f"astromansion.set_api_key(...), or set {Api.KEY_ENV}.",
                error_code="missing_api_key",
            )


class Backoff:
    """How long to wait before repeating a request."""

    @staticmethod
    def parse_header(value: str | None) -> float | None:
        """Read a ``Retry-After`` header expressed in seconds."""
        if not value:
            return None
        try:
            return max(0.0, float(value.strip()))
        except ValueError:
            # The header also allows an HTTP date; backoff covers that rather
            # than pulling in date parsing for a hint.
            return None

    @staticmethod
    def delay(attempt: int, retry_after: float | None) -> float:
        """Return the pause before the next attempt.

        The server's ``Retry-After`` wins when present; it knows when the
        window reopens. Otherwise exponential backoff with jitter, so clients
        that failed together do not retry together.
        """
        if retry_after is not None and retry_after >= 0:
            return min(retry_after, Retry.BACKOFF_CEILING)
        window = min(
            Retry.BACKOFF_SECONDS * (2**attempt),
            Retry.BACKOFF_CEILING,
        )
        return window * (0.5 + random.random() / 2.0)


class Envelope:
    """Reading what the API said about a response."""

    @staticmethod
    def code_of(response: Any) -> str | None:
        """Read the machine code a refusal carries, if it carries one.

        Used to decide whether repeating the request could help, which has to
        happen before the body is decoded for the caller.

        :param response: The HTTP response as it arrived.
        :returns: The error code, or ``None`` when the body names none.
        """
        try:
            payload = response.json()
        except Exception:
            return None
        return Envelope.parts(payload)[0]

    @staticmethod
    def parts(payload: Any) -> tuple[str | None, str | None, Any]:
        """Pull ``code``, ``message`` and ``detail`` out of an error body."""
        if isinstance(payload, dict):
            error = payload.get("error")
            if isinstance(error, dict):
                return (
                    error.get("code"),
                    error.get("message"),
                    error.get("detail"),
                )
            if "detail" in payload:
                return None, None, payload["detail"]
        return None, None, None

    @classmethod
    def raise_for_status(
        cls,
        status: int,
        payload: Any,
        headers: Any,
        request_id: str | None,
    ) -> None:
        """Turn a failed response into the exception that names its cause.

        A body that is not the documented envelope must not crash the client:
        the status alone still says something useful, and a caller handling
        errors should not meet a second, different error from the SDK.

        :raises AstroMansionError: For any status at or above 400.
        """
        if status < 400:
            return
        code, message, details = cls.parts(payload)
        raise ErrorPolicy.for_response(status, code)(
            message or f"AstroMansion API returned HTTP {status}",
            status_code=status,
            error_code=code,
            details=details,
            request_id=request_id,
            retry_after=Backoff.parse_header(headers.get(Retry.HEADER)),
        )

    @staticmethod
    def wrap(payload: Any) -> Any:
        """Return a mapping with attribute access, other bodies untouched."""
        if isinstance(payload, dict):
            return Result(payload)
        return payload


class Arguments:
    """Reconciling the two ways a caller may pass a body."""

    @staticmethod
    def merge(
        payload: dict[str, Any] | None,
        fields: dict[str, Any],
    ) -> dict[str, Any]:
        """Accept either a payload mapping or keyword fields, never both.

        Both styles are ergonomic and mixing them is ambiguous: it hides which
        source wins for a field named twice. The refusal is explicit.

        :param payload: Positional mapping, if the caller passed one.
        :param fields: Keyword fields, unset values already dropped.
        :returns: The chosen mapping.
        :raises TypeError: The caller supplied both forms.
        """
        given = {name: value for name, value in fields.items() if value is not None}
        if payload is None:
            return given
        if given:
            raise TypeError(
                "pass either a payload mapping or keyword arguments, not both",
            )
        if not isinstance(payload, dict):
            raise TypeError(
                f"payload must be a mapping, got {type(payload).__name__}",
            )
        return dict(payload)


class Pages:
    """Walk the paginated ``/v1/chart`` catalog.

    The arithmetic lives here so the synchronous and asynchronous clients
    share one definition of what a page is and when the walk is over. Each
    of them owns only its own way of making the call.
    """

    @staticmethod
    def options(
        categories: tuple[str, ...],
        base: dict[str, Any] | None,
        offset: int,
        limit: int,
    ) -> dict[str, Any]:
        """Build the chart options for one page of a catalog walk.

        :param categories: Category keys to read.
        :param base: Caller options the page fields are added to.
        :param offset: Zero-based offset of this page.
        :param limit: Bodies requested in this page.
        :returns: The ``options`` mapping for one request.
        :raises ValidationError: No category, or a page size the API refuses.
        """
        if not categories:
            raise ValidationError(
                'name at least one category, for example "fixed_stars"',
                error_code="validation",
            )
        if not 1 <= limit <= Catalog.PAGE_MAX:
            raise ValidationError(
                f"page_size must be within 1..{Catalog.PAGE_MAX}, got {limit!r}",
                error_code="validation",
            )
        merged = dict(base or {})
        merged.update(
            {
                "categories": list(categories),
                "catalog_offset": offset,
                "catalog_limit": limit,
            }
        )
        return merged

    @staticmethod
    def absorb(
        page: Any,
        collected: dict[str, list[Any]],
        offset: int,
    ) -> int | None:
        """Take one page's rows and report where the next page begins.

        A category is missing from ``bodies`` whenever the page happened to
        hold none of it, which is ordinary: the page is a window over the
        whole selection and the chart's own bodies fill the first of it.

        :param page: Decoded chart response.
        :param collected: Accumulator, keyed by the categories asked for.
        :param offset: Offset this page was asked for.
        :returns: Offset of the next page, or ``None`` when the walk is over.
        :raises ServerError: The walk was told to stand still, which would
            read the same page forever and count its rows each time.
        """
        data = page.data if hasattr(page, "data") else page
        bodies = data.get("bodies") or {}
        for name, rows in collected.items():
            rows.extend(bodies.get(name) or [])
        paging = data.get("catalog_page") or {}
        following = paging.get("next_offset")
        if not isinstance(following, int):
            return None
        if following <= offset:
            raise ServerError(
                "the API asked the catalog walk to go back to offset "
                f"{following} from {offset}, which would never end",
                error_code="pagination",
            )
        return following

    @staticmethod
    def total_of(page: Any) -> int:
        """Bodies the whole selection holds, or zero when unstated."""
        data = page.data if hasattr(page, "data") else page
        paging = data.get("catalog_page") or {}
        total = paging.get("total")
        return int(total) if isinstance(total, int) else 0

    @staticmethod
    def remaining(page: Any, limit: int) -> int:
        """Requests still expected after this page."""
        data = page.data if hasattr(page, "data") else page
        paging = data.get("catalog_page") or {}
        following = paging.get("next_offset")
        total = Pages.total_of(page)
        if not isinstance(following, int) or total <= 0 or limit <= 0:
            return 0
        return max(0, -(-(total - following) // limit))

    @staticmethod
    def guard_size(page: Any, limit: int, categories: tuple[str, ...]) -> None:
        """Stop a walk that is far larger than a caller is likely to want.

        Nothing here is slow or broken; the walk would finish. But twenty-eight
        thousand asteroids is a hundred and seventy-seven round trips with no
        output until the last one, and a program that prints nothing for a
        minute is indistinguishable from a hung one. Saying the number is
        cheaper than letting somebody find out.

        :raises ValidationError: The category needs an explicit confirmation.
        """
        total = Pages.total_of(page)
        if limit <= 0:
            return
        requests = -(-total // limit)
        if requests <= Catalog.WALK_WARN_REQUESTS:
            return
        raise ValidationError(
            f"{', '.join(categories)} holds {total} bodies, which is "
            f"{requests} requests and will print nothing until the last one "
            "lands. Pass confirm_large=True to read it, on_page=... to watch "
            "it arrive, or call chart() for a single page.",
            error_code="validation",
        )


class Route:
    """Refuse to send the key anywhere but the API.

    ``request`` exists so a caller can reach a path this release does not
    name. A path is all it may reach: the client attaches the API key to
    every call it makes, so an absolute URL would hand that key to whichever
    host the string named.
    """

    @staticmethod
    def check(path: str) -> None:
        """Refuse a target that is not a published API path.

        :param path: The path a caller passed to ``request``.
        :raises ValidationError: The target is absolute, or outside the API.
        """
        if not isinstance(path, str):
            raise ValidationError(
                f"path must be a string, got {type(path).__name__}",
                error_code="validation",
            )
        text = path.strip()
        if text.startswith("//") or "://" in text:
            raise ValidationError(
                'path must be a relative API path such as "/v1/natal"; '
                f"refusing to send the API key to {text!r}",
                error_code="validation",
            )
        if not text.startswith(Api.PATH_PREFIX):
            raise ValidationError(
                f"path must begin with {Api.PATH_PREFIX!r}, got {path!r}",
                error_code="validation",
            )


class Media:
    """Tell a response meant for reading from one meant for a file."""

    @staticmethod
    def is_text(content_type: str | None) -> bool:
        """Return whether a body should be decoded to text.

        Only ``text/plain`` qualifies. A CSV export and an SVG wheel are
        documents the caller writes to disk, and turning those into ``str``
        would break every ``open(path, "wb")`` already written against them.

        :param content_type: The response's ``Content-Type``, if it sent one.
        :returns: True when the body is prose or a rendered table.
        """
        if not content_type:
            return False
        return content_type.split(";")[0].strip().lower() == "text/plain"
