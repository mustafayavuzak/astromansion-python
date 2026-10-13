"""src/astromansion/async_client.py: The asynchronous AstroMansion client.

The same surface as :class:`~astromansion.AstroMansion`, awaited. Python cannot
make one class serve both, so this one shares everything that does not wait:
key handling, bodies, decoding, and paging live in the modules both import.
Only the waiting differs, ``await`` and ``asyncio.sleep`` in place of a block.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx

from ._backoff import Backoff
from ._bodies import RequestBodies
from ._credentials import Credentials
from ._methods_async import AsyncEndpoints
from ._paging import CatalogPages
from ._responses import Responses
from .errors import AstroMansionConnectionError, ErrorPolicy
from .models.constants.bodies import RequestBodyConstants
from .models.constants.catalog import CatalogConstants
from .models.constants.transport import RetryConstants, TimeoutConstants


class AsyncAstroMansion(AsyncEndpoints):
    """The same API as :class:`~astromansion.AstroMansion`, awaited.

    Written for callers already inside an event loop, such as a FastAPI route
    or a chat bot, where the blocking client would stall everything else.

    Attributes:
        base_url: The API root requests go to, without a trailing slash.
        max_retries: Repeats allowed after a failed first attempt.

    Examples:
        Build, await, and close::

            from astromansion import AsyncAstroMansion

            async with AsyncAstroMansion() as client:
                chart = await client.natal(
                    date="2000-01-01", time="12:00",
                    lat=51.4779, lon=0.0, timezone="Europe/London",
                )
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = TimeoutConstants.READ_SECONDS,
        max_retries: int = RetryConstants.MAX_RETRIES,
        require_key: bool = True,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """Resolve the key and open the connection pool.

        The key is checked before httpx reads the proxy environment, so a
        missing key is reported as a missing key.

        Args:
            api_key: API key. Falls back to the shared key, then the environment.
            base_url: API root. Falls back to ``ASTROMANSION_BASE_URL``, then
                production. A trailing slash is trimmed.
            timeout: Read timeout in seconds.
            max_retries: Retries for connection failures, rate limits, and
                server errors. Negative values count as zero.
            require_key: Refuse before the network when no key is available.
                Set False to reach the endpoints the API serves to visitors.
            transport: An httpx transport to send through, as tests do.

        Raises:
            AuthenticationError: ``require_key`` is set and no key was found.
        """
        self._api_key = Credentials.resolve(api_key)
        self._require_key = bool(require_key)
        if self._require_key:
            Credentials.require(self._api_key)
        self.base_url = Credentials.base_url(base_url)
        self.max_retries = max(0, int(max_retries))
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout, connect=TimeoutConstants.CONNECT_SECONDS),
            headers=Credentials.headers(self._api_key),
            transport=transport,
        )

    async def __aenter__(self) -> AsyncAstroMansion:
        """Enter an ``async with`` block.

        Returns:
            This client.
        """
        return self

    async def __aexit__(self, *_exc: object) -> None:
        """Close the connection pool on leaving the ``async with`` block.

        Args:
            _exc: The exception details, which are not suppressed.
        """
        await self.aclose()

    async def aclose(self) -> None:
        """Release the connection pool. The client cannot send after this."""
        await self._client.aclose()

    def __repr__(self) -> str:
        """Describe the client with its key masked, since reprs reach logs.

        Returns:
            The base URL and the masked key.
        """
        return (
            f"AsyncAstroMansion(base_url={self.base_url!r}, "
            f"api_key={Credentials.mask(self._api_key)!r})"
        )

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
        """Call any endpoint. Awaited form of :meth:`AstroMansion.request`.

        Args:
            method: HTTP verb.
            path: A path beginning with ``/v1/``.
            require_key: Override the client's key requirement for this call.
            binary: Whether a success is a document rather than JSON.
            technique: Endpoint name the result reports when the body names none.
            enveloped: Whether a success is wrapped in ``{technique, result}``;
                ``None`` lets the body decide.
            **kwargs: Passed to httpx, notably ``json`` and ``params``.

        Returns:
            A :class:`Result` for JSON, ``str`` for ``text/plain``, and
            ``bytes`` for any other document.

        Raises:
            ValidationError: The path is not a published API path.
            AuthenticationError: A key is required and none was found.
            AstroMansionConnectionError: No answer arrived after every retry.
            AstroMansionError: The API refused the call.
        """
        Credentials.check_path(path)
        needs_key = self._require_key if require_key is None else require_key
        if needs_key:
            Credentials.require(self._api_key)

        last: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(method, path, **kwargs)
            except httpx.HTTPError as error:
                # A request that never completed cannot have been counted, so
                # repeating it cannot spend the allowance twice.
                last = error
                if attempt >= self.max_retries:
                    raise AstroMansionConnectionError(
                        f"could not reach the AstroMansion API: {error}",
                    ) from error
                await asyncio.sleep(Backoff.delay(attempt, None))
                continue

            if attempt < self.max_retries and ErrorPolicy.is_retryable(
                response.status_code,
                Responses.error_code(response),
            ):
                await asyncio.sleep(
                    Backoff.delay(attempt, Backoff.retry_after(response.headers))
                )
                continue
            return Responses.decode(response, binary, technique, enveloped)

        raise AstroMansionConnectionError(
            f"could not reach the AstroMansion API: {last}",
        )

    async def bodies(
        self,
        *categories: str,
        payload: dict[str, Any] | None = None,
        page_size: int = CatalogConstants.PAGE_MAX,
        options: dict[str, Any] | None = None,
        confirm_large: bool = False,
        on_page: Callable[[int, int, dict[str, list[Any]]], None] | None = None,
        **fields: Any,
    ) -> dict[str, list[Any]]:
        """Read whole catalog categories. Awaited form of :meth:`AstroMansion.bodies`.

        Args:
            *categories: Category keys, such as ``fixed_stars``.
            payload: Birth fields as one mapping, instead of keywords.
            page_size: Bodies per request; the default is the largest the API serves.
            options: Further chart options, carried on every page.
            confirm_large: Read a category too large to read by accident.
            on_page: Called after each page with the requests made, the
                requests still expected, and the rows gathered so far.
            **fields: Birth fields passed as keywords.

        Returns:
            Each category asked for, mapped to all of its rows.

        Raises:
            ValidationError: No category, a page size the API refuses, or a
                category large enough to need ``confirm_large``.
            ServerError: The answers never ended the walk.
            AstroMansionError: The API refused, or never answered.
        """
        collected: dict[str, list[Any]] = {name: [] for name in categories}
        offset = 0
        for pass_number in range(CatalogConstants.PAGE_CEILING):
            page = await self._chart(
                CatalogConstants.PATH,
                payload,
                CatalogPages.options(categories, options, offset, page_size),
                technique=CatalogConstants.TECHNIQUE,
                **fields,
            )
            requests = pass_number + 1
            following = CatalogPages.absorb(page, collected, offset)
            if requests == 1 and not confirm_large:
                CatalogPages.guard_size(page, page_size, categories)
            if on_page is not None:
                on_page(requests, CatalogPages.remaining(page, page_size), collected)
            if following is None:
                return collected
            offset = following
        raise CatalogPages.exhausted()

    async def render_sharecard(
        self,
        birth: dict[str, Any] | None = None,
        partner: dict[str, Any] | None = None,
        *,
        type: str = RequestBodyConstants.SHARECARD_SYNASTRY,
        name: str | None = None,
        names: tuple[str, ...] | list[str] | None = None,
        lang: str | None = None,
        output: str | Path | None = None,
        **extra: Any,
    ) -> bytes | Path:
        """Draw a story card. Awaited form of :meth:`AstroMansion.render_sharecard`.

        Args:
            birth: The chart as a mapping, or the first of two. Birth fields
                may also be passed flat among ``extra``.
            partner: The second chart. Required for a synastry card.
            type: ``synastry`` or ``natal``.
            name: The single display name a natal card prints.
            names: Display names, one for a natal card and two for a synastry card.
            lang: Card language, ``en`` or ``tr``.
            output: Path to write the SVG to, or ``None`` for the bytes.
            **extra: Further body fields, or one chart's birth fields.

        Returns:
            The SVG bytes, or the path written.

        Raises:
            ValueError: Both ``name`` and ``names`` were given.
            ValidationError: A birth field is malformed, or the API refused the card.
            AstroMansionError: The API refused, or never answered.
        """
        return Responses.save_document(
            await self.request(
                "POST",
                RequestBodyConstants.SHARECARD_PATH,
                json=RequestBodies.sharecard(
                    birth,
                    partner,
                    card_type=type,
                    name=name,
                    names=names,
                    lang=lang,
                    extra=extra,
                ),
                binary=True,
                technique=RequestBodyConstants.SHARECARD_TECHNIQUE,
                enveloped=None,
            ),
            output,
        )

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
        """Send a one-person request, the hook every generated chart method awaits.

        Args:
            path: The endpoint's path.
            payload: Birth fields as one mapping, if the caller passed one.
            options: The endpoint's options.
            binary: Whether a success is a document.
            technique: The endpoint's name.
            enveloped: Whether a success is wrapped, or ``None``.
            **fields: Birth fields passed as keywords.

        Returns:
            What :meth:`request` returns.
        """
        return await self.request(
            "POST",
            path,
            binary=binary,
            technique=technique,
            enveloped=enveloped,
            json=RequestBodies.chart(payload, options, fields),
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
        """Send a two-person request, the hook every generated pair method awaits.

        Args:
            path: The endpoint's path.
            birth: The first person's birth fields.
            partner: The second person's birth fields.
            options: The endpoint's options.
            binary: Whether a success is a document.
            technique: The endpoint's name.
            enveloped: Whether a success is wrapped, or ``None``.
            **extra: Further top-level body fields.

        Returns:
            What :meth:`request` returns.
        """
        return await self.request(
            "POST",
            path,
            binary=binary,
            technique=technique,
            enveloped=enveloped,
            json=RequestBodies.pair(birth, partner, options, extra),
        )
