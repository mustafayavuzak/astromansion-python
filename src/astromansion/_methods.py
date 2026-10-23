"""src/astromansion/_methods.py: Generated client methods, one per endpoint.

Produced by ``tools/generate_endpoints.py``. Do not edit: rerun the generator
so the SDK cannot describe a surface the API does not serve.

Endpoints: 66. Written on the client itself: render_sharecard.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, overload
from urllib.parse import quote

from ._bodies import RequestBodies
from ._responses import Responses
from .response import Result


class SyncEndpoints:
    """Every endpoint, mixed into the synchronous client.

    The transport lives on the client this is mixed into. Declaring its hooks
    here is what lets a type checker see the mixin as complete instead of
    reporting every method as calling something that does not exist. Each
    hook is declared for a JSON answer, for a document, and for either; the
    last is the form the client implements.
    """

    if TYPE_CHECKING:

        @overload
        def request(
            self,
            method: str,
            path: str,
            *,
            binary: Literal[False] = ...,
            technique: str | None = ...,
            enveloped: bool | None = ...,
            **kwargs: Any,
        ) -> Result:
            """Send a request whose success is JSON.

            Args:
                method: HTTP verb.
                path: A path beginning with ``/v1/``.
                binary: Whether a success is a document rather than JSON.
                technique: Endpoint name the result reports when the body
                    names none.
                enveloped: Whether a success is wrapped in
                    ``{technique, result}``; ``None`` lets the body decide.
                **kwargs: Passed to httpx, notably ``json`` and ``params``.

            Returns:
                The decoded response.
            """

        @overload
        def request(
            self,
            method: str,
            path: str,
            *,
            binary: Literal[True],
            technique: str | None = ...,
            enveloped: bool | None = ...,
            **kwargs: Any,
        ) -> bytes:
            """Send a request whose success is a document.

            Args:
                method: HTTP verb.
                path: A path beginning with ``/v1/``.
                binary: Whether a success is a document rather than JSON.
                technique: Endpoint name the result reports when the body
                    names none.
                enveloped: Whether a success is wrapped in
                    ``{technique, result}``; ``None`` lets the body decide.
                **kwargs: Passed to httpx, notably ``json`` and ``params``.

            Returns:
                The document's bytes.
            """

        def request(
            self,
            method: str,
            path: str,
            *,
            binary: bool = ...,
            technique: str | None = ...,
            enveloped: bool | None = ...,
            **kwargs: Any,
        ) -> Result | bytes:
            """Send a request whose success is JSON or a document.

            Args:
                method: HTTP verb.
                path: A path beginning with ``/v1/``.
                binary: Whether a success is a document rather than JSON.
                technique: Endpoint name the result reports when the body
                    names none.
                enveloped: Whether a success is wrapped in
                    ``{technique, result}``; ``None`` lets the body decide.
                **kwargs: Passed to httpx, notably ``json`` and ``params``.

            Returns:
                The decoded response, or the document's bytes.
            """

        @overload
        def _chart(
            self,
            path: str,
            payload: dict[str, Any] | None,
            options: dict[str, Any] | None,
            *,
            binary: Literal[False] = ...,
            technique: str | None = ...,
            enveloped: bool | None = ...,
            **fields: Any,
        ) -> Result:
            """Send a one-person request whose success is JSON.

            Args:
                path: The endpoint's path.
                payload: Birth fields as one mapping, if the caller passed one.
                options: The endpoint's options.
                binary: Whether a success is a document rather than JSON.
                technique: Endpoint name the result reports when the body
                    names none.
                enveloped: Whether a success is wrapped in
                    ``{technique, result}``; ``None`` lets the body decide.
                **fields: Birth fields passed as keywords.

            Returns:
                The decoded response.
            """

        @overload
        def _chart(
            self,
            path: str,
            payload: dict[str, Any] | None,
            options: dict[str, Any] | None,
            *,
            binary: Literal[True],
            technique: str | None = ...,
            enveloped: bool | None = ...,
            **fields: Any,
        ) -> bytes:
            """Send a one-person request whose success is a document.

            Args:
                path: The endpoint's path.
                payload: Birth fields as one mapping, if the caller passed one.
                options: The endpoint's options.
                binary: Whether a success is a document rather than JSON.
                technique: Endpoint name the result reports when the body
                    names none.
                enveloped: Whether a success is wrapped in
                    ``{technique, result}``; ``None`` lets the body decide.
                **fields: Birth fields passed as keywords.

            Returns:
                The document's bytes.
            """

        def _chart(
            self,
            path: str,
            payload: dict[str, Any] | None,
            options: dict[str, Any] | None,
            *,
            binary: bool = ...,
            technique: str | None = ...,
            enveloped: bool | None = ...,
            **fields: Any,
        ) -> Result | bytes:
            """Send a one-person request whose success is JSON or a document.

            Args:
                path: The endpoint's path.
                payload: Birth fields as one mapping, if the caller passed one.
                options: The endpoint's options.
                binary: Whether a success is a document rather than JSON.
                technique: Endpoint name the result reports when the body
                    names none.
                enveloped: Whether a success is wrapped in
                    ``{technique, result}``; ``None`` lets the body decide.
                **fields: Birth fields passed as keywords.

            Returns:
                The decoded response, or the document's bytes.
            """

        @overload
        def _pair(
            self,
            path: str,
            birth: dict[str, Any],
            partner: dict[str, Any],
            options: dict[str, Any] | None,
            *,
            binary: Literal[False] = ...,
            technique: str | None = ...,
            enveloped: bool | None = ...,
            **extra: Any,
        ) -> Result:
            """Send a two-person request whose success is JSON.

            Args:
                path: The endpoint's path.
                birth: The first person's birth fields.
                partner: The second person's birth fields.
                options: The endpoint's options.
                binary: Whether a success is a document rather than JSON.
                technique: Endpoint name the result reports when the body
                    names none.
                enveloped: Whether a success is wrapped in
                    ``{technique, result}``; ``None`` lets the body decide.
                **extra: Further top-level body fields.

            Returns:
                The decoded response.
            """

        @overload
        def _pair(
            self,
            path: str,
            birth: dict[str, Any],
            partner: dict[str, Any],
            options: dict[str, Any] | None,
            *,
            binary: Literal[True],
            technique: str | None = ...,
            enveloped: bool | None = ...,
            **extra: Any,
        ) -> bytes:
            """Send a two-person request whose success is a document.

            Args:
                path: The endpoint's path.
                birth: The first person's birth fields.
                partner: The second person's birth fields.
                options: The endpoint's options.
                binary: Whether a success is a document rather than JSON.
                technique: Endpoint name the result reports when the body
                    names none.
                enveloped: Whether a success is wrapped in
                    ``{technique, result}``; ``None`` lets the body decide.
                **extra: Further top-level body fields.

            Returns:
                The document's bytes.
            """

        def _pair(
            self,
            path: str,
            birth: dict[str, Any],
            partner: dict[str, Any],
            options: dict[str, Any] | None,
            *,
            binary: bool = ...,
            technique: str | None = ...,
            enveloped: bool | None = ...,
            **extra: Any,
        ) -> Result | bytes:
            """Send a two-person request whose success is JSON or a document.

            Args:
                path: The endpoint's path.
                birth: The first person's birth fields.
                partner: The second person's birth fields.
                options: The endpoint's options.
                binary: Whether a success is a document rather than JSON.
                technique: Endpoint name the result reports when the body
                    names none.
                enveloped: Whether a success is wrapped in
                    ``{technique, result}``; ``None`` lets the body decide.
                **extra: Further top-level body fields.

            Returns:
                The decoded response, or the document's bytes.
            """

    def almanac(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Eclipses, retrogrades, planetary hours, and void Moon…. Wraps ``POST /v1/almanac``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/almanac",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="almanac",
            enveloped=True,
        )

    def antiscia(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Antiscia and contra-antiscia. Wraps ``POST /v1/antiscia``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/antiscia",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="antiscia",
            enveloped=True,
        )

    def aspects(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Complete natal aspect list. Wraps ``POST /v1/aspects``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/aspects",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="aspects",
            enveloped=True,
        )

    def astrocartography(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Astrocartography lines. Wraps ``POST /v1/astrocartography``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/astrocartography",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="astrocartography",
            enveloped=True,
        )

    def batch(self, body: dict[str, Any] | None = None, **fields: Any) -> Result:
        """Batch computation (Enterprise). Wraps ``POST /v1/batch``.

        Args:
            body: The request body as one mapping, instead of keyword fields.
            **fields: Body fields as keywords: ``items``.

        Returns:
            The decoded response.

        Raises:
            TypeError: Both a body mapping and keyword fields were given.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "POST",
            "/v1/batch",
            json=RequestBodies.merge(body, fields),
            binary=False,
            technique="batch",
            enveloped=False,
        )

    def chart(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Extended natal chart with category selection. Wraps ``POST /v1/chart``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/chart",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="chart",
            enveloped=None,
        )

    def compatibility(
        self,
        birth: dict[str, Any],
        partner: dict[str, Any],
        *,
        options: dict[str, Any] | None = None,
        **extra: Any,
    ) -> Result:
        """Compatibility score from 0 to 100. Wraps ``POST /v1/compatibility``.

        Args:
            birth: The first person's birth fields, as ``natal`` takes them.
            partner: The second person's birth fields.
            options: The endpoint's options.
            **extra: Further top-level body fields.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field of either person is malformed, or
                the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._pair(
            "/v1/compatibility",
            birth,
            partner,
            options,
            binary=False,
            technique="compatibility",
            enveloped=True,
            **extra,
        )

    def composite(
        self,
        birth: dict[str, Any],
        partner: dict[str, Any],
        *,
        options: dict[str, Any] | None = None,
        **extra: Any,
    ) -> Result:
        """Midpoint composite chart. Wraps ``POST /v1/composite``.

        Args:
            birth: The first person's birth fields, as ``natal`` takes them.
            partner: The second person's birth fields.
            options: The endpoint's options.
            **extra: Further top-level body fields.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field of either person is malformed, or
                the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._pair(
            "/v1/composite",
            birth,
            partner,
            options,
            binary=False,
            technique="composite",
            enveloped=True,
            **extra,
        )

    def custom_body(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Custom elliptic or hyperbolic Keplerian body. Wraps ``POST /v1/custom-body``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/custom-body",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="custom_body",
            enveloped=True,
        )

    def custom_bodies(self, **params: Any) -> Result:
        """List saved custom bodies. Wraps ``GET /v1/custom-body/list``.

        Args:
            **params: Query parameters; those set to ``None`` are left out.

        Returns:
            The decoded response.

        Raises:
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "GET",
            "/v1/custom-body/list",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="custom_bodies",
            enveloped=False,
        )

    def save_custom_body(
        self, body: dict[str, Any] | None = None, **fields: Any
    ) -> Result:
        """Save and calculate a named custom Keplerian body. Wraps ``POST /v1/custom-body/save``.

        Args:
            body: The request body as one mapping, instead of keyword fields.
            **fields: Body fields as keywords: ``birth``, ``name``, ``elements``, ``heliocentric``, ``save``, ``wheel``, ``aspects``.

        Returns:
            The decoded response.

        Raises:
            TypeError: Both a body mapping and keyword fields were given.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "POST",
            "/v1/custom-body/save",
            json=RequestBodies.merge(body, fields),
            binary=False,
            technique="save_custom_body",
            enveloped=False,
        )

    def chart_with_custom_body(
        self, name: str, body: dict[str, Any] | None = None, **fields: Any
    ) -> Result:
        """Calculate a saved custom body by name. Wraps ``POST /v1/custom-body/{name}``.

        Args:
            name: The ``{name}`` path segment, quoted into the URL.
            body: The request body as one mapping, instead of keyword fields.
            **fields: Body fields as keywords: ``birth``, ``wheel``, ``aspects``.

        Returns:
            The decoded response.

        Raises:
            TypeError: Both a body mapping and keyword fields were given.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "POST",
            f"/v1/custom-body/{quote(str(name), safe='')}",
            json=RequestBodies.merge(body, fields),
            binary=False,
            technique="chart_with_custom_body",
            enveloped=False,
        )

    def delete_custom_body(self, name: str, **params: Any) -> Result:
        """Delete a saved custom body. Wraps ``DELETE /v1/custom-body/{name}``.

        Args:
            name: The ``{name}`` path segment, quoted into the URL.
            **params: Query parameters; those set to ``None`` are left out.

        Returns:
            The decoded response.

        Raises:
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "DELETE",
            f"/v1/custom-body/{quote(str(name), safe='')}",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="delete_custom_body",
            enveloped=False,
        )

    def custom_lot(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Custom Arabic lot formula (A+B-C). Wraps ``POST /v1/custom-lot``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/custom-lot",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="custom_lot",
            enveloped=True,
        )

    def daily(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Daily sky summary. Wraps ``POST /v1/daily``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/daily",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="daily",
            enveloped=True,
        )

    def declinations(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Declination parallels. Wraps ``POST /v1/declinations``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/declinations",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="declinations",
            enveloped=True,
        )

    def dignities(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Classical dignities and almuten. Wraps ``POST /v1/dignities``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/dignities",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="dignities",
            enveloped=True,
        )

    def draconic(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Draconic zodiac. Wraps ``POST /v1/draconic``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/draconic",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="draconic",
            enveloped=True,
        )

    def eclipses(self, **params: Any) -> Result:
        """Eclipse calendar. Wraps ``GET /v1/eclipses``.

        Args:
            **params: Query parameters; those set to ``None`` are left out.

        Returns:
            The decoded response.

        Raises:
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "GET",
            "/v1/eclipses",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="eclipses",
            enveloped=False,
        )

    def electional(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Electional date-window scan. Wraps ``POST /v1/electional``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/electional",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="electional",
            enveloped=True,
        )

    def export_csv(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
        output: str | Path | None = None,
    ) -> bytes | Path:
        """Chart data as CSV. Wraps ``POST /v1/export/csv``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.
            output: Path to write the document to, or ``None`` for the bytes.

        Returns:
            The document's bytes, or the path it was written to.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return Responses.save_document(
            self._chart(
                "/v1/export/csv",
                payload,
                options,
                date=date,
                lat=lat,
                lon=lon,
                time=time,
                timezone=timezone,
                houses=houses,
                binary=True,
                technique="export_csv",
                enveloped=None,
            ),
            output,
        )

    def export_pdf(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
        output: str | Path | None = None,
    ) -> bytes | Path:
        """Multi-page PDF report. Wraps ``POST /v1/export/pdf``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.
            output: Path to write the document to, or ``None`` for the bytes.

        Returns:
            The document's bytes, or the path it was written to.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return Responses.save_document(
            self._chart(
                "/v1/export/pdf",
                payload,
                options,
                date=date,
                lat=lat,
                lon=lon,
                time=time,
                timezone=timezone,
                houses=houses,
                binary=True,
                technique="export_pdf",
                enveloped=None,
            ),
            output,
        )

    def export_report(
        self,
        body: dict[str, Any] | None = None,
        output: str | Path | None = None,
        **fields: Any,
    ) -> bytes | Path:
        """Editable multi-page PDF report. Wraps ``POST /v1/export/report``.

        Args:
            body: The request body as one mapping, instead of keyword fields.
            output: Path to write the document to, or ``None`` for the bytes.
            **fields: Body fields as keywords: ``sections``, ``page_size``, ``title``, ``author``, ``custom_text``, ``accent``, ``white_label``, ``logo_b64``, ``birth``.

        Returns:
            The document's bytes, or the path it was written to.

        Raises:
            TypeError: Both a body mapping and keyword fields were given.
            AstroMansionError: The API refused the call, or never answered.
        """
        return Responses.save_document(
            self.request(
                "POST",
                "/v1/export/report",
                json=RequestBodies.merge(body, fields),
                binary=True,
                technique="export_report",
                enveloped=None,
            ),
            output,
        )

    def firdaria(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Firdaria periods. Wraps ``POST /v1/firdaria``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/firdaria",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="firdaria",
            enveloped=True,
        )

    def search_places(self, **params: Any) -> Result:
        """Search place names. Wraps ``GET /v1/geo/search``.

        Args:
            **params: Query parameters; those set to ``None`` are left out.

        Returns:
            The decoded response.

        Raises:
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "GET",
            "/v1/geo/search",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="search_places",
            enveloped=False,
        )

    def harmonics(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Harmonic chart. Wraps ``POST /v1/harmonics``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/harmonics",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="harmonics",
            enveloped=True,
        )

    def health(self, **params: Any) -> Result:
        """Service health check. Wraps ``GET /v1/health``.

        Args:
            **params: Query parameters; those set to ``None`` are left out.

        Returns:
            The decoded response.

        Raises:
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "GET",
            "/v1/health",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="health",
            enveloped=None,
        )

    def heliacal(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Heliacal rising and setting events. Wraps ``POST /v1/heliacal``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/heliacal",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="heliacal",
            enveloped=True,
        )

    def heliocentric(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Heliocentric positions. Wraps ``POST /v1/heliocentric``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/heliocentric",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="heliocentric",
            enveloped=True,
        )

    def horary(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Horary question chart. Wraps ``POST /v1/horary``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/horary",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="horary",
            enveloped=True,
        )

    def list_jobs(self, **params: Any) -> Result:
        """List jobs. Wraps ``GET /v1/jobs``.

        Args:
            **params: Query parameters; those set to ``None`` are left out.

        Returns:
            The decoded response.

        Raises:
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "GET",
            "/v1/jobs",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="list_jobs",
            enveloped=False,
        )

    def submit_job(self, body: dict[str, Any] | None = None, **fields: Any) -> Result:
        """Create an async job for any technique. Wraps ``POST /v1/jobs``.

        Args:
            body: The request body as one mapping, instead of keyword fields.
            **fields: Body fields as keywords: ``technique``, ``callback_url``, ``body``.

        Returns:
            The decoded response.

        Raises:
            TypeError: Both a body mapping and keyword fields were given.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "POST",
            "/v1/jobs",
            json=RequestBodies.merge(body, fields),
            binary=False,
            technique="submit_job",
            enveloped=None,
        )

    def submit_batch_job(
        self, body: dict[str, Any] | None = None, **fields: Any
    ) -> Result:
        """Create an async job batch of up to 20 items. Wraps ``POST /v1/jobs/batch``.

        Args:
            body: The request body as one mapping, instead of keyword fields.
            **fields: Body fields as keywords: ``items``.

        Returns:
            The decoded response.

        Raises:
            TypeError: Both a body mapping and keyword fields were given.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "POST",
            "/v1/jobs/batch",
            json=RequestBodies.merge(body, fields),
            binary=False,
            technique="submit_batch_job",
            enveloped=None,
        )

    def job(self, job_id: str, **params: Any) -> Result:
        """Inspect job status. Wraps ``GET /v1/jobs/{job_id}``.

        Args:
            job_id: The ``{job_id}`` path segment, quoted into the URL.
            **params: Query parameters; those set to ``None`` are left out.

        Returns:
            The decoded response.

        Raises:
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "GET",
            f"/v1/jobs/{quote(str(job_id), safe='')}",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="job",
            enveloped=False,
        )

    def lunar_return(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Lunar return charts. Wraps ``POST /v1/lunar-return``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/lunar-return",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="lunar_return",
            enveloped=True,
        )

    def mansions(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Twenty-eight lunar mansions. Wraps ``POST /v1/mansions``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/mansions",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="mansions",
            enveloped=True,
        )

    def midpoints(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Planetary midpoints. Wraps ``POST /v1/midpoints``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/midpoints",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="midpoints",
            enveloped=True,
        )

    def moon_phases(self, **params: Any) -> Result:
        """Lunar phase calendar. Wraps ``GET /v1/moon-phases``.

        Args:
            **params: Query parameters; those set to ``None`` are left out.

        Returns:
            The decoded response.

        Raises:
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "GET",
            "/v1/moon-phases",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="moon_phases",
            enveloped=False,
        )

    def moon_phases_for(
        self, body: dict[str, Any] | None = None, **fields: Any
    ) -> Result:
        """Lunar phase query filtered by month and phase. Wraps ``POST /v1/moon-phases/query``.

        Args:
            body: The request body as one mapping, instead of keyword fields.
            **fields: Body fields as keywords: ``year``, ``month``, ``only``.

        Returns:
            The decoded response.

        Raises:
            TypeError: Both a body mapping and keyword fields were given.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "POST",
            "/v1/moon-phases/query",
            json=RequestBodies.merge(body, fields),
            binary=False,
            technique="moon_phases_for",
            enveloped=False,
        )

    def nakshatra(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Moon nakshatra, pada, and ruler. Wraps ``POST /v1/nakshatra``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/nakshatra",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="nakshatra",
            enveloped=True,
        )

    def natal(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Free natal chart. Wraps ``POST /v1/natal``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/natal",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="natal",
            enveloped=False,
        )

    def navamsa(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """D9 Navamsa and other divisional charts. Wraps ``POST /v1/navamsa``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/navamsa",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="navamsa",
            enveloped=True,
        )

    def pair_aspects(
        self,
        birth: dict[str, Any],
        partner: dict[str, Any],
        *,
        options: dict[str, Any] | None = None,
        **extra: Any,
    ) -> Result:
        """Aspects between two charts. Wraps ``POST /v1/pair-aspects``.

        Args:
            birth: The first person's birth fields, as ``natal`` takes them.
            partner: The second person's birth fields.
            options: The endpoint's options.
            **extra: Further top-level body fields.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field of either person is malformed, or
                the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._pair(
            "/v1/pair-aspects",
            birth,
            partner,
            options,
            binary=False,
            technique="pair_aspects",
            enveloped=True,
            **extra,
        )

    def parans(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Fixed-star parans. Wraps ``POST /v1/parans``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/parans",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="parans",
            enveloped=True,
        )

    def patterns(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Jones patterns, stelliums, and aspect figures. Wraps ``POST /v1/patterns``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/patterns",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="patterns",
            enveloped=True,
        )

    def profection(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Annual profections. Wraps ``POST /v1/profection``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/profection",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="profection",
            enveloped=True,
        )

    def progression(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Secondary progressions. Wraps ``POST /v1/progression``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/progression",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="progression",
            enveloped=True,
        )

    def query(self, body: dict[str, Any] | None = None, **fields: Any) -> Result:
        """MansionSQL query over a calculated chart. Wraps ``POST /v1/query``.

        Args:
            body: The request body as one mapping, instead of keyword fields.
            **fields: Body fields as keywords: ``birth``, ``partner``, ``moment``, ``sql``, ``query``, ``format``, ``border``.

        Returns:
            The decoded response.

        Raises:
            TypeError: Both a body mapping and keyword fields were given.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "POST",
            "/v1/query",
            json=RequestBodies.merge(body, fields),
            binary=False,
            technique="query",
            enveloped=None,
        )

    def rectification(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Birth-time rectification. Wraps ``POST /v1/rectification``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/rectification",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="rectification",
            enveloped=True,
        )

    def render_astrocartography(
        self,
        body: dict[str, Any] | None = None,
        output: str | Path | None = None,
        **fields: Any,
    ) -> bytes | Path:
        """Astrocartography map with line meanings. Wraps ``POST /v1/render/astrocartography``.

        Args:
            body: The request body as one mapping, instead of keyword fields.
            output: Path to write the document to, or ``None`` for the bytes.
            **fields: Body fields as keywords: ``birth``, ``place``, ``lang``.

        Returns:
            The document's bytes, or the path it was written to.

        Raises:
            TypeError: Both a body mapping and keyword fields were given.
            AstroMansionError: The API refused the call, or never answered.
        """
        return Responses.save_document(
            self.request(
                "POST",
                "/v1/render/astrocartography",
                json=RequestBodies.merge(body, fields),
                binary=True,
                technique="render_astrocartography",
                enveloped=None,
            ),
            output,
        )

    def render_biwheel(
        self,
        birth: dict[str, Any],
        partner: dict[str, Any],
        *,
        options: dict[str, Any] | None = None,
        output: str | Path | None = None,
        **extra: Any,
    ) -> bytes | Path:
        """Bi-wheel chart (natal and second chart). Wraps ``POST /v1/render/biwheel``.

        Args:
            birth: The first person's birth fields, as ``natal`` takes them.
            partner: The second person's birth fields.
            options: The endpoint's options.
            output: Path to write the document to, or ``None`` for the bytes.
            **extra: Further top-level body fields.

        Returns:
            The document's bytes, or the path it was written to.

        Raises:
            ValidationError: A birth field of either person is malformed, or
                the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return Responses.save_document(
            self._pair(
                "/v1/render/biwheel",
                birth,
                partner,
                options,
                binary=True,
                technique="render_biwheel",
                enveloped=None,
                **extra,
            ),
            output,
        )

    def render_png(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
        output: str | Path | None = None,
    ) -> bytes | Path:
        """Chart wheel PNG image. Wraps ``POST /v1/render/png``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.
            output: Path to write the document to, or ``None`` for the bytes.

        Returns:
            The document's bytes, or the path it was written to.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return Responses.save_document(
            self._chart(
                "/v1/render/png",
                payload,
                options,
                date=date,
                lat=lat,
                lon=lon,
                time=time,
                timezone=timezone,
                houses=houses,
                binary=True,
                technique="render_png",
                enveloped=None,
            ),
            output,
        )

    def render_svg(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
        output: str | Path | None = None,
    ) -> bytes | Path:
        """Chart wheel SVG with optional interactive HTML. Wraps ``POST /v1/render/svg``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.
            output: Path to write the document to, or ``None`` for the bytes.

        Returns:
            The document's bytes, or the path it was written to.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return Responses.save_document(
            self._chart(
                "/v1/render/svg",
                payload,
                options,
                date=date,
                lat=lat,
                lon=lon,
                time=time,
                timezone=timezone,
                houses=houses,
                binary=True,
                technique="render_svg",
                enveloped=None,
            ),
            output,
        )

    def retrogrades(self, **params: Any) -> Result:
        """Planetary retrograde calendar. Wraps ``GET /v1/retrogrades``.

        Args:
            **params: Query parameters; those set to ``None`` are left out.

        Returns:
            The decoded response.

        Raises:
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "GET",
            "/v1/retrogrades",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="retrogrades",
            enveloped=False,
        )

    def saturn_return(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Saturn return dates. Wraps ``POST /v1/saturn-return``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/saturn-return",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="saturn_return",
            enveloped=False,
        )

    def solar_arc(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Solar arc directions. Wraps ``POST /v1/solar-arc``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/solar-arc",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="solar_arc",
            enveloped=True,
        )

    def solar_return(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Solar return chart. Wraps ``POST /v1/solar-return``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/solar-return",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="solar_return",
            enveloped=True,
        )

    def stations(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Planetary stations and retrograde shadows. Wraps ``POST /v1/stations``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/stations",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="stations",
            enveloped=True,
        )

    def synastry(
        self,
        birth: dict[str, Any],
        partner: dict[str, Any],
        *,
        options: dict[str, Any] | None = None,
        **extra: Any,
    ) -> Result:
        """Two-chart synastry analysis. Wraps ``POST /v1/synastry``.

        Args:
            birth: The first person's birth fields, as ``natal`` takes them.
            partner: The second person's birth fields.
            options: The endpoint's options.
            **extra: Further top-level body fields.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field of either person is malformed, or
                the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._pair(
            "/v1/synastry",
            birth,
            partner,
            options,
            binary=False,
            technique="synastry",
            enveloped=True,
            **extra,
        )

    def timeline(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Life timing timeline. Wraps ``POST /v1/timeline``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/timeline",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="timeline",
            enveloped=True,
        )

    def transit_hits(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Exact aspect times with bisection precision. Wraps ``POST /v1/transit-hits``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/transit-hits",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="transit_hits",
            enveloped=True,
        )

    def transits(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Transit scan over a year or date range. Wraps ``POST /v1/transits``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/transits",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="transits",
            enveloped=True,
        )

    def vedic_chart(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Sidereal Vedic chart with rashi, nakshatra, and lagna. Wraps ``POST /v1/vedic-chart``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/vedic-chart",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="vedic_chart",
            enveloped=True,
        )

    def vimshottari(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Vimshottari dasha periods. Wraps ``POST /v1/vimshottari``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/vimshottari",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="vimshottari",
            enveloped=True,
        )

    def void_moon(self, **params: Any) -> Result:
        """Void-of-course Moon calendar. Wraps ``GET /v1/void-moon``.

        Args:
            **params: Query parameters; those set to ``None`` are left out.

        Returns:
            The decoded response.

        Raises:
            AstroMansionError: The API refused the call, or never answered.
        """
        return self.request(
            "GET",
            "/v1/void-moon",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="void_moon",
            enveloped=False,
        )

    def zodiacal_releasing(
        self,
        payload: dict[str, Any] | None = None,
        *,
        date: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        time: str | None = None,
        timezone: float | str | None = None,
        houses: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """Zodiacal releasing. Wraps ``POST /v1/zodiacal-releasing``.

        Birth fields come as one mapping or as keywords, never both.

        Args:
            payload: Birth fields as one mapping, instead of the keywords.
            date: Calendar date as ``YYYY-MM-DD``.
            lat: Latitude in decimal degrees, north positive.
            lon: Longitude in decimal degrees, east positive.
            time: Clock time as ``HH:MM``; omit it for an unknown birth time.
            timezone: UTC offset in hours, or an IANA zone name.
            houses: A house system identifier the API publishes.
            options: The endpoint's options.

        Returns:
            The decoded response.

        Raises:
            ValidationError: A birth field is malformed, or the API refused the body.
            AstroMansionError: The API refused the call, or never answered.
        """
        return self._chart(
            "/v1/zodiacal-releasing",
            payload,
            options,
            date=date,
            lat=lat,
            lon=lon,
            time=time,
            timezone=timezone,
            houses=houses,
            binary=False,
            technique="zodiacal_releasing",
            enveloped=True,
        )
