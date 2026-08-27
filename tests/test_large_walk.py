"""A category too large to read by accident says so before it starts."""

from __future__ import annotations

import httpx
import pytest
import respx

from astromansion import AstroMansion, ValidationError

BASE = "https://api.astromansion.com"
KEY = "am_test_key"
BIRTH = {"date": "2000-01-01", "lat": 51.4779, "lon": 0.0}


def _page(total: int, following: int | None, rows: int = 160) -> dict:
    return {
        "bodies": {"asteroids": [{"name": f"a{i}"} for i in range(rows)]},
        "catalog_page": {
            "offset": 0,
            "limit": 160,
            "total": total,
            "next_offset": following,
        },
    }


@respx.mock(base_url=BASE)
def test_a_twenty_eight_thousand_body_category_stops_and_says_so(
    respx_mock: respx.Router,
) -> None:
    """The real complaint this fixes: a program that prints nothing for a
    minute cannot be told apart from one that has hung."""
    route = respx_mock.post("/v1/chart").mock(
        httpx.Response(200, json=_page(28199, 160)),
    )
    with pytest.raises(ValidationError) as caught:
        AstroMansion(api_key=KEY).bodies("asteroids", **BIRTH)
    assert "28199" in str(caught.value)
    assert "177" in str(caught.value)
    # One request, not a hundred and seventy-seven.
    assert route.call_count == 1


@respx.mock(base_url=BASE)
def test_confirming_reads_it_anyway(respx_mock: respx.Router) -> None:
    served = iter([_page(320, 160), _page(320, None)])
    respx_mock.post("/v1/chart").mock(
        side_effect=lambda request: httpx.Response(200, json=next(served)),
    )
    found = AstroMansion(api_key=KEY).bodies("asteroids", confirm_large=True, **BIRTH)
    assert len(found["asteroids"]) == 320


@respx.mock(base_url=BASE)
def test_a_category_that_fits_needs_no_confirmation(
    respx_mock: respx.Router,
) -> None:
    """A category below the safety threshold needs no confirmation."""
    served = iter([_page(890, 160), _page(890, None)])
    respx_mock.post("/v1/chart").mock(
        side_effect=lambda request: httpx.Response(200, json=next(served)),
    )
    found = AstroMansion(api_key=KEY).bodies("asteroids", **BIRTH)
    assert len(found["asteroids"]) == 320


@respx.mock(base_url=BASE)
def test_progress_is_reported_page_by_page(respx_mock: respx.Router) -> None:
    """Watching it arrive is the other answer to the same complaint."""
    served = iter([_page(28199, 160), _page(28199, 320), _page(28199, None)])
    respx_mock.post("/v1/chart").mock(
        side_effect=lambda request: httpx.Response(200, json=next(served)),
    )
    seen: list[tuple[int, int, int]] = []
    AstroMansion(api_key=KEY).bodies(
        "asteroids",
        confirm_large=True,
        **BIRTH,
        on_page=lambda done, left, rows: seen.append(
            (done, left, len(rows["asteroids"]))
        ),
    )
    assert [row[0] for row in seen] == [1, 2, 3]
    assert seen[0][1] == 176
    assert [row[2] for row in seen] == [160, 320, 480]
