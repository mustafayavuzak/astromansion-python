"""src/astromansion/models/constants/catalog.py: Paging the ``/v1/chart`` catalog."""

from __future__ import annotations

from typing import Final


class CatalogConstants:
    """The page sizes, limits, and wire names of a catalog walk.

    A page costs one round trip and the calculation inside it is a rounding
    error beside that, so the only sensible page is the largest the API
    serves, ``PAGE_MAX``. The engine computes at most 192 points and keeps the
    rest of them for axes and derived points. Reading the 906 unambiguous
    fixed-star targets is six requests at this size and 182 at five.

    ``PAGE_CEILING`` stops a walk whose answers never end; the API ends a walk
    with a null next offset, so only a malformed answer reaches it.
    ``WALK_WARN_REQUESTS`` is the number of requests a walk may need before
    it stops after the first page and names the size. ``asteroids`` holds
    twenty-eight thousand bodies, 177 round trips with nothing printed until
    the last one lands. Reading it is reasonable to want and terrible to start
    by accident.

    The ``*_FIELD`` names are the request options and response fields the
    walk reads and writes, as the API names them.
    """

    PATH: Final[str] = "/v1/chart"
    TECHNIQUE: Final[str] = "chart"

    PAGE_MAX: Final[int] = 160
    PAGE_CEILING: Final[int] = 200
    WALK_WARN_REQUESTS: Final[int] = 12

    CATEGORIES_FIELD: Final[str] = "categories"
    OFFSET_FIELD: Final[str] = "catalog_offset"
    LIMIT_FIELD: Final[str] = "catalog_limit"
    BODIES_FIELD: Final[str] = "bodies"
    PAGE_FIELD: Final[str] = "catalog_page"
    NEXT_OFFSET_FIELD: Final[str] = "next_offset"
    TOTAL_FIELD: Final[str] = "total"
