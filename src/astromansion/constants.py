"""Values the client is bound by, grouped by what owns them.

Kept out of the modules that use them so a contract change has one place to
happen. Each class is a namespace, not a base to inherit: the client reads
``Api.BASE_URL`` rather than carrying it as state.
"""

from __future__ import annotations

import re
from typing import Final


class Package:
    """Identity this package presents to the API."""

    VERSION: Final[str] = "0.2.1"
    #: Matches the name on PyPI, so a server log names what to install.
    NAME: Final[str] = "astromansion"

    @classmethod
    def user_agent(cls) -> str:
        """Return the User-Agent every request carries.

        Version only. Nothing about the machine or the caller travels here.
        """
        return f"{cls.NAME}/{cls.VERSION}"


class Api:
    """Where the API lives and how it reads a key.

    The header is the one the published security scheme names, not an
    assumption. The API also accepts a bearer token; this is its primary.
    """

    BASE_URL: Final[str] = "https://api.astromansion.com"
    KEY_HEADER: Final[str] = "X-API-Key"
    KEY_ENV: Final[str] = "ASTROMANSION_API_KEY"
    BASE_URL_ENV: Final[str] = "ASTROMANSION_BASE_URL"
    REQUEST_ID_HEADER: Final[str] = "X-Request-ID"
    #: Every published path begins here. ``request`` refuses anything else so
    #: a mistyped or attacker-supplied target cannot carry the key off-site.
    PATH_PREFIX: Final[str] = "/v1/"


class Timeouts:
    """Time budgets. A chart is computed server-side, so reading is generous
    while connecting stays short: an unreachable host should fail fast."""

    CONNECT: Final[float] = 5.0
    READ: Final[float] = 30.0


class Retry:
    """When a repeat is safe and how long to wait.

    Only failures that carry no result are repeated. A request that never
    completed cannot have been counted against the caller's allowance, and a
    5xx means the server produced nothing, so neither can be charged twice.
    A refusal the caller must fix is never repeated: the answer would not
    change and the attempt would still be spent.
    """

    MAX_ATTEMPTS: Final[int] = 2
    BACKOFF_SECONDS: Final[float] = 0.5
    BACKOFF_CEILING: Final[float] = 8.0
    STATUSES: Final[frozenset[int]] = frozenset({429, 500, 502, 503, 504})
    HEADER: Final[str] = "Retry-After"


class Birth:
    """Shapes the API accepts for a moment of birth.

    Checked before the request so an error names the argument the caller
    wrote, rather than a JSON path the SDK built for them.
    """

    DATE: Final[re.Pattern[str]] = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    TIME: Final[re.Pattern[str]] = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?$")
    LAT_RANGE: Final[tuple[float, float]] = (-90.0, 90.0)
    LON_RANGE: Final[tuple[float, float]] = (-180.0, 180.0)


class Catalog:
    """Paging the ``/v1/chart`` catalog.

    A page costs one round trip and the calculation inside it is a rounding
    error beside that, so the only sensible page is the largest one the API
    will serve. Reading 890 fixed stars is six requests at this size and a
    hundred and eighty at five.
    """

    #: Largest page ``/v1/chart`` accepts. The engine computes at most 192
    #: points and the remainder is reserved for axes and derived points.
    PAGE_MAX: Final[int] = 160
    #: Refuse to keep asking past this many pages. The API ends a walk with a
    #: null ``next_offset``; this only stops a malformed answer from looping.
    PAGE_CEILING: Final[int] = 200
    #: Requests a walk may make before it stops and says how big the category
    #: turned out to be.
    #:
    #: ``asteroids`` holds twenty-eight thousand bodies, which is a hundred
    #: and seventy-seven round trips and the better part of a minute with no
    #: output. Reading it is a reasonable thing to want and a terrible thing
    #: to start by accident, so a walk past this size stops and names the
    #: number rather than going quiet.
    WALK_WARN_REQUESTS: Final[int] = 12
