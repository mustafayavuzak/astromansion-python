"""A rendered table must arrive as text, a document as bytes.

``/v1/query`` answers ``format="box"`` with ``text/plain``, meant to be
printed. Handing that back as ``bytes`` prints the repr, escape sequences and
box drawing included, which is unreadable. Every other non-JSON answer is a
document the caller writes to a file, and those stay bytes.
"""

from __future__ import annotations

import httpx
import pytest

from astromansion import AstroMansion
from astromansion._core import Media

BOX = "┌────────┬───────────┐\n│ name   │ sign      │\n└────────┴───────────┘"


def _client(content: bytes, content_type: str) -> AstroMansion:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, content=content, headers={"Content-Type": content_type},
        )

    return AstroMansion(
        api_key="test", base_url="https://api.example",
        transport=httpx.MockTransport(handler),
    )


def test_rendered_table_arrives_as_text() -> None:
    """A ``text/plain`` answer is printable without decoding it by hand."""
    client = _client(BOX.encode(), "text/plain; charset=utf-8")

    answer = client.query(birth={"date": "2000-01-01"}, sql="SELECT 1",
                          format="box")

    assert isinstance(answer, str)
    assert answer == BOX


def test_a_document_stays_bytes() -> None:
    """A PDF must not become ``str``: it would not survive the round trip."""
    client = _client(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3", "application/pdf")

    answer = client.export_pdf(date="2000-01-01", lat=51.4779, lon=0.0)

    assert isinstance(answer, bytes)


@pytest.mark.parametrize("content_type", ["text/csv", "image/svg+xml"])
def test_csv_and_svg_stay_bytes(content_type: str) -> None:
    """Both are text on the wire and files in practice.

    Changing them would break every ``open(path, "wb")`` written against
    them, so the text rule is deliberately narrower than "is it readable".
    """
    client = _client(b"name,sign\nSun,Leo\n", content_type)

    answer = client.request("POST", "/v1/export-csv", binary=True, json={})

    assert isinstance(answer, bytes)


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ("text/plain", True),
        ("text/plain; charset=utf-8", True),
        ("TEXT/PLAIN", True),
        ("  text/plain  ; charset=utf-8", True),
        ("text/csv", False),
        ("application/pdf", False),
        ("image/svg+xml", False),
        ("text/plaintext", False),
        ("", False),
        (None, False),
    ],
)
def test_media_reads_the_header(header: str | None, expected: bool) -> None:
    """The parameter, the case and the whitespace must not decide the answer."""
    assert Media.is_text(header) is expected


def test_a_missing_content_type_stays_bytes() -> None:
    """Without a declared type the safe reading is a document."""
    client = _client(b"\x00\x01\x02", "")

    answer = client.request("POST", "/v1/export-pdf", binary=True, json={})

    assert isinstance(answer, bytes)
