"""Synchronous AstroMansion API client."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx

from . import _core, config
from ._methods import SyncEndpoints
from .constants import Catalog, Package, Retry, Timeouts
from .errors import AstroMansionConnectionError, ErrorPolicy, ServerError
from .response import Result


class AstroMansion(SyncEndpoints):
    """Talk to the AstroMansion API.

    The key is read from :func:`astromansion.set_api_key` or the
    ``ASTROMANSION_API_KEY`` environment variable when it is not passed, which
    keeps it out of source files.

    Usage::

        from astromansion import AstroMansion

        client = AstroMansion()
        chart = client.natal(date="2000-01-01", time="12:00",
                             lat=51.4779, lon=0.0,
                             timezone="Europe/London")
        print(chart.summary.Sun.sign)

    The instance holds a connection pool, so build one and keep it. It is also
    a context manager, which closes the pool on exit.

    :param api_key: API key. Falls back to the module key, then the
        environment.
    :param base_url: API root. Falls back to ``ASTROMANSION_BASE_URL``, then
        production. A trailing slash is trimmed.
    :param timeout: Read timeout in seconds, or an ``httpx.Timeout``.
    :param max_retries: Retries for connection failures, rate limits and
        server errors. Validation and permission failures are never retried.
    :param require_key: Refuse before the network when no key is available.
        Set False to reach the endpoints the API serves to visitors.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float | httpx.Timeout = Timeouts.READ,
        max_retries: int = Retry.MAX_ATTEMPTS,
        require_key: bool = True,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._api_key = _core.Credentials.resolve(api_key)
        self._require_key = bool(require_key)
        if self._require_key:
            _core.Credentials.require(self._api_key)
        self.base_url = _core.Credentials.base_url(base_url)
        self.max_retries = max(0, int(max_retries))
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=(
                timeout
                if isinstance(timeout, httpx.Timeout)
                else httpx.Timeout(timeout, connect=Timeouts.CONNECT)
            ),
            headers=_core.Credentials.headers(self._api_key, Package.user_agent()),
            transport=transport,
        )

    def __enter__(self) -> AstroMansion:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        """Release the connection pool."""
        self._client.close()

    def __repr__(self) -> str:
        # Masked deliberately: reprs reach logs, tracebacks and notebooks.
        return (
            f"AstroMansion(base_url={self.base_url!r}, "
            f"api_key={_core.Credentials.mask(self._api_key)!r})"
        )

    # ---------------------------------------------------------------- core

    def request(
        self,
        method: str,
        path: str,
        *,
        require_key: bool | None = None,
        binary: bool = False,
        technique: str | None = None,
        enveloped: bool | None = None,
        **kwargs: Any,
    ) -> Any:
        """Call any endpoint, including ones without a named method here.

        The API publishes more endpoints than this class names, so this is the
        supported way to reach the rest::

            client.request("POST", "/v1/harmonics", json={"birth": {...}})

        Authentication, timeouts, retries and error mapping behave exactly as
        they do for the named methods.

        :param method: HTTP verb.
        :param path: Path beginning with ``/v1/``.
        :param require_key: Override the client's key requirement.
        :param kwargs: Passed to the transport, notably ``json``.
        :returns: Decoded response; a mapping gains attribute access, a
            non-JSON body is returned as bytes.
        :raises AstroMansionError: The API refused, or never answered.
        """
        _core.Route.check(path)
        needs_key = self._require_key if require_key is None else require_key
        if needs_key:
            _core.Credentials.require(self._api_key)

        last: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.request(method, path, **kwargs)
            except httpx.HTTPError as error:
                # A request that never completed cannot have been counted, so
                # repeating it cannot spend the allowance twice.
                last = error
                if attempt >= self.max_retries:
                    raise AstroMansionConnectionError(
                        f"could not reach the AstroMansion API: {error}",
                    ) from error
                time.sleep(_core.Backoff.delay(attempt, None))
                continue

            if attempt < self.max_retries and ErrorPolicy.is_retryable(
                response.status_code,
                _core.Envelope.code_of(response),
            ):
                time.sleep(
                    _core.Backoff.delay(
                        attempt,
                        _core.Backoff.parse_header(response.headers.get("Retry-After")),
                    )
                )
                continue
            return _decode(response, binary, technique, enveloped)

        raise AstroMansionConnectionError(
            f"could not reach the AstroMansion API: {last}",
        )

    def bodies(
        self,
        *categories: str,
        payload: dict[str, Any] | None = None,
        page_size: int = Catalog.PAGE_MAX,
        options: dict[str, Any] | None = None,
        confirm_large: bool = False,
        on_page: Callable[[int, int, dict[str, list[Any]]], None] | None = None,
        **fields: Any,
    ) -> dict[str, list[Any]]:
        """Read whole catalog categories, following the paging for you.

        ``chart`` answers one page at a time and the catalog is larger than
        one page, so this walks it. Naming several categories reads them in
        one walk rather than one walk each::

            found = client.bodies(
                "fixed_stars", "arabic_lots",
                date="2000-01-01", time="12:00",
                lat=51.4779, lon=0.0, timezone="Europe/London",
            )
            found["fixed_stars"]   # every star
            found["arabic_lots"]   # every lot

        The return is always a mapping keyed by the categories asked for, one
        category or several, so the shape never depends on how many.

        Some categories are enormous. ``asteroids`` is twenty-eight thousand
        bodies and a hundred and seventy-seven round trips, which looks like
        a hung program because nothing is printed until the last page lands.
        A walk that turns out that large stops after the first page and tells
        you the size; pass ``confirm_large=True`` to read it anyway, or
        ``on_page`` to watch it arrive.

        :param categories: Category keys, such as ``fixed_stars``.
        :param payload: Birth fields as a mapping, instead of keywords.
        :param page_size: Bodies per request. Lower it and you buy nothing
            but round trips; the default is the largest the API serves.
        :param options: Further chart options, carried on every page.
        :param confirm_large: Read a category too large to read by accident.
        :param on_page: Called after each page with the request count, the
            requests still expected, and the rows gathered so far.
        :param fields: Birth fields passed flat.
        :returns: Mapping from category key to its rows.
        :raises ValidationError: No category, a page size the API refuses, or
            a category large enough to need ``confirm_large``.
        :raises AstroMansionError: The API refused, or never answered.
        """
        collected: dict[str, list[Any]] = {name: [] for name in categories}
        offset = 0
        for pass_number in range(Catalog.PAGE_CEILING):
            page = self._chart(
                "/v1/chart",
                payload,
                _core.Pages.options(categories, options, offset, page_size),
                technique="chart",
                **fields,
            )
            requests = pass_number + 1
            following = _core.Pages.absorb(page, collected, offset)
            if requests == 1 and not confirm_large:
                _core.Pages.guard_size(page, page_size, categories)
            if on_page is not None:
                on_page(requests, _core.Pages.remaining(page, page_size),
                        collected)
            if following is None:
                return collected
            offset = following
        raise ServerError(
            f"the catalog walk passed {Catalog.PAGE_CEILING} pages without "
            "reaching the end; returning what was read would look complete "
            "while missing the rest",
            error_code="pagination",
        )

    # The generated twin takes one body mapping; this keeps the two
    # charts positional, which is the signature already released.
    def render_sharecard(  # type: ignore[override]
        self,
        birth: dict[str, Any] | None = None,
        partner: dict[str, Any] | None = None,
        *,
        type: str = "synastry",
        name: str | None = None,
        names: tuple[str, ...] | list[str] | None = None,
        lang: str | None = None,
        output: str | Path | None = None,
        **extra: Any,
    ) -> bytes | Path:
        """Story card for one chart or for two. Wraps ``POST /v1/render/sharecard``.

        One endpoint draws both cards. ``type="synastry"`` reads both charts
        and leads on the compatibility score; ``type="natal"`` reads ``birth``
        alone and leads on the Sun, Moon and Ascendant.

        Written by hand rather than generated so the two charts stay
        positional: they were positional before the natal card existed, and a
        released signature is not worth breaking over a new option.

        :param birth: The chart as a mapping, or the first of two. Birth
            fields may also be passed flat, as the other chart methods take
            them.
        :param partner: The second chart. Required for a synastry card.
        :param type: ``synastry`` or ``natal``.
        :param name: The single display name a natal card prints. Shorthand
            for a one-entry ``names``, so a one-chart card does not have to
            invent a second person.
        :param names: Display names: one for a natal card, two for a synastry
            card.
        :param lang: Card language, ``en`` or ``tr``.
        :param output: Path to write the SVG to, or ``None`` for the bytes.
        :returns: The SVG bytes, or the path written.
        """
        # Three call styles reach the same body: two mappings positionally,
        # the same as keywords, or one chart's fields passed flat.
        chart = dict(birth) if birth is not None else {
            key: extra.pop(key) for key in list(extra)
            if key in config.Body.BIRTH_FIELDS
        }
        body: dict[str, Any] = {"birth": config.Body.birth(**chart), "type": type}
        if partner is not None:
            body["partner"] = config.Body.birth(**partner)
        if name is not None and names is not None:
            raise ValueError("pass either name or names, not both")
        if name is not None:
            body["names"] = [name]
        elif names is not None:
            body["names"] = list(names)
        if lang is not None:
            body["lang"] = lang
        body.update({key: value for key, value in extra.items()
                     if value is not None})
        return self._document(
            self.request("POST", "/v1/render/sharecard", json=body,
                         binary=True, technique="render_sharecard",
                         enveloped=None),
            output,
        )

    @staticmethod
    def _document(content: Any, output: str | Path | None) -> Any:
        """Return a document, or the path it was written to.

        Bytes come back unless a path is named, so a call cannot overwrite a
        file the caller did not choose.

        :param content: The decoded response.
        :param output: Path to write to, or ``None`` to keep the bytes.
        :returns: The bytes, or the path written.
        """
        if output is None or not isinstance(content, bytes):
            return content
        destination = Path(output)
        destination.write_bytes(content)
        return destination

    def _chart(
        self,
        path: str,
        payload: dict[str, Any] | None,
        options: dict[str, Any] | None,
        *,
        binary: bool = False,
        technique: str | None = None,
        enveloped: bool | None = None,
        **fields: Any,
    ) -> Any:
        return self.request(
            "POST",
            path,
            binary=binary,
            technique=technique,
            enveloped=enveloped,
            json=config.Body.chart(payload, options, fields),
        )

    def _pair(
        self,
        path: str,
        birth: dict[str, Any],
        partner: dict[str, Any],
        options: dict[str, Any] | None,
        *,
        binary: bool = False,
        technique: str | None = None,
        enveloped: bool | None = None,
        **extra: Any,
    ) -> Any:
        return self.request(
            "POST",
            path,
            binary=binary,
            technique=technique,
            enveloped=enveloped,
            json=config.Body.pair(birth, partner, options, extra),
        )



def _decode(
    response: httpx.Response,
    binary: bool = False,
    technique: str | None = None,
    enveloped: bool | None = None,
) -> Any:
    """Raise on failure, otherwise return the decoded body.

    Shared by both clients so a status means the same thing in each.
    """
    payload: Any = None
    if not binary:
        try:
            payload = response.json()
        except ValueError:
            payload = None
    elif response.status_code >= 400:
        # A failed document request still answers with the JSON envelope.
        try:
            payload = response.json()
        except ValueError:
            payload = None
    _core.Envelope.raise_for_status(
        response.status_code,
        payload,
        response.headers,
        response.headers.get("X-Request-ID"),
    )
    if payload is None:
        if _core.Media.is_text(response.headers.get("Content-Type")):
            # A rendered table is meant to be printed. Handing back bytes
            # would print the repr, escape sequences and all, and the box
            # drawing the server sent would be unreadable.
            return response.text
        # A success that is not JSON is a document: PDF, PNG, SVG or CSV.
        return response.content
    return Result.build(payload, technique=technique, enveloped=enveloped)
