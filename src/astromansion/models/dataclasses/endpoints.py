"""src/astromansion/models/dataclasses/endpoints.py: One operation the API publishes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Endpoint:
    """One published operation, from the generated table to the code that reads it.

    The generator writes one per operation into ``EndpointConstants.ALL``; the
    tests read them to check that both clients and the shortcuts cover the API.

    Attributes:
        name: Method name exposed on the clients.
        method: HTTP verb.
        path: Path template, possibly containing one placeholder.
        kind: Request shape: ``chart``, ``pair``, ``birth_extra``, ``body``,
            ``get``, ``delete`` or ``empty``.
        fields: Top-level body fields the schema declares.
        binary: Whether a success returns a document rather than JSON.
        enveloped: Whether a success is wrapped in ``{technique, result}``;
            ``None`` when the schema is free-form and the body decides.
        summary: One-line description taken from the schema.
    """

    name: str
    method: str
    path: str
    kind: str
    fields: tuple[str, ...]
    binary: bool
    enveloped: bool | None
    summary: str
