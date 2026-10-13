"""src/astromansion/_paging.py: Walk the paginated ``/v1/chart`` catalog.

The arithmetic lives here so the synchronous and the asynchronous client share
one definition of a page and of when the walk is over. Each client owns only
its own way of making the call::

    page 1 ──► options(offset=0)   ──► absorb ──► next offset ─┐
                                    guard_size (first page)     │
    page n ──► options(offset=n)   ──► absorb ──► None ──► done ◄┘
    after PAGE_CEILING pages       ──► exhausted() is raised
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .errors import ServerError, ValidationError
from .models.constants.catalog import CatalogConstants
from .models.constants.errors import ErrorConstants


class CatalogPages:
    """Build each page's request and read each page's answer."""

    @staticmethod
    def _paging(page: Any) -> Mapping[str, Any]:
        """Return the ``catalog_page`` block of a page, empty when it has none.

        Args:
            page: A decoded chart response, a :class:`Result` or a mapping.

        Returns:
            The block, or an empty mapping.
        """
        data = page.data if hasattr(page, "data") else page
        paging = data.get(CatalogConstants.PAGE_FIELD) or {}
        return paging if isinstance(paging, Mapping) else {}

    @staticmethod
    def options(
        categories: tuple[str, ...],
        base: Mapping[str, Any] | None,
        offset: int,
        limit: int,
    ) -> dict[str, Any]:
        """Build the chart options for one page of a catalog walk.

        Args:
            categories: Category keys to read.
            base: The caller's own options, which every page carries.
            offset: Zero-based offset of this page.
            limit: Bodies requested in this page, within 1..``PAGE_MAX``.

        Returns:
            The ``options`` mapping of one request.

        Raises:
            ValidationError: No category was named, or the page size is out of
                the range the API serves.

        Examples:
            >>> CatalogPages.options(("fixed_stars",), {"houses": "whole"}, 160, 160)
            ... # doctest: +NORMALIZE_WHITESPACE
            {'houses': 'whole', 'categories': ['fixed_stars'],
             'catalog_offset': 160, 'catalog_limit': 160}
        """
        if not categories:
            raise ValidationError(
                'name at least one category, for example "fixed_stars"',
                error_code=ErrorConstants.VALIDATION,
            )
        if not 1 <= limit <= CatalogConstants.PAGE_MAX:
            raise ValidationError(
                f"page_size must be within 1..{CatalogConstants.PAGE_MAX}, "
                f"got {limit!r}",
                error_code=ErrorConstants.VALIDATION,
            )
        merged = dict(base or {})
        merged.update(
            {
                CatalogConstants.CATEGORIES_FIELD: list(categories),
                CatalogConstants.OFFSET_FIELD: offset,
                CatalogConstants.LIMIT_FIELD: limit,
            }
        )
        return merged

    @classmethod
    def absorb(
        cls, page: Any, collected: dict[str, list[Any]], offset: int
    ) -> int | None:
        """Take one page's rows and report where the next page begins.

        A category is missing from ``bodies`` whenever the page held none of
        it, which is ordinary: the page is a window over the whole selection,
        and the chart's own bodies fill the first of it.

        Args:
            page: The decoded chart response.
            collected: Rows gathered so far, keyed by the categories asked for;
                this page's rows are appended to it.
            offset: The offset this page was asked for.

        Returns:
            The offset of the next page, or ``None`` when the walk is over.

        Raises:
            ServerError: The answer told the walk to stand still or go back,
                which would read the same page forever.
        """
        data = page.data if hasattr(page, "data") else page
        bodies = data.get(CatalogConstants.BODIES_FIELD) or {}
        for name, rows in collected.items():
            rows.extend(bodies.get(name) or [])
        following = cls._paging(page).get(CatalogConstants.NEXT_OFFSET_FIELD)
        if not isinstance(following, int):
            return None
        if following <= offset:
            raise ServerError(
                "the API asked the catalog walk to go back to offset "
                f"{following} from {offset}, which would never end",
                error_code=ErrorConstants.PAGINATION,
            )
        return following

    @classmethod
    def total_of(cls, page: Any) -> int:
        """Return how many bodies the whole selection holds.

        Args:
            page: A decoded chart response.

        Returns:
            The total the page states, or zero when it states none.
        """
        total = cls._paging(page).get(CatalogConstants.TOTAL_FIELD)
        return int(total) if isinstance(total, int) else 0

    @classmethod
    def remaining(cls, page: Any, limit: int) -> int:
        """Return how many requests the walk still expects after this page.

        Args:
            page: A decoded chart response.
            limit: Bodies per request.

        Returns:
            The requests still needed, or zero when the page ends the walk or
            states no total.
        """
        following = cls._paging(page).get(CatalogConstants.NEXT_OFFSET_FIELD)
        total = cls.total_of(page)
        if not isinstance(following, int) or total <= 0 or limit <= 0:
            return 0
        return max(0, -(-(total - following) // limit))

    @classmethod
    def guard_size(cls, page: Any, limit: int, categories: tuple[str, ...]) -> None:
        """Stop a walk far larger than a caller is likely to want.

        Nothing here is slow or broken, and the walk would finish. But a walk
        that prints nothing for a minute cannot be told apart from a hung
        program, and saying the number is cheaper than letting somebody find
        out.

        Args:
            page: The first page's decoded response.
            limit: Bodies per request.
            categories: The categories being read, named in the message.

        Raises:
            ValidationError: The walk would take more than
                ``WALK_WARN_REQUESTS`` requests.
        """
        total = cls.total_of(page)
        if limit <= 0:
            return
        requests = -(-total // limit)
        if requests <= CatalogConstants.WALK_WARN_REQUESTS:
            return
        raise ValidationError(
            f"{', '.join(categories)} holds {total} bodies, which is "
            f"{requests} requests and will print nothing until the last one "
            "lands. Pass confirm_large=True to read it, on_page=... to watch "
            "it arrive, or call chart() for a single page.",
            error_code=ErrorConstants.VALIDATION,
        )

    @staticmethod
    def exhausted() -> ServerError:
        """Return the error of a walk that passed ``PAGE_CEILING`` pages.

        Returning what was read would look complete while missing the rest, so
        the walk fails instead.

        Returns:
            The error for the client to raise.
        """
        return ServerError(
            f"the catalog walk passed {CatalogConstants.PAGE_CEILING} pages without "
            "reaching the end; returning what was read would look complete "
            "while missing the rest",
            error_code=ErrorConstants.PAGINATION,
        )
