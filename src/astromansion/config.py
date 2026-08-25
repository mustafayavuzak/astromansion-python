"""Turn caller arguments into the bodies the API's endpoints declare.

Only shaping lives here. The values it is bound by are in
:mod:`astromansion.constants`.
"""

from __future__ import annotations

from typing import Any, Final

from .constants import Birth
from .errors import ValidationError


class Body:
    """Build the request bodies the endpoints declare.

    A namespace rather than a base to inherit: the clients call
    ``Body.chart(...)`` and carry none of this as state.
    """

    #: The fields that describe a chart. Named once so a caller can pass
    #: them flat and a wrapper can tell them from its own options.
    BIRTH_FIELDS: Final[frozenset[str]] = frozenset(
        {"date", "time", "lat", "lon", "timezone", "houses"},
    )

    @staticmethod
    def birth(
        date: str,
        *,
        time: str | None = None,
        lat: float,
        lon: float,
        timezone: float | str | None = None,
        houses: str | None = None,
    ) -> dict[str, Any]:
        """Build the ``birth`` object the API expects.

        Callers pass these fields flat because that is how a chart is
        described; the wire format nests them, and this is the single place
        that knows the difference.

        The shape is checked here rather than left to the server: a local
        error names the argument the caller wrote, while the round trip
        answers with a JSON path the SDK built for them.

        :param date: Calendar date as ``YYYY-MM-DD``.
        :param time: Clock time as ``HH:MM``. Omit for an unknown birth time.
        :param lat: Latitude in decimal degrees, north positive.
        :param lon: Longitude in decimal degrees, east positive.
        :param timezone: UTC offset in hours, or an IANA zone name.
        :param houses: House system identifier the API publishes.
        :returns: The ``birth`` mapping.
        :raises ValidationError: A field cannot be the value given.
        """
        if not isinstance(date, str) or not Birth.DATE.match(date):
            raise ValidationError(
                f"date must look like YYYY-MM-DD, got {date!r}",
                error_code="validation",
            )
        if time is not None and (
            not isinstance(time, str) or not Birth.TIME.match(time)
        ):
            raise ValidationError(
                f"time must look like HH:MM, got {time!r}",
                error_code="validation",
            )
        try:
            latitude, longitude = float(lat), float(lon)
        except (TypeError, ValueError):
            raise ValidationError(
                f"lat and lon must be numbers, got {lat!r} and {lon!r}",
                error_code="validation",
            ) from None

        low, high = Birth.LAT_RANGE
        if not low <= latitude <= high:
            raise ValidationError(
                f"lat must be within {low}..{high}, got {lat!r}",
                error_code="validation",
            )
        low, high = Birth.LON_RANGE
        if not low <= longitude <= high:
            raise ValidationError(
                f"lon must be within {low}..{high}, got {lon!r}",
                error_code="validation",
            )

        birth: dict[str, Any] = {
            "date": date,
            "lat": latitude,
            "lon": longitude,
        }
        if time is not None:
            birth["time"] = time
        if timezone is not None:
            birth["timezone"] = timezone
        if houses is not None:
            birth["houses"] = houses
        return birth

    @staticmethod
    def chart(
        payload: dict[str, Any] | None,
        options: dict[str, Any] | None,
        fields: dict[str, Any],
    ) -> dict[str, Any]:
        """Build the wrapped body a one-person endpoint expects."""
        from ._core import Arguments

        body: dict[str, Any] = {
            "birth": Body.birth(**Arguments.merge(payload, fields)),
        }
        if options:
            body["options"] = options
        return body

    @staticmethod
    def pair(
        birth: dict[str, Any],
        partner: dict[str, Any],
        options: dict[str, Any] | None,
        extra: dict[str, Any],
    ) -> dict[str, Any]:
        """Build the body a two-person endpoint expects.

        The API names the second person ``partner``, not ``second``: the wire
        contract decides, not what reads nicely here.
        """
        body: dict[str, Any] = {
            "birth": Body.birth(**birth),
            "partner": Body.birth(**partner),
        }
        if options:
            body["options"] = options
        body.update({k: v for k, v in extra.items() if v is not None})
        return body
