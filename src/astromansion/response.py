"""src/astromansion/response.py: One shape for every answer the API sends.

The API replies two ways. Some endpoints hand back the data directly, others
wrap it::

    {"summary": {...}, "planets": [...]}
    {"technique": "chart", "result": {"summary": {...}}}

A caller who learned ``chart.summary`` from one would meet an AttributeError on
the other, over a difference that says nothing about their request. The
wrapper is opened here, so ``.summary`` reads the same everywhere, while
``.raw`` keeps exactly what the server sent.

Nothing is remodelled beyond that. A response stays the server's own JSON, so a
field the API adds reaches the caller instead of being dropped, and no field it
did not send is invented.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any

from .models.constants.envelope import EnvelopeConstants


class Result(Mapping[str, Any]):
    """An API response, read the same way whether or not it was wrapped.

    It behaves as a read-only mapping over the data, so ``dict(result)``,
    ``in``, ``.get()``, and iteration work, and attribute access reads through
    nested objects and lists: ``chart.summary.Sun.sign``. A response whose data
    is a list or a scalar, as a query can return, has no attributes to offer
    and is reached through :attr:`data`.

    Examples:
        >>> chart = Result.build(
        ...     {"technique": "chart", "result": {"summary": {"Sun": {"sign": "Leo"}}}}
        ... )
        >>> chart.summary.Sun.sign
        'Leo'
        >>> chart.technique
        'chart'
        >>> chart["summary"]["Sun"]["sign"]
        'Leo'
        >>> sorted(chart.raw)
        ['result', 'technique']
    """

    __slots__ = ("_data", "_raw", "_technique")

    _data: Any
    _raw: Any
    _technique: str | None

    def __init__(
        self,
        data: Any,
        *,
        technique: str | None = None,
        raw: Any = None,
    ) -> None:
        """Hold a payload whose wrapper, if any, is already opened.

        Args:
            data: The payload proper.
            technique: The technique the server named, or the endpoint the
                client called when the server named none.
            raw: The complete body the server sent; defaults to ``data``.
        """
        object.__setattr__(self, "_data", data)
        object.__setattr__(self, "_technique", technique)
        object.__setattr__(self, "_raw", raw if raw is not None else data)

    @staticmethod
    def is_envelope(payload: Any) -> bool:
        """Return whether a body is the wrapper rather than the data.

        Deliberately strict. Unwrapping anything that merely owns a ``result``
        field would swallow real data the day an endpoint publishes one.

        Args:
            payload: A decoded response body.

        Returns:
            True when the body is exactly ``{technique, result}`` with a text
            ``technique``.

        Examples:
            >>> Result.is_envelope({"technique": "chart", "result": {}})
            True
            >>> Result.is_envelope({"technique": "chart", "result": {}, "page": 1})
            False
        """
        return (
            isinstance(payload, Mapping)
            and set(payload) == EnvelopeConstants.KEYS
            and isinstance(payload.get(EnvelopeConstants.TECHNIQUE_KEY), str)
        )

    @classmethod
    def build(
        cls,
        payload: Any,
        *,
        technique: str | None = None,
        enveloped: bool | None = None,
    ) -> Result:
        """Wrap a decoded body, opening the wrapper when there is one.

        Args:
            payload: A decoded response body.
            technique: The endpoint's name, used when the body names none.
            enveloped: What the schema says: True, False, or ``None`` when the
                schema is free-form and the body has to be recognised.

        Returns:
            A result reading the data and keeping the original.

        Examples:
            >>> Result.build({"planets": []}, technique="natal").technique
            'natal'
        """
        wrapped = cls.is_envelope(payload) if enveloped is None else enveloped
        if (
            wrapped
            and isinstance(payload, Mapping)
            and EnvelopeConstants.RESULT_KEY in payload
        ):
            named = payload.get(EnvelopeConstants.TECHNIQUE_KEY)
            return cls(
                payload[EnvelopeConstants.RESULT_KEY],
                technique=named if isinstance(named, str) else technique,
                raw=payload,
            )
        return cls(payload, technique=technique, raw=payload)

    @classmethod
    def _read(cls, value: Any) -> Any:
        """Give a nested value the same reading as the response itself.

        Args:
            value: A value inside the payload.

        Returns:
            A :class:`Result` for a mapping, a list read item by item, and any
            other value unchanged.
        """
        if isinstance(value, Result):
            return value
        if isinstance(value, Mapping):
            return cls(value)
        if isinstance(value, list):
            return [cls._read(item) for item in value]
        return value

    @property
    def data(self) -> Any:
        """The payload proper, with any wrapper opened."""
        return self._read(self._data)

    @property
    def raw(self) -> Any:
        """The complete body the server sent, wrapper included."""
        return self._raw

    @property
    def technique(self) -> str | None:
        """What the server called this, or the endpoint that was called."""
        return self._technique

    @property
    def result(self) -> Any:
        """The payload, matching the server's own wrapper name.

        A payload that publishes its own ``result`` field wins: this alias is a
        convenience and must never hide data the server actually sent.
        """
        data = self._data
        if isinstance(data, Mapping) and EnvelopeConstants.RESULT_KEY in data:
            return self._read(data[EnvelopeConstants.RESULT_KEY])
        return self.data

    def to_dict(self) -> Any:
        """Return the data as plain Python, untouched.

        Returns:
            A dict copy of a mapping payload, or the payload itself otherwise.
        """
        data = self._data
        return dict(data) if isinstance(data, Mapping) else data

    def _fields(self) -> Mapping[str, Any]:
        """Return the data as a mapping, or an empty one when it is not.

        Returns:
            The payload when it is a mapping, else an empty mapping.
        """
        data = self._data
        return data if isinstance(data, Mapping) else {}

    def __getitem__(self, key: Any) -> Any:
        """Read one field, or one item of a list payload.

        Args:
            key: A field name, or an index into a list payload.

        Returns:
            The value, read the same way as the response.
        """
        return self._read(self._data[key])

    def __getattr__(self, name: str) -> Any:
        """Read a field as an attribute.

        Args:
            name: The field name.

        Returns:
            The value, read the same way as the response.

        Raises:
            AttributeError: The field is absent, naming the ones present, or
                the payload is not a mapping.
        """
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
        """Iterate over the field names of a mapping payload.

        Returns:
            An iterator over the names; empty for any other payload.
        """
        return iter(self._fields())

    def __len__(self) -> int:
        """Count the fields of a mapping or the items of a list.

        Returns:
            The count, or zero for a scalar payload.
        """
        data = self._data
        return len(data) if isinstance(data, (Mapping, list)) else 0

    def __dir__(self) -> list[str]:
        """List the attributes, the payload's field names included.

        Returns:
            The sorted names.
        """
        return sorted(set(super().__dir__()) | set(self._fields()))

    def __repr__(self) -> str:
        """Show the payload and the technique.

        Returns:
            ``Result(<payload>)``, with the technique when there is one.
        """
        named = f", technique={self._technique!r}" if self._technique else ""
        return f"Result({self._data!r}{named})"
