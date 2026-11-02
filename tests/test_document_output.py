"""tests/test_document_output.py: Both clients write every document endpoint.

Without an output path they return bytes and leave the filesystem unchanged.
"""

from __future__ import annotations

import asyncio
import inspect
import json
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from astromansion import AstroMansion, AsyncAstroMansion
from astromansion.models.constants.endpoints import EndpointConstants
from astromansion.models.dataclasses.endpoints import Endpoint

BASE = "https://api.astromansion.com"
KEY = "am_test_key"
BIRTH: dict[str, object] = {"date": "1990-07-19", "lat": 41.0082, "lon": 28.9784}
BLOB = b"%PDF-1.4 or <svg/> or PNG, the client does not care"

#: A styled wheel whose kind and format stay beside its birth in the request.
CHART_REQUEST: dict[str, object] = {
    "type": "natal",
    "format": "png",
    "birth": BIRTH,
    "options": {
        "theme": "dark",
        "style": {
            "preset": "ink",
            "colors": {"house_lines": "#123456"},
            "show": {"watermark": False, "canvas_background": False},
        },
    },
}

#: Endpoints whose success is a document rather than JSON.
BINARY: tuple[Endpoint, ...] = tuple(e for e in EndpointConstants.ALL if e.binary)


def _arguments(endpoint: Endpoint) -> tuple[tuple[object, ...], dict[str, object]]:
    """Build the smallest call each endpoint kind accepts.

    Args:
        endpoint: The document operation that determines the request shape.

    Returns:
        Positional and keyword fields for the operation's public method.
    """
    if endpoint.name == "render_chart":
        return (), dict(CHART_REQUEST)
    if endpoint.kind == "pair":
        return (BIRTH, dict(BIRTH)), {}
    return (), dict(BIRTH)


def test_the_binary_endpoints_are_the_ones_this_covers() -> None:
    """A new document endpoint must not slip past this file unnoticed.

    0.3.0 kept ``export_report`` out, because its generator listed the
    document endpoints by hand. The schema now declares each one's media
    types, and the PDF report is among them.
    """
    assert {e.name for e in BINARY} == {
        "export_csv",
        "export_pdf",
        "export_report",
        "render_astrocartography",
        "render_biwheel",
        "render_chart",
        "render_png",
        "render_sharecard",
        "render_svg",
    }


def test_render_chart_preserves_the_kind_format_and_style() -> None:
    """The chart renderer sends its body unchanged and returns the document bytes."""
    with respx.mock(base_url=BASE) as router:
        route = router.post("/v1/render/chart").mock(httpx.Response(200, content=BLOB))
        with AstroMansion(api_key=KEY) as client:
            content = client.render_chart(CHART_REQUEST)
    assert content == BLOB
    assert json.loads(route.calls.last.request.content) == CHART_REQUEST


@pytest.mark.parametrize("endpoint", BINARY, ids=lambda e: e.name)
def test_every_document_endpoint_can_write_itself(
    endpoint: Endpoint,
    tmp_path: Path,
) -> None:
    """Every document operation can write its result to the chosen path.

    Args:
        endpoint: One document operation from the schema table.
        tmp_path: An isolated directory for the requested output file.
    """
    target = tmp_path / f"{endpoint.name}.bin"
    with respx.mock(base_url=BASE) as router:
        router.post(endpoint.path).mock(httpx.Response(200, content=BLOB))
        args, kwargs = _arguments(endpoint)
        written = getattr(AstroMansion(api_key=KEY), endpoint.name)(
            *args,
            output=target,
            **kwargs,
        )
    assert written == target
    assert target.read_bytes() == BLOB


@pytest.mark.parametrize("endpoint", BINARY, ids=lambda e: e.name)
def test_the_async_client_writes_the_same_documents(
    endpoint: Endpoint,
    tmp_path: Path,
) -> None:
    """The asynchronous client saves the same bytes as the synchronous client.

    Args:
        endpoint: One document operation from the schema table.
        tmp_path: An isolated directory for the requested output file.
    """
    target = tmp_path / f"{endpoint.name}.bin"

    async def call() -> Any:
        """Call the selected asynchronous document operation.

        Returns:
            The path the operation wrote, as reported by the client.
        """
        async with AsyncAstroMansion(api_key=KEY) as client:
            args, kwargs = _arguments(endpoint)
            return await getattr(client, endpoint.name)(
                *args,
                output=target,
                **kwargs,
            )

    with respx.mock(base_url=BASE) as router:
        router.post(endpoint.path).mock(httpx.Response(200, content=BLOB))
        written = asyncio.run(call())
    assert written == target
    assert target.read_bytes() == BLOB


@pytest.mark.parametrize("endpoint", BINARY, ids=lambda e: e.name)
def test_nothing_is_written_unless_a_path_is_named(
    endpoint: Endpoint,
    tmp_path: Path,
) -> None:
    """Bytes are the default, so a call cannot overwrite an unchosen file.

    Args:
        endpoint: One document operation from the schema table.
        tmp_path: An isolated directory that must remain empty.
    """
    with respx.mock(base_url=BASE) as router:
        router.post(endpoint.path).mock(httpx.Response(200, content=BLOB))
        args, kwargs = _arguments(endpoint)
        content = getattr(AstroMansion(api_key=KEY), endpoint.name)(
            *args,
            **kwargs,
        )
    assert content == BLOB
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("endpoint", BINARY, ids=lambda e: e.name)
def test_the_shortcut_carries_output_too(endpoint: Endpoint) -> None:
    """Every document operation has a callable shortcut and an output parameter.

    Args:
        endpoint: The operation whose shortcut must expose the same method.
    """
    import astromansion as am

    assert (
        "output"
        in inspect.signature(
            getattr(AstroMansion, endpoint.name),
        ).parameters
    )
    # The shortcuts forward **kwargs, so the parameter reaches the method.
    assert callable(getattr(am, endpoint.name))


def test_a_json_endpoint_is_not_given_a_path_to_write() -> None:
    """``output`` on a method that answers with data would mean nothing."""
    for endpoint in EndpointConstants.ALL:
        if endpoint.binary:
            continue
        parameters = inspect.signature(
            getattr(AstroMansion, endpoint.name),
        ).parameters
        assert "output" not in parameters, endpoint.name
