"""src/astromansion/_bodies.py: Build the request bodies the endpoints declare.

Callers describe a chart flat, the way a chart is spoken of; the wire nests it
under ``birth``. This module is the one place that knows the difference::

    client.natal(date="2000-01-01", lat=51.4779, lon=0.0)
        ──► {"birth": {"date": "2000-01-01", "lat": 51.4779, "lon": 0.0}}

Both clients and every generated method build their bodies here, so the
synchronous and the asynchronous client cannot send different shapes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .errors import ValidationError
from .models.constants.birth import BirthConstants
from .models.constants.bodies import RequestBodyConstants
from .models.constants.errors import ErrorConstants


class RequestBodies:
    """Build and check the request bodies the endpoints declare."""

    @staticmethod
    def merge(
        payload: dict[str, Any] | None, fields: Mapping[str, Any]
    ) -> dict[str, Any]:
        """Accept either a payload mapping or keyword fields, never both.

        Both styles are convenient and mixing them is ambiguous: it hides
        which source wins for a field named twice, so the mix is refused.

        Args:
            payload: The dict a caller passed positionally, if any.
            fields: Keyword fields. Fields set to ``None`` count as not given.

        Returns:
            A new dict holding the chosen source.

        Raises:
            TypeError: Both forms were given, or the payload is not a dict.

        Examples:
            >>> RequestBodies.merge(None, {"lat": 1.0, "time": None})
            {'lat': 1.0}
            >>> RequestBodies.merge({"lat": 1.0}, {})
            {'lat': 1.0}
            >>> RequestBodies.merge({"lat": 1.0}, {"lon": 2.0})
            Traceback (most recent call last):
                ...
            TypeError: pass either a payload mapping or keyword arguments, not both
        """
        given = {name: value for name, value in fields.items() if value is not None}
        if payload is None:
            return given
        if given:
            raise TypeError(
                "pass either a payload mapping or keyword arguments, not both"
            )
        if not isinstance(payload, dict):
            raise TypeError(f"payload must be a mapping, got {type(payload).__name__}")
        return dict(payload)

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
        """Build the ``birth`` object, checked before it is sent.

        A local error names the argument the caller wrote, while the round
        trip would answer with a JSON path the client built for them.

        Args:
            date: Calendar date as ``YYYY-MM-DD``.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            lat: Latitude in decimal degrees, north positive, within -90..90.
            lon: Longitude in decimal degrees, east positive, within -180..180.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.

        Returns:
            The ``birth`` mapping, holding only the fields that were given.

        Raises:
            ValidationError: A field cannot be the value given.

        Examples:
            >>> RequestBodies.birth("2000-01-01", lat=51.4779, lon=0)
            {'date': '2000-01-01', 'lat': 51.4779, 'lon': 0.0}
            >>> RequestBodies.birth("01-01-2000", lat=0, lon=0)  # doctest: +ELLIPSIS
            Traceback (most recent call last):
                ...
            astromansion.errors.ValidationError: date must look like YYYY-MM-DD...
        """
        if not isinstance(date, str) or not BirthConstants.DATE.match(date):
            raise ValidationError(
                f"date must look like YYYY-MM-DD, got {date!r}",
                error_code=ErrorConstants.VALIDATION,
            )
        if time is not None and (
            not isinstance(time, str) or not BirthConstants.TIME.match(time)
        ):
            raise ValidationError(
                f"time must look like HH:MM, got {time!r}",
                error_code=ErrorConstants.VALIDATION,
            )
        try:
            latitude, longitude = float(lat), float(lon)
        except (TypeError, ValueError):
            raise ValidationError(
                f"lat and lon must be numbers, got {lat!r} and {lon!r}",
                error_code=ErrorConstants.VALIDATION,
            ) from None

        low, high = BirthConstants.LAT_RANGE_DEGREES
        if not low <= latitude <= high:
            raise ValidationError(
                f"lat must be within {low}..{high}, got {lat!r}",
                error_code=ErrorConstants.VALIDATION,
            )
        low, high = BirthConstants.LON_RANGE_DEGREES
        if not low <= longitude <= high:
            raise ValidationError(
                f"lon must be within {low}..{high}, got {lon!r}",
                error_code=ErrorConstants.VALIDATION,
            )

        birth: dict[str, Any] = {
            BirthConstants.DATE_FIELD: date,
            BirthConstants.LAT_FIELD: latitude,
            BirthConstants.LON_FIELD: longitude,
        }
        if time is not None:
            birth[BirthConstants.TIME_FIELD] = time
        if timezone is not None:
            birth[BirthConstants.TIMEZONE_FIELD] = timezone
        if houses is not None:
            birth[BirthConstants.HOUSES_FIELD] = houses
        return birth

    @classmethod
    def chart(
        cls,
        payload: dict[str, Any] | None,
        options: Mapping[str, Any] | None,
        fields: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Build the body a one-person endpoint expects.

        Args:
            payload: Birth fields as one mapping, if the caller passed one.
            options: The endpoint's options; left out when empty.
            fields: Birth fields passed as keywords.

        Returns:
            ``{"birth": {...}}``, with ``options`` when there are any.

        Raises:
            TypeError: Both a payload and keyword fields were given.
            ValidationError: A birth field cannot be the value given.

        Examples:
            >>> RequestBodies.chart(
            ...     None, {"wheel": True}, {"date": "2000-01-01", "lat": 0, "lon": 0}
            ... )  # doctest: +NORMALIZE_WHITESPACE
            {'birth': {'date': '2000-01-01', 'lat': 0.0, 'lon': 0.0},
             'options': {'wheel': True}}
        """
        body: dict[str, Any] = {
            RequestBodyConstants.BIRTH: cls.birth(**cls.merge(payload, fields))
        }
        if options:
            body[RequestBodyConstants.OPTIONS] = dict(options)
        return body

    @classmethod
    def pair(
        cls,
        birth: Mapping[str, Any],
        partner: Mapping[str, Any],
        options: Mapping[str, Any] | None,
        extra: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Build the body a two-person endpoint expects.

        The API names the second person ``partner``, not ``second``: the wire
        contract decides, not what reads nicely here.

        Args:
            birth: The first person's birth fields.
            partner: The second person's birth fields.
            options: The endpoint's options; left out when empty.
            extra: Further top-level fields; those set to ``None`` are left out.

        Returns:
            ``{"birth": {...}, "partner": {...}}`` with the options and extras.

        Raises:
            ValidationError: A birth field of either person is malformed.
        """
        body: dict[str, Any] = {
            RequestBodyConstants.BIRTH: cls.birth(**birth),
            RequestBodyConstants.PARTNER: cls.birth(**partner),
        }
        if options:
            body[RequestBodyConstants.OPTIONS] = dict(options)
        body.update({key: value for key, value in extra.items() if value is not None})
        return body

    @classmethod
    def sharecard(
        cls,
        birth: Mapping[str, Any] | None,
        partner: Mapping[str, Any] | None,
        *,
        card_type: str,
        name: str | None,
        names: Sequence[str] | None,
        lang: str | None,
        extra: dict[str, Any],
    ) -> dict[str, Any]:
        """Build the body of the share card, for one chart or for two.

        Three call styles reach the same body: two mappings positionally, the
        same as keywords, or one chart's fields passed flat among ``extra``.
        Birth fields found in ``extra`` are taken out of it.

        Args:
            birth: The chart as a mapping, or the first of two; ``None`` reads
                the chart's fields from ``extra``.
            partner: The second chart, required by a synastry card.
            card_type: ``synastry`` or ``natal``.
            name: The one display name a natal card prints.
            names: Display names, one per chart.
            lang: Card language, ``en`` or ``tr``.
            extra: Further top-level fields; those set to ``None`` are left out.

        Returns:
            The share card's request body.

        Raises:
            ValueError: Both ``name`` and ``names`` were given.
            ValidationError: A birth field is malformed.

        Examples:
            >>> RequestBodies.sharecard(
            ...     None, None, card_type="natal", name="Ada", names=None, lang=None,
            ...     extra={"date": "2000-01-01", "lat": 0, "lon": 0},
            ... )  # doctest: +NORMALIZE_WHITESPACE
            {'birth': {'date': '2000-01-01', 'lat': 0.0, 'lon': 0.0},
             'type': 'natal', 'names': ['Ada']}
        """
        chart = (
            dict(birth)
            if birth is not None
            else {
                key: extra.pop(key)
                for key in list(extra)
                if key in BirthConstants.FIELDS
            }
        )
        body: dict[str, Any] = {
            RequestBodyConstants.BIRTH: cls.birth(**chart),
            RequestBodyConstants.SHARECARD_TYPE: card_type,
        }
        if partner is not None:
            body[RequestBodyConstants.PARTNER] = cls.birth(**partner)
        if name is not None and names is not None:
            raise ValueError("pass either name or names, not both")
        if name is not None:
            body[RequestBodyConstants.SHARECARD_NAMES] = [name]
        elif names is not None:
            body[RequestBodyConstants.SHARECARD_NAMES] = list(names)
        if lang is not None:
            body[RequestBodyConstants.SHARECARD_LANG] = lang
        body.update({key: value for key, value in extra.items() if value is not None})
        return body
