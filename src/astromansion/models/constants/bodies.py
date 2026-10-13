"""src/astromansion/models/constants/bodies.py: Wire names of request bodies."""

from __future__ import annotations

from typing import Final


class RequestBodyConstants:
    """Top-level fields of a request body, and the share card's fixed values.

    One-person endpoints take ``birth`` and ``options``; two-person endpoints
    add ``partner``, which is what the API calls the second chart. The share
    card is the one endpoint written by hand: it is sent to
    ``SHARECARD_PATH``, draws a synastry card unless asked for a natal one,
    and takes ``names`` and ``lang`` beside the charts.
    """

    BIRTH: Final[str] = "birth"
    PARTNER: Final[str] = "partner"
    OPTIONS: Final[str] = "options"

    SHARECARD_PATH: Final[str] = "/v1/render/sharecard"
    SHARECARD_TECHNIQUE: Final[str] = "render_sharecard"
    SHARECARD_SYNASTRY: Final[str] = "synastry"
    SHARECARD_TYPE: Final[str] = "type"
    SHARECARD_NAMES: Final[str] = "names"
    SHARECARD_LANG: Final[str] = "lang"
