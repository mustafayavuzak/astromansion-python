"""Regressions for the defects a third-party review of 0.1.3 measured."""

from __future__ import annotations

import pathlib

import httpx
import pytest
import respx

from astromansion import (
    AstroMansion,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from astromansion.constants import Catalog

BASE = "https://api.astromansion.com"
KEY = "am_secret_key"
BIRTH = {"date": "1990-07-19", "lat": 41.0082, "lon": 28.9784}


def _client(**kwargs: object) -> AstroMansion:
    return AstroMansion(api_key=KEY, **kwargs)


# --- a path parameter must reach the URL -----------------------------------

@respx.mock(base_url=BASE)
def test_a_named_body_reaches_its_own_path(respx_mock: respx.Router) -> None:
    """0.1.3 sent the template itself, so every call hit ``/{name}``."""
    route = respx_mock.post("/v1/custom-body/ceres").mock(
        httpx.Response(200, json={}),
    )
    _client().chart_with_custom_body("ceres", birth=BIRTH)
    assert route.called


@respx.mock(base_url=BASE)
def test_a_path_parameter_cannot_reshape_the_path(
    respx_mock: respx.Router,
) -> None:
    """A slash in a name is part of the name, not a new path segment."""
    route = respx_mock.post(url__regex=r".*").mock(httpx.Response(200, json={}))
    _client().chart_with_custom_body("a/b c", birth=BIRTH)
    assert route.calls[0].request.url.raw_path == b"/v1/custom-body/a%2Fb%20c"


def test_no_generated_url_still_carries_a_template() -> None:
    """The generator must leave no placeholder behind in any method."""
    from astromansion import _methods, _methods_async

    for module in (_methods, _methods_async):
        source = pathlib.Path(module.__file__).read_text(encoding="utf-8")
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith('"/v1/') and "{" in stripped:
                raise AssertionError(f"unsubstituted path template: {stripped}")


# --- the key must not leave the API ----------------------------------------

@pytest.mark.parametrize(
    "target",
    [
        "https://other.example/collect",
        "http://other.example/collect",
        "//other.example/collect",
        "/collect",
        "v1/natal",
        "/v2/natal",
    ],
)
def test_request_refuses_a_target_that_is_not_an_api_path(target: str) -> None:
    """0.1.3 sent ``X-API-Key`` to whatever host the string named."""
    with pytest.raises(ValidationError):
        _client().request("GET", target)


@respx.mock(base_url=BASE)
def test_request_still_reaches_an_unnamed_api_path(
    respx_mock: respx.Router,
) -> None:
    """The escape hatch stays open for paths this release does not name."""
    route = respx_mock.post("/v1/not-yet-named").mock(
        httpx.Response(200, json={"ok": True}),
    )
    _client().request("POST", "/v1/not-yet-named", json={})
    assert route.called


def test_no_request_leaves_for_another_host_at_all() -> None:
    """Nothing is sent, so the key cannot leak even to a listening server."""
    with respx.mock(assert_all_called=False) as router:
        route = router.get(url__regex=r".*").mock(httpx.Response(200, json={}))
        with pytest.raises(ValidationError):
            _client().request("GET", "https://other.example/collect")
        assert route.call_count == 0


# --- a spent quota is not a busy moment ------------------------------------

@respx.mock(base_url=BASE)
def test_a_spent_quota_is_asked_about_once(respx_mock: respx.Router) -> None:
    """0.1.3 spent three round trips to be told the same thing."""
    route = respx_mock.post("/v1/natal").mock(
        httpx.Response(
            429, json={"error": {"code": "quota_exceeded", "message": "spent"}},
        ),
    )
    with pytest.raises(QuotaExceededError):
        _client(max_retries=2).natal(**BIRTH)
    assert route.call_count == 1


@respx.mock(base_url=BASE)
def test_a_real_rate_limit_is_still_retried(respx_mock: respx.Router) -> None:
    """The fix must not stop the client waiting out a busy moment."""
    route = respx_mock.post("/v1/natal").mock(
        side_effect=[
            httpx.Response(
                429,
                json={"error": {"code": "rate_limited"}},
                headers={"Retry-After": "0"},
            ),
            httpx.Response(200, json={"summary": {}}),
        ],
    )
    _client(max_retries=2).natal(**BIRTH)
    assert route.call_count == 2


@respx.mock(base_url=BASE)
def test_a_server_error_is_still_retried(respx_mock: respx.Router) -> None:
    route = respx_mock.post("/v1/natal").mock(
        side_effect=[
            httpx.Response(500, json={"error": {"code": "server_error"}}),
            httpx.Response(200, json={"summary": {}}),
        ],
    )
    _client(max_retries=2).natal(**BIRTH)
    assert route.call_count == 2


@respx.mock(base_url=BASE)
def test_a_rate_limit_without_a_body_is_still_retried(
    respx_mock: respx.Router,
) -> None:
    """No machine code means no reason to treat it as permanent."""
    route = respx_mock.post("/v1/natal").mock(
        side_effect=[
            httpx.Response(429, text="slow down", headers={"Retry-After": "0"}),
            httpx.Response(200, json={"summary": {}}),
        ],
    )
    _client(max_retries=2).natal(**BIRTH)
    assert route.call_count == 2


@respx.mock(base_url=BASE)
def test_the_quota_exception_is_still_the_one_raised(
    respx_mock: respx.Router,
) -> None:
    respx_mock.post("/v1/natal").mock(
        httpx.Response(429, json={"error": {"code": "quota_exceeded"}}),
    )
    with pytest.raises(QuotaExceededError):
        _client(max_retries=0).natal(**BIRTH)

    respx_mock.post("/v1/transits").mock(
        httpx.Response(429, json={"error": {"code": "rate_limited"}}),
    )
    with pytest.raises(RateLimitError):
        _client(max_retries=0).transits(**BIRTH)


# --- a partial catalog walk must not look complete -------------------------

@respx.mock(base_url=BASE)
def test_a_walk_that_never_ends_is_refused_rather_than_truncated(
    respx_mock: respx.Router,
) -> None:
    """Returning what was read would look like the whole category."""
    # The offset advances every time, so the walk is well formed and only the
    # ceiling can end it. An endlessly paging API must not read as a complete
    # answer that happens to be short.
    served = iter(range(1, 10 ** 6))
    route = respx_mock.post("/v1/chart").mock(
        side_effect=lambda request: httpx.Response(200, json={
            "bodies": {"fixed_stars": [{"name": "S"}]},
            "catalog_page": {"next_offset": next(served) * Catalog.PAGE_MAX},
        }),
    )
    with pytest.raises(ServerError):
        _client().bodies("fixed_stars", **BIRTH)
    assert route.call_count == Catalog.PAGE_CEILING


@respx.mock(base_url=BASE)
def test_a_walk_told_to_stand_still_is_refused(
    respx_mock: respx.Router,
) -> None:
    """An offset that does not advance would read one page forever."""
    route = respx_mock.post("/v1/chart").mock(
        httpx.Response(200, json={
            "bodies": {"fixed_stars": [{"name": "S"}]},
            "catalog_page": {"next_offset": 0},
        }),
    )
    with pytest.raises(ServerError):
        _client().bodies("fixed_stars", **BIRTH)
    assert route.call_count == 1
