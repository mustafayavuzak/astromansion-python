"""Asynchronous AstroMansion API client."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx

from . import _core, config
from ._methods_async import AsyncEndpoints
from .client import _decode
from .constants import Catalog, Package, Retry, Timeouts
from .errors import AstroMansionConnectionError, ErrorPolicy, ServerError


class AsyncAstroMansion(AsyncEndpoints):
    """The same API as :class:`~astromansion.AstroMansion`, awaited.

    Written for callers already inside an event loop, such as a FastAPI route
    or a chat bot, where the blocking client would stall everything else.

    Usage::

        from astromansion import AsyncAstroMansion

        async with AsyncAstroMansion() as client:
            chart = await client.natal(
                date="1990-07-19", time="14:30",
                lat=41.0082, lon=28.9784, timezone=3,
            )

    :param api_key: API key. Falls back to ``ASTROMANSION_API_KEY``.
    :param base_url: API root. Falls back to the environment, then production.
    :param timeout: Read timeout in seconds.
    :param max_retries: Retries for rate limits and server errors.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = Timeouts.READ,
        max_retries: int = Retry.MAX_ATTEMPTS,
        require_key: bool = True,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._api_key = _core.Credentials.resolve(api_key)
        self._require_key = bool(require_key)
        # See ``AstroMansion.__init__``: the key is checked before httpx reads
        # the proxy environment, so a missing key names itself.
        if self._require_key:
            _core.Credentials.require(self._api_key)
        self.base_url = _core.Credentials.base_url(base_url)
        self.max_retries = max(0, int(max_retries))
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout, connect=Timeouts.CONNECT),
            headers=_core.Credentials.headers(self._api_key, Package.user_agent()),
            transport=transport,
        )

    async def __aenter__(self) -> AsyncAstroMansion:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Release the connection pool."""
        await self._client.aclose()

    def __repr__(self) -> str:
        return (
            f"AsyncAstroMansion(base_url={self.base_url!r}, "
            f"api_key={_core.Credentials.mask(self._api_key)!r})"
        )

    # ---------------------------------------------------------------- core

    async def request(
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
        """Call any endpoint. See :meth:`AstroMansion.request`."""
        _core.Route.check(path)
        needs_key = self._require_key if require_key is None else require_key
        if needs_key:
            _core.Credentials.require(self._api_key)
        last: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(method, path, **kwargs)
            except httpx.HTTPError as error:
                last = error
                if attempt >= self.max_retries:
                    raise AstroMansionConnectionError(
                        f"could not reach the AstroMansion API: {error}",
                    ) from error
                await asyncio.sleep(_core.Backoff.delay(attempt, None))
                continue

            if attempt < self.max_retries and ErrorPolicy.is_retryable(
                response.status_code,
                _core.Envelope.code_of(response),
            ):
                await asyncio.sleep(
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

    async def bodies(
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
                date="1990-07-19", time="14:30",
                lat=41.0082, lon=28.9784, timezone=3,
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
            page = await self._chart(
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
    async def render_sharecard(  # type: ignore[override]
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
            await self.request("POST", "/v1/render/sharecard", json=body,
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

    async def _chart(
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
        return await self.request(
            "POST",
            path,
            binary=binary,
            technique=technique,
            enveloped=enveloped,
            json=config.Body.chart(payload, options, fields),
        )

    async def _pair(
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
        return await self.request(
            "POST",
            path,
            binary=binary,
            technique=technique,
            enveloped=enveloped,
            json=config.Body.pair(birth, partner, options, extra),
        )
