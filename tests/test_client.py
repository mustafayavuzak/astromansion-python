"""Client behaviour, checked against a mocked transport.

No test reaches the production API. Every request is answered locally, so the
suite spends no quota and passes without credentials.
"""

from __future__ import annotations

import asyncio
import json

import httpx
import pytest
import respx

import astromansion as am
from astromansion import (
    AstroMansion,
    AstroMansionConnectionError,
    AstroMansionError,
    AsyncAstroMansion,
    AuthenticationError,
    PermissionDeniedError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    ValidationError,
)

BASE = "https://api.astromansion.com"
KEY = "am_live_testkey_0123456789abcdef"
BIRTH = {"date": "1990-07-19", "time": "14:30", "lat": 41.0082, "lon": 28.9784}
NATAL = {
    "summary": {"Sun": {"sign": "Cancer", "dms": "26 32 37"}},
    "planets": [{"name": "Sun", "sign": "Cancer", "house": 9}],
    "aspects": [],
}


@pytest.fixture(autouse=True)
def _clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """No ambient key or shared client leaks between tests."""
    monkeypatch.delenv("ASTROMANSION_API_KEY", raising=False)
    monkeypatch.delenv("ASTROMANSION_BASE_URL", raising=False)
    am.reset()


# ------------------------------------------------------------ credentials


@respx.mock
def test_an_explicit_key_travels_in_the_documented_header() -> None:
    route = respx.post(f"{BASE}/v1/natal").mock(httpx.Response(200, json=NATAL))
    AstroMansion(api_key=KEY).natal(**BIRTH)
    assert route.calls.last.request.headers["X-API-Key"] == KEY


@respx.mock
def test_the_environment_supplies_the_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ASTROMANSION_API_KEY", KEY)
    route = respx.post(f"{BASE}/v1/natal").mock(httpx.Response(200, json=NATAL))
    AstroMansion().natal(**BIRTH)
    assert route.calls.last.request.headers["X-API-Key"] == KEY


@respx.mock
def test_an_explicit_key_outranks_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ASTROMANSION_API_KEY", "am_live_environment_key")
    route = respx.post(f"{BASE}/v1/natal").mock(httpx.Response(200, json=NATAL))
    AstroMansion(api_key=KEY).natal(**BIRTH)
    assert route.calls.last.request.headers["X-API-Key"] == KEY


@respx.mock
def test_set_api_key_reaches_the_shortcuts() -> None:
    route = respx.post(f"{BASE}/v1/natal").mock(httpx.Response(200, json=NATAL))
    am.set_api_key(KEY)
    am.natal(**BIRTH)
    assert route.calls.last.request.headers["X-API-Key"] == KEY


@respx.mock
def test_set_api_key_replaces_a_key_already_in_use() -> None:
    """A second call must not keep answering with the first key."""
    route = respx.post(f"{BASE}/v1/natal").mock(httpx.Response(200, json=NATAL))
    am.set_api_key("am_live_first_key_padding")
    am.natal(**BIRTH)
    am.set_api_key(KEY)
    am.natal(**BIRTH)
    assert route.calls.last.request.headers["X-API-Key"] == KEY


def test_reset_forgets_the_key_and_the_client() -> None:
    """Reset returns the shortcuts to reading the environment."""
    am.set_api_key(KEY)
    am.reset()
    with respx.mock:
        route = respx.post(f"{BASE}/v1/natal")
        with pytest.raises(AuthenticationError):
            am.natal(**BIRTH)
        assert not route.called


def test_reset_leaves_explicit_clients_alone() -> None:
    client = AstroMansion(api_key=KEY)
    am.reset()
    with respx.mock:
        route = respx.post(f"{BASE}/v1/natal").mock(
            httpx.Response(200, json=NATAL),
        )
        client.natal(**BIRTH)
    assert route.calls.last.request.headers["X-API-Key"] == KEY


def test_a_missing_key_fails_before_any_request_is_sent() -> None:
    with respx.mock:
        route = respx.post(f"{BASE}/v1/natal")
        with pytest.raises(AuthenticationError):
            AstroMansion().natal(**BIRTH)
        assert not route.called, "anahtarsiz istek yine de gonderildi"


@respx.mock
def test_two_clients_keep_their_own_keys() -> None:
    route = respx.post(f"{BASE}/v1/natal").mock(httpx.Response(200, json=NATAL))
    AstroMansion(api_key="am_live_first_padding").natal(**BIRTH)
    AstroMansion(api_key="am_live_second_padding").natal(**BIRTH)
    sent = [call.request.headers["X-API-Key"] for call in route.calls]
    assert sent == ["am_live_first_padding", "am_live_second_padding"]


# ---------------------------------------------------------------- secrecy


def test_the_key_never_appears_in_the_repr() -> None:
    text = repr(AstroMansion(api_key=KEY))
    assert KEY not in text


def test_the_key_never_appears_in_an_error() -> None:
    with respx.mock:
        respx.post(f"{BASE}/v1/natal").mock(
            httpx.Response(
                401,
                json={"error": {"code": "unauthorized", "message": "no"}},
            ),
        )
        with pytest.raises(AuthenticationError) as caught:
            AstroMansion(api_key=KEY).natal(**BIRTH)
    assert KEY not in str(caught.value)
    assert KEY not in repr(caught.value)


def test_the_key_never_travels_in_the_query_string() -> None:
    with respx.mock:
        route = respx.post(f"{BASE}/v1/natal").mock(
            httpx.Response(200, json=NATAL),
        )
        AstroMansion(api_key=KEY).natal(**BIRTH)
    assert KEY not in str(route.calls.last.request.url)


# --------------------------------------------------------------- requests


@respx.mock
def test_a_trailing_slash_does_not_double_the_path() -> None:
    route = respx.post(f"{BASE}/v1/natal").mock(httpx.Response(200, json=NATAL))
    AstroMansion(api_key=KEY, base_url=f"{BASE}/").natal(**BIRTH)
    assert str(route.calls.last.request.url) == f"{BASE}/v1/natal"


@respx.mock
def test_the_body_matches_the_wire_contract() -> None:
    """The API nests birth data; callers pass it flat."""
    route = respx.post(f"{BASE}/v1/natal").mock(httpx.Response(200, json=NATAL))
    AstroMansion(api_key=KEY).natal(**BIRTH, timezone=3)
    body = json.loads(route.calls.last.request.content)
    assert set(body) == {"birth"}
    assert body["birth"] == {
        "date": "1990-07-19",
        "lat": 41.0082,
        "lon": 28.9784,
        "time": "14:30",
        "timezone": 3,
    }


@respx.mock
def test_a_two_person_body_names_birth_and_partner() -> None:
    """The API names the second chart `partner`, not `second`."""
    route = respx.post(f"{BASE}/v1/synastry").mock(
        httpx.Response(200, json={"ok": True}),
    )
    AstroMansion(api_key=KEY).synastry(BIRTH, BIRTH)
    body = json.loads(route.calls.last.request.content)
    assert set(body) == {"birth", "partner"}


@respx.mock
def test_a_mapping_and_keywords_reach_the_same_request() -> None:
    route = respx.post(f"{BASE}/v1/natal").mock(httpx.Response(200, json=NATAL))
    client = AstroMansion(api_key=KEY)
    client.natal(**BIRTH)
    client.natal(BIRTH)
    first, second = (call.request.content for call in route.calls)
    assert first == second


def test_mixing_a_mapping_with_keywords_is_refused() -> None:
    """Two sources for one field hides which one won."""
    with pytest.raises(TypeError):
        AstroMansion(api_key=KEY).natal(BIRTH, date="1991-01-01")


@pytest.mark.parametrize("bad", ["19-07-1990", "1990/07/19", "", "yesterday"])
def test_a_malformed_date_is_caught_before_the_network(bad: str) -> None:
    with respx.mock:
        route = respx.post(f"{BASE}/v1/natal")
        with pytest.raises(ValidationError):
            AstroMansion(api_key=KEY).natal(date=bad, lat=41.0, lon=29.0)
        assert not route.called


@respx.mock
def test_the_user_agent_names_the_package_and_version() -> None:
    route = respx.post(f"{BASE}/v1/natal").mock(httpx.Response(200, json=NATAL))
    AstroMansion(api_key=KEY).natal(**BIRTH)
    agent = route.calls.last.request.headers["User-Agent"]
    assert agent == f"astromansion/{am.__version__}"


@respx.mock
def test_request_applies_the_same_authentication_as_named_methods() -> None:
    route = respx.post(f"{BASE}/v1/harmonics").mock(
        httpx.Response(200, json={"ok": True}),
    )
    AstroMansion(api_key=KEY).request(
        "POST",
        "/v1/harmonics",
        json={"birth": BIRTH},
    )
    assert route.calls.last.request.headers["X-API-Key"] == KEY


# -------------------------------------------------------------- responses


@respx.mock
def test_a_response_reads_as_attributes_and_as_a_mapping() -> None:
    respx.post(f"{BASE}/v1/natal").mock(httpx.Response(200, json=NATAL))
    chart = AstroMansion(api_key=KEY).natal(**BIRTH)
    assert chart.summary.Sun.sign == "Cancer"
    assert chart["summary"]["Sun"]["sign"] == "Cancer"
    assert chart.planets[0].name == "Sun"
    assert chart.to_dict() == NATAL


@respx.mock
def test_an_unknown_field_survives_instead_of_being_dropped() -> None:
    """A field the server adds must reach the caller, not vanish."""
    respx.post(f"{BASE}/v1/natal").mock(
        httpx.Response(200, json={**NATAL, "houses": [1, 2], "new": "kept"}),
    )
    chart = AstroMansion(api_key=KEY).natal(**BIRTH)
    assert chart.new == "kept"
    assert chart.houses == [1, 2]


@respx.mock
def test_a_missing_field_names_what_was_available() -> None:
    respx.post(f"{BASE}/v1/natal").mock(httpx.Response(200, json=NATAL))
    chart = AstroMansion(api_key=KEY).natal(**BIRTH)
    with pytest.raises(AttributeError) as caught:
        _ = chart.houses
    assert "summary" in str(caught.value)


@respx.mock
def test_a_pdf_comes_back_as_bytes() -> None:
    respx.post(f"{BASE}/v1/export/pdf").mock(
        httpx.Response(
            200,
            content=b"%PDF-1.4 fake",
            headers={"Content-Type": "application/pdf"},
        ),
    )
    document = AstroMansion(api_key=KEY).export_pdf(BIRTH)
    assert isinstance(document, bytes)
    assert document.startswith(b"%PDF-")


@respx.mock
def test_a_pdf_is_written_only_when_a_path_is_given(tmp_path) -> None:
    respx.post(f"{BASE}/v1/export/pdf").mock(
        httpx.Response(
            200,
            content=b"%PDF-1.4 fake",
            headers={"Content-Type": "application/pdf"},
        ),
    )
    target = tmp_path / "chart.pdf"
    written = AstroMansion(api_key=KEY).export_pdf(BIRTH, output=target)
    assert written == target
    assert target.read_bytes().startswith(b"%PDF-")


# ----------------------------------------------------------------- errors


@pytest.mark.parametrize(
    "status,code,expected",
    [
        (401, "unauthorized", AuthenticationError),
        (402, "quota", QuotaExceededError),
        (403, "forbidden", PermissionDeniedError),
        (422, "validation", ValidationError),
        (429, "rate_limited", RateLimitError),
        (429, "quota_exceeded", QuotaExceededError),
        (500, "server_error", ServerError),
        (418, "teapot", AstroMansionError),
    ],
)
@respx.mock
def test_each_status_maps_to_the_error_that_names_it(
    status: int,
    code: str,
    expected: type[Exception],
) -> None:
    respx.post(f"{BASE}/v1/natal").mock(
        httpx.Response(status, json={"error": {"code": code, "message": "no"}}),
    )
    with pytest.raises(expected):
        AstroMansion(api_key=KEY, max_retries=0).natal(**BIRTH)


@respx.mock
def test_validation_detail_survives_to_the_caller() -> None:
    respx.post(f"{BASE}/v1/natal").mock(
        httpx.Response(
            422,
            json={
                "error": {
                    "code": "validation",
                    "message": "Invalid input.",
                    "detail": "birth.date: must be YYYY-MM-DD",
                }
            },
        ),
    )
    with pytest.raises(ValidationError) as caught:
        AstroMansion(api_key=KEY, max_retries=0).natal(**BIRTH)
    assert "birth.date" in str(caught.value.details)
    assert caught.value.status_code == 422
    assert caught.value.error_code == "validation"


@respx.mock
def test_a_body_that_is_not_the_envelope_does_not_crash_the_client() -> None:
    respx.post(f"{BASE}/v1/natal").mock(
        httpx.Response(500, content=b"<html>gateway</html>"),
    )
    with pytest.raises(ServerError) as caught:
        AstroMansion(api_key=KEY, max_retries=0).natal(**BIRTH)
    assert caught.value.status_code == 500


@respx.mock
def test_a_rate_limit_reports_the_wait_the_server_asked_for() -> None:
    respx.post(f"{BASE}/v1/natal").mock(
        httpx.Response(
            429,
            headers={"Retry-After": "12"},
            json={"error": {"code": "rate_limited", "message": "slow"}},
        ),
    )
    with pytest.raises(RateLimitError) as caught:
        AstroMansion(api_key=KEY, max_retries=0).natal(**BIRTH)
    assert caught.value.retry_after == 12.0


@respx.mock
def test_the_request_id_is_carried_for_support() -> None:
    respx.post(f"{BASE}/v1/natal").mock(
        httpx.Response(
            500,
            headers={"X-Request-ID": "req_abc123"},
            json={"error": {"code": "server_error", "message": "boom"}},
        ),
    )
    with pytest.raises(ServerError) as caught:
        AstroMansion(api_key=KEY, max_retries=0).natal(**BIRTH)
    assert caught.value.request_id == "req_abc123"
    assert "req_abc123" in str(caught.value)


@respx.mock
def test_a_timeout_becomes_a_connection_error() -> None:
    respx.post(f"{BASE}/v1/natal").mock(side_effect=httpx.ReadTimeout("slow"))
    with pytest.raises(AstroMansionConnectionError):
        AstroMansion(api_key=KEY, max_retries=0).natal(**BIRTH)


# ------------------------------------------------------------------ retry


@respx.mock
def test_a_server_error_is_retried_within_the_limit() -> None:
    route = respx.post(f"{BASE}/v1/natal").mock(
        side_effect=[
            httpx.Response(503, json={"error": {"code": "x", "message": "x"}}),
            httpx.Response(200, json=NATAL),
        ],
    )
    chart = AstroMansion(api_key=KEY, max_retries=2).natal(**BIRTH)
    assert chart.summary.Sun.sign == "Cancer"
    assert route.call_count == 2


@respx.mock
def test_retrying_stops_at_the_configured_limit() -> None:
    route = respx.post(f"{BASE}/v1/natal").mock(
        httpx.Response(503, json={"error": {"code": "x", "message": "x"}}),
    )
    with pytest.raises(ServerError):
        AstroMansion(api_key=KEY, max_retries=2).natal(**BIRTH)
    assert route.call_count == 3


@pytest.mark.parametrize("status", [400, 401, 403, 404, 422])
@respx.mock
def test_a_refusal_the_caller_must_fix_is_never_retried(status: int) -> None:
    """Repeating a rejected request cannot change the answer."""
    route = respx.post(f"{BASE}/v1/natal").mock(
        httpx.Response(status, json={"error": {"code": "n", "message": "n"}}),
    )
    with pytest.raises(AstroMansionError):
        AstroMansion(api_key=KEY, max_retries=3).natal(**BIRTH)
    assert route.call_count == 1


# ------------------------------------------------------------------ async


@respx.mock
async def test_the_async_client_matches_the_sync_one() -> None:
    route = respx.post(f"{BASE}/v1/natal").mock(httpx.Response(200, json=NATAL))
    async with AsyncAstroMansion(api_key=KEY) as client:
        chart = await client.natal(**BIRTH)
    assert chart.summary.Sun.sign == "Cancer"
    assert route.calls.last.request.headers["X-API-Key"] == KEY


@respx.mock
async def test_the_async_client_raises_the_same_errors() -> None:
    respx.post(f"{BASE}/v1/natal").mock(
        httpx.Response(403, json={"error": {"code": "forbidden", "message": "n"}}),
    )
    async with AsyncAstroMansion(api_key=KEY, max_retries=0) as client:
        with pytest.raises(PermissionDeniedError):
            await client.natal(**BIRTH)


async def test_the_async_context_manager_closes_the_pool() -> None:
    client = AsyncAstroMansion(api_key=KEY)
    async with client:
        pass
    assert client._client.is_closed


def test_the_sync_client_closes_its_pool() -> None:
    client = AstroMansion(api_key=KEY)
    with client:
        pass
    assert client._client.is_closed


def test_a_missing_key_is_reported_before_any_transport_is_built() -> None:
    """The key is checked in the constructor, not at the first request.

    Building an ``httpx`` client reads the proxy environment, and that step
    can fail on its own (a SOCKS proxy without ``socksio``, for one). A
    caller who simply forgot the key would then be handed somebody else's
    error, so the key is answered for first.
    """
    with pytest.raises(AuthenticationError):
        AstroMansion(transport=_ExplodingTransport())

    async def build() -> None:
        AsyncAstroMansion(transport=_ExplodingAsyncTransport())

    with pytest.raises(AuthenticationError):
        asyncio.run(build())


class _ExplodingTransport(httpx.BaseTransport):
    """Stand in for a transport whose construction the client must not reach."""

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        raise AssertionError("the transport was reached without a key")


class _ExplodingAsyncTransport(httpx.AsyncBaseTransport):
    """Async counterpart of :class:`_ExplodingTransport`."""

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        raise AssertionError("the transport was reached without a key")
