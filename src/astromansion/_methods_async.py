"""Generated client methods, one per published endpoint.

Produced by ``tools/generate_endpoints.py``. Do not edit: rerun the generator
so the SDK cannot describe a surface the API does not serve.

Endpoints: 67
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from . import _core
from .response import Result


class AsyncEndpoints:
    """Every endpoint, mixed into the asynchronous client.

    The transport lives on the client this is mixed into. Declaring the three
    hooks here is what lets a type checker see the mixin as complete instead
    of reporting every method as calling something that does not exist.
    """

    if TYPE_CHECKING:

        async def request(
            self,
            method: str,
            path: str,
            *,
            binary: bool = ...,
            technique: str | None = ...,
            enveloped: bool | None = ...,
            **kwargs: Any,
        ) -> Any: ...

        async def _chart(
            self,
            path: str,
            payload: dict[str, Any] | None,
            options: dict[str, Any] | None,
            *,
            binary: bool = ...,
            technique: str | None = ...,
            enveloped: bool | None = ...,
            **fields: Any,
        ) -> Any: ...

        async def _pair(
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
        ) -> Any: ...

        @staticmethod
        def _document(content: Any, output: str | Path | None) -> Any: ...

    async def almanac(
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
        """Eclipses, retrogrades, planetary hours, and void Moon….

        Wraps ``POST /v1/almanac``.
        """
        return await self._chart(
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

    async def antiscia(
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
        """Antiscia and contra-antiscia.

        Wraps ``POST /v1/antiscia``.
        """
        return await self._chart(
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

    async def aspects(
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
        """Complete natal aspect list.

        Wraps ``POST /v1/aspects``.
        """
        return await self._chart(
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

    async def astrocartography(
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
        """Astrocartography lines.

        Wraps ``POST /v1/astrocartography``.
        """
        return await self._chart(
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

    async def batch(self, body: dict[str, Any] | None = None, **fields: Any) -> Result:
        """Batch computation (Enterprise). Wraps ``POST /v1/batch``.

        Body fields: ``items``.
        """
        return await self.request(
            "POST",
            "/v1/batch",
            json=_core.Arguments.merge(body, fields),
            binary=False,
            technique="batch",
            enveloped=None,
        )

    async def chart(
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
        """Extended natal chart with category selection.

        Wraps ``POST /v1/chart``.
        """
        return await self._chart(
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

    async def compatibility(
        self,
        birth: dict[str, Any],
        partner: dict[str, Any],
        *,
        options: dict[str, Any] | None = None,
        **extra: Any,
    ) -> Result:
        """Compatibility score from 0 to 100. Wraps ``POST /v1/compatibility``.

        Both people are mappings of the fields ``natal`` accepts.
        """
        return await self._pair(
            "/v1/compatibility",
            birth,
            partner,
            options,
            binary=False,
            technique="compatibility",
            enveloped=True,
            **extra,
        )

    async def composite(
        self,
        birth: dict[str, Any],
        partner: dict[str, Any],
        *,
        options: dict[str, Any] | None = None,
        **extra: Any,
    ) -> Result:
        """Midpoint composite chart. Wraps ``POST /v1/composite``.

        Both people are mappings of the fields ``natal`` accepts.
        """
        return await self._pair(
            "/v1/composite",
            birth,
            partner,
            options,
            binary=False,
            technique="composite",
            enveloped=True,
            **extra,
        )

    async def custom_body(
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
        """Custom elliptic or hyperbolic Keplerian body.

        Wraps ``POST /v1/custom-body``.
        """
        return await self._chart(
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

    async def custom_bodies(self, **params: Any) -> Result:
        """List saved custom bodies.

        Wraps ``GET /v1/custom-body/list``.
        """
        return await self.request(
            "GET",
            "/v1/custom-body/list",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="custom_bodies",
            enveloped=None,
        )

    async def save_custom_body(
        self, body: dict[str, Any] | None = None, **fields: Any
    ) -> Result:
        """Save and calculate a named custom Keplerian body. Wraps ``POST /v1/custom-body/save``.

        Body fields: ``birth``, ``name``, ``elements``, ``heliocentric``, ``save``, ``wheel``, ``aspects``.
        """
        return await self.request(
            "POST",
            "/v1/custom-body/save",
            json=_core.Arguments.merge(body, fields),
            binary=False,
            technique="save_custom_body",
            enveloped=None,
        )

    async def chart_with_custom_body(
        self, name: str, body: dict[str, Any] | None = None, **fields: Any
    ) -> Result:
        """Calculate a saved custom body by name. Wraps ``POST /v1/custom-body/{name}``.

        Body fields: ``birth``, ``wheel``, ``aspects``.
        """
        return await self.request(
            "POST",
            f"/v1/custom-body/{quote(str(name), safe='')}",
            json=_core.Arguments.merge(body, fields),
            binary=False,
            technique="chart_with_custom_body",
            enveloped=None,
        )

    async def delete_custom_body(self, name: str, **params: Any) -> Result:
        """Delete a saved custom body.

        Wraps ``DELETE /v1/custom-body/{name}``.
        """
        return await self.request(
            "DELETE",
            f"/v1/custom-body/{quote(str(name), safe='')}",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="delete_custom_body",
            enveloped=None,
        )

    async def custom_lot(
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
        """Custom Arabic lot formula (A+B-C).

        Wraps ``POST /v1/custom-lot``.
        """
        return await self._chart(
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

    async def daily(
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
        """Daily sky summary.

        Wraps ``POST /v1/daily``.
        """
        return await self._chart(
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

    async def declinations(
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
        """Declination parallels.

        Wraps ``POST /v1/declinations``.
        """
        return await self._chart(
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

    async def dignities(
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
        """Classical dignities and almuten.

        Wraps ``POST /v1/dignities``.
        """
        return await self._chart(
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

    async def draconic(
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
        """Draconic zodiac.

        Wraps ``POST /v1/draconic``.
        """
        return await self._chart(
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

    async def eclipses(self, **params: Any) -> Result:
        """Eclipse calendar.

        Wraps ``GET /v1/eclipses``.
        """
        return await self.request(
            "GET",
            "/v1/eclipses",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="eclipses",
            enveloped=False,
        )

    async def electional(
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
        """Electional date-window scan.

        Wraps ``POST /v1/electional``.
        """
        return await self._chart(
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

    async def export_csv(
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
        """Chart data as CSV.

        Wraps ``POST /v1/export/csv``.
        """
        return self._document(
            await self._chart(
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

    async def export_pdf(
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
        """Multi-page PDF report.

        Wraps ``POST /v1/export/pdf``.
        """
        return self._document(
            await self._chart(
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

    async def export_report(
        self, body: dict[str, Any] | None = None, **fields: Any
    ) -> Result:
        """Editable multi-page PDF report. Wraps ``POST /v1/export/report``.

        Body fields: ``birth``, ``sections``, ``page_size``, ``title``, ``author``, ``custom_text``, ``accent``, ``white_label``, ``logo_b64``.
        """
        return await self.request(
            "POST",
            "/v1/export/report",
            json=_core.Arguments.merge(body, fields),
            binary=False,
            technique="export_report",
            enveloped=None,
        )

    async def firdaria(
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
        """Firdaria periods.

        Wraps ``POST /v1/firdaria``.
        """
        return await self._chart(
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

    async def search_places(self, **params: Any) -> Result:
        """Search place names.

        Wraps ``GET /v1/geo/search``.
        """
        return await self.request(
            "GET",
            "/v1/geo/search",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="search_places",
            enveloped=False,
        )

    async def harmonics(
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
        """Harmonic chart.

        Wraps ``POST /v1/harmonics``.
        """
        return await self._chart(
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

    async def health(self, **params: Any) -> Result:
        """Service health check.

        Wraps ``GET /v1/health``.
        """
        return await self.request(
            "GET",
            "/v1/health",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="health",
            enveloped=None,
        )

    async def heliacal(
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
        """Heliacal rising and setting events.

        Wraps ``POST /v1/heliacal``.
        """
        return await self._chart(
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

    async def heliocentric(
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
        """Heliocentric positions.

        Wraps ``POST /v1/heliocentric``.
        """
        return await self._chart(
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

    async def horary(
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
        """Horary question chart.

        Wraps ``POST /v1/horary``.
        """
        return await self._chart(
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

    async def list_jobs(self, **params: Any) -> Result:
        """List jobs.

        Wraps ``GET /v1/jobs``.
        """
        return await self.request(
            "GET",
            "/v1/jobs",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="list_jobs",
            enveloped=False,
        )

    async def submit_job(
        self, body: dict[str, Any] | None = None, **fields: Any
    ) -> Result:
        """Create an async job for any technique. Wraps ``POST /v1/jobs``.

        Body fields: ``technique``, ``body``, ``callback_url``.
        """
        return await self.request(
            "POST",
            "/v1/jobs",
            json=_core.Arguments.merge(body, fields),
            binary=False,
            technique="submit_job",
            enveloped=None,
        )

    async def submit_batch_job(
        self, body: dict[str, Any] | None = None, **fields: Any
    ) -> Result:
        """Create an async job batch of up to 20 items. Wraps ``POST /v1/jobs/batch``.

        Body fields: ``items``.
        """
        return await self.request(
            "POST",
            "/v1/jobs/batch",
            json=_core.Arguments.merge(body, fields),
            binary=False,
            technique="submit_batch_job",
            enveloped=None,
        )

    async def job(self, job_id: str, **params: Any) -> Result:
        """Inspect job status.

        Wraps ``GET /v1/jobs/{job_id}``.
        """
        return await self.request(
            "GET",
            f"/v1/jobs/{quote(str(job_id), safe='')}",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="job",
            enveloped=True,
        )

    async def lunar_return(
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
        """Lunar return charts.

        Wraps ``POST /v1/lunar-return``.
        """
        return await self._chart(
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

    async def mansions(
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
        """Twenty-eight lunar mansions.

        Wraps ``POST /v1/mansions``.
        """
        return await self._chart(
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

    async def midpoints(
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
        """Planetary midpoints.

        Wraps ``POST /v1/midpoints``.
        """
        return await self._chart(
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

    async def moon_phases(self, **params: Any) -> Result:
        """Lunar phase calendar.

        Wraps ``GET /v1/moon-phases``.
        """
        return await self.request(
            "GET",
            "/v1/moon-phases",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="moon_phases",
            enveloped=False,
        )

    async def moon_phases_for(
        self, body: dict[str, Any] | None = None, **fields: Any
    ) -> Result:
        """Lunar phase query filtered by month and phase. Wraps ``POST /v1/moon-phases/query``.

        Body fields: ``year``, ``month``, ``only``.
        """
        return await self.request(
            "POST",
            "/v1/moon-phases/query",
            json=_core.Arguments.merge(body, fields),
            binary=False,
            technique="moon_phases_for",
            enveloped=False,
        )

    async def nakshatra(
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
        """Moon nakshatra, pada, and ruler.

        Wraps ``POST /v1/nakshatra``.
        """
        return await self._chart(
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

    async def natal(
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
        """Free natal chart.

        Wraps ``POST /v1/natal``.
        """
        return await self._chart(
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

    async def navamsa(
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
        """D9 Navamsa and other divisional charts.

        Wraps ``POST /v1/navamsa``.
        """
        return await self._chart(
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

    async def pair_aspects(
        self,
        birth: dict[str, Any],
        partner: dict[str, Any],
        *,
        options: dict[str, Any] | None = None,
        **extra: Any,
    ) -> Result:
        """Aspects between two charts. Wraps ``POST /v1/pair-aspects``.

        Both people are mappings of the fields ``natal`` accepts.
        """
        return await self._pair(
            "/v1/pair-aspects",
            birth,
            partner,
            options,
            binary=False,
            technique="pair_aspects",
            enveloped=True,
            **extra,
        )

    async def parans(
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
        """Fixed-star parans.

        Wraps ``POST /v1/parans``.
        """
        return await self._chart(
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

    async def patterns(
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
        """Jones patterns, stelliums, and aspect figures.

        Wraps ``POST /v1/patterns``.
        """
        return await self._chart(
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

    async def profection(
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
        """Annual profections.

        Wraps ``POST /v1/profection``.
        """
        return await self._chart(
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

    async def progression(
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
        """Secondary progressions.

        Wraps ``POST /v1/progression``.
        """
        return await self._chart(
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

    async def query(self, body: dict[str, Any] | None = None, **fields: Any) -> Result:
        """MansionSQL query over a calculated chart. Wraps ``POST /v1/query``.

        Body fields: ``birth``, ``partner``, ``moment``, ``sql``, ``query``, ``format``, ``border``.
        """
        return await self.request(
            "POST",
            "/v1/query",
            json=_core.Arguments.merge(body, fields),
            binary=False,
            technique="query",
            enveloped=None,
        )

    async def rectification(
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
        """Birth-time rectification.

        Wraps ``POST /v1/rectification``.
        """
        return await self._chart(
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

    async def render_astrocartography(
        self,
        body: dict[str, Any] | None = None,
        output: str | Path | None = None,
        **fields: Any,
    ) -> bytes | Path:
        """Astrocartography map with line meanings. Wraps ``POST /v1/render/astrocartography``.

        Body fields: ``birth``, ``place``, ``lang``.
        """
        return self._document(
            await self.request(
                "POST",
                "/v1/render/astrocartography",
                json=_core.Arguments.merge(body, fields),
                binary=True,
                technique="render_astrocartography",
                enveloped=None,
            ),
            output,
        )

    async def render_biwheel(
        self,
        birth: dict[str, Any],
        partner: dict[str, Any],
        *,
        options: dict[str, Any] | None = None,
        output: str | Path | None = None,
        **extra: Any,
    ) -> bytes | Path:
        """Bi-wheel chart (natal and second chart). Wraps ``POST /v1/render/biwheel``.

        Both people are mappings of the fields ``natal`` accepts.
        """
        return self._document(
            await self._pair(
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

    async def render_png(
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
        """Chart wheel PNG image.

        Wraps ``POST /v1/render/png``.
        """
        return self._document(
            await self._chart(
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

    async def render_sharecard(
        self,
        body: dict[str, Any] | None = None,
        output: str | Path | None = None,
        **fields: Any,
    ) -> bytes | Path:
        """Story card, natal or synastry (1080x1920). Wraps ``POST /v1/render/sharecard``.

        Body fields: ``birth``, ``partner``, ``type``, ``names``, ``lang``.
        """
        return self._document(
            await self.request(
                "POST",
                "/v1/render/sharecard",
                json=_core.Arguments.merge(body, fields),
                binary=True,
                technique="render_sharecard",
                enveloped=None,
            ),
            output,
        )

    async def render_svg(
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
        """Chart wheel SVG with optional interactive HTML.

        Wraps ``POST /v1/render/svg``.
        """
        return self._document(
            await self._chart(
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

    async def retrogrades(self, **params: Any) -> Result:
        """Planetary retrograde calendar.

        Wraps ``GET /v1/retrogrades``.
        """
        return await self.request(
            "GET",
            "/v1/retrogrades",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="retrogrades",
            enveloped=False,
        )

    async def saturn_return(
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
        """Saturn return dates.

        Wraps ``POST /v1/saturn-return``.
        """
        return await self._chart(
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

    async def solar_arc(
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
        """Solar arc directions.

        Wraps ``POST /v1/solar-arc``.
        """
        return await self._chart(
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

    async def solar_return(
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
        """Solar return chart.

        Wraps ``POST /v1/solar-return``.
        """
        return await self._chart(
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

    async def stations(
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
        """Planetary stations and retrograde shadows.

        Wraps ``POST /v1/stations``.
        """
        return await self._chart(
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

    async def synastry(
        self,
        birth: dict[str, Any],
        partner: dict[str, Any],
        *,
        options: dict[str, Any] | None = None,
        **extra: Any,
    ) -> Result:
        """Two-chart synastry analysis. Wraps ``POST /v1/synastry``.

        Both people are mappings of the fields ``natal`` accepts.
        """
        return await self._pair(
            "/v1/synastry",
            birth,
            partner,
            options,
            binary=False,
            technique="synastry",
            enveloped=True,
            **extra,
        )

    async def timeline(
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
        """Life timing timeline.

        Wraps ``POST /v1/timeline``.
        """
        return await self._chart(
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

    async def transit_hits(
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
        """Exact aspect times with bisection precision.

        Wraps ``POST /v1/transit-hits``.
        """
        return await self._chart(
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

    async def transits(
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
        """Transit scan over a year or date range.

        Wraps ``POST /v1/transits``.
        """
        return await self._chart(
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

    async def vedic_chart(
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
        """Sidereal Vedic chart with rashi, nakshatra, and lagna.

        Wraps ``POST /v1/vedic-chart``.
        """
        return await self._chart(
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

    async def vimshottari(
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
        """Vimshottari dasha periods.

        Wraps ``POST /v1/vimshottari``.
        """
        return await self._chart(
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

    async def void_moon(self, **params: Any) -> Result:
        """Void-of-course Moon calendar.

        Wraps ``GET /v1/void-moon``.
        """
        return await self.request(
            "GET",
            "/v1/void-moon",
            params={k: v for k, v in params.items() if v is not None},
            binary=False,
            technique="void_moon",
            enveloped=False,
        )

    async def zodiacal_releasing(
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
        """Zodiacal releasing.

        Wraps ``POST /v1/zodiacal-releasing``.
        """
        return await self._chart(
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
