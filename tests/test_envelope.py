"""Bir cevap, gonderildigi sekle bakilmaksizin ayni okunur.

Sunucu bazi uclarda veriyi dogrudan, bazilarinda `{technique, result}` icinde
donduruyordu. `natal.summary` ogrenen cagiran, `chart.summary` yazinca hata
aliyordu; oysa fark istegiyle hicbir ilgisi olmayan bir sunucu ayrintisi.
"""

from __future__ import annotations

import httpx
import pytest
import respx

from astromansion import AstroMansion
from astromansion.response import Result

BASE = "https://api.astromansion.com"
KEY = "am_live_testkey_0123456789abcdef"
BIRTH = {"date": "1990-07-19", "lat": 41.0082, "lon": 28.9784}
DATA = {"summary": {"Sun": {"sign": "Leo"}}, "aspects": []}
WRAPPED = {"technique": "chart", "result": DATA}


def _client() -> AstroMansion:
    return AstroMansion(api_key=KEY, max_retries=0)


@respx.mock
def test_a_direct_response_reads_flat() -> None:
    respx.post(f"{BASE}/v1/natal").mock(httpx.Response(200, json=DATA))
    response = _client().natal(**BIRTH)
    assert response.summary.Sun.sign == "Leo"
    assert response.technique == "natal"


@respx.mock
def test_an_enveloped_response_reads_the_same_way() -> None:
    respx.post(f"{BASE}/v1/chart").mock(httpx.Response(200, json=WRAPPED))
    response = _client().chart(**BIRTH)
    assert response.summary.Sun.sign == "Leo"
    assert response.technique == "chart"


@respx.mock
def test_the_original_body_is_kept() -> None:
    respx.post(f"{BASE}/v1/chart").mock(httpx.Response(200, json=WRAPPED))
    response = _client().chart(**BIRTH)
    assert response.raw["technique"] == "chart"
    assert "result" in response.raw


@respx.mock
def test_the_server_s_own_name_stays_reachable() -> None:
    respx.post(f"{BASE}/v1/chart").mock(httpx.Response(200, json=WRAPPED))
    response = _client().chart(**BIRTH)
    assert response.result.summary.Sun.sign == "Leo"
    assert response.data.summary.Sun.sign == "Leo"


@respx.mock
def test_a_list_result_is_read_through_data() -> None:
    """A query answers with rows, which have no attributes to offer."""
    rows = [{"name": "Kingship", "sign": "Gemini"}]
    respx.post(f"{BASE}/v1/query").mock(
        httpx.Response(200, json={"technique": "query", "result": rows}),
    )
    response = _client().query(birth=BIRTH)
    assert response.technique == "query"
    assert len(response.data) == 1
    assert response.data[0].name == "Kingship"
    with pytest.raises(AttributeError) as caught:
        _ = response.name
    assert ".data" in str(caught.value)


def test_a_payload_owning_a_result_field_is_not_unwrapped() -> None:
    """Strictness matters: real data may name a field `result`.

    Unwrapping on the mere presence of `result` would throw away everything
    beside it the day an endpoint publishes one.
    """
    payload = {"result": "won", "score": 3, "technique": "match"}
    built = Result.build(payload, technique="whatever", enveloped=None)
    assert built.score == 3
    assert built.result == "won"


def test_the_schema_decides_when_it_knows() -> None:
    """A declared envelope is opened even if the body looks unusual."""
    payload = {"technique": "x", "result": {"a": 1}, "extra": 2}
    assert Result.build(payload, enveloped=True).a == 1
    # And a schema that says flat is honoured over the shape.
    # A schema that says flat is honoured over the shape: the body stays the
    # data, so its own `technique` field is data rather than a label.
    flat = Result.build({"technique": "x", "result": {"a": 1}}, enveloped=False)
    assert flat.technique is None
    assert flat["technique"] == "x"
    assert flat["result"] == {"a": 1}
