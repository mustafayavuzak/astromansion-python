"""src/astromansion/models/constants/birth.py: The birth fields the API accepts.

Checked before the request, so an error names the argument the caller wrote
rather than a JSON path the client built for them. The patterns check the
shape only; the API checks that a date or a time exists.
"""

from __future__ import annotations

import re
from typing import Final


class BirthConstants:
    """Field names, patterns, and ranges of the ``birth`` object.

    The ``*_FIELD`` names are the wire names, which are also the keyword
    arguments every chart method takes, and ``FIELDS`` is the set of them,
    used to tell birth fields apart from an endpoint's own options. Latitude
    and longitude are decimal degrees, north and east positive, and their
    ranges include both ends.
    """

    DATE_FIELD: Final[str] = "date"
    TIME_FIELD: Final[str] = "time"
    LAT_FIELD: Final[str] = "lat"
    LON_FIELD: Final[str] = "lon"
    TIMEZONE_FIELD: Final[str] = "timezone"
    HOUSES_FIELD: Final[str] = "houses"
    FIELDS: Final[frozenset[str]] = frozenset(
        {
            DATE_FIELD,
            TIME_FIELD,
            LAT_FIELD,
            LON_FIELD,
            TIMEZONE_FIELD,
            HOUSES_FIELD,
        }
    )

    LAT_RANGE_DEGREES: Final[tuple[float, float]] = (-90.0, 90.0)
    LON_RANGE_DEGREES: Final[tuple[float, float]] = (-180.0, 180.0)

    DATE: Final[re.Pattern[str]] = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    r"""A calendar date written ``YYYY-MM-DD``.

    Drawing::

        ^ \d{4} - \d{2} - \d{2} $
          year    month   day

    Accepts: ``2000-01-01``, ``1990-07-19``
    Refuses: ``2000-1-1``, ``01-01-2000``, ``2000-01-01T12:00``
    """

    TIME: Final[re.Pattern[str]] = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?$")
    r"""A clock time written ``HH:MM``, with optional seconds.

    Drawing::

        ^ \d{1,2} : \d{2} (:\d{2})? $
          hour      minute  seconds

    Accepts: ``12:00``, ``9:05``, ``23:59:30``
    Refuses: ``1200``, ``12:0``, ``12:00 PM``
    """
