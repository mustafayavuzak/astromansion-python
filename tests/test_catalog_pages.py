"""Reading a whole catalog category, however many pages it takes."""

from __future__ import annotations

import asyncio

import httpx
import pytest
import respx

from astromansion import (
    AstroMansion,
    AsyncAstroMansion,
    ValidationError,
)

BASE = "https://api.astromansion.com"
KEY = "am_test_key"
BIRTH = {
    "date": "2000-01-01",
    "time": "12:00",
    "lat": 51.4779,
    "lon": 0.0,
    "timezone": 3,
}

# Measured against the live API at catalog_limit=10: the chart's own bodies
# fill the window first, so the opening page carries no star at all and the
# ``fixed_stars`` key is simply absent.
PAGES = [
    {
        "bodies": {"planets": [{"name": "Sun"}] * 10},
        "catalog_page": {"offset": 0, "total": 25, "next_offset": 10},
    },
    {
        "bodies": {
            "points": [{"name": "Asc"}] * 5,
            "fixed_stars": [{"name": f"S{i}"} for i in range(5)],
        },
        "catalog_page": {"offset": 10, "total": 25, "next_offset": 20},
    },
    {
        "bodies": {"fixed_stars": [{"name": f"T{i}"} for i in range(5)]},
        "catalog_page": {"offset": 20, "total": 25, "next_offset": None},
    },
]
STARS = ["S0", "S1", "S2", "S3", "S4", "T0", "T1", "T2", "T3", "T4"]


def _serve(router: respx.Router) -> respx.Route:
    """Answer each POST with the next page, in order."""
    pages = iter(PAGES)
    return router.post("/v1/chart").mock(
        side_effect=lambda request: httpx.Response(200, json=next(pages)),
    )


@respx.mock(base_url=BASE)
def test_the_walk_follows_every_page_to_the_end(respx_mock: respx.Router) -> None:
    route = _serve(respx_mock)
    found = AstroMansion(api_key=KEY).bodies("fixed_stars", **BIRTH)
    assert [star["name"] for star in found["fixed_stars"]] == STARS
    assert route.call_count == len(PAGES)


@respx.mock(base_url=BASE)
def test_a_page_holding_none_of_the_category_is_not_an_error(
    respx_mock: respx.Router,
) -> None:
    """The opening page carries only planets. That is ordinary, not a fault."""
    _serve(respx_mock)
    found = AstroMansion(api_key=KEY).bodies("fixed_stars", **BIRTH)
    assert len(found["fixed_stars"]) == 10


@respx.mock(base_url=BASE)
def test_each_request_asks_for_the_largest_page_the_api_serves(
    respx_mock: respx.Router,
) -> None:
    """A smaller page buys nothing but round trips, so it is not the default."""
    route = _serve(respx_mock)
    AstroMansion(api_key=KEY).bodies("fixed_stars", **BIRTH)
    first = route.calls[0].request
    assert b'"catalog_limit": 160' in first.content.replace(
        b'"catalog_limit":160', b'"catalog_limit": 160'
    )


@respx.mock(base_url=BASE)
def test_the_offsets_come_from_the_api_rather_than_being_counted_here(
    respx_mock: respx.Router,
) -> None:
    route = _serve(respx_mock)
    AstroMansion(api_key=KEY).bodies("fixed_stars", **BIRTH)
    sent = [call.request.content for call in route.calls]
    assert b'"catalog_offset": 0' in sent[0] or b'"catalog_offset":0' in sent[0]
    assert b'"catalog_offset": 10' in sent[1] or b'"catalog_offset":10' in sent[1]
    assert b'"catalog_offset": 20' in sent[2] or b'"catalog_offset":20' in sent[2]


@respx.mock(base_url=BASE)
def test_several_categories_are_read_in_one_walk(respx_mock: respx.Router) -> None:
    pages = [
        {
            "bodies": {"fixed_stars": [{"name": "S"}], "arabic_lots": [{"name": "L"}]},
            "catalog_page": {"next_offset": None},
        },
    ]
    served = iter(pages)
    route = respx_mock.post("/v1/chart").mock(
        side_effect=lambda request: httpx.Response(200, json=next(served)),
    )
    found = AstroMansion(api_key=KEY).bodies("fixed_stars", "arabic_lots", **BIRTH)
    assert set(found) == {"fixed_stars", "arabic_lots"}
    assert route.call_count == 1


@respx.mock(base_url=BASE)
def test_the_shape_does_not_depend_on_how_many_categories_were_asked_for(
    respx_mock: respx.Router,
) -> None:
    _serve(respx_mock)
    found = AstroMansion(api_key=KEY).bodies("fixed_stars", **BIRTH)
    assert isinstance(found, dict)
    assert list(found) == ["fixed_stars"]


def test_naming_no_category_is_refused_before_the_network() -> None:
    with pytest.raises(ValidationError):
        AstroMansion(api_key=KEY).bodies(**BIRTH)


@pytest.mark.parametrize("size", [0, -1, 161, 1000])
def test_a_page_size_the_api_would_refuse_is_refused_here(size: int) -> None:
    with pytest.raises(ValidationError):
        AstroMansion(api_key=KEY).bodies("fixed_stars", page_size=size, **BIRTH)


@respx.mock(base_url=BASE)
def test_the_async_client_walks_the_same_pages(respx_mock: respx.Router) -> None:
    route = _serve(respx_mock)

    async def walk() -> dict[str, list[object]]:
        async with AsyncAstroMansion(api_key=KEY) as client:
            return await client.bodies("fixed_stars", **BIRTH)

    found = asyncio.run(walk())
    assert [star["name"] for star in found["fixed_stars"]] == STARS
    assert route.call_count == len(PAGES)


@respx.mock(base_url=BASE)
def test_a_missing_next_offset_ends_the_walk(respx_mock: respx.Router) -> None:
    """A body without paging is one page, not a reason to keep asking."""
    route = respx_mock.post("/v1/chart").mock(
        httpx.Response(200, json={"bodies": {"fixed_stars": [{"name": "S"}]}}),
    )
    found = AstroMansion(api_key=KEY).bodies("fixed_stars", **BIRTH)
    assert route.call_count == 1
    assert len(found["fixed_stars"]) == 1
