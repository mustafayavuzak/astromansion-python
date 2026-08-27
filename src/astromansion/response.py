"""One shape for every answer, whatever shape the API sent.

The API replies two ways. Some endpoints hand back the data directly::

    {"summary": {...}, "planets": [...]}

and others wrap it::

    {"technique": "chart", "result": {"summary": {...}}}

A caller who learned ``chart.summary`` from one would meet an AttributeError
on the other, over a difference that says nothing about their request. The
envelope is opened here so ``.summary`` reads the same everywhere, while
``.raw`` keeps exactly what the server sent for anyone who needs it.

Nothing is remodelled beyond that. A response stays the server's own JSON, so
a field the API adds reaches the caller instead of being dropped, and no field
it did not send is invented.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any, ClassVar


class Result(Mapping[str, Any]):
    """An API response, read the same way whether or not it was wrapped.

    Behaves as a read-only mapping over the data, so ``dict(result)``, ``in``,
    ``.get()`` and iteration work, and attribute access reads through nested
    objects and lists: ``chart.summary.Sun.sign``.

    A response whose data is a list or a scalar, as a query can return, has no
    attributes to offer. Reach it through :attr:`data`.

    :param data: The payload proper, with any envelope already opened.
    :param technique: Technique the server named, or the endpoint the SDK
        called when the server named none.
    :param raw: The complete body the server sent, envelope included.
    """

    __slots__ = ("_data", "_raw", "_technique")

    _data: Any
    _raw: Any
    _technique: str | None

    #: The two keys an envelope carries, and nothing else. Consulted only
    #: where the schema does not say: a payload that merely happens to own a
    #: ``result`` field keeps more keys than these and is left alone.
    ENVELOPE_KEYS: ClassVar[frozenset[str]] = frozenset({"technique", "result"})

    def __init__(
        self,
        data: Any,
        *,
        technique: str | None = None,
        raw: Any = None,
    ) -> None:
        object.__setattr__(self, "_data", data)
        object.__setattr__(self, "_technique", technique)
        object.__setattr__(self, "_raw", raw if raw is not None else data)

    # ------------------------------------------------------------ building

    @classmethod
    def is_envelope(cls, payload: Any) -> bool:
        """Return whether a body is the wrapper rather than the data.

        Deliberately strict. Unwrapping anything that merely owns a ``result``
        field would swallow real data the day an endpoint publishes one.

        :param payload: Decoded response body.
        :returns: True when the body is exactly ``{technique, result}``.
        """
        return (
            isinstance(payload, Mapping)
            and set(payload) == cls.ENVELOPE_KEYS
            and isinstance(payload.get("technique"), str)
        )

    @classmethod
    def build(
        cls,
        payload: Any,
        *,
        technique: str | None = None,
        enveloped: bool | None = None,
    ) -> Result:
        """Wrap a decoded body, opening the envelope when there is one.

        :param payload: Decoded response body.
        :param technique: Endpoint name, used when the body names none.
        :param enveloped: What the schema says: True, False, or None when the
            schema is free-form and the body has to be recognised.
        :returns: A result reading the data and keeping the original.
        """
        wrapped = cls.is_envelope(payload) if enveloped is None else enveloped
        if wrapped and isinstance(payload, Mapping) and "result" in payload:
            named = payload.get("technique")
            return cls(
                payload["result"],
                technique=named if isinstance(named, str) else technique,
                raw=payload,
            )
        return cls(payload, technique=technique, raw=payload)

    @classmethod
    def _read(cls, value: Any) -> Any:
        """Give a nested value the same reading as the response itself."""
        if isinstance(value, Result):
            return value
        if isinstance(value, Mapping):
            return cls(value)
        if isinstance(value, list):
            return [cls._read(item) for item in value]
        return value

    # -------------------------------------------------------------- access

    @property
    def data(self) -> Any:
        """The payload proper, with any envelope opened."""
        return self._read(self._data)

    @property
    def raw(self) -> Any:
        """The complete body the server sent, envelope included."""
        return self._raw

    @property
    def technique(self) -> str | None:
        """What the server called this, or the endpoint that was called."""
        return self._technique

    @property
    def result(self) -> Any:
        """Alias of :attr:`data`, matching the server's own envelope name.

        A payload that publishes its own ``result`` field wins: the alias is a
        convenience and must never hide data the server actually sent.
        """
        data = self._data
        if isinstance(data, Mapping) and "result" in data:
            return self._read(data["result"])
        return self.data

    def to_dict(self) -> Any:
        """Return the data as plain Python, untouched."""
        data = self._data
        return dict(data) if isinstance(data, Mapping) else data

    # -------------------------------------------------------- mapping shape

    def _fields(self) -> Mapping[str, Any]:
        """Return the data as a mapping, or an empty one when it is not."""
        data = self._data
        return data if isinstance(data, Mapping) else {}

    def __getitem__(self, key: Any) -> Any:
        # A list result still answers integer indexing the obvious way.
        return self._read(self._data[key])

    def __getattr__(self, name: str) -> Any:
        data = object.__getattribute__(self, "_data")
        if isinstance(data, Mapping):
            if name in data:
                return self._read(data[name])
            raise AttributeError(
                f"{name!r} is not in this response. "
                f"Available: {', '.join(sorted(data))}"
            )
        raise AttributeError(
            f"this response holds a {type(data).__name__}, which has no "
            f"{name!r}. Read it through .data"
        )

    def __iter__(self) -> Iterator[str]:
        return iter(self._fields())

    def __len__(self) -> int:
        data = self._data
        return len(data) if isinstance(data, (Mapping, list)) else 0

    def __dir__(self) -> list[str]:
        return sorted(set(super().__dir__()) | set(self._fields()))

    def __repr__(self) -> str:
        named = f", technique={self._technique!r}" if self._technique else ""
        return f"Result({self._data!r}{named})"
