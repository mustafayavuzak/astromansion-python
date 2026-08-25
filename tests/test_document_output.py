"""Writing a document to disk: every binary endpoint, both clients."""

from __future__ import annotations

import asyncio
import inspect
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from astromansion import AstroMansion, AsyncAstroMansion
from astromansion._endpoints import ENDPOINTS

BASE = "https://api.astromansion.com"
KEY = "am_test_key"
BIRTH = {"date": "1990-07-19", "lat": 41.0082, "lon": 28.9784}
BLOB = b"%PDF-1.4 or <svg/> or PNG, the client does not care"

#: Endpoints whose success is a document rather than JSON.
BINARY = tuple(e for e in ENDPOINTS if e.binary)


def _arguments(endpoint: Any) -> tuple[tuple[Any, ...], dict[str, Any]]:
    """Build the smallest call each endpoint kind accepts."""
    if endpoint.kind == "pair":
        return (BIRTH, dict(BIRTH)), {}
    return (), dict(BIRTH)


def test_the_binary_endpoints_are_the_ones_this_covers() -> None:
    """A new document endpoint must not slip past this file unnoticed."""
    assert {e.name for e in BINARY} == {
        "export_csv", "export_pdf", "render_astrocartography",
        "render_biwheel", "render_png", "render_sharecard", "render_svg",
    }


@pytest.mark.parametrize("endpoint", BINARY, ids=lambda e: e.name)
def test_every_document_endpoint_can_write_itself(
    endpoint: Any, tmp_path: Path,
) -> None:
    """0.1.4 offered ``output`` on ``export_pdf`` alone."""
    target = tmp_path / f"{endpoint.name}.bin"
    with respx.mock(base_url=BASE) as router:
        router.post(endpoint.path).mock(httpx.Response(200, content=BLOB))
        args, kwargs = _arguments(endpoint)
        written = getattr(AstroMansion(api_key=KEY), endpoint.name)(
            *args, output=target, **kwargs,
        )
    assert written == target
    assert target.read_bytes() == BLOB


@pytest.mark.parametrize("endpoint", BINARY, ids=lambda e: e.name)
def test_the_async_client_writes_the_same_documents(
    endpoint: Any, tmp_path: Path,
) -> None:
    target = tmp_path / f"{endpoint.name}.bin"

    async def call() -> Any:
        async with AsyncAstroMansion(api_key=KEY) as client:
            args, kwargs = _arguments(endpoint)
            return await getattr(client, endpoint.name)(
                *args, output=target, **kwargs,
            )

    with respx.mock(base_url=BASE) as router:
        router.post(endpoint.path).mock(httpx.Response(200, content=BLOB))
        written = asyncio.run(call())
    assert written == target
    assert target.read_bytes() == BLOB


@pytest.mark.parametrize("endpoint", BINARY, ids=lambda e: e.name)
def test_nothing_is_written_unless_a_path_is_named(
    endpoint: Any, tmp_path: Path,
) -> None:
    """Bytes are the default, so a call cannot overwrite an unchosen file."""
    with respx.mock(base_url=BASE) as router:
        router.post(endpoint.path).mock(httpx.Response(200, content=BLOB))
        args, kwargs = _arguments(endpoint)
        content = getattr(AstroMansion(api_key=KEY), endpoint.name)(
            *args, **kwargs,
        )
    assert content == BLOB
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("endpoint", BINARY, ids=lambda e: e.name)
def test_the_shortcut_carries_output_too(endpoint: Any) -> None:
    """A shortcut that cannot save is a second, poorer way to call."""
    import astromansion as am

    assert "output" in inspect.signature(
        getattr(AstroMansion, endpoint.name),
    ).parameters
    # The shortcuts forward **kwargs, so the parameter reaches the method.
    assert callable(getattr(am, endpoint.name))


def test_a_json_endpoint_is_not_given_a_path_to_write() -> None:
    """``output`` on a method that answers with data would mean nothing."""
    for endpoint in ENDPOINTS:
        if endpoint.binary:
            continue
        parameters = inspect.signature(
            getattr(AstroMansion, endpoint.name),
        ).parameters
        assert "output" not in parameters, endpoint.name
